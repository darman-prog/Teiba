"""Siembra perfiles, incidentes, elementos y tareas de mantenimiento demo.

Es idempotente: los perfiles se buscan por correo y los documentos demo usan
_ids fijos con `replace_one(..., upsert=True)`. No borra datos existentes.
"""
import sys
from datetime import UTC, datetime, timedelta

from bson import ObjectId
from pymongo.errors import PyMongoError

from app.db import close_client, get_db
from app.infrastructure.mongo_repositories import (
    MongoIncidentRepository,
    MongoInventoryRepository,
    MongoMaintenanceRepository,
)

AHORA = datetime.now(UTC)

PERFILES = [
    ("admin@teiba.local", "Ana Administradora", "administrador"),
    ("operador@teiba.local", "Óscar Operador", "operador_mantenimiento"),
    ("otro@teiba.local", "Olga Operadora", "operador_mantenimiento"),
    ("user@teiba.local", "Carla Ciudadana", "ciudadano"),
]

ELEMENTO_BANCA = ObjectId("671160000000000000000001")
ELEMENTO_JUEGO = ObjectId("671160000000000000000002")
INCIDENTE_JUEGO = ObjectId("671161000000000000000001")
INCIDENTE_BANCA = ObjectId("671161000000000000000002")
INCIDENTE_SENDERO = ObjectId("671161000000000000000003")

TAREAS = [
    (
        "671162000000000000000001", "pendiente", "alta", -1, None, None,
        INCIDENTE_JUEGO, ELEMENTO_JUEGO,
    ),
    ("671162000000000000000002", "pendiente", "media", 2, None, None, None, ELEMENTO_BANCA),
    ("671162000000000000000003", "pendiente", "baja", 5, None, None, None, None),
    (
        "671162000000000000000004", "en_proceso", "alta", -2, None, None,
        INCIDENTE_BANCA, ELEMENTO_BANCA,
    ),
    ("671162000000000000000005", "en_proceso", "media", 1, None, None, None, ELEMENTO_JUEGO),
    (
        "671162000000000000000006", "finalizado", "alta", -6, -5,
        "Tornillo cambiado y probado.", INCIDENTE_SENDERO, None,
    ),
    (
        "671162000000000000000007", "finalizado", "media", -8, -7,
        "Sendero limpio y señalizado.", None, None,
    ),
    (
        "671162000000000000000008", "finalizado", "baja", -10, -9,
        "Banca lijada y pintada.", None, ELEMENTO_BANCA,
    ),
]


def _perfil(db, correo: str, nombre: str, rol: str) -> ObjectId:
    existente = db.usuarios.find_one({"correo": correo}, {"_id": 1})
    if existente:
        db.usuarios.update_one(
            {"_id": existente["_id"]},
            {"$set": {"nombre": nombre, "rol": rol}},
        )
        return existente["_id"]
    creado = db.usuarios.insert_one(
        {
            "nombre": nombre,
            "correo": correo,
            "telefono": "",
            "rol": rol,
            "fecha_registro": AHORA,
        }
    )
    return creado.inserted_id


def main() -> int:
    db = get_db()
    parque = db.parques.find_one({}, sort=[("codigo", 1)])
    if parque is None:
        print("ERROR: no hay parques; ejecuta 01_crear_objetos.js y 02_cargar_datos.js.")
        return 1
    parque_id = parque["_id"]
    codigo = parque.get("codigo", "—")

    try:
        perfil_admin = _perfil(db, *PERFILES[0])
        perfil_operador = _perfil(db, *PERFILES[1])
        perfil_otro = _perfil(db, *PERFILES[2])
        perfil_ciudadano = _perfil(db, *PERFILES[3])

        for elemento_id, tipo, cantidad, estado in [
            (ELEMENTO_BANCA, "banca", 12, "bueno"),
            (ELEMENTO_JUEGO, "juego_infantil", 3, "danado"),
        ]:
            db.elementos_inventario.replace_one(
                {"_id": elemento_id},
                {
                    "_id": elemento_id,
                    "parque_id": parque_id,
                    "sector_id": None,
                    "tipo_elemento": tipo,
                    "cantidad": cantidad,
                    "estado": estado,
                },
                upsert=True,
            )

        for incidente_id, tipo, descripcion, estado, prioridad, horas in [
            (
                INCIDENTE_JUEGO,
                "infraestructura",
                "Juego infantil con tornillo suelto.",
                "reportado",
                "alta",
                4,
            ),
            (
                INCIDENTE_BANCA,
                "infraestructura",
                "Banca con tablón astillado.",
                "en_revision",
                "media",
                20,
            ),
            (
                INCIDENTE_SENDERO,
                "limpieza",
                "Sendero con residuos acumulados.",
                "en_proceso",
                "baja",
                30,
            ),
        ]:
            db.incidentes.replace_one(
                {"_id": incidente_id},
                {
                    "_id": incidente_id,
                    "tipo": tipo,
                    "descripcion": descripcion,
                    "fecha_hora": AHORA - timedelta(hours=horas),
                    "parque_id": parque_id,
                    "reportado_por_id": perfil_ciudadano,
                    "estado": estado,
                    "prioridad": prioridad,
                    "evidencias": [],
                },
                upsert=True,
            )

        operadores = [perfil_operador, perfil_otro]
        for index, (
            tarea_id,
            estado,
            prioridad,
            dias,
            ejecucion,
            nota,
            incidente_id,
            elemento_id,
        ) in enumerate(TAREAS):
            fecha = AHORA + timedelta(days=dias)
            db.mantenimientos.replace_one(
                {"_id": ObjectId(tarea_id)},
                {
                    "_id": ObjectId(tarea_id),
                    "tipo": "correctivo" if index % 2 == 0 else "preventivo",
                    "descripcion": f"Tarea demo {index + 1}: revisar {codigo}.",
                    "fecha_programada": fecha,
                    "fecha_ejecucion": AHORA + timedelta(days=ejecucion) if ejecucion else None,
                    "estado": estado,
                    "prioridad": prioridad,
                    "nota_cierre": nota,
                    "nota_reapertura": None,
                    "fecha_reapertura": None,
                    "incidente_id": incidente_id,
                    "parque_id": parque_id,
                    "elemento_id": elemento_id,
                    "responsable_id": operadores[index % 2],
                    "costo_estimado": 50000.0 + index * 15000,
                },
                upsert=True,
            )

        MongoMaintenanceRepository(db).ensure_indexes()
        MongoIncidentRepository(db).ensure_indexes()
        MongoInventoryRepository(db).ensure_indexes()
    except PyMongoError as exc:
        print(f"ERROR: no se pudo sembrar mantenimientos: {type(exc).__name__}.")
        return 1
    finally:
        close_client()

    print(f"Demo sembrada en el parque {codigo}:")
    print(f"  - perfiles: {perfil_admin}, {perfil_operador}, {perfil_otro}, {perfil_ciudadano}")
    print(f"  - 3 incidentes, 2 elementos y {len(TAREAS)} tareas (idempotente).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
