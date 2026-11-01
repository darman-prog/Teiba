"""Reglas de estado, permisos y notas de los mantenimientos.

El dominio no conoce HTTP, Mongo ni la sesión: recibe un `Actor` de negocio y
devuelve la transición normalizada o levanta un error tipado.
"""
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Literal

from app.domain.profiles import Actor, RolDominio

NOTA_MAX = 300


class TipoMantenimiento(StrEnum):
    PREVENTIVO = "preventivo"
    CORRECTIVO = "correctivo"


class Prioridad(StrEnum):
    ALTA = "alta"
    MEDIA = "media"
    BAJA = "baja"


class EstadoMantenimiento(StrEnum):
    PENDIENTE = "pendiente"
    EN_PROCESO = "en_proceso"
    FINALIZADO = "finalizado"


class ErrorMantenimiento(ValueError):
    """Base de errores de negocio de mantenimientos."""


class TransicionInvalida(ErrorMantenimiento):
    """El par de estados no existe en la máquina."""


class PermisoDenegado(ErrorMantenimiento):
    """El actor no puede ejecutar esa transición."""


class NotaRequerida(ErrorMantenimiento):
    """Finalizar o reabrir exige una nota no vacía."""


CampoNota = Literal["nota_cierre", "nota_reapertura"]

# Orden de presentación: alta primero, luego media y baja.
PRIORIDAD_ORDEN: dict[Prioridad, int] = {
    Prioridad.ALTA: 0,
    Prioridad.MEDIA: 1,
    Prioridad.BAJA: 2,
}

# Pares que la máquina reconoce, aunque no todos los roles puedan ejecutarlos.
_TRANSICIONES = {
    (EstadoMantenimiento.PENDIENTE, EstadoMantenimiento.EN_PROCESO),
    (EstadoMantenimiento.PENDIENTE, EstadoMantenimiento.FINALIZADO),
    (EstadoMantenimiento.EN_PROCESO, EstadoMantenimiento.FINALIZADO),
    (EstadoMantenimiento.FINALIZADO, EstadoMantenimiento.EN_PROCESO),
}


@dataclass(frozen=True)
class Transicion:
    """Resultado normalizado de un cambio de estado."""

    estado: EstadoMantenimiento
    campo_nota: CampoNota | None = None
    nota: str | None = None
    limpia_ejecucion: bool = False
    marca_reapertura: bool = False


def es_responsable(actor: Actor, responsable_id: str) -> bool:
    """El operador solo actúa sobre tareas asignadas a su perfil Mongo."""
    return actor.rol == RolDominio.OPERADOR_MANTENIMIENTO and actor.perfil_id == responsable_id


def puede_ver_tarea(actor: Actor, responsable_id: str) -> bool:
    if actor.rol == RolDominio.ADMINISTRADOR:
        return True
    return es_responsable(actor, responsable_id)


def puede_crear(actor: Actor) -> bool:
    return actor.rol == RolDominio.ADMINISTRADOR


def puede_reasignar(actor: Actor, estado: EstadoMantenimiento) -> bool:
    return actor.rol == RolDominio.ADMINISTRADOR and estado in {
        EstadoMantenimiento.PENDIENTE,
        EstadoMantenimiento.EN_PROCESO,
    }


def puede_gestionar_incidentes(actor: Actor) -> bool:
    return actor.rol == RolDominio.ADMINISTRADOR


def validar_nota(nota: str | None) -> str:
    """Normaliza una nota obligatoria; vacía o demasiado larga es error."""
    limpia = (nota or "").strip()
    if not limpia:
        raise NotaRequerida("La nota es obligatoria para este cambio de estado.")
    if len(limpia) > NOTA_MAX:
        raise ErrorMantenimiento(f"La nota no puede superar {NOTA_MAX} caracteres.")
    return limpia


def validar_transicion(
    *,
    actor: Actor,
    estado_actual: EstadoMantenimiento,
    destino: EstadoMantenimiento,
    responsable_id: str,
    nota: str | None,
) -> Transicion:
    """Valida rol, responsabilidad, estado y nota; devuelve el cambio a aplicar."""
    if (estado_actual, destino) not in _TRANSICIONES:
        raise TransicionInvalida(
            f"No se puede pasar de '{estado_actual}' a '{destino}'."
        )

    if actor.rol == RolDominio.CIUDADANO:
        raise PermisoDenegado("El ciudadano no puede cambiar tareas de mantenimiento.")

    if destino is EstadoMantenimiento.EN_PROCESO:
        if estado_actual is EstadoMantenimiento.PENDIENTE:
            if not es_responsable(actor, responsable_id):
                raise PermisoDenegado("Solo el operador asignado puede iniciar la tarea.")
            return Transicion(estado=destino)

        # Reapertura: solo admin y con motivo.
        if actor.rol != RolDominio.ADMINISTRADOR:
            raise PermisoDenegado("Solo el administrador puede reabrir una tarea.")
        nota_limpia = validar_nota(nota)
        return Transicion(
            estado=destino,
            campo_nota="nota_reapertura",
            nota=nota_limpia,
            limpia_ejecucion=True,
            marca_reapertura=True,
        )

    # destino == FINALIZADO
    if estado_actual is EstadoMantenimiento.PENDIENTE:
        if actor.rol != RolDominio.ADMINISTRADOR:
            raise PermisoDenegado("El operador debe iniciar la tarea antes de finalizarla.")
    elif not es_responsable(actor, responsable_id) and actor.rol != RolDominio.ADMINISTRADOR:
        raise PermisoDenegado("Solo el operador asignado o el administrador pueden finalizar.")

    nota_limpia = validar_nota(nota)
    return Transicion(
        estado=destino,
        campo_nota="nota_cierre",
        nota=nota_limpia,
    )


def calcular_vencida(
    estado: EstadoMantenimiento,
    fecha_programada: datetime,
    ahora: datetime,
) -> bool:
    """Una tarea no finalizada cuya fecha programada ya pasó está vencida."""
    if estado is EstadoMantenimiento.FINALIZADO:
        return False
    fecha = fecha_programada if fecha_programada.tzinfo else fecha_programada.replace(tzinfo=UTC)
    referencia = ahora if ahora.tzinfo else ahora.replace(tzinfo=UTC)
    return fecha < referencia
