"""Errores de la capa de aplicación de acceso.

Independientes de FastAPI: el handler de `api/errors.py` los traduce al contrato
HTTP `{code, message, details, traceId}`.
"""

from typing import Any


class AuthError(Exception):
    """Error controlado de auth con código HTTP, código de contrato y detalle."""

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: Any | None = None,
        retry_after: int | None = None,
    ) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details
        self.retry_after = retry_after
        super().__init__(message)


class AuthStorageError(AuthError):
    """Fallo de SQLite (I/O, locked): se responde 503 auth_unavailable."""

    def __init__(self, message: str = "El servicio de acceso no está disponible.") -> None:
        super().__init__(503, "auth_unavailable", message)
