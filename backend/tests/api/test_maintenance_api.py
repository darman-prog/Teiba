"""Contrato HTTP de mantenimientos, incidentes, elementos y operadores."""
from datetime import UTC, datetime

from bson import ObjectId

from app.api.deps import get_maintenance_service
from app.domain.maintenance import NotaRequerida, PermisoDenegado, TransicionInvalida

TAREA_ID = "671153000000000000000001"
INCIDENTE_ID = "671155000000000000000001"
OPERADOR_ID = "671154000000000000000002"

TAREA = {
    "_id": ObjectId(TAREA_ID),
    "tipo": "correctivo",
    "descripcion": "Ajustar tornillo del juego.",
    "prioridad": "alta",
    "estado": "pendiente",
    "fecha_programada": datetime(2026, 10, 30, 8, 0, tzinfo=UTC),
    "fecha_ejecucion": None,
    "fecha_reapertura": None,
    "nota_cierre": None,
    "nota_reapertura": None,
    "costo_estimado": 120000.0,
    "parque": {
        "id": ObjectId("671150000000000000000001"),
        "codigo": "PRQ-001",
        "nombre": "Parque San Pío",
    },
    "responsable": {
        "id": ObjectId(OPERADOR_ID),
        "nombre": "Óscar Operador",
        "rol": "operador_mantenimiento",
    },
    "incidente": {
        "id": ObjectId(INCIDENTE_ID),
        "tipo": "infraestructura",
        "descripcion": "Tornillo suelto",
        "prioridad": "alta",
        "estado": "reportado",
    },
    "elemento": {
        "id": ObjectId("671152000000000000000002"),
        "tipo_elemento": "juego_infantil",
        "cantidad": 3,
        "estado": "danado",
    },
}

INCIDENTE = {
    "_id": ObjectId(INCIDENTE_ID),
    "tipo": "infraestructura",
    "descripcion": "Tornillo suelto",
    "fecha_hora": datetime(2026, 10, 30, 10, 0, tzinfo=UTC),
    "estado": "reportado",
    "prioridad": "alta",
    "parque": {
        "id": ObjectId("671150000000000000000001"),
        "codigo": "PRQ-001",
        "nombre": "Parque San Pío",
    },
    "reportado_por": {"id": ObjectId("671154000000000000000004"), "nombre": "Carla Ciudadana"},
}

ELEMENTO = {
    "_id": ObjectId("671152000000000000000002"),
    "tipo_elemento": "juego_infantil",
    "cantidad": 3,
    "estado": "danado",
    "sector": {
        "id": ObjectId("671151000000000000000004"),
        "codigo": "SEC-004",
        "nombre": "Sector Bosque",
    },
}

OPERADOR = {"_id": ObjectId(OPERADOR_ID), "nombre": "Óscar Operador"}


class FakeService:
    def __init__(self):
        self.calls = []
        self.error = None
        self.vacio = False

    def _check(self):
        if self.error:
            raise self.error

    def listar(self, actor, **kwargs):
        self.calls.append(("listar", actor, kwargs))
        self._check()
        return [] if self.vacio else [TAREA]

    def detalle(self, actor, tarea_id):
        self.calls.append(("detalle", actor, tarea_id))
        self._check()
        return None if self.vacio else TAREA

    def crear(self, actor, nueva):
        self.calls.append(("crear", actor, nueva))
        self._check()
        return TAREA

    def cambiar_estado(self, actor, tarea_id, cambio):
        self.calls.append(("estado", actor, tarea_id, cambio))
        self._check()
        return None if self.vacio else TAREA

    def reasignar(self, actor, tarea_id, responsable_id):
        self.calls.append(("reasignar", actor, tarea_id, responsable_id))
        self._check()
        return None if self.vacio else TAREA

    def listar_operadores(self, actor):
        self.calls.append(("operadores", actor))
        self._check()
        return [] if self.vacio else [OPERADOR]

    def listar_incidentes(self, actor, **kwargs):
        self.calls.append(("incidentes", actor, kwargs))
        self._check()
        return [] if self.vacio else [INCIDENTE]

    def cambiar_estado_incidente(self, actor, incidente_id, estado):
        self.calls.append(("estado_incidente", actor, incidente_id, estado))
        self._check()
        return None if self.vacio else INCIDENTE

    def listar_elementos(self, actor, **kwargs):
        self.calls.append(("elementos", actor, kwargs))
        self._check()
        return [] if self.vacio else [ELEMENTO]


def _usar(client, service):
    client.app.dependency_overrides[get_maintenance_service] = lambda: service
    return service


def test_anonimo_401(client, _auth_env):
    assert client.get("/api/mantenimientos").status_code == 401


def test_admin_lista_y_serializa(authed_admin):
    service = _usar(authed_admin, FakeService())
    resp = authed_admin.get("/api/mantenimientos?parque=PRQ-001&prioridad=alta")

    assert resp.status_code == 200
    item = resp.json()["items"][0]
    assert item["id"] == TAREA_ID
    assert item["parque"]["codigo"] == "PRQ-001"
    assert item["responsable"]["nombre"] == "Óscar Operador"
    assert item["incidente"]["tipo"] == "infraestructura"
    assert item["elemento"]["tipo_elemento"] == "juego_infantil"
    assert item["vencida"] is True
    assert service.calls[0][0] == "listar"
    assert service.calls[0][1].rol == "administrador"


