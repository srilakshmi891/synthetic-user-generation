import type { InterviewSession, StoredPersona } from '../types/persona';

const PERSONAS_KEY = 'synthresearch_personas';
const INTERVIEWS_KEY = 'synthresearch_interviews';

export function loadPersonas(): StoredPersona[] {
  try {
    const raw = localStorage.getItem(PERSONAS_KEY);
    return raw ? (JSON.parse(raw) as StoredPersona[]) : [];
  } catch {
    return [];
  }
}

export function savePersonas(personas: StoredPersona[]): void {
  localStorage.setItem(PERSONAS_KEY, JSON.stringify(personas));
}

export function addPersonas(
  personas: StoredPersona[],
  incoming: StoredPersona[]
): StoredPersona[] {
  const merged = [...incoming, ...personas];
  savePersonas(merged);
  return merged;
}

export function getPersonaById(id: string): StoredPersona | undefined {
  return loadPersonas().find((p) => p.id === id);
}

export function loadInterviews(): Record<string, InterviewSession> {
  try {
    const raw = localStorage.getItem(INTERVIEWS_KEY);
    return raw ? (JSON.parse(raw) as Record<string, InterviewSession>) : {};
  } catch {
    return {};
  }
}

export function saveInterview(session: InterviewSession): void {
  const all = loadInterviews();
  all[session.personaId] = session;
  localStorage.setItem(INTERVIEWS_KEY, JSON.stringify(all));
}

export function getInterview(personaId: string): InterviewSession | undefined {
  return loadInterviews()[personaId];
}
