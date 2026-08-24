from typing import List, Optional, Literal, Dict
from pydantic import BaseModel, Field
from app.models.persona import ComprehensivePersona

class QuestionAnswerPair(BaseModel):
    question: str
    answer: str

class SurveyPersonaResult(BaseModel):
    persona_id: str
    persona_name: str
    avatar_description: str
    occupation: str
    age: int
    quote: str
    answers: List[QuestionAnswerPair]

class QuestionResult(BaseModel):
    question: str
    responses: List[Dict[str, str]]

class SurveyRequest(BaseModel):
    personas: List[ComprehensivePersona] = Field(..., min_length=1, description="List of personas to survey.")
    questions: List[str] = Field(..., min_length=1, description="One or more survey questions.")
    product_context: Optional[str] = Field(None, description="Optional product context.")
    provider: Optional[Literal["gemini", "openai", "mock"]] = Field("gemini", description="LLM provider.")
    model_name: Optional[str] = Field(None, description="Optional model override.")


class SurveyResponse(BaseModel):
    questions: List[str]
    results: List[SurveyPersonaResult]
