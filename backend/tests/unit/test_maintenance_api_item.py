"""Compatibilidad del listado con documentos anteriores a la feature 011."""
from datetime import UTC, datetime

from app.api.maintenance import _item


def test_item_sin_prioridad_usa_media():
    doc = {
        "_id": "legacy-1",
        "tipo": "correctivo",
        "descripcion": "Tarea anterior a la feature 011.",
        "estado": "pendiente",
    }

    item = _item(doc, datetime.now(UTC))

    assert item.prioridad == "media"
    assert item.estado == "pendiente"
