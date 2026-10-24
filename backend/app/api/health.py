"""Endpoint de salud: no expone URI, versión de Mongo ni secretos."""
from fastapi import APIRouter

from app import db as db_module
from app.config import get_settings
from app.schemas import HealthResponse, LlmHealth, MongoHealth

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    settings = get_settings()
    mongo_ok = db_module.ping()
    llm_ok = settings.llm_configurado
    return HealthResponse(
        status="ok" if mongo_ok and llm_ok else "degraded",
        mongo=MongoHealth(ok=mongo_ok, db=settings.mongodb_db),
        llm=LlmHealth(configurado=llm_ok, modelo=settings.agent_model),
        version=settings.app_version,
    )
