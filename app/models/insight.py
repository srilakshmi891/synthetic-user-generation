from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from app.models.persona import ComprehensivePersona


class ThemeItem(BaseModel):
    theme: str = Field(..., description="Theme title, e.g. Price Sensitivity.")
    frequency: int = Field(..., description="Number of personas expressing this theme.")
    percentage: float = Field(..., description="Percentage of analyzed personas expressing this theme (0-100).")
    description: str = Field(..., description="Detailed description of the recurring theme.")
    supporting_personas: List[str] = Field(default_factory=list, description="List of persona names supporting this theme.")


class SentimentBreakdown(BaseModel):
    positive: float = Field(..., description="Percentage of positive sentiment (0-100).")
    neutral: float = Field(..., description="Percentage of neutral sentiment (0-100).")
    negative: float = Field(..., description="Percentage of negative sentiment (0-100).")
    positive_count: int = Field(0, description="Count of positive responses/personas.")
    neutral_count: int = Field(0, description="Count of neutral responses/personas.")
    negative_count: int = Field(0, description="Count of negative responses/personas.")


class AgreementPattern(BaseModel):
    question_or_topic: str = Field(..., description="Question or research topic evaluated.")
    agreement_percentage: float = Field(..., description="Agreement rate percentage (0-100).")
    majority_response: str = Field(..., description="Summary of the majority viewpoint.")
    minority_response: str = Field(..., description="Summary of the minority viewpoint.")
    agreed_personas: List[str] = Field(default_factory=list, description="Personas agreeing with majority.")
    disagreed_personas: List[str] = Field(default_factory=list, description="Personas holding minority or alternative view.")


class BehavioralTrend(BaseModel):
    trend: str = Field(..., description="Short title of the behavioral pattern.")
    frequency: int = Field(..., description="Number of personas exhibiting this behavior.")
    percentage: float = Field(..., description="Percentage of cohort showing this behavior.")
    description: str = Field(..., description="Explanation of the observed behavioral pattern.")
    supporting_personas: List[str] = Field(default_factory=list, description="Names of personas exhibiting this trend.")


class PersonaUsageScore(BaseModel):
    persona_id: str = Field(..., description="Unique persona identifier.")
    persona_name: str = Field(..., description="Full name of persona.")
    score: int = Field(..., ge=0, le=10, description="Product intent/usage score from 0 to 10.")
    decision: str = Field(..., description="Categorical decision, e.g. Definitely would use / Likely to use / Unsure / Unlikely to use.")
    reasoning: str = Field(..., description="Persona reasoning for their score.")
    positive_factors: List[str] = Field(default_factory=list, description="Key features or factors encouraging adoption.")
    negative_factors: List[str] = Field(default_factory=list, description="Key concerns or blockers discouraging adoption.")


class SegmentUsageScore(BaseModel):
    segment_name: str = Field(..., description="Segment grouping name, e.g. Students, Working Professionals.")
    average_score: float = Field(..., description="Average usage score for this segment (0-10).")
    persona_count: int = Field(..., description="Number of personas in this segment.")
    reasoning: str = Field(..., description="Primary reason for this segment's evaluation.")
    personas: List[str] = Field(default_factory=list, description="Names of personas belonging to this segment.")


class AggregateUsageScore(BaseModel):
    overall_score: float = Field(..., description="Average product usage score across all analyzed personas (0-10).")
    total_personas_analyzed: int = Field(..., description="Total number of personas analyzed.")
    percentage_likely_to_use: float = Field(..., description="Percentage of personas with score >= 6.")
    percentage_unlikely_to_use: float = Field(..., description="Percentage of personas with score <= 4.")
    highest_scoring_segment: str = Field("N/A", description="Segment with the highest average score.")
    lowest_scoring_segment: str = Field("N/A", description="Segment with the lowest average score.")
    summary: str = Field(..., description="Executive summary of product usage intent.")


class InterviewTranscriptInput(BaseModel):
    persona_id: str
    persona_name: str
    messages: List[Dict[str, Any]]


class SurveyResponseInput(BaseModel):
    persona_id: str
    persona_name: str
    answers: List[Dict[str, Any]]


class InsightExtractionRequest(BaseModel):
    personas: List[ComprehensivePersona] = Field(..., description="List of synthetic personas to analyze.")
    interview_transcripts: Optional[List[InterviewTranscriptInput]] = Field(None, description="Optional collected interview transcripts.")
    survey_responses: Optional[List[SurveyResponseInput]] = Field(None, description="Optional collected survey responses.")
    product_context: str = Field(..., description="Product description or research objective context.")
    provider: Optional[Literal["gemini", "openai", "mock"]] = Field("gemini", description="LLM provider.")
    model_name: Optional[str] = Field(None, description="Model override.")


class InsightResult(BaseModel):
    summary: str = Field(..., description="High-level synthesis of user research findings.")
    recurring_themes: List[ThemeItem] = Field(default_factory=list)
    sentiment: SentimentBreakdown
    agreement_patterns: List[AgreementPattern] = Field(default_factory=list)
    behavioral_trends: List[BehavioralTrend] = Field(default_factory=list)
    key_findings: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    persona_scores: List[PersonaUsageScore] = Field(default_factory=list)
    aggregate_score: AggregateUsageScore
    segment_scores: List[SegmentUsageScore] = Field(default_factory=list)
