import pytest
from pydantic import ValidationError

from wealthbrain.config.settings import Settings


def test_settings_parse_comma_separated_cors_origins() -> None:
    settings = Settings(cors_origins="https://app.example, http://localhost:3000")

    assert settings.cors_origins == ["https://app.example", "http://localhost:3000"]


def test_settings_reject_wildcard_cors_in_production() -> None:
    with pytest.raises(ValidationError, match="must not contain"):
        Settings(app_env="production", cors_origins="*")
