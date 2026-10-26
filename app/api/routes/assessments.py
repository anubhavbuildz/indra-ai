"""Read persisted assessment results."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.assessment import AssessmentList, AssessmentRead
from app.services.assessment_service import AssessmentService

router = APIRouter(prefix="/assessments", tags=["assessments"])


@router.get("", response_model=AssessmentList)
def list_assessments(
    session: Annotated[Session, Depends(get_db)],
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> AssessmentList:
    items = AssessmentService(session).list(limit, offset)
    return AssessmentList(items=items, limit=limit, offset=offset)


@router.get("/{assessment_id}", response_model=AssessmentRead)
def get_assessment(
    assessment_id: str,
    session: Annotated[Session, Depends(get_db)],
) -> AssessmentRead:
    return AssessmentService(session).get(assessment_id)
