"""Catálogo de sensores: estados ok, warning, danger y sin datos."""
from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from pymongo.errors import PyMongoError

from app.api.deps import get_device_repository, get_reading_repository

ORIGIN = "http://testserver"


def _login(client: TestClient, correo: str, contrasena: str) -> None:
    resp = client.post(
        "/api/auth/login",
        json={"correo": correo, "contrasena": contrasena},
        headers={"Origin": ORIGIN},
    )
    assert resp.status_code == 200, f"login test fallo: {resp.text}"


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


def test_sensores_estados(client, _auth_env):
    ahora = datetime.now(UTC)
    docs = [_device("SS-01"), _device("SS-02"), _device("SS-03")]
    readings = FakeReadings(
        latest={
            "SS-01": _lectura(6.8, ahora - timedelta(minutes=30)),
            "SS-02": _lectura(6.8, ahora - timedelta(hours=7)),
            "SS-03": _lectura(5.4, ahora - timedelta(minutes=30)),
        }
    )
    _override(client.app, FakeDevices(docs), readings)
    _login(client, "admin@teiba.local", "admin12345678")

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


def test_sensores_sin_datos(client, _auth_env):
    _override(client.app, FakeDevices([_device("SS-04")]), FakeReadings(latest={}))
    _login(client, "admin@teiba.local", "admin12345678")

    response = client.get("/api/sensores")

    assert response.status_code == 200
    item = response.json()["items"][0]
    assert item["estado"] == "sin_datos"
    assert item["ultima_lectura"] is None


def test_sensores_db_caida(client, _auth_env):
    _override(client.app, FakeDevices(error=PyMongoError("caída")), FakeReadings())
    _login(client, "admin@teiba.local", "admin12345678")

    response = client.get("/api/sensores")

    assert response.status_code == 503
    assert response.json()["code"] == "db_unavailable"


def test_sensores_tipo_invalido(client, _auth_env):
    _override(client.app, FakeDevices(), FakeReadings())
    _login(client, "admin@teiba.local", "admin12345678")

    response = client.get("/api/sensores?tipo=otro")

    assert response.status_code == 422
    assert response.json()["code"] == "invalid_request"


def test_sensores_limite_invalido(client, _auth_env):
    _override(client.app, FakeDevices(), FakeReadings())
    _login(client, "admin@teiba.local", "admin12345678")

    response = client.get("/api/sensores?limite=0")

    assert response.status_code == 422
    assert response.json()["code"] == "invalid_request"


def test_sensores_user_403(client, _auth_env):
    _override(client.app, FakeDevices([_device("SS-01")]), FakeReadings())
    _login(client, "user@teiba.local", "user12345678")
    response = client.get("/api/sensores?tipo=calidad_suelo")
    assert response.status_code == 403
    assert response.json()["code"] == "forbidden"


def test_sensores_sin_sesion_401(client, _auth_env):
    _override(client.app, FakeDevices([_device("SS-01")]), FakeReadings())
    response = client.get("/api/sensores?tipo=calidad_suelo")
    assert response.status_code == 401
    assert response.json()["code"] == "not_authenticated"
