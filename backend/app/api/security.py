"""Defensas transversales de la API: CSRF fail-closed y rate limit de login.

CSRF: para todo POST/PUT/PATCH/DELETE se exige un `Origin` que pertenezca a la
allowlist de CORS (o coincida con el propio origen de la request). Si falta o no
está permitido, se responde 403 csrf_origin. curl/Postman sin Origin se quedan
fuera, pero el navegador siempre envía Origin en POST (incluso same-origin).

Rate limit de login: contador en memoria por (IP, correo) que solo cuenta fallos
de autenticación dentro de una ventana deslizante.
"""
import time
from collections import deque
from threading import Lock

from fastapi import Request

from app.api.errors import ApiError
from app.config import Settings, get_settings


class _VerificadorOrigen:
    """Fail-closed: sin Origin o con Origin no permitido -> 403 csrf_origin."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def verificar(self, request: Request) -> None:
        # El preflight (OPTIONS) no lleva cookie ni carga util; se deja pasar.
        if request.method == "OPTIONS":
            return
        permitidos = set(self._settings.cors_origins_list)
        permitidos.add(self._origen_propio(request))
        origen = request.headers.get("origin")
        if not origen or origen not in permitidos:
            raise ApiError(403, "csrf_origin", "Origen de la peticion no permitido.")

    @staticmethod
    def _origen_propio(request: Request) -> str:
        host = request.headers.get("host")
        if not host:
            return ""
        esquema = "https" if request.url.scheme == "https" else "http"
        return f"{esquema}://{host}"


class _RateLimitLogin:
    """Cuenta fallos de login por (IP, correo) y responde 429 si supera el cupo."""

    def __init__(self, settings: Settings) -> None:
        self._max = max(1, settings.auth_login_max_failures)
        self._ventana = max(1, settings.auth_login_window_seconds)
        self._hits: dict[str, deque[float]] = {}
        self._lock = Lock()

    def _clave(self, request: Request, correo: str) -> str:
        ip = request.client.host if request.client else "unknown"
        return f"{ip}:{correo}"

    def _purgar(self, hits: deque[float], ahora: float) -> None:
        while hits and ahora - hits[0] >= self._ventana:
            hits.popleft()

    def registrar_fallo(self, request: Request, correo: str) -> None:
        clave = self._clave(request, correo)
        ahora = time.monotonic()
        with self._lock:
            hits = self._hits.setdefault(clave, deque())
            self._purgar(hits, ahora)
            hits.append(ahora)

    def comprobar(self, request: Request, correo: str) -> None:
        clave = self._clave(request, correo)
        ahora = time.monotonic()
        with self._lock:
            hits = self._hits.get(clave, deque())
            self._purgar(hits, ahora)
            if len(hits) >= self._max:
                reintento = max(1, int(self._ventana - (ahora - hits[0])) + 1)
                raise ApiError(
                    429,
                    "rate_limited",
                    "Demasiados intentos de acceso. Espera unos segundos.",
                    {"retry_after": reintento},
                )

    def reiniciar(self, request: Request, correo: str) -> None:
        clave = self._clave(request, correo)
        with self._lock:
            self._hits.pop(clave, None)


async def verificar_origen(request: Request) -> None:
    await _VerificadorOrigen(get_settings()).verificar(request)


def proveer_rate_limit_login() -> _RateLimitLogin:
    return _RateLimitLogin(get_settings())
