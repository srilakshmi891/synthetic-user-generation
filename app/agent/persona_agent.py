from typing import List, Optional
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from app.models.persona import ComprehensivePersona, ArchetypePlanList, ArchetypePlan, PersonaCohort
from app.core.llm_factory import get_llm


class PersonaPromptBuilder:
    """
    Encapsulates prompt construction for persona generation.
    Separates prompt engineering logic from LLM execution.
    """

    @staticmethod
    def build_archetype_planning_prompt() -> ChatPromptTemplate:
        system_instructions = (
            "You are a Senior UX Research Scientist specializing in demographic analysis and persona planning.\n"
            "Your task is to plan {count} distinct, non-overlapping user archetypes for synthetic user research."
        )
        user_instructions = (
            "Product Description: {product_description}\n"
            "Target Audience: {target_audience}\n"
            "Research Objective: {research_objective}\n\n"
            "Generate {count} unique archetype plans to ensure cohort diversity."
        )
        return ChatPromptTemplate.from_messages([
            ("system", system_instructions),
            ("human", user_instructions)
        ])

    @staticmethod
    def build_persona_synthesis_prompt() -> ChatPromptTemplate:
        system_instructions = (
            "You are an expert UX Researcher synthesizing highly detailed synthetic user personas.\n"
            "Generate exactly {number_of_personas} realistic, internally consistent personas matching the requested schema.\n"
            "Each persona must be unique and diverse relative to the others (different demographics, occupations, "
            "motivations, pain points, and tech literacy where appropriate).\n"
            "Assign a distinct persona_id and full_name to every persona.\n"
            "Avoid stereotypes and ensure all attributes align with each persona's background and job role."
        )
        user_instructions = (
            "Product Description: {product_description}\n"
            "Target Audience: {target_audience}\n"
            "Research Objective: {research_objective}\n\n"
            "Number of Personas Required: {number_of_personas}\n\n"
            "Optional Archetype Guidance (use as a soft focus when relevant):\n"
            "- Title: {archetype_title}\n"
            "- Differentiator: {key_differentiator}\n"
            "- Target Focus: {target_demographic_focus}\n\n"
            "Synthesize exactly {number_of_personas} complete, multi-dimensional personas. "
            "Return them as a single structured response containing a 'personas' list. "
            "Ensure the cohort covers meaningful diversity within the target audience for the research objective."
        )
        return ChatPromptTemplate.from_messages([
            ("system", system_instructions),
            ("human", user_instructions)
        ])


class PersonaGenerationAgent:
    """
    Production-quality Persona Generation Agent adhering to Clean Architecture & SOLID Principles.

    - No global variables
    - Injected LLM dependency
    - Explicit separation of Prompt Building, LLM Execution, and JSON Schema Parsing
    """

    def __init__(
        self,
        llm: Optional[BaseChatModel] = None,
        provider: str = "gemini",
        model_name: Optional[str] = None,
        prompt_builder: Optional[PersonaPromptBuilder] = None
    ):
        """
        Initialize agent with dependencies.
        If an explicit LLM instance is not provided, uses the unified LLM factory.
        """
        self.llm: BaseChatModel = llm or get_llm(provider=provider, model_name=model_name)
        self.prompt_builder: PersonaPromptBuilder = prompt_builder or PersonaPromptBuilder()

    def build_archetype_prompt(
        self,
        product_description: str,
        target_audience: str,
        research_objective: str,
        count: int
    ) -> ChatPromptTemplate:
        """
        Public method to build and inspect the archetype prompt before invocation.
        """
        return self.prompt_builder.build_archetype_planning_prompt()

    def build_persona_prompt(
        self,
        product_description: str,
        target_audience: str,
        research_objective: str,
        archetype: ArchetypePlan
    ) -> ChatPromptTemplate:
        """
        Public method to build and inspect the persona synthesis prompt before invocation.
        """
        return self.prompt_builder.build_persona_synthesis_prompt()

    async def generate_personas(
        self,
        product_description: str,
        target_audience: str,
        research_objective: str,
        number_of_personas: int = 1,
        archetype_title: str = "General Target User",
        key_differentiator: str = "Primary user demographic",
        target_demographic_focus: str = "Main target audience"
    ) -> List[ComprehensivePersona]:
        """
        Generates N unique synthetic personas in a single LLM structured-output call.
        """
        if number_of_personas < 1 or number_of_personas > 100:
            raise ValueError("number_of_personas must be between 1 and 100 inclusive.")

        prompt = self.prompt_builder.build_persona_synthesis_prompt()
        structured_llm = self.llm.with_structured_output(PersonaCohort)
        chain = prompt | structured_llm

        cohort: PersonaCohort = await chain.ainvoke({
            "product_description": product_description,
            "target_audience": target_audience,
            "research_objective": research_objective,
            "number_of_personas": number_of_personas,
            "archetype_title": archetype_title,
            "key_differentiator": key_differentiator,
            "target_demographic_focus": target_demographic_focus
        })

        personas = list(cohort.personas)

        # Soft guard: if the model returns fewer/more than requested, trim or surface clearly
        if len(personas) > number_of_personas:
            personas = personas[:number_of_personas]

        return personas

    async def generate_single_persona(
        self,
        product_description: str,
        target_audience: str,
        research_objective: str,
        archetype_title: str = "General Target User",
        key_differentiator: str = "Primary user demographic",
        target_demographic_focus: str = "Main target audience"
    ) -> ComprehensivePersona:
        """
        Generates a single synthetic persona (convenience wrapper around generate_personas).
        """
        personas = await self.generate_personas(
            product_description=product_description,
            target_audience=target_audience,
            research_objective=research_objective,
            number_of_personas=1,
            archetype_title=archetype_title,
            key_differentiator=key_differentiator,
            target_demographic_focus=target_demographic_focus
        )
        return personas[0]

    async def generate_persona_cohort(
        self,
        product_description: str,
        target_audience: str,
        research_objective: str,
        count: int = 3
    ) -> List[ComprehensivePersona]:
        """
        Generates a diverse cohort of N synthetic user personas in one structured LLM response.
        """
        return await self.generate_personas(
            product_description=product_description,
            target_audience=target_audience,
            research_objective=research_objective,
            number_of_personas=count
        )
