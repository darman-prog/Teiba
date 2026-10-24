"""Bucle del agente: LLM + tools + trazas + caché.

El RAG vive aquí: se recupera con tools, se aumenta el contexto del LLM y se
genera una respuesta trazable. El LLM nunca consulta Mongo directamente.
"""
import json
import logging
import time
from typing import Any

from app.agent.cache import ResponseCache
from app.agent.prompts import SYSTEM_PROMPT
from app.agent.tools import TOOLS, AgentTools
from app.application.errors import AgentError
from app.application.ports import LLMClient, LLMError, LLMMessage
from app.config import Settings, get_settings

logger = logging.getLogger("teiba.agent")


class AgentRunner:
    def __init__(
        self,
        llm: LLMClient,
        tools: AgentTools,
        settings: Settings | None = None,
        cache: ResponseCache | None = None,
    ) -> None:
        self._llm = llm
        self._tools = tools
        self._settings = settings or get_settings()
        self._cache = cache or ResponseCache(self._settings.demo_cache_ttl_seconds)

    def consultar(self, pregunta: str, trace_id: str) -> dict[str, Any]:
        pregunta = (pregunta or "").strip()
        if not pregunta:
            raise AgentError(422, "invalid_request", "La pregunta no puede estar vacía.")
        if not self._settings.llm_configurado:
            raise AgentError(
                503,
                "llm_not_configured",
                "La API del agente no está configurada. Define OPENCODE_API_KEY.",
            )

        cache_key = self._cache_key(pregunta)
        cached = self._cache.get(cache_key)
        inicio = time.perf_counter()
        if cached is not None:
            respuesta, trazas = cached
            return self._response(
                respuesta,
                trazas,
                trace_id,
                inicio,
                pasos=0,
                cached=True,
            )

        messages: list[dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": pregunta},
        ]
        trazas: list[dict[str, Any]] = []
        firmas: set[tuple[str, str]] = set()
        pasos = 0
        correctivo_usado = False

        for _ in range(self._settings.agent_max_steps):
            # Tope duro de pasos: sin esto, un modelo confundido puede iterar sin fin.
            if time.perf_counter() - inicio > self._settings.agent_total_timeout_seconds:
                raise AgentError(
                    504,
                    "timeout",
                    "La consulta superó el tiempo máximo permitido.",
                )
            pasos += 1
            message = self._chat_with_retry(messages)

            if not message.tool_calls:
                content = (message.content or "").strip()
                if content and trazas:
                    self._cache.set(cache_key, content, trazas)
                    return self._response(content, trazas, trace_id, inicio, pasos)
                if content and not trazas and not correctivo_usado:
                    # Si el modelo responde sin tools, no se acepta: se le obliga a verificar.
                    correctivo_usado = True
                    messages.append({"role": "assistant", "content": content})
                    messages.append(
                        {
                            "role": "system",
                            "content": (
                                "No respondiste usando herramientas. Vuelve a intentarlo: "
                                "consulta los datos con las tools y responde solo con ellos. "
                                "Si no hay datos, dilo."
                            ),
                        }
                    )
                    continue
                if content and not trazas:
                    return self._fallback(trazas, trace_id, inicio, pasos)
                messages.append(
                    {
                        "role": "system",
                        "content": (
                            "Tu respuesta quedó vacía. Usa las herramientas para obtener "
                            "datos y responde en español."
                        ),
                    }
                )
                continue

            messages.append(self._assistant_message(message))
            for call in message.tool_calls:
                args = self._safe_args(call.arguments)
                firma = (
                    call.name,
                    json.dumps(args, sort_keys=True, ensure_ascii=False, default=str),
                )
                start = time.perf_counter()
                # Evita que el modelo repita la misma consulta y queme pasos/tokens.
                if firma in firmas:
                    result = {
                        "error": {
                            "code": "repeated_call",
                            "message": (
                                "Ya consultaste esta herramienta con los mismos "
                                "argumentos; usa el resultado anterior."
                            ),
                        }
                    }
                else:
                    firmas.add(firma)
                    result = self._tools.dispatch(call.name, call.arguments)
                ms = max(0, int((time.perf_counter() - start) * 1000))
                trazas.append(self._trace(call.name, args, result, ms))
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": json.dumps(result, ensure_ascii=False, default=str),
                    }
                )

        return self._fallback(trazas, trace_id, inicio, pasos)

    def _chat_with_retry(self, messages: list[dict]) -> LLMMessage:
        for intento in range(2):
            try:
                return self._llm.chat(messages, TOOLS)
            except LLMError as exc:
                if exc.retryable and intento == 0:
                    time.sleep(1.0)
                    continue
                raise self._to_agent_error(exc) from exc
        raise AgentError(
            502,
            "llm_unavailable",
            "El servicio del agente no está disponible.",
        )

    @staticmethod
    def _to_agent_error(exc: LLMError) -> AgentError:
        logger.warning("llm_error code=%s retryable=%s", exc.code, exc.retryable)
        if exc.code == "llm_timeout":
            return AgentError(504, "timeout", "El agente no respondió a tiempo.")
        if exc.code == "llm_auth":
            return AgentError(
                503,
                "llm_not_configured",
                "La API del agente no está configurada o rechazó las credenciales.",
            )
        return AgentError(
            502,
            "llm_unavailable",
            "El servicio del agente no está disponible. Intenta de nuevo.",
        )

    @staticmethod
    def _assistant_message(message: LLMMessage) -> dict:
        return {
            "role": "assistant",
            "content": message.content,
            "tool_calls": [
                {
                    "id": call.id,
                    "type": "function",
                    "function": {
                        "name": call.name,
                        "arguments": call.arguments,
                    },
                }
                for call in message.tool_calls
            ],
        }

    @staticmethod
    def _safe_args(raw_arguments: str) -> dict:
        try:
            data = json.loads(raw_arguments)
        except (json.JSONDecodeError, TypeError):
            return {}
        return data if isinstance(data, dict) else {}

    def _trace(self, name: str, args: dict, result: dict, ms: int) -> dict:
        resultado = json.dumps(result, ensure_ascii=False, default=str)
        limite = self._settings.tool_result_max_chars
        if len(resultado) > limite:
            resultado = resultado[:limite] + "... [truncado]"
        return {
            "tool": name,
            "args": args,
            "ok": "error" not in result,
            "ms": ms,
            "resumen": self._resumen(result),
            "resultado": resultado,
        }

    @staticmethod
    def _resumen(result: dict) -> str:
        if "error" in result:
            return str(result["error"].get("message", ""))[:200]
        if result.get("resumen"):
            return str(result["resumen"])[:200]
        if result.get("estado") == "ok":
            if "items" in result:
                return f"{result.get('total', len(result['items']))} dispositivos"
            return "ok"
        if result.get("estado"):
            mensaje = result.get("mensaje", "")
            return f"{result['estado']}: {mensaje}"[:200]
        if result.get("estado_datos"):
            return str(result.get("resumen", ""))[:200]
        return "ok"

    def _response(
        self,
        respuesta: str,
        trazas: list[dict],
        trace_id: str,
        inicio: float,
        pasos: int,
        cached: bool = False,
    ) -> dict[str, Any]:
        return {
            "respuesta": respuesta,
            "trazas": trazas,
            "meta": {
                "modelo": self._settings.agent_model,
                "pasos": pasos,
                "duracion_ms": max(0, int((time.perf_counter() - inicio) * 1000)),
                "cached": cached,
                "trace_id": trace_id,
            },
        }

    def _fallback(
        self,
        trazas: list[dict],
        trace_id: str,
        inicio: float,
        pasos: int,
    ) -> dict[str, Any]:
        return self._response(
            (
                "No pude verificar la información con las herramientas disponibles. "
                "Reformula la pregunta o indica el sector y el sensor."
            ),
            trazas,
            trace_id,
            inicio,
            pasos,
        )

    def _cache_key(self, pregunta: str) -> str:
        normalizada = " ".join(pregunta.lower().split())
        return f"{self._settings.agent_model}:{normalizada}"
