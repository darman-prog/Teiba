"""Inventario de parques para vincular elementos a tareas."""
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_admin_actor, get_maintenance_service
from app.application.maintenance import MaintenanceService
from app.domain.profiles import Actor
from app.schemas import ElementoItem, ElementoListResponse, ElementoSector

router = APIRouter(prefix="/elementos", tags=["mantenimientos"])


def _sector(doc: dict | None) -> ElementoSector | None:
    if not doc:
        return None
    return ElementoSector(
        id=str(doc["id"]),
        codigo=doc.get("codigo"),
        nombre=doc.get("nombre"),
    )


@router.get("", response_model=ElementoListResponse)
def listar_elementos(
    service: Annotated[MaintenanceService, Depends(get_maintenance_service)],
    actor: Annotated[Actor, Depends(get_admin_actor)],
    parque: str | None = Query(default=None, max_length=20),
    limite: int = Query(default=50, ge=1, le=50),
) -> ElementoListResponse:
    docs = service.listar_elementos(actor, parque_codigo=parque, limite=limite)
    items = [
        ElementoItem(
            id=str(doc["_id"]),
            tipo_elemento=doc.get("tipo_elemento"),
            cantidad=doc.get("cantidad"),
            estado=doc.get("estado"),
            sector=_sector(doc.get("sector")),
        )
        for doc in docs
    ]
    return ElementoListResponse(items=items, total=len(items))
