"""Chat workflow orchestration and assessment persistence."""

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.core.config import Settings
from app.services.assessment_service import AssessmentService
from app.services.llm.workflow import chat_workflow


@dataclass(frozen=True)
class ChatExecution:
    """Completed workflow output and persisted assessment identifier."""

    cloud_agent_response: dict[str, object]
    compliance_agent_response: str
    senior_agent_response: str
    sources: list[dict[str, str]]
    assessment_id: str


class ChatService:
    """Use-case service for running and persisting a chat review."""

    def __init__(self, settings: Settings, session: Session) -> None:
        self.settings = settings
        self.session = session

    async def run(
        self,
        question: str,
        history: list[dict[str, str]] | None = None,
    ) -> ChatExecution:
        """Run the agent workflow, persist its completed results, and return them."""
        result = await chat_workflow(self.settings, question, history)
        assessment = AssessmentService(self.session).record_chat(
            question=question,
            audit_report=result["cloud_agent_response"],
            compliance_review=result["compliance_agent_response"],
            senior_review=result["senior_agent_response"],
        )
        return ChatExecution(
            cloud_agent_response=result["cloud_agent_response"],
            compliance_agent_response=result["compliance_agent_response"],
            senior_agent_response=result["senior_agent_response"],
            sources=result["sources"],
            assessment_id=assessment.id,
        )
