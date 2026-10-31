"""PasswordHasher respaldado con bcrypt.

bcrypt trunca a 72 bytes: la capa de validación (LoginRequest) y el seed aseguran
que la contraseña no pase de ahí en UTF-8. Para correos inexistentes se verifica
contra un hash fijo (dummy) y así no se revela si el correo existe por timing.
"""

import bcrypt

# Hash fijo de una cadena aleatoria; solo se usa para igualar tiempos en login
# cuando el correo no existe. Nunca coincide con una contraseña real.
_HASH_DUMMY = bcrypt.hashpw(b"teiba-auth-dummy-password-2026", bcrypt.gensalt(4))


class BcryptPasswordHasher:
    """Implementa PasswordHasher con un coste configurable (tests usan 4)."""

    def __init__(self, rounds: int = 12) -> None:
        self._rounds = rounds

    def hash(self, contrasena: str) -> str:
        sal = bcrypt.gensalt(self._rounds)
        return bcrypt.hashpw(contrasena.encode("utf-8"), sal).decode("ascii")

    def verify(self, contrasena: str, almacenado: str) -> bool:
        try:
            return bcrypt.checkpw(contrasena.encode("utf-8"), almacenado.encode("ascii"))
        except (ValueError, TypeError):
            # Hash mal formado o corrupto: trátalo como coincidencia fallida.
            return False

    def verify_dummy(self, contrasena: str) -> None:
        """Consume tiempo similar a una verdadera sin revelar existencia."""
        bcrypt.checkpw(contrasena.encode("utf-8"), _HASH_DUMMY)
