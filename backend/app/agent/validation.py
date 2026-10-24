"""Validación estricta de los argumentos que propone el LLM.

Los argumentos llegan como texto JSON y no son confiables: se rechazan
claves extra, operadores (`$`), puntos y tipos que no sean escalares.
"""
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

TipoDispositivo = Literal[
    "calidad_suelo",
    "estacion_meteorologica",
    "luminaria_inteligente",
    "antena_enlace",
]

# Rechaza operadores de Mongo y puntos, que permitirían inyectar filtros.
SAFE_TEXT = r"^[^$.\x00]{1,80}$"
# Los IDs técnicos son cortos y alfanuméricos; nada de espacios ni símbolos.
SAFE_ID = r"^[A-Za-z0-9-]{1,20}$"


class ToolArgs(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class ListSensorsArgs(ToolArgs):
    tipo: TipoDispositivo | None = None
    sector: str | None = Field(default=None, pattern=SAFE_TEXT)
    parque: str | None = Field(default=None, pattern=SAFE_TEXT)
    depende_de: str | None = Field(default=None, pattern=SAFE_ID)
    limite: int = Field(default=20, ge=1, le=50)


class SensorHistoryArgs(ToolArgs):
    sensor_id: str = Field(pattern=SAFE_ID)
    horas: int = Field(default=6, ge=1, le=168)
    limite: int = Field(default=20, ge=1, le=50)


class DeviceContextArgs(ToolArgs):
    device_id: str = Field(pattern=SAFE_ID)


class DevicesByAntennaArgs(ToolArgs):
    antena: str = Field(pattern=SAFE_ID)


TOOL_MODELS = {
    "list_sensors": ListSensorsArgs,
    "get_sensor_history": SensorHistoryArgs,
    "get_device_context": DeviceContextArgs,
    "get_devices_by_antenna": DevicesByAntennaArgs,
}


class ToolValidationError(Exception):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


def parse_tool_args(name: str, raw_arguments: str) -> BaseModel:
    """Convierte el JSON del LLM en un modelo validado o lanza error tipado."""
    modelo = TOOL_MODELS.get(name)
    if modelo is None:
        raise ToolValidationError(
            "unknown_tool",
            f"La herramienta '{name}' no está permitida.",
        )
    if not isinstance(raw_arguments, str) or not raw_arguments.strip():
        raise ToolValidationError(
            "invalid_args",
            "Los argumentos deben ser un objeto JSON no vacío.",
        )
    try:
        data = json.loads(raw_arguments)
    except json.JSONDecodeError as exc:
        raise ToolValidationError(
            "invalid_args",
            "Los argumentos no son JSON válido.",
        ) from exc
    if not isinstance(data, dict):
        raise ToolValidationError(
            "invalid_args",
            "Los argumentos deben ser un objeto JSON.",
        )
    try:
        return modelo.model_validate(data)
    except ValidationError as exc:
        detalles = "; ".join(
            f"{'.'.join(str(parte) for parte in error['loc'])}: {error['msg']}"
            for error in exc.errors()
        )
        raise ToolValidationError(
            "invalid_args",
            f"Argumentos inválidos: {detalles}",
        ) from exc
