"""El endpoint del agente responde 429 al superar el límite por minuto."""
from fastapi.testclient import TestClient

from app.api.deps import get_agent_runner

ORIGIN = "http://testserver"


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


def _login_admin(client: TestClient) -> None:
    resp = client.post(
        "/api/auth/login",
        json={"correo": "admin@teiba.local", "contrasena": "admin12345678"},
        headers={"Origin": ORIGIN},
    )
    assert resp.status_code == 200, resp.text


def test_rate_limit_login_429(client, _auth_env, monkeypatch):
    # Con AUTH_LOGIN_MAX_FAILURES=2, el 3er intento (incluso con credencial
    # correcta) debe devolver 429.
    monkeypatch.setenv("AUTH_LOGIN_MAX_FAILURES", "2")
    from app.config import get_settings
    get_settings.cache_clear()

    assert client.post(
        "/api/auth/login",
        json={"correo": "admin@teiba.local", "contrasena": "mala-1"},
        headers={"Origin": ORIGIN},
    ).status_code == 401
    assert client.post(
        "/api/auth/login",
        json={"correo": "admin@teiba.local", "contrasena": "mala-2"},
        headers={"Origin": ORIGIN},
    ).status_code == 401
    resp = client.post(
        "/api/auth/login",
        json={"correo": "admin@teiba.local", "contrasena": "admin12345678"},
        headers={"Origin": ORIGIN},
    )
    assert resp.status_code == 429
    assert resp.json()["code"] == "rate_limited"
    assert resp.headers["Retry-After"]


def test_rate_limit_por_minute(monkeypatch, tmp_path):
    # Test aislado creando la app ya con el limite bajo, igual que el original.
    monkeypatch.setenv("RATE_LIMIT_PER_MINUTE", "2")
    monkeypatch.setenv("RATE_LIMIT_CONCURRENT", "1")
    import os
    from app.config import get_settings
    get_settings.cache_clear()
    from app import db as db_module
    monkeypatch.setattr(db_module, "ping", lambda: True)
    from app.main import create_app
    app = create_app()
    app.dependency_overrides[get_agent_runner] = lambda: FakeRunner()

    # Sembrar usuarios directamente en la BD temporal de la app.
    from pathlib import Path
    db_path = Path(get_settings().auth_db_path)
    from app.infrastructure.sqlite_auth import BaseAuth
    from datetime import UTC, datetime
    from app.infrastructure.passwords import BcryptPasswordHasher
    base = BaseAuth(str(db_path))
    base.asegurar_esquema()
    hasher = BcryptPasswordHasher(4)
    with base._conectar() as conn:
        conn.execute(
            "INSERT INTO users (email, password_hash, role, is_active, created_at, updated_at) "
            "VALUES (?, ?, ?, 1, strftime('%s','now'), strftime('%s','now'))",
            ("admin@teiba.local", hasher.hash("admin12345678"), "admin"),
        )

    try:
        with TestClient(app) as client:
            _login_admin(client)
            body = {"pregunta": "¿Cómo está el suelo?"}
            assert client.post("/api/agente/consulta", json=body, headers={"Origin": ORIGIN}).status_code == 200
            assert client.post("/api/agente/consulta", json=body, headers={"Origin": ORIGIN}).status_code == 200
            response = client.post("/api/agente/consulta", json=body, headers={"Origin": ORIGIN})
    finally:
        get_settings.cache_clear()

    assert response.status_code == 429
    body_resp = response.json()
    assert body_resp["code"] == "rate_limited"
    assert body_resp["traceId"]
    assert response.headers["Retry-After"]
