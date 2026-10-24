"""Genera lecturas frescas para la demo sin tocar los datos de la entrega.

Idempotente: borra solo los documentos con `meta.origen="demo"` y vuelve a
insertar. No modifica `01_crear_objetos.js` ni `02_cargar_datos.js`.
"""
import os
import sys
from datetime import UTC, datetime, timedelta

from pymongo.errors import PyMongoError

from app.db import get_db

ORIGEN_DEMO = "demo"
LECTURAS_POR_SENSOR = 49  # 12 h cada 15 min


def _ahora() -> datetime:
    raw = os.getenv("DEMO_NOW")
    if raw:
        valor = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if valor.tzinfo is None:
            valor = valor.replace(tzinfo=UTC)
        return valor.astimezone(UTC)
    return datetime.now(UTC)


def _lecturas(
    sensor_id: str,
    indice: int,
    ahora: datetime,
    primer_offset_min: int = 0,
    ph_ultima: float | None = None,
    bateria_baja: int | None = None,
) -> list[dict]:
    docs = []
    for i in range(LECTURAS_POR_SENSOR):
        minutos_atras = primer_offset_min + i * 15
        if minutos_atras > 12 * 60:
            break
        timestamp = ahora - timedelta(minutes=minutos_atras)
        humedad = 38.0 + indice * 2.0 + (i % 5) * 0.6
        ph = 6.4 + (indice % 3) * 0.1 - (i % 4) * 0.02
        temperatura = 19.0 + indice * 0.7 + (i % 6) * 0.3
        bateria = 95 - indice * 3 - (i // 12)
        if i == 0 and ph_ultima is not None:
            ph = ph_ultima
        if bateria_baja is not None and i < 4:
            bateria = bateria_baja
        docs.append(
            {
                "timestamp": timestamp,
                "meta": {
                    "sensor_id": sensor_id,
                    "tipo": "calidad_suelo",
                    "origen": ORIGEN_DEMO,
                },
                "humedad": float(round(humedad, 1)),
                "ph": float(round(ph, 2)),
                "temperatura": float(round(temperatura, 1)),
                "bateria": int(bateria),
            }
        )
    return docs


def main() -> int:
    db = get_db()
    sensores = list(
        db.dispositivos.find({"tipo": "calidad_suelo"}, {"_id": 1}).sort("_id", 1)
    )
    if not sensores:
        print(
            "ERROR: no hay sensores de calidad_suelo. "
            "Ejecuta 01_crear_objetos.js y 02_cargar_datos.js primero."
        )
        return 1

    ahora = _ahora()
    documentos: list[dict] = []
    resumen: dict[str, int] = {}
    for indice, sensor in enumerate(sensores):
        sensor_id = sensor["_id"]
        if sensor_id == "SS-01":
            docs = _lecturas(sensor_id, indice, ahora, ph_ultima=5.4)
        elif sensor_id == "SS-02":
            # Última lectura hace 7 h: dispara `sin_reportar` en la demo.
            docs = _lecturas(sensor_id, indice, ahora, primer_offset_min=7 * 60)
        elif sensor_id == "SS-03":
            docs = _lecturas(sensor_id, indice, ahora, bateria_baja=15)
        else:
            docs = _lecturas(sensor_id, indice, ahora)
        documentos.extend(docs)
        resumen[sensor_id] = len(docs)

    try:
        borrados = db.lecturas.delete_many({"meta.origen": ORIGEN_DEMO}).deleted_count
        db.lecturas.insert_many(documentos, ordered=False)
    except PyMongoError as exc:
        print(f"ERROR: no se pudo escribir en MongoDB: {exc}")
        return 1

    print(f"Lecturas demo borradas: {borrados}")
    print(f"Lecturas demo insertadas: {len(documentos)}")
    for sensor_id, cantidad in resumen.items():
        print(f"  {sensor_id}: {cantidad}")
    print("Anomalías: SS-01 pH 5.4; SS-02 última hace 7 h; SS-03 batería 15 %.")
    print(f"Referencia temporal: {ahora.isoformat().replace('+00:00', 'Z')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
