"""Middlewares de trazabilidad y rate limit.

El rate limit es en memoria y de un solo proceso: suficiente para la demo
local, no para producción multi-worker.
"""
import logging
import threading
import time
import uuid
from collections import deque

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.errors import error_payload

logger = logging.getLogger("teiba.api")

AGENT_PATH = "/api/agente/consulta"


class TraceIdMiddleware(BaseHTTPMiddleware):
    """Propaga un identificador por request y lo devuelve en `X-Trace-Id`."""

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-Id") or uuid.uuid4().hex
        request.state.trace_id = request_id
        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000
        response.headers["X-Trace-Id"] = request_id
        logger.info(
            "%s %s %s %.1fms trace_id=%s",
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
            request_id,
        )
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Limita por IP y por concurrencia solo el endpoint que llama al LLM."""

    def __init__(self, app, max_per_minute: int = 10, max_concurrent: int = 2):
        super().__init__(app)
        self.max_per_minute = max(1, max_per_minute)
        self._hits: dict[str, deque[float]] = {}
        self._lock = threading.Lock()
        self._semaphore = threading.BoundedSemaphore(max(1, max_concurrent))

    def _too_many(self, request: Request, message: str, retry_after: int) -> JSONResponse:
        return JSONResponse(
            status_code=429,
            content=error_payload(
                request,
                "rate_limited",
                message,
                {"retry_after": retry_after},
            ),
            headers={"Retry-After": str(retry_after)},
        )

    async def dispatch(self, request: Request, call_next):
        if request.method != "POST" or request.url.path != AGENT_PATH:
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.monotonic()
        with self._lock:
            hits = self._hits.setdefault(client_ip, deque())
            # Ventana deslizante de 60 s por IP; solo cuenta el endpoint del LLM.
            while hits and now - hits[0] >= 60.0:
                hits.popleft()
            if len(hits) >= self.max_per_minute:
                retry_after = max(1, int(60.0 - (now - hits[0])) + 1)
                return self._too_many(
                    request,
                    "Demasiadas consultas. Intenta de nuevo en unos segundos.",
                    retry_after,
                )
            hits.append(now)

        # Si ya hay dos consultas en vuelo, responde rápido en vez de encolar.
        if not self._semaphore.acquire(blocking=False):
            return self._too_many(
                request,
                "El agente está ocupado. Intenta de nuevo en un momento.",
                2,
            )
        try:
            return await call_next(request)
        finally:
            self._semaphore.release()
