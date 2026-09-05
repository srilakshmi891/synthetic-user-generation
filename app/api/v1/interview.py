from fastapi import APIRouter, HTTPException, status, Depends, Query
import traceback
from typing import Optional

from app.models.interview import (
    InterviewRequest,
    InterviewResponse,
    ClearMemoryRequest,
    StartInterviewRequest,
    InterviewSessionInfo,
    InterviewMessageRequest
)
from app.agent.interview_agent import PersonaInterviewAgent
from app.services.interview_service import interview_service
from app.memory.json_memory import memory_service

router = APIRouter(tags=["Persona Interview"])


def get_interview_agent(payload: InterviewRequest) -> PersonaInterviewAgent:
    """Dependency injecting configured PersonaInterviewAgent."""
    model_name = payload.model_name
    if model_name in (None, "", "string"):
        model_name = None

    return PersonaInterviewAgent(
        provider=payload.provider or "gemini",
        model_name=model_name,
        memory=memory_service
    )


# --- EXISTING ENDPOINTS (PRESERVED) ---

@router.post(
    "/interview",
    response_model=InterviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Interactive Multi-Turn Persona Interview",
    description="Conduct multi-turn conversations with a synthetic user persona. Retains conversation history and personality consistency.",
    responses={
        200: {"description": "Interview reply generated successfully."},
        400: {"description": "Invalid input request."},
        500: {"description": "Interview generation error."}
    }
)
async def conduct_interview_endpoint(
    payload: InterviewRequest,
    agent: PersonaInterviewAgent = Depends(get_interview_agent)
) -> InterviewResponse:
    try:
        print(f"[INTERVIEW API] Starting turn for persona: {payload.persona.basic_info.full_name} | Session: {payload.session_id}")
        response = await agent.conduct_interview(
            persona=payload.persona,
            session_id=payload.session_id,
            user_question=payload.user_question,
            product_context=payload.product_context
        )
        print(f"[INTERVIEW API] Successfully generated reply for persona: {payload.persona.basic_info.full_name}")
        return response
    except HTTPException:
        raise
    except Exception as e:
        from app.core.llm_factory import is_quota_or_rate_limit_error
        print("\n========== INTERVIEW ERROR ==========")
        traceback.print_exc()
        print("=====================================\n")
        if is_quota_or_rate_limit_error(e):
            err_msg = "Gemini is temporarily unavailable because the current API quota has been reached. Switch to Mock mode to continue testing."
        else:
            err_msg = f"Interview generation failed: {str(e)}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=err_msg
        )


@router.post(
    "/interview/clear",
    status_code=status.HTTP_200_OK,
    summary="Clear Persona Conversation Memory",
    description="Resets the conversation history for a specific persona and session ID."
)
async def clear_interview_memory_endpoint(payload: ClearMemoryRequest):
    try:
        success = memory_service.clear_memory(
            persona_id=payload.persona_id,
            session_id=payload.session_id
        )
        return {"status": "success", "cleared": success, "persona_id": payload.persona_id, "session_id": payload.session_id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# --- NEW MILESTONE 3 REST INTERVIEW SESSION ENDPOINTS ---

@router.post(
    "/interviews/start",
    response_model=InterviewSessionInfo,
    status_code=status.HTTP_201_CREATED,
    summary="Start an Interview Session",
    description="Initializes a structured interview session for a synthetic user persona."
)
async def start_interview_endpoint(payload: StartInterviewRequest) -> InterviewSessionInfo:
    try:
        return interview_service.start_session(
            persona=payload.persona,
            session_id=payload.session_id,
            product_context=payload.product_context
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start interview session: {str(e)}"
        )


@router.post(
    "/interviews/{interview_id}/message",
    response_model=InterviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Send Question to Interview Session",
    description="Asks a researcher question to a synthetic persona within an active interview session."
)
async def send_interview_message_endpoint(
    interview_id: str,
    payload: InterviewMessageRequest
) -> InterviewResponse:
    try:
        return await interview_service.process_message(
            session_id=interview_id,
            payload=payload
        )
    except HTTPException:
        raise
    except Exception as e:
        from app.core.llm_factory import is_quota_or_rate_limit_error
        if is_quota_or_rate_limit_error(e):
            err_msg = "Gemini is temporarily unavailable because the current API quota has been reached. Switch to Mock mode to continue testing."
        else:
            err_msg = f"Interview generation error: {str(e)}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=err_msg
        )


@router.get(
    "/interviews/{interview_id}",
    response_model=InterviewSessionInfo,
    status_code=status.HTTP_200_OK,
    summary="Get Interview Session Details",
    description="Retrieves active interview session details and complete message history."
)
async def get_interview_session_endpoint(
    interview_id: str,
    persona_id: str = Query("default_persona", description="Persona ID associated with the session")
) -> InterviewSessionInfo:
    try:
        return interview_service.get_session(persona_id=persona_id, session_id=interview_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve interview session: {str(e)}"
        )
