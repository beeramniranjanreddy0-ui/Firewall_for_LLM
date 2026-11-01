from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Adaptive AI Security Firewall"
    environment: str = "development"
    debug: bool = False
    database_url: str = "sqlite:///./firewall.db"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    rate_limit_per_minute: int = 60
    allow_origins: str | None = None

    llm_provider: str = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"

    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"

    gemini_api_key: str | None = None
    gemini_model: str = "gemini-1.5-flash"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        raw_origins = self.allow_origins or self.cors_origins
        return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]


def get_settings() -> Settings:
    return Settings()
