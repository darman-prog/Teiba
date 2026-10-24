"""DTOs del contrato HTTP.

La API usa `snake_case`; los tipos del frontend espejan estos nombres.
"""
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class MongoHealth(BaseModel):
    ok: bool
    db: str


class LlmHealth(BaseModel):
    configurado: bool
    modelo: str


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    mongo: MongoHealth
    llm: LlmHealth
    version: str


class ConsultaRequest(BaseModel):
    """Pregunta del operador al agente Sage."""

    model_config = ConfigDict(extra="forbid")

    pregunta: str = Field(min_length=3, max_length=500)


class TraceItem(BaseModel):
    tool: str
    args: dict[str, Any]
    ok: bool
    ms: int
    resumen: str
    resultado: Any | None = None


class ConsultaMeta(BaseModel):
    modelo: str
    pasos: int
    duracion_ms: int
    cached: bool = False
    trace_id: str


class ConsultaResponse(BaseModel):
    respuesta: str
    trazas: list[TraceItem]
    meta: ConsultaMeta


class UltimaLectura(BaseModel):
    timestamp: str | None = None
    humedad: float | None = None
    ph: float | None = None
    temperatura: float | None = None
    bateria: int | None = None
    antiguedad_min: int | None = None


class SensorItem(BaseModel):
    id: str
    tipo: str
    marca: str | None = None
    sector: str | None = None
    sector_id: str | None = None
    parque: str | None = None
    comuna: str | None = None
    depende_de: str | None = None
    alimentado_por: str | None = None
    ultima_lectura: UltimaLectura | None = None
    estado: Literal["ok", "warning", "danger", "sin_datos"]


class SensorListResponse(BaseModel):
    items: list[SensorItem]
    total: int
