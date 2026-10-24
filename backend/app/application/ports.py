"""Puertos que la capa de aplicación usa; infraestructura los implementa."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Protocol


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
