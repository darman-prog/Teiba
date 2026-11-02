"""Políticas de autorización del dominio de acceso."""

from .models import Rol, Usuario


def puede_administrar(usuario: Usuario) -> bool:
    """Solo el rol admin accede a recursos operativos (Sage, sensores)."""
    return usuario.rol == Rol.ADMIN
