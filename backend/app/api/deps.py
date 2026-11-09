"""Dependencias de la API: repositorios, runner del agente e identidad de acceso."""
from datetime import timedelta
from functools import lru_cache
from typing import Annotated

from fastapi import Depends, Request
from pymongo.errors import PyMongoError

from app.agent.loop import AgentRunner
from app.agent.tools import AgentTools
from app.api.errors import ApiError
from app.application.auth.service import AuthService
from app.application.errors import AgentError
from app.application.maintenance import MaintenanceService
from app.config import Settings, get_settings
from app.db import get_db
from app.domain.auth.models import Usuario
from app.domain.profiles import Actor, RolDominio
from app.infrastructure.clock import SystemClock
from app.infrastructure.llm import OpenCodeLLMClient
from app.infrastructure.mongo_repositories import (
    MongoDeviceRepository,
    MongoIncidentRepository,
    MongoInventoryRepository,
    MongoMaintenanceRepository,
    MongoParkRepository,
    MongoProfileRepository,
    MongoReadingRepository,
)
from app.infrastructure.passwords import BcryptPasswordHasher
from app.infrastructure.sqlite_auth import BaseAuth
from app.infrastructure.sqlite_auth_repositories import (
    SqliteSessionRepository,
    SqliteUserRepository,
)


def get_device_repository() -> MongoDeviceRepository:
    return MongoDeviceRepository(get_db())


def get_park_repository() -> MongoParkRepository:
    return MongoParkRepository(get_db())


def get_profile_repository() -> MongoProfileRepository:
    """Perfil de negocio para `/auth/login` y `/auth/me`."""
    return MongoProfileRepository(get_db())


def get_reading_repository() -> MongoReadingRepository:
    return MongoReadingRepository(get_db())


def get_maintenance_repository() -> MongoMaintenanceRepository:
    return MongoMaintenanceRepository(get_db())


def get_incident_repository() -> MongoIncidentRepository:
    return MongoIncidentRepository(get_db())


def get_inventory_repository() -> MongoInventoryRepository:
    return MongoInventoryRepository(get_db())


def get_maintenance_service(
    tareas: Annotated[MongoMaintenanceRepository, Depends(get_maintenance_repository)],
    perfiles: Annotated[MongoProfileRepository, Depends(get_profile_repository)],
    incidentes: Annotated[MongoIncidentRepository, Depends(get_incident_repository)],
    inventario: Annotated[MongoInventoryRepository, Depends(get_inventory_repository)],
    parques: Annotated[MongoParkRepository, Depends(get_park_repository)],
) -> MaintenanceService:
    """Servicio de mantenimientos con repositorios y reloj del proceso."""
    return MaintenanceService(tareas, perfiles, incidentes, inventario, parques, SystemClock())


@lru_cache
def _build_agent_runner() -> AgentRunner:
    """Un solo runner por proceso para que la caché de demo sobreviva."""
    settings = get_settings()
    if not settings.llm_configurado:
        raise AgentError(
            503,
            "llm_not_configured",
            "La API del agente no está configurada. Define OPENCODE_API_KEY.",
        )
    devices = MongoDeviceRepository(get_db())
    readings = MongoReadingRepository(get_db())
    tools = AgentTools(
        devices,
        readings,
        SystemClock(),
        sin_reportar_min=settings.sin_reportar_min,
    )
    llm = OpenCodeLLMClient(settings)
    return AgentRunner(llm, tools, settings)


def get_agent_runner() -> AgentRunner:
    return _build_agent_runner()


# --- Identidad de acceso ---

def get_auth_service(
    settings: Annotated[Settings, Depends(get_settings)],
    perfiles: Annotated[MongoProfileRepository, Depends(get_profile_repository)],
) -> AuthService:
    """Construye el servicio de auth por request (sin lru_cache: tests cambian env)."""
    base = BaseAuth(settings.auth_db_path)
    base.asegurar_esquema()
    return AuthService(
        users=SqliteUserRepository(base),
        sessions=SqliteSessionRepository(base),
        hasher=BcryptPasswordHasher(settings.auth_bcrypt_rounds),
        clock=SystemClock(),
        ttl=timedelta(hours=settings.auth_session_ttl_hours),
        profiles=perfiles,
    )


async def require_user(
    request: Request,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> Usuario:
    """Devuelve el usuario autenticado o levanta AuthError 401."""
    token = request.cookies.get(get_settings().auth_cookie_name)
    return service.usuario_actual(token).usuario


async def require_admin(
    usuario: Annotated[Usuario, Depends(require_user)],
) -> Usuario:
    """Autenticado + rol admin; si no, AuthError 403."""
    from app.application.auth.errors import AuthError
    if usuario.rol != "admin":
        raise AuthError(403, "forbidden", "No tienes permisos para este recurso.")
    return usuario


# --- Identidad de negocio para mantenimientos ---

async def get_maintenance_actor(
    usuario: Annotated[Usuario, Depends(require_user)],
    perfiles: Annotated[MongoProfileRepository, Depends(get_profile_repository)],
) -> Actor:
    """Une la sesión SQLite con el perfil Mongo y valida la combinación de roles."""
    try:
        perfil = perfiles.get_by_correo(usuario.correo)
    except PyMongoError as exc:
        raise ApiError(
            503,
            "db_unavailable",
            "La base de datos no está disponible.",
        ) from exc

    if not perfil:
        raise ApiError(
            403,
            "profile_missing",
            "Tu sesión no tiene un perfil de dominio configurado.",
        )

    try:
        rol = RolDominio(perfil.get("rol"))
    except (TypeError, ValueError) as exc:
        raise ApiError(403, "profile_missing", "Tu perfil de dominio no es válido.") from exc

    acceso = usuario.rol.value if hasattr(usuario.rol, "value") else str(usuario.rol)
    if acceso == "admin" and rol in {
        RolDominio.ADMINISTRADOR,
        RolDominio.OPERADOR_MANTENIMIENTO,
    }:
        # El acceso admin manda en la estación; el perfil solo aporta identidad.
        efectivo = RolDominio.ADMINISTRADOR
    elif acceso == "operator" and rol == RolDominio.OPERADOR_MANTENIMIENTO:
        efectivo = RolDominio.OPERADOR_MANTENIMIENTO
    else:
        raise ApiError(403, "forbidden", "Tu rol de acceso no permite mantenimientos.")

    return Actor(
        perfil_id=str(perfil["_id"]),
        correo=perfil.get("correo", usuario.correo),
        rol=efectivo,
    )


async def get_admin_actor(
    usuario: Annotated[Usuario, Depends(require_user)],
    actor: Annotated[Actor, Depends(get_maintenance_actor)],
) -> Actor:
    """Actor de mantenimientos con acceso admin explícito."""
    if usuario.rol != "admin":
        raise ApiError(403, "forbidden", "Solo el administrador puede hacer esta acción.")
    return actor
