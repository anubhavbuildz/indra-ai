"""Assessment persistence operations."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.assessment import Assessment


class AssessmentRepository:
    """Database operations for completed assessments."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create_from_chat(
        self,
        question: str,
        audit_report: dict[str, object],
        compliance_review: str,
        senior_review: str,
    ) -> Assessment:
        assessment = Assessment(
            name=question[:120],
            description=None,
            status="completed",
            question=question,
            audit_report=audit_report,
            compliance_review=compliance_review,
            senior_review=senior_review,
        )
        self.session.add(assessment)
        self.session.commit()
        self.session.refresh(assessment)
        return assessment

    def get(self, assessment_id: str) -> Assessment | None:
        return self.session.get(Assessment, assessment_id)

    def list(self, limit: int, offset: int) -> list[Assessment]:
        query = (
            select(Assessment).order_by(Assessment.created_at.desc()).limit(limit).offset(offset)
        )
        return list(self.session.scalars(query))
