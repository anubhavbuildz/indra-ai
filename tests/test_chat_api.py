"""HTTP response contract tests for the chat endpoint."""

from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.services.chat_service import ChatExecution, ChatService


def test_chat_sends_separate_agent_responses_to_frontend(
    client: TestClient,
    monkeypatch,
) -> None:
    execution = ChatExecution(
        cloud_agent_response={
            "audited_regions": ["us-east-1"],
            "audited_services": ["s3"],
            "total_issues": 1,
            "critical_count": 0,
            "high_count": 1,
            "medium_count": 0,
            "low_count": 0,
            "findings": [],
        },
        compliance_agent_response="Compliance summary only.",
        senior_agent_response="Independent Senior review only.",
        sources=[],
        assessment_id="assessment-test-id",
    )
    run = AsyncMock(return_value=execution)
    monkeypatch.setattr(ChatService, "run", run)

    response = client.post(
        "/api/v1/chat",
        json={"message": "Review my AWS account."},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["cloud_agent_response"]["high_count"] == 1
    assert payload["compliance_agent_response"] == "Compliance summary only."
    assert payload["senior_agent_response"] == "Independent Senior review only."
    assert payload["assessment_id"] == "assessment-test-id"
    assert "cloud_agent_response" in payload
    assert "compliance_agent_response" in payload
    assert "senior_agent_response" in payload
