"""Rangos operativos y evaluación determinista de una lectura.

El LLM no calcula rangos: recibe `evaluacion` ya resuelta por el dominio.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Rango:
    minimo: float
    maximo: float
    unidad: str
    etiqueta: str


RANGOS: dict[str, Rango] = {
    "humedad": Rango(30.0, 60.0, "%", "Humedad"),
    "ph": Rango(6.0, 7.5, "", "pH"),
    "temperatura": Rango(15.0, 28.0, "°C", "Temperatura"),
    "bateria": Rango(20.0, 100.0, "%", "Batería"),
}


def rango_texto(nombre: str) -> str:
    rango = RANGOS[nombre]
    unidad = f" {rango.unidad}" if rango.unidad else ""
    return f"{rango.minimo:.1f} - {rango.maximo:.1f}{unidad}"


def evaluar_metrica(nombre: str, valor: float | int | None) -> dict:
    """Evalúa una métrica contra su rango y explica la dirección del desvío."""
    rango = RANGOS[nombre]
    if valor is None:
        return {
            "metrica": nombre,
            "etiqueta": rango.etiqueta,
            "valor": None,
            "rango": rango_texto(nombre),
            "unidad": rango.unidad,
            "estado": "sin_datos",
            "direccion": None,
        }

    estado = "normal"
    direccion = None
    if valor < rango.minimo:
        estado = "bajo"
        direccion = "bajo"
    elif valor > rango.maximo:
        estado = "alto"
        direccion = "alto"

    return {
        "metrica": nombre,
        "etiqueta": rango.etiqueta,
        "valor": valor,
        "rango": rango_texto(nombre),
        "unidad": rango.unidad,
        "estado": estado,
        "direccion": direccion,
    }


def evaluar_lectura(lectura: dict) -> dict:
    """Evalúa las cuatro métricas y resume si algo está fuera de rango."""
    metricas = {
        nombre: evaluar_metrica(nombre, lectura.get(nombre))
        for nombre in RANGOS
    }
    fuera_de_rango = [
        nombre
        for nombre, evaluacion in metricas.items()
        if evaluacion["estado"] in {"bajo", "alto"}
    ]
    return {
        "metricas": metricas,
        "estado_global": "normal" if not fuera_de_rango else "fuera_de_rango",
        "fuera_de_rango": fuera_de_rango,
    }
