from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, field_validator, model_validator
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
    log_level: str = "INFO"
    cors_origins: list[str] = Field(default_factory=list)

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        """Accept a comma-separated environment variable without weakening production CORS."""
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @model_validator(mode="after")
    def forbid_wildcard_production_cors(self) -> "Settings":
        if self.app_env == "production" and "*" in self.cors_origins:
            raise ValueError("CORS_ORIGINS must not contain '*' in production")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
