"""Caché en memoria para el plan B de la demo.

No es una caché distribuida: vive en el proceso y se reinicia con él.
"""
import threading
import time


class ResponseCache:
    def __init__(self, ttl_seconds: int = 600):
        self._ttl = max(1, ttl_seconds)
        self._data: dict[str, tuple[float, str, list[dict]]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> tuple[str, list[dict]] | None:
        with self._lock:
            item = self._data.get(key)
            if item is None:
                return None
            expires_at, respuesta, trazas = item
            if time.monotonic() > expires_at:
                self._data.pop(key, None)
                return None
            return respuesta, trazas

    def set(self, key: str, respuesta: str, trazas: list[dict]) -> None:
        with self._lock:
            self._data[key] = (
                time.monotonic() + self._ttl,
                respuesta,
                trazas,
            )
