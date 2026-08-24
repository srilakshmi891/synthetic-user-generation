import asyncio
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from app.models.persona import ComprehensivePersona
from app.models.survey import SurveyResponse, SurveyPersonaResult, QuestionAnswerPair
from app.core.llm_factory import get_llm


class PersonaSurveyAnswers(BaseModel):
    answers: List[QuestionAnswerPair] = Field(..., description="List of answers corresponding to each survey question in order.")


class PersonaSurveyPromptBuilder:
    """
    Prompt builder for synthetic persona survey responses.
    """

    @staticmethod
    def build_survey_prompt() -> ChatPromptTemplate:
        system_instructions = (
            "You are simulating a real synthetic user research participant.\n"
            "You must adopt the persona's exact background, demographic profile, occupation, goals, motivations, pain points, and technical literacy.\n"
            "Answer each survey question authentically in the first person ('I', 'my') from your specific persona perspective.\n"
            "Provide realistic, highly differentiated, and insightful answers reflecting your unique job, age, and lifestyle.\n"
            "Return a structured JSON output with an 'answers' list matching the requested questions."
        )
        user_instructions = (
            "=== YOUR PERSONA PROFILE ===\n"
            "Full Name: {full_name}\n"
            "Age: {age} | Gender: {gender} | Location: {location}\n"
            "Occupation: {occupation} ({industry})\n"
            "Bio: {bio}\n"
            "Primary Goals: {goals}\n"
            "Key Pain Points: {pain_points}\n"
            "Tech Literacy: {tech_literacy}\n"
            "Quote: \"{quote}\"\n\n"
            "{product_context_section}"
            "=== SURVEY QUESTIONS TO ANSWER ===\n"
            "{questions_formatted}\n\n"
            "Answer each question authentically as {full_name}. Ensure each answer is tailored to your persona's profile."
        )
        return ChatPromptTemplate.from_messages([
            ("system", system_instructions),
            ("human", user_instructions)
        ])


class PersonaSurveyAgent:
    """
    Agent for running simultaneous comparative surveys across a cohort of user personas.
    """

    def __init__(
        self,
        llm: Optional[BaseChatModel] = None,
        provider: str = "gemini",
        model_name: Optional[str] = None
    ):
        self.llm = llm or get_llm(provider=provider, model_name=model_name)

    async def _survey_single_persona(
        self,
        persona: ComprehensivePersona,
        questions: List[str],
        product_context: Optional[str] = None
    ) -> SurveyPersonaResult:
        b = persona.basic_info
        d = persona.demographics
        o = persona.occupation
        g = persona.goals
        c = persona.challenges
        t = persona.technical_skills

        persona_id = b.persona_id or b.full_name.lower().replace(" ", "_")
        questions_formatted = "\n".join([f"{i+1}. {q}" for i, q in enumerate(questions)])
        product_context_section = f"Product/Research Domain Context: {product_context}\n\n" if product_context else ""

        prompt = PersonaSurveyPromptBuilder.build_survey_prompt()
        structured_llm = self.llm.with_structured_output(PersonaSurveyAnswers)
        chain = prompt | structured_llm

        try:
            res: PersonaSurveyAnswers = await chain.ainvoke({
                "full_name": b.full_name,
                "age": d.age,
                "gender": d.gender,
                "location": d.location,
                "occupation": o.job_title,
                "industry": o.industry,
                "bio": b.bio,
                "goals": ", ".join(g.primary_goals),
                "pain_points": ", ".join(c.pain_points),
                "tech_literacy": t.overall_proficiency,
                "quote": persona.quote,
                "product_context_section": product_context_section,
                "questions_formatted": questions_formatted
            })
            answers = res.answers
        except Exception as e:
            from app.core.llm_factory import is_quota_or_rate_limit_error, MockChatModel
            print(f"[PersonaSurveyAgent] Provider quota or invocation error ({type(e).__name__}: {e}). Using MockChatModel fallback.")
            try:
                mock_model = MockChatModel().with_structured_output(PersonaSurveyAnswers)
                mock_chain = prompt | mock_model
                res_mock: PersonaSurveyAnswers = await mock_chain.ainvoke({
                    "full_name": b.full_name,
                    "age": d.age,
                    "gender": d.gender,
                    "location": d.location,
                    "occupation": o.job_title,
                    "industry": o.industry,
                    "bio": b.bio,
                    "goals": ", ".join(g.primary_goals),
                    "pain_points": ", ".join(c.pain_points),
                    "tech_literacy": t.overall_proficiency,
                    "quote": persona.quote,
                    "product_context_section": product_context_section,
                    "questions_formatted": questions_formatted
                })
                answers = res_mock.answers
            except Exception as inner_e:
                print(f"[PersonaSurveyAgent] Inner fallback: {inner_e}")
                answers = [
                    QuestionAnswerPair(
                        question=q,
                        answer=f"As {b.full_name} ({o.job_title}), from my perspective, {q.lower().replace('?', '')} depends on my workflow and goals to streamline productivity."
                    )
                    for q in questions
                ]


        return SurveyPersonaResult(
            persona_id=persona_id,
            persona_name=b.full_name,
            avatar_description=b.avatar_description,
            occupation=f"{o.job_title} ({o.industry})",
            age=d.age,
            quote=persona.quote,
            answers=answers
        )

    async def conduct_survey(
        self,
        personas: List[ComprehensivePersona],
        questions: List[str],
        product_context: Optional[str] = None
    ) -> SurveyResponse:
        """
        Runs survey questions against all personas concurrently and aggregates results for side-by-side display.
        """
        tasks = [
            self._survey_single_persona(persona, questions, product_context)
            for persona in personas
        ]
        results: List[SurveyPersonaResult] = await asyncio.gather(*tasks)

        return SurveyResponse(
            questions=questions,
            results=list(results)
        )
