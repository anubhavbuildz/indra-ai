"""Shared OpenAI client behavior tests."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import pytest
from openai import APIConnectionError, AuthenticationError, RateLimitError

from app.core.config import Settings
from app.core.errors import AppError
from app.services.llm.base import BaseLLM
from app.services.llm.compliance_agent import ComplianceAgent
from app.services.llm.orchestrator import review_scan
from app.services.llm.prowler_agent import ProwlerAgent
from app.services.llm.role_prompts import load_role_prompt
from app.services.llm.senior_agent import SENIOR_MODEL, SeniorAgent
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
        max_completion_tokens=8192,
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


def test_prowler_and_compliance_agents_inherit_from_shared_base():
    assert issubclass(ProwlerAgent, BaseLLM)
    assert issubclass(ComplianceAgent, BaseLLM)
    assert issubclass(SeniorAgent, BaseLLM)
    assert issubclass(LLMService, BaseLLM)


def test_role_prompts_load_from_markdown_and_report_missing_sections():
    assert "Prowler findings assistant" in load_role_prompt("prowler_role.md")
    assert "NIST Cybersecurity Framework" in load_role_prompt("compliance_role.md")
    assert "Review both the Prowler assessment" in load_role_prompt("senior_role.md")
    with pytest.raises(ValueError, match="Prompt section 'Missing' is missing"):
        load_role_prompt("prowler_role.md", "Missing")


def test_prowler_agent_summarizes_untrusted_json_findings():
    client = mock_client("Prioritized findings")
    agent = ProwlerAgent(configured_settings(), client=client)

    response = asyncio.run(
        agent.summarize(
            [{"check_id": "s3-encryption", "status": "FAIL"}],
            "us-east-1",
            question="What should I fix first?",
            history=[{"role": "user", "content": "Scan the account."}],
        )
    )

    assert response == "Prioritized findings"
    messages = client.chat.completions.create.call_args.kwargs["messages"]
    assert "Prioritize failed checks by severity" in messages[0]["content"]
    assert "untrusted data" in messages[2]["content"][0]["text"]
    assert "s3-encryption" in messages[2]["content"][0]["text"]
    assert "What should I fix first?" in messages[2]["content"][0]["text"]
    assert messages[1]["role"] == "user"


def test_prowler_agent_summarizes_findings_in_one_call():
    client = mock_client("Summary.")
    agent = ProwlerAgent(configured_settings(), client=client)

    response = asyncio.run(
        agent.summarize(
            [
                {"check_id": "first-check"},
                {"check_id": "second-check"},
            ],
            "us-east-1",
        )
    )

    assert response == "Summary."
    client.chat.completions.create.assert_awaited_once()
    prompt = client.chat.completions.create.call_args.kwargs["messages"][1]["content"][0]["text"]
    assert "first-check" in prompt
    assert "second-check" in prompt


def test_prowler_agent_runs_scanner_tool(monkeypatch):
    scan_result = {
        "operation_id": "operation-1",
        "region": "eu-west-1",
        "findings": [],
        "findings_count": 0,
    }
    run_scan = AsyncMock(return_value=scan_result)
    monkeypatch.setattr("app.services.llm.prowler_agent.Scanner.run_scan", run_scan)
    agent = ProwlerAgent(configured_settings())

    response = asyncio.run(
        agent.run_scan(
            region="eu-west-1",
            services=["s3"],
            prowler_args=["--checks", "check-a"],
        )
    )

    assert response == scan_result
    run_scan.assert_awaited_once()
    assert run_scan.await_args.kwargs == {
        "region": "eu-west-1",
        "services": ["s3"],
        "prowler_args": ["--checks", "check-a"],
    }


def test_compliance_agent_includes_sources_and_non_certification_prompt():
    client = mock_client("Evidence-limited assessment")
    agent = ComplianceAgent(configured_settings(), client=client)

    response = asyncio.run(
        agent.review(
            "An S3 bucket",
            [{"chunk_id": "source-1", "source_title": "Storage guidance"}],
        )
    )

    assert response == "Evidence-limited assessment"
    sent_messages = client.chat.completions.create.call_args.kwargs["messages"]
    assert "source-1" in sent_messages[1]["content"][0]["text"]
    assert "NIST Cybersecurity Framework" in sent_messages[0]["content"]
    assert "NIST Privacy Framework" in sent_messages[0]["content"]
    assert "least privilege" in sent_messages[0]["content"]
    assert "not a formal control mapping" in sent_messages[0]["content"]
    assert "not a certification" in sent_messages[0]["content"]


def test_senior_agent_reviews_both_agent_assessments_and_sources():
    client = mock_client("Senior cross-check")
    agent = SeniorAgent(configured_settings(), client=client)

    response = asyncio.run(
        agent.review_prowler(
            question="What needs attention?",
            region="us-west-2",
            prowler_summary="Prowler found an exposed resource.",
            compliance="Guidance source-1 recommends restricting access.",
            sources=[{"chunk_id": "source-1", "source_title": "AWS guidance"}],
        )
    )

    messages = client.chat.completions.create.call_args.kwargs["messages"]
    assert response == "Senior cross-check"
    assert client.chat.completions.create.call_args.kwargs["model"] == SENIOR_MODEL
    assert "Prowler found an exposed resource." in messages[1]["content"][0]["text"]
    assert "Guidance source-1 recommends restricting access." in messages[1]["content"][0]["text"]
    assert "source-1" in messages[1]["content"][0]["text"]


def test_review_scan_runs_prowler_and_compliance_in_parallel_then_senior_review():
    events: set[str] = set()
    both_agents_started = asyncio.Event()

    prowler_agent = Mock()
    compliance_agent = Mock()
    senior_agent = Mock()

    async def prowler_review(**kwargs):
        events.add("prowler")
        if events == {"prowler", "compliance"}:
            both_agents_started.set()
        await asyncio.wait_for(both_agents_started.wait(), timeout=1)
        assert '"check-1"' in kwargs["query"]
        return "Prowler summary."

    async def compliance_review(*, infrastructure, sources):
        events.add("compliance")
        if events == {"prowler", "compliance"}:
            both_agents_started.set()
        await asyncio.wait_for(both_agents_started.wait(), timeout=1)
        assert '"check-1"' in infrastructure
        return "Compliance assessment."

    async def senior_review(**kwargs):
        assert kwargs["prowler_summary"] == "Prowler summary."
        assert kwargs["compliance"] == "Compliance assessment."
        assert events == {"prowler", "compliance"}
        return "Senior review."

    prowler_agent.review = AsyncMock(side_effect=prowler_review)
    compliance_agent.review = AsyncMock(side_effect=compliance_review)
    senior_agent.review_prowler = AsyncMock(side_effect=senior_review)
    sources = [{"chunk_id": "source-1", "source_title": "AWS guidance"}]

    result = asyncio.run(
        review_scan(
            prowler_agent,
            compliance_agent,
            senior_agent,
            [{"check_id": "check-1"}],
            "us-east-1",
            sources,
            "Review this scan.",
        )
    )

    assert result == (
        "Prowler summary.",
        "Compliance assessment.",
        "Senior review.",
    )
    assert events == {"prowler", "compliance"}
    prowler_agent.review.assert_awaited_once()
    compliance_agent.review.assert_awaited_once()
