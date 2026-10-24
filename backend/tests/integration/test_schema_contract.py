"""Contrato de esquema contra `ModeloDatos.md` §3.1/§3.3.

Valida la base real de la entrega (solo lectura). Si falta un campo o cambia
un tipo BSON, este test falla y evita que la app derive del modelo.
"""
from datetime import datetime

import pytest
from bson import ObjectId

pytestmark = pytest.mark.integration

TIPOS_DISPOSITIVO = {
    "calidad_suelo",
    "estacion_meteorologica",
    "luminaria_inteligente",
    "antena_enlace",
}
ZONAS_RIESGO = {"alta", "media", "baja", "ninguna"}


def _docs(db, coleccion: str, limite: int = 10) -> list[dict]:
    docs = list(db[coleccion].find({}).limit(limite))
    assert docs, f"{coleccion} no tiene documentos"
    return docs


def test_parques_cumplen_modelo(mongo_real):
    for doc in _docs(mongo_real, "parques"):
        assert isinstance(doc["_id"], ObjectId)
        assert isinstance(doc["codigo"], str) and doc["codigo"]
        assert isinstance(doc["nombre"], str)
        ubicacion = doc["ubicacion"]
        assert isinstance(ubicacion, dict)
        assert isinstance(ubicacion["direccion"], str)
        assert isinstance(ubicacion["comuna"], str)
        coordenadas = ubicacion["coordenadas"]
        assert coordenadas["type"] == "Point"
        assert len(coordenadas["coordinates"]) == 2
        assert all(isinstance(valor, (int, float)) for valor in coordenadas["coordinates"])
        assert isinstance(doc["area_m2"], (int, float))
        assert isinstance(doc["tipo_parque"], str)
        assert isinstance(doc["estado_general"], str)


def test_sectores_cumplen_modelo(mongo_real):
    for doc in _docs(mongo_real, "sectores"):
        assert isinstance(doc["_id"], ObjectId)
        assert isinstance(doc["codigo"], str)
        assert isinstance(doc["parque_id"], ObjectId)
        assert isinstance(doc["nombre"], str)
        assert isinstance(doc["tipo_suelo"], str)
        assert doc["zona_riesgo"] in ZONAS_RIESGO


def test_dispositivos_cumplen_modelo_e_invariante(mongo_real):
    for doc in _docs(mongo_real, "dispositivos"):
        assert isinstance(doc["_id"], str)
        assert doc["tipo"] in TIPOS_DISPOSITIVO
        assert isinstance(doc["marca"], str)
        assert isinstance(doc["fecha_instalacion"], datetime)
        assert isinstance(doc["sector_id"], ObjectId)
        assert isinstance(doc["parque_id"], ObjectId)
        assert doc["depende_de"] is None or isinstance(doc["depende_de"], str)
        assert isinstance(doc["alimentado_por"], str)

        sector = mongo_real.sectores.find_one({"_id": doc["sector_id"]})
        assert sector is not None, f"dispositivo {doc['_id']} apunta a un sector inexistente"
        assert sector["parque_id"] == doc["parque_id"], (
            f"dispositivo {doc['_id']} tiene parque_id distinto al de su sector"
        )


def test_lecturas_cumplen_modelo(mongo_real):
    campos_permitidos = {
        "_id",
        "timestamp",
        "meta",
        "humedad",
        "ph",
        "temperatura",
        "bateria",
    }
    for doc in _docs(mongo_real, "lecturas", limite=20):
        assert isinstance(doc["timestamp"], datetime)
        assert isinstance(doc["meta"], dict)
        assert isinstance(doc["meta"]["sensor_id"], str)
        assert isinstance(doc["meta"]["tipo"], str)
        # El shell de Mongo guarda los enteros de JS como Int32; el dominio
        # acepta numéricos y el seed de la demo fuerza Double.
        assert isinstance(doc["humedad"], (int, float))
        assert isinstance(doc["ph"], (int, float))
        assert isinstance(doc["temperatura"], (int, float))
        assert isinstance(doc["bateria"], int)
        assert set(doc) <= campos_permitidos
        assert "mediciones" not in doc
        assert set(doc["meta"]) <= {"sensor_id", "tipo", "origen"}
