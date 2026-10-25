"""Project use cases."""

from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.repositories.project_repository import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    """Project operations independent of HTTP concerns."""

    def __init__(self, session: Session) -> None:
        self.repository = ProjectRepository(session)

    def create(self, project_data: ProjectCreate):
        return self.repository.create(project_data)

    def list(self, limit: int, offset: int):
        return self.repository.list(limit, offset)

    def get(self, project_id: str):
        project = self.repository.get(project_id)
        if project is None:
            raise AppError(404, "project_not_found", "Project was not found.")
        return project

    def update(self, project_id: str, changes: ProjectUpdate):
        project = self.get(project_id)
        if not changes.model_fields_set:
            return project
        return self.repository.update(project, changes)
