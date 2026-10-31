"""Casos de uso de acceso: login, logout y resolución de sesión.

Nunca toca HTTP ni cookies: devuelve el token en claro solo a la capa API,
que es la única que puede leer/escribir la cookie.
"""

import hashlib
import secrets
from datetime import datetime, timedelta

from app.application.auth.errors import AuthError, AuthStorageError
from app.application.ports import (
    Clock,
    PasswordHasher,
    SessionRepository,
    UserRepository,
)
from app.domain.auth.errors import AlmacenAuthNoDisponible
from app.domain.auth.models import Sesion, Usuario


def _hash_token(token: str) -> str:
    """Token opaco -> huella almacenada. El token en claro nunca se persiste."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class SesionActual:
    """Sesión resuelta que devuelve `me` (incluye expiración para el cliente)."""

    def __init__(self, usuario: Usuario, expira_en: datetime) -> None:
        self.usuario = usuario
        self.expira_en = expira_en


class SesionIniciada:
    """Resultado del login: token en claro + metadatos para la cookie."""

    def __init__(self, token: str, usuario: Usuario, expira_en: datetime) -> None:
        self.token = token
        self.usuario = usuario
        self.expira_en = expira_en


class AuthService:
    """Orquesta login/logout/me contra los puertos de identidad."""

    def __init__(
        self,
        users: UserRepository,
        sessions: SessionRepository,
        hasher: PasswordHasher,
        clock: Clock,
        ttl: timedelta,
    ) -> None:
        self._users = users
        self._sessions = sessions
        self._hasher = hasher
        self._clock = clock
        self._ttl = ttl

    def login(self, correo: str, contrasena: str, token_previo: str | None) -> SesionIniciada:
        ahora = self._clock.now()
        correo_norm = self._normalizar_correo(correo)

        try:
            cred = self._users.get_credentials(correo_norm)
        except AlmacenAuthNoDisponible as exc:
            raise AuthStorageError() from exc

        if cred is None:
            # No revelamos si el correo existe: verificamos contra un hash fijo.
            self._hasher.verify_dummy(contrasena)
            raise AuthError(401, "invalid_credentials", "Correo o contraseña incorrectos.")

        if not cred.usuario.activo or not self._hasher.verify(contrasena, cred.password_hash):
            raise AuthError(401, "invalid_credentials", "Correo o contraseña incorrectos.")

        # Anti-fixation: si venía una cookie válida, la revocamos antes de crear una nueva.
        if token_previo:
            self._sessions.delete(_hash_token(token_previo))

        token = secrets.token_urlsafe(32)
        sesion = Sesion(
            token_hash=_hash_token(token),
            user_id=cred.usuario.id,
            creada_en=ahora,
            expira_en=ahora + self._ttl,
        )
        try:
            self._sessions.create(sesion)
            self._sessions.delete_expired(ahora)
        except AlmacenAuthNoDisponible as exc:
            raise AuthStorageError() from exc

        return SesionIniciada(token=token, usuario=cred.usuario, expira_en=sesion.expira_en)

    def logout(self, token: str | None) -> None:
        if not token:
            return
        try:
            self._sessions.delete(_hash_token(token))
        except AlmacenAuthNoDisponible:
            # Logout best-effort: la expiración absoluta la caduca igual.
            return

    def usuario_actual(self, token: str | None) -> SesionActual:
        if not token:
            raise AuthError(401, "not_authenticated", "No hay una sesión activa.")
        token_hash = _hash_token(token)

        try:
            sesion = self._sessions.get(token_hash)
        except AlmacenAuthNoDisponible as exc:
            raise AuthStorageError() from exc

        if sesion is None:
            raise AuthError(401, "not_authenticated", "No hay una sesión activa.")

        try:
            usuario = self._users.get_by_id(sesion.user_id)
        except AlmacenAuthNoDisponible as exc:
            raise AuthStorageError() from exc

        if usuario is None or not usuario.activo:
            self._sessions.delete(token_hash)
            raise AuthError(401, "not_authenticated", "No hay una sesión activa.")

        ahora_ts = self._clock.now().timestamp()
        if ahora_ts >= sesion.expira_en.timestamp():
            self._sessions.delete(token_hash)
            raise AuthError(401, "not_authenticated", "La sesión expiró.")

        return SesionActual(usuario=usuario, expira_en=sesion.expira_en)

    @staticmethod
    def _normalizar_correo(correo: str) -> str:
        return correo.strip().lower()
