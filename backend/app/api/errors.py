"""Contrato único de errores: `{code, message, details, traceId}`."""

import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.cookies import limpiar_cookie_sesion
from app.application.auth.errors import AuthError
from app.application.errors import AgentError
from app.config import get_settings
from app.domain.incidents import TransicionIncidenteInvalida
from app.domain.maintenance import (
    ErrorMantenimiento,
    NotaRequerida,
    PermisoDenegado,
    TransicionInvalida,
)

logger = logging.getLogger("teiba.api")


class ApiError(Exception):
    """Error controlado que el handler convierte al contrato público."""

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: Any | None = None,
    ) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details
        super().__init__(message)


def trace_id(request: Request) -> str:
    return getattr(request.state, "trace_id", "")


def error_payload(
    request: Request,
    code: str,
    message: str,
    details: Any | None = None,
) -> dict[str, Any]:
    return {
        "code": code,
        "message": message,
        "details": details,
        "traceId": trace_id(request),
    }


def register_exception_handlers(app: FastAPI) -> None:
    """Registra el formato único para todos los errores de la API."""

    @app.exception_handler(ApiError)
    async def api_error_handler(request: Request, exc: ApiError) -> JSONResponse:
        response = JSONResponse(
            status_code=exc.status_code,
            content=error_payload(request, exc.code, exc.message, exc.details),
        )
        # Rate limit (429) lleva Retry-After tanto en detalle como en header.
        if exc.code == "rate_limited":
            reintento = None
            if isinstance(exc.details, dict):
                reintento = exc.details.get("retry_after")
            if reintento is None and exc.status_code == 429:
                reintento = 60
            if reintento is not None:
                response.headers["Retry-After"] = str(reintento)
        return response

    @app.exception_handler(AuthError)
    async def auth_error_handler(request: Request, exc: AuthError) -> JSONResponse:
        response = JSONResponse(
            status_code=exc.status_code,
            content=error_payload(request, exc.code, exc.message, exc.details),
        )
        # Un 401 de sesión invalida limpia la cookie para que el cliente quede
        # coherente (login/cierre). Un 401 de login fallido no la borra.
        if exc.status_code == 401 and exc.code == "not_authenticated":
            limpiar_cookie_sesion(response, get_settings())
        if exc.retry_after is not None:
            response.headers["Retry-After"] = str(exc.retry_after)
        return response

    @app.exception_handler(AgentError)
    async def agent_error_handler(request: Request, exc: AgentError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=error_payload(request, exc.code, exc.message, exc.details),
        )

    @app.exception_handler(PermisoDenegado)
    async def permiso_handler(request: Request, exc: PermisoDenegado) -> JSONResponse:
        return JSONResponse(
            status_code=403,
            content=error_payload(request, "forbidden", str(exc)),
        )

    @app.exception_handler(TransicionInvalida)
    async def transicion_handler(request: Request, exc: TransicionInvalida) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content=error_payload(request, "invalid_transition", str(exc)),
        )

    @app.exception_handler(TransicionIncidenteInvalida)
    async def transicion_incidente_handler(
        request: Request,
        exc: TransicionIncidenteInvalida,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content=error_payload(request, "invalid_transition", str(exc)),
        )

    @app.exception_handler(NotaRequerida)
    async def nota_handler(request: Request, exc: NotaRequerida) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content=error_payload(request, "invalid_request", str(exc)),
        )

    @app.exception_handler(ErrorMantenimiento)
    async def mantenimiento_handler(
        request: Request,
        exc: ErrorMantenimiento,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content=error_payload(request, "invalid_request", str(exc)),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        # No devolvemos el input original para no filtrar datos del cliente.
        details = [
            {
                "loc": list(error.get("loc", [])),
                "msg": error.get("msg", ""),
                "type": error.get("type", ""),
            }
            for error in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content=error_payload(
                request,
                "invalid_request",
                "Los datos enviados no son válidos.",
                details,
            ),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_handler(
        request: Request,
        exc: StarletteHTTPException,
    ) -> JSONResponse:
        code = "not_found" if exc.status_code == 404 else "http_error"
        return JSONResponse(
            status_code=exc.status_code,
            content=error_payload(request, code, str(exc.detail), None),
        )

    @app.exception_handler(Exception)
    async def unhandled_handler(request: Request, exc: Exception) -> JSONResponse:
        # El stack queda en el log local; al cliente solo va el traceId.
        logger.exception("unhandled_error trace_id=%s", trace_id(request))
        return JSONResponse(
            status_code=500,
            content=error_payload(
                request,
                "internal_error",
                "Error interno del servidor.",
                None,
            ),
        )
