from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from app.models.persona import ComprehensivePersona


class GeneratePersonaRequest(BaseModel):
    product_description: str = Field(
        ...,
        min_length=10,
        description="Detailed description of the product or service being researched.",
        example="An AI-powered personal finance mobile app that automates micro-investing and budget tracking."
    )
    target_audience: str = Field(
        ...,
        min_length=5,
        description="Definition of the target user segment or market.",
        example="Gen Z and Millennial young professionals earning $50k-$100k struggling with financial management."
    )
    research_objective: str = Field(
        ...,
        min_length=10,
        description="Primary goal or hypothesis of the research study.",
        example="Understand onboarding friction, security concerns regarding linking bank accounts, and preferred feature priorities."
    )
    number_of_personas: int = Field(
        default=1,
        ge=1,
        le=100,
        description="Number of unique synthetic personas to generate (minimum 1, maximum 100).",
        example=3
    )
    provider: Optional[Literal["gemini", "openai", "mock"]] = Field(
        default="gemini",
        description="LLM provider to use for persona generation."
    )

    model_name: Optional[str] = Field(
        default=None,
        description="Optional model override. Leave empty to use the default model.",
        examples=["gemini-2.5-flash", "gpt-5.5"]

    )


class PersonaGenerationResponse(BaseModel):
    personas: List[ComprehensivePersona] = Field(
        ...,
        description="List of generated synthetic user personas."
    )
