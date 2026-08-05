from langgraph.graph import StateGraph, START, END
from app.agent.state import AgentState
from app.agent.nodes import plan_archetypes_node, generate_personas_node, audit_cohort_node

def create_persona_generation_graph():
    """
    Constructs and compiles the LangGraph StateGraph workflow for persona generation.
    """
    builder = StateGraph(AgentState)
    
    # Add Nodes
    builder.add_node("plan_archetypes", plan_archetypes_node)
    builder.add_node("generate_personas", generate_personas_node)
    builder.add_node("audit_cohort", audit_cohort_node)
    
    # Define Edge Flow
    builder.add_edge(START, "plan_archetypes")
    builder.add_edge("plan_archetypes", "generate_personas")
    builder.add_edge("generate_personas", "audit_cohort")
    builder.add_edge("audit_cohort", END)
    
    return builder.compile()

# Instantiated graph executor
persona_graph = create_persona_generation_graph()
