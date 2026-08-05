import asyncio
from app.agent.persona_agent import PersonaGenerationAgent, PersonaPromptBuilder
from app.core.llm_factory import get_llm


async def main():
    # 1. Input Parameters
    product_desc = "An AI-powered personal finance assistant that automates micro-investing and budget categorization."
    target_aud = "Gen Z and Millennials earning $50k-$100k struggling with saving discipline."
    research_obj = "Evaluate willingness to connect bank accounts via Plaid, price sensitivity, and onboarding friction."
    number_of_personas = 3

    print("--- 1. Testing Clean Dependency Injection ---")
    llm_instance = get_llm(provider="gemini", model_name="gemini-1.5-pro")
    agent = PersonaGenerationAgent(llm=llm_instance)

    print("\n--- 2. Testing Prompt Builder Separation ---")
    prompt_builder = PersonaPromptBuilder()
    persona_prompt = prompt_builder.build_persona_synthesis_prompt()
    print("Generated Prompt Template Messages:")
    for msg in persona_prompt.messages:
        print(f"- Role: {msg.type} | Content: {msg.prompt.template[:80]}...")

    print("\n--- 3. Invoking Agent to Generate Personas ---")
    # Note: Requires GOOGLE_API_KEY or OPENAI_API_KEY environment variable set
    # personas = await agent.generate_personas(
    #     product_description=product_desc,
    #     target_audience=target_aud,
    #     research_objective=research_obj,
    #     number_of_personas=number_of_personas
    # )
    # print(f"Generated {len(personas)} personas:")
    # for persona in personas:
    #     print(f"- {persona.basic_info.full_name}: {persona.quote}")
    #     print(persona.model_dump_json(indent=2))

if __name__ == "__main__":
    asyncio.run(main())
