"""Configuración tipada de la aplicación.

Las variables se leen de entorno o de `backend/.env`. Ningún secreto se
expone en respuestas ni en logs.
"""
from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración única de la API y del agente Sage."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "Teiba Sage API"
    app_version: str = "0.1.0"

    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db: str = "teiba_db"

    opencode_api_key: SecretStr | None = None
    opencode_base_url: str = "https://opencode.ai/zen/go/v1"
    agent_model: str = "deepseek-v4.1-flash"
    agent_temperature: float = 0.0
    agent_max_steps: int = 6
    agent_max_tokens: int = 600
    agent_timeout_seconds: float = 30.0
    agent_total_timeout_seconds: float = 60.0

    max_pregunta_chars: int = 500
    rate_limit_per_minute: int = 10
    rate_limit_concurrent: int = 2

    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    allowed_hosts: str = "127.0.0.1,localhost,testserver"

    demo_cache_ttl_seconds: int = 600
    sin_reportar_min: int = 60
    log_level: str = "INFO"
    tool_result_max_chars: int = 1500

    @property
    def cors_origins_list(self) -> list[str]:
        return [origen.strip() for origen in self.cors_origins.split(",") if origen.strip()]

    @property
    def allowed_hosts_list(self) -> list[str]:
        return [host.strip() for host in self.allowed_hosts.split(",") if host.strip()]

    @property
    def llm_configurado(self) -> bool:
        return bool(
            self.opencode_api_key
            and self.opencode_api_key.get_secret_value().strip()
        )


@lru_cache
def get_settings() -> Settings:
    """Devuelve la configuración cacheada para no releer el entorno."""
    return Settings()
