"""Indicaciones de visita derivadas de los datos del parque.

Son reglas deterministas sobre campos que ya existen (`tipo_parque`,
`estado_general`, `zona_riesgo`): no inventan contenido editorial y no
requieren ninguna colección nueva.
"""
from typing import Any, Literal

Nivel = Literal["info", "warning"]


def generar_indicaciones(
    tipo_parque: str | None,
    estado_general: str | None,
    sectores: list[dict[str, Any]],
) -> list[dict[str, str]]:
    """Devuelve indicaciones ordenadas por relevancia y sin duplicados."""
    indicaciones: list[dict[str, str]] = []

    def _agregar(nivel: Nivel, mensaje: str) -> None:
        if all(item["mensaje"] != mensaje for item in indicaciones):
            indicaciones.append({"nivel": nivel, "mensaje": mensaje})

    if estado_general == "deteriorado":
        _agregar(
            "warning",
            "Parque en estado deteriorado; transita con precaución.",
        )
    elif estado_general == "regular":
        _agregar(
            "info",
            "Parque en estado regular; revisa los sectores antes de tu visita.",
        )

    if any(sector.get("zona_riesgo") == "alta" for sector in sectores):
        _agregar(
            "warning",
            "Hay sectores con riesgo alto; sigue las indicaciones del personal.",
        )

    if tipo_parque == "infantil":
        _agregar("info", "Zona infantil; supervisa a los menores.")
    elif tipo_parque == "ecologico":
        _agregar("info", "Parque ecológico; permanece en los senderos.")
    elif tipo_parque == "deportivo":
        _agregar("info", "Parque deportivo; usa el calzado adecuado.")
    elif tipo_parque == "metropolitano":
        _agregar("info", "Parque metropolitano; consulta los accesos disponibles.")
    elif tipo_parque == "recreativo":
        _agregar("info", "Parque recreativo; disfruta las zonas verdes.")

    if estado_general == "bueno" and not any(
        sector.get("zona_riesgo") == "alta" for sector in sectores
    ):
        _agregar(
            "info",
            "Parque en buen estado; respeta las zonas verdes y el mobiliario.",
        )
    elif estado_general != "deteriorado":
        _agregar("info", "Revisa el estado de los sectores antes de tu visita.")

    return indicaciones
