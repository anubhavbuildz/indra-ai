"""Chat endpoint workflow response tests."""

import asyncio
from unittest.mock import AsyncMock, Mock

from app.api.routes import chat as chat_route
from app.core.config import Settings
from app.schemas.chat import ChatRequest


def test_chat_endpoint_returns_separate_review_terraform_and_compliance(monkeypatch):
    terraform = 'resource "aws_s3_bucket" "example" {}'
    compliance = "Assessment: encryption and access controls need review."
    review = "Senior-agent review findings."
    agent = Mock()
    agent.__aenter__ = AsyncMock(return_value=agent)
    agent.__aexit__ = AsyncMock(return_value=None)
    for name in ("SeniorAgent", "TerraformAgent", "ComplianceAgent"):
        monkeypatch.setattr(chat_route, name, Mock(return_value=agent))
    monkeypatch.setattr(
        chat_route,
        "RagService",
        Mock(return_value=Mock(query=Mock(return_value={"results": []}))),
    )
    monkeypatch.setattr(
        chat_route,
        "workflow",
        AsyncMock(
            return_value={
                "response": review,
                "terraform": terraform,
                "compliance": compliance,
            }
        ),
    )
    settings = Settings(
        nvidia_api_key="test-key",
        nvidia_base_url="https://example.invalid/v1",
        nvidia_model="test-model",
        nvidia_api_format="openai-chat-completions",
    )

    result = asyncio.run(
        chat_route.chat(ChatRequest(message="Create a secure storage tier"), settings)
    )

    assert result.assistant_response == review
    assert result.terraform == terraform
    assert result.compliance == compliance
