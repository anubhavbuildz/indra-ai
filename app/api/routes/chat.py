"""Chat completion endpoint."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm.workflow import chat_workflow

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    settings: Annotated[Settings, Depends(get_settings)],
) -> ChatResponse:
    """Audit AWS, summarize the result, and return a senior review."""
    history = [item.model_dump() for item in body.history]
    result = await chat_workflow(
        settings,
        body.message,
        history,
    )
    return ChatResponse(
        cloud_agent_response=result["cloud_agent_response"],
        compliance_agent_response=result["compliance_agent_response"],
        senior_agent_response=result["senior_agent_response"],
        sources=result["sources"],
        operation_id=str(result["operation_id"]),
        status="completed",
    )
