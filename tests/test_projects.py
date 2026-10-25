"""Project API tests."""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app


@pytest.fixture
def project_client() -> Generator[TestClient, None, None]:
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


def test_create_list_get_and_patch_project(project_client):
    created = project_client.post(
        "/api/v1/projects",
        json={"name": "Demo infrastructure", "description": "Local test project"},
    )

    assert created.status_code == 201, created.text
    project = created.json()
    assert project["name"] == "Demo infrastructure"
    assert project["owner_id"] is None

    listed = project_client.get("/api/v1/projects")
    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()["items"]] == [project["id"]]

    fetched = project_client.get(f"/api/v1/projects/{project['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["id"] == project["id"]

    updated = project_client.patch(f"/api/v1/projects/{project['id']}", json={"status": "archived"})
    assert updated.status_code == 200
    assert updated.json()["status"] == "archived"


def test_missing_project_has_stable_error(project_client):
    response = project_client.get("/api/v1/projects/not-a-project")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "project_not_found"
