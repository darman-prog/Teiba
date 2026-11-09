"""Smoke test de las dos consultas de la demo.

Requiere la API en ejecución, SQLite con seed_auth, MongoDB con el seed y
`OPENCODE_API_KEY`. Se autentica como admin antes de consultar.
"""
import json
import os
import sys

import httpx

from app.config import cargar_env_local

cargar_env_local()

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
ORIGIN = os.getenv("ORIGIN", "http://localhost:5173")
PREGUNTA_PRINCIPAL = "¿Cómo está el sensor de calidad del suelo del Sector Norte?"
PREGUNTA_ANTENA = "¿Qué sensores dependen de la antena ANT-01 y alguno está sin reportar?"


def _autenticarse(client: httpx.Client) -> bool:
    correo = os.getenv("AUTH_ADMIN_EMAIL", "admin@teiba.local")
    contrasena = os.getenv("AUTH_ADMIN_PASSWORD", "")
    resp = client.post(
        f"{API_URL}/api/auth/login",
        json={"correo": correo, "contrasena": contrasena},
        headers={"Origin": ORIGIN},
    )
    if resp.status_code != 200:
        print(f"ERROR login {resp.status_code}: {resp.text}")
        return False
    return True


def _consultar(client: httpx.Client, pregunta: str) -> dict | None:
    try:
        response = client.post(
            f"{API_URL}/api/agente/consulta",
            json={"pregunta": pregunta},
            headers={"Origin": ORIGIN},
            timeout=90,
        )
    except httpx.HTTPError as exc:
        print(f"ERROR: no se pudo conectar con la API: {exc}")
        return None
    if response.status_code != 200:
        print(f"ERROR {response.status_code}: {response.text}")
        return None
    return response.json()


def main() -> int:
    with httpx.Client() as client:
        if not _autenticarse(client):
            return 1
        principal = _consultar(client, PREGUNTA_PRINCIPAL)
        if principal is None:
            return 1
        tools_principal = [traza["tool"] for traza in principal["trazas"]]
        print("Pregunta 1:", PREGUNTA_PRINCIPAL)
        print("Respuesta 1:", principal["respuesta"])
        print("Herramientas 1:", tools_principal)

        ok_principal = (
            "SS-01" in principal["respuesta"]
            and "Sector Norte" in principal["respuesta"]
            and {"list_sensors", "get_sensor_history", "get_device_context"}
            <= set(tools_principal)
        )

        antena = _consultar(client, PREGUNTA_ANTENA)
        if antena is None:
            return 1
        tools_antena = [traza["tool"] for traza in antena["trazas"]]
        print("\nPregunta 2:", PREGUNTA_ANTENA)
        print("Respuesta 2:", antena["respuesta"])
        print("Herramientas 2:", tools_antena)

        ok_antena = "get_devices_by_antenna" in tools_antena and (
            "SS-02" in antena["respuesta"]
            or "sin_reportar" in json.dumps(antena["trazas"], ensure_ascii=False)
        )

    if not ok_principal:
        print("\nFALLO: la consulta principal no devolvió SS-01/Sector Norte con las 3 tools.")
    if not ok_antena:
        print("\nFALLO: la consulta de antena no marcó SS-02 o sin_reportar.")
    return 0 if ok_principal and ok_antena else 1


if __name__ == "__main__":
    sys.exit(main())
