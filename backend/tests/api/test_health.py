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
    assert body["auth"]["ok"] is True
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


def test_health_degraded_sin_auth(client, monkeypatch, tmp_path):
    # Forzamos que SQLite falle parcheando la disponibilidad directamente,
    # porque BaseAuth auto-crea el directorio de la BD.
    import app.infrastructure.sqlite_auth as sqlite_auth
    monkeypatch.setattr(sqlite_auth.BaseAuth, "esta_disponible", lambda self: False)
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["auth"]["ok"] is False
    assert response.json()["status"] == "degraded"


def test_trace_id_se_respeta(client):
    response = client.get(
        "/api/health",
        headers={"X-Request-Id": "trace-de-prueba"},
    )

    assert response.headers["X-Trace-Id"] == "trace-de-prueba"
