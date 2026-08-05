from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class BasicInformation(BaseModel):
    persona_id: str = Field(..., description="Unique slug or ID for system referencing.",
                            example="persona_ux_001")
    full_name: str = Field(..., description="Full synthetic name of the persona.",
                           example="Sarah Jenkins")
    avatar_description: str = Field(..., description="Visual description of the persona's appearance for UI rendering.",
                                    example="32-year-old woman with spectacles, casual tech office attire.")
    bio: str = Field(..., description="Short biographical narrative summarizing background and lifestyle.",
                     example="Sarah is a mid-level product manager working at a remote-first software company who balances a busy career with urban living.")


class Demographics(BaseModel):
    age: int = Field(..., description="Age in years.", example=32)
    gender: str = Field(..., description="Gender identity.", example="Female")
    ethnicity: Optional[str] = Field(
        None, description="Ethnic or cultural background.", example="Caucasian")
    location: str = Field(..., description="City, country, and urban density environment.",
                          example="Seattle, WA, USA (Urban)")
    marital_status: str = Field(..., description="Marital or relationship status.",
                                example="Married, no children")
    household_income: str = Field(..., description="Annual household income tier.",
                                  example="$110,000 - $130,000 USD")


class Education(BaseModel):
    degree_level: str = Field(..., description="Highest degree attained.",
                              example="Master's Degree")
    field_of_study: str = Field(..., description="Major or area of specialization.",
                                example="Human-Computer Interaction & Business")
    institution_type: str = Field(
        ..., description="Type of educational background.", example="State University")


class Occupation(BaseModel):
    job_title: str = Field(..., description="Current job title.",
                           example="Senior Product Manager")
    industry: str = Field(..., description="Industry sector.",
                          example="Enterprise B2B Software")
    company_size: str = Field(..., description="Size of employing organization.",
                              example="250-500 employees")
    work_mode: str = Field(..., description="Remote, hybrid, or in-office status.",
                           example="Hybrid (2 days office, 3 days remote)")
    key_responsibilities: List[str] = Field(
        ...,
        description="Main day-to-day job responsibilities.",
        example=["Roadmap planning",
                 "Cross-functional feature prioritization", "User interview analysis"]
    )


class Goals(BaseModel):
    primary_goals: List[str] = Field(..., description="Top work or life objectives.", example=[
                                     "Streamline team sprint velocity", "Reduce user onboarding drop-off by 20%"])
    secondary_goals: List[str] = Field(..., description="Secondary aspirational targets.", example=[
                                       "Learn SQL for self-serve analytics", "Maintain work-life balance"])
    personal_aspirations: List[str] = Field(..., description="Long-term life aspirations.", example=[
                                            "Transition into VP of Product role within 5 years"])


class Motivations(BaseModel):
    intrinsic_motivations: List[str] = Field(..., description="Internal emotional drivers.", example=[
                                             "Desire for mastery", "Solving complex human workflow problems"])
    extrinsic_motivations: List[str] = Field(..., description="External rewards or recognitions.", example=[
                                             "Career promotion", "Industry recognition", "Financial bonuses"])
    core_values: List[str] = Field(..., description="Ethical and professional principles.", example=[
                                   "Transparency", "User empathy", "Data-driven decisions"])


class Challenges(BaseModel):
    pain_points: List[str] = Field(..., description="Critical obstacles faced in current workflow.", example=[
                                   "Fragmented tools cause information silos", "Endless status meetings limit focus time"])
    daily_frustrations: List[str] = Field(..., description="Minor recurring annoyances.", example=[
                                          "Slow software loading times", "Manual status updates in Jira"])
    workflow_blockers: List[str] = Field(..., description="Hard constraints preventing progress.", example=[
                                         "Strict IT procurement cycles for new software adoption"])


class Behaviour(BaseModel):
    decision_making_style: str = Field(..., description="How choices are evaluated.",
                                       example="Analytical and evidence-based; relies heavily on metrics and peer reviews.")
    purchasing_behavior: str = Field(..., description="Software buying habits.",
                                     example="Prefers 14-day free trials before scheduling demo calls; seeks team subscription discounts.")
    media_consumption: List[str] = Field(..., description="Primary media and content sources.", example=[
                                         "TechCrunch", "Lenny's Newsletter", "UX Podcast"])
    discovery_channels: List[str] = Field(..., description="Where they discover new solutions.", example=[
                                          "LinkedIn", "Product Hunt", "Peer Slack communities"])


class PersonalityTraits(BaseModel):
    big_five_summary: Dict[str, str] = Field(
        ...,
        description="Big Five personality dimensions.",
        example={"Openness": "High", "Conscientiousness": "Very High",
                 "Extraversion": "Moderate", "Agreeableness": "High", "Neuroticism": "Low"}
    )
    key_traits: List[str] = Field(..., description="Descriptive personality keywords.", example=[
                                  "Structured", "Empathic", "Pragmatic", "Analytical"])
    communication_style: str = Field(..., description="Preferred tone and medium.",
                                     example="Direct, concise, and structured bullet points via Slack or email.")
    attitude_towards_change: str = Field(..., description="Openness to new processes.",
                                         example="Embraces change if ROI and efficiency gains are clearly proven.")


class TechnicalSkills(BaseModel):
    overall_proficiency: str = Field(
        ..., description="Level of tech literacy.", example="Advanced")
    domain_expertise: List[str] = Field(..., description="Areas of specialized knowledge.", example=[
                                        "Agile Methodologies", "User Research Synthesis", "A/B Testing"])
    software_proficiency: Dict[str, str] = Field(
        ...,
        description="Specific tools and skill rating.",
        example={"Figma": "Intermediate", "Jira": "Expert",
                 "Mixpanel": "Advanced", "Notion": "Expert"}
    )


class TechnologyUsage(BaseModel):
    primary_devices: List[str] = Field(..., description="Hardware devices used daily.", example=[
                                       "MacBook Pro 16-inch", "iPhone 15 Pro", "Dual 27-inch 4K Monitors"])
    operating_systems: List[str] = Field(..., description="OS environments.", example=[
                                         "macOS Sonoma", "iOS 17"])
    favorite_apps: List[str] = Field(..., description="Go-to daily applications.", example=[
                                     "Slack", "Notion", "Figma", "Spotify", "Superhuman"])
    daily_screen_time_hours: float = Field(
        ..., description="Average daily screen exposure.", example=9.5)
    tech_adoption_stage: str = Field(
        ..., description="Technology adoption lifecycle position.", example="Early Majority")


class ComprehensivePersona(BaseModel):
    basic_info: BasicInformation
    demographics: Demographics
    education: Education
    occupation: Occupation
    goals: Goals
    motivations: Motivations
    challenges: Challenges
    behaviour: Behaviour
    personality_traits: PersonalityTraits
    technical_skills: TechnicalSkills
    technology_usage: TechnologyUsage
    quote: str = Field(..., description="Representative verbatim quote capturing persona mindset.",
                       example="I just want a tool that eliminates manual status syncs so my team can focus on building great products.")


class PersonaCohort(BaseModel):
    """
    Structured LLM output wrapper for generating one or more personas in a single response.
    Individual ComprehensivePersona field schemas remain unchanged.
    """
    personas: List[ComprehensivePersona] = Field(
        ...,
        min_length=1,
        description="List of unique, diverse synthetic user personas."
    )


class ArchetypePlan(BaseModel):
    title: str
    key_differentiator: str
    target_demographic_focus: str


class ArchetypePlanList(BaseModel):
    archetypes: List[ArchetypePlan]
