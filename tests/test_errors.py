"""Safe API error response tests."""


def test_unconfigured_chat_does_not_echo_prompt_or_credentials(client):
    secret_prompt = "do-not-echo-this-private-text"
    response = client.post("/api/v1/chat", json={"message": secret_prompt})

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "provider_not_configured"
    assert secret_prompt not in response.text
