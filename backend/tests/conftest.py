"""Fixtures compartidas de la suite."""
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Anade el backend al path para `python -m pytest` y para imports de scripts.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app import db as db_module
from app.config import get_settings
from app.infrastructure.passwords import BcryptPasswordHasher
from app.infrastructure.sqlite_auth import BaseAuth
from app.infrastructure.sqlite_auth_repositories import SqliteUserRepository


@pytest.fixture(autouse=True)
def _auth_env(tmp_path, monkeypatch):
    """DB SQLite temporal + credenciales demo para todas las pruebas."""
    db_path = tmp_path / "auth.db"
    monkeypatch.setenv("AUTH_DB_PATH", str(db_path))
    monkeypatch.setenv("AUTH_COOKIE_SECURE", "false")
    monkeypatch.setenv("AUTH_BCRYPT_ROUNDS", "4")
    # Limite bajo para que los tests de rate limit de login fallen rapido.
    monkeypatch.setenv("AUTH_LOGIN_MAX_FAILURES", "2")
    monkeypatch.setenv("AUTH_LOGIN_WINDOW_SECONDS", "60")
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://testserver")
    # invalidar la cache de settings para que relea el entorno
    get_settings.cache_clear()
    yield db_path
    get_settings.cache_clear()


def _sembrar_usuarios(db_path: Path) -> None:
    base = BaseAuth(str(db_path))
    base.asegurar_esquema()
    hasher = BcryptPasswordHasher(4)
    repo = SqliteUserRepository(base)
    for correo, rol, pwd in [
        ("admin@teiba.local", "admin", "admin12345678"),
        ("user@teiba.local", "user", "user12345678"),
    ]:
        hashh = hasher.hash(pwd)
        with base._conectar() as conn:
            existente = conn.execute("SELECT id FROM users WHERE email = ?", (correo,)).fetchone()
            if existente is None:
                conn.execute(
                    "INSERT INTO users (email, password_hash, role, is_active, created_at, updated_at) "
                    "VALUES (?, ?, ?, 1, strftime('%s','now'), strftime('%s','now'))",
                    (correo, hashh, rol),
                )


@pytest.fixture()
def app(monkeypatch, _auth_env):
    """App de prueba sin Mongo real y con SQLite auth temporal."""
    monkeypatch.setattr(db_module, "ping", lambda: True)
    from app.main import create_app
    return create_app()


@pytest.fixture()
def client(app, _auth_env):
    _sembrar_usuarios(_auth_env)
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def authed_admin(client, _auth_env):
    """Cliente con sesión de admin; fallback a DB si el login HTTP falla (tests de unidad)."""
    _sembrar_usuarios(_auth_env)
    resp = client.post(
        "/api/auth/login",
        json={"correo": "admin@teiba.local", "contrasena": "admin12345678"},
        headers={"Origin": "http://testserver"},
    )
    if resp.status_code != 200:
        pytest.fail(f"login admin de test fallo: {resp.status_code} {resp.text}")
    return client


@pytest.fixture()
def authed_user(client, _auth_env):
    _sembrar_usuarios(_auth_env)
    resp = client.post(
        "/api/auth/login",
        json={"correo": "user@teiba.local", "contrasena": "user12345678"},
        headers={"Origin": "http://testserver"},
    )
    if resp.status_code != 200:
        pytest.fail(f"login user de test fallo: {resp.status_code} {resp.text}")
    return client
