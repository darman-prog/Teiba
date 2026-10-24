"""Catálogo de sensores: estados ok, warning, danger y sin datos."""
from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from pymongo.errors import PyMongoError

from app.api.deps import get_device_repository, get_reading_repository


def _device(device_id: str) -> dict:
    return {
        "_id": device_id,
        "tipo": "calidad_suelo",
        "marca": "SoilPro-Sense",
        "sector_id": "SEC-001",
        "sector": "Sector Norte - Jardines",
        "sector_codigo": "SEC-001",
        "parque": "Parque San Pío",
        "comuna": "Comuna 12",
        "depende_de": "ANT-01",
        "alimentado_por": "Panel_Solar_PS1",
    }


def _lectura(ph: float, cuando: datetime) -> dict:
    return {
        "timestamp": cuando,
        "humedad": 41.2,
        "ph": ph,
        "temperatura": 21.0,
        "bateria": 90,
    }


class FakeDevices:
    def __init__(self, docs=None, error=None):
        self.docs = docs or []
        self.error = error
        self.kwargs = None

    def find_devices(self, **kwargs):
        if self.error:
            raise self.error
        self.kwargs = kwargs
        return self.docs


class FakeReadings:
    def __init__(self, latest=None, error=None):
        self.latest = latest or {}
        self.error = error

    def latest_many(self, sensor_ids):
        if self.error:
            raise self.error
        return self.latest


def _override(app, devices, readings):
    app.dependency_overrides[get_device_repository] = lambda: devices
    app.dependency_overrides[get_reading_repository] = lambda: readings


def test_sensores_estados(app):
    ahora = datetime.now(UTC)
    docs = [_device("SS-01"), _device("SS-02"), _device("SS-03")]
    readings = FakeReadings(
        latest={
            "SS-01": _lectura(6.8, ahora - timedelta(minutes=30)),
            "SS-02": _lectura(6.8, ahora - timedelta(hours=7)),
            "SS-03": _lectura(5.4, ahora - timedelta(minutes=30)),
        }
    )
    _override(app, FakeDevices(docs), readings)

    with TestClient(app) as client:
        response = client.get("/api/sensores?tipo=calidad_suelo")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 3
    items = {item["id"]: item for item in body["items"]}
    assert items["SS-01"]["estado"] == "ok"
    assert items["SS-02"]["estado"] == "warning"
    assert items["SS-03"]["estado"] == "danger"
    assert items["SS-01"]["ultima_lectura"]["antiguedad_min"] >= 29
    assert items["SS-01"]["sector"].startswith("Sector Norte")
    assert items["SS-01"]["comuna"] == "Comuna 12"


def test_sensores_sin_datos(app):
    _override(app, FakeDevices([_device("SS-04")]), FakeReadings(latest={}))

    with TestClient(app) as client:
        response = client.get("/api/sensores")

    assert response.status_code == 200
    item = response.json()["items"][0]
    assert item["estado"] == "sin_datos"
    assert item["ultima_lectura"] is None


def test_sensores_db_caida(app):
    _override(app, FakeDevices(error=PyMongoError("caída")), FakeReadings())

    with TestClient(app) as client:
        response = client.get("/api/sensores")

    assert response.status_code == 503
    assert response.json()["code"] == "db_unavailable"


def test_sensores_tipo_invalido(app):
    _override(app, FakeDevices(), FakeReadings())

    with TestClient(app) as client:
        response = client.get("/api/sensores?tipo=otro")

    assert response.status_code == 422
    assert response.json()["code"] == "invalid_request"


def test_sensores_limite_invalido(app):
    _override(app, FakeDevices(), FakeReadings())

    with TestClient(app) as client:
        response = client.get("/api/sensores?limite=0")

    assert response.status_code == 422
