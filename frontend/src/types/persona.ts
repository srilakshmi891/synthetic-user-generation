export interface BasicInformation {
  persona_id: string;
  full_name: string;
  avatar_description: string;
  bio: string;
}

export interface Demographics {
  age: number;
  gender: string;
  ethnicity?: string | null;
  location: string;
  marital_status: string;
  household_income: string;
}

export interface Education {
  degree_level: string;
  field_of_study: string;
  institution_type: string;
}

export interface Occupation {
  job_title: string;
  industry: string;
  company_size: string;
  work_mode: string;
  key_responsibilities: string[];
}

export interface Goals {
  primary_goals: string[];
  secondary_goals: string[];
  personal_aspirations: string[];
}

export interface Motivations {
  intrinsic_motivations: string[];
  extrinsic_motivations: string[];
  core_values: string[];
}

export interface Challenges {
  pain_points: string[];
  daily_frustrations: string[];
  workflow_blockers: string[];
}

export interface Behaviour {
  decision_making_style: string;
  purchasing_behavior: string;
  media_consumption: string[];
  discovery_channels: string[];
}

export interface PersonalityTraits {
  big_five_summary: Record<string, string>;
  key_traits: string[];
  communication_style: string;
  attitude_towards_change: string;
}

export interface TechnicalSkills {
  overall_proficiency: string;
  domain_expertise: string[];
  software_proficiency: Record<string, string>;
}

export interface TechnologyUsage {
  primary_devices: string[];
  operating_systems: string[];
  favorite_apps: string[];
  daily_screen_time_hours: number;
  tech_adoption_stage: string;
}

export interface ComprehensivePersona {
  basic_info: BasicInformation;
  demographics: Demographics;
  education: Education;
  occupation: Occupation;
  goals: Goals;
  motivations: Motivations;
  challenges: Challenges;
  behaviour: Behaviour;
  personality_traits: PersonalityTraits;
  technical_skills: TechnicalSkills;
  technology_usage: TechnologyUsage;
  quote: string;
}

export interface StoredPersona extends ComprehensivePersona {
  id: string;
  createdAt: string;
  researchSession?: ResearchSessionMeta;
}

export interface ResearchSessionMeta {
  productDescription: string;
  targetAudience: string;
  researchObjective: string;
  provider: string;
  modelName?: string;
  numberOfPersonas: number;
}

export interface GeneratePersonaRequest {
  product_description: string;
  target_audience: string;
  research_objective: string;
  number_of_personas: number;
  provider?: 'gemini' | 'openai';
  model_name?: string | null;
}

export interface PersonaGenerationResponse {
  personas: ComprehensivePersona[];
}

export interface HealthResponse {
  status: string;
  service: string;
  docs: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface InterviewSession {
  personaId: string;
  messages: ChatMessage[];
  startedAt: string;
}
