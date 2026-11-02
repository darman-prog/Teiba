"""Casos de uso de mantenimientos: asignación, ejecución y vínculos."""
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from bson import ObjectId

from app.application.ports import (
    Clock,
    IncidentRepository,
    InventoryRepository,
    MaintenanceRepository,
    ParkRepository,
    ProfileRepository,
)
from app.domain.incidents import (
    EstadoIncidente,
)
from app.domain.incidents import (
    validar_transicion as validar_transicion_incidente,
)
from app.domain.maintenance import (
    ErrorMantenimiento,
    EstadoMantenimiento,
    PermisoDenegado,
    Prioridad,
    TipoMantenimiento,
    puede_crear,
    puede_gestionar_incidentes,
    puede_reasignar,
    puede_ver_tarea,
    validar_transicion,
)
from app.domain.profiles import Actor, RolDominio


@dataclass(frozen=True)
class NuevaTarea:
    tipo: str
    descripcion: str
    fecha_programada: datetime
    prioridad: str
    parque_codigo: str
    responsable_id: str
    elemento_id: str | None = None
    incidente_id: str | None = None
    costo_estimado: float | None = None


@dataclass(frozen=True)
class CambioEstado:
    estado: str
    nota: str | None = None


def _oid(value: str) -> ObjectId:
    """Convierte un id textual a ObjectId; un id inválido es error de negocio."""
    if not isinstance(value, str) or not ObjectId.is_valid(value):
        raise ErrorMantenimiento("Identificador inválido.")
    return ObjectId(value)


