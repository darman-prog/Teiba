"""Implementaciones SQLite de los puertos de identidad."""

import logging
import sqlite3
from datetime import UTC, datetime
from sqlite3 import Row

from app.domain.auth.errors import AlmacenAuthNoDisponible, CorreoYaRegistrado
from app.domain.auth.models import Credenciales, Rol, Sesion, Usuario

from .sqlite_auth import BaseAuth, _epoch, _from_epoch

logger = logging.getLogger("teiba.auth")


def _row_a_usuario(row: Row) -> Usuario:
    return Usuario(
        id=row["id"],
        correo=row["email"],
        rol=Rol(row["role"]),
        activo=bool(row["is_active"]),
    )


class SqliteUserRepository:
    """UserRepository respaldado por SQLite."""

    def __init__(self, base: BaseAuth) -> None:
        self._base = base

    def get_credentials(self, correo: str) -> Credenciales | None:
        try:
            with self._base._conectar() as conn:
                row = conn.execute(
                    "SELECT id, email, password_hash, role, is_active FROM users WHERE email = ?",
                    (correo,),
                ).fetchone()
        except AlmacenAuthNoDisponible:
            raise
        if row is None:
            return None
        return Credenciales(usuario=_row_a_usuario(row), password_hash=row["password_hash"])

    def get_by_id(self, user_id: int) -> Usuario | None:
        try:
            with self._base._conectar() as conn:
                row = conn.execute(
                    "SELECT id, email, password_hash, role, is_active FROM users WHERE id = ?",
                    (user_id,),
                ).fetchone()
        except AlmacenAuthNoDisponible:
            raise
        if row is None:
            return None
        return _row_a_usuario(row)

    def create_usuario(self, correo: str, password_hash: str, rol: Rol) -> Usuario:
        ahora = int(datetime.now(UTC).timestamp())
        try:
            with self._base._conectar() as conn:
                cur = conn.execute(
                    "INSERT INTO users "
                    "(email, password_hash, role, is_active, created_at, updated_at) "
                    "VALUES (?, ?, ?, 1, ?, ?)",
                    (correo, password_hash, rol.value, ahora, ahora),
                )
                user_id = int(cur.lastrowid or 0)
        except sqlite3.IntegrityError as exc:
            # El índice único ux_users_email es la fuente de verdad del duplicado.
            raise CorreoYaRegistrado() from exc
        except sqlite3.Error as exc:
            raise AlmacenAuthNoDisponible() from exc
        return Usuario(id=user_id, correo=correo, rol=rol, activo=True)

    def delete_usuario(self, user_id: int) -> None:
        try:
            with self._base._conectar() as conn:
                cur = conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
                if cur.rowcount != 1:
                    # La compensación no encontró la fila: se deja rastro sin PII.
                    logger.warning("Compensacion de registro sin filas user_id=%s", user_id)
        except (AlmacenAuthNoDisponible, sqlite3.Error):
            # Mejor esfuerzo: si la compensación falla, no se enmascara el 503.
            logger.warning("No se pudo compensar el registro user_id=%s", user_id)


class SqliteSessionRepository:
    """SessionRepository respaldado por SQLite."""

    def __init__(self, base: BaseAuth) -> None:
        self._base = base

    def create(self, sesion: Sesion) -> None:
        try:
            with self._base._conectar() as conn:
                conn.execute(
                    "INSERT INTO sessions "
                    "(token_hash, user_id, created_at, expires_at) VALUES (?, ?, ?, ?)",
                    (
                        sesion.token_hash,
                        sesion.user_id,
                        _epoch(sesion.creada_en),
                        _epoch(sesion.expira_en),
                    ),
                )
        except AlmacenAuthNoDisponible:
            raise

    def get(self, token_hash: str) -> Sesion | None:
        try:
            with self._base._conectar() as conn:
                row = conn.execute(
                    "SELECT token_hash, user_id, created_at, expires_at "
                    "FROM sessions WHERE token_hash = ?",
                    (token_hash,),
                ).fetchone()
        except AlmacenAuthNoDisponible:
            raise
        if row is None:
            return None
        return Sesion(
            token_hash=row["token_hash"],
            user_id=row["user_id"],
            creada_en=_from_epoch(row["created_at"]),
            expira_en=_from_epoch(row["expires_at"]),
        )

    def delete(self, token_hash: str) -> None:
        try:
            with self._base._conectar() as conn:
                conn.execute("DELETE FROM sessions WHERE token_hash = ?", (token_hash,))
        except AlmacenAuthNoDisponible:
            raise

    def delete_for_user(self, user_id: int) -> None:
        try:
            with self._base._conectar() as conn:
                conn.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
        except AlmacenAuthNoDisponible:
            raise

    def delete_expired(self, ahora: datetime) -> int:
        return self._base.limpiar_expiradas(ahora)
