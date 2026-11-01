"""Conexión y esquema de la base de identidad SQLite.

Cada operación abre una conexión corta (threadpool de FastAPI = hilos, no async).
"""

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from app.domain.auth.errors import AlmacenAuthNoDisponible


def _epoch(dt: datetime) -> int:
    return int(dt.timestamp())


def _from_epoch(val: int) -> datetime:
    return datetime.fromtimestamp(val)


class BaseAuth:
    """Envuelve la creación de conexiones y la migración idempotente."""

    def __init__(self, db_path: str) -> None:
        self._path = Path(db_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def _conectar(self) -> Iterator[sqlite3.Connection]:
        try:
            conn = sqlite3.connect(
                self._path,
                timeout=5.0,
                isolation_level=None,
            )
        except sqlite3.Error as exc:
            raise AlmacenAuthNoDisponible() from exc
        try:
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("PRAGMA journal_mode = WAL")
            conn.execute("PRAGMA busy_timeout = 5000")
            yield conn
        finally:
            conn.close()

    def asegurar_esquema(self) -> None:
        """Crea el esquema v2 o migra desde v1; idempotente por user_version."""
        with self._conectar() as conn:
            version = conn.execute("PRAGMA user_version").fetchone()[0]
            if version >= 2:
                return
            if version == 0:
                self._crear_esquema_v2(conn)
                return
            if version == 1:
                self._migrar_v1_a_v2(conn)
                return
            # Una versión futura no se toca: mejor fallar que corromper datos.
            raise RuntimeError(f"Versión de esquema SQLite no soportada: {version}")

    def _crear_esquema_v2(self, conn: sqlite3.Connection) -> None:
        """Crea users/sessions en v2 para una base nueva."""
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY,
                email         TEXT    NOT NULL COLLATE NOCASE,
                password_hash TEXT    NOT NULL,
                role          TEXT    NOT NULL CHECK (role IN ('admin', 'operator', 'user')),
                is_active     INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
                created_at    INTEGER NOT NULL,
                updated_at    INTEGER NOT NULL
            );
            CREATE UNIQUE INDEX IF NOT EXISTS ux_users_email ON users (email);

            CREATE TABLE IF NOT EXISTS sessions (
                token_hash TEXT    PRIMARY KEY,
                user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                created_at INTEGER NOT NULL,
                expires_at INTEGER NOT NULL
            );
            CREATE INDEX IF NOT EXISTS ix_sessions_user_id    ON sessions (user_id);
            CREATE INDEX IF NOT EXISTS ix_sessions_expires_at ON sessions (expires_at);
            """
        )
        conn.execute("PRAGMA user_version = 2")

    def _migrar_v1_a_v2(self, conn: sqlite3.Connection) -> None:
        """Reconstruye users para admitir operator sin perder ids ni sesiones."""
        # Foreign keys debe apagarse fuera de la transacción; dentro no tiene efecto.
        conn.execute("PRAGMA foreign_keys = OFF")
        try:
            conn.execute("BEGIN IMMEDIATE")
            conn.execute(
                """
                CREATE TABLE users_v2 (
                    id            INTEGER PRIMARY KEY,
                    email         TEXT    NOT NULL COLLATE NOCASE,
                    password_hash TEXT    NOT NULL,
                    role          TEXT    NOT NULL CHECK (role IN ('admin', 'operator', 'user')),
                    is_active     INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
                    created_at    INTEGER NOT NULL,
                    updated_at    INTEGER NOT NULL
                )
                """
            )
            conn.execute(
                """
                INSERT INTO users_v2 (
                    id, email, password_hash, role, is_active, created_at, updated_at
                )
                SELECT id, email, password_hash, role, is_active, created_at, updated_at
                FROM users
                """
            )
            conn.execute("DROP TABLE users")
            conn.execute("ALTER TABLE users_v2 RENAME TO users")
            conn.execute("CREATE UNIQUE INDEX ux_users_email ON users(email)")

            # Se valida antes del COMMIT: con huérfanos se revierte la transacción.
            problemas = conn.execute("PRAGMA foreign_key_check").fetchall()
            if problemas:
                conn.execute("ROLLBACK")
                raise RuntimeError(
                    "La migración SQLite v2 dejó referencias huérfanas; se revirtió."
                )

            conn.execute("PRAGMA user_version = 2")
            conn.execute("COMMIT")
        except Exception:
            # Si el fallo ocurrió antes del COMMIT, se revierte lo que esté abierto.
            try:
                conn.execute("ROLLBACK")
            except sqlite3.Error:
                pass
            raise
        finally:
            conn.execute("PRAGMA foreign_keys = ON")

    def limpiar_expiradas(self, ahora: datetime) -> int:
        with self._conectar() as conn:
            cur = conn.execute("DELETE FROM sessions WHERE expires_at <= ?", (_epoch(ahora),))
            return cur.rowcount

    def esta_disponible(self) -> bool:
        """Para el endpoint de salud: no revela la ruta ni el driver."""
        try:
            with self._conectar() as conn:
                conn.execute("SELECT 1")
            return True
        except AlmacenAuthNoDisponible:
            return False
