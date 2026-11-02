"""Servicio de mantenimientos: validaciones, alcance por rol y transiciones."""
from datetime import UTC, datetime

import pytest
from bson import ObjectId

from app.application.maintenance import CambioEstado, MaintenanceService, NuevaTarea
from app.domain.incidents import TransicionIncidenteInvalida
from app.domain.maintenance import (
    ErrorMantenimiento,
    NotaRequerida,
    PermisoDenegado,
)
from app.domain.profiles import Actor, RolDominio

AHORA = datetime(2026, 10, 31, 12, 0, tzinfo=UTC)
PARQUE_ID = ObjectId("671150000000000000000001")
OTRO_PARQUE_ID = ObjectId("671150000000000000000099")
ADMIN_ID = ObjectId("671154000000000000000001")
OPERADOR_ID = ObjectId("671154000000000000000002")
OTRO_ID = ObjectId("671154000000000000000003")
ELEMENTO_ID = ObjectId("671152000000000000000002")
INCIDENTE_ID = ObjectId("671155000000000000000001")

ADMIN = Actor(perfil_id=str(ADMIN_ID), correo="admin@teiba.local", rol=RolDominio.ADMINISTRADOR)
OPERADOR = Actor(
    perfil_id=str(OPERADOR_ID),
    correo="operador@teiba.local",
    rol=RolDominio.OPERADOR_MANTENIMIENTO,
)


class FakeClock:
    def now(self):
        return AHORA


class FakeParques:
    def get_parque_id(self, codigo):
        return PARQUE_ID if codigo == "PRQ-001" else None

    def list_parques(self):
        return []

    def get_parque(self, codigo):
        return None


class FakePerfiles:
    def __init__(self):
        self.perfiles = {
            str(ADMIN_ID): {"_id": ADMIN_ID, "nombre": "Ana", "rol": "administrador"},
            str(OPERADOR_ID): {
                "_id": OPERADOR_ID,
                "nombre": "Óscar",
                "rol": "operador_mantenimiento",
            },
            str(OTRO_ID): {
                "_id": OTRO_ID,
                "nombre": "Olga",
                "rol": "operador_mantenimiento",
            },
        }

    def get_by_id(self, perfil_id):
        return self.perfiles.get(str(perfil_id))

    def get_by_correo(self, correo):
        return None

    def list_operadores(self):
        return [p for p in self.perfiles.values() if p["rol"] == "operador_mantenimiento"]


class FakeIncidentes:
    def __init__(self):
        self.incidente = {
            "_id": INCIDENTE_ID,
            "parque_id": PARQUE_ID,
            "estado": "reportado",
            "prioridad": "alta",
            "tipo": "infraestructura",
        }

    def get_incidente(self, incidente_id):
        return self.incidente if str(incidente_id) == str(INCIDENTE_ID) else None

    def list_incidentes(self, **kwargs):
        return [self.incidente]

    def update_estado(self, incidente_id, estado):
        self.incidente["estado"] = estado
        return self.incidente

    def ensure_indexes(self):
        return None


class FakeInventario:
    def __init__(self):
        self.elemento = {
            "_id": ELEMENTO_ID,
            "parque_id": PARQUE_ID,
            "tipo_elemento": "juego_infantil",
            "cantidad": 3,
            "estado": "danado",
        }

    def get_elemento(self, elemento_id):
        return self.elemento if str(elemento_id) == str(ELEMENTO_ID) else None

    def list_elementos(self, **kwargs):
        return [self.elemento]

    def ensure_indexes(self):
        return None


class FakeTareas:
    def __init__(self):
        self.docs = {}
        self.ultimo_filtro = None

    def _doc(self, tarea_id):
        return self.docs.get(str(tarea_id))

    def list_tareas(self, **kwargs):
        self.ultimo_filtro = kwargs
        docs = list(self.docs.values())
        if kwargs.get("responsable_id"):
            docs = [d for d in docs if str(d["responsable_id"]) == str(kwargs["responsable_id"])]
        return docs

    def get_tarea(self, tarea_id):
        return self._doc(tarea_id)

    def create_tarea(self, doc):
        tarea_id = ObjectId()
        self.docs[str(tarea_id)] = {**doc, "_id": tarea_id}
        return tarea_id

    def update_estado(
        self,
        tarea_id,
        *,
        estado,
        campo_nota,
        nota,
        limpia_ejecucion,
        marca_reapertura,
        ahora,
    ):
        doc = self._doc(tarea_id)
        if doc is None:
            return None
        doc["estado"] = estado
        if campo_nota and nota is not None:
            doc[campo_nota] = nota
        if estado == "finalizado":
            doc["fecha_ejecucion"] = ahora
        if limpia_ejecucion:
            doc["fecha_ejecucion"] = None
        if marca_reapertura:
            doc["fecha_reapertura"] = ahora
        return doc

    def reasignar(self, tarea_id, responsable_id):
        doc = self._doc(tarea_id)
        if doc is None:
            return None
        doc["responsable_id"] = ObjectId(responsable_id)
        return doc

    def ensure_indexes(self):
        return None


def _service():
    tareas = FakeTareas()
    return (
        MaintenanceService(
            tareas=tareas,
            perfiles=FakePerfiles(),
            incidentes=FakeIncidentes(),
            inventario=FakeInventario(),
            parques=FakeParques(),
            clock=FakeClock(),
        ),
        tareas,
    )


def _nueva(**kwargs):
    data = {
        "tipo": "correctivo",
        "descripcion": "Ajustar tornillo",
        "fecha_programada": AHORA,
        "prioridad": "alta",
        "parque_codigo": "PRQ-001",
        "responsable_id": str(OPERADOR_ID),
    }
    data.update(kwargs)
    return NuevaTarea(**data)


