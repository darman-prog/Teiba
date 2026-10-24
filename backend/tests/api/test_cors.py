"""CORS con allowlist explícita, sin comodines."""
def test_cors_origen_permitido(client):
    response = client.get(
        "/api/health",
        headers={"Origin": "http://localhost:5173"},
    )

    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"


def test_cors_origen_rechazado(client):
    response = client.get(
        "/api/health",
        headers={"Origin": "http://evil.test"},
    )

    assert "access-control-allow-origin" not in response.headers


def test_cors_preflight(client):
    response = client.options(
        "/api/agente/consulta",
        headers={
            "Origin": "http://127.0.0.1:5173",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:5173"
