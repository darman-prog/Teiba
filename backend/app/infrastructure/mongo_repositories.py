"""Repositorios MongoDB con las consultas del agente.

`ModeloDatos.md` §3.1/§3.3 es el contrato: `dispositivos` referencia
`sectores` y `parques`; no existen nombres desnormalizados en el dispositivo.
"""
import re
from datetime import datetime
from typing import Any

from bson import ObjectId
from pymongo.database import Database

DEVICE_PROJECTION = {
    "_id": 1,
    "tipo": 1,
    "marca": 1,
    "fecha_instalacion": 1,
    "sector_id": 1,
    "parque_id": 1,
    "depende_de": 1,
    "alimentado_por": 1,
    "sector": "$_sector.nombre",
    "sector_codigo": "$_sector.codigo",
    "parque": "$_parque.nombre",
    "comuna": "$_parque.ubicacion.comuna",
}


def _oid(value: Any) -> ObjectId:
    """Normaliza un id de ruta/body a ObjectId; rechaza texto inválido."""
    if isinstance(value, ObjectId):
        return value
    if not isinstance(value, str) or not ObjectId.is_valid(value):
        raise ValueError("Identificador inválido.")
    return ObjectId(value)


class MongoDeviceRepository:
    """Lectura de dispositivos, sectores y parques."""

    def __init__(self, db: Database):
        self._db = db

    def resolve_sector(self, nombre: str) -> list[dict[str, Any]]:
        """Resuelve por nombre (prefijo, sin distinguir mayúsculas) o código."""
        valor = nombre.strip()
        if not valor:
            return []
        # Prefijo escapado: "Sector Norte" resuelve el nombre completo del sector.
        patron = {"$regex": f"^{re.escape(valor)}", "$options": "i"}
        cursor = (
            self._db.sectores.find(
                {"$or": [{"nombre": patron}, {"codigo": valor.upper()}]},
                {"_id": 1, "codigo": 1, "nombre": 1, "parque_id": 1},
            )
            .sort("codigo", 1)
            .limit(6)
        )
        # El id viaja como ObjectId para encadenar consultas sin reconvertir.
        return [
            {
                "id": doc["_id"],
                "codigo": doc.get("codigo"),
                "nombre": doc.get("nombre"),
                "parque_id": doc.get("parque_id"),
            }
            for doc in cursor
        ]

    def resolve_parque(self, nombre: str) -> list[dict[str, Any]]:
        """Resuelve por nombre (prefijo) o código."""
        valor = nombre.strip()
        if not valor:
            return []
        patron = {"$regex": f"^{re.escape(valor)}", "$options": "i"}
        cursor = (
            self._db.parques.find(
                {"$or": [{"nombre": patron}, {"codigo": valor.upper()}]},
                {"_id": 1, "codigo": 1, "nombre": 1},
            )
            .sort("codigo", 1)
            .limit(6)
        )
        return [
            {
                "id": doc["_id"],
                "codigo": doc.get("codigo"),
                "nombre": doc.get("nombre"),
            }
            for doc in cursor
        ]

    def find_devices(
        self,
        *,
        device_id: str | None = None,
        tipo: str | None = None,
        sector_ids: list[Any] | None = None,
        parque_ids: list[Any] | None = None,
        depende_de: str | None = None,
        limite: int = 20,
    ) -> list[dict[str, Any]]:
        """Devuelve dispositivos enriquecidos con sector, parque y comuna."""
        filtro: dict[str, Any] = {}
        if device_id:
            filtro["_id"] = device_id
        if tipo:
            filtro["tipo"] = tipo
        if sector_ids is not None:
            filtro["sector_id"] = {"$in": sector_ids}
        if parque_ids is not None:
            filtro["parque_id"] = {"$in": parque_ids}
        if depende_de is not None:
            filtro["depende_de"] = depende_de

        # El $lookup trae los nombres que el modelo necesita sin desnormalizar.
        pipeline = [
            {"$match": filtro},
            {"$sort": {"_id": 1}},
            {"$limit": max(1, min(limite, 50))},
            {
                "$lookup": {
                    "from": "sectores",
                    "localField": "sector_id",
                    "foreignField": "_id",
                    "as": "_sector",
                }
            },
            {"$unwind": {"path": "$_sector", "preserveNullAndEmptyArrays": True}},
            {
                "$lookup": {
                    "from": "parques",
                    "localField": "parque_id",
                    "foreignField": "_id",
                    "as": "_parque",
                }
            },
            {"$unwind": {"path": "$_parque", "preserveNullAndEmptyArrays": True}},
            {"$project": DEVICE_PROJECTION},
        ]
        return list(self._db.dispositivos.aggregate(pipeline))

    def get_device(self, device_id: str) -> dict[str, Any] | None:
        docs = self.find_devices(device_id=device_id, limite=1)
        return docs[0] if docs else None

    def children_of(self, antena: str) -> list[dict[str, Any]]:
        return self.find_devices(depende_de=antena, limite=50)

    def count_children(self, antena: str) -> int:
        return self._db.dispositivos.count_documents({"depende_de": antena})


