"""Puertos que la capa de aplicación usa; infraestructura los implementa."""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Protocol

from app.domain.auth.models import Credenciales, Rol, Sesion, Usuario


class DeviceRepository(Protocol):
    def resolve_sector(self, nombre: str) -> list[dict[str, Any]]: ...

    def resolve_parque(self, nombre: str) -> list[dict[str, Any]]: ...

    def find_devices(
        self,
        *,
        device_id: str | None = None,
        tipo: str | None = None,
        sector_ids: list[Any] | None = None,
        parque_ids: list[Any] | None = None,
        depende_de: str | None = None,
        limite: int = 20,
    ) -> list[dict[str, Any]]: ...

    def get_device(self, device_id: str) -> dict[str, Any] | None: ...

    def children_of(self, antena: str) -> list[dict[str, Any]]: ...

    def count_children(self, antena: str) -> int: ...


class ParkRepository(Protocol):
    """Lectura de parques y sus sectores para el libro de parques."""

    def list_parques(self) -> list[dict[str, Any]]: ...

    def get_parque(self, codigo: str) -> dict[str, Any] | None: ...


class ReadingRepository(Protocol):
    def history(
        self,
        sensor_id: str,
        since: datetime,
        limite: int = 20,
    ) -> list[dict[str, Any]]: ...

    def latest(self, sensor_id: str) -> dict[str, Any] | None: ...

    def latest_many(self, sensor_ids: list[str]) -> dict[str, dict[str, Any]]: ...


class Clock(Protocol):
    def now(self) -> datetime: ...


# --- Puertos de identidad de acceso (SQLite) ---

class UserRepository(Protocol):
    """Credenciales y usuarios persistidos en SQLite."""

    def get_credentials(self, correo: str) -> Credenciales | None: ...

    def get_by_id(self, user_id: int) -> Usuario | None: ...


class SessionRepository(Protocol):
    """Sesiones de acceso opacas persistidas en SQLite."""

    def create(self, sesion: Sesion) -> None: ...

    def get(self, token_hash: str) -> Sesion | None: ...

    def delete(self, token_hash: str) -> None: ...

    def delete_for_user(self, user_id: int) -> None:
        """Revoca todas las sesiones de un usuario (rotación de contraseña)."""

    def delete_expired(self, ahora: datetime) -> int:
        """Limpia sesiones vencidas; devuelve cuántas borro."""


class PasswordHasher(Protocol):
    """Abstracción del KDF para no acoplar la aplicación a bcrypt directamente."""

    def hash(self, contrasena: str) -> str: ...

    def verify(self, contrasena: str, almacenado: str) -> bool: ...

    def verify_dummy(self, contrasena: str) -> None:
        """Verifica contra un hash fijo para igualar tiempos si el correo no existe."""
        ...


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: str


@dataclass
class LLMMessage:
    content: str | None
    tool_calls: list[ToolCall] = field(default_factory=list)


class LLMClient(Protocol):
    def chat(self, messages: list[dict], tools: list[dict]) -> LLMMessage: ...


class LLMError(Exception):
    """Fallo del proveedor LLM ya clasificado para el bucle del agente."""

    def __init__(self, code: str, message: str, retryable: bool = False) -> None:
        self.code = code
        self.retryable = retryable
        super().__init__(message)
