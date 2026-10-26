"""Assessment use cases."""

from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.db.models.assessment import Assessment
from app.repositories.assessment_repository import AssessmentRepository


class AssessmentService:
    """Assessment operations independent of HTTP concerns."""

    def __init__(self, session: Session) -> None:
        self.repository = AssessmentRepository(session)

    def record_chat(
        self,
        question: str,
        audit_report: dict[str, object],
        compliance_review: str,
        senior_review: str,
    ) -> Assessment:
        return self.repository.create_from_chat(
            question,
            audit_report,
            compliance_review,
            senior_review,
        )

    def list(self, limit: int, offset: int) -> list[Assessment]:
        return self.repository.list(limit, offset)

    def get(self, assessment_id: str) -> Assessment:
        assessment = self.repository.get(assessment_id)
        if assessment is None:
            raise AppError(404, "assessment_not_found", "Assessment was not found.")
        return assessment
