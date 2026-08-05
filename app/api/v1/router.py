from fastapi import APIRouter, HTTPException, status, Depends
from app.models.request import GeneratePersonaRequest, PersonaGenerationResponse
from app.agent.persona_agent import PersonaGenerationAgent
from app.validation.validator import PersonaValidator
from app.core.llm_factory import get_llm

router = APIRouter(tags=["Persona Generation"])


def get_agent_service(payload: GeneratePersonaRequest) -> PersonaGenerationAgent:
    """FastAPI Dependency injecting configured PersonaGenerationAgent."""
    llm = get_llm(provider=payload.provider, model_name=payload.model_name)
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
        201: {"description": "Personas generated successfully.", "model": PersonaGenerationResponse},
        400: {"description": "Invalid input payload."},
        422: {"description": "Unprocessable entity / Pydantic or persona validation error."},
        500: {"description": "LLM generation or upstream API failure."}
    }
)
async def generate_persona_endpoint(
    payload: GeneratePersonaRequest,
    agent: PersonaGenerationAgent = Depends(get_agent_service),
    validator: PersonaValidator = Depends(get_validator_service)
) -> PersonaGenerationResponse:
    """
    REST API Endpoint generating structured synthetic personas.

    - **product_description**: Description of product/service.
    - **target_audience**: Target user segment definition.
    - **research_objective**: Goals and hypothesis for the research.
    - **number_of_personas**: How many unique personas to generate (1-100).
    """
    try:
        personas = await agent.generate_personas(
            product_description=payload.product_description,
            target_audience=payload.target_audience,
            research_objective=payload.research_objective,
            number_of_personas=payload.number_of_personas
        )

        validation_result = await validator.validate_personas(
            personas,
            include_semantic_audit=False
        )

        if not validation_result.is_valid:
            error_messages = [f"{e.field_path}: {e.message}" for e in validation_result.errors]
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Generated persona(s) failed validation checks: {'; '.join(error_messages)}"
            )

        return PersonaGenerationResponse(personas=personas)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate synthetic persona(s): {str(e)}"
        )
