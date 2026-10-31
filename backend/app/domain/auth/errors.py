"""Errores de dominio de acceso, traducidos al contrato HTTP por la capa API."""


class CredencialesInvalidas(Exception):
    """Correo inexistente, contraseña mala o cuenta inactiva."""


class NoAutenticado(Exception):
    """No hay sesión válida (cookie ausente, expirada o revocada)."""


class SesionExpirada(Exception):
    """La sesión llegó a su tiempo máximo absoluto."""


class RecursoProhibido(Exception):
    """El usuario está autenticado pero no tiene el rol requerido."""


class AlmacenAuthNoDisponible(Exception):
    """SQLite caído o inaccesible: se traduce a 503 auth_unavailable."""
