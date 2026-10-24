"""Catálogo de sensores para la tira de estado del panel."""
from datetime import UTC, datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query
from pymongo.errors import PyMongoError

from app.api.deps import get_device_repository, get_reading_repository
from app.api.errors import ApiError
from app.application.serializers import antiguedad_min, serialize_lectura, str_id
from app.config import Settings, get_settings
from app.domain.ranges import evaluar_lectura
from app.infrastructure.mongo_repositories import (
    MongoDeviceRepository,
    MongoReadingRepository,
)
from app.schemas import SensorItem, SensorListResponse, UltimaLectura

TipoDispositivo = Literal[
    "calidad_suelo",
    "estacion_meteorologica",
    "luminaria_inteligente",
    "antena_enlace",
]

router = APIRouter(tags=["sensores"])


def _estado(
    evaluacion: dict | None,
    antiguedad: int | None,
    sin_reportar_min: int,
) -> str:
    if evaluacion is None:
        return "sin_datos"
    # El color resume la última lectura, no todo el histórico de la ventana.
    if evaluacion["fuera_de_rango"]:
        return "danger"
    if antiguedad is not None and antiguedad > sin_reportar_min:
        return "warning"
    return "ok"


@router.get("/sensores", response_model=SensorListResponse)
def listar_sensores(
    devices: Annotated[MongoDeviceRepository, Depends(get_device_repository)],
    readings: Annotated[MongoReadingRepository, Depends(get_reading_repository)],
    settings: Annotated[Settings, Depends(get_settings)],
    tipo: TipoDispositivo = "calidad_suelo",
    limite: Annotated[int, Query(ge=1, le=50)] = 50,
) -> SensorListResponse:
    try:
        docs = devices.find_devices(tipo=tipo, limite=limite)
        latest = readings.latest_many([doc["_id"] for doc in docs])
    except PyMongoError as exc:
        raise ApiError(
            503,
            "db_unavailable",
            "La base de datos no está disponible.",
        ) from exc

    ahora = datetime.now(UTC)
    items = []
    for doc in docs:
        ultima = latest.get(doc["_id"])
        antiguedad = antiguedad_min(ultima.get("timestamp"), ahora) if ultima else None
        evaluacion = evaluar_lectura(ultima) if ultima else None
        items.append(
            SensorItem(
                id=doc["_id"],
                tipo=doc.get("tipo", ""),
                marca=doc.get("marca"),
                sector=doc.get("sector"),
                sector_id=str_id(doc.get("sector_id")),
                parque=doc.get("parque"),
                comuna=doc.get("comuna"),
                depende_de=doc.get("depende_de"),
                alimentado_por=doc.get("alimentado_por"),
                ultima_lectura=(
                    UltimaLectura(**serialize_lectura(ultima, ahora)) if ultima else None
                ),
                estado=_estado(evaluacion, antiguedad, settings.sin_reportar_min),
            )
        )
    return SensorListResponse(items=items, total=len(items))
