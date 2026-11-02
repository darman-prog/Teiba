"""DTOs del contrato HTTP.

La API usa `snake_case`; los tipos del frontend espejan estos nombres.
"""
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class MongoHealth(BaseModel):
    ok: bool
    db: str


class LlmHealth(BaseModel):
    configurado: bool
    modelo: str


class AuthHealth(BaseModel):
    ok: bool


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    mongo: MongoHealth
    llm: LlmHealth
    auth: AuthHealth
    version: str


class LoginRequest(BaseModel):
    """Credenciales para el login. bcrypt trunca a 72 bytes; se valida en UTF-8."""

    model_config = ConfigDict(extra="forbid")

    correo: str = Field(min_length=3, max_length=254)
    contrasena: str = Field(min_length=1, max_length=256)

    @field_validator("contrasena")
    @classmethod
    def contrasena_no_supera_72_bytes(cls, v: str) -> str:
        if len(v.encode("utf-8")) > 72:
            raise ValueError("La contraseña supera el límite de 72 bytes.")
        return v


class AuthUser(BaseModel):
    correo: str
    rol: Literal["admin", "operator", "user"]


class PerfilUsuario(BaseModel):
    """Perfil de negocio de Mongo; auth solo lo lee y nunca expone PII extra."""

    id: str
    nombre: str
    correo: str
    rol: Literal["administrador", "operador_mantenimiento", "ciudadano"]


class SessionResponse(BaseModel):
    usuario: AuthUser
    perfil: PerfilUsuario | None = None
    expira_en: str


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


class ParqueResumen(BaseModel):
    codigo: str
    nombre: str
    comuna: str | None = None
    direccion: str | None = None
    area_m2: float | None = None
    tipo_parque: str | None = None
    estado_general: str | None = None
    total_sectores: int = 0


class ParqueSector(BaseModel):
    codigo: str | None = None
    nombre: str
    tipo_suelo: str | None = None
    zona_riesgo: str | None = None


class Indicacion(BaseModel):
    nivel: Literal["info", "warning"]
    mensaje: str


class ParqueDetalle(BaseModel):
    codigo: str
    nombre: str
    comuna: str | None = None
    direccion: str | None = None
    area_m2: float | None = None
    tipo_parque: str | None = None
    estado_general: str | None = None
    sectores: list[ParqueSector] = []
    indicaciones: list[Indicacion] = []


class ParqueListResponse(BaseModel):
    items: list[ParqueResumen]
    total: int