class MongoParkRepository:
    """Lectura de parques con sus sectores para el libro de parques."""

    def __init__(self, db: Database):
        self._db = db

    def list_parques(self) -> list[dict[str, Any]]:
        # Un solo aggregate: evita el N+1 de contar sectores por parque.
        pipeline = [
            {"$sort": {"codigo": 1}},
            {
                "$lookup": {
                    "from": "sectores",
                    "localField": "_id",
                    "foreignField": "parque_id",
                    "as": "_sectores",
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "codigo": 1,
                    "nombre": 1,
                    "direccion": "$ubicacion.direccion",
                    "comuna": "$ubicacion.comuna",
                    "area_m2": 1,
                    "tipo_parque": 1,
                    "estado_general": 1,
                    "total_sectores": {"$size": "$_sectores"},
                }
            },
        ]
        return list(self._db.parques.aggregate(pipeline))

    def get_parque(self, codigo: str) -> dict[str, Any] | None:
        parque = self._db.parques.find_one({"codigo": codigo})
        if parque is None:
            return None
        sectores = list(
            self._db.sectores.find(
                {"parque_id": parque["_id"]},
                {"_id": 0, "codigo": 1, "nombre": 1, "tipo_suelo": 1, "zona_riesgo": 1},
            ).sort("codigo", 1)
        )
        parque.pop("_id", None)
        return {**parque, "sectores": sectores}

    def get_parque_id(self, codigo: str) -> Any | None:
        """Resuelve el código legible al ObjectId que guarda `mantenimientos`."""
        doc = self._db.parques.find_one({"codigo": codigo}, {"_id": 1})
        return doc["_id"] if doc else None


class MongoProfileRepository:
    """Perfiles de negocio; el correo es el puente con la sesión de auth."""

    PROJECTION = {"_id": 1, "nombre": 1, "correo": 1, "rol": 1}

    def __init__(self, db: Database):
        self._db = db

    def get_by_correo(self, correo: str) -> dict[str, Any] | None:
        limpio = (correo or "").strip().lower()
        if not limpio:
            return None
        return self._db.usuarios.find_one({"correo": limpio}, self.PROJECTION)

    def get_by_id(self, perfil_id: Any) -> dict[str, Any] | None:
        return self._db.usuarios.find_one({"_id": _oid(perfil_id)}, self.PROJECTION)

    def list_operadores(self) -> list[dict[str, Any]]:
        return list(
            self._db.usuarios.find(
                {"rol": "operador_mantenimiento"},
                self.PROJECTION,
            ).sort("nombre", 1)
        )


