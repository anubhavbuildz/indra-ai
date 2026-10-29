"""Configuration behavior tests."""

import pytest

from app.core.config import Settings


def test_defaults_allow_startup_without_provider_credentials(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    settings = Settings(_env_file=None)

    assert settings.app_name == "Indra-AI"
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


def test_env_file_is_loaded_from_project_root(monkeypatch, tmp_path):
    from pydantic_settings.sources import DotEnvSettingsSource

    from app.core.config import PROJECT_ROOT

    def read_environment(source):
        assert source.env_file == PROJECT_ROOT / ".env"
        return {"CORS_ORIGINS": "http://127.0.0.1:5173"}

    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    monkeypatch.setattr(DotEnvSettingsSource, "_read_env_files", read_environment)
    assert Settings().cors_origin_list == ["http://127.0.0.1:5173"]
