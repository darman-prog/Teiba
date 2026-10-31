"""Modelos puros de la identidad de acceso.

El dominio no sabe de HTTP, cookies ni SQLite: solo define las invariantes
(rol válido, sesión expirada) y las firmas que infraestructura implementa.

MongoDB `usuarios` guarda perfiles de dominio (administrador, operador, ciudadano)
y no tiene contraseñas. Aquí `users` es solo la identidad de login: el rol de
acceso (`admin`/`user`) vive en SQLite y es la unica fuente para autorizar.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class Rol(StrEnum):
    """Rol de acceso. Refleja la matriz de permisos, no los roles de dominio."""

    ADMIN = "admin"
    USER = "user"


@dataclass(frozen=True)
class Usuario:
    """Identidad de acceso resuelta desde SQLite."""

    id: int
    correo: str
    rol: Rol
    activo: bool = True


@dataclass(frozen=True)
class Credenciales:
    """Credenciales de un usuario, tal como persiste SQLite."""

    usuario: Usuario
    password_hash: str


@dataclass(frozen=True)
class Sesion:
    """Sesión de acceso activa."""

    token_hash: str
    user_id: int
    creada_en: datetime
    expira_en: datetime



