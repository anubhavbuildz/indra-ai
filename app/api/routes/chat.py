"""Chat completion endpoint."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm_service import LLMService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    settings: Annotated[Settings, Depends(get_settings)],
) -> ChatResponse:
    """Return model text and safe action/source placeholders; never execute actions."""
    history = [item.model_dump() for item in body.history]
    answer = await LLMService(settings).complete(body.message, history)
    return ChatResponse(
        assistant_response=answer,
        proposed_actions=[],
        sources=[],
        status="completed",
    )
