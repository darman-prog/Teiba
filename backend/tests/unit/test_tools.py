"""Tools con repositorios y reloj falsos: dominio sin Mongo ni LLM."""
from datetime import timedelta

from app.agent.tools import AgentTools
from app.agent.validation import (
    DeviceContextArgs,
    DevicesByAntennaArgs,
    ListSensorsArgs,
    SensorHistoryArgs,
)
from tests.integration.fixtures import FIXTURE_NOW, PARQUE_ID, SECTOR_NORTE


class FixedClock:
    def now(self):
        return FIXTURE_NOW


def _device(device_id, tipo, depende_de=None, sector_id=SECTOR_NORTE):
    return {
        "_id": device_id,
        "tipo": tipo,
        "marca": "Marca",
        "fecha_instalacion": FIXTURE_NOW - timedelta(days=100),
        "sector_id": sector_id,
        "parque_id": PARQUE_ID,
        "depende_de": depende_de,
        "alimentado_por": "Panel_Solar",
        "sector": "Sector Norte - Jardines",
        "sector_codigo": "SEC-001",
        "parque": "Parque San Pío",
        "comuna": "Comuna 12",
    }


def _lectura(cuando, ph=6.8, humedad=41.2, temperatura=21.0, bateria=90):
    return {
        "timestamp": cuando,
        "meta": {"sensor_id": "SS-01", "tipo": "calidad_suelo"},
        "humedad": humedad,
        "ph": ph,
        "temperatura": temperatura,
        "bateria": bateria,
    }


class FakeDevices:
    def __init__(self):
        self.sector_matches = [
            {"id": "S1", "codigo": "SEC-001", "nombre": "Sector Norte", "parque_id": "P1"}
        ]
        self.parque_matches = [
            {"id": "P1", "codigo": "PRQ-001", "nombre": "Parque San Pío"}
        ]
        self.device_map = {
            "ANT-01": _device("ANT-01", "antena_enlace"),
            "SS-01": _device("SS-01", "calidad_suelo", "ANT-01"),
            "SS-02": _device("SS-02", "calidad_suelo", "ANT-01"),
            "MET-01": _device("MET-01", "estacion_meteorologica", "ANT-01"),
        }
        self.find_kwargs = None

    def resolve_sector(self, nombre):
        return self.sector_matches

    def resolve_parque(self, nombre):
        return self.parque_matches

    def find_devices(self, **kwargs):
        self.find_kwargs = kwargs
        return [self.device_map["SS-01"]]

    def get_device(self, device_id):
        return self.device_map.get(device_id)

    def children_of(self, antena):
        if antena != "ANT-01":
            return []
        return [self.device_map[k] for k in ("SS-01", "SS-02", "MET-01")]

    def count_children(self, antena):
        return len(self.children_of(antena))


class FakeReadings:
    def __init__(self, history=None, latest=None, latest_many=None):
        self._history = history or []
        self._latest = latest
        self._latest_many = latest_many or {}

    def history(self, sensor_id, since, limite=20):
        return self._history

    def latest(self, sensor_id):
        return self._latest

    def latest_many(self, sensor_ids):
        return self._latest_many


def _tools(readings=None, sin_reportar_min=60):
    return AgentTools(
        FakeDevices(),
        readings or FakeReadings(),
        FixedClock(),
        sin_reportar_min=sin_reportar_min,
    )


def test_list_sensors_resuelve_sector():
    tools = _tools()
    resultado = tools.list_sensors(
        ListSensorsArgs(tipo="calidad_suelo", sector="Sector Norte")
    )

    assert resultado["estado"] == "ok"
    assert resultado["items"][0]["id"] == "SS-01"
    assert tools._devices.find_kwargs["sector_ids"] == ["S1"]


def test_list_sensors_sector_ambiguo():
    tools = _tools()
    tools._devices.sector_matches = [
        {"id": "S1", "codigo": "SEC-001", "nombre": "Sector Norte", "parque_id": "P1"},
        {"id": "S2", "codigo": "SEC-002", "nombre": "Sector Sur", "parque_id": "P1"},
    ]

    resultado = tools.list_sensors(ListSensorsArgs(sector="Sector"))

    assert resultado["estado"] == "ambiguo"
    assert len(resultado["candidatos"]) == 2


