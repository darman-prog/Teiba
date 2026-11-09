"""DTOs del contrato HTTP.

La API usa `snake_case`; los tipos del frontend espejan estos nombres.
"""
import re
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


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


class RegisterRequest(BaseModel):
    """Alta pública. El rol nunca viaja en el body: lo fija el servidor."""

    model_config = ConfigDict(extra="forbid")

    correo: str = Field(min_length=5, max_length=254)
    contrasena: str = Field(min_length=12, max_length=256)
    nombre: str | None = Field(default=None, max_length=80)

    @field_validator("correo")
    @classmethod
    def correo_valido(cls, v: str) -> str:
        limpio = v.strip().lower()
        if not _EMAIL_RE.match(limpio):
            raise ValueError("El correo no tiene un formato válido.")
        return limpio

    @field_validator("contrasena")
    @classmethod
    def contrasena_no_supera_72_bytes(cls, v: str) -> str:
        if len(v.encode("utf-8")) > 72:
            raise ValueError("La contraseña supera el límite de 72 bytes.")
        return v

    @field_validator("nombre")
    @classmethod
    def nombre_limpio(cls, v: str | None) -> str | None:
        if v is None:
            return None
        limpio = v.strip()
        return limpio or None


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


# --- Mantenimientos, incidentes e inventario ---

class MantenimientoParque(BaseModel):
    id: str
    codigo: str | None = None
    nombre: str


class MantenimientoResponsable(BaseModel):
    id: str
    nombre: str
    rol: str | None = None


class MantenimientoIncidente(BaseModel):
    id: str
    tipo: str | None = None
    descripcion: str | None = None
    prioridad: str | None = None
    estado: str | None = None


class MantenimientoElemento(BaseModel):
    id: str
    tipo_elemento: str | None = None
    cantidad: int | None = None
    estado: str | None = None


class MantenimientoItem(BaseModel):
    id: str
    tipo: Literal["preventivo", "correctivo"]
    descripcion: str
    prioridad: Literal["alta", "media", "baja"]
    estado: Literal["pendiente", "en_proceso", "finalizado"]
    fecha_programada: str | None = None
    fecha_ejecucion: str | None = None
    fecha_reapertura: str | None = None
    nota_cierre: str | None = None
    nota_reapertura: str | None = None
    costo_estimado: float | None = None
    vencida: bool = False
    parque: MantenimientoParque | None = None
    responsable: MantenimientoResponsable | None = None
    incidente: MantenimientoIncidente | None = None
    elemento: MantenimientoElemento | None = None


class MantenimientoListResponse(BaseModel):
    items: list[MantenimientoItem]
    total: int


class MantenimientoCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tipo: Literal["preventivo", "correctivo"]
    descripcion: str = Field(min_length=1, max_length=250)
    fecha_programada: datetime
    prioridad: Literal["alta", "media", "baja"] = "media"
    parque_codigo: str = Field(min_length=1, max_length=20)
    responsable_id: str = Field(min_length=1, max_length=40)
    elemento_id: str | None = Field(default=None, max_length=40)
    incidente_id: str | None = Field(default=None, max_length=40)
    costo_estimado: float | None = Field(default=None, ge=0)


class MantenimientoEstadoRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    estado: Literal["en_proceso", "finalizado"]
    nota: str | None = Field(default=None, max_length=300)


class MantenimientoReasignarRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    responsable_id: str = Field(min_length=1, max_length=40)


class OperadorItem(BaseModel):
    id: str
    nombre: str


class OperadorListResponse(BaseModel):
    items: list[OperadorItem]
    total: int


class IncidenteReportante(BaseModel):
    id: str
    nombre: str


class IncidenteItem(BaseModel):
    id: str
    tipo: str | None = None
    descripcion: str | None = None
    fecha_hora: str | None = None
    estado: Literal["reportado", "en_revision", "en_proceso", "resuelto"]
    prioridad: str | None = None
    parque: MantenimientoParque | None = None
    reportado_por: IncidenteReportante | None = None


class IncidenteListResponse(BaseModel):
    items: list[IncidenteItem]
    total: int


class IncidenteEstadoRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    estado: Literal["reportado", "en_revision", "en_proceso", "resuelto"]


class ElementoSector(BaseModel):
    id: str
    codigo: str | None = None
    nombre: str | None = None


class ElementoItem(BaseModel):
    id: str
    tipo_elemento: str | None = None
    cantidad: int | None = None
    estado: str | None = None
    sector: ElementoSector | None = None


class ElementoListResponse(BaseModel):
    items: list[ElementoItem]
    total: int
