import datetime
from typing import Optional, List, Dict, Any
from app.models.persona import ComprehensivePersona
from app.models.interview import (
    InterviewSessionInfo,
    InterviewMessageRequest,
    InterviewResponse,
    ChatMessagePayload
)
from app.agent.interview_agent import PersonaInterviewAgent
from app.memory.base import BasePersonaMemory
from app.memory.json_memory import memory_service


class InterviewService:
    """
    Service managing multi-turn synthetic user persona interviews,
    session tracking, prompt assembly, and memory persistence.
    """

    def __init__(self, memory: Optional[BasePersonaMemory] = None):
        self.memory = memory or memory_service

    def start_session(
        self,
        persona: ComprehensivePersona,
        session_id: Optional[str] = None,
        product_context: Optional[str] = None
    ) -> InterviewSessionInfo:
        persona_id = persona.basic_info.persona_id or persona.basic_info.full_name.lower().replace(" ", "_")
        effective_session_id = session_id or f"session_{persona_id}"

        raw_history = self.memory.get_history(persona_id=persona_id, session_id=effective_session_id, limit=50)
        formatted_messages = [
            ChatMessagePayload(
                id=f"msg_{i}",
                role=h["role"],
                content=h["content"],
                timestamp=h.get("timestamp")
            )
            for i, h in enumerate(raw_history)
        ]

        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()

        return InterviewSessionInfo(
            interview_id=effective_session_id,
            persona_id=persona_id,
            persona_name=persona.basic_info.full_name,
            product_context=product_context,
            start_timestamp=now_str,
            status="active",
            messages=formatted_messages
        )

    async def process_message(
        self,
        session_id: str,
        payload: InterviewMessageRequest
    ) -> InterviewResponse:
        agent = PersonaInterviewAgent(
            provider=payload.provider or "gemini",
            model_name=payload.model_name,
            memory=self.memory
        )

        response = await agent.conduct_interview(
            persona=payload.persona,
            session_id=session_id,
            user_question=payload.user_question,
            product_context=payload.product_context
        )

        return response

    def get_session(
        self,
        persona_id: str,
        session_id: str
    ) -> InterviewSessionInfo:
        raw_history = self.memory.get_history(persona_id=persona_id, session_id=session_id, limit=100)
        formatted_messages = [
            ChatMessagePayload(
                id=f"msg_{i}",
                role=h["role"],
                content=h["content"],
                timestamp=h.get("timestamp")
            )
            for i, h in enumerate(raw_history)
        ]

        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
        return InterviewSessionInfo(
            interview_id=session_id,
            persona_id=persona_id,
            persona_name=persona_id,
            start_timestamp=now_str,
            status="active",
            messages=formatted_messages
        )


interview_service = InterviewService()
