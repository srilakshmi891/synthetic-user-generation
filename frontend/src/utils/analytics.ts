import type { StoredPersona } from '../types/persona';

export interface DistributionItem {
  name: string;
  value: number;
}

export function countBy<T>(
  items: T[],
  keyFn: (item: T) => string
): DistributionItem[] {
  const map = new Map<string, number>();
  for (const item of items) {
    const key = keyFn(item) || 'Unknown';
    map.set(key, (map.get(key) ?? 0) + 1);
  }
  return Array.from(map.entries())
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value);
}

export function ageDistribution(personas: StoredPersona[]): DistributionItem[] {
  const buckets = [
    { name: '18-24', min: 18, max: 24 },
    { name: '25-34', min: 25, max: 34 },
    { name: '35-44', min: 35, max: 44 },
    { name: '45-54', min: 45, max: 54 },
    { name: '55+', min: 55, max: 120 },
  ];
  const counts = buckets.map((b) => ({
    name: b.name,
    value: personas.filter(
      (p) => p.demographics.age >= b.min && p.demographics.age <= b.max
    ).length,
  }));
  return counts.filter((c) => c.value > 0);
}

export function topGoals(personas: StoredPersona[], limit = 8): DistributionItem[] {
  const map = new Map<string, number>();
  for (const p of personas) {
    for (const goal of p.goals.primary_goals) {
      map.set(goal, (map.get(goal) ?? 0) + 1);
    }
  }
  return Array.from(map.entries())
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value)
    .slice(0, limit);
}

export function topPainPoints(personas: StoredPersona[], limit = 8): DistributionItem[] {
  const map = new Map<string, number>();
  for (const p of personas) {
    for (const pain of p.challenges.pain_points) {
      map.set(pain, (map.get(pain) ?? 0) + 1);
    }
  }
  return Array.from(map.entries())
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value)
    .slice(0, limit);
}

export function skillFrequency(personas: StoredPersona[], limit = 10): DistributionItem[] {
  const map = new Map<string, number>();
  for (const p of personas) {
    for (const skill of p.technical_skills.domain_expertise) {
      map.set(skill, (map.get(skill) ?? 0) + 1);
    }
  }
  return Array.from(map.entries())
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value)
    .slice(0, limit);
}

export function generationTrend(personas: StoredPersona[]): DistributionItem[] {
  const map = new Map<string, number>();
  for (const p of personas) {
    const day = new Date(p.createdAt).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    });
    map.set(day, (map.get(day) ?? 0) + 1);
  }
  return Array.from(map.entries())
    .map(([name, value]) => ({ name, value }))
    .slice(0, 7)
    .reverse();
}

export function averageAge(personas: StoredPersona[]): number {
  if (!personas.length) return 0;
  const sum = personas.reduce((acc, p) => acc + p.demographics.age, 0);
  return Math.round(sum / personas.length);
}

export function uniqueIndustries(personas: StoredPersona[]): number {
  return new Set(personas.map((p) => p.occupation.industry)).size;
}
