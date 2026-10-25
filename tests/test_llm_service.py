"""NVIDIA provider adapter tests."""

import asyncio
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from app.core.config import Settings
from app.core.errors import AppError
from app.services.llm_service import LLMService


def test_missing_provider_settings_fail_clearly():
    with pytest.raises(AppError) as error:
        asyncio.run(LLMService(Settings(_env_file=None)).complete("hello", []))
    assert error.value.code == "provider_not_configured"


def test_provider_auth_error_does_not_leak_key():
    settings = Settings(
        _env_file=None,
        NVIDIA_API_KEY="test-secret",
        NVIDIA_BASE_URL="https://provider.invalid/request",
        NVIDIA_MODEL="test-model",
        NVIDIA_API_FORMAT="openai-chat-completions",
    )
    response = httpx.Response(401, request=httpx.Request("POST", settings.nvidia_base_url))
    client = AsyncMock()
    client.post.return_value = response

    with patch("app.services.llm_service.httpx.AsyncClient") as client_class:
        client_class.return_value.__aenter__.return_value = client
        with pytest.raises(AppError) as error:
            asyncio.run(LLMService(settings).complete("private prompt", []))
        assert error.value.code == "provider_auth_error"
        assert "test-secret" not in error.value.message
        assert client.post.call_args.kwargs["headers"]["Authorization"] == "Bearer test-secret"

    client.post.assert_awaited_once()


def test_malformed_provider_payload_is_safe():
    settings = Settings(
        _env_file=None,
        NVIDIA_API_KEY="test-secret",
        NVIDIA_BASE_URL="https://provider.invalid/request",
        NVIDIA_MODEL="test-model",
        NVIDIA_API_FORMAT="openai-chat-completions",
    )
    response = httpx.Response(
        200,
        json={"unexpected": "payload"},
        request=httpx.Request("POST", settings.nvidia_base_url),
    )
    client = AsyncMock()
    client.post.return_value = response

    with patch("app.services.llm_service.httpx.AsyncClient") as client_class:
        client_class.return_value.__aenter__.return_value = client
        with pytest.raises(AppError) as error:
            asyncio.run(LLMService(settings).complete("private prompt", []))
        assert error.value.code == "provider_invalid_response"


def test_provider_rate_limit_is_reported_without_response_body():
    settings = Settings(
        _env_file=None,
        NVIDIA_API_KEY="test-secret",
        NVIDIA_BASE_URL="https://provider.invalid/request",
        NVIDIA_MODEL="test-model",
        NVIDIA_API_FORMAT="openai-chat-completions",
    )
    response = httpx.Response(
        429,
        text="private provider details",
        request=httpx.Request("POST", settings.nvidia_base_url),
    )
    client = AsyncMock()
    client.post.return_value = response

    with patch("app.services.llm_service.httpx.AsyncClient") as client_class:
        client_class.return_value.__aenter__.return_value = client
        with pytest.raises(AppError) as error:
            asyncio.run(LLMService(settings).complete("private prompt", []))

    assert error.value.code == "provider_rate_limited"
    assert "private provider details" not in error.value.message


def test_network_failure_is_reported_safely():
    settings = Settings(
        _env_file=None,
        NVIDIA_API_KEY="test-secret",
        NVIDIA_BASE_URL="https://provider.invalid/request",
        NVIDIA_MODEL="test-model",
        NVIDIA_API_FORMAT="openai-chat-completions",
    )
    client = AsyncMock()
    client.post.side_effect = httpx.ConnectError(
        "private network detail", request=httpx.Request("POST", settings.nvidia_base_url)
    )

    with patch("app.services.llm_service.httpx.AsyncClient") as client_class:
        client_class.return_value.__aenter__.return_value = client
        with pytest.raises(AppError) as error:
            asyncio.run(LLMService(settings).complete("private prompt", []))

    assert error.value.code == "provider_unavailable"
    assert "private network detail" not in error.value.message
