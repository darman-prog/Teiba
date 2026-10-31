"""Repositorios de mantenimientos, perfiles, incidentes e inventario."""
from datetime import timedelta

from app.infrastructure.mongo_repositories import (
    MongoIncidentRepository,
    MongoInventoryRepository,
    MongoMaintenanceRepository,
    MongoProfileRepository,
)
from tests.integration.fixtures import (
    ELEMENTO_BANCA_ID,
    ELEMENTO_JUEGO_ID,
    FIXTURE_NOW,
    INCIDENTE_ID,
    MANTENIMIENTO_FINALIZADO_ID,
    MANTENIMIENTO_PENDIENTE_ID,
    MANTENIMIENTO_PROCESO_ID,
    PARQUE_ID,
    USUARIO_ADMIN_ID,
    USUARIO_CIUDADANO_ID,
    USUARIO_OPERADOR_ID,
    USUARIO_OTRO_ID,
)


def test_perfiles_por_correo_y_operadores(mongo_db):
    repo = MongoProfileRepository(mongo_db)

    operador = repo.get_by_correo("operador@teiba.local")
    assert operador is not None
    assert operador["_id"] == USUARIO_OPERADOR_ID
    assert operador["rol"] == "operador_mantenimiento"
    assert repo.get_by_correo("nadie@teiba.local") is None

    operadores = repo.list_operadores()
    assert [item["_id"] for item in operadores] == [USUARIO_OTRO_ID, USUARIO_OPERADOR_ID]
    assert all(item["rol"] == "operador_mantenimiento" for item in operadores)

    admin = repo.get_by_id(USUARIO_ADMIN_ID)
    assert admin is not None
    assert admin["nombre"] == "Ana Administradora"


def test_lista_tareas_ordena_y_resuelve_referencias(mongo_db):
    repo = MongoMaintenanceRepository(mongo_db)

    tareas = repo.list_tareas()
    assert [tarea["_id"] for tarea in tareas] == [
        MANTENIMIENTO_PENDIENTE_ID,
        MANTENIMIENTO_PROCESO_ID,
        MANTENIMIENTO_FINALIZADO_ID,
    ]
    primera = tareas[0]
    assert primera["parque"]["nombre"] == "Parque San Pío"
    assert primera["responsable"]["nombre"] == "Óscar Operador"
    assert primera["incidente"]["tipo"] == "infraestructura"
    assert primera["elemento"]["tipo_elemento"] == "juego_infantil"

    propias = repo.list_tareas(responsable_id=str(USUARIO_OPERADOR_ID))
    assert {tarea["_id"] for tarea in propias} == {
        MANTENIMIENTO_PENDIENTE_ID,
        MANTENIMIENTO_PROCESO_ID,
    }
    assert repo.list_tareas(estado="pendiente")[0]["_id"] == MANTENIMIENTO_PENDIENTE_ID
    assert repo.list_tareas(prioridad="baja")[0]["_id"] == MANTENIMIENTO_FINALIZADO_ID
    assert len(repo.list_tareas(limite=1)) == 1
    assert repo.get_tarea(str(MANTENIMIENTO_PENDIENTE_ID))["prioridad"] == "alta"
    assert repo.get_tarea("671153000000000000000099") is None


def test_crear_y_reasignar_tarea(mongo_db):
    repo = MongoMaintenanceRepository(mongo_db)
    nuevo_id = repo.create_tarea(
        {
            "tipo": "preventivo",
            "descripcion": "Lubricar bisagras del portón.",
            "fecha_programada": FIXTURE_NOW + timedelta(days=3),
            "fecha_ejecucion": None,
            "estado": "pendiente",
            "prioridad": "media",
            "nota_cierre": None,
            "nota_reapertura": None,
            "fecha_reapertura": None,
            "incidente_id": None,
            "parque_id": PARQUE_ID,
            "elemento_id": None,
            "responsable_id": USUARIO_OPERADOR_ID,
            "costo_estimado": 25000.0,
        }
    )

    creada = repo.get_tarea(nuevo_id)
    assert creada is not None
    assert creada["descripcion"] == "Lubricar bisagras del portón."
    assert creada["responsable"]["nombre"] == "Óscar Operador"

    reasignada = repo.reasignar(nuevo_id, str(USUARIO_OTRO_ID))
    assert reasignada is not None
    assert reasignada["responsable"]["nombre"] == "Olga Operadora"
    assert repo.reasignar("671153000000000000000099", USUARIO_OTRO_ID) is None


