"""Herramientas de solo lectura que el LLM puede invocar.

Cada tool devuelve un dict JSON-serializable, acotado y con errores
explÃ­citos. El LLM nunca ejecuta consultas: solo elige la tool y sus args.
"""
import logging
from datetime import timedelta

from app.agent.validation import (
    DeviceContextArgs,
    DevicesByAntennaArgs,
    ListSensorsArgs,
    SensorHistoryArgs,
    ToolValidationError,
    parse_tool_args,
)
from app.application.ports import Clock, DeviceRepository, ReadingRepository
from app.application.serializers import (
    antiguedad_min,
    serialize_device,
    serialize_lectura,
)
from app.domain.ranges import RANGOS, evaluar_lectura

logger = logging.getLogger("teiba.agent")

SENSOR_TYPES = {"calidad_suelo", "estacion_meteorologica"}

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_sensors",
            "description": (
                "Lista dispositivos (sensores o antenas) y su sector/parque. "
                "Usa tipo='calidad_suelo' para sensores de suelo y "
                "tipo='antena_enlace' para antenas. Puede filtrar por sector, "
                "parque o ID de antena."
            ),
            "parameters": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "tipo": {
                        "type": "string",
                        "enum": [
                            "calidad_suelo",
                            "estacion_meteorologica",
                            "luminaria_inteligente",
                            "antena_enlace",
                        ],
                    },
                    "sector": {"type": "string"},
                    "parque": {"type": "string"},
                    "depende_de": {"type": "string"},
                    "limite": {"type": "integer", "minimum": 1, "maximum": 50},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_sensor_history",
            "description": (
                "Devuelve las lecturas recientes de un sensor (mÃ¡s nuevas primero), "
                "su Ãºltima lectura, la antigÃ¼edad en minutos y la evaluaciÃ³n de "
                "rangos ya calculada. Si no hay datos en la ventana, indÃ­calo."
            ),
            "parameters": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "sensor_id": {"type": "string"},
                    "horas": {"type": "integer", "minimum": 1, "maximum": 168},
                    "limite": {"type": "integer", "minimum": 1, "maximum": 50},
                },
                "required": ["sensor_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_device_context",
            "description": (
                "Datos estÃ¡ticos de un dispositivo: sector, parque, comuna, "
                "antena de la que depende, alimentaciÃ³n y dispositivos dependientes."
            ),
            "parameters": {
                "type": "object",
                "additionalProperties": False,
                "properties": {"device_id": {"type": "string"}},
                "required": ["device_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_devices_by_antenna",
            "description": (
                "Lista los dispositivos que dependen de una antena y su Ãºltima "
                "lectura. Marca sin_reportar cuando no hay lecturas o son mÃ¡s "
                "antiguas que el umbral configurado."
            ),
            "parameters": {
                "type": "object",
                "additionalProperties": False,
                "properties": {"antena": {"type": "string"}},
                "required": ["antena"],
            },
        },
    },
]


def _sensor_ref(doc: dict) -> dict:
    return {
        "id": doc.get("_id"),
        "tipo": doc.get("tipo"),
        "marca": doc.get("marca"),
        "sector": doc.get("sector"),
        "parque": doc.get("parque"),
        "depende_de": doc.get("depende_de"),
    }


