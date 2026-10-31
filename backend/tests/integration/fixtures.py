"""Datos de prueba compartidos por los tests de integración."""
from datetime import UTC, datetime, timedelta

from bson import ObjectId

FIXTURE_NOW = datetime(2026, 10, 24, 12, 0, tzinfo=UTC)
PARQUE_ID = ObjectId("671150000000000000000001")
SECTOR_NORTE = ObjectId("671151000000000000000001")
SECTOR_BOSQUE = ObjectId("671151000000000000000004")

USUARIO_ADMIN_ID = ObjectId("671154000000000000000001")
USUARIO_OPERADOR_ID = ObjectId("671154000000000000000002")
USUARIO_OTRO_ID = ObjectId("671154000000000000000003")
USUARIO_CIUDADANO_ID = ObjectId("671154000000000000000004")
INCIDENTE_ID = ObjectId("671155000000000000000001")
ELEMENTO_BANCA_ID = ObjectId("671152000000000000000001")
ELEMENTO_JUEGO_ID = ObjectId("671152000000000000000002")
MANTENIMIENTO_PENDIENTE_ID = ObjectId("671153000000000000000001")
MANTENIMIENTO_PROCESO_ID = ObjectId("671153000000000000000002")
MANTENIMIENTO_FINALIZADO_ID = ObjectId("671153000000000000000003")


def _lectura(sensor_id: str, tipo: str, cuando: datetime, humedad: float, ph: float,
             temperatura: float, bateria: int) -> dict:
    return {
        "timestamp": cuando,
        "meta": {"sensor_id": sensor_id, "tipo": tipo},
        "humedad": humedad,
        "ph": ph,
        "temperatura": temperatura,
        "bateria": bateria,
    }


