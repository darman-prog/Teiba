"""Siembra las cuentas demo de acceso en SQLite.

Lee las credenciales de backend/.env y las inserta/actualiza de forma idempotente.
Si falta alguna variable o la contraseña es corta, aborta sin tocar la BD.

Ejemplo:
    AUTH_ADMIN_EMAIL=admin@teiba.local AUTH_ADMIN_PASSWORD=admin123456 \\
    AUTH_USER_EMAIL=user@teiba.local AUTH_USER_PASSWORD=user123456 \\
    python -m app.scripts.seed_auth
"""

import os
import sys
from datetime import UTC, datetime

from app.config import get_settings
from app.infrastructure.passwords import BcryptPasswordHasher
from app.infrastructure.sqlite_auth import BaseAuth


def main() -> int:
    settings = get_settings()

    cuentas = [
        (
            os.getenv("AUTH_ADMIN_EMAIL", "admin@teiba.local"),
            "AUTH_ADMIN_PASSWORD",
            "admin",
        ),
        (
            os.getenv("AUTH_OPERATOR_EMAIL", "operador@teiba.local"),
            "AUTH_OPERATOR_PASSWORD",
            "operator",
        ),
        (
            os.getenv("AUTH_USER_EMAIL", "user@teiba.local"),
            "AUTH_USER_PASSWORD",
            "user",
        ),
    ]

    ahora = datetime.now(UTC)
    hasher = BcryptPasswordHasher(settings.auth_bcrypt_rounds)
    base = BaseAuth(settings.auth_db_path)
    base.asegurar_esquema()

    for correo, var_pass, rol in cuentas:
        correo_norm = (correo or "").strip().lower()
        contrasena = os.getenv(var_pass, "")

        if not correo_norm or "@" not in correo_norm:
            print(f"ERROR: correo invalido para rol '{rol}': {correo!r}")
            return 1
        if not contrasena or len(contrasena) < 12:
            print(
                f"ERROR: contraseña para '{correo_norm}' ausente o menor a "
                f"12 caracteres (define {var_pass})."
            )
            return 1

        with base._conectar() as conn:
            existente = conn.execute(
                "SELECT id FROM users WHERE email = ?", (correo_norm,)
            ).fetchone()
            hash_nuevo = hasher.hash(contrasena)
            if existente is None:
                cols = "email, password_hash, role, is_active, created_at, updated_at"
                conn.execute(
                    f"INSERT INTO users ({cols}) VALUES (?, ?, ?, 1, ?, ?)",
                    (correo_norm, hash_nuevo, rol, int(ahora.timestamp()), int(ahora.timestamp())),
                )
            else:
                conn.execute(
                    "UPDATE users SET password_hash=?, role=?, is_active=1, "
                    "updated_at=? WHERE id=?",
                    (hash_nuevo, rol, int(ahora.timestamp()), existente["id"]),
                )
            # Rotar contraseña revoca todas las sesiones del usuario.
            conn.execute(
                "DELETE FROM sessions WHERE user_id = ?",
                (existente["id"],)
                if existente
                else (
                    conn.execute("SELECT id FROM users WHERE email = ?", (correo_norm,)).fetchone()[
                        "id"
                    ],
                ),
            )

    print(f"Cuentas de acceso sembradas/actualizadas en {base._path}:")
    for correo, _, rol in cuentas:
        print(f"  - {correo.strip().lower()} ({rol})")
    print("Nota: las contraseñas se leen de las variables de entorno; no se imprimen.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
