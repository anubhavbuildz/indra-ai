"""Chat endpoint workflow tests."""

import asyncio
from unittest.mock import AsyncMock

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.api.routes import chat as chat_route
from app.core.config import Settings
from app.db.base import Base
from app.db.models.assessment import Assessment
from app.schemas.chat import ChatRequest


def test_chat_returns_review_and_forwards_history(monkeypatch):
    workflow = AsyncMock(
        return_value={
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
            "sources": [],
        }
    )
    monkeypatch.setattr(chat_route, "chat_workflow", workflow)

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    try:
        with Session(engine) as session:
            result = asyncio.run(
                chat_route.chat(
                    ChatRequest(
                        message="How should I review storage configuration?",
                        history=[{"role": "user", "content": "I manage an AWS account."}],
                    ),
                    Settings(_env_file=None),
                    session,
                )
            )
            assessment = session.scalar(
                select(Assessment).where(Assessment.id == result.assessment_id)
            )
            assert assessment is not None
            assert assessment.question == "How should I review storage configuration?"
            assert assessment.senior_review == "Senior review."
            assert assessment.compliance_review == "Compliance assessment."
            assert assessment.audit_report is not None
    finally:
        engine.dispose()

    assert result.cloud_agent_response.total_issues == 0
    assert result.compliance_agent_response == "Compliance assessment."
    assert result.senior_agent_response == "Senior review."
    assert result.sources == []
    assert result.assessment_id
    workflow.assert_awaited_once_with(
        Settings(_env_file=None),
        "How should I review storage configuration?",
        [{"role": "user", "content": "I manage an AWS account."}],
    )
