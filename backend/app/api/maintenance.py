"""API de mantenimientos: lista, detalle, asignación y transiciones."""
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from app.api.deps import (
    get_admin_actor,
    get_maintenance_actor,
    get_maintenance_service,
)
from app.api.errors import ApiError
from app.application.maintenance import CambioEstado, MaintenanceService, NuevaTarea
from app.application.serializers import iso
from app.domain.maintenance import EstadoMantenimiento, calcular_vencida
from app.domain.profiles import Actor
from app.schemas import (
    MantenimientoCreateRequest,
    MantenimientoElemento,
    MantenimientoEstadoRequest,
    MantenimientoIncidente,
    MantenimientoItem,
    MantenimientoListResponse,
    MantenimientoParque,
    MantenimientoReasignarRequest,
    MantenimientoResponsable,
)

router = APIRouter(prefix="/mantenimientos", tags=["mantenimientos"])

ActorMantenimiento = Annotated[Actor, Depends(get_maintenance_actor)]
AdminMantenimiento = Annotated[Actor, Depends(get_admin_actor)]
Servicio = Annotated[MaintenanceService, Depends(get_maintenance_service)]


def _parque(doc: dict | None) -> MantenimientoParque | None:
    if not doc:
        return None
    return MantenimientoParque(
        id=str(doc["id"]),
        codigo=doc.get("codigo"),
        nombre=doc.get("nombre", ""),
    )


def _responsable(doc: dict | None) -> MantenimientoResponsable | None:
    if not doc:
        return None
    return MantenimientoResponsable(
        id=str(doc["id"]),
        nombre=doc.get("nombre", ""),
        rol=doc.get("rol"),
    )


def _incidente(doc: dict | None) -> MantenimientoIncidente | None:
    if not doc:
        return None
    return MantenimientoIncidente(
        id=str(doc["id"]),
        tipo=doc.get("tipo"),
        descripcion=doc.get("descripcion"),
        prioridad=doc.get("prioridad"),
        estado=doc.get("estado"),
    )


def _elemento(doc: dict | None) -> MantenimientoElemento | None:
    if not doc:
        return None
    return MantenimientoElemento(
        id=str(doc["id"]),
        tipo_elemento=doc.get("tipo_elemento"),
        cantidad=doc.get("cantidad"),
        estado=doc.get("estado"),
    )


def _item(doc: dict, ahora: datetime) -> MantenimientoItem:
    fecha = doc.get("fecha_programada")
    vencida = False
    if fecha is not None:
        vencida = calcular_vencida(
            EstadoMantenimiento(doc["estado"]),
            fecha,
            ahora,
        )
    return MantenimientoItem(
        id=str(doc["_id"]),
        tipo=doc["tipo"],
        descripcion=doc["descripcion"],
        prioridad=doc["prioridad"],
        estado=doc["estado"],
        fecha_programada=iso(fecha),
        fecha_ejecucion=iso(doc.get("fecha_ejecucion")),
        fecha_reapertura=iso(doc.get("fecha_reapertura")),
        nota_cierre=doc.get("nota_cierre"),
        nota_reapertura=doc.get("nota_reapertura"),
        costo_estimado=doc.get("costo_estimado"),
        vencida=vencida,
        parque=_parque(doc.get("parque")),
        responsable=_responsable(doc.get("responsable")),
        incidente=_incidente(doc.get("incidente")),
        elemento=_elemento(doc.get("elemento")),
    )


@router.get("", response_model=MantenimientoListResponse)
def listar_mantenimientos(
    service: Servicio,
    actor: ActorMantenimiento,
    estado: str | None = Query(
        default=None,
        pattern="^(pendiente|en_proceso|finalizado)$",
    ),
    prioridad: str | None = Query(default=None, pattern="^(alta|media|baja)$"),
    parque: str | None = Query(default=None, max_length=20),
    responsable: str | None = Query(default=None, max_length=40),
    limite: int = Query(default=50, ge=1, le=50),
) -> MantenimientoListResponse:
    docs = service.listar(
        actor,
        estado=estado,
        prioridad=prioridad,
        parque_codigo=parque,
        responsable_id=responsable,
        limite=limite,
    )
    ahora = datetime.now(UTC)
    items = [_item(doc, ahora) for doc in docs]
    return MantenimientoListResponse(items=items, total=len(items))


@router.post("", response_model=MantenimientoItem, status_code=201)
def crear_mantenimiento(
    body: MantenimientoCreateRequest,
    service: Servicio,
    actor: AdminMantenimiento,
) -> MantenimientoItem:
    doc = service.crear(
        actor,
        NuevaTarea(
            tipo=body.tipo,
            descripcion=body.descripcion,
            fecha_programada=body.fecha_programada,
            prioridad=body.prioridad,
            parque_codigo=body.parque_codigo,
            responsable_id=body.responsable_id,
            elemento_id=body.elemento_id,
            incidente_id=body.incidente_id,
            costo_estimado=body.costo_estimado,
        ),
    )
    return _item(doc, datetime.now(UTC))


@router.get("/{tarea_id}", response_model=MantenimientoItem)
def detalle_mantenimiento(
    tarea_id: Annotated[str, Path(min_length=1, max_length=40)],
    service: Servicio,
    actor: ActorMantenimiento,
) -> MantenimientoItem:
    doc = service.detalle(actor, tarea_id)
    if doc is None:
        raise ApiError(404, "not_found", f"No existe la tarea '{tarea_id}'.")
    return _item(doc, datetime.now(UTC))


@router.patch("/{tarea_id}/estado", response_model=MantenimientoItem)
def cambiar_estado(
    tarea_id: Annotated[str, Path(min_length=1, max_length=40)],
    body: MantenimientoEstadoRequest,
    service: Servicio,
    actor: ActorMantenimiento,
) -> MantenimientoItem:
    doc = service.cambiar_estado(
        actor,
        tarea_id,
        CambioEstado(estado=body.estado, nota=body.nota),
    )
    if doc is None:
        raise ApiError(404, "not_found", f"No existe la tarea '{tarea_id}'.")
    return _item(doc, datetime.now(UTC))


@router.patch("/{tarea_id}/responsable", response_model=MantenimientoItem)
def reasignar(
    tarea_id: Annotated[str, Path(min_length=1, max_length=40)],
    body: MantenimientoReasignarRequest,
    service: Servicio,
    actor: AdminMantenimiento,
) -> MantenimientoItem:
    doc = service.reasignar(actor, tarea_id, body.responsable_id)
    if doc is None:
        raise ApiError(404, "not_found", f"No existe la tarea '{tarea_id}'.")
    return _item(doc, datetime.now(UTC))
