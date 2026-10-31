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


class ParkRepository(Protocol):
    """Lectura de parques y sus sectores para el libro de parques."""

    def list_parques(self) -> list[dict[str, Any]]: ...

    def get_parque(self, codigo: str) -> dict[str, Any] | None: ...


class ProfileRepository(Protocol):
    """Perfiles de negocio en Mongo, enlazados por correo con la sesión."""

    def get_by_correo(self, correo: str) -> dict[str, Any] | None: ...

    def get_by_id(self, perfil_id: Any) -> dict[str, Any] | None: ...

    def list_operadores(self) -> list[dict[str, Any]]: ...


class MaintenanceRepository(Protocol):
    """Tareas de mantenimiento y su ciclo de vida."""

    def list_tareas(
        self,
        *,
        tarea_id: Any | None = None,
        estado: str | None = None,
        prioridad: str | None = None,
        parque_id: Any | None = None,
        responsable_id: Any | None = None,
        incidente_id: Any | None = None,
        limite: int = 50,
    ) -> list[dict[str, Any]]: ...

    def get_tarea(self, tarea_id: Any) -> dict[str, Any] | None: ...

    def create_tarea(self, doc: dict[str, Any]) -> Any: ...

    def update_estado(
        self,
        tarea_id: Any,
        *,
        estado: str,
        campo_nota: str | None,
        nota: str | None,
        limpia_ejecucion: bool,
        marca_reapertura: bool,
        ahora: datetime,
    ) -> dict[str, Any] | None: ...

    def reasignar(self, tarea_id: Any, responsable_id: Any) -> dict[str, Any] | None: ...

    def ensure_indexes(self) -> None: ...


class IncidentRepository(Protocol):
    """Lectura y cambio de estado de incidentes ciudadanos."""

    def list_incidentes(
        self,
        *,
        incidente_id: Any | None = None,
        parque_id: Any | None = None,
        estados: list[str] | None = None,
        limite: int = 50,
    ) -> list[dict[str, Any]]: ...

    def get_incidente(self, incidente_id: Any) -> dict[str, Any] | None: ...

    def update_estado(self, incidente_id: Any, estado: str) -> dict[str, Any] | None: ...

    def ensure_indexes(self) -> None: ...


class InventoryRepository(Protocol):
    """Elementos de inventario para vincular tareas."""

    def list_elementos(
        self,
        *,
        parque_id: Any | None = None,
        elemento_id: Any | None = None,
        limite: int = 50,
    ) -> list[dict[str, Any]]: ...

    def get_elemento(self, elemento_id: Any) -> dict[str, Any] | None: ...

    def ensure_indexes(self) -> None: ...


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
