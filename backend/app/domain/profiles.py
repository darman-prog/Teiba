"""Roles de dominio y actor autenticado.

El rol de acceso (`admin`/`user`) vive en auth; estos roles describen el perfil
de negocio en Mongo y deciden qué superficies puede usar cada persona.
"""
from dataclasses import dataclass
from enum import StrEnum


class RolDominio(StrEnum):
    """Rol del perfil de negocio, no el rol de acceso."""

    ADMINISTRADOR = "administrador"
    OPERADOR_MANTENIMIENTO = "operador_mantenimiento"
    CIUDADANO = "ciudadano"


@dataclass(frozen=True)
class Actor:
    """Identidad de negocio resuelta desde la sesión y el perfil Mongo."""

    perfil_id: str
    correo: str
    rol: RolDominio
