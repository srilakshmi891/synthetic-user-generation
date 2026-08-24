import re
from typing import Optional, Any, List, Dict
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from app.core.config import settings


def is_quota_or_rate_limit_error(e: Exception) -> bool:
    """
    Detects if an exception is related to API rate limits, quota exhaustion (e.g. 429 RESOURCE_EXHAUSTED),
    or temporary provider outages.
    """
    err_str = str(e).lower()
    err_type = type(e).__name__.lower()

    quota_indicators = [
        "429",
        "resource_exhausted",
        "quota",
        "rate limit",
        "ratelimit",
        "generaterequestsperday",
        "exceeded your current quota",
        "free tier limit",
        "too many requests",
        "insufficient_quota",
        "quota exceeded"
    ]
    return any(ind in err_str or ind in err_type for ind in quota_indicators)


class MockChatModel(BaseChatModel):
    """
    Context-aware Mock Chat Model that provides realistic, deterministic, and consistent
    responses for Persona Generation, Multi-turn Interviews, and Comparative Surveys
    when offline, testing, or when API quotas are exhausted.
    """
    def __init__(self, target_schema: Any = None):
        super().__init__()
        self._target_schema = target_schema

    def _generate(self, messages: Any, stop: Any = None, run_manager: Any = None, **kwargs: Any) -> Any:
        from langchain_core.outputs import ChatResult, ChatGeneration
        res_text = "As a synthetic user, I value efficiency and seamless workflow integration."
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=res_text))])

    @property
    def _llm_type(self) -> str:
        return "mock-chat-model"

    def with_structured_output(self, schema: Any, **kwargs: Any) -> "MockChatModel":
        return MockChatModel(target_schema=schema)

    async def ainvoke(self, input: Any, config: Any = None, **kwargs: Any) -> Any:
        schema_name = getattr(self._target_schema, "__name__", str(self._target_schema))

        # -------------------------------------------------------------
        # 1. PERSONA GENERATION (PersonaCohort structured output)
        # -------------------------------------------------------------
        if schema_name == "PersonaCohort":
            from app.models.persona import ComprehensivePersona, PersonaCohort
            
            num_personas = 1
            if isinstance(input, dict):
                num_personas = input.get("number_of_personas", 1)
            
            personas_pool = [
                ComprehensivePersona(
                    basic_info={
                        "persona_id": "sarah_chen_mock",
                        "full_name": "Sarah Chen",
                        "avatar_description": "A focused professional with a laptop in a modern studio",
                        "bio": "Digital marketing specialist navigating multi-channel campaigns and analytics daily."
                    },
                    demographics={"age": 29, "gender": "Female", "ethnicity": "Asian", "location": "San Francisco, CA", "marital_status": "Single", "household_income": "$105,000"},
                    education={"degree_level": "Bachelor's Degree", "field_of_study": "Marketing & Communications", "institution_type": "State University"},
                    occupation={"job_title": "Digital Marketing Specialist", "industry": "Technology / SaaS", "company_size": "50-200", "work_mode": "Hybrid", "key_responsibilities": ["Paid search & social ads", "Funnel analytics", "Campaign budget optimization"]},
                    goals={"primary_goals": ["Automate repetitive ad reporting", "Maximize return on ad spend (ROAS)"], "secondary_goals": ["Learn AI prompt engineering"], "personal_aspirations": ["Lead a growth marketing team"]},
                    motivations={"intrinsic_motivations": ["Data clarity", "Continuous learning"], "extrinsic_motivations": ["Career recognition"], "core_values": ["Transparency", "Efficiency"]},
                    challenges={"pain_points": ["Context switching between 6+ ad platforms", "Clunky reporting dashboards"], "daily_frustrations": ["Slow data syncs"], "workflow_blockers": ["Manual CSV exports"]},
                    behaviour={"decision_making_style": "Data-driven", "purchasing_behavior": "Evaluates free trials first", "media_consumption": ["TechCrunch", "GrowthHackers"], "discovery_channels": ["Product Hunt", "LinkedIn"]},
                    personality_traits={"big_five_summary": {"Openness": "High", "Conscientiousness": "High"}, "key_traits": ["Analytical", "Detail-oriented", "Resourceful"], "communication_style": "Concise & direct", "attitude_towards_change": "Eager adopter"},
                    technical_skills={"overall_proficiency": "Advanced", "domain_expertise": ["Google Ads", "Meta Ads", "Google Analytics 4"], "software_proficiency": {"Excel": "Expert", "Notion": "Proficient"}},
                    technology_usage={"primary_devices": ["MacBook Pro 16", "iPhone 15"], "operating_systems": ["macOS", "iOS"], "favorite_apps": ["Slack", "Notion", "Figma"], "daily_screen_time_hours": 8.5, "tech_adoption_stage": "Early Adopter"},
                    quote="I need tools that eliminate repetitive busywork so I can focus on creative campaign strategy."
                ),
                ComprehensivePersona(
                    basic_info={
                        "persona_id": "marcus_vance_mock",
                        "full_name": "Marcus Vance",
                        "avatar_description": "An experienced operations lead reviewing logistics charts",
                        "bio": "Senior logistics coordinator optimizing supply chain efficiency and warehouse fulfillment."
                    },
                    demographics={"age": 42, "gender": "Male", "ethnicity": "Caucasian", "location": "Austin, TX", "marital_status": "Married", "household_income": "$115,000"},
                    education={"degree_level": "Bachelor's Degree", "field_of_study": "Supply Chain Management", "institution_type": "University"},
                    occupation={"job_title": "Operations & Logistics Manager", "industry": "E-Commerce / Retail", "company_size": "200-500", "work_mode": "On-Site", "key_responsibilities": ["Inventory tracking", "Vendor negotiations", "Carrier SLA monitoring"]},
                    goals={"primary_goals": ["Reduce shipment delays", "Cut operational overhead by 15%"], "secondary_goals": ["Modernize legacy warehouse ERP"], "personal_aspirations": ["Become VP of Global Operations"]},
                    motivations={"intrinsic_motivations": ["Operational excellence", "Problem solving"], "extrinsic_motivations": ["Team performance bonuses"], "core_values": ["Reliability", "Accountability"]},
                    challenges={"pain_points": ["Disparate inventory databases", "Unpredictable delivery delays"], "daily_frustrations": ["Legacy desktop software crashes"], "workflow_blockers": ["Manual paper manifests"]},
                    behaviour={"decision_making_style": "Pragmatic & risk-averse", "purchasing_behavior": "Requires enterprise SLA and security guarantees", "media_consumption": ["SupplyChainDigest"], "discovery_channels": ["Industry conferences"]},
                    personality_traits={"big_five_summary": {"Conscientiousness": "Very High"}, "key_traits": ["Methodical", "Decisive", "Process-driven"], "communication_style": "Structured & assertive", "attitude_towards_change": "Cautious until proven"},
                    technical_skills={"overall_proficiency": "Intermediate", "domain_expertise": ["SAP", "WMS Software", "Excel Modeling"], "software_proficiency": {"SAP": "Advanced", "Excel": "Expert"}},
                    technology_usage={"primary_devices": ["ThinkPad", "iPad Pro"], "operating_systems": ["Windows 11", "iPadOS"], "favorite_apps": ["Outlook", "Teams", "SAP Mobile"], "daily_screen_time_hours": 6.5, "tech_adoption_stage": "Late Majority"},
                    quote="If a software isn't 100% reliable on the warehouse floor, it costs us thousands every single minute."
                ),
                ComprehensivePersona(
                    basic_info={
                        "persona_id": "priya_patel_mock",
                        "full_name": "Priya Patel",
                        "avatar_description": "A vibrant freelance UX designer working at a sunlit cafe",
                        "bio": "Independent product designer crafting accessible mobile interfaces for fintech and healthtech startups."
                    },
                    demographics={"age": 26, "gender": "Female", "ethnicity": "South Asian", "location": "Seattle, WA", "marital_status": "Single", "household_income": "$88,000"},
                    education={"degree_level": "Bachelor's Degree", "field_of_study": "Human-Computer Interaction", "institution_type": "Design Academy"},
                    occupation={"job_title": "Freelance Product Designer", "industry": "Design / Tech Consulting", "company_size": "Self-Employed", "work_mode": "Remote", "key_responsibilities": ["User testing", "Interactive wireframing", "Design system documentation"]},
                    goals={"primary_goals": ["Deliver client prototypes faster", "Maintain steady freelance pipeline"], "secondary_goals": ["Build a design component library"], "personal_aspirations": ["Launch a digital design studio"]},
                    motivations={"intrinsic_motivations": ["Creative autonomy", "Aesthetic craftsmanship"], "extrinsic_motivations": ["Client acclaim"], "core_values": ["Accessibility", "Inclusivity"]},
                    challenges={"pain_points": ["Client invoicing & contract chasing", "Scattered feedback across email and Slack"], "daily_frustrations": ["Exporting design specs manually"], "workflow_blockers": ["Lack of integrated project management"]},
                    behaviour={"decision_making_style": "Intuitive & visual", "purchasing_behavior": "Buys sleek subscription apps", "media_consumption": ["Dribbble", "Sidebar.io"], "discovery_channels": ["Twitter/X", "Design Communities"]},
                    personality_traits={"big_five_summary": {"Openness": "Very High"}, "key_traits": ["Empathetic", "Creative", "Adaptive"], "communication_style": "Warm & expressive", "attitude_towards_change": "Pioneer"},
                    technical_skills={"overall_proficiency": "Advanced", "domain_expertise": ["Figma", "Design Systems", "Prototyping"], "software_proficiency": {"Figma": "Expert", "Webflow": "Advanced"}},
                    technology_usage={"primary_devices": ["MacBook Air", "iPad Pro"], "operating_systems": ["macOS", "iOS"], "favorite_apps": ["Figma", "Linear", "Cron"], "daily_screen_time_hours": 9.0, "tech_adoption_stage": "Innovator"},
                    quote="Design should feel effortless and inclusive; every detail matters."
                )
            ]
            
            selected = personas_pool[:num_personas]
            if len(selected) < num_personas:
                selected = personas_pool * ((num_personas // len(personas_pool)) + 1)
                selected = selected[:num_personas]
            return PersonaCohort(personas=selected)

        # -------------------------------------------------------------
        # 2. SURVEY MODE (PersonaSurveyAnswers structured output)
        # -------------------------------------------------------------
        if schema_name == "PersonaSurveyAnswers":
            from app.agent.survey_agent import PersonaSurveyAnswers
            from app.models.survey import QuestionAnswerPair
            
            full_name = "User"
            occupation = "Professional"
            goals = "productivity"
            pain_points = "friction"
            quote = "I value clarity."
            questions = ["What is your opinion?"]

            if isinstance(input, dict):
                full_name = input.get("full_name", full_name)
                occupation = input.get("occupation", occupation)
                goals = input.get("goals", goals)
                pain_points = input.get("pain_points", pain_points)
                quote = input.get("quote", quote)
                
                raw_q = input.get("questions_formatted", "")
                parsed_q = [line.split(". ", 1)[-1].strip() for line in raw_q.split("\n") if line.strip() and ". " in line]
                if parsed_q:
                    questions = parsed_q

            answers = []
            for q in questions:
                q_lower = q.lower()
                
                if "grocery" in q_lower or "delivery" in q_lower or "food" in q_lower:
                    if "marketing" in occupation.lower() or "developer" in occupation.lower() or "designer" in occupation.lower():
                        ans = f"As a {occupation}, convenience, speed, and real-time delivery tracking are the most critical factors for me. Because my work schedule is hybrid and fast-paced, I need accurate delivery time windows and a clean app interface with zero friction."
                    elif "logistics" in occupation.lower() or "operations" in occupation.lower():
                        ans = f"Working in {occupation}, inventory accuracy and reliable delivery fulfillment matter most to me. If items are frequently out of stock or substitutions are poor, I won't use the service. Pricing transparency and dependable scheduled slots are essential."
                    else:
                        ans = f"For me as {full_name}, quality of fresh produce and dependable on-time delivery are the main priorities. I look for reasonable delivery fees and seamless reordering."
                
                elif "factor" in q_lower or "choose" in q_lower or "software" in q_lower or "tool" in q_lower or "app" in q_lower:
                    ans = f"When choosing a solution, I prioritize ease of use, speed, and whether it directly resolves my biggest pain point: {pain_points}. As {full_name} ({occupation}), I look for clean workflows that help me achieve my goal to {goals}."
                
                elif "frustration" in q_lower or "challenge" in q_lower or "friction" in q_lower:
                    ans = f"My biggest frustration is definitely {pain_points}. Clunky navigation and slow sync times disrupt my daily rhythm as a {occupation}."
                
                else:
                    ans = f"From my perspective as {full_name} ({occupation}), '{q.strip('?')}' is closely tied to my goals ({goals}). In my experience, {quote.strip('\"')} Having a straightforward, dependable experience is what matters most."
                
                answers.append(QuestionAnswerPair(question=q, answer=ans))

            return PersonaSurveyAnswers(answers=answers)

        # -------------------------------------------------------------
        # 3. INTERVIEW MODE (Context-Aware Multi-Turn Dialogue)
        # -------------------------------------------------------------
        persona_name = "Synthetic User"
        occupation = "Professional"
        goals = []
        pain_points = []
        quote = ""
        user_query = ""
        conversation_history: List[Dict[str, str]] = []

        if isinstance(input, list):
            for msg in input:
                content = getattr(msg, "content", str(msg))
                if isinstance(msg, SystemMessage):
                    # Parse persona profile from system prompt
                    m_name = re.search(r"participant named\s+([^.\n]+)", content)
                    if m_name:
                        persona_name = m_name.group(1).strip()
                    m_occ = re.search(r"Occupation:\s+([^(\n]+)", content)
                    if m_occ:
                        occupation = m_occ.group(1).strip()
                    m_goals = re.search(r"Primary Goals:\s+([^\n]+)", content)
                    if m_goals:
                        goals = [g.strip() for g in m_goals.group(1).split(",") if g.strip()]
                    m_quote = re.search(r"Representative Quote:\s+\"([^\"]+)\"", content)
                    if m_quote:
                        quote = m_quote.group(1).strip()
                elif isinstance(msg, HumanMessage):
                    conversation_history.append({"role": "user", "content": content})
                    user_query = content
                elif isinstance(msg, AIMessage):
                    conversation_history.append({"role": "assistant", "content": content})

        q_clean = user_query.lower()

        # Check for context references to previous questions (Multi-turn Memory!)
        has_prev_assistant_turns = any(h["role"] == "assistant" for h in conversation_history[:-1])
        prev_assistant_answers = [h["content"] for h in conversation_history[:-1] if h["role"] == "assistant"]
        last_assistant_answer = prev_assistant_answers[-1] if prev_assistant_answers else ""

        # Multi-turn memory query: "What responsibilities do you have in that role / in that job?"
        if any(w in q_clean for w in ["responsibility", "responsibilities", "duties", "in that role", "in that job", "that position"]):
            reply = (
                f"In my role as a {occupation}, my day-to-day responsibilities focus on managing end-to-end workflows, "
                f"collaborating across cross-functional teams, and ensuring we meet our performance milestones. "
                f"I spend a lot of time monitoring metrics, solving operational bottlenecks, and optimizing our processes."
            )

        # Multi-turn memory query: "What did you say / career goal / what was your goal?"
        elif any(w in q_clean for w in ["what did you say", "what was your", "earlier", "career goal", "mention your goal", "biggest goal"]):
            if goals:
                goal_str = ", and to ".join(goals)
                reply = (
                    f"As I mentioned earlier, my primary career goal is to {goal_str}. "
                    f"Achieving that is really important to me because it allows me to make a bigger impact in my role as a {occupation}."
                )
            elif "career" in last_assistant_answer.lower() or "goal" in last_assistant_answer.lower():
                reply = (
                    f"Yes! As I shared previously, my main goal is focused on advancing my skill set and streamlining team operations "
                    f"so that we can scale efficiently without manual friction."
                )
            else:
                reply = (
                    f"My biggest career goal is to master modern tools in my field and advance into a senior leadership role, "
                    f"helping my team eliminate repetitive busywork."
                )

        # Occupation query: "What is your current occupation / job / what do you do?"
        elif any(w in q_clean for w in ["occupation", "job", "what do you do", "profession", "title"]):
            reply = (
                f"I am a {occupation}. In my daily work, I focus on executing projects, coordinating with stakeholders, "
                f"and finding ways to make our workflows more efficient."
            )

        # Frustrations / pain points query
        elif any(w in q_clean for w in ["frustration", "pain point", "annoy", "struggle", "challenge", "hardest"]):
            reply = (
                f"The biggest challenge in my daily routine is dealing with fragmented tools and slow, repetitive manual tasks. "
                f"When software is clunky or unintuitive, it takes away valuable time from high-impact work."
            )

        # Generic / Fallback in-character reply
        else:
            quote_mention = f' "{quote}"' if quote else ""
            reply = (
                f"From my perspective as {persona_name} ({occupation}), that is an important point regarding '{user_query.strip('?')}'. "
                f"In my workflow, I prioritize reliability, clear value, and simplicity.{quote_mention}"
            )

        return AIMessage(content=reply)


def get_llm(provider: str = "gemini", model_name: Optional[str] = None) -> BaseChatModel:
    """
    Factory function returning a configured LangChain ChatModel for Gemini or OpenAI.
    Supports explicit 'mock' provider, and gracefully falls back to MockChatModel
    if API keys or network connection are unavailable.
    """
    selected_provider = (provider or settings.LLM_PROVIDER or "gemini").lower().strip()

    if selected_provider == "mock":
        print("[LLM Factory] Explicit 'mock' provider selected. Using MockChatModel.")
        return MockChatModel()

    elif selected_provider == "gemini":
        api_key = settings.GOOGLE_API_KEY
        if not api_key:
            import os
            api_key = os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")

        if api_key:
            try:
                model = model_name or settings.DEFAULT_GEMINI_MODEL
                return ChatGoogleGenerativeAI(
                    model=model,
                    google_api_key=api_key,
                    temperature=0.7,
                )
            except Exception as e:
                print(f"[LLM Factory] Could not instantiate Gemini LLM ({e}), falling back to MockChatModel.")
                return MockChatModel()
        else:
            print("[LLM Factory] No Gemini API key found, using MockChatModel fallback.")
            return MockChatModel()

    elif selected_provider == "openai":
        api_key = settings.OPENAI_API_KEY
        if not api_key:
            import os
            api_key = os.getenv("OPENAI_API_KEY", "")

        if api_key:
            try:
                model = model_name or settings.DEFAULT_OPENAI_MODEL
                return ChatOpenAI(
                    model=model,
                    api_key=api_key,
                    temperature=0.7,
                )
            except Exception as e:
                print(f"[LLM Factory] Could not instantiate OpenAI LLM ({e}), falling back to MockChatModel.")
                return MockChatModel()
        else:
            print("[LLM Factory] No OpenAI API key found, using MockChatModel fallback.")
            return MockChatModel()

    else:
        print(f"[LLM Factory] Unknown provider '{selected_provider}'. Falling back to MockChatModel.")
        return MockChatModel()
