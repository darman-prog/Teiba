"""Dependencias de la API: repositorios, runner del agente e identidad de acceso."""
from datetime import timedelta
from functools import lru_cache
from typing import Annotated

from fastapi import Depends, Request

from app.agent.loop import AgentRunner
from app.agent.tools import AgentTools
from app.application.auth.service import AuthService
from app.application.errors import AgentError
from app.config import Settings, get_settings
from app.db import get_db
from app.domain.auth.models import Usuario
from app.infrastructure.clock import SystemClock
from app.infrastructure.llm import OpenCodeLLMClient
from app.infrastructure.mongo_repositories import (
    MongoDeviceRepository,
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
