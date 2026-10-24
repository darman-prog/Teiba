"""Controles de seguridad visibles en el contrato HTTP y en las tools."""
import pytest
from fastapi.testclient import TestClient

from app.agent.validation import ToolValidationError, parse_tool_args


def test_health_no_expone_uri_ni_key(client):
    response = client.get("/api/health")
    texto = response.text.lower()

    assert response.status_code == 200
    assert "mongodb://" not in texto
    assert "opencode_api_key" not in texto
    assert "sk-" not in texto
    assert response.json()["mongo"]["db"] == "teiba_db"


def test_error_no_filtra_stack(app):
    @app.get("/crash-seguridad")
    def crash():
        raise RuntimeError("secreto-interno")

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/crash-seguridad")

    assert response.status_code == 500
    assert "secreto-interno" not in response.text
    assert "Traceback" not in response.text
    assert response.json()["traceId"]


def test_tool_rechaza_operador_nosql():
    with pytest.raises(ToolValidationError) as exc:
        parse_tool_args("get_sensor_history", '{"sensor_id":{"$ne":null}}')

    assert exc.value.code == "invalid_args"


def test_cors_rechaza_origen_externo(client):
    response = client.get(
        "/api/health",
        headers={"Origin": "http://evil.test"},
    )

    assert "access-control-allow-origin" not in response.headers
