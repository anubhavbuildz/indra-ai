"""Guidance-backed chat endpoint tests."""

import asyncio
from unittest.mock import AsyncMock

from app.api.routes import chat as chat_route
from app.core.config import Settings
from app.schemas.chat import ChatRequest


def test_chat_returns_guidance_answer_and_forwards_history(monkeypatch):
    sources = [{"chunk_id": "aws-guidance-1", "source_title": "Storage guidance"}]
    workflow = AsyncMock(
        return_value={
            "operation_id": "operation-1",
            "cloud_agent_response": {
                "audited_regions": ["us-east-1"],
                "total_issues": 0,
                "critical_count": 0,
                "high_count": 0,
                "medium_count": 0,
                "low_count": 0,
                "findings": [],
            },
            "compliance_agent_response": "Compliance assessment.",
            "senior_agent_response": "Senior review.",
            "sources": sources,
        }
    )
    monkeypatch.setattr(chat_route, "chat_workflow", workflow)

    result = asyncio.run(
        chat_route.chat(
            ChatRequest(
                message="How should I review storage configuration?",
                history=[{"role": "user", "content": "I manage an AWS account."}],
            ),
            Settings(_env_file=None),
        )
    )

    assert result.cloud_agent_response.total_issues == 0
    assert result.compliance_agent_response == "Compliance assessment."
    assert result.senior_agent_response == "Senior review."
    assert result.sources == sources
    assert result.operation_id == "operation-1"
    workflow.assert_awaited_once_with(
        Settings(_env_file=None),
        "How should I review storage configuration?",
        [{"role": "user", "content": "I manage an AWS account."}],
    )
