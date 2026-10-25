"""Chat endpoint response tests for the three-agent Prowler workflow."""

import asyncio
from unittest.mock import AsyncMock

from app.api.routes import chat as chat_route
from app.core.config import Settings
from app.schemas.chat import ChatRequest


def test_chat_returns_prowler_compliance_and_senior_assessments(monkeypatch):
    findings = [{"finding_info": {"title": "Encryption disabled"}}]
    sources = [{"chunk_id": "aws-guidance-1", "source_title": "Storage guidance"}]
    scan_workflow = AsyncMock(
        return_value={
            "operation_id": "operation-1",
            "region": "us-east-1",
            "findings_count": 1,
            "findings": findings,
            "prowler_summary": "Prowler assessment.",
            "compliance": "Evidence-based compliance assessment.",
            "response": "Senior review of both assessments.",
            "sources": sources,
        }
    )
    monkeypatch.setattr(chat_route, "scan_workflow", scan_workflow)

    result = asyncio.run(
        chat_route.chat(
            ChatRequest(
                message="Prioritize the most urgent findings.",
                region="eu-west-1",
                services=["s3", "iam"],
                prowler_args=["--checks", "check-a"],
                history=[{"role": "user", "content": "Check the account."}],
            ),
            Settings(_env_file=None),
        )
    )

    assert result.assistant_response == "Senior review of both assessments."
    assert result.prowler_summary == "Prowler assessment."
    assert result.compliance == "Evidence-based compliance assessment."
    assert result.findings == findings
    assert result.findings_count == 1
    assert result.sources == sources
    scan_workflow.assert_awaited_once()
    assert scan_workflow.await_args.args[1:] == (
        "Prioritize the most urgent findings.",
        [{"role": "user", "content": "Check the account."}],
    )
    assert scan_workflow.await_args.kwargs == {
        "region": "eu-west-1",
        "services": ["s3", "iam"],
        "prowler_args": ["--checks", "check-a"],
    }
