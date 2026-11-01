"""Migración SQLite v1 -> v2 y creación del esquema v2 en base nueva."""
import sqlite3

from app.infrastructure.sqlite_auth import BaseAuth

V1_SCHEMA = """
CREATE TABLE users (
    id            INTEGER PRIMARY KEY,
    email         TEXT    NOT NULL COLLATE NOCASE,
    password_hash TEXT    NOT NULL,
    role          TEXT    NOT NULL CHECK (role IN ('admin', 'user')),
    is_active     INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    created_at    INTEGER NOT NULL,
    updated_at    INTEGER NOT NULL
);
CREATE UNIQUE INDEX ux_users_email ON users (email);
CREATE TABLE sessions (
    token_hash TEXT    PRIMARY KEY,
    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at INTEGER NOT NULL,
    expires_at INTEGER NOT NULL
);
CREATE INDEX ix_sessions_user_id    ON sessions (user_id);
CREATE INDEX ix_sessions_expires_at ON sessions (expires_at);
"""


def _crear_v1(path) -> None:
    conn = sqlite3.connect(str(path))
    conn.isolation_level = None
    conn.executescript(V1_SCHEMA)
    conn.execute(
        "INSERT INTO users (id, email, password_hash, role, is_active, created_at, updated_at) "
        "VALUES (1, 'admin@teiba.local', 'hash', 'admin', 1, 1, 1)"
    )
    conn.execute(
        "INSERT INTO sessions (token_hash, user_id, created_at, expires_at) "
        "VALUES ('token-v1', 1, 1, 9999999999)"
    )
    conn.execute("PRAGMA user_version = 1")
    conn.close()


def _version(path) -> int:
    conn = sqlite3.connect(str(path))
    try:
        return conn.execute("PRAGMA user_version").fetchone()[0]
    finally:
        conn.close()


def test_base_nueva_crea_v2_y_admite_operator(tmp_path):
    path = tmp_path / "auth.db"
    base = BaseAuth(str(path))
    base.asegurar_esquema()

    assert _version(path) == 2
    with base._conectar() as conn:
        conn.execute(
            "INSERT INTO users (email, password_hash, role, is_active, created_at, updated_at) "
            "VALUES ('operador@teiba.local', 'hash', 'operator', 1, 1, 1)"
        )
        assert conn.execute("SELECT role FROM users").fetchone()[0] == "operator"


def test_migracion_v1_a_v2_preserva_usuarios_y_sesiones(tmp_path):
    path = tmp_path / "auth.db"
    _crear_v1(path)
    assert _version(path) == 1

    base = BaseAuth(str(path))
    base.asegurar_esquema()

    assert _version(path) == 2
    with base._conectar() as conn:
        usuario = conn.execute("SELECT id, email, role FROM users").fetchone()
        assert (usuario["id"], usuario["email"], usuario["role"]) == (
            1,
            "admin@teiba.local",
            "admin",
        )
        assert conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0] == 1
        assert conn.execute("PRAGMA foreign_key_check").fetchall() == []

        conn.execute(
            "INSERT INTO users (email, password_hash, role, is_active, created_at, updated_at) "
            "VALUES ('operador@teiba.local', 'hash', 'operator', 1, 1, 1)"
        )


def test_migracion_es_idempotente(tmp_path):
    path = tmp_path / "auth.db"
    _crear_v1(path)
    base = BaseAuth(str(path))

    base.asegurar_esquema()
    base.asegurar_esquema()

    assert _version(path) == 2
    with base._conectar() as conn:
        assert conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0] == 1
