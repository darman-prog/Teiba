"""Fixtures compartidas de la suite."""
import pytest
from fastapi.testclient import TestClient

from app import db as db_module
from app.main import create_app


@pytest.fixture()
def app(monkeypatch):
    """App de prueba sin depender de un Mongo real para el health."""
    monkeypatch.setattr(db_module, "ping", lambda: True)
    return create_app()


@pytest.fixture()
def client(app):
    with TestClient(app) as test_client:
        yield test_client
