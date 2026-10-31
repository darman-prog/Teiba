"""Libro de parques: lista, ficha con sectores e indicaciones, y errores."""
from fastapi.testclient import TestClient
from pymongo.errors import PyMongoError

from app.api.deps import get_park_repository


def _parque() -> dict:
    return {
        "codigo": "PRQ-001",
        "nombre": "Parque San Pío",
        "comuna": "Comuna 12 - Cabecera del Llano",
        "direccion": "Carrera 33 con Calle 45",
        "area_m2": 15400.0,
        "tipo_parque": "recreativo",
        "estado_general": "bueno",
        "total_sectores": 2,
    }


def _detalle() -> dict:
    return {
        **{k: v for k, v in _parque().items() if k != "total_sectores"},
        "sectores": [
            {
                "codigo": "SEC-001",
                "nombre": "Sector Norte - Jardines",
                "tipo_suelo": "césped natural",
                "zona_riesgo": "baja",
            },
            {
                "codigo": "SEC-002",
                "nombre": "Sector Sur - Plazoleta",
                "tipo_suelo": "pavimento blando",
                "zona_riesgo": "media",
            },
        ],
    }


class FakeParks:
    def __init__(self, docs=None, detalle=None, error=None):
        self.docs = docs if docs is not None else [_parque()]
        self.detalle = detalle if detalle is not None else _detalle()
        self.error = error

    def list_parques(self):
        if self.error:
            raise self.error
        return self.docs

    def get_parque(self, codigo):
        if self.error:
            raise self.error
        return self.detalle if codigo == "PRQ-001" else None


def _override(app, repo):
    app.dependency_overrides[get_park_repository] = lambda: repo


def test_parques_lista_ok(app):
    _override(app, FakeParks())

    with TestClient(app) as client:
        response = client.get("/api/parques")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    item = body["items"][0]
    assert item["codigo"] == "PRQ-001"
    assert item["comuna"] == "Comuna 12 - Cabecera del Llano"
    assert item["total_sectores"] == 2


def test_parques_ficha_ok(app):
    _override(app, FakeParks())

    with TestClient(app) as client:
        response = client.get("/api/parques/PRQ-001")

    assert response.status_code == 200
    body = response.json()
    assert [sector["codigo"] for sector in body["sectores"]] == ["SEC-001", "SEC-002"]
    assert body["indicaciones"]
    assert all("mensaje" in item for item in body["indicaciones"])


def test_parques_no_encontrado(app):
    _override(app, FakeParks())

    with TestClient(app) as client:
        response = client.get("/api/parques/PRQ-999")

    assert response.status_code == 404
    assert response.json()["code"] == "not_found"


def test_parques_codigo_invalido(app):
    _override(app, FakeParks())

    with TestClient(app) as client:
        response = client.get("/api/parques/PRQ..001??")

    assert response.status_code == 422
    assert response.json()["code"] == "invalid_request"


def test_parques_db_caida(app):
    _override(app, FakeParks(error=PyMongoError("caída")))

    with TestClient(app) as client:
        response = client.get("/api/parques")

    assert response.status_code == 503
    assert response.json()["code"] == "db_unavailable"