class MongoMaintenanceRepository:
    """Tareas de mantenimiento con sus referencias resueltas."""

    def __init__(self, db: Database):
        self._db = db

    def list_tareas(
        self,
        *,
        tarea_id: Any | None = None,
        estado: str | None = None,
        prioridad: str | None = None,
        parque_id: Any | None = None,
        responsable_id: Any | None = None,
        incidente_id: Any | None = None,
        limite: int = 50,
    ) -> list[dict[str, Any]]:
        filtro: dict[str, Any] = {}
        if tarea_id is not None:
            filtro["_id"] = _oid(tarea_id)
        if estado:
            filtro["estado"] = estado
        if prioridad:
            filtro["prioridad"] = prioridad
        if parque_id is not None:
            filtro["parque_id"] = _oid(parque_id)
        if responsable_id is not None:
            filtro["responsable_id"] = _oid(responsable_id)
        if incidente_id is not None:
            filtro["incidente_id"] = _oid(incidente_id)

        pipeline = [
            {"$match": filtro},
            {
                "$addFields": {
                    "_prioridad_orden": {
                        "$switch": {
                            "branches": [
                                {"case": {"$eq": ["$prioridad", "alta"]}, "then": 0},
                                {"case": {"$eq": ["$prioridad", "baja"]}, "then": 2},
                            ],
                            "default": 1,
                        }
                    }
                }
            },
            {"$sort": {"_prioridad_orden": 1, "fecha_programada": 1, "_id": 1}},
            {"$limit": max(1, min(limite, 50))},
            {
                "$lookup": {
                    "from": "parques",
                    "localField": "parque_id",
                    "foreignField": "_id",
                    "as": "_parque",
                }
            },
            {"$set": {"_parque": {"$arrayElemAt": ["$_parque", 0]}}},
            {
                "$lookup": {
                    "from": "usuarios",
                    "localField": "responsable_id",
                    "foreignField": "_id",
                    "as": "_responsable",
                }
            },
            {"$set": {"_responsable": {"$arrayElemAt": ["$_responsable", 0]}}},
            {
                "$lookup": {
                    "from": "incidentes",
                    "localField": "incidente_id",
                    "foreignField": "_id",
                    "as": "_incidente",
                }
            },
            {"$set": {"_incidente": {"$arrayElemAt": ["$_incidente", 0]}}},
            {
                "$lookup": {
                    "from": "elementos_inventario",
                    "localField": "elemento_id",
                    "foreignField": "_id",
                    "as": "_elemento",
                }
            },
            {"$set": {"_elemento": {"$arrayElemAt": ["$_elemento", 0]}}},
            {
                "$project": {
                    "_id": 1,
                    "tipo": 1,
                    "descripcion": 1,
                    "prioridad": 1,
                    "estado": 1,
                    "fecha_programada": 1,
                    "fecha_ejecucion": 1,
                    "fecha_reapertura": 1,
                    "nota_cierre": 1,
                    "nota_reapertura": 1,
                    "costo_estimado": 1,
                    "parque_id": 1,
                    "responsable_id": 1,
                    "incidente_id": 1,
                    "elemento_id": 1,
                    "parque": {
                        "$cond": [
                            {"$eq": ["$_parque", None]},
                            None,
                            {
                                "id": "$_parque._id",
                                "codigo": "$_parque.codigo",
                                "nombre": "$_parque.nombre",
                            },
                        ]
                    },
                    "responsable": {
                        "$cond": [
                            {"$eq": ["$_responsable", None]},
                            None,
                            {
                                "id": "$_responsable._id",
                                "nombre": "$_responsable.nombre",
                                "rol": "$_responsable.rol",
                            },
                        ]
                    },
                    "incidente": {
                        "$cond": [
                            {"$eq": ["$_incidente", None]},
                            None,
                            {
                                "id": "$_incidente._id",
                                "tipo": "$_incidente.tipo",
                                "descripcion": "$_incidente.descripcion",
                                "prioridad": "$_incidente.prioridad",
                                "estado": "$_incidente.estado",
                            },
                        ]
                    },
                    "elemento": {
                        "$cond": [
                            {"$eq": ["$_elemento", None]},
                            None,
                            {
                                "id": "$_elemento._id",
                                "tipo_elemento": "$_elemento.tipo_elemento",
                                "cantidad": "$_elemento.cantidad",
                                "estado": "$_elemento.estado",
                            },
                        ]
                    },
                }
            },
        ]
        return list(self._db.mantenimientos.aggregate(pipeline))

    def get_tarea(self, tarea_id: Any) -> dict[str, Any] | None:
        docs = self.list_tareas(tarea_id=tarea_id, limite=1)
        return docs[0] if docs else None

    def create_tarea(self, doc: dict[str, Any]) -> Any:
        return self._db.mantenimientos.insert_one(doc).inserted_id

    def update_estado(
        self,
        tarea_id: Any,
        *,
        estado: str,
        campo_nota: str | None,
        nota: str | None,
        limpia_ejecucion: bool,
        marca_reapertura: bool,
        ahora: datetime,
    ) -> dict[str, Any] | None:
        cambios: dict[str, Any] = {"estado": estado}
        if campo_nota and nota is not None:
            cambios[campo_nota] = nota
        if estado == "finalizado" and not limpia_ejecucion:
            cambios["fecha_ejecucion"] = ahora
        if limpia_ejecucion:
            # Se deja el campo en null para que el DTO mantenga una forma estable.
            cambios["fecha_ejecucion"] = None
        if marca_reapertura:
            cambios["fecha_reapertura"] = ahora

        update: dict[str, Any] = {"$set": cambios}
        resultado = self._db.mantenimientos.update_one({"_id": _oid(tarea_id)}, update)
        if resultado.matched_count == 0:
            return None
        return self.get_tarea(tarea_id)

    def reasignar(self, tarea_id: Any, responsable_id: Any) -> dict[str, Any] | None:
        resultado = self._db.mantenimientos.update_one(
            {"_id": _oid(tarea_id)},
            {"$set": {"responsable_id": _oid(responsable_id)}},
        )
        if resultado.matched_count == 0:
            return None
        return self.get_tarea(tarea_id)

    def ensure_indexes(self) -> None:
        self._db.mantenimientos.create_index(
            [("responsable_id", 1), ("estado", 1), ("fecha_programada", 1)]
        )
        self._db.mantenimientos.create_index(
            [("estado", 1), ("prioridad", -1), ("fecha_programada", 1)]
        )
        self._db.mantenimientos.create_index([("incidente_id", 1)])
        self._db.mantenimientos.create_index([("parque_id", 1)])


