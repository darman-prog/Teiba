"""Formato único de errores: code, message, details y traceId."""
from fastapi.testclient import TestClient

from app.api.errors import ApiError


def test_api_error_shape(app):
    @app.get("/boom")
    def boom():
        raise ApiError(400, "invalid_request", "boom", {"campo": "x"})

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/boom")

    assert response.status_code == 400
    body = response.json()
    assert set(body) == {"code", "message", "details", "traceId"}
    assert body["code"] == "invalid_request"
    assert body["traceId"]
    assert response.headers["X-Trace-Id"] == body["traceId"]


def test_validation_error_shape(app):
    @app.get("/validar")
    def validar(n: int = 0):
        return {"n": n}

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/validar?n=no-es-numero")

    assert response.status_code == 422
    body = response.json()
    assert body["code"] == "invalid_request"
    assert body["traceId"]
    assert isinstance(body["details"], list)
    assert body["details"][0]["loc"]


def test_unhandled_no_filtra_stack(app):
    @app.get("/crash")
    def crash():
        raise RuntimeError("detalle-interno-secreto")

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/crash")

    assert response.status_code == 500
    body = response.json()
    assert body["code"] == "internal_error"
    assert "detalle-interno-secreto" not in response.text
    assert "Traceback" not in response.text
