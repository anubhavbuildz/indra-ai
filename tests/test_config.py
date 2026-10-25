"""Configuration behavior tests."""

from app.core.config import Settings


def test_defaults_allow_startup_without_provider_credentials():
    settings = Settings(_env_file=None)

    assert settings.app_name == "Indra API"
    assert settings.database_url == "sqlite:///./data/indra.db"
    assert not settings.nvidia_api_key
    assert not settings.nvidia_base_url
    assert not settings.nvidia_model


def test_credentials_are_not_in_settings_repr():
    settings = Settings(_env_file=None, NVIDIA_API_KEY="unit-test-secret")

    assert "unit-test-secret" not in repr(settings)