class MongoIncidentRepository:
    """Incidentes ciudadanos con parque y reportante resueltos."""

    def __init__(self, db: Database):
        self._db = db

    def list_incidentes(
        self,
        *,
        incidente_id: Any | None = None,
        parque_id: Any | None = None,
        estados: list[str] | None = None,
        limite: int = 50,
    ) -> list[dict[str, Any]]:
        filtro: dict[str, Any] = {}
        if incidente_id is not None:
            filtro["_id"] = _oid(incidente_id)
        if parque_id is not None:
            filtro["parque_id"] = _oid(parque_id)
        if estados:
            filtro["estado"] = {"$in": estados}

        pipeline = [
            {"$match": filtro},
            {"$sort": {"fecha_hora": -1, "_id": 1}},
            {"$limit": max(1, min(limite, 50))},
            {
                "$lookup": {
                    "from": "parques",
                    "localField": "parque_id",
                    "foreignField": "_id",
                    "as": "_parque",
                }
            },
            {"$set": {"_parque": {"$arrayElemAt": ["$_parque", 0]}}},
            {
                "$lookup": {
                    "from": "usuarios",
                    "localField": "reportado_por_id",
                    "foreignField": "_id",
                    "as": "_reportante",
                }
            },
            {"$set": {"_reportante": {"$arrayElemAt": ["$_reportante", 0]}}},
            {
                "$project": {
                    "_id": 1,
                    "tipo": 1,
                    "descripcion": 1,
                    "fecha_hora": 1,
                    "estado": 1,
                    "prioridad": 1,
                    "parque_id": 1,
                    "reportado_por_id": 1,
                    "parque": {
                        "$cond": [
                            {"$eq": ["$_parque", None]},
                            None,
                            {
                                "id": "$_parque._id",
                                "codigo": "$_parque.codigo",
                                "nombre": "$_parque.nombre",
                            },
                        ]
                    },
                    "reportado_por": {
                        "$cond": [
                            {"$eq": ["$_reportante", None]},
                            None,
                            {
                                "id": "$_reportante._id",
                                "nombre": "$_reportante.nombre",
                            },
                        ]
                    },
                }
            },
        ]
        return list(self._db.incidentes.aggregate(pipeline))

    def get_incidente(self, incidente_id: Any) -> dict[str, Any] | None:
        docs = self.list_incidentes(incidente_id=incidente_id, limite=1)
        return docs[0] if docs else None

    def update_estado(self, incidente_id: Any, estado: str) -> dict[str, Any] | None:
        resultado = self._db.incidentes.update_one(
            {"_id": _oid(incidente_id)},
            {"$set": {"estado": estado}},
        )
        if resultado.matched_count == 0:
            return None
        return self.get_incidente(incidente_id)

    def ensure_indexes(self) -> None:
        self._db.incidentes.create_index([("parque_id", 1), ("estado", 1)])
        self._db.incidentes.create_index([("fecha_hora", -1)])


