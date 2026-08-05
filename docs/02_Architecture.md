# 02. System Architecture

## 1. High-Level Architectural Diagram

```mermaid
flowchart TD
    Client[Web UI / HTTP Client] -->|POST /generate-persona| Gateway[FastAPI API Gateway]
    
    subgraph Core Platform
        Gateway --> Router[API Router & Request Validator]
        Router --> GraphEngine[LangGraph Engine]
        
        subgraph LangGraph 6-Node Workflow
            Input[1. Input Node] --> Prompt[2. Prompt Builder Node]
            Prompt --> LLM[3. LLM Node]
            LLM --> Val[4. Validator Node]
            Val -->|Validation Failed & Retries < 2| Prompt
            Val -->|Validation Passed OR Retries Exhausted| DB[5. Database Node]
            DB --> Output[6. Output Node]
        end
        
        LLM <-->|Structured Output Binding| LLMFactory[LLM Factory: Gemini / OpenAI]
        Val <-->|Rule Engine + LLM Semantic Audit| ValEngine[Persona Validation Engine]
        DB <-->|Async ORM Session| Postgres[(PostgreSQL Database)]
    end
    
    Output --> Gateway
    Gateway -->|HTTP 201 Created| Client
```

## 2. Layered Responsibilities & Design Patterns

1. **API Gateway Layer (`app/api/`)**: Controller Pattern. Handles REST routes, HTTP status codes, and dependency injection (`Depends()`).
2. **Agent Engine Layer (`app/agent/`)**: State Machine & Builder Pattern. Constructs prompts and executes LangGraph state graphs.
3. **Quality Validation Layer (`app/validation/`)**: Strategy & Rule Engine Pattern. Runs rule-based and LLM semantic checks.
4. **Data Persistence Layer (`app/db/`)**: Data Mapper ORM Pattern. PostgreSQL persistence using SQLAlchemy 2.0.
5. **Infrastructure Layer (`app/core/`)**: Factory Method & Singleton Pattern. Loads configurations and manages LLM provider instances.
