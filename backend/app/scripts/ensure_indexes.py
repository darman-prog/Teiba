"""Crea los índices operativos de usuarios, mantenimientos, incidentes e inventario.

Es idempotente: `create_index` no duplica índices existentes. Se ejecuta a mano
o desde el seed de datos demo; la API no crea índices en cada request.
"""
import sys

from pymongo.errors import DuplicateKeyError

from app.db import close_client, get_db
from app.infrastructure.mongo_repositories import (
    MongoIncidentRepository,
    MongoInventoryRepository,
    MongoMaintenanceRepository,
)


def main() -> int:
    db = get_db()
    try:
        # El correo es la llave del perfil y del registro: no puede duplicarse.
        db.usuarios.create_index("correo", unique=True)
    except DuplicateKeyError:
        print("ERROR: hay correos duplicados en usuarios; limpialos antes del índice.")
        close_client()
        return 1
    MongoMaintenanceRepository(db).ensure_indexes()
    MongoIncidentRepository(db).ensure_indexes()
    MongoInventoryRepository(db).ensure_indexes()
    print(
        "Índices asegurados: "
        f"{len(db.usuarios.index_information())} usuarios, "
        f"{len(db.mantenimientos.index_information())} mantenimientos, "
        f"{len(db.incidentes.index_information())} incidentes, "
        f"{len(db.elementos_inventario.index_information())} elementos."
    )
    close_client()
    return 0


if __name__ == "__main__":
    sys.exit(main())