def seed_test_db(db) -> None:
    """Crea un conjunto mínimo y coherente con `ModeloDatos.md`."""
    db.parques.insert_one(
        {
            "_id": PARQUE_ID,
            "codigo": "PRQ-001",
            "nombre": "Parque San Pío",
            "ubicacion": {
                "direccion": "Carrera 33 con Calle 45",
                "comuna": "Comuna 12 - Cabecera del Llano",
                "coordenadas": {"type": "Point", "coordinates": [-73.1114, 7.1192]},
            },
            "area_m2": 15400.0,
            "tipo_parque": "recreativo",
            "estado_general": "bueno",
        }
    )
    db.sectores.insert_many(
        [
            {
                "_id": SECTOR_NORTE,
                "codigo": "SEC-001",
                "parque_id": PARQUE_ID,
                "nombre": "Sector Norte - Jardines de la Escultura de Botero",
                "tipo_suelo": "césped natural",
                "zona_riesgo": "baja",
            },
            {
                "_id": SECTOR_BOSQUE,
                "codigo": "SEC-004",
                "parque_id": PARQUE_ID,
                "nombre": "Sector Bosque - Zona Verde y Cancha Múltiple",
                "tipo_suelo": "tierra arcillosa y césped",
                "zona_riesgo": "baja",
            },
        ]
    )
    db.dispositivos.insert_many(
        [
            {
                "_id": "ANT-01",
                "tipo": "antena_enlace",
                "marca": "Ubiquiti NanoStation 5AC",
                "fecha_instalacion": FIXTURE_NOW - timedelta(days=250),
                "sector_id": SECTOR_NORTE,
                "parque_id": PARQUE_ID,
                "depende_de": None,
                "alimentado_por": "Red_Electrica_Poste_P12",
            },
            {
                "_id": "SS-01",
                "tipo": "calidad_suelo",
                "marca": "SoilPro-Sense LoRa",
                "fecha_instalacion": FIXTURE_NOW - timedelta(days=240),
                "sector_id": SECTOR_NORTE,
                "parque_id": PARQUE_ID,
                "depende_de": "ANT-01",
                "alimentado_por": "Panel_Solar_PS1",
            },
            {
                "_id": "SS-02",
                "tipo": "calidad_suelo",
                "marca": "SoilPro-Sense LoRa",
                "fecha_instalacion": FIXTURE_NOW - timedelta(days=240),
                "sector_id": SECTOR_BOSQUE,
                "parque_id": PARQUE_ID,
                "depende_de": "ANT-01",
                "alimentado_por": "Bateria_Litio_18650",
            },
            {
                "_id": "MET-01",
                "tipo": "estacion_meteorologica",
                "marca": "Davis Vantage Pro2 Plus",
                "fecha_instalacion": FIXTURE_NOW - timedelta(days=230),
                "sector_id": SECTOR_NORTE,
                "parque_id": PARQUE_ID,
                "depende_de": "ANT-01",
                "alimentado_por": "Panel_Solar_PS2",
            },
            {
                "_id": "LUM-01",
                "tipo": "luminaria_inteligente",
                "marca": "Philips DigiCity",
                "fecha_instalacion": FIXTURE_NOW - timedelta(days=200),
                "sector_id": SECTOR_BOSQUE,
                "parque_id": PARQUE_ID,
                "depende_de": None,
                "alimentado_por": "Red_Alumbrado_Publico",
            },
        ]
    )
    db.lecturas.insert_many(
        [
            _lectura(
                "SS-01", "calidad_suelo",
                FIXTURE_NOW - timedelta(minutes=30), 41.2, 6.8, 21.0, 90,
            ),
            _lectura(
                "SS-01", "calidad_suelo",
                FIXTURE_NOW - timedelta(minutes=90), 40.5, 6.7, 20.8, 91,
            ),
            _lectura(
                "SS-01", "calidad_suelo",
                FIXTURE_NOW - timedelta(hours=3), 39.8, 6.9, 20.5, 92,
            ),
            _lectura(
                "SS-02", "calidad_suelo",
                FIXTURE_NOW - timedelta(hours=7), 45.0, 6.6, 22.0, 70,
            ),
        ]
    )
    db.lecturas.create_index([("meta.sensor_id", 1), ("timestamp", -1)])

    db.usuarios.insert_many(
        [
            {
                "_id": USUARIO_ADMIN_ID,
                "nombre": "Ana Administradora",
                "correo": "admin@teiba.local",
                "telefono": "+57 300 000 0001",
                "rol": "administrador",
                "fecha_registro": FIXTURE_NOW,
            },
            {
                "_id": USUARIO_OPERADOR_ID,
                "nombre": "Óscar Operador",
                "correo": "operador@teiba.local",
                "telefono": "+57 300 000 0002",
                "rol": "operador_mantenimiento",
                "fecha_registro": FIXTURE_NOW,
            },
            {
                "_id": USUARIO_OTRO_ID,
                "nombre": "Olga Operadora",
                "correo": "otro@teiba.local",
                "telefono": "+57 300 000 0003",
                "rol": "operador_mantenimiento",
                "fecha_registro": FIXTURE_NOW,
            },
            {
                "_id": USUARIO_CIUDADANO_ID,
                "nombre": "Carla Ciudadana",
                "correo": "ciudadano@teiba.local",
                "telefono": "+57 300 000 0004",
                "rol": "ciudadano",
                "fecha_registro": FIXTURE_NOW,
            },
        ]
    )

    db.elementos_inventario.insert_many(
        [
            {
                "_id": ELEMENTO_BANCA_ID,
                "parque_id": PARQUE_ID,
                "sector_id": SECTOR_NORTE,
                "tipo_elemento": "banca",
                "cantidad": 12,
                "estado": "bueno",
            },
            {
                "_id": ELEMENTO_JUEGO_ID,
                "parque_id": PARQUE_ID,
                "sector_id": SECTOR_BOSQUE,
                "tipo_elemento": "juego_infantil",
                "cantidad": 3,
                "estado": "danado",
            },
        ]
    )

    db.incidentes.insert_one(
        {
            "_id": INCIDENTE_ID,
            "tipo": "infraestructura",
            "descripcion": "Juego infantil con tornillo suelto en el Sector Bosque.",
            "fecha_hora": FIXTURE_NOW - timedelta(hours=6),
            "parque_id": PARQUE_ID,
            "reportado_por_id": USUARIO_CIUDADANO_ID,
            "estado": "reportado",
            "prioridad": "alta",
            "evidencias": [],
        }
    )

    db.mantenimientos.insert_many(
        [
            {
                "_id": MANTENIMIENTO_PENDIENTE_ID,
                "tipo": "correctivo",
                "descripcion": "Ajustar tornillo del juego infantil.",
                "fecha_programada": FIXTURE_NOW + timedelta(days=2),
                "fecha_ejecucion": None,
                "estado": "pendiente",
                "prioridad": "alta",
                "nota_cierre": None,
                "nota_reapertura": None,
                "fecha_reapertura": None,
                "incidente_id": INCIDENTE_ID,
                "parque_id": PARQUE_ID,
                "elemento_id": ELEMENTO_JUEGO_ID,
                "responsable_id": USUARIO_OPERADOR_ID,
                "costo_estimado": 120000.0,
            },
            {
                "_id": MANTENIMIENTO_PROCESO_ID,
                "tipo": "preventivo",
                "descripcion": "Revisar anclajes de las bancas.",
                "fecha_programada": FIXTURE_NOW - timedelta(days=1),
                "fecha_ejecucion": None,
                "estado": "en_proceso",
                "prioridad": "media",
                "nota_cierre": None,
                "nota_reapertura": None,
                "fecha_reapertura": None,
                "incidente_id": None,
                "parque_id": PARQUE_ID,
                "elemento_id": ELEMENTO_BANCA_ID,
                "responsable_id": USUARIO_OPERADOR_ID,
                "costo_estimado": 80000.0,
            },
            {
                "_id": MANTENIMIENTO_FINALIZADO_ID,
                "tipo": "correctivo",
                "descripcion": "Cambiar tablón deteriorado del sendero.",
                "fecha_programada": FIXTURE_NOW - timedelta(days=5),
                "fecha_ejecucion": FIXTURE_NOW - timedelta(days=4),
                "estado": "finalizado",
                "prioridad": "baja",
                "nota_cierre": "Tablón reemplazado y lijado.",
                "nota_reapertura": None,
                "fecha_reapertura": None,
                "incidente_id": None,
                "parque_id": PARQUE_ID,
                "elemento_id": None,
                "responsable_id": USUARIO_OTRO_ID,
                "costo_estimado": 45000.0,
            },
        ]
    )
