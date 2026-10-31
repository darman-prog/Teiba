"""Libro de parques: catálogo de solo lectura para el rol usuario."""
from typing import Annotated

from fastapi import APIRouter, Depends, Path
from pymongo.errors import PyMongoError

from app.api.deps import get_park_repository
from app.api.errors import ApiError
from app.domain.parks import generar_indicaciones
from app.infrastructure.mongo_repositories import MongoParkRepository
from app.schemas import (
    Indicacion,
    ParqueDetalle,
    ParqueListResponse,
    ParqueResumen,
    ParqueSector,
)

router = APIRouter(tags=["parques"])


@router.get("/parques", response_model=ParqueListResponse)
def listar_parques(
    parques: Annotated[MongoParkRepository, Depends(get_park_repository)],
) -> ParqueListResponse:
    try:
        docs = parques.list_parques()
    except PyMongoError as exc:
        raise ApiError(
            503,
            "db_unavailable",
            "La base de datos no está disponible.",
        ) from exc
    items = [ParqueResumen(**doc) for doc in docs]
    return ParqueListResponse(items=items, total=len(items))


@router.get("/parques/{codigo}", response_model=ParqueDetalle)
def detalle_parque(
    parques: Annotated[MongoParkRepository, Depends(get_park_repository)],
    codigo: Annotated[str, Path(pattern=r"^[A-Za-z0-9-]{1,20}$")],
) -> ParqueDetalle:
    try:
        doc = parques.get_parque(codigo)
    except PyMongoError as exc:
        raise ApiError(
            503,
            "db_unavailable",
            "La base de datos no está disponible.",
        ) from exc
    if doc is None:
        raise ApiError(404, "not_found", f"No existe el parque '{codigo}'.")
    sectores = [ParqueSector(**sector) for sector in doc.get("sectores", [])]
    indicaciones = [
        Indicacion(**item)
        for item in generar_indicaciones(
            doc.get("tipo_parque"), doc.get("estado_general"), doc.get("sectores", [])
        )
    ]
    ubicacion = doc.get("ubicacion") or {}
    return ParqueDetalle(
        codigo=doc.get("codigo", ""),
        nombre=doc.get("nombre", ""),
        comuna=doc.get("comuna", ubicacion.get("comuna")),
        direccion=doc.get("direccion", ubicacion.get("direccion")),
        area_m2=doc.get("area_m2"),
        tipo_parque=doc.get("tipo_parque"),
        estado_general=doc.get("estado_general"),
        sectores=sectores,
        indicaciones=indicaciones,
    )
