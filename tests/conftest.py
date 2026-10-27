"""Shared test fixtures."""

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.main import app

TEST_JWT_SECRET = "test-signing-secret-with-at-least-32-bytes"


@pytest.fixture
def test_auth_settings() -> Settings:
    return Settings(
        _env_file=None,
        AUTH_USERNAME="test-user",
        AUTH_PASSWORD="test-password",
        JWT_SECRET_KEY=TEST_JWT_SECRET,
    )


@pytest.fixture
def client(test_auth_settings: Settings):
    """Create a test client authenticated with a test-only bearer token."""
    app.dependency_overrides[get_settings] = lambda: test_auth_settings
    try:
        with TestClient(app) as test_client:
            response = test_client.post(
                "/api/v1/auth/login",
                json={"username": "test-user", "password": "test-password"},
            )
            test_client.headers["Authorization"] = f"Bearer {response.json()['access_token']}"
            yield test_client
    finally:
        app.dependency_overrides.pop(get_settings, None)
