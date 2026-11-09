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
    ProfileRepository,
    SessionRepository,
    UserRepository,
)
from app.domain.auth.errors import (
    AlmacenAuthNoDisponible,
    AlmacenPerfilNoDisponible,
    CorreoYaRegistrado,
)
from app.domain.auth.models import Rol, Sesion, Usuario

PASSWORD_MIN_CHARS = 12


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
        profiles: ProfileRepository,
    ) -> None:
        self._users = users
        self._sessions = sessions
        self._hasher = hasher
        self._clock = clock
        self._ttl = ttl
        self._profiles = profiles

    def login(self, correo: str, contrasena: str, token_previo: str | None) -> SesionIniciada:
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

        return self._iniciar_sesion(cred.usuario, token_previo)

    def register(
        self,
        correo: str,
        contrasena: str,
        nombre: str | None,
        token_previo: str | None = None,
    ) -> SesionIniciada:
        """Alta pública: rol de acceso `user` y perfil `ciudadano` fijados aquí."""
        correo_norm = self._normalizar_correo(correo)
        self._validar_contrasena(contrasena)
        nombre_norm = (nombre or "").strip() or correo_norm.split("@")[0]
        if len(nombre_norm) > 80:
            raise AuthError(
                422, "invalid_request", "El nombre no puede superar 80 caracteres."
            )

        password_hash = self._hasher.hash(contrasena)
        try:
            usuario = self._users.create_usuario(correo_norm, password_hash, Rol.USER)
        except CorreoYaRegistrado as exc:
            raise AuthError(
                409, "email_taken", "Ya existe una cuenta con ese correo."
            ) from exc
        except AlmacenAuthNoDisponible as exc:
            raise AuthStorageError() from exc

        try:
            perfil = self._profiles.create_perfil(correo_norm, nombre_norm, "ciudadano")
        except AlmacenPerfilNoDisponible as exc:
            # Sin transacción distribuida: se deshace la identidad SQLite.
            self._users.delete_usuario(usuario.id)
            raise AuthError(
                503, "db_unavailable", "La base de datos no está disponible."
            ) from exc

        if perfil is None:
            # Un perfil previo en Mongo es intocable: no se hereda la identidad.
            self._users.delete_usuario(usuario.id)
            raise AuthError(409, "email_taken", "Ya existe una cuenta con ese correo.")

        return self._iniciar_sesion(usuario, token_previo)

    def _iniciar_sesion(self, usuario: Usuario, token_previo: str | None) -> SesionIniciada:
        ahora = self._clock.now()
        # Anti-fixation: si venía una cookie válida, la revocamos antes de crear una nueva.
        if token_previo:
            self._sessions.delete(_hash_token(token_previo))

        token = secrets.token_urlsafe(32)
        sesion = Sesion(
            token_hash=_hash_token(token),
            user_id=usuario.id,
            creada_en=ahora,
            expira_en=ahora + self._ttl,
        )
        try:
            self._sessions.create(sesion)
            self._sessions.delete_expired(ahora)
        except AlmacenAuthNoDisponible as exc:
            raise AuthStorageError() from exc

        return SesionIniciada(token=token, usuario=usuario, expira_en=sesion.expira_en)

    @staticmethod
    def _validar_contrasena(contrasena: str) -> None:
        if len(contrasena) < PASSWORD_MIN_CHARS:
            raise AuthError(
                422,
                "invalid_request",
                f"La contraseña debe tener al menos {PASSWORD_MIN_CHARS} caracteres.",
            )
        if len(contrasena.encode("utf-8")) > 72:
            raise AuthError(
                422,
                "invalid_request",
                "La contraseña no puede superar 72 bytes en UTF-8.",
            )

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
