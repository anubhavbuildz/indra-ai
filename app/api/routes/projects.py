"""Project CRUD endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.project import ProjectCreate, ProjectList, ProjectRead, ProjectUpdate
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(
    body: ProjectCreate, session: Annotated[Session, Depends(get_db)]
) -> ProjectRead:
    return ProjectService(session).create(body)


@router.get("", response_model=ProjectList)
def list_projects(
    session: Annotated[Session, Depends(get_db)],
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> ProjectList:
    items = ProjectService(session).list(limit, offset)
    return ProjectList(items=items, limit=limit, offset=offset)


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project_id: str, session: Annotated[Session, Depends(get_db)]) -> ProjectRead:
    return ProjectService(session).get(project_id)


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: str,
    body: ProjectUpdate,
    session: Annotated[Session, Depends(get_db)],
) -> ProjectRead:
    return ProjectService(session).update(project_id, body)
