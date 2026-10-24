"""Contrato único de errores: `{code, message, details, traceId}`."""
import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.application.errors import AgentError

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
        return JSONResponse(
            status_code=exc.status_code,
            content=error_payload(request, exc.code, exc.message, exc.details),
        )

    @app.exception_handler(AgentError)
    async def agent_error_handler(request: Request, exc: AgentError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=error_payload(request, exc.code, exc.message, exc.details),
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
