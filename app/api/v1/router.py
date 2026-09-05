from fastapi import APIRouter, HTTPException, status, Depends
import traceback

from app.models.request import GeneratePersonaRequest, PersonaGenerationResponse
from app.agent.persona_agent import PersonaGenerationAgent
from app.validation.validator import PersonaValidator
from app.core.llm_factory import get_llm

from app.api.v1.interview import router as interview_router
from app.api.v1.survey import router as survey_router
from app.api.v1.insights import router as insights_router

router = APIRouter()
router.include_router(interview_router)
router.include_router(survey_router)
router.include_router(insights_router)



def get_agent_service(payload: GeneratePersonaRequest) -> PersonaGenerationAgent:
    """FastAPI Dependency injecting configured PersonaGenerationAgent."""

    model_name = payload.model_name

    # Ignore Swagger's default placeholder
    if model_name in (None, "", "string"):
        model_name = None

    llm = get_llm(
        provider=payload.provider,
        model_name=model_name,
    )

    return PersonaGenerationAgent(llm=llm)


def get_validator_service(payload: GeneratePersonaRequest) -> PersonaValidator:
    """FastAPI Dependency injecting PersonaValidator."""
    return PersonaValidator(llm_provider=payload.provider)


@router.post(
    "/generate-persona",
    response_model=PersonaGenerationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate Synthetic User Personas",
    description=(
        "Generates one or more structured multi-dimensional synthetic user personas "
        "given product details, target audience, research objective, and number_of_personas (1-100)."
    ),
    responses={
        201: {
            "description": "Personas generated successfully.",
            "model": PersonaGenerationResponse,
        },
        400: {"description": "Invalid input payload."},
        422: {"description": "Unprocessable entity / Persona validation error."},
        500: {"description": "LLM generation failure."},
    },
)
async def generate_persona_endpoint(
    payload: GeneratePersonaRequest,
    agent: PersonaGenerationAgent = Depends(get_agent_service),
    validator: PersonaValidator = Depends(get_validator_service),
) -> PersonaGenerationResponse:
    """
    Generate synthetic personas.
    """

    try:
        print("========== START PERSONA GENERATION ==========")
        print(f"Provider: {payload.provider}")
        print(f"Model: {payload.model_name}")
        print(f"Personas: {payload.number_of_personas}")

        personas = await agent.generate_personas(
            product_description=payload.product_description,
            target_audience=payload.target_audience,
            research_objective=payload.research_objective,
            number_of_personas=payload.number_of_personas,
        )

        print("[SUCCESS] Persona generation completed")

        validation_result = await validator.validate_personas(
            personas,
            include_semantic_audit=False,
        )

        if not validation_result.is_valid:
            error_messages = [
                f"{err.field_path}: {err.message}"
                for err in validation_result.errors
            ]

            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="; ".join(error_messages),
            )

        print("[SUCCESS] Validation completed")
        print("========== SUCCESS ==========")

        return PersonaGenerationResponse(personas=personas)

    except HTTPException:
        raise

    except Exception as e:
        from app.core.llm_factory import is_quota_or_rate_limit_error
        print("\n========== ERROR ==========")
        traceback.print_exc()
        print("===========================\n")

        if is_quota_or_rate_limit_error(e):
            err_msg = "Gemini is temporarily unavailable because the current API quota has been reached. Switch to Mock mode to continue testing."
        else:
            err_msg = f"Persona generation failed: {str(e)}"

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=err_msg,
        )

