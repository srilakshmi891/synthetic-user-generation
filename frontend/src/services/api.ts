import type {
  GeneratePersonaRequest,
  HealthResponse,
  PersonaGenerationResponse,
} from '../types/persona';

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? '';

class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public detail?: string
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    let detail = '';
    try {
      const body = await response.json();
      detail = typeof body.detail === 'string'
        ? body.detail
        : JSON.stringify(body.detail ?? body);
    } catch {
      detail = response.statusText;
    }
    throw new ApiError(`Request failed: ${response.status}`, response.status, detail);
  }

  return response.json() as Promise<T>;
}

export const api = {
  health: () => request<HealthResponse>('/health'),

  generatePersonas: (payload: GeneratePersonaRequest) =>
    request<PersonaGenerationResponse>('/api/v1/generate-persona', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
};

export { ApiError };
