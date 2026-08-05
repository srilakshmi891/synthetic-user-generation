import os
import asyncio
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from app.core.llm_factory import get_llm
from app.agent.prompts_india_swe import SYSTEM_PROMPT_ASPIRING_SWE_INDIA, USER_PROMPT_ASPIRING_SWE_INDIA

class BasicInfo(BaseModel):
    persona_id: str = Field(..., description="Unique slug ID", example="persona_swe_in_001")
    full_name: str = Field(..., description="Full synthetic Indian name", example="Priya Sharma")
    avatar_description: str = Field(..., description="Visual appearance summary for UI avatar generation.")
    bio: str = Field(..., description="Short biographical summary.")

class DemographicsIndia(BaseModel):
    age: int = Field(..., description="Age in years.")
    gender: str = Field(..., description="Gender identity.")
    location: str = Field(..., description="City and city tier (e.g. Pune - Tier 2, Kanpur - Tier 2, Bengaluru - Tier 1).")
    college_tier: str = Field(..., description="Tier 1 (IIT/NIT/BITS), Tier 2, Tier 3, or Non-Engineering.")
    family_background: str = Field(..., description="Socio-economic context of the family.")
    monthly_learning_budget_inr: str = Field(..., description="Budget for courses/subscriptions in INR.", example="₹500 - ₹2,000 / month")

class EducationIndia(BaseModel):
    degree: str = Field(..., description="e.g. B.Tech, BCA, MCA, B.Sc Computer Science.")
    branch: str = Field(..., description="e.g. Computer Science, Electronics & Communication, Mechanical.")
    graduation_year: int = Field(..., description="Year of graduation.")
    college_name_type: str = Field(..., description="e.g. Regional Affiliated State Engineering College.")

class Goals(BaseModel):
    primary_career_goals: List[str] = Field(..., description="Top career targets (e.g., Land product-based company job, remote international role).")
    short_term_goals: List[str] = Field(..., description="Goals for next 3-6 months (e.g., complete 250 LeetCode problems, build MERN stack project).")

class Motivations(BaseModel):
    intrinsic_motivations: List[str] = Field(..., description="Internal emotional drivers.")
    extrinsic_motivations: List[str] = Field(..., description="External drivers e.g. financial independence, elevated family status.")

class ChallengesIndia(BaseModel):
    placement_friction: List[str] = Field(..., description="Friction in campus placements or off-campus resume screening.")
    technical_learning_blockers: List[str] = Field(..., description="Obstacles in mastering DSA, System Design, or Web Dev.")
    infrastructure_constraints: List[str] = Field(..., description="Hardware, internet, or environment limitations.")

class BehaviourIndia(BaseModel):
    daily_learning_routine: str = Field(..., description="Summary of daily study/coding schedule.")
    learning_platforms: List[str] = Field(..., description="Primary learning tools (YouTube, GeeksforGeeks, TakeUForward, Coursera, etc.).")
    job_application_strategy: str = Field(..., description="Cold emailing, LinkedIn networking, referral hunting, off-campus drives.")

class PersonalityTraits(BaseModel):
    key_traits: List[str] = Field(..., description="Descriptive personality keywords.")
    communication_style: str = Field(..., description="English fluency, confidence level, preference for written vs spoken.")
    resilience_level: str = Field(..., description="Handling rejection during hiring seasons.")

class TechnicalSkills(BaseModel):
    primary_languages: List[str] = Field(..., description="Core coding languages (Java, C++, Python, JavaScript).")
    frameworks_tools: List[str] = Field(..., description="Web/mobile frameworks and tools (React, Node.js, Git, SQL).")
    dsa_proficiency: str = Field(..., description="Data Structures & Algorithms problem-solving readiness.")

class TechnologyUsage(BaseModel):
    laptop_hardware_spec: str = Field(..., description="e.g., i3 8th Gen, 8GB RAM or M1 MacBook Air.")
    internet_setup: str = Field(..., description="Mobile 4G/5G hotspot vs Home Broadband Fiber.")
    primary_ide: str = Field(..., description="e.g., VS Code, IntelliJ IDEA, Online Compiler.")
    daily_screen_time_hours: float = Field(..., description="Hours per day.")

class AspiringSWEPersonaIndia(BaseModel):
    basic_info: BasicInfo
    demographics: DemographicsIndia
    education: EducationIndia
    goals: Goals
    motivations: Motivations
    challenges: ChallengesIndia
    behaviour: BehaviourIndia
    personality_traits: PersonalityTraits
    technical_skills: TechnicalSkills
    technology_usage: TechnologyUsage
    quote: str = Field(..., description="Representative verbatim quote in natural Indian English.")

class AspiringSWECohort(BaseModel):
    cohort_summary: str
    personas: List[AspiringSWEPersonaIndia]

async def generate_india_swe_personas(
    product_description: str,
    research_objective: str,
    persona_count: int = 3,
    provider: str = "gemini"
) -> AspiringSWECohort:
    """
    Executes prompt with structured output LLM chain to generate realistic personas.
    """
    llm = get_llm(provider=provider)
    structured_llm = llm.with_structured_output(AspiringSWECohort)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT_ASPIRING_SWE_INDIA),
        ("human", USER_PROMPT_ASPIRING_SWE_INDIA)
    ])
    
    chain = prompt | structured_llm
    
    result: AspiringSWECohort = await chain.ainvoke({
        "persona_count": persona_count,
        "product_description": product_description,
        "research_objective": research_objective,
    })
    
    return result

if __name__ == "__main__":
    # Test script entrypoint
    sample_product = "An AI-powered Coding Interview Simulator that conducts mock technical interviews in DSA and System Design with real-time voice feedback."
    sample_objective = "Evaluate price sensitivity in INR, willingness to practice with AI vs human mentors, and feature demand among Tier-2 and Tier-3 Indian engineering students."
    
    print("Generating personas for Aspiring SWEs in India...")
    # asyncio.run(generate_india_swe_personas(sample_product, sample_objective))
