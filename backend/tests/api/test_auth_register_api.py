"""Contrato del registro público: rol fijo, perfil ciudadano y compensación."""
from fastapi.testclient import TestClient

from app.api.deps import get_profile_repository
from app.domain.auth.errors import AlmacenPerfilNoDisponible

ORIGIN = "http://testserver"
PASSWORD = "clave-segura-123"


def _register(
    client: TestClient,
    correo: str,
    contrasena: str = PASSWORD,
    *,
    nombre: str | None = "Nueva Ciudadana",
    origin: str | None = ORIGIN,
):
    body: dict[str, object] = {"correo": correo, "contrasena": contrasena}
    if nombre is not None:
        body["nombre"] = nombre
    headers = {"Origin": origin} if origin else {}
    return client.post("/api/auth/register", json=body, headers=headers)


def test_registro_publico_crea_ciudadano_y_sesion(client, _auth_env):
    resp = _register(client, "nueva@teiba.local")

    assert resp.status_code == 201
    body = resp.json()
    assert body["usuario"] == {"correo": "nueva@teiba.local", "rol": "user"}
    assert body["perfil"]["rol"] == "ciudadano"
    assert body["perfil"]["nombre"] == "Nueva Ciudadana"
    assert "HttpOnly" in resp.headers.get("set-cookie", "")

    me = client.get("/api/auth/me")
    assert me.status_code == 200
    assert me.json()["usuario"]["correo"] == "nueva@teiba.local"


def test_registro_normaliza_correo_y_nombre_por_defecto(client, _auth_env):
    resp = _register(client, "  Nueva.Dos@TEIBA.local  ", nombre="   ")

    assert resp.status_code == 201
    body = resp.json()
    assert body["usuario"]["correo"] == "nueva.dos@teiba.local"
    assert body["perfil"]["nombre"] == "nueva.dos"


def test_registro_correo_duplicado_409(client, _auth_env):
    assert _register(client, "repetida@teiba.local").status_code == 201
    resp = _register(client, "repetida@teiba.local")

    assert resp.status_code == 409
    assert resp.json()["code"] == "email_taken"


def test_registro_contrasena_corta_422(client, _auth_env):
    resp = _register(client, "corta@teiba.local", "corta123")

    assert resp.status_code == 422


def test_registro_contrasena_mayor_a_72_bytes_422(client, _auth_env):
    resp = _register(client, "larga@teiba.local", "a" * 73)

    assert resp.status_code == 422


def test_registro_ignora_rol_del_cliente(client, _auth_env):
    resp = client.post(
        "/api/auth/register",
        json={
            "correo": "escalada@teiba.local",
            "contrasena": PASSWORD,
            "rol": "admin",
        },
        headers={"Origin": ORIGIN},
    )

    # `extra=forbid`: el rol ni siquiera se acepta en el contrato.
    assert resp.status_code == 422


def test_registro_sin_origin_403(client, _auth_env):
    resp = _register(client, "sin-origen@teiba.local", origin=None)

    assert resp.status_code == 403
    assert resp.json()["code"] == "csrf_origin"


def test_registro_rate_limit_429(client, _auth_env):
    for i in range(5):
        assert _register(client, f"cupo{i}@teiba.local").status_code == 201

    resp = _register(client, "cupo-excedido@teiba.local")
    assert resp.status_code == 429
    assert resp.json()["code"] == "rate_limited"


class _PerfilCaido:
    def create_perfil(self, correo: str, nombre: str, rol: str):
        raise AlmacenPerfilNoDisponible()

    def get_by_correo(self, correo: str):
        return None


def test_registro_compensa_sqlite_si_mongo_falla(client, _auth_env):
    client.app.dependency_overrides[get_profile_repository] = lambda: _PerfilCaido()

    resp = _register(client, "huerfana@teiba.local")

    assert resp.status_code == 503
    assert resp.json()["code"] == "db_unavailable"
    # La identidad SQLite se revirtió: no puede quedar una cuenta a medias.
    assert (
        client.post(
            "/api/auth/login",
            json={"correo": "huerfana@teiba.local", "contrasena": PASSWORD},
            headers={"Origin": ORIGIN},
        ).status_code
        == 401
    )


class _PerfilDuplicado:
    def create_perfil(self, correo: str, nombre: str, rol: str):
        return None

    def get_by_correo(self, correo: str):
        return None


def test_registro_no_hereda_perfil_existente_409(client, _auth_env):
    client.app.dependency_overrides[get_profile_repository] = lambda: _PerfilDuplicado()

    resp = _register(client, "perfil-ajeno@teiba.local")

    assert resp.status_code == 409
    assert (
        client.post(
            "/api/auth/login",
            json={"correo": "perfil-ajeno@teiba.local", "contrasena": PASSWORD},
            headers={"Origin": ORIGIN},
        ).status_code
        == 401
    )
