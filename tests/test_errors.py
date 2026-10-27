"""Safe API error response tests."""

from app.core.config import Settings, get_settings


def test_unconfigured_chat_does_not_echo_prompt_or_credentials(client, test_auth_settings):
    secret_prompt = "do-not-echo-this-private-text"
    client.app.dependency_overrides[get_settings] = lambda: Settings(
        _env_file=None,
        AUTH_USERNAME=test_auth_settings.auth_username,
        AUTH_PASSWORD=test_auth_settings.auth_password,
        JWT_SECRET_KEY=test_auth_settings.jwt_secret_key,
    )
    try:
        response = client.post("/api/v1/chat", json={"message": secret_prompt})
    finally:
        client.app.dependency_overrides.pop(get_settings, None)

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "provider_not_configured"
    assert secret_prompt not in response.text
