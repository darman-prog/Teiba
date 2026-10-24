"""Validación de argumentos de tools."""
import pytest

from app.agent.validation import ToolValidationError, parse_tool_args


def test_argumentos_validos():
    args = parse_tool_args("get_sensor_history", '{"sensor_id":"SS-01"}')

    assert args.sensor_id == "SS-01"
    assert args.horas == 6
    assert args.limite == 20


def test_rechaza_claves_extra():
    with pytest.raises(ToolValidationError) as exc:
        parse_tool_args("get_sensor_history", '{"sensor_id":"SS-01","extra":1}')

    assert exc.value.code == "invalid_args"


def test_rechaza_operador_nosql():
    with pytest.raises(ToolValidationError) as exc:
        parse_tool_args("get_sensor_history", '{"sensor_id":{"$ne":null}}')

    assert exc.value.code == "invalid_args"


def test_rechaza_punto_en_sector():
    with pytest.raises(ToolValidationError) as exc:
        parse_tool_args("list_sensors", '{"sector":"Sector.Norte"}')

    assert exc.value.code == "invalid_args"


def test_rechaza_horas_fuera_de_rango():
    with pytest.raises(ToolValidationError) as exc:
        parse_tool_args("get_sensor_history", '{"sensor_id":"SS-01","horas":0}')

    assert exc.value.code == "invalid_args"


def test_rechaza_limite_fuera_de_rango():
    with pytest.raises(ToolValidationError) as exc:
        parse_tool_args("list_sensors", '{"limite":51}')

    assert exc.value.code == "invalid_args"


def test_rechaza_tool_desconocida():
    with pytest.raises(ToolValidationError) as exc:
        parse_tool_args("drop_database", "{}")

    assert exc.value.code == "unknown_tool"


def test_rechaza_json_invalido():
    with pytest.raises(ToolValidationError) as exc:
        parse_tool_args("get_sensor_history", "{sensor_id:")

    assert exc.value.code == "invalid_args"
