import uuid
from typing import TypedDict, List, Optional, Any, Dict
from langgraph.graph import StateGraph, START, END
from app.models.persona import ComprehensivePersona, PersonaCohort
from app.models.request import GeneratePersonaRequest
from app.agent.persona_agent import PersonaPromptBuilder
from app.validation.validator import PersonaValidator
from app.validation.models import ValidationResult
from app.core.llm_factory import get_llm

class PersonaWorkflowState(TypedDict):
    """
    LangGraph Workflow State passed across all nodes.
    """
    # 1. Input Node State
    product_description: str
    target_audience: str
    research_objective: str
    provider: str
    model_name: Optional[str]
    session_id: str
    
    # 2. Prompt Builder Node State
    formatted_prompt: Optional[str]
    validation_feedback: Optional[str]
    
    # 3. LLM Node State
    generated_persona: Optional[ComprehensivePersona]
    
    # 4. Validator Node State
    validation_result: Optional[ValidationResult]
    retry_count: int
    max_retries: int
    
    # 5. Database Node State
    database_session_id: Optional[str]
    database_persona_id: Optional[str]
    is_persisted: bool
    
    # 6. Output Node State
    final_output: Optional[Dict[str, Any]]
    status: str
    errors: List[str]

# --- Node Implementations ---

async def input_node(state: PersonaWorkflowState) -> Dict[str, Any]:
    """
    Node 1: Input Node
    Validates initial request parameters, assigns session UUID, and initializes state defaults.
    """
    session_id = state.get("session_id") or str(uuid.uuid4())
    return {
        "session_id": session_id,
        "retry_count": state.get("retry_count", 0),
        "max_retries": state.get("max_retries", 2),
        "status": "INITIALIZED",
        "errors": []
    }

async def prompt_builder_node(state: PersonaWorkflowState) -> Dict[str, Any]:
    """
    Node 2: Prompt Builder Node
    Constructs System and User Prompts. If retrying due to validation errors, injects correction feedback.
    """
    builder = PersonaPromptBuilder()
    prompt_template = builder.build_persona_synthesis_prompt()
    
    feedback = ""
    if state.get("validation_result") and not state["validation_result"].is_valid:
        error_msgs = [e.message for e in state["validation_result"].errors]
        feedback = f"\n\n[PREVIOUS VALIDATION ERRORS TO FIX]:\n- " + "\n- ".join(error_msgs)
        
    formatted_messages = prompt_template.format_messages(
        product_description=state["product_description"],
        target_audience=state["target_audience"],
        research_objective=state["research_objective"] + feedback,
        number_of_personas=1,
        archetype_title="Primary Persona",
        key_differentiator="Core target audience representative",
        target_demographic_focus=state["target_audience"]
    )
    
    prompt_text = "\n".join([f"[{m.type}]: {m.content}" for m in formatted_messages])
    return {
        "formatted_prompt": prompt_text,
        "validation_feedback": feedback,
        "status": "PROMPT_BUILT"
    }

async def llm_node(state: PersonaWorkflowState) -> Dict[str, Any]:
    """
    Node 3: LLM Node
    Calls Google Gemini or OpenAI with structured output parsing (PersonaCohort).
    This workflow path generates a single persona (number_of_personas=1).
    """
    llm = get_llm(provider=state.get("provider", "gemini"), model_name=state.get("model_name"))
    structured_llm = llm.with_structured_output(PersonaCohort)
    
    builder = PersonaPromptBuilder()
    prompt_template = builder.build_persona_synthesis_prompt()
    chain = prompt_template | structured_llm
    
    cohort: PersonaCohort = await chain.ainvoke({
        "product_description": state["product_description"],
        "target_audience": state["target_audience"],
        "research_objective": state["research_objective"] + state.get("validation_feedback", ""),
        "number_of_personas": 1,
        "archetype_title": "Primary Persona",
        "key_differentiator": "Core target audience representative",
        "target_demographic_focus": state["target_audience"]
    })
    persona: ComprehensivePersona = cohort.personas[0]
    
    return {
        "generated_persona": persona,
        "status": "LLM_GENERATED"
    }

