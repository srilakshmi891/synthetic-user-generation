import asyncio
from app.models.persona import ComprehensivePersona
from app.validation.validator import PersonaValidator

async def test_validator():
    validator = PersonaValidator(llm_provider=None) # Testing fast deterministic mode

    # 1. Construct an INVALID persona with deliberate contradictions
    invalid_persona_data = {
        "basic_info": {
            "persona_id": "persona_invalid_01",
            "full_name": "Jimmy Teenager",
            "avatar_description": "16-year-old high school student",
            "bio": "High school student learning HTML."
        },
        "demographics": {
            "age": 16,
            "gender": "Male",
            "location": "New York, NY",
            "marital_status": "Single",
            "household_income": "$250,000 USD"
        },
        "education": {
            "degree_level": "High School Diploma in progress",
            "field_of_study": "General",
            "institution_type": "Public High School"
        },
        "occupation": {
            "job_title": "Vice President of Software Engineering",  # Age (16) vs Title mismatch!
            "industry": "Enterprise Tech",
            "company_size": "1000+ employees",
            "work_mode": "In-office",
            "key_responsibilities": ["Managing 50 engineers"]
        },
        "goals": {
            "primary_goals": [], # Missing required primary goal!
            "secondary_goals": [],
            "personal_aspirations": []
        },
        "motivations": {
            "intrinsic_motivations": ["Fun"],
            "extrinsic_motivations": ["Money"],
            "core_values": ["Speed"]
        },
        "challenges": {
            "pain_points": [], # Missing required pain point!
            "daily_frustrations": [],
            "workflow_blockers": []
        },
        "behaviour": {
            "decision_making_style": "Impulsive",
            "purchasing_behavior": "Buys online",
            "media_consumption": ["TikTok"],
            "discovery_channels": ["YouTube"]
        },
        "personality_traits": {
            "big_five_summary": {"Openness": "High"},
            "key_traits": ["Young"],
            "communication_style": "Casual",
            "attitude_towards_change": "Open"
        },
        "technical_skills": {
            "overall_proficiency": "Beginner",
            "domain_expertise": ["HTML"],
            "software_proficiency": {"VS Code": "Beginner"}
        },
        "technology_usage": {
            "primary_devices": ["iPhone"],
            "operating_systems": ["iOS"],
            "favorite_apps": ["TikTok"],
            "daily_screen_time_hours": 6.0,
            "tech_adoption_stage": "Early Majority"
        },
        "quote": "" # Missing required quote!
    }

    persona = ComprehensivePersona(**invalid_persona_data)
    
    print("--- Running Persona Validation Engine ---")
    result = await validator.validate(persona, include_semantic_audit=False)
    
    print(f"\nIs Valid: {result.is_valid}")
    print(f"Quality Score: {result.quality_score} / 100")
    
    print(f"\nErrors Found ({len(result.errors)}):")
    for err in result.errors:
        print(f"❌ [{err.category}] Field '{err.field_path}': {err.message}")
        if err.suggested_fix:
            print(f"   💡 Suggested Fix: {err.suggested_fix}")

    print(f"\nWarnings Found ({len(result.warnings)}):")
    for warn in result.warnings:
        print(f"⚠️  [{warn.category}] Field '{warn.field_path}': {warn.message}")

if __name__ == "__main__":
    asyncio.run(test_validator())


async def test_cohort_validator():
    validator = PersonaValidator(llm_provider=None)

    valid_base = {
        "basic_info": {
            "persona_id": "persona_dup_01",
            "full_name": "Alex Rivera",
            "avatar_description": "Adult professional in business casual.",
            "bio": "Product-minded professional balancing career growth and personal finance."
        },
        "demographics": {
            "age": 29,
            "gender": "Non-binary",
            "location": "Austin, TX, USA",
            "marital_status": "Single",
            "household_income": "$85,000 - $95,000 USD"
        },
        "education": {
            "degree_level": "Bachelor's Degree",
            "field_of_study": "Marketing",
            "institution_type": "State University"
        },
        "occupation": {
            "job_title": "Marketing Specialist",
            "industry": "Consumer Tech",
            "company_size": "100-250 employees",
            "work_mode": "Hybrid",
            "key_responsibilities": ["Campaign planning", "Analytics reporting"]
        },
        "goals": {
            "primary_goals": ["Improve campaign ROI"],
            "secondary_goals": ["Learn SQL"],
            "personal_aspirations": ["Buy a home"]
        },
        "motivations": {
            "intrinsic_motivations": ["Mastery"],
            "extrinsic_motivations": ["Promotion"],
            "core_values": ["Transparency"]
        },
        "challenges": {
            "pain_points": ["Fragmented analytics tools"],
            "daily_frustrations": ["Manual reporting"],
            "workflow_blockers": ["Limited budget approvals"]
        },
        "behaviour": {
            "decision_making_style": "Data-informed",
            "purchasing_behavior": "Prefers free trials",
            "media_consumption": ["Industry newsletters"],
            "discovery_channels": ["LinkedIn"]
        },
        "personality_traits": {
            "big_five_summary": {"Openness": "High", "Conscientiousness": "High"},
            "key_traits": ["Curious", "Organized"],
            "communication_style": "Concise and collaborative",
            "attitude_towards_change": "Open with evidence"
        },
        "technical_skills": {
            "overall_proficiency": "Intermediate",
            "domain_expertise": ["Digital marketing"],
            "software_proficiency": {"Google Analytics": "Advanced"}
        },
        "technology_usage": {
            "primary_devices": ["MacBook Air"],
            "operating_systems": ["macOS"],
            "favorite_apps": ["Slack", "Notion"],
            "daily_screen_time_hours": 8.0,
            "tech_adoption_stage": "Early Majority"
        },
        "quote": "I need tools that remove busywork so I can focus on strategy."
    }

    persona_a = ComprehensivePersona(**valid_base)
    persona_b_data = {
        **valid_base,
        "basic_info": {
            **valid_base["basic_info"],
            "persona_id": "persona_dup_01",  # duplicate id
            "full_name": "Alex Rivera"       # duplicate name
        }
    }
    persona_b = ComprehensivePersona(**persona_b_data)

    print("\n--- Running Cohort Uniqueness Validation ---")
    result = await validator.validate_personas([persona_a, persona_b], include_semantic_audit=False)
    print(f"Is Valid: {result.is_valid}")
    for err in result.errors:
        print(f"❌ [{err.category}] Field '{err.field_path}': {err.message}")


if __name__ == "__main__":
    async def _run_all():
        await test_validator()
        await test_cohort_validator()

    asyncio.run(_run_all())
