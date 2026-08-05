from typing import Any, Dict
from langchain_core.prompts import ChatPromptTemplate
from app.agent.state import AgentState
from app.agent.prompts import ARCHETYPE_PLANNER_PROMPT, PERSONA_GENERATOR_PROMPT, COHORT_AUDITOR_PROMPT
from app.core.llm_factory import get_llm
from app.models.persona import ArchetypePlanList, ComprehensivePersona

async def plan_archetypes_node(state: AgentState) -> Dict[str, Any]:
    """
    Node 1: Audience Decomposition & Archetype Planner
    Generates N distinct archetype plans to maximize cohort diversity.
    """
    llm = get_llm(provider=state.get("provider", "gemini"), model_name=state.get("model_name"))
    structured_llm = llm.with_structured_output(ArchetypePlanList)
    
    prompt = ChatPromptTemplate.from_template(ARCHETYPE_PLANNER_PROMPT)
    chain = prompt | structured_llm
    
    result: ArchetypePlanList = await chain.ainvoke({
        "product_description": state["product_description"],
        "target_audience": state["target_audience"],
        "research_objective": state["research_objective"],
        "persona_count": state["persona_count"],
    })
    
    return {"archetypes": result.archetypes}

async def generate_personas_node(state: AgentState) -> Dict[str, Any]:
    """
    Node 2: Persona Synthesizer & Profile Generator
    Iterates through each planned archetype and synthesizes full structured persona.
    """
    llm = get_llm(provider=state.get("provider", "gemini"), model_name=state.get("model_name"))
    structured_llm = llm.with_structured_output(ComprehensivePersona)
    prompt = ChatPromptTemplate.from_template(PERSONA_GENERATOR_PROMPT)
    chain = prompt | structured_llm
    
    generated_personas = []
    for archetype in state["archetypes"]:
        persona: ComprehensivePersona = await chain.ainvoke({
            "product_description": state["product_description"],
            "target_audience": state["target_audience"],
            "research_objective": state["research_objective"],
            "archetype_title": archetype.archetype_title,
            "key_differentiator": archetype.key_differentiator,
            "target_demographic_focus": archetype.target_demographic_focus,
        })
        generated_personas.append(persona)
        
    return {"personas": generated_personas}

async def audit_cohort_node(state: AgentState) -> Dict[str, Any]:
    """
    Node 3: Cohort Auditor & Diversity Checker
    Evaluates cohort coverage and diversity relative to the research objective.
    """
    llm = get_llm(provider=state.get("provider", "gemini"), model_name=state.get("model_name"))
    
    personas_summary = "\n\n".join([
        f"Persona {i+1}: {p.basic_info.full_name} ({p.occupation.job_title})\n"
        f"Quote: \"{p.quote}\"\n"
        f"Pain Points: {', '.join(p.challenges.pain_points)}"
        for i, p in enumerate(state["personas"])
    ])
    
    prompt = ChatPromptTemplate.from_template(COHORT_AUDITOR_PROMPT)
    chain = prompt | llm
    
    response = await chain.ainvoke({
        "product_description": state["product_description"],
        "research_objective": state["research_objective"],
        "personas_summary": personas_summary,
    })
    
    analysis_text = str(response.content)
    return {"cohort_diversity_analysis": analysis_text}
