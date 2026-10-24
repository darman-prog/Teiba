"""Contrato del endpoint del agente y mapeo de errores."""
from fastapi.testclient import TestClient

from app.api.deps import _build_agent_runner, get_agent_runner
from app.config import get_settings


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


def test_consulta_ok(app):
    fake = FakeRunner()
    app.dependency_overrides[get_agent_runner] = lambda: fake

    with TestClient(app) as client:
        response = client.post(
            "/api/agente/consulta",
            json={"pregunta": "¿Cómo está el suelo del Sector Norte?"},
            headers={"X-Request-Id": "trace-api"},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["respuesta"].startswith("El sensor SS-01")
    assert body["trazas"][0]["tool"] == "list_sensors"
    assert body["meta"]["trace_id"] == "trace-api"
    assert fake.calls == [("¿Cómo está el suelo del Sector Norte?", "trace-api")]


def test_consulta_pregunta_corta(app):
    app.dependency_overrides[get_agent_runner] = lambda: FakeRunner()

    with TestClient(app) as client:
        response = client.post("/api/agente/consulta", json={"pregunta": "ab"})

    assert response.status_code == 422
    body = response.json()
    assert body["code"] == "invalid_request"
    assert body["traceId"]


def test_consulta_rechaza_campos_extra(app):
    app.dependency_overrides[get_agent_runner] = lambda: FakeRunner()

    with TestClient(app) as client:
        response = client.post(
            "/api/agente/consulta",
            json={"pregunta": "¿Cómo está el suelo?", "extra": 1},
        )

    assert response.status_code == 422
    assert response.json()["code"] == "invalid_request"


def test_sin_key_responde_503(app, monkeypatch):
    monkeypatch.setattr(get_settings(), "opencode_api_key", None)
    _build_agent_runner.cache_clear()

    with TestClient(app) as client:
        response = client.post(
            "/api/agente/consulta",
            json={"pregunta": "¿Cómo está el suelo?"},
        )

    assert response.status_code == 503
    body = response.json()
    assert body["code"] == "llm_not_configured"
    assert body["traceId"]
    assert "OPENCODE_API_KEY" in body["message"]
