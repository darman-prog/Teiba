"""Router de autenticación: login, logout y sesión actual."""

import logging
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from pydantic import ValidationError
from pymongo.errors import PyMongoError

from app.api.cookies import establecer_cookie_sesion, limpiar_cookie_sesion
from app.api.deps import get_auth_service, get_profile_repository
from app.api.security import verificar_origen
from app.application.ports import ProfileRepository
from app.config import Settings, get_settings
from app.schemas import LoginRequest, PerfilUsuario, SessionResponse

router = APIRouter(prefix="/auth", tags=["auth"])


def _a_iso_z(expira_en: datetime) -> str:
    return expira_en.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _leer_token(request: Request, settings: Settings) -> str | None:
    return request.cookies.get(settings.auth_cookie_name)


def _perfil_de(
    perfiles: ProfileRepository,
    correo: str,
    request: Request,
) -> PerfilUsuario | None:
    """Resuelve el perfil de dominio; un fallo de Mongo no rompe la sesión."""
    try:
        doc = perfiles.get_by_correo(correo)
    except PyMongoError:
        # Solo se registra el trace_id: ni correo ni datos personales.
        logging.getLogger("teiba.api").warning(
            "No se pudo resolver el perfil de dominio trace_id=%s",
            getattr(request.state, "trace_id", "-"),
        )
        return None

    if not doc or "_id" not in doc:
        return None

    try:
        return PerfilUsuario(
            id=str(doc["_id"]),
            nombre=doc["nombre"],
            correo=doc["correo"],
            rol=doc["rol"],
        )
    except (KeyError, TypeError, ValidationError):
        # Un perfil incompleto o con rol desconocido se trata como ausente.
        return None


@router.post("/login", response_model=SessionResponse)
def login(
    body: LoginRequest,
    request: Request,
    response: Response,
    settings: Annotated[Settings, Depends(get_settings)],
    service: Annotated[object, Depends(get_auth_service)],
    perfiles: Annotated[ProfileRepository, Depends(get_profile_repository)],
    _: Annotated[None, Depends(verificar_origen)],
) -> SessionResponse:
    limitador = request.app.state.login_rate_limit
    # Rate limit antes de tocar la BD: si ya se paso, ni validamos.
    limitador.comprobar(request, body.correo)
    try:
        resultado = service.login(body.correo, body.contrasena, _leer_token(request, settings))
    except Exception:
        # Cualquier fallo de credenciales/almacen cuenta como intento fallido.
        limitador.registrar_fallo(request, body.correo)
        raise
    limitador.reiniciar(request, body.correo)
    max_age = int((resultado.expira_en - datetime.now(resultado.expira_en.tzinfo)).total_seconds())
    establecer_cookie_sesion(response, settings, resultado.token, max_age)
    return SessionResponse(
        usuario={"correo": resultado.usuario.correo, "rol": resultado.usuario.rol.value},
        perfil=_perfil_de(perfiles, resultado.usuario.correo, request),
        expira_en=_a_iso_z(resultado.expira_en),
    )


@router.post("/logout", status_code=204)
def logout(
    request: Request,
    response: Response,
    settings: Annotated[Settings, Depends(get_settings)],
    service: Annotated[object, Depends(get_auth_service)],
    _: Annotated[None, Depends(verificar_origen)],
) -> None:
    service.logout(_leer_token(request, settings))
    limpiar_cookie_sesion(response, settings)


@router.get("/me", response_model=SessionResponse)
def me(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
    service: Annotated[object, Depends(get_auth_service)],
    perfiles: Annotated[ProfileRepository, Depends(get_profile_repository)],
) -> SessionResponse:
    token = _leer_token(request, settings)
    actual = service.usuario_actual(token)
    return SessionResponse(
        usuario={"correo": actual.usuario.correo, "rol": actual.usuario.rol.value},
        perfil=_perfil_de(perfiles, actual.usuario.correo, request),
        expira_en=_a_iso_z(actual.expira_en),
    )
