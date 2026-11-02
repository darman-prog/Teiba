"""Incidentes ciudadanos: lectura y ciclo de estado para el administrador."""
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from app.api.deps import get_admin_actor, get_maintenance_service
from app.api.errors import ApiError
from app.application.maintenance import MaintenanceService
from app.application.serializers import iso
from app.domain.profiles import Actor
from app.schemas import (
    IncidenteEstadoRequest,
    IncidenteItem,
    IncidenteListResponse,
    IncidenteReportante,
    MantenimientoParque,
)

router = APIRouter(prefix="/incidentes", tags=["mantenimientos"])


def _parque(doc: dict | None) -> MantenimientoParque | None:
    if not doc:
        return None
    return MantenimientoParque(
        id=str(doc["id"]),
        codigo=doc.get("codigo"),
        nombre=doc.get("nombre", ""),
    )


def _item(doc: dict) -> IncidenteItem:
    reportante = doc.get("reportado_por")
    return IncidenteItem(
        id=str(doc["_id"]),
        tipo=doc.get("tipo"),
        descripcion=doc.get("descripcion"),
        fecha_hora=iso(doc.get("fecha_hora")),
        estado=doc["estado"],
        prioridad=doc.get("prioridad"),
        parque=_parque(doc.get("parque")),
        reportado_por=(
            IncidenteReportante(
                id=str(reportante["id"]),
                nombre=reportante.get("nombre", ""),
            )
            if reportante
            else None
        ),
    )


@router.get("", response_model=IncidenteListResponse)
def listar_incidentes(
    service: Annotated[MaintenanceService, Depends(get_maintenance_service)],
    actor: Annotated[Actor, Depends(get_admin_actor)],
    parque: str | None = Query(default=None, max_length=20),
    estado: str | None = Query(
        default=None,
        pattern="^(reportado|en_revision|en_proceso|resuelto)$",
    ),
    limite: int = Query(default=50, ge=1, le=50),
) -> IncidenteListResponse:
    docs = service.listar_incidentes(
        actor,
        parque_codigo=parque,
        estados=[estado] if estado else None,
        limite=limite,
    )
    items = [_item(doc) for doc in docs]
    return IncidenteListResponse(items=items, total=len(items))


@router.patch("/{incidente_id}/estado", response_model=IncidenteItem)
def cambiar_estado_incidente(
    incidente_id: Annotated[str, Path(min_length=1, max_length=40)],
    body: IncidenteEstadoRequest,
    service: Annotated[MaintenanceService, Depends(get_maintenance_service)],
    actor: Annotated[Actor, Depends(get_admin_actor)],
) -> IncidenteItem:
    doc = service.cambiar_estado_incidente(actor, incidente_id, body.estado)
    if doc is None:
        raise ApiError(404, "not_found", f"No existe el incidente '{incidente_id}'.")
    return _item(doc)
