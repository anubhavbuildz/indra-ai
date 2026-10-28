"""INTEGRATION-031/032: real HTTP and SQLite with only workflow boundary replaced."""

from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.services import chat_service


@pytest.fixture
def isolated_client(test_auth_settings):
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)

    def database():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_db] = database
    app.dependency_overrides[get_settings] = lambda: test_auth_settings
    try:
        with TestClient(app) as client:
            login = client.post(
                "/api/v1/auth/login", json={"username": "test-user", "password": "test-password"}
            )
            client.headers["Authorization"] = f"Bearer {login.json()['access_token']}"
            yield client
    finally:
        app.dependency_overrides.pop(get_db, None)
        app.dependency_overrides.pop(get_settings, None)
        engine.dispose()


def test_chat_persists_and_reads(isolated_client, monkeypatch):
    workflow = AsyncMock(
        return_value={
            "cloud_agent_response": {
                "audited_regions": ["us-east-1"],
                "audited_services": ["s3"],
                "total_issues": 0,
                "critical_count": 0,
                "high_count": 0,
                "medium_count": 0,
                "low_count": 0,
                "findings": [],
            },
            "compliance_agent_response": "Synthetic guidance, no certification.",
            "senior_agent_response": "Synthetic review; no real audit evidence.",
            "sources": [],
        }
    )
    monkeypatch.setattr(chat_service, "chat_workflow", workflow)
    response = isolated_client.post("/api/v1/chat", json={"message": "Fixture review"})
    assert response.status_code == 200
    assessment_id = response.json()["assessment_id"]
    saved = isolated_client.get(f"/api/v1/assessments/{assessment_id}")
    assert saved.status_code == 200
    assert saved.json()["senior_review"] == "Synthetic review; no real audit evidence."
    assert isolated_client.get("/api/v1/assessments").json()["items"][0]["id"] == assessment_id
    workflow.assert_awaited_once()


@pytest.mark.parametrize("query", ["limit=0", "limit=101", "offset=-1"])
def test_invalid_pagination(isolated_client, query):
    assert isolated_client.get(f"/api/v1/assessments?{query}").status_code == 422