class AgentTools:
    """Dispatcher acotado con validaciÃ³n y errores explÃ­citos."""

    def __init__(
        self,
        devices: DeviceRepository,
        readings: ReadingRepository,
        clock: Clock,
        sin_reportar_min: int = 60,
    ) -> None:
        self._devices = devices
        self._readings = readings
        self._clock = clock
        self._sin_reportar_min = sin_reportar_min
        self._handlers = {
            "list_sensors": self.list_sensors,
            "get_sensor_history": self.get_sensor_history,
            "get_device_context": self.get_device_context,
            "get_devices_by_antenna": self.get_devices_by_antenna,
        }

    def dispatch(self, name: str, raw_arguments: str) -> dict:
        """Valida y ejecuta la tool; nunca deja escapar una excepciÃ³n."""
        try:
            args = parse_tool_args(name, raw_arguments)
        except ToolValidationError as exc:
            return {"error": {"code": exc.code, "message": exc.message}}
        handler = self._handlers.get(name)
        if handler is None:
            return {
                "error": {
                    "code": "unknown_tool",
                    "message": f"La herramienta '{name}' no estÃ¡ permitida.",
                }
            }
        try:
            return handler(args)
        except Exception:
            logger.exception("tool_error tool=%s", name)
            return {
                "error": {
                    "code": "db_error",
                    "message": "No se pudo consultar la base de datos.",
                }
            }

    def list_sensors(self, args: ListSensorsArgs) -> dict:
        sector_ids = None
        if args.sector:
            sectores = self._devices.resolve_sector(args.sector)
            if not sectores:
                return {
                    "estado": "sin_resultados",
                    "mensaje": f"No encontrÃ© un sector que coincida con '{args.sector}'.",
                    "items": [],
                }
            if len(sectores) > 1:
                return {
                    "estado": "ambiguo",
                    "mensaje": "Hay varios sectores que coinciden; pide el nombre exacto.",
                    "candidatos": [
                        {"id": str(s["id"]), "codigo": s["codigo"], "nombre": s["nombre"]}
                        for s in sectores
                    ],
                }
            sector_ids = [sectores[0]["id"]]

        parque_ids = None
        if args.parque:
            parques = self._devices.resolve_parque(args.parque)
            if not parques:
                return {
                    "estado": "sin_resultados",
                    "mensaje": f"No encontrÃ© un parque que coincida con '{args.parque}'.",
                    "items": [],
                }
            if len(parques) > 1:
                return {
                    "estado": "ambiguo",
                    "mensaje": "Hay varios parques que coinciden; pide el nombre exacto.",
                    "candidatos": [
                        {"id": str(p["id"]), "codigo": p["codigo"], "nombre": p["nombre"]}
                        for p in parques
                    ],
                }
            parque_ids = [parques[0]["id"]]

        docs = self._devices.find_devices(
            tipo=args.tipo,
            sector_ids=sector_ids,
            parque_ids=parque_ids,
            depende_de=args.depende_de,
            limite=args.limite,
        )
        if not docs:
            return {
                "estado": "sin_resultados",
                "mensaje": "No hay dispositivos que cumplan los filtros.",
                "items": [],
            }
        items = [serialize_device(doc) for doc in docs]
        return {"estado": "ok", "items": items, "total": len(items)}

    def get_sensor_history(self, args: SensorHistoryArgs) -> dict:
        device = self._devices.get_device(args.sensor_id)
        if device is None:
            return {
                "estado": "not_found",
                "mensaje": f"No existe el dispositivo '{args.sensor_id}'.",
            }
        if device.get("tipo") not in SENSOR_TYPES:
            return {
                "estado": "not_a_sensor",
                "mensaje": (
                    f"'{args.sensor_id}' es de tipo '{device.get('tipo')}' "
                    "y no reporta telemetrÃ­a ambiental."
                ),
            }

        ahora = self._clock.now()
        desde = ahora - timedelta(hours=args.horas)
        lecturas = self._readings.history(args.sensor_id, desde, args.limite)
        sensor = _sensor_ref(device)

        if lecturas:
            ultima = lecturas[0]
            evaluacion = evaluar_lectura(ultima)
            antiguedad = antiguedad_min(ultima.get("timestamp"), ahora)
            fuera = evaluacion["fuera_de_rango"]
            resumen = f"{len(lecturas)} lecturas; "
            resumen += f"fuera de rango: {', '.join(fuera)}" if fuera else "todas en rango"
            return {
                "estado_datos": "ok",
                "sensor": sensor,
                "ventana_horas": args.horas,
                "lecturas": [serialize_lectura(doc, ahora) for doc in lecturas],
                "ultima_lectura": serialize_lectura(ultima, ahora),
                "antiguedad_min": antiguedad,
                "evaluacion": evaluacion,
                "alertas_en_ventana": self._alertas_en_ventana(lecturas),
                "resumen": resumen,
            }

        ultima = self._readings.latest(args.sensor_id)
        if ultima is None:
            return {
                "estado_datos": "sin_datos",
                "sensor": sensor,
                "ventana_horas": args.horas,
                "lecturas": [],
                "ultima_lectura": None,
                "antiguedad_min": None,
                "evaluacion": None,
                "resumen": "El sensor no tiene lecturas registradas.",
            }

        antiguedad = antiguedad_min(ultima.get("timestamp"), ahora)
        return {
            "estado_datos": "sin_datos_en_ventana",
            "sensor": sensor,
            "ventana_horas": args.horas,
            "lecturas": [],
            "ultima_lectura": serialize_lectura(ultima, ahora),
            "antiguedad_min": antiguedad,
            "evaluacion": None,
            "resumen": (
                f"Sin lecturas en las Ãºltimas {args.horas} h; "
                f"la Ãºltima es de hace {antiguedad} min."
            ),
        }

    def get_device_context(self, args: DeviceContextArgs) -> dict:
        device = self._devices.get_device(args.device_id)
        if device is None:
            return {
                "estado": "not_found",
                "mensaje": f"No existe el dispositivo '{args.device_id}'.",
            }
        parent = None
        if device.get("depende_de"):
            parent = self._devices.get_device(device["depende_de"])
        children = self._devices.children_of(device["_id"])
        return {
            "estado": "ok",
            "device": serialize_device(device),
            "antena": serialize_device(parent) if parent else None,
            "dependientes": {
                "total": len(children),
                "items": [
                    {"id": child["_id"], "tipo": child.get("tipo")}
                    for child in children
                ],
            },
        }

    def get_devices_by_antenna(self, args: DevicesByAntennaArgs) -> dict:
        antena = self._devices.get_device(args.antena)
        if antena is None or antena.get("tipo") != "antena_enlace":
            return {
                "estado": "not_found",
                "mensaje": f"No existe una antena con ID '{args.antena}'.",
            }
        children = self._devices.children_of(args.antena)
        if not children:
            return {
                "estado": "sin_resultados",
                "mensaje": f"La antena '{args.antena}' no tiene dispositivos dependientes.",
                "items": [],
            }

        ahora = self._clock.now()
        latest = self._readings.latest_many([child["_id"] for child in children])
        items = []
        for child in children:
            ultima = latest.get(child["_id"])
            antiguedad = antiguedad_min(ultima.get("timestamp"), ahora) if ultima else None
            # Sin lectura o con retraso mayor al umbral: el dispositivo no reporta.
            sin_reportar = ultima is None or (
                antiguedad is not None and antiguedad > self._sin_reportar_min
            )
            motivo = None
            if ultima is None:
                motivo = "sin_lecturas"
            elif sin_reportar:
                motivo = "antiguedad"
            evaluacion = evaluar_lectura(ultima) if ultima else None
            items.append(
                {
                    "id": child["_id"],
                    "tipo": child.get("tipo"),
                    "sector": child.get("sector"),
                    "parque": child.get("parque"),
                    "ultima_lectura": serialize_lectura(ultima, ahora) if ultima else None,
                    "antiguedad_min": antiguedad,
                    "sin_reportar": sin_reportar,
                    "motivo": motivo,
                    "evaluacion": evaluacion,
                }
            )
        return {
            "estado": "ok",
            "antena": serialize_device(antena),
            "items": items,
            "total": len(items),
            "sin_reportar": sum(1 for item in items if item["sin_reportar"]),
        }

    @staticmethod
    def _alertas_en_ventana(lecturas: list[dict]) -> list[str]:
        # La alerta de ventana es histórica; la evaluación actual es la última lectura.
        alertas = []
        for nombre in RANGOS:
            valores = [doc.get(nombre) for doc in lecturas if doc.get(nombre) is not None]
            rango = RANGOS[nombre]
            if any(valor < rango.minimo or valor > rango.maximo for valor in valores):
                alertas.append(nombre)
        return alertas
