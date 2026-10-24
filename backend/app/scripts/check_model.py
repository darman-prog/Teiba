"""Smoke test acotado del modelo: una pregunta, una corrida.

Uso:
    AGENT_MODEL=deepseek-v4.1-flash python -m app.scripts.check_model
    AGENT_MODEL=longcat-2.0 python -m app.scripts.check_model
"""
import os
import sys

import httpx

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
PREGUNTA = "¿Cómo está el sensor de calidad del suelo del Sector Norte?"


def main() -> int:
    try:
        response = httpx.post(
            f"{API_URL}/api/agente/consulta",
            json={"pregunta": PREGUNTA},
            timeout=90,
        )
    except httpx.HTTPError as exc:
        print(f"ERROR: no se pudo conectar con la API: {exc}")
        return 1
    if response.status_code != 200:
        print(f"ERROR {response.status_code}: {response.text}")
        return 1

    body = response.json()
    tools = [traza["tool"] for traza in body["trazas"]]
    print(f"Modelo: {body['meta']['modelo']}")
    print(f"Pasos: {body['meta']['pasos']}  Duración: {body['meta']['duracion_ms']} ms")
    print(f"Herramientas: {tools}")
    print(f"Respuesta: {body['respuesta']}")

    if "list_sensors" not in tools or "get_sensor_history" not in tools:
        print("FALLO: el modelo no completó la secuencia mínima de tools.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
