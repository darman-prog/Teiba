"""Errores de la capa de aplicación, independientes de FastAPI."""
from typing import Any


class AgentError(Exception):
    """Error controlado del agente; la capa API lo traduce al contrato HTTP."""

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
