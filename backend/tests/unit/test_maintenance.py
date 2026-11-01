"""Reglas de negocio de mantenimientos: estados, permisos y notas."""
from datetime import UTC, datetime

import pytest

from app.domain.incidents import (
    EstadoIncidente,
    TransicionIncidenteInvalida,
    puede_gestionar,
)
from app.domain.incidents import (
    validar_transicion as validar_incidente,
)
from app.domain.maintenance import (
    PRIORIDAD_ORDEN,
    EstadoMantenimiento,
    NotaRequerida,
    PermisoDenegado,
    Prioridad,
    TransicionInvalida,
    calcular_vencida,
    puede_crear,
    puede_reasignar,
    puede_ver_tarea,
    validar_nota,
    validar_transicion,
)
from app.domain.profiles import Actor, RolDominio

ADMIN = Actor(perfil_id="admin-mongo", correo="admin@teiba.local", rol=RolDominio.ADMINISTRADOR)
OPERADOR = Actor(
    perfil_id="operador-mongo",
    correo="operador@teiba.local",
    rol=RolDominio.OPERADOR_MANTENIMIENTO,
)
OTRO_OPERADOR = Actor(
    perfil_id="otro-mongo",
    correo="otro@teiba.local",
    rol=RolDominio.OPERADOR_MANTENIMIENTO,
)
CIUDADANO = Actor(
    perfil_id="ciudadano-mongo",
    correo="ciudadano@teiba.local",
    rol=RolDominio.CIUDADANO,
)

AHORA = datetime(2026, 10, 31, 12, 0, tzinfo=UTC)


def _transicion(actor, actual, destino, responsable=OPERADOR.perfil_id, nota=None):
    return validar_transicion(
        actor=actor,
        estado_actual=actual,
        destino=destino,
        responsable_id=responsable,
        nota=nota,
    )


def test_admin_finaliza_desde_pendiente_y_en_proceso():
    desde_pendiente = _transicion(
        ADMIN,
        EstadoMantenimiento.PENDIENTE,
        EstadoMantenimiento.FINALIZADO,
        nota="  cierre externo  ",
    )
    assert desde_pendiente.estado is EstadoMantenimiento.FINALIZADO
    assert desde_pendiente.campo_nota == "nota_cierre"
    assert desde_pendiente.nota == "cierre externo"
    assert desde_pendiente.limpia_ejecucion is False

    desde_proceso = _transicion(
        ADMIN, EstadoMantenimiento.EN_PROCESO, EstadoMantenimiento.FINALIZADO, nota="listo"
    )
    assert desde_proceso.estado is EstadoMantenimiento.FINALIZADO


def test_admin_reabre_con_nota_y_limpia_ejecucion():
    cambio = _transicion(
        ADMIN,
        EstadoMantenimiento.FINALIZADO,
        EstadoMantenimiento.EN_PROCESO,
        nota="trabajo incompleto",
    )
    assert cambio.estado is EstadoMantenimiento.EN_PROCESO
    assert cambio.campo_nota == "nota_reapertura"
    assert cambio.limpia_ejecucion is True
    assert cambio.marca_reapertura is True


def test_admin_no_inicia_tareas():
    with pytest.raises(PermisoDenegado):
        _transicion(ADMIN, EstadoMantenimiento.PENDIENTE, EstadoMantenimiento.EN_PROCESO)


def test_operador_inicia_y_finaliza_sus_tareas():
    inicio = _transicion(OPERADOR, EstadoMantenimiento.PENDIENTE, EstadoMantenimiento.EN_PROCESO)
    assert inicio.estado is EstadoMantenimiento.EN_PROCESO
    assert inicio.campo_nota is None

    fin = _transicion(
        OPERADOR, EstadoMantenimiento.EN_PROCESO, EstadoMantenimiento.FINALIZADO, nota="revisado"
    )
    assert fin.estado is EstadoMantenimiento.FINALIZADO
    assert fin.campo_nota == "nota_cierre"


def test_operador_no_finaliza_sin_iniciar():
    with pytest.raises(PermisoDenegado):
        _transicion(
            OPERADOR,
            EstadoMantenimiento.PENDIENTE,
            EstadoMantenimiento.FINALIZADO,
            nota="sin iniciar",
        )


