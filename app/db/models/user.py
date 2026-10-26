"""Infrastructure operation persistence model."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.project import utc_now

if TYPE_CHECKING:
    from app.db.models.project import Project


class User(Base):
    """Project owner account."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    safe_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)
    projects: Mapped[list["Project"]] = relationship("Project", back_populates="owner")