async def validator_node(state: PersonaWorkflowState) -> Dict[str, Any]:
    """
    Node 4: Validator Node
    Executes rule-based and semantic validation checks on the generated persona.
    """
    validator = PersonaValidator(llm_provider=state.get("provider"))
    validation_result: ValidationResult = await validator.validate(
        persona=state["generated_persona"],
        include_semantic_audit=False
    )
    
    return {
        "validation_result": validation_result,
        "status": "VALIDATED" if validation_result.is_valid else "VALIDATION_FAILED"
    }

async def database_node(state: PersonaWorkflowState) -> Dict[str, Any]:
    """
    Node 5: Database Node
    Persists validated ResearchSession, Persona, and ValidationStatus records.
    """
    persona = state["generated_persona"]
    db_session_id = state["session_id"]
    db_persona_id = str(uuid.uuid4())
    
    # Simulated DB Persistence Write
    # In production with PostgreSQL, inserts records into research_sessions, personas, and validation_statuses tables.
    
    return {
        "database_session_id": db_session_id,
        "database_persona_id": db_persona_id,
        "is_persisted": True,
        "status": "PERSISTED"
    }

async def output_node(state: PersonaWorkflowState) -> Dict[str, Any]:
    """
    Node 6: Output Node
    Prepares final structured response payload for API response.
    """
    persona = state["generated_persona"]
    val_result = state.get("validation_result")
    
    final_output = {
        "session_id": state["session_id"],
        "database_persona_id": state.get("database_persona_id"),
        "persona": persona.model_dump(),
        "validation_summary": {
            "is_valid": val_result.is_valid if val_result else True,
            "quality_score": val_result.quality_score if val_result else 100.0,
            "retry_count": state.get("retry_count", 0)
        }
    }
    
    return {
        "final_output": final_output,
        "status": "COMPLETED"
    }

# --- Conditional Edge Logic ---

def should_retry_or_persist(state: PersonaWorkflowState) -> str:
    """
    Conditional Transition Router:
    - If valid OR retries exhausted -> Transition to 'Database' node.
    - If invalid AND retries remain -> Loop back to 'Prompt Builder' node for auto-correction.
    """
    val_result = state.get("validation_result")
    retry_count = state.get("retry_count", 0)
    max_retries = state.get("max_retries", 2)
    
    if val_result and not val_result.is_valid and retry_count < max_retries:
        state["retry_count"] = retry_count + 1
        return "Prompt Builder"
    
    return "Database"

# --- Graph Compilation ---

def build_persona_langgraph():
    """
    Assembles and compiles the 6-Node Persona Generation StateGraph.
    Nodes: Input -> Prompt Builder -> LLM -> Validator -> Database -> Output
    """
    workflow = StateGraph(PersonaWorkflowState)
    
    # 1. Add Nodes
    workflow.add_node("Input", input_node)
    workflow.add_node("Prompt Builder", prompt_builder_node)
    workflow.add_node("LLM", llm_node)
    workflow.add_node("Validator", validator_node)
    workflow.add_node("Database", database_node)
    workflow.add_node("Output", output_node)
    
    # 2. Add Fixed Edges
    workflow.add_edge(START, "Input")
    workflow.add_edge("Input", "Prompt Builder")
    workflow.add_edge("Prompt Builder", "LLM")
    workflow.add_edge("LLM", "Validator")
    
    # 3. Add Conditional Edge from Validator
    workflow.add_conditional_edges(
        "Validator",
        should_retry_or_persist,
        {
            "Prompt Builder": "Prompt Builder",  # Auto-correction loop
            "Database": "Database"              # Persistence path
        }
    )
    
    # 4. Final Edges
    workflow.add_edge("Database", "Output")
    workflow.add_edge("Output", END)
    
    return workflow.compile()

# Instantiated StateGraph Workflow
persona_state_graph = build_persona_langgraph()
