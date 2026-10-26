"""Chat completion endpoint."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.assessment_service import AssessmentService
from app.services.llm.workflow import chat_workflow

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    settings: Annotated[Settings, Depends(get_settings)],
    session: Annotated[Session, Depends(get_db)],
) -> ChatResponse:
    """Run an AWS audit, persist its reviews, and return the assessment."""
    history = [item.model_dump() for item in body.history]
    result = await chat_workflow(
        settings,
        body.message,
        history,
    )
    assessment = AssessmentService(session).record_chat(
        question=body.message,
        audit_report=result["cloud_agent_response"],
        compliance_review=result["compliance_agent_response"],
        senior_review=result["senior_agent_response"],
    )
    return ChatResponse(
        cloud_agent_response=result["cloud_agent_response"],
        compliance_agent_response=result["compliance_agent_response"],
        senior_agent_response=result["senior_agent_response"],
        sources=result["sources"],
        assessment_id=assessment.id,
        status="completed",
    )
