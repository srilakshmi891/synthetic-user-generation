from fastapi import APIRouter, HTTPException, status, Depends
import traceback
from app.models.survey import SurveyRequest, SurveyResponse
from app.agent.survey_agent import PersonaSurveyAgent

router = APIRouter(tags=["Persona Survey"])


def get_survey_agent(payload: SurveyRequest) -> PersonaSurveyAgent:
    """Dependency injecting configured PersonaSurveyAgent."""
    model_name = payload.model_name
    if model_name in (None, "", "string"):
        model_name = None

    return PersonaSurveyAgent(
        provider=payload.provider or "gemini",
        model_name=model_name
    )


@router.post(
    "/survey",
    response_model=SurveyResponse,
    status_code=status.HTTP_200_OK,
    summary="Simultaneous Comparative Persona Survey",
    description="Query multiple synthetic personas simultaneously with 1 or more questions and receive structured side-by-side comparative feedback.",
    responses={
        200: {"description": "Survey completed successfully."},
        400: {"description": "Invalid input request."},
        500: {"description": "Survey execution error."}
    }
)
async def conduct_survey_endpoint(
    payload: SurveyRequest,
    agent: PersonaSurveyAgent = Depends(get_survey_agent)
) -> SurveyResponse:
    try:
        print(f"[SURVEY API] Starting survey across {len(payload.personas)} personas and {len(payload.questions)} questions")
        response = await agent.conduct_survey(
            personas=payload.personas,
            questions=payload.questions,
            product_context=payload.product_context
        )
        print("[SURVEY API] Successfully completed survey")
        return response
    except HTTPException:
        raise
    except Exception as e:
        from app.core.llm_factory import is_quota_or_rate_limit_error
        print("\n========== SURVEY ERROR ==========")
        traceback.print_exc()
        print("==================================\n")
        if is_quota_or_rate_limit_error(e):
            err_msg = "Gemini is temporarily unavailable because the current API quota has been reached. Switch to Mock mode to continue testing."
        else:
            err_msg = f"Survey execution failed: {str(e)}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=err_msg
        )

