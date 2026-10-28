"""Shared OpenAI client and guidance agent behavior tests."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import pytest
from openai import APIConnectionError, APITimeoutError, AuthenticationError, RateLimitError

from app.core.config import Settings
from app.core.errors import AppError
from app.schemas.audit_schema import AuditReport
from app.services.llm.base import BaseLLM
from app.services.llm.compliance_agent import ComplianceAgent
from app.services.llm.role_prompts import load_role_prompt
from app.services.llm_service import LLMService


def configured_settings() -> Settings:
    return Settings(
        _env_file=None,
        NVIDIA_API_KEY="test-secret",
        NVIDIA_BASE_URL="https://provider.invalid/v1",
        NVIDIA_MODEL="developer-selected-model",
        NVIDIA_API_FORMAT="openai-chat-completions",
    )


def mock_client(content: str | None = "completion") -> Mock:
    response = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content))])
    client = Mock()
    client.chat.completions.create = AsyncMock(return_value=response)
    client.close = AsyncMock()
    return client


def test_missing_provider_settings_fail_clearly():
    with pytest.raises(AppError) as error:
        asyncio.run(LLMService(Settings(_env_file=None)).complete("hello"))

    assert error.value.code == "provider_not_configured"


def test_nebius_provider_defaults():
    settings = Settings(_env_file=None)

    assert settings.nvidia_base_url == "https://api.tokenfactory.nebius.com/v1"
    assert settings.nvidia_model == "nvidia/Nemotron-3_5-Lightning"
    assert settings.nvidia_api_format == "openai-chat-completions"
    assert settings.inference_timeout_seconds == 120.0


def test_client_is_created_from_settings_without_default_endpoint():
    settings = configured_settings()

    with patch("app.services.llm.base.AsyncOpenAI") as openai_client:
        llm = BaseLLM(settings, timeout_seconds=12.0)
        client = llm.client

    assert client is openai_client.return_value
    assert openai_client.call_args.kwargs == {
        "api_key": "test-secret",
        "base_url": "https://provider.invalid/v1",
        "timeout": 12.0,
        "max_retries": 0,
    }


def test_client_uses_configured_inference_timeout():
    settings = configured_settings()
    settings.inference_timeout_seconds = 180.0

    with patch("app.services.llm.base.AsyncOpenAI") as openai_client:
        client = BaseLLM(settings).client

    assert client is openai_client.return_value
    assert openai_client.call_args.kwargs["timeout"] == 180.0


def test_completion_uses_shared_client_model_and_conversation():
    client = mock_client()
    llm = BaseLLM(configured_settings(), client=client)

    response = asyncio.run(
        llm.complete(
            "What next?",
            [{"role": "assistant", "content": "Ready."}],
            system_prompt="You are the base agent.",
        )
    )

    assert response == "completion"
    client.chat.completions.create.assert_awaited_once_with(
        model="developer-selected-model",
        temperature=0.6,
        max_completion_tokens=2048,
        messages=[
            {"role": "system", "content": "You are the base agent."},
            {"role": "assistant", "content": "Ready."},
            {"role": "user", "content": [{"type": "text", "text": "What next?"}]},
        ],
    )


@pytest.mark.parametrize(
    ("provider_error", "expected_code"),
    [
        (
            APITimeoutError(request=Mock()),
            "provider_timeout",
        ),
        (
            AuthenticationError(
                "private provider detail",
                response=Mock(status_code=401, request=Mock(), headers={}),
                body=None,
            ),
            "provider_auth_error",
        ),
        (
            RateLimitError(
                "private provider detail",
                response=Mock(status_code=429, request=Mock(), headers={}),
                body=None,
            ),
            "provider_rate_limited",
        ),
        (
            APIConnectionError(message="private provider detail", request=Mock()),
            "provider_unavailable",
        ),
    ],
)
def test_provider_errors_are_mapped_without_details(provider_error, expected_code):
    client = mock_client()
    client.chat.completions.create.side_effect = provider_error
    llm = BaseLLM(configured_settings(), client=client)

    with pytest.raises(AppError) as error:
        asyncio.run(llm.complete("private prompt"))

    assert error.value.code == expected_code
    assert "private provider detail" not in error.value.message


def test_malformed_provider_response_is_safe():
    client = mock_client(content=None)
    llm = BaseLLM(configured_settings(), client=client)

    with pytest.raises(AppError) as error:
        asyncio.run(llm.complete("private prompt"))

    assert error.value.code == "provider_invalid_response"


def test_compliance_agent_summarizes_audit_report_and_history():
    client = mock_client("Evidence-limited answer")
    agent = ComplianceAgent(configured_settings(), client=client)
    audit_report = AuditReport(
        audited_regions=["us-east-1"],
        total_issues=1,
        critical_count=1,
        high_count=0,
        medium_count=0,
        low_count=0,
        findings=[
            {
                "service": "ec2",
                "region": "us-east-1",
                "resource": "sg-123",
                "severity": "CRITICAL",
                "title": "SSH Open to Internet",
            }
        ],
    )

    response = asyncio.run(
        agent.review(
            question="What should I prioritize?",
            audit_result=audit_report,
            history=[{"role": "user", "content": "I use AWS."}],
        )
    )

    assert response == "Evidence-limited answer"
    sent_messages = client.chat.completions.create.call_args.kwargs["messages"]
    assert "SSH Open to Internet" in sent_messages[2]["content"][0]["text"]
    assert "no more than 5 bullets" in sent_messages[2]["content"][0]["text"]
    assert sent_messages[1] == {"role": "user", "content": "I use AWS."}
    assert "compliance summarizer" in sent_messages[0]["content"]
    assert "not a certification" in sent_messages[0]["content"]


def test_compliance_role_prompt_loads_from_markdown():
    assert "compliance summarizer" in load_role_prompt("compliance_role.md")
