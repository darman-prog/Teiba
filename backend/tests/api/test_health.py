"""Contrato del endpoint de salud y del header de trazabilidad."""
from pydantic import SecretStr

from app import db as db_module
from app.config import get_settings


def test_health_ok(client, monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "opencode_api_key", SecretStr("test-key"))

    response = client.get("/api/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["mongo"] == {"ok": True, "db": settings.mongodb_db}
    assert body["llm"]["configurado"] is True
    assert response.headers["X-Trace-Id"]


def test_health_degraded_sin_llm(client, monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "opencode_api_key", None)

    response = client.get("/api/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "degraded"
    assert body["llm"]["configurado"] is False


def test_health_degraded_sin_mongo(client, monkeypatch):
    monkeypatch.setattr(db_module, "ping", lambda: False)

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["mongo"]["ok"] is False


def test_trace_id_se_respeta(client):
    response = client.get(
        "/api/health",
        headers={"X-Request-Id": "trace-de-prueba"},
    )

    assert response.headers["X-Trace-Id"] == "trace-de-prueba"