def test_update_estado_finaliza_y_reabre(mongo_db):
    repo = MongoMaintenanceRepository(mongo_db)

    en_proceso = repo.update_estado(
        MANTENIMIENTO_PENDIENTE_ID,
        estado="en_proceso",
        campo_nota=None,
        nota=None,
        limpia_ejecucion=False,
        marca_reapertura=False,
        ahora=FIXTURE_NOW,
    )
    assert en_proceso is not None
    assert en_proceso["estado"] == "en_proceso"
    assert en_proceso["fecha_ejecucion"] is None

    finalizada = repo.update_estado(
        MANTENIMIENTO_PENDIENTE_ID,
        estado="finalizado",
        campo_nota="nota_cierre",
        nota="Tornillo ajustado.",
        limpia_ejecucion=False,
        marca_reapertura=False,
        ahora=FIXTURE_NOW,
    )
    assert finalizada is not None
    assert finalizada["estado"] == "finalizado"
    assert finalizada["fecha_ejecucion"] == FIXTURE_NOW
    assert finalizada["nota_cierre"] == "Tornillo ajustado."

    reabierta = repo.update_estado(
        MANTENIMIENTO_PENDIENTE_ID,
        estado="en_proceso",
        campo_nota="nota_reapertura",
        nota="El ajuste no quedó.",
        limpia_ejecucion=True,
        marca_reapertura=True,
        ahora=FIXTURE_NOW + timedelta(hours=1),
    )
    assert reabierta is not None
    assert reabierta["estado"] == "en_proceso"
    assert reabierta["fecha_ejecucion"] is None
    assert reabierta["fecha_reapertura"] == FIXTURE_NOW + timedelta(hours=1)
    assert reabierta["nota_reapertura"] == "El ajuste no quedó."

    inexistente = repo.update_estado(
        "671153000000000000000099",
        estado="finalizado",
        campo_nota="nota_cierre",
        nota="x",
        limpia_ejecucion=False,
        marca_reapertura=False,
        ahora=FIXTURE_NOW,
    )
    assert inexistente is None


def test_incidentes_lista_y_cambio_de_estado(mongo_db):
    repo = MongoIncidentRepository(mongo_db)

    incidentes = repo.list_incidentes(parque_id=str(PARQUE_ID))
    assert len(incidentes) == 1
    assert incidentes[0]["parque"]["nombre"] == "Parque San Pío"
    assert incidentes[0]["reportado_por"]["nombre"] == "Carla Ciudadana"

    actualizado = repo.update_estado(INCIDENTE_ID, "en_revision")
    assert actualizado is not None
    assert actualizado["estado"] == "en_revision"
    assert repo.list_incidentes(estados=["en_revision"])[0]["_id"] == INCIDENTE_ID
    assert repo.get_incidente("671155000000000000000099") is None


def test_elementos_por_parque(mongo_db):
    repo = MongoInventoryRepository(mongo_db)

    elementos = repo.list_elementos(parque_id=str(PARQUE_ID))
    assert {elemento["_id"] for elemento in elementos} == {
        ELEMENTO_BANCA_ID,
        ELEMENTO_JUEGO_ID,
    }
    assert elementos[0]["sector"]["nombre"].startswith("Sector")
    assert repo.get_elemento(ELEMENTO_JUEGO_ID)["estado"] == "danado"


def test_indices_operativos(mongo_db):
    MongoMaintenanceRepository(mongo_db).ensure_indexes()
    MongoIncidentRepository(mongo_db).ensure_indexes()
    MongoInventoryRepository(mongo_db).ensure_indexes()

    mantenimientos = mongo_db.mantenimientos.index_information()
    assert "responsable_id_1_estado_1_fecha_programada_1" in mantenimientos
    assert "estado_1_prioridad_-1_fecha_programada_1" in mantenimientos
    assert "incidente_id_1" in mantenimientos
    assert "parque_id_1" in mantenimientos

    incidentes = mongo_db.incidentes.index_information()
    assert "parque_id_1_estado_1" in incidentes

    elementos = mongo_db.elementos_inventario.index_information()
    assert "parque_id_1_tipo_elemento_1" in elementos


def test_ciudadano_no_es_operador(mongo_db):
    repo = MongoProfileRepository(mongo_db)
    ciudadano = repo.get_by_correo("ciudadano@teiba.local")
    assert ciudadano is not None
    assert ciudadano["_id"] == USUARIO_CIUDADANO_ID
    assert ciudadano["rol"] == "ciudadano"
