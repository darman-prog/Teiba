"""Router de autenticación: login, logout y sesión actual."""

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response

from app.api.cookies import establecer_cookie_sesion, limpiar_cookie_sesion
from app.api.deps import get_auth_service
from app.api.security import verificar_origen
from app.config import Settings, get_settings
from app.schemas import LoginRequest, SessionResponse

router = APIRouter(prefix="/auth", tags=["auth"])


def _a_iso_z(expira_en: datetime) -> str:
    return expira_en.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _leer_token(request: Request, settings: Settings) -> str | None:
    return request.cookies.get(settings.auth_cookie_name)


@router.post("/login", response_model=SessionResponse)
def login(
    body: LoginRequest,
    request: Request,
    response: Response,
    settings: Annotated[Settings, Depends(get_settings)],
    service: Annotated[object, Depends(get_auth_service)],
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
) -> SessionResponse:
    token = _leer_token(request, settings)
    actual = service.usuario_actual(token)
    return SessionResponse(
        usuario={"correo": actual.usuario.correo, "rol": actual.usuario.rol.value},
        expira_en=_a_iso_z(actual.expira_en),
    )