def test_operador_no_reabre_ni_reasigna_ni_crea():
    with pytest.raises(PermisoDenegado):
        _transicion(
            OPERADOR,
            EstadoMantenimiento.FINALIZADO,
            EstadoMantenimiento.EN_PROCESO,
            nota="reapertura",
        )
    assert puede_reasignar(OPERADOR, EstadoMantenimiento.PENDIENTE) is False
    assert puede_crear(OPERADOR) is False
    assert puede_gestionar(OPERADOR) is False


def test_operador_ajeno_no_ve_ni_actua():
    assert puede_ver_tarea(OTRO_OPERADOR, OPERADOR.perfil_id) is False
    with pytest.raises(PermisoDenegado):
        _transicion(OTRO_OPERADOR, EstadoMantenimiento.PENDIENTE, EstadoMantenimiento.EN_PROCESO)


def test_ciudadano_no_ve_ni_crea_ni_cambia():
    assert puede_ver_tarea(CIUDADANO, OPERADOR.perfil_id) is False
    assert puede_crear(CIUDADANO) is False
    with pytest.raises(PermisoDenegado):
        _transicion(CIUDADANO, EstadoMantenimiento.PENDIENTE, EstadoMantenimiento.EN_PROCESO)


def test_admin_ve_todas_y_reasigna_solo_abiertas():
    assert puede_ver_tarea(ADMIN, "cualquiera") is True
    assert puede_reasignar(ADMIN, EstadoMantenimiento.PENDIENTE) is True
    assert puede_reasignar(ADMIN, EstadoMantenimiento.EN_PROCESO) is True
    assert puede_reasignar(ADMIN, EstadoMantenimiento.FINALIZADO) is False


@pytest.mark.parametrize(
    ("actual", "destino"),
    [
        (EstadoMantenimiento.PENDIENTE, EstadoMantenimiento.PENDIENTE),
        (EstadoMantenimiento.FINALIZADO, EstadoMantenimiento.PENDIENTE),
        (EstadoMantenimiento.EN_PROCESO, EstadoMantenimiento.PENDIENTE),
    ],
)
def test_pares_de_estado_invalidos(actual, destino):
    with pytest.raises(TransicionInvalida):
        _transicion(ADMIN, actual, destino, nota="x")


def test_nota_obligatoria_y_limite():
    with pytest.raises(NotaRequerida):
        validar_nota("   ")
    with pytest.raises(ValueError):
        validar_nota("x" * 301)
    assert validar_nota("  ok  ") == "ok"


def test_prioridad_alta_primero():
    assert PRIORIDAD_ORDEN[Prioridad.ALTA] < PRIORIDAD_ORDEN[Prioridad.MEDIA]
    assert PRIORIDAD_ORDEN[Prioridad.MEDIA] < PRIORIDAD_ORDEN[Prioridad.BAJA]


def test_vencida_solo_si_no_finalizo():
    pasada = datetime(2026, 10, 30, 8, 0, tzinfo=UTC)
    futura = datetime(2026, 11, 2, 8, 0, tzinfo=UTC)
    assert calcular_vencida(EstadoMantenimiento.PENDIENTE, pasada, AHORA) is True
    assert calcular_vencida(EstadoMantenimiento.EN_PROCESO, pasada, AHORA) is True
    assert calcular_vencida(EstadoMantenimiento.FINALIZADO, pasada, AHORA) is False
    assert calcular_vencida(EstadoMantenimiento.PENDIENTE, futura, AHORA) is False


def test_vencida_acepta_fechas_sin_zona():
    pasada = datetime(2026, 10, 30, 8, 0)
    assert calcular_vencida(EstadoMantenimiento.PENDIENTE, pasada, AHORA) is True


def test_incidentes_solo_admin_y_transiciones_validas():
    assert puede_gestionar(ADMIN) is True
    assert puede_gestionar(OPERADOR) is False

    validar_incidente(EstadoIncidente.REPORTADO, EstadoIncidente.EN_REVISION)
    validar_incidente(EstadoIncidente.EN_REVISION, EstadoIncidente.EN_PROCESO)
    validar_incidente(EstadoIncidente.EN_PROCESO, EstadoIncidente.RESUELTO)
    validar_incidente(EstadoIncidente.RESUELTO, EstadoIncidente.EN_PROCESO)

    with pytest.raises(TransicionIncidenteInvalida):
        validar_incidente(EstadoIncidente.REPORTADO, EstadoIncidente.RESUELTO)