def _tarea(service, tareas, estado="pendiente"):
    tarea_id = tareas.create_tarea(
        {
            "tipo": "correctivo",
            "descripcion": "Ajustar",
            "fecha_programada": AHORA,
            "fecha_ejecucion": None,
            "estado": estado,
            "prioridad": "alta",
            "nota_cierre": None,
            "nota_reapertura": None,
            "fecha_reapertura": None,
            "incidente_id": None,
            "parque_id": PARQUE_ID,
            "elemento_id": None,
            "responsable_id": OPERADOR_ID,
            "costo_estimado": None,
        }
    )
    return str(tarea_id)


def test_admin_crea_tarea_con_vinculos():
    service, _ = _service()
    doc = service.crear(
        ADMIN,
        _nueva(elemento_id=str(ELEMENTO_ID), incidente_id=str(INCIDENTE_ID)),
    )
    assert doc["estado"] == "pendiente"
    assert doc["parque_id"] == PARQUE_ID
    assert doc["responsable_id"] == OPERADOR_ID
    assert doc["elemento_id"] == ELEMENTO_ID
    assert doc["incidente_id"] == INCIDENTE_ID
    assert doc["nota_cierre"] is None


def test_operador_no_crea_tareas():
    service, _ = _service()
    with pytest.raises(PermisoDenegado):
        service.crear(OPERADOR, _nueva())


def test_operador_lista_solo_sus_tareas():
    service, tareas = _service()
    service.listar(OPERADOR)
    assert tareas.ultimo_filtro["responsable_id"] == OPERADOR.perfil_id

    service.listar(ADMIN, responsable_id=str(OTRO_ID))
    assert tareas.ultimo_filtro["responsable_id"] == str(OTRO_ID)


def test_vinculos_de_otro_parque_se_rechazan():
    service, _ = _service()
    service._inventario.elemento["parque_id"] = OTRO_PARQUE_ID
    with pytest.raises(ErrorMantenimiento):
        service.crear(ADMIN, _nueva(elemento_id=str(ELEMENTO_ID)))


def test_incidente_resuelto_no_se_vincula():
    service, _ = _service()
    service._incidentes.incidente["estado"] = "resuelto"
    with pytest.raises(ErrorMantenimiento):
        service.crear(ADMIN, _nueva(incidente_id=str(INCIDENTE_ID)))


def test_operador_inicia_y_finaliza_su_tarea():
    service, tareas = _service()
    tarea_id = _tarea(service, tareas)

    inicio = service.cambiar_estado(OPERADOR, tarea_id, CambioEstado("en_proceso"))
    assert inicio["estado"] == "en_proceso"

    fin = service.cambiar_estado(
        OPERADOR,
        tarea_id,
        CambioEstado("finalizado", "Tornillo ajustado."),
    )
    assert fin["estado"] == "finalizado"
    assert fin["fecha_ejecucion"] == AHORA
    assert fin["nota_cierre"] == "Tornillo ajustado."


def test_finalizar_sin_nota_falla():
    service, tareas = _service()
    tarea_id = _tarea(service, tareas, estado="en_proceso")
    with pytest.raises(NotaRequerida):
        service.cambiar_estado(OPERADOR, tarea_id, CambioEstado("finalizado"))


def test_admin_reabre_y_operador_no():
    service, tareas = _service()
    tarea_id = _tarea(service, tareas, estado="finalizado")
    reabierta = service.cambiar_estado(
        ADMIN,
        tarea_id,
        CambioEstado("en_proceso", "El trabajo quedó mal."),
    )
    assert reabierta["estado"] == "en_proceso"
    assert reabierta["fecha_ejecucion"] is None
    assert reabierta["nota_reapertura"] == "El trabajo quedó mal."

    otra_finalizada = _tarea(service, tareas, estado="finalizado")
    with pytest.raises(PermisoDenegado):
        service.cambiar_estado(
            OPERADOR,
            otra_finalizada,
            CambioEstado("en_proceso", "No puedo reabrir."),
        )


def test_reasignar_solo_admin_y_solo_abiertas():
    service, tareas = _service()
    tarea_id = _tarea(service, tareas)
    reasignada = service.reasignar(ADMIN, tarea_id, str(OTRO_ID))
    assert reasignada["responsable_id"] == OTRO_ID

    with pytest.raises(PermisoDenegado):
        service.reasignar(OPERADOR, tarea_id, str(OTRO_ID))

    finalizada = _tarea(service, tareas, estado="finalizado")
    with pytest.raises(PermisoDenegado):
        service.reasignar(ADMIN, finalizada, str(OTRO_ID))


def test_incidente_cambia_solo_admin_y_transicion_valida():
    service, _ = _service()
    actualizado = service.cambiar_estado_incidente(ADMIN, str(INCIDENTE_ID), "en_revision")
    assert actualizado["estado"] == "en_revision"

    with pytest.raises(PermisoDenegado):
        service.cambiar_estado_incidente(OPERADOR, str(INCIDENTE_ID), "en_proceso")

    with pytest.raises(TransicionIncidenteInvalida):
        service.cambiar_estado_incidente(ADMIN, str(INCIDENTE_ID), "resuelto")


def test_operadores_y_elementos_solo_admin():
    service, _ = _service()
    assert len(service.listar_operadores(ADMIN)) == 2
    assert len(service.listar_elementos(ADMIN, parque_codigo="PRQ-001")) == 1
    with pytest.raises(PermisoDenegado):
        service.listar_operadores(OPERADOR)
