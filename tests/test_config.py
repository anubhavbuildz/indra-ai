"""Configuration behavior tests."""

import pytest

from app.core.config import Settings


def test_defaults_allow_startup_without_provider_credentials():
    settings = Settings(_env_file=None)

    assert settings.app_name == "Indra API"
    assert settings.database_url == "sqlite:///./data/indra.db"
    assert not settings.nvidia_api_key
    assert settings.nvidia_base_url == "https://api.tokenfactory.nebius.com/v1"
    assert settings.nvidia_model == "nvidia/Nemotron-3_5-Lightning"
    assert settings.nvidia_api_format == "openai-chat-completions"
    assert settings.inference_timeout_seconds == 120.0
    assert not settings.integrations_ready["nvidia"]


def test_inference_timeout_is_bounded():
    settings = Settings(_env_file=None, INFERENCE_TIMEOUT_SECONDS=240)

    assert settings.inference_timeout_seconds == 240


def test_inference_timeout_rejects_values_above_maximum():
    with pytest.raises(ValueError, match="less than or equal to 600"):
        Settings(_env_file=None, INFERENCE_TIMEOUT_SECONDS=601)


def test_credentials_are_not_in_settings_repr():
    settings = Settings(_env_file=None, NVIDIA_API_KEY="unit-test-secret")

    assert "unit-test-secret" not in repr(settings)
