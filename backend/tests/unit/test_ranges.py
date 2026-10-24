"""Rangos y evaluación determinista."""
from app.domain.ranges import evaluar_lectura, evaluar_metrica, rango_texto


def test_rango_texto_incluye_unidad():
    assert "6.0 - 7.5" in rango_texto("ph")
    assert "%" in rango_texto("humedad")


def test_metrica_normal():
    evaluacion = evaluar_metrica("ph", 6.8)
    assert evaluacion["estado"] == "normal"
    assert evaluacion["direccion"] is None


def test_metrica_baja():
    evaluacion = evaluar_metrica("ph", 5.4)
    assert evaluacion["estado"] == "bajo"
    assert evaluacion["direccion"] == "bajo"


def test_metrica_alta():
    evaluacion = evaluar_metrica("temperatura", 30.0)
    assert evaluacion["estado"] == "alto"
    assert evaluacion["direccion"] == "alto"


def test_metrica_sin_datos():
    evaluacion = evaluar_metrica("humedad", None)
    assert evaluacion["estado"] == "sin_datos"
    assert evaluacion["valor"] is None


def test_lectura_fuera_de_rango():
    evaluacion = evaluar_lectura(
        {"humedad": 41.2, "ph": 5.4, "temperatura": 21.0, "bateria": 80}
    )
    assert evaluacion["estado_global"] == "fuera_de_rango"
    assert evaluacion["fuera_de_rango"] == ["ph"]
    assert evaluacion["metricas"]["ph"]["estado"] == "bajo"


def test_lectura_normal():
    evaluacion = evaluar_lectura(
        {"humedad": 41.2, "ph": 6.8, "temperatura": 21.0, "bateria": 80}
    )
    assert evaluacion["estado_global"] == "normal"
    assert evaluacion["fuera_de_rango"] == []


def test_bateria_baja_es_alerta():
    evaluacion = evaluar_lectura(
        {"humedad": 41.2, "ph": 6.8, "temperatura": 21.0, "bateria": 15}
    )
    assert evaluacion["fuera_de_rango"] == ["bateria"]
