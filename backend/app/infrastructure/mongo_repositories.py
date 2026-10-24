"""Repositorios MongoDB con las consultas del agente.

`ModeloDatos.md` §3.1/§3.3 es el contrato: `dispositivos` referencia
`sectores` y `parques`; no existen nombres desnormalizados en el dispositivo.
"""
import re
from datetime import datetime
from typing import Any

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
