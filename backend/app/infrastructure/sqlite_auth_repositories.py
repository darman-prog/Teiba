"""Implementaciones SQLite de los puertos de identidad."""

from datetime import datetime
from sqlite3 import Row

from app.domain.auth.errors import AlmacenAuthNoDisponible
from app.domain.auth.models import Credenciales, Rol, Sesion, Usuario

from .sqlite_auth import BaseAuth, _epoch, _from_epoch


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
