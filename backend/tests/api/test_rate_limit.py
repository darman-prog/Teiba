"""El endpoint del agente responde 429 al superar el límite por minuto."""
from fastapi.testclient import TestClient

from app.api.deps import get_agent_runner
from app.config import get_settings
from app.main import create_app


class FakeRunner:
    def consultar(self, pregunta, trace_id):
        return {
            "respuesta": "ok",
            "trazas": [],
            "meta": {
                "modelo": "fake",
                "pasos": 1,
                "duracion_ms": 1,
                "cached": False,
                "trace_id": trace_id,
            },
        }


def test_rate_limit_por_minuto(monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_PER_MINUTE", "2")
    monkeypatch.setenv("RATE_LIMIT_CONCURRENT", "1")
    get_settings.cache_clear()
    app = create_app()
    app.dependency_overrides[get_agent_runner] = lambda: FakeRunner()

    try:
        with TestClient(app) as client:
            body = {"pregunta": "¿Cómo está el suelo?"}
            assert client.post("/api/agente/consulta", json=body).status_code == 200
            assert client.post("/api/agente/consulta", json=body).status_code == 200
            response = client.post("/api/agente/consulta", json=body)
    finally:
        get_settings.cache_clear()

    assert response.status_code == 429
    body = response.json()
    assert body["code"] == "rate_limited"
    assert body["traceId"]
    assert response.headers["Retry-After"]
