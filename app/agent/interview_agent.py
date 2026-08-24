from typing import Optional, List, Dict, Any
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from app.models.persona import ComprehensivePersona
from app.models.interview import InterviewResponse, ChatMessagePayload
from app.memory.base import BasePersonaMemory
from app.memory.json_memory import memory_service
from app.core.llm_factory import get_llm

class PersonaInterviewPromptBuilder:
    """
    Constructs prompts for interactive synthetic user persona interviews.
    Ensures stable persona attributes, past context, and strict in-character consistency.
    """

    @staticmethod
    def build_system_prompt(persona: ComprehensivePersona, product_context: Optional[str] = None) -> str:
        b = persona.basic_info
        d = persona.demographics
        o = persona.occupation
        e = persona.education
        g = persona.goals
        m = persona.motivations
        c = persona.challenges
        p = persona.personality_traits
        t = persona.technical_skills
        u = persona.technology_usage

        product_info = f"\nResearch Product Context: {product_context}" if product_context else ""

        system_text = (
            f"You are simulating a real synthetic user research participant named {b.full_name}.\n"
            f"You must strictly adopt {b.full_name}'s identity, perspective, voice, and mindset in this user interview.{product_info}\n\n"
            f"=== YOUR PROFILE & BACKSTORY ===\n"
            f"- Full Name: {b.full_name}\n"
            f"- Age: {d.age} | Gender: {d.gender} | Location: {d.location}\n"
            f"- Occupation: {o.job_title} ({o.industry}, {o.work_mode})\n"
            f"- Bio: {b.bio}\n"
            f"- Education: {e.degree_level} in {e.field_of_study}\n"
            f"- Household Income: {d.household_income}\n"
            f"- Primary Goals: {', '.join(g.primary_goals)}\n"
            f"- Core Motivations: {', '.join(m.intrinsic_motivations + m.core_values)}\n"
            f"- Key Pain Points & Frustrations: {', '.join(c.pain_points + c.daily_frustrations)}\n"
            f"- Communication Style: {p.communication_style}\n"
            f"- Tech Literacy: {t.overall_proficiency} (Favorite apps: {', '.join(u.favorite_apps)})\n"
            f"- Representative Quote: \"{persona.quote}\"\n\n"
            f"=== STRICT INTERVIEW INSTRUCTIONS ===\n"
            f"1. Stay strictly in character as {b.full_name} at all times. Answer in the first person ('I', 'my').\n"
            f"2. Maintain absolute consistency with your established age, occupation, background, goals, preferences, and prior conversation context.\n"
            f"3. Do NOT contradict statements or opinions you expressed earlier in this conversation.\n"
            f"4. Speak naturally, authentically, and conversationally as a real research participant.\n"
            f"5. Do NOT break character or mention that you are an AI model or synthetic assistant.\n"
            f"6. Provide thoughtful, realistic answers grounded in your specific background and challenges."
        )
        return system_text


class PersonaInterviewAgent:
    """
    Agent responsible for managing multi-turn interview interactions with synthetic user personas.
    Integrates prompt building, memory retrieval, LLM execution, and memory persistence.
    """

    def __init__(
        self,
        llm: Optional[BaseChatModel] = None,
        provider: str = "gemini",
        model_name: Optional[str] = None,
        memory: Optional[BasePersonaMemory] = None
    ):
        self.llm = llm or get_llm(provider=provider, model_name=model_name)
        self.memory = memory or memory_service

    async def conduct_interview(
        self,
        persona: ComprehensivePersona,
        session_id: str,
        user_question: str,
        product_context: Optional[str] = None,
        history_limit: int = 10
    ) -> InterviewResponse:
        persona_id = persona.basic_info.persona_id or persona.basic_info.full_name.lower().replace(" ", "_")

        # 1. Retrieve history from isolated persona memory
        history = self.memory.get_history(persona_id=persona_id, session_id=session_id, limit=history_limit)

        # 2. Build system message
        system_text = PersonaInterviewPromptBuilder.build_system_prompt(persona, product_context)

        # 3. Assemble LangChain message chain
        messages = [SystemMessage(content=system_text)]
        for turn in history:
            if turn["role"] == "user":
                messages.append(HumanMessage(content=turn["content"]))
            elif turn["role"] == "assistant":
                messages.append(AIMessage(content=turn["content"]))

        # Append current user question
        messages.append(HumanMessage(content=user_question))

        # 4. Invoke LLM with automatic fallback on quota exhaustion / 429
        try:
            response = await self.llm.ainvoke(messages)
        except Exception as e:
            from app.core.llm_factory import is_quota_or_rate_limit_error, MockChatModel
            if is_quota_or_rate_limit_error(e) or not isinstance(self.llm, MockChatModel):
                print(f"[Interview Agent] Gemini quota/provider limit reached ({type(e).__name__}). Using development MockChatModel fallback.")
                mock_model = MockChatModel()
                response = await mock_model.ainvoke(messages)
            else:
                raise

        reply_text = response.content if hasattr(response, "content") else str(response)

        # Handle string formatting if reply_text is list or weird object
        if isinstance(reply_text, list):
            reply_text = "\n".join([str(item.get("text", item)) if isinstance(item, dict) else str(item) for item in reply_text])
        else:
            reply_text = str(reply_text).strip()

        # 5. Persist turn to persona memory
        self.memory.add_turn(
            persona_id=persona_id,
            session_id=session_id,
            user_query=user_question,
            persona_response=reply_text
        )

        # 6. Fetch updated full history to return to caller
        updated_history_raw = self.memory.get_history(persona_id=persona_id, session_id=session_id, limit=50)
        formatted_history = [
            ChatMessagePayload(
                id=f"msg_{i}",
                role=h["role"],
                content=h["content"],
                timestamp=h.get("timestamp")
            )
            for i, h in enumerate(updated_history_raw)
        ]

        return InterviewResponse(
            persona_id=persona_id,
            session_id=session_id,
            reply=reply_text,
            history=formatted_history
        )
