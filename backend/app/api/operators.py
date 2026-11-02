"""Operadores disponibles para asignar tareas."""
from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_admin_actor, get_maintenance_service
from app.application.maintenance import MaintenanceService
from app.domain.profiles import Actor
from app.schemas import OperadorItem, OperadorListResponse

router = APIRouter(prefix="/operadores", tags=["mantenimientos"])


@router.get("", response_model=OperadorListResponse)
def listar_operadores(
    service: Annotated[MaintenanceService, Depends(get_maintenance_service)],
    actor: Annotated[Actor, Depends(get_admin_actor)],
) -> OperadorListResponse:
    docs = service.listar_operadores(actor)
    items = [OperadorItem(id=str(doc["_id"]), nombre=doc["nombre"]) for doc in docs]
    return OperadorListResponse(items=items, total=len(items))