def test_list_sensors_sector_inexistente():
    tools = _tools()
    tools._devices.sector_matches = []

    resultado = tools.list_sensors(ListSensorsArgs(sector="Sector Luna"))

    assert resultado["estado"] == "sin_resultados"


def test_history_con_datos_y_fuera_de_rango():
    lecturas = [
        _lectura(FIXTURE_NOW - timedelta(minutes=30), ph=5.4),
        _lectura(FIXTURE_NOW - timedelta(minutes=90), ph=6.8),
    ]
    tools = _tools(FakeReadings(history=lecturas, latest=lecturas[0]))

    resultado = tools.get_sensor_history(SensorHistoryArgs(sensor_id="SS-01"))

    assert resultado["estado_datos"] == "ok"
    assert resultado["ultima_lectura"]["antiguedad_min"] == 30
    assert resultado["evaluacion"]["fuera_de_rango"] == ["ph"]
    assert "fuera de rango" in resultado["resumen"]
    assert resultado["sensor"]["sector"].startswith("Sector Norte")


def test_history_sin_datos_en_ventana():
    ultima = _lectura(FIXTURE_NOW - timedelta(hours=3))
    tools = _tools(FakeReadings(history=[], latest=ultima))

    resultado = tools.get_sensor_history(
        SensorHistoryArgs(sensor_id="SS-01", horas=6)
    )

    assert resultado["estado_datos"] == "sin_datos_en_ventana"
    assert resultado["evaluacion"] is None
    assert resultado["antiguedad_min"] == 180


def test_history_sin_datos():
    tools = _tools(FakeReadings(history=[], latest=None))

    resultado = tools.get_sensor_history(SensorHistoryArgs(sensor_id="SS-01"))

    assert resultado["estado_datos"] == "sin_datos"
    assert resultado["ultima_lectura"] is None


def test_history_dispositivo_no_sensor():
    tools = _tools()

    resultado = tools.get_sensor_history(SensorHistoryArgs(sensor_id="ANT-01"))

    assert resultado["estado"] == "not_a_sensor"


def test_devices_by_antenna_marca_stale_y_sin_lecturas():
    tools = _tools(
        FakeReadings(
            latest_many={
                "SS-01": _lectura(FIXTURE_NOW - timedelta(minutes=30)),
                "SS-02": _lectura(FIXTURE_NOW - timedelta(hours=7)),
            }
        )
    )

    resultado = tools.get_devices_by_antenna(DevicesByAntennaArgs(antena="ANT-01"))

    assert resultado["estado"] == "ok"
    assert resultado["total"] == 3
    assert resultado["sin_reportar"] == 2
    items = {item["id"]: item for item in resultado["items"]}
    assert items["SS-01"]["sin_reportar"] is False
    assert items["SS-02"]["sin_reportar"] is True
    assert items["SS-02"]["motivo"] == "antiguedad"
    assert items["MET-01"]["sin_reportar"] is True
    assert items["MET-01"]["motivo"] == "sin_lecturas"


def test_devices_by_antenna_no_es_antena():
    tools = _tools()

    resultado = tools.get_devices_by_antenna(DevicesByAntennaArgs(antena="SS-01"))

    assert resultado["estado"] == "not_found"


def test_device_context_con_antena_y_dependientes():
    tools = _tools()

    resultado = tools.get_device_context(DeviceContextArgs(device_id="SS-01"))

    assert resultado["estado"] == "ok"
    assert resultado["antena"]["id"] == "ANT-01"
    assert resultado["dependientes"]["total"] == 0

    antena = tools.get_device_context(DeviceContextArgs(device_id="ANT-01"))
    assert antena["dependientes"]["total"] == 3


def test_dispatch_rechaza_operador_nosql():
    tools = _tools()

    resultado = tools.dispatch(
        "get_sensor_history",
        '{"sensor_id":{"$ne":null}}',
    )

    assert resultado["error"]["code"] == "invalid_args"


def test_dispatch_rechaza_tool_desconocida():
    tools = _tools()

    resultado = tools.dispatch("drop_database", "{}")

    assert resultado["error"]["code"] == "unknown_tool"
