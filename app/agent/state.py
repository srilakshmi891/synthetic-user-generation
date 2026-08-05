from typing import List, Optional, TypedDict
from app.models.persona import ArchetypePlan, Persona

class AgentState(TypedDict):
    product_description: str
    target_audience: str
    research_objective: str
    persona_count: int
    provider: str
    model_name: Optional[str]
    
    # Internal agent pipeline state
    archetypes: List[ArchetypePlan]
    personas: List[Persona]
    cohort_diversity_analysis: str
    errors: List[str]
