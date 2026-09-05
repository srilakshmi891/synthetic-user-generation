from typing import List, Optional
from app.models.persona import ComprehensivePersona
from app.models.insight import (
    PersonaUsageScore,
    SegmentUsageScore,
    AggregateUsageScore,
    InsightResult
)
from app.agent.insight_agent import InsightExtractionAgent


class ProductUsageScoringService:
    """
    Service responsible for calculating individual persona scores (0-10),
    segment-level breakdowns, and aggregate adoption willingness.
    """

    async def calculate_scores(
        self,
        personas: List[ComprehensivePersona],
        product_context: str,
        provider: str = "gemini",
        model_name: Optional[str] = None
    ) -> InsightResult:
        agent = InsightExtractionAgent(provider=provider, model_name=model_name)
        return await agent.extract_insights(
            personas=personas,
            product_context=product_context
        )


product_usage_scoring_service = ProductUsageScoringService()
