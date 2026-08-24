from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from app.models.persona import ComprehensivePersona

class ChatMessagePayload(BaseModel):
    id: Optional[str] = None
    role: Literal["user", "assistant"]
    content: str
    timestamp: Optional[str] = None

class InterviewRequest(BaseModel):
    persona: ComprehensivePersona = Field(..., description="The comprehensive synthetic user persona object.")
    session_id: str = Field("default_session", description="Conversation session ID to isolate dialogue state.")
    user_question: str = Field(..., min_length=1, description="Question or prompt asked by the researcher.")
    product_context: Optional[str] = Field(None, description="Optional product or study context.")
    provider: Optional[Literal["gemini", "openai", "mock"]] = Field("gemini", description="AI provider.")
    model_name: Optional[str] = Field(None, description="Model override.")


class InterviewResponse(BaseModel):
    persona_id: str
    session_id: str
    reply: str
    history: List[ChatMessagePayload]

class ClearMemoryRequest(BaseModel):
    persona_id: str
    session_id: str = "default_session"