class MongoInventoryRepository:
    """Elementos de inventario por parque para vincular tareas."""

    def __init__(self, db: Database):
        self._db = db

    def list_elementos(
        self,
        *,
        parque_id: Any | None = None,
        elemento_id: Any | None = None,
        limite: int = 50,
    ) -> list[dict[str, Any]]:
        filtro: dict[str, Any] = {}
        if parque_id is not None:
            filtro["parque_id"] = _oid(parque_id)
        if elemento_id is not None:
            filtro["_id"] = _oid(elemento_id)

        pipeline = [
            {"$match": filtro},
            {"$sort": {"tipo_elemento": 1, "_id": 1}},
            {"$limit": max(1, min(limite, 50))},
            {
                "$lookup": {
                    "from": "sectores",
                    "localField": "sector_id",
                    "foreignField": "_id",
                    "as": "_sector",
                }
            },
            {"$set": {"_sector": {"$arrayElemAt": ["$_sector", 0]}}},
            {
                "$project": {
                    "_id": 1,
                    "parque_id": 1,
                    "sector_id": 1,
                    "tipo_elemento": 1,
                    "cantidad": 1,
                    "estado": 1,
                    "sector": {
                        "$cond": [
                            {"$eq": ["$_sector", None]},
                            None,
                            {
                                "id": "$_sector._id",
                                "codigo": "$_sector.codigo",
                                "nombre": "$_sector.nombre",
                            },
                        ]
                    },
                }
            },
        ]
        return list(self._db.elementos_inventario.aggregate(pipeline))

    def get_elemento(self, elemento_id: Any) -> dict[str, Any] | None:
        docs = self.list_elementos(elemento_id=elemento_id, limite=1)
        return docs[0] if docs else None

    def ensure_indexes(self) -> None:
        self._db.elementos_inventario.create_index(
            [("parque_id", 1), ("tipo_elemento", 1)]
        )


class MongoReadingRepository:
    """Lectura de la colección time-series `lecturas`."""

    def __init__(self, db: Database):
        self._db = db

    def history(
        self,
        sensor_id: str,
        since: datetime,
        limite: int = 20,
    ) -> list[dict[str, Any]]:
        cursor = (
            self._db.lecturas.find(
                {
                    "meta.sensor_id": sensor_id,
                    "timestamp": {"$gte": since},
                },
                {"_id": 0},
            )
            .sort("timestamp", -1)
            .limit(max(1, min(limite, 50)))
        )
        return list(cursor)

    def latest(self, sensor_id: str) -> dict[str, Any] | None:
        return self._db.lecturas.find_one(
            {"meta.sensor_id": sensor_id},
            {"_id": 0},
            sort=[("timestamp", -1)],
        )

    def latest_many(self, sensor_ids: list[str]) -> dict[str, dict[str, Any]]:
        if not sensor_ids:
            return {}
        # Agrupa la última lectura por sensor usando el índice existente.
        pipeline = [
            {"$match": {"meta.sensor_id": {"$in": sensor_ids}}},
            {"$sort": {"timestamp": -1}},
            {
                "$group": {
                    "_id": "$meta.sensor_id",
                    "doc": {"$first": "$$ROOT"},
                }
            },
        ]
        return {
            row["_id"]: row["doc"]
            for row in self._db.lecturas.aggregate(pipeline)
        }
