"""Ciclo de vida de un incidente ciudadano."""
from enum import StrEnum

from app.domain.profiles import Actor, RolDominio


class EstadoIncidente(StrEnum):
    REPORTADO = "reportado"
    EN_REVISION = "en_revision"
    EN_PROCESO = "en_proceso"
    RESUELTO = "resuelto"


class TransicionIncidenteInvalida(ValueError):
    """El cambio de estado del incidente no está permitido."""


_TRANSICIONES = {
    EstadoIncidente.REPORTADO: {EstadoIncidente.EN_REVISION},
    EstadoIncidente.EN_REVISION: {EstadoIncidente.EN_PROCESO},
    EstadoIncidente.EN_PROCESO: {EstadoIncidente.RESUELTO},
    EstadoIncidente.RESUELTO: {EstadoIncidente.EN_PROCESO},
}


def puede_gestionar(actor: Actor) -> bool:
    return actor.rol == RolDominio.ADMINISTRADOR


def validar_transicion(actual: EstadoIncidente, destino: EstadoIncidente) -> None:
    if destino not in _TRANSICIONES[actual]:
        raise TransicionIncidenteInvalida(
            f"No se puede pasar el incidente de '{actual}' a '{destino}'."
        )
