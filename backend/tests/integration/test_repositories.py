"""Repositorios contra un MongoDB de prueba (`teiba_test`)."""
from datetime import timedelta

import pytest

from app.infrastructure.mongo_repositories import (
    MongoDeviceRepository,
    MongoReadingRepository,
)
from tests.integration.fixtures import FIXTURE_NOW, SECTOR_NORTE

pytestmark = pytest.mark.integration


def test_resolve_sector_norte(mongo_db):
    matches = MongoDeviceRepository(mongo_db).resolve_sector("Sector Norte")

    assert len(matches) == 1
    assert matches[0]["codigo"] == "SEC-001"
    assert matches[0]["id"] == SECTOR_NORTE


def test_resolve_sector_ambiguo(mongo_db):
    matches = MongoDeviceRepository(mongo_db).resolve_sector("Sector")

    assert len(matches) == 2


def test_find_devices_por_sector(mongo_db):
    docs = MongoDeviceRepository(mongo_db).find_devices(sector_ids=[SECTOR_NORTE])

    assert {doc["_id"] for doc in docs} == {"ANT-01", "SS-01", "MET-01"}
    ss01 = next(doc for doc in docs if doc["_id"] == "SS-01")
    assert ss01["sector"].startswith("Sector Norte")
    assert ss01["parque"] == "Parque San Pío"
    assert ss01["comuna"].startswith("Comuna")


def test_get_device_con_contexto(mongo_db):
    doc = MongoDeviceRepository(mongo_db).get_device("SS-01")

    assert doc is not None
    assert doc["depende_de"] == "ANT-01"
    assert doc["tipo"] == "calidad_suelo"
    assert doc["sector_codigo"] == "SEC-001"


def test_children_of_ant01(mongo_db):
    repo = MongoDeviceRepository(mongo_db)

    assert {doc["_id"] for doc in repo.children_of("ANT-01")} == {"SS-01", "SS-02", "MET-01"}
    assert repo.count_children("ANT-01") == 3


def test_history_en_ventana(mongo_db):
    hist = MongoReadingRepository(mongo_db).history(
        "SS-01",
        FIXTURE_NOW - timedelta(hours=2),
        20,
    )

    assert len(hist) == 2
    assert hist[0]["timestamp"] > hist[1]["timestamp"]


def test_history_respeta_limite(mongo_db):
    hist = MongoReadingRepository(mongo_db).history(
        "SS-01",
        FIXTURE_NOW - timedelta(hours=4),
        1,
    )

    assert len(hist) == 1


def test_history_sin_lecturas(mongo_db):
    hist = MongoReadingRepository(mongo_db).history(
        "MET-01",
        FIXTURE_NOW - timedelta(hours=4),
        20,
    )

    assert hist == []


def test_latest_y_latest_many(mongo_db):
    repo = MongoReadingRepository(mongo_db)

    latest = repo.latest("SS-01")
    assert latest is not None
    assert latest["timestamp"] == FIXTURE_NOW - timedelta(minutes=30)

    varios = repo.latest_many(["SS-01", "SS-02", "MET-01"])
    assert set(varios) == {"SS-01", "SS-02"}
    assert varios["SS-02"]["bateria"] == 70


def test_latest_sin_lecturas(mongo_db):
    assert MongoReadingRepository(mongo_db).latest("MET-01") is None
