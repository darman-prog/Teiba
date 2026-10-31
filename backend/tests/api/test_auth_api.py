"""Contrato del login/logout/me, cookies y permisos."""
from fastapi.testclient import TestClient

ORIGIN = "http://testserver"


def _login(client: TestClient, correo: str, contrasena: str):
    return client.post(
        "/api/auth/login",
        json={"correo": correo, "contrasena": contrasena},
        headers={"Origin": ORIGIN},
    )


def test_login_ok_set_cookie(client, _auth_env):
    resp = _login(client, "admin@teiba.local", "admin12345678")
    assert resp.status_code == 200
    body = resp.json()
    assert body["usuario"]["correo"] == "admin@teiba.local"
    assert body["usuario"]["rol"] == "admin"
    assert body["expira_en"]
    cookie = resp.headers.get("set-cookie", "").lower()
    assert "teiba_session=" in cookie
    assert "httponly" in cookie
    assert "samesite=lax" in cookie
    assert "path=/api" in cookie
    import re as _re
    assert _re.search(r"max-age=2879\d", cookie)


def test_login_password_mala_401_generico(client, _auth_env):
    resp = _login(client, "admin@teiba.local", "contrasena-incorrecta")
    assert resp.status_code == 401
    assert resp.json()["code"] == "invalid_credentials"
    # No debe revelar si el correo existe.
    assert "correo" not in resp.json()["message"].lower() or "contraseña" in resp.json()["message"].lower()


def test_login_correo_inexistente_401_igual_que_mala(client, _auth_env):
    resp = _login(client, "no-existe@teiba.local", "alguna-clave-larga-1234")
    assert resp.status_code == 401
    assert resp.json()["code"] == "invalid_credentials"


def test_login_rate_limit_429(client, _auth_env, monkeypatch):
    monkeypatch.setenv("AUTH_LOGIN_MAX_FAILURES", "2")
    from app.config import get_settings
    get_settings.cache_clear()
    # Dos fallos agotan el cupo.
    assert _login(client, "admin@teiba.local", "mala-1").status_code == 401
    assert _login(client, "admin@teiba.local", "mala-2").status_code == 401
    resp = _login(client, "admin@teiba.local", "admin12345678")
    assert resp.status_code == 429
    assert resp.json()["code"] == "rate_limited"
    assert resp.headers["Retry-After"]


def test_login_usuario_desactivado_401(client, _auth_env):
    import sqlite3
    base_path = _auth_env
    conn = sqlite3.connect(base_path)
    conn.execute("UPDATE users SET is_active = 0 WHERE email = ?", ("user@teiba.local",))
    conn.commit()
    conn.close()
    resp = _login(client, "user@teiba.local", "user12345678")
    assert resp.status_code == 401
    assert resp.json()["code"] == "invalid_credentials"


def test_login_72_bytes_rechazado(client, _auth_env):
    # Contrasena de 80 bytes (40 caracteres UTF-8 de 2 bytes... usemos 80 'a')
    resp = _login(client, "admin@teiba.local", "a" * 80)
    assert resp.status_code == 422


def test_logout_204_y_revoca(client, _auth_env):
    resp_login = _login(client, "admin@teiba.local", "admin12345678")
    assert resp_login.status_code == 200
    client.cookies.set("teiba_session", resp_login.cookies.get("teiba_session"))
    resp_logout = client.post("/api/auth/logout", headers={"Origin": ORIGIN})
    assert resp_logout.status_code == 204
    # Tras logout, me -> 401.
    resp_me = client.get("/api/auth/me")
    assert resp_me.status_code == 401
    assert resp_me.json()["code"] == "not_authenticated"


def test_logout_sin_sesion_204_igual(client, _auth_env):
    resp = client.post("/api/auth/logout", headers={"Origin": ORIGIN})
    assert resp.status_code == 204


def test_me_sin_cookie_401(client, _auth_env):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401
    assert resp.json()["code"] == "not_authenticated"


def test_me_ok_con_sesion(client, _auth_env):
    resp_login = _login(client, "user@teiba.local", "user12345678")
    assert resp_login.status_code == 200
    client.cookies.set("teiba_session", resp_login.cookies.get("teiba_session"))
    resp = client.get("/api/auth/me")
    assert resp.status_code == 200
    assert resp.json()["usuario"]["correo"] == "user@teiba.local"
    assert resp.json()["usuario"]["rol"] == "user"


def test_csrf_sin_origin_403(client, _auth_env):
    resp = client.post(
        "/api/auth/login",
        json={"correo": "admin@teiba.local", "contrasena": "admin12345678"},
    )
    assert resp.status_code == 403
    assert resp.json()["code"] == "csrf_origin"


def test_csrf_origen_no_permitido_403(client, _auth_env):
    resp = client.post(
        "/api/auth/login",
        json={"correo": "admin@teiba.local", "contrasena": "admin12345678"},
        headers={"Origin": "http://evil.test"},
    )
    assert resp.status_code == 403
    assert resp.json()["code"] == "csrf_origin"


def test_parques_anonimo_401(client, _auth_env):
    resp = client.get("/api/parques")
    assert resp.status_code == 401
    assert resp.json()["code"] == "not_authenticated"


def test_agente_user_403(client, _auth_env):
    resp_login = _login(client, "user@teiba.local", "user12345678")
    assert resp_login.status_code == 200
    client.cookies.set("teiba_session", resp_login.cookies.get("teiba_session"))
    resp = client.post(
        "/api/agente/consulta",
        json={"pregunta": "¿Cómo está el suelo?"},
        headers={"Origin": ORIGIN},
    )
    assert resp.status_code == 403
    assert resp.json()["code"] == "forbidden"
