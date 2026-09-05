from typing import Optional, List
from app.models.insight import (
    InsightExtractionRequest,
    InsightResult,
    AggregateUsageScore,
    PersonaUsageScore,
    SegmentUsageScore
)
from app.agent.insight_agent import InsightExtractionAgent
from app.core.llm_factory import get_llm


class InsightExtractionService:
    """
    Service coordinating research insight synthesis, sentiment classification,
    recurring theme clustering, agreement pattern mapping, and usage intent scoring.
    """

    async def extract_insights(self, payload: InsightExtractionRequest) -> InsightResult:
        agent = InsightExtractionAgent(
            provider=payload.provider or "gemini",
            model_name=payload.model_name
        )

        return await agent.extract_insights(
            personas=payload.personas,
            product_context=payload.product_context,
            interview_transcripts=payload.interview_transcripts,
            survey_responses=payload.survey_responses
        )


insight_extraction_service = InsightExtractionService()
