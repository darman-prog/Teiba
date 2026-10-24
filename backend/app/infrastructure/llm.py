"""Cliente del LLM contra OpenCode Go (API compatible con OpenAI).

El SDK se aísla aquí: la capa de aplicación solo ve `LLMMessage` y `LLMError`.
"""
import logging

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    OpenAI,
    PermissionDeniedError,
    RateLimitError,
)

from app.application.ports import LLMClient, LLMError, LLMMessage, ToolCall
from app.config import Settings

logger = logging.getLogger("teiba.llm")


class OpenCodeLLMClient(LLMClient):
    def __init__(self, settings: Settings):
        if not settings.llm_configurado or settings.opencode_api_key is None:
            raise LLMError(
                "llm_auth",
                "OPENCODE_API_KEY no está configurada.",
                retryable=False,
            )
        self._settings = settings
        self._client = OpenAI(
            base_url=settings.opencode_base_url,
            api_key=settings.opencode_api_key.get_secret_value(),
            timeout=settings.agent_timeout_seconds,
            max_retries=0,
        )

    def chat(self, messages: list[dict], tools: list[dict]) -> LLMMessage:
        # Traduce cada fallo del SDK a un código que el bucle sabe reintentar o mapear.
        try:
            response = self._client.chat.completions.create(
                model=self._settings.agent_model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=self._settings.agent_temperature,
                max_tokens=self._settings.agent_max_tokens,
            )
        except AuthenticationError as exc:
            raise LLMError("llm_auth", "Credenciales del LLM rechazadas.", False) from exc
        except PermissionDeniedError as exc:
            raise LLMError("llm_auth", "El modelo no está permitido.", False) from exc
        except RateLimitError as exc:
            raise LLMError("llm_rate", "Límite de uso del LLM alcanzado.", True) from exc
        except APITimeoutError as exc:
            raise LLMError("llm_timeout", "El LLM no respondió a tiempo.", True) from exc
        except APIConnectionError as exc:
            raise LLMError("llm_connection", "No se pudo conectar con el LLM.", True) from exc
        except BadRequestError as exc:
            raise LLMError("llm_error", "Solicitud rechazada por el LLM.", False) from exc
        except APIStatusError as exc:
            retryable = exc.status_code >= 500 or exc.status_code == 429
            if exc.status_code in (401, 403):
                raise LLMError(
                    "llm_auth",
                    "Credenciales o permisos del LLM inválidos.",
                    False,
                ) from exc
            raise LLMError("llm_upstream", "Error del proveedor LLM.", retryable) from exc
        except Exception as exc:
            logger.exception("llm_error_inesperado")
            raise LLMError("llm_error", "Error inesperado del LLM.", False) from exc

        if not response.choices:
            raise LLMError("llm_error", "El LLM no devolvió opciones.", False)

        message = response.choices[0].message
        tool_calls = [
            ToolCall(
                id=call.id,
                name=call.function.name,
                arguments=call.function.arguments or "{}",
            )
            for call in (message.tool_calls or [])
        ]
        return LLMMessage(content=message.content, tool_calls=tool_calls)
