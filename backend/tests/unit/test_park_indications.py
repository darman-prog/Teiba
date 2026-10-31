"""Indicaciones de visita: reglas deterministas sobre datos del parque."""
from app.domain.parks import generar_indicaciones


def test_parque_sano_sin_riesgo():
    indicaciones = generar_indicaciones("recreativo", "bueno", [])

    mensajes = [item["mensaje"] for item in indicaciones]
    assert any("buen estado" in mensaje for mensaje in mensajes)
    assert not [item for item in indicaciones if item["nivel"] == "warning"]


def test_parque_deteriorado_advierte():
    indicaciones = generar_indicaciones("recreativo", "deteriorado", [])

    assert indicaciones[0]["nivel"] == "warning"
    assert "deteriorado" in indicaciones[0]["mensaje"]


def test_sector_riesgo_alto_advierte():
    sectores = [{"zona_riesgo": "alta"}]
    indicaciones = generar_indicaciones("ecologico", "bueno", sectores)

    niveles = [item["nivel"] for item in indicaciones]
    assert "warning" in niveles
    assert any("riesgo alto" in item["mensaje"] for item in indicaciones)


def test_tipo_infantil_y_ecologico():
    infantil = generar_indicaciones("infantil", "bueno", [])
    ecologico = generar_indicaciones("ecologico", "bueno", [])

    assert any("menores" in item["mensaje"] for item in infantil)
    assert any("senderos" in item["mensaje"] for item in ecologico)


def test_sin_duplicados():
    sectores = [{"zona_riesgo": "alta"}, {"zona_riesgo": "alta"}]
    indicaciones = generar_indicaciones("deportivo", "regular", sectores)

    mensajes = [item["mensaje"] for item in indicaciones]
    assert len(mensajes) == len(set(mensajes))
