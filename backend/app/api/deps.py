"""Dependencias de la API: repositorios y runner del agente."""
from functools import lru_cache

from app.agent.loop import AgentRunner
from app.agent.tools import AgentTools
from app.application.errors import AgentError
from app.config import get_settings
from app.db import get_db
from app.infrastructure.clock import SystemClock
from app.infrastructure.llm import OpenCodeLLMClient
from app.infrastructure.mongo_repositories import (
    MongoDeviceRepository,
    MongoReadingRepository,
)


def get_device_repository() -> MongoDeviceRepository:
    return MongoDeviceRepository(get_db())


def get_reading_repository() -> MongoReadingRepository:
    return MongoReadingRepository(get_db())


@lru_cache
def _build_agent_runner() -> AgentRunner:
    """Un solo runner por proceso para que la caché de demo sobreviva."""
    settings = get_settings()
    if not settings.llm_configurado:
        raise AgentError(
            503,
            "llm_not_configured",
            "La API del agente no está configurada. Define OPENCODE_API_KEY.",
        )
    devices = MongoDeviceRepository(get_db())
    readings = MongoReadingRepository(get_db())
    tools = AgentTools(
        devices,
        readings,
        SystemClock(),
        sin_reportar_min=settings.sin_reportar_min,
    )
    llm = OpenCodeLLMClient(settings)
    return AgentRunner(llm, tools, settings)


def get_agent_runner() -> AgentRunner:
    return _build_agent_runner()
