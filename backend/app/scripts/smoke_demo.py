"""Smoke test de las dos consultas de la demo.

Requiere la API en ejecución, MongoDB con el seed y `OPENCODE_API_KEY`.
"""
import json
import os
import sys

import httpx

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
PREGUNTA_PRINCIPAL = "¿Cómo está el sensor de calidad del suelo del Sector Norte?"
PREGUNTA_ANTENA = "¿Qué sensores dependen de la antena ANT-01 y alguno está sin reportar?"


def _consultar(pregunta: str) -> dict | None:
    try:
        response = httpx.post(
            f"{API_URL}/api/agente/consulta",
            json={"pregunta": pregunta},
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
    principal = _consultar(PREGUNTA_PRINCIPAL)
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

    antena = _consultar(PREGUNTA_ANTENA)
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
