import type { StoredPersona } from '../types/persona';
import type { ChatMessage } from '../types/persona';

const SUGGESTED_PROMPTS = [
  'What are your biggest frustrations with current tools?',
  'Walk me through how you would evaluate a new product.',
  'What would make you switch from your current solution?',
  'Describe your ideal onboarding experience.',
  'What security concerns do you have?',
  'How do you prefer to learn about new features?',
];

export function getSuggestedPrompts(): string[] {
  return SUGGESTED_PROMPTS;
}

function pickRandom<T>(arr: T[]): T {
  return arr[Math.floor(Math.random() * arr.length)];
}

export function generatePersonaResponse(
  persona: StoredPersona,
  userMessage: string
): string {
  const lower = userMessage.toLowerCase();
  const { basic_info, challenges, goals, behaviour, motivations, occupation, quote } = persona;

  if (lower.includes('frustrat') || lower.includes('pain') || lower.includes('problem')) {
    const pain = pickRandom(challenges.pain_points);
    const frustration = challenges.daily_frustrations[0];
    return `Honestly, ${pain.toLowerCase()} is a major issue for me. ${frustration ? `Day to day, I also deal with ${frustration.toLowerCase()}.` : ''} As a ${occupation.job_title}, these things really slow me down.`;
  }

  if (lower.includes('switch') || lower.includes('change') || lower.includes('leave')) {
    return `I'd consider switching if a solution clearly addressed ${pickRandom(challenges.pain_points).toLowerCase()}. ${behaviour.purchasing_behavior} That's generally how I approach new tools — I need to see real value before committing.`;
  }

  if (lower.includes('onboard') || lower.includes('getting started') || lower.includes('setup')) {
    return `For onboarding, I want something straightforward. ${behaviour.decision_making_style} I don't have patience for lengthy setup flows — show me value in the first few minutes. My main goal right now is ${pickRandom(goals.primary_goals).toLowerCase()}.`;
  }

  if (lower.includes('security') || lower.includes('trust') || lower.includes('privacy')) {
    return `Security is non-negotiable for me. ${motivations.core_values.includes('Transparency') ? 'Transparency about data usage is key.' : 'I need to understand exactly how my data is handled.'} I'm cautious — ${behaviour.purchasing_behavior.toLowerCase()}`;
  }

  if (lower.includes('goal') || lower.includes('priority') || lower.includes('objective')) {
    const goal = pickRandom([...goals.primary_goals, ...goals.secondary_goals]);
    return `My top priority is ${goal.toLowerCase()}. Longer term, I'm focused on ${pickRandom(goals.personal_aspirations).toLowerCase()}. That shapes most of my decisions around tools and workflows.`;
  }

  if (lower.includes('evaluate') || lower.includes('decide') || lower.includes('choose')) {
    return `When evaluating options, I'm ${behaviour.decision_making_style.toLowerCase()} I typically discover products through ${pickRandom(behaviour.discovery_channels)} and ${behaviour.purchasing_behavior.toLowerCase()}`;
  }

  if (lower.includes('hello') || lower.includes('hi ') || lower.includes('hey')) {
    return `Hi! I'm ${basic_info.full_name}, a ${occupation.job_title} in ${persona.demographics.location.split(',')[0]}. Happy to share my perspective — what would you like to know?`;
  }

  return `${quote} To give you more context: as a ${occupation.job_title}, I'm driven by ${pickRandom(motivations.intrinsic_motivations).toLowerCase()}. My communication style is ${persona.personality_traits.communication_style.toLowerCase()} Feel free to ask about my workflow, goals, or pain points.`;
}

export function createMessage(role: 'user' | 'assistant', content: string): ChatMessage {
  return {
    id: crypto.randomUUID(),
    role,
    content,
    timestamp: new Date().toISOString(),
  };
}

export function exportConversation(
  persona: StoredPersona,
  messages: ChatMessage[]
): string {
  const header = `Interview with ${persona.basic_info.full_name}\n${persona.occupation.job_title} · ${persona.demographics.location}\nExported: ${new Date().toISOString()}\n${'='.repeat(60)}\n\n`;
  const body = messages
    .map((m) => `[${m.role.toUpperCase()}] ${new Date(m.timestamp).toLocaleTimeString()}\n${m.content}\n`)
    .join('\n');
  return header + body;
}
