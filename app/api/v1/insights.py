from fastapi import APIRouter, HTTPException, status
import traceback
from app.models.insight import InsightExtractionRequest, InsightResult
from app.services.insight_extraction_service import insight_extraction_service
from app.services.product_usage_scoring_service import product_usage_scoring_service

router = APIRouter(prefix="/insights", tags=["Research Insights & Product Scoring"])


@router.post(
    "/extract",
    response_model=InsightResult,
    status_code=status.HTTP_200_OK,
    summary="Extract Research Insights & Product Usage Scores",
    description=(
        "Analyzes persona profiles, interview transcripts, and survey responses to produce "
        "recurring themes, sentiment breakdown, agreement patterns, behavioral trends, "
        "and persona-level / segment-level / aggregate product adoption scores (0-10)."
    )
)
async def extract_insights_endpoint(payload: InsightExtractionRequest) -> InsightResult:
    try:
        print(f"[INSIGHTS API] Extracting research insights for {len(payload.personas)} personas | Domain: {payload.product_context[:50]}")
        result = await insight_extraction_service.extract_insights(payload)
        print("[INSIGHTS API] Successfully synthesized research insights & scores.")
        return result
    except HTTPException:
        raise
    except Exception as e:
        from app.core.llm_factory import is_quota_or_rate_limit_error
        print("\n========== INSIGHT EXTRACTION ERROR ==========")
        traceback.print_exc()
        print("==============================================\n")
        if is_quota_or_rate_limit_error(e):
            err_msg = "Gemini API quota reached. Switch to Mock mode to continue testing."
        else:
            err_msg = f"Insight extraction failed: {str(e)}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=err_msg
        )


@router.post(
    "/scoring",
    response_model=InsightResult,
    status_code=status.HTTP_200_OK,
    summary="Compute 'Would Use This Product?' Intent Scores",
    description="Generates individual persona, segment, and aggregate product intent scores (0-10)."
)
async def calculate_scoring_endpoint(payload: InsightExtractionRequest) -> InsightResult:
    try:
        return await product_usage_scoring_service.calculate_scores(
            personas=payload.personas,
            product_context=payload.product_context,
            provider=payload.provider or "gemini",
            model_name=payload.model_name
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Product usage scoring failed: {str(e)}"
        )
