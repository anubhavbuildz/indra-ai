"""Chat endpoint Prowler workflow tests."""

import asyncio
from unittest.mock import AsyncMock

from app.api.routes import chat as chat_route
from app.core.config import Settings
from app.schemas.chat import ChatRequest


def test_chat_runs_scan_and_passes_question_and_history_to_agent(monkeypatch):
    findings = [{"finding_info": {"title": "Encryption disabled"}}]
    scan_workflow = AsyncMock(
        return_value={
            "operation_id": "operation-1",
            "region": "us-east-1",
            "findings": findings,
            "findings_count": 1,
            "prowler_summary": "Scan summary.",
            "compliance": "Assessment.",
            "response": "Senior review.",
            "sources": [],
        }
    )
    monkeypatch.setattr(chat_route, "scan_workflow", scan_workflow)

    result = asyncio.run(
        chat_route.chat(
            ChatRequest(
                message="Prioritize the most urgent findings.",
                history=[{"role": "user", "content": "Check the account."}],
            ),
            Settings(_env_file=None),
        )
    )

    assert result.assistant_response == "Senior review."
    assert result.findings == findings
    assert result.findings_count == 1
    assert scan_workflow.await_args.args[1:] == (
        "Prioritize the most urgent findings.",
        [{"role": "user", "content": "Check the account."}],
    )
