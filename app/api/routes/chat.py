"""Chat completion endpoint."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    settings: Annotated[Settings, Depends(get_settings)],
    session: Annotated[Session, Depends(get_db)],
) -> ChatResponse:
    """Run an AWS audit, persist its reviews, and return the assessment."""
    history = [item.model_dump() for item in body.history]
    result = await ChatService(settings, session).run(body.message, history)
    return ChatResponse(
        cloud_agent_response=result.cloud_agent_response,
        compliance_agent_response=result.compliance_agent_response,
        senior_agent_response=result.senior_agent_response,
        sources=result.sources,
        assessment_id=result.assessment_id,
        status="completed",
    )