def test_operador_lista_sus_tareas(authed_operator):
    service = _usar(authed_operator, FakeService())
    resp = authed_operator.get("/api/mantenimientos")
    assert resp.status_code == 200
    assert service.calls[0][1].rol == "operador_mantenimiento"


def test_user_no_accede_a_mantenimientos(authed_user):
    _usar(authed_user, FakeService())
    resp = authed_user.get("/api/mantenimientos")
    assert resp.status_code == 403
    assert resp.json()["code"] == "forbidden"


def test_operador_no_crea_tareas(authed_operator):
    _usar(authed_operator, FakeService())
    resp = authed_operator.post(
        "/api/mantenimientos",
        json={
            "tipo": "correctivo",
            "descripcion": "Ajustar",
            "fecha_programada": "2026-11-05T08:00:00Z",
            "parque_codigo": "PRQ-001",
            "responsable_id": OPERADOR_ID,
        },
        headers={"Origin": "http://testserver"},
    )
    assert resp.status_code == 403


def test_admin_crea_tarea(authed_admin):
    service = _usar(authed_admin, FakeService())
    resp = authed_admin.post(
        "/api/mantenimientos",
        json={
            "tipo": "correctivo",
            "descripcion": "Ajustar",
            "fecha_programada": "2026-11-05T08:00:00Z",
            "prioridad": "alta",
            "parque_codigo": "PRQ-001",
            "responsable_id": OPERADOR_ID,
            "incidente_id": INCIDENTE_ID,
        },
        headers={"Origin": "http://testserver"},
    )
    assert resp.status_code == 201
    assert service.calls[0][0] == "crear"
    assert service.calls[0][2].parque_codigo == "PRQ-001"
    assert service.calls[0][2].prioridad == "alta"


def test_admin_cambia_estado_y_reasigna(authed_admin):
    service = _usar(authed_admin, FakeService())
    estado = authed_admin.patch(
        f"/api/mantenimientos/{TAREA_ID}/estado",
        json={"estado": "en_proceso"},
        headers={"Origin": "http://testserver"},
    )
    assert estado.status_code == 200
    assert service.calls[0][0] == "estado"

    reasignada = authed_admin.patch(
        f"/api/mantenimientos/{TAREA_ID}/responsable",
        json={"responsable_id": OPERADOR_ID},
        headers={"Origin": "http://testserver"},
    )
    assert reasignada.status_code == 200
    assert service.calls[1][0] == "reasignar"


def test_detalle_inexistente_404(authed_admin):
    service = _usar(authed_admin, FakeService())
    service.vacio = True
    assert authed_admin.get(f"/api/mantenimientos/{TAREA_ID}").status_code == 404


def test_errores_de_dominio_se_mapean(authed_admin):
    service = _usar(authed_admin, FakeService())
    service.error = PermisoDenegado("No puedes")
    assert authed_admin.get("/api/mantenimientos").status_code == 403

    service.error = TransicionInvalida("No se puede")
    resp = authed_admin.patch(
        f"/api/mantenimientos/{TAREA_ID}/estado",
        json={"estado": "finalizado", "nota": "x"},
        headers={"Origin": "http://testserver"},
    )
    assert resp.status_code == 409
    assert resp.json()["code"] == "invalid_transition"

    service.error = NotaRequerida("Falta la nota")
    resp = authed_admin.patch(
        f"/api/mantenimientos/{TAREA_ID}/estado",
        json={"estado": "finalizado"},
        headers={"Origin": "http://testserver"},
    )
    assert resp.status_code == 422


def test_admin_operadores_incidentes_y_elementos(authed_admin):
    _usar(authed_admin, FakeService())
    operadores = authed_admin.get("/api/operadores")
    assert operadores.status_code == 200
    assert operadores.json()["items"][0]["nombre"] == "Óscar Operador"

    incidentes = authed_admin.get("/api/incidentes?parque=PRQ-001")
    assert incidentes.status_code == 200
    assert incidentes.json()["items"][0]["reportado_por"]["nombre"] == "Carla Ciudadana"

    estado = authed_admin.patch(
        f"/api/incidentes/{INCIDENTE_ID}/estado",
        json={"estado": "en_revision"},
        headers={"Origin": "http://testserver"},
    )
    assert estado.status_code == 200

    elementos = authed_admin.get("/api/elementos?parque=PRQ-001")
    assert elementos.status_code == 200
    assert elementos.json()["items"][0]["sector"]["codigo"] == "SEC-004"


def test_operador_no_ve_operadores_ni_incidentes(authed_operator):
    _usar(authed_operator, FakeService())
    assert authed_operator.get("/api/operadores").status_code == 403
    assert authed_operator.get("/api/incidentes").status_code == 403
    assert authed_operator.get("/api/elementos").status_code == 403
