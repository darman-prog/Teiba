"""Fixtures de integración: `teiba_test` para repositorios y `teiba_db` para el contrato."""
import pytest
from pymongo import MongoClient

from app.config import get_settings
from tests.integration.fixtures import seed_test_db


@pytest.fixture()
def mongo_db():
    settings = get_settings()
    client = MongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=2000, tz_aware=True)
    try:
        client.admin.command("ping")
    except Exception:
        pytest.skip("MongoDB no disponible")
    db = client["teiba_test"]
    client.drop_database("teiba_test")
    seed_test_db(db)
    yield db
    client.drop_database("teiba_test")
    client.close()


@pytest.fixture(scope="session")
def mongo_real():
    """Conexión de solo lectura a la base real de la entrega."""
    settings = get_settings()
    client = MongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=2000, tz_aware=True)
    try:
        client.admin.command("ping")
    except Exception:
        pytest.skip("MongoDB no disponible")
    db = client[settings.mongodb_db]
    if db.parques.count_documents({}) == 0:
        pytest.skip("La base real está vacía; ejecuta 01_crear_objetos.js y 02_cargar_datos.js")
    yield db
    client.close()
