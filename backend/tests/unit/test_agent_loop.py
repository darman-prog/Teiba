"""Bucle del agente con LLM y tools falsos (sin red ni Mongo)."""
import pytest
from pydantic import SecretStr

from app.agent.loop import AgentRunner
from app.application.errors import AgentError
from app.application.ports import LLMError, LLMMessage, ToolCall
from app.config import get_settings


class FakeLLM:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = 0

    def chat(self, messages, tools):
        self.calls += 1
        if not self.responses:
            raise AssertionError("El LLM falso no tiene más respuestas")
        return self.responses.pop(0)


class FailingLLM:
    def __init__(self, error: LLMError):
        self.error = error
        self.calls = 0

    def chat(self, messages, tools):
        self.calls += 1
        raise self.error


class FakeTools:
    def __init__(self, results=None):
        self.results = results or {}
        self.calls = []

    def dispatch(self, name, raw_arguments):
        self.calls.append((name, raw_arguments))
        return self.results.get(name, {"estado": "ok", "items": [], "total": 0})


@pytest.fixture()
def settings(monkeypatch):
    config = get_settings()
    monkeypatch.setattr(config, "opencode_api_key", SecretStr("test-key"))
    monkeypatch.setattr(config, "agent_max_steps", 6)
    monkeypatch.setattr(config, "demo_cache_ttl_seconds", 60)
    return config


def _tool_call(name="list_sensors", arguments='{"tipo":"calidad_suelo"}'):
    return LLMMessage(
        content=None,
        tool_calls=[ToolCall(id="call-1", name=name, arguments=arguments)],
    )


def test_consulta_con_tools_y_respuesta_final(settings):
    llm = FakeLLM(
        [
            _tool_call(),
            LLMMessage(content="SS-01 está en rango.", tool_calls=[]),
        ]
    )
    tools = FakeTools({"list_sensors": {"estado": "ok", "items": [{"id": "SS-01"}], "total": 1}})
    runner = AgentRunner(llm, tools, settings)

    resultado = runner.consultar("¿Cómo está el suelo?", "trace-1")

    assert resultado["respuesta"] == "SS-01 está en rango."
    assert len(resultado["trazas"]) == 1
    assert resultado["trazas"][0]["tool"] == "list_sensors"
    assert resultado["trazas"][0]["ok"] is True
    assert resultado["meta"]["pasos"] == 2
    assert resultado["meta"]["cached"] is False
    assert resultado["meta"]["trace_id"] == "trace-1"


def test_correctivo_si_responde_sin_tools(settings):
    llm = FakeLLM(
        [
            LLMMessage(content="Respuesta inventada", tool_calls=[]),
            _tool_call(),
            LLMMessage(content="SS-01 está en rango.", tool_calls=[]),
        ]
    )
    tools = FakeTools({"list_sensors": {"estado": "ok", "items": [{"id": "SS-01"}], "total": 1}})
    runner = AgentRunner(llm, tools, settings)

    resultado = runner.consultar("¿Cómo está el suelo?", "trace-2")

    assert resultado["respuesta"] == "SS-01 está en rango."
    assert resultado["meta"]["pasos"] == 3
    assert len(resultado["trazas"]) == 1
    assert "inventada" not in resultado["respuesta"]


def test_sin_tools_dos_veces_devuelve_fallback(settings):
    llm = FakeLLM(
        [
            LLMMessage(content="Respuesta inventada", tool_calls=[]),
            LLMMessage(content="Otra respuesta inventada", tool_calls=[]),
        ]
    )
    runner = AgentRunner(llm, FakeTools(), settings)

    resultado = runner.consultar("¿Cómo está el suelo?", "trace-3")

    assert "No pude verificar" in resultado["respuesta"]
    assert resultado["trazas"] == []
    assert resultado["meta"]["pasos"] == 2


def test_repeticion_de_tool_no_se_ejecuta_dos_veces(settings):
    llm = FakeLLM(
        [
            _tool_call(),
            _tool_call(),
            LLMMessage(content="SS-01 está en rango.", tool_calls=[]),
        ]
    )
    tools = FakeTools({"list_sensors": {"estado": "ok", "items": [{"id": "SS-01"}], "total": 1}})
    runner = AgentRunner(llm, tools, settings)

    resultado = runner.consultar("¿Cómo está el suelo?", "trace-4")

    assert len(resultado["trazas"]) == 2
    assert resultado["trazas"][0]["ok"] is True
    assert resultado["trazas"][1]["ok"] is False
    assert "Ya consultaste" in resultado["trazas"][1]["resumen"]
    assert len(tools.calls) == 1


def test_agota_pasos_y_devuelve_fallback(settings):
    corta = settings.model_copy(update={"agent_max_steps": 2})
    llm = FakeLLM([_tool_call(), _tool_call(), _tool_call()])
    runner = AgentRunner(llm, FakeTools(), corta)

    resultado = runner.consultar("¿Cómo está el suelo?", "trace-5")

    assert "No pude verificar" in resultado["respuesta"]
    assert resultado["meta"]["pasos"] == 2
    assert len(resultado["trazas"]) == 2


def test_cache_evita_segunda_llamada(settings):
    llm = FakeLLM(
        [
            _tool_call(),
            LLMMessage(content="SS-01 está en rango.", tool_calls=[]),
        ]
    )
    tools = FakeTools({"list_sensors": {"estado": "ok", "items": [{"id": "SS-01"}], "total": 1}})
    runner = AgentRunner(llm, tools, settings)

    primera = runner.consultar("¿Cómo está el suelo?", "trace-6")
    segunda = runner.consultar("¿Cómo está el suelo?", "trace-7")

    assert primera["meta"]["cached"] is False
    assert segunda["meta"]["cached"] is True
    assert segunda["respuesta"] == primera["respuesta"]
    assert segunda["meta"]["trace_id"] == "trace-7"
    assert llm.calls == 2


def test_error_de_autenticacion_no_se_reintenta(settings):
    llm = FailingLLM(LLMError("llm_auth", "sin permisos", retryable=False))
    runner = AgentRunner(llm, FakeTools(), settings)

    with pytest.raises(AgentError) as exc:
        runner.consultar("¿Cómo está el suelo?", "trace-8")

    assert exc.value.status_code == 503
    assert exc.value.code == "llm_not_configured"
    assert llm.calls == 1


def test_error_de_rate_se_reintenta_una_vez(settings, monkeypatch):
    monkeypatch.setattr("app.agent.loop.time.sleep", lambda _: None)
    llm = FailingLLM(LLMError("llm_rate", "límite", retryable=True))
    runner = AgentRunner(llm, FakeTools(), settings)

    with pytest.raises(AgentError) as exc:
        runner.consultar("¿Cómo está el suelo?", "trace-9")

    assert exc.value.status_code == 502
    assert exc.value.code == "llm_unavailable"
    assert llm.calls == 2


def test_sin_key_no_llama_al_llm(settings):
    sin_key = settings.model_copy(update={"opencode_api_key": None})
    llm = FakeLLM([])
    runner = AgentRunner(llm, FakeTools(), sin_key)

    with pytest.raises(AgentError) as exc:
        runner.consultar("¿Cómo está el suelo?", "trace-10")

    assert exc.value.status_code == 503
    assert exc.value.code == "llm_not_configured"
    assert llm.calls == 0


def test_pregunta_vacia(settings):
    runner = AgentRunner(FakeLLM([]), FakeTools(), settings)

    with pytest.raises(AgentError) as exc:
        runner.consultar("   ", "trace-11")

    assert exc.value.status_code == 422