class MaintenanceService:
    """Orquesta repositorios y reglas de dominio sin conocer HTTP."""

    def __init__(
        self,
        tareas: MaintenanceRepository,
        perfiles: ProfileRepository,
        incidentes: IncidentRepository,
        inventario: InventoryRepository,
        parques: ParkRepository,
        clock: Clock,
    ) -> None:
        self._tareas = tareas
        self._perfiles = perfiles
        self._incidentes = incidentes
        self._inventario = inventario
        self._parques = parques
        self._clock = clock

    def listar(
        self,
        actor: Actor,
        *,
        estado: str | None = None,
        prioridad: str | None = None,
        parque_codigo: str | None = None,
        responsable_id: str | None = None,
        limite: int = 50,
    ) -> list[dict[str, Any]]:
        parque_id = self._resolver_parque(parque_codigo) if parque_codigo else None
        if actor.rol == RolDominio.ADMINISTRADOR:
            responsable = responsable_id
        elif actor.rol == RolDominio.OPERADOR_MANTENIMIENTO:
            # El operador nunca puede ampliar el filtro a tareas ajenas.
            responsable = actor.perfil_id
        else:
            raise PermisoDenegado("No tienes acceso a mantenimientos.")
        return self._tareas.list_tareas(
            estado=estado,
            prioridad=prioridad,
            parque_id=parque_id,
            responsable_id=responsable,
            limite=limite,
        )

    def detalle(self, actor: Actor, tarea_id: str) -> dict[str, Any] | None:
        tarea = self._tareas.get_tarea(_oid(tarea_id))
        if tarea is None:
            return None
        if not puede_ver_tarea(actor, str(tarea["responsable_id"])):
            raise PermisoDenegado("No puedes ver una tarea ajena.")
        return tarea

    def crear(self, actor: Actor, nueva: NuevaTarea) -> dict[str, Any]:
        if not puede_crear(actor):
            raise PermisoDenegado("Solo el administrador puede asignar tareas.")

        parque_id = self._resolver_parque(nueva.parque_codigo)
        responsable = self._validar_operador(nueva.responsable_id)
        responsable_id = (
            responsable["_id"]
            if isinstance(responsable["_id"], ObjectId)
            else _oid(responsable["_id"])
        )
        elemento_id = self._validar_elemento(nueva.elemento_id, parque_id)
        incidente_id = self._validar_incidente(nueva.incidente_id, parque_id)

        try:
            tipo = TipoMantenimiento(nueva.tipo).value
            prioridad = Prioridad(nueva.prioridad).value
        except ValueError as exc:
            raise ErrorMantenimiento("Tipo o prioridad inválidos.") from exc

        descripcion = nueva.descripcion.strip()
        if not descripcion:
            raise ErrorMantenimiento("La descripción es obligatoria.")

        doc = {
            "tipo": tipo,
            "descripcion": descripcion,
            "fecha_programada": nueva.fecha_programada,
            "fecha_ejecucion": None,
            "estado": EstadoMantenimiento.PENDIENTE.value,
            "prioridad": prioridad,
            "nota_cierre": None,
            "nota_reapertura": None,
            "fecha_reapertura": None,
            "incidente_id": incidente_id,
            "parque_id": parque_id,
            "elemento_id": elemento_id,
            "responsable_id": responsable_id,
            "costo_estimado": nueva.costo_estimado,
        }
        tarea_id = self._tareas.create_tarea(doc)
        creada = self._tareas.get_tarea(tarea_id)
        if creada is None:
            raise ErrorMantenimiento("No se pudo recuperar la tarea creada.")
        return creada

    def cambiar_estado(
        self,
        actor: Actor,
        tarea_id: str,
        cambio: CambioEstado,
    ) -> dict[str, Any] | None:
        tarea = self._tareas.get_tarea(_oid(tarea_id))
        if tarea is None:
            return None
        transicion = validar_transicion(
            actor=actor,
            estado_actual=EstadoMantenimiento(tarea["estado"]),
            destino=EstadoMantenimiento(cambio.estado),
            responsable_id=str(tarea["responsable_id"]),
            nota=cambio.nota,
        )
        return self._tareas.update_estado(
            tarea_id,
            estado=transicion.estado.value,
            campo_nota=transicion.campo_nota,
            nota=transicion.nota,
            limpia_ejecucion=transicion.limpia_ejecucion,
            marca_reapertura=transicion.marca_reapertura,
            ahora=self._clock.now(),
        )

    def reasignar(
        self,
        actor: Actor,
        tarea_id: str,
        responsable_id: str,
    ) -> dict[str, Any] | None:
        tarea = self._tareas.get_tarea(_oid(tarea_id))
        if tarea is None:
            return None
        if not puede_reasignar(actor, EstadoMantenimiento(tarea["estado"])):
            raise PermisoDenegado("Solo el administrador reasigna tareas abiertas.")
        self._validar_operador(responsable_id)
        return self._tareas.reasignar(tarea_id, _oid(responsable_id))

    def listar_operadores(self, actor: Actor) -> list[dict[str, Any]]:
        if not puede_crear(actor):
            raise PermisoDenegado("Solo el administrador ve los operadores.")
        return self._perfiles.list_operadores()

    def listar_incidentes(
        self,
        actor: Actor,
        *,
        parque_codigo: str | None = None,
        estados: list[str] | None = None,
        limite: int = 50,
    ) -> list[dict[str, Any]]:
        if not puede_gestionar_incidentes(actor):
            raise PermisoDenegado("Solo el administrador ve incidentes.")
        parque_id = self._resolver_parque(parque_codigo) if parque_codigo else None
        return self._incidentes.list_incidentes(
            parque_id=parque_id,
            estados=estados,
            limite=limite,
        )

    def cambiar_estado_incidente(
        self,
        actor: Actor,
        incidente_id: str,
        estado: str,
    ) -> dict[str, Any] | None:
        if not puede_gestionar_incidentes(actor):
            raise PermisoDenegado("Solo el administrador cambia incidentes.")
        incidente = self._incidentes.get_incidente(_oid(incidente_id))
        if incidente is None:
            return None
        validar_transicion_incidente(
            EstadoIncidente(incidente["estado"]),
            EstadoIncidente(estado),
        )
        return self._incidentes.update_estado(incidente_id, estado)

    def listar_elementos(
        self,
        actor: Actor,
        *,
        parque_codigo: str | None = None,
        limite: int = 50,
    ) -> list[dict[str, Any]]:
        if not puede_crear(actor):
            raise PermisoDenegado("Solo el administrador ve el inventario.")
        parque_id = self._resolver_parque(parque_codigo) if parque_codigo else None
        return self._inventario.list_elementos(parque_id=parque_id, limite=limite)

    def _resolver_parque(self, codigo: str) -> ObjectId:
        parque_id = self._parques.get_parque_id(codigo.strip())
        if parque_id is None:
            raise ErrorMantenimiento(f"No existe el parque '{codigo}'.")
        return parque_id

    def _validar_operador(self, responsable_id: str) -> dict[str, Any]:
        perfil = self._perfiles.get_by_id(_oid(responsable_id))
        if perfil is None or perfil.get("rol") != RolDominio.OPERADOR_MANTENIMIENTO.value:
            raise ErrorMantenimiento("El responsable no es un operador de mantenimiento.")
        return perfil

    def _validar_elemento(
        self,
        elemento_id: str | None,
        parque_id: ObjectId,
    ) -> ObjectId | None:
        if not elemento_id:
            return None
        elemento = self._inventario.get_elemento(_oid(elemento_id))
        if elemento is None:
            raise ErrorMantenimiento("El elemento de inventario no existe.")
        if str(elemento.get("parque_id")) != str(parque_id):
            raise ErrorMantenimiento("El elemento no pertenece al parque.")
        return ObjectId(elemento_id)

    def _validar_incidente(
        self,
        incidente_id: str | None,
        parque_id: ObjectId,
    ) -> ObjectId | None:
        if not incidente_id:
            return None
        incidente = self._incidentes.get_incidente(_oid(incidente_id))
        if incidente is None:
            raise ErrorMantenimiento("El incidente no existe.")
        if str(incidente.get("parque_id")) != str(parque_id):
            raise ErrorMantenimiento("El incidente no pertenece al parque.")
        if incidente.get("estado") == EstadoIncidente.RESUELTO.value:
            raise ErrorMantenimiento("No se puede vincular un incidente resuelto.")
        return ObjectId(incidente_id)
