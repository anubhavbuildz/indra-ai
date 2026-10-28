"""Authentication endpoint and JWT helper tests."""

from collections.abc import Generator
from datetime import UTC, datetime, timedelta

import jwt
import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.core.errors import AppError
from app.core.security import ALGORITHM, verify_access_token
from app.main import app

TEST_SECRET = "test-signing-secret-with-at-least-32-bytes"


@pytest.fixture
def auth_client() -> Generator[TestClient, None, None]:
    settings = Settings(
        _env_file=None,
        AUTH_USERNAME="test-user",
        AUTH_PASSWORD="test-password",
        JWT_SECRET_KEY=TEST_SECRET,
    )
    app.dependency_overrides[get_settings] = lambda: settings
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.pop(get_settings, None)


def test_login_issues_verifiable_access_token(auth_client: TestClient) -> None:
    response = auth_client.post(
        "/api/v1/auth/login",
        json={"username": "test-user", "password": "test-password"},
    )

    assert response.status_code == 200
    result = response.json()
    assert result["token_type"] == "bearer"
    assert result["expires_in"] == 2 * 60 * 60
    settings = Settings(
        _env_file=None,
        AUTH_USERNAME="test-user",
        AUTH_PASSWORD="test-password",
        JWT_SECRET_KEY=TEST_SECRET,
    )
    assert verify_access_token(result["access_token"], settings)["sub"] == "test-user"


def test_login_rejects_invalid_credentials(auth_client: TestClient) -> None:
    response = auth_client.post(
        "/api/v1/auth/login",
        json={"username": "test-user", "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_credentials"


@pytest.mark.parametrize(
    ("method", "path", "payload"),
    [
        ("get", "/api/v1/assessments", None),
        ("post", "/api/v1/chat", {"message": "Run a security review."}),
        ("get", "/api/v1/rag/status", None),
        ("get", "/api/v1/aws/identity", None),
    ],
)
def test_versioned_routes_reject_missing_bearer_token(
    auth_client: TestClient,
    method: str,
    path: str,
    payload: dict[str, str] | None,
) -> None:
    if payload is None:
        response = getattr(auth_client, method)(path)
    else:
        response = getattr(auth_client, method)(path, json=payload)

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "authentication_required"


def test_protected_route_accepts_login_token(auth_client: TestClient) -> None:
    login_response = auth_client.post(
        "/api/v1/auth/login",
        json={"username": "test-user", "password": "test-password"},
    )
    token = login_response.json()["access_token"]

    response = auth_client.get(
        "/api/v1/rag/status",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert "available" in response.json()


def test_protected_route_rejects_invalid_bearer_token(auth_client: TestClient) -> None:
    response = auth_client.get(
        "/api/v1/rag/status",
        headers={"Authorization": "Bearer not-a-valid-jwt"},
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_token"


def test_openapi_documents_bearer_auth_on_protected_routes(auth_client: TestClient) -> None:
    response = auth_client.get("/openapi.json")

    assert response.status_code == 200
    schema = response.json()
    assert "security" not in schema["paths"]["/api/v1/auth/login"]["post"]
    assert schema["paths"]["/api/v1/chat"]["post"]["security"] == [{"HTTPBearer": []}]


def test_login_reports_missing_configuration() -> None:
    app.dependency_overrides[get_settings] = lambda: Settings(_env_file=None)
    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/auth/login",
                json={"username": "test-user", "password": "test-password"},
            )
    finally:
        app.dependency_overrides.pop(get_settings, None)

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "login_not_configured"


def test_verify_access_token_rejects_expired_token() -> None:
    now = datetime.now(UTC)
    expired_token = jwt.encode(
        {
            "sub": "test-user",
            "iat": now - timedelta(minutes=2),
            "exp": now - timedelta(minutes=1),
        },
        TEST_SECRET,
        algorithm=ALGORITHM,
    )

    with pytest.raises(AppError) as error:
        verify_access_token(
            expired_token,
            Settings(_env_file=None, JWT_SECRET_KEY=TEST_SECRET),
        )

    assert error.value.code == "invalid_token"


def test_jwt_secret_must_be_at_least_32_bytes() -> None:
    with pytest.raises(ValueError, match="at least 32 bytes"):
        Settings(_env_file=None, JWT_SECRET_KEY="too-short")
