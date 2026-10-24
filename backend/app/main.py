"""Punto de entrada de la API Teiba Sage.

Orden de middlewares: CORS (outer) → TrustedHost → TraceId → RateLimit.
Así el 429 también sale con CORS y `X-Trace-Id`.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app import db as db_module
from app.api.agent import router as agent_router
from app.api.errors import register_exception_handlers
from app.api.health import router as health_router
from app.api.middleware import RateLimitMiddleware, TraceIdMiddleware
from app.api.sensors import router as sensors_router
from app.config import get_settings


def create_app() -> FastAPI:
    """Fábrica de la app para poder testear con configuración aislada."""
    settings = get_settings()
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if not settings.llm_configurado:
            logging.getLogger("teiba.api").warning(
                "OPENCODE_API_KEY no configurada: /api/agente/consulta responderá 503."
            )
        yield
        db_module.close_client()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
    )

    # El último middleware agregado queda más afuera.
    app.add_middleware(
        RateLimitMiddleware,
        max_per_minute=settings.rate_limit_per_minute,
        max_concurrent=settings.rate_limit_concurrent,
    )
    app.add_middleware(TraceIdMiddleware)
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.allowed_hosts_list,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "X-Request-Id"],
        expose_headers=["X-Trace-Id"],
        max_age=600,
    )

    register_exception_handlers(app)
    app.include_router(health_router, prefix="/api")
    app.include_router(agent_router, prefix="/api")
    app.include_router(sensors_router, prefix="/api")
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
