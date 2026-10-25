"""Project persistence operations."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectRepository:
    """Database operations for projects."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, project_data: ProjectCreate) -> Project:
        project = Project(name=project_data.name, description=project_data.description)
        self.session.add(project)
        self.session.commit()
        self.session.refresh(project)
        return project

    def get(self, project_id: str) -> Project | None:
        return self.session.get(Project, project_id)

    def list(self, limit: int, offset: int) -> list[Project]:
        query = select(Project).order_by(Project.created_at.desc()).limit(limit).offset(offset)
        return list(self.session.scalars(query))

    def update(self, project: Project, changes: ProjectUpdate) -> Project:
        for key, value in changes.model_dump(exclude_unset=True).items():
            setattr(project, key, value)
        self.session.commit()
        self.session.refresh(project)
        return project
