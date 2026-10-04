from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Validated configuration loaded only from the process environment or .env file."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: Literal["development", "test", "production"] = "development"
    port: int = Field(default=8000, ge=1, le=65535)
    database_url: PostgresDsn = PostgresDsn(
        "postgresql+asyncpg://wealthbrain:wealthbrain@localhost:5432/wealthbrain"
    )
    default_ai_provider: Literal["fake", "openai", "anthropic", "google"] = "fake"
    default_ai_model: str = Field(default="wealthbrain-test", min_length=1, max_length=200)
    ai_base_url: str = "https://api.openai.com/v1"
    ai_api_key: str | None = None
    ai_timeout_seconds: float = Field(default=30.0, gt=0, le=120)
    default_research_provider: Literal["fake", "http"] = "fake"
    research_search_url: str | None = None
    research_api_key: str | None = None
    research_timeout_seconds: float = Field(default=20.0, gt=0, le=120)
    research_max_response_bytes: int = Field(default=1_000_000, ge=1_024, le=10_000_000)
    research_max_results: int = Field(default=5, ge=1, le=20)
    research_user_agent: str = Field(default="WealthBrainResearch/0.2", min_length=1, max_length=200)
    log_level: str = "INFO"
    cors_origins: list[str] = Field(default_factory=list)

    @field_validator("cors_origins", mode="before")
    @classmethod
    def validate_cors_origins(
        cls, value: list[str] | str, info: ValidationInfo
    ) -> list[str]:
        raw_origins = value.split(",") if isinstance(value, str) else value
        origins = [origin.strip() for origin in raw_origins if origin.strip()]
        if info.data.get("app_env") == "production" and "*" in origins:
            raise ValueError("cors_origins must not contain '*' in production")
        return origins


@lru_cache
def get_settings() -> Settings:
    return Settings()
