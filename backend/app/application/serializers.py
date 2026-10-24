"""Serialización compartida de documentos BSON a JSON.

Convierte `Date` a ISO 8601 UTC y `ObjectId` a string; nunca expone BSON crudo.
"""
from datetime import UTC, datetime
from typing import Any

from bson import ObjectId


def iso(value: Any) -> Any:
    if isinstance(value, datetime):
        # Mongo puede devolver naive si el cliente no usa tz_aware; se asume UTC.
        if value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        return value.astimezone(UTC).isoformat().replace("+00:00", "Z")
    return value


def antiguedad_min(timestamp: datetime | None, ahora: datetime) -> int | None:
    if timestamp is None:
        return None
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=UTC)
    return max(0, int((ahora - timestamp).total_seconds() / 60))


def serialize_lectura(doc: dict, ahora: datetime) -> dict:
    return {
        "timestamp": iso(doc.get("timestamp")),
        "humedad": doc.get("humedad"),
        "ph": doc.get("ph"),
        "temperatura": doc.get("temperatura"),
        "bateria": doc.get("bateria"),
        "antiguedad_min": antiguedad_min(doc.get("timestamp"), ahora),
    }


def str_id(value: Any) -> Any:
    return str(value) if isinstance(value, ObjectId) else value


def serialize_device(doc: dict) -> dict:
    return {
        "id": doc.get("_id"),
        "tipo": doc.get("tipo"),
        "marca": doc.get("marca"),
        "fecha_instalacion": iso(doc.get("fecha_instalacion")),
        "sector": doc.get("sector"),
        "sector_id": str_id(doc.get("sector_id")),
        "sector_codigo": doc.get("sector_codigo"),
        "parque": doc.get("parque"),
        "parque_id": str_id(doc.get("parque_id")),
        "comuna": doc.get("comuna"),
        "depende_de": doc.get("depende_de"),
        "alimentado_por": doc.get("alimentado_por"),
    }
