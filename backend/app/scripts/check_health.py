"""Comprueba el endpoint /api/health de la API en ejecución."""
import json
import os
import sys

import httpx

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")


def main() -> int:
    try:
        response = httpx.get(f"{API_URL}/api/health", timeout=10)
    except httpx.HTTPError as exc:
        print(f"ERROR: no se pudo conectar con {API_URL}: {exc}")
        return 1

    body = response.json()
    print(json.dumps(body, ensure_ascii=False, indent=2))
    if response.status_code != 200:
        return 1
    if not body.get("mongo", {}).get("ok"):
        print("ERROR: MongoDB no responde. Revisa el contenedor mongo-iot.")
        return 1
    if not body.get("llm", {}).get("configurado"):
        print("ERROR: OPENCODE_API_KEY no está configurada en backend/.env.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
