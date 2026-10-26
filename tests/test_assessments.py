"""Assessment result API tests."""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.models.assessment import Assessment
from app.db.session import get_db
from app.main import app


@pytest.fixture
def assessment_client() -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False)

    def override_db() -> Generator[Session, None, None]:
        session = factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_db
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.pop(get_db, None)
        engine.dispose()


def test_list_and_read_assessments_with_senior_review(assessment_client: TestClient) -> None:
    session_dependency = app.dependency_overrides[get_db]
    session_generator = session_dependency()
    session = next(session_generator)
    assessment = Assessment(
        name="AWS account security review",
        question="Review this AWS account",
        audit_report={"total_issues": 1},
        compliance_review="Compliance review.",
        senior_review="Senior review output.",
        status="completed",
    )
    session.add(assessment)
    session.commit()
    assessment_id = assessment.id
    session_generator.close()

    listed = assessment_client.get("/api/v1/assessments")
    assert listed.status_code == 200
    assert listed.json()["items"][0]["id"] == assessment_id
    assert listed.json()["items"][0]["senior_review"] == "Senior review output."

    fetched = assessment_client.get(f"/api/v1/assessments/{assessment_id}")
    assert fetched.status_code == 200
    assert fetched.json()["question"] == "Review this AWS account"


def test_missing_assessment_has_stable_error(assessment_client: TestClient) -> None:
    response = assessment_client.get("/api/v1/assessments/not-an-assessment")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "assessment_not_found"
