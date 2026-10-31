"""Contrato del endpoint del agente y mapeo de errores."""
from fastapi.testclient import TestClient

from app.api.deps import _build_agent_runner, get_agent_runner
from app.config import get_settings

ORIGIN = "http://testserver"


class FakeRunner:
    def __init__(self):
        self.calls = []

    def consultar(self, pregunta, trace_id):
        self.calls.append((pregunta, trace_id))
        return {
            "respuesta": "El sensor SS-01 está en rango.",
            "trazas": [
                {
                    "tool": "list_sensors",
                    "args": {"tipo": "calidad_suelo"},
                    "ok": True,
                    "ms": 3,
                    "resumen": "1 dispositivos",
                    "resultado": '{"estado": "ok"}',
                }
            ],
            "meta": {
                "modelo": "fake",
                "pasos": 2,
                "duracion_ms": 10,
                "cached": False,
                "trace_id": trace_id,
            },
        }


def _login_admin(client: TestClient) -> None:
    resp = client.post(
        "/api/auth/login",
        json={"correo": "admin@teiba.local", "contrasena": "admin12345678"},
        headers={"Origin": ORIGIN},
    )
    assert resp.status_code == 200, f"login admin test fallo: {resp.text}"


def test_consulta_ok(client, _auth_env):
    fake = FakeRunner()
    client.app.dependency_overrides[get_agent_runner] = lambda: fake
    _login_admin(client)

    response = client.post(
        "/api/agente/consulta",
        json={"pregunta": "¿Cómo está suelo del Sector Norte?"},
        headers={"X-Request-Id": "trace-api", "Origin": ORIGIN},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["respuesta"].startswith("El sensor SS-01")
    assert body["trazas"][0]["tool"] == "list_sensors"
    assert body["meta"]["trace_id"] == "trace-api"
    assert fake.calls == [("¿Cómo está suelo del Sector Norte?", "trace-api")]


def test_consulta_sin_sesion_401(client, _auth_env):
    client.app.dependency_overrides[get_agent_runner] = lambda: FakeRunner()
    response = client.post(
        "/api/agente/consulta",
        json={"pregunta": "¿Cómo está el suelo?"},
        headers={"Origin": ORIGIN},
    )
    assert response.status_code == 401
    assert response.json()["code"] == "not_authenticated"


def test_consulta_pregunta_corta(client, _auth_env):
    client.app.dependency_overrides[get_agent_runner] = lambda: FakeRunner()
    _login_admin(client)
    response = client.post("/api/agente/consulta", json={"pregunta": "ab"}, headers={"Origin": ORIGIN})

    assert response.status_code == 422
    body = response.json()
    assert body["code"] == "invalid_request"
    assert body["traceId"]


def test_consulta_rechaza_campos_extra(client, _auth_env):
    client.app.dependency_overrides[get_agent_runner] = lambda: FakeRunner()
    _login_admin(client)
    response = client.post(
        "/api/agente/consulta",
        json={"pregunta": "¿Cómo está el suelo?", "extra": 1},
        headers={"Origin": ORIGIN},
    )

    assert response.status_code == 422
    assert response.json()["code"] == "invalid_request"


def test_sin_key_responde_503(client, _auth_env, monkeypatch):
    monkeypatch.setattr(get_settings(), "opencode_api_key", None)
    _build_agent_runner.cache_clear()
    _login_admin(client)

    response = client.post(
        "/api/agente/consulta",
        json={"pregunta": "¿Cómo está el suelo?"},
        headers={"Origin": ORIGIN},
    )

    assert response.status_code == 503
    body = response.json()
    assert body["code"] == "llm_not_configured"
    assert body["traceId"]
    assert "OPENCODE_API_KEY" in body["message"]
