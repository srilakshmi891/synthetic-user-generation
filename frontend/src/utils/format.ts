import type { ComprehensivePersona, StoredPersona } from '../types/persona';
import type { ResearchSessionMeta } from '../types/persona';

export function createStoredPersona(
  persona: ComprehensivePersona,
  session?: ResearchSessionMeta
): StoredPersona {
  return {
    ...persona,
    id: `${persona.basic_info.persona_id}_${Date.now()}`,
    createdAt: new Date().toISOString(),
    researchSession: session,
  };
}

export function getInitials(name: string): string {
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .slice(0, 2)
    .toUpperCase();
}

export function formatDate(iso: string): string {
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  }).format(new Date(iso));
}

export function truncate(text: string, max = 120): string {
  if (text.length <= max) return text;
  return `${text.slice(0, max).trim()}…`;
}

export function cn(...classes: (string | false | undefined | null)[]): string {
  return classes.filter(Boolean).join(' ');
}
