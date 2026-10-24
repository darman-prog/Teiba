"""Cliente MongoDB compartido por la API.

La conexión es perezosa: si Mongo está caído, la API arranca igual y el
health reporta el fallo en lugar de tumbar el proceso.
"""
from pymongo import MongoClient
from pymongo.database import Database

from app.config import get_settings

_client: MongoClient | None = None


def get_client() -> MongoClient:
    """Crea el cliente una sola vez y lo reutiliza."""
    global _client
    if _client is None:
        settings = get_settings()
        _client = MongoClient(
            settings.mongodb_uri,
            serverSelectionTimeoutMS=2000,
            connectTimeoutMS=2000,
            tz_aware=True,
        )
    return _client


def get_db() -> Database:
    """Devuelve la base de datos configurada (`teiba_db` por defecto)."""
    return get_client()[get_settings().mongodb_db]


def ping() -> bool:
    """Comprueba la conexión sin lanzar excepción hacia el endpoint."""
    try:
        get_client().admin.command("ping")
        return True
    except Exception:
        return False


def close_client() -> None:
    """Cierra el cliente al apagar la aplicación."""
    global _client
    if _client is not None:
        _client.close()
        _client = None
