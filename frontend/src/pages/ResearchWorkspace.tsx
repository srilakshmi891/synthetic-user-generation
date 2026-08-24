import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, AlertCircle, CheckCircle2 } from 'lucide-react';
import { Card, CardHeader } from '../components/ui/Card';
import { Textarea } from '../components/ui/Textarea';
import { Input } from '../components/ui/Input';
import { Select } from '../components/ui/Select';
import { Button } from '../components/ui/Button';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { Badge } from '../components/ui/Badge';
import { api, ApiError } from '../services/api';
import { usePersonas } from '../context/PersonaContext';
import { createStoredPersona } from '../utils/format';
import type { GeneratePersonaRequest } from '../types/persona';

const PROVIDER_MODELS: Record<string, { value: string; label: string }[]> = {
  gemini: [
    { value: '', label: 'Default (gemini-2.5-flash)' },
    { value: 'gemini-2.5-flash', label: 'Gemini 2.5 Flash' },
    { value: 'gemini-1.5-pro', label: 'Gemini 1.5 Pro' },
  ],
  openai: [
    { value: '', label: 'Default (gpt-4o)' },
    { value: 'gpt-4o', label: 'GPT-4o' },
    { value: 'gpt-4o-mini', label: 'GPT-4o Mini' },
  ],
};

export function ResearchWorkspace() {
  const navigate = useNavigate();
  const { addPersonas } = usePersonas();

  const [form, setForm] = useState({
    product_description: '',
    target_audience: '',
    research_objective: '',
    number_of_personas: 3,
    provider: 'gemini' as 'gemini' | 'openai',
    model_name: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);
  const [successCount, setSuccessCount] = useState<number | null>(null);

  const validate = (): boolean => {
    const next: Record<string, string> = {};
    if (form.product_description.length < 10) {
      next.product_description = 'Minimum 10 characters required';
    }
    if (form.target_audience.length < 5) {
      next.target_audience = 'Minimum 5 characters required';
    }
    if (form.research_objective.length < 10) {
      next.research_objective = 'Minimum 10 characters required';
    }
    if (form.number_of_personas < 1 || form.number_of_personas > 100) {
      next.number_of_personas = 'Must be between 1 and 100';
    }
    setErrors(next);
    return Object.keys(next).length === 0;
  };

  const handleGenerate = async () => {
    if (!validate()) return;
    setLoading(true);
    setApiError(null);
    setSuccessCount(null);

    const payload: GeneratePersonaRequest = {
      product_description: form.product_description,
      target_audience: form.target_audience,
      research_objective: form.research_objective,
      number_of_personas: form.number_of_personas,
      provider: form.provider,
      model_name: form.model_name || null,
    };

    try {
      const response = await api.generatePersonas(payload);
      const sessionMeta = {
        productDescription: form.product_description,
        targetAudience: form.target_audience,
        researchObjective: form.research_objective,
        provider: form.provider,
        modelName: form.model_name || undefined,
        numberOfPersonas: form.number_of_personas,
      };
      const stored = response.personas.map((p) => createStoredPersona(p, sessionMeta));
      addPersonas(stored);
      setSuccessCount(stored.length);
      setTimeout(() => navigate('/personas'), 1500);
    } catch (err) {
      if (err instanceof ApiError) {
        setApiError(err.detail ?? err.message);
      } else {
        setApiError('An unexpected error occurred. Ensure the backend is running on port 8000.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <Card>
        <CardHeader
          title="Research Configuration"
          subtitle="Define your study parameters and generate a diverse cohort of synthetic users"
        />

        <AnimatePresence mode="wait">
          {loading ? (
            <motion.div
              key="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <LoadingSpinner message={`Generating ${form.number_of_personas} unique personas…`} />
              <p className="mt-2 text-center text-xs text-slate-400">
                This may take 30–90 seconds depending on cohort size
              </p>
            </motion.div>
          ) : (
            <motion.div
              key="form"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="space-y-6"
            >
              <Textarea
                label="Product Description"
                placeholder="Describe the product or service you're researching…"
                rows={4}
                value={form.product_description}
                onChange={(e) => setForm({ ...form, product_description: e.target.value })}
                error={errors.product_description}
              />
              <Textarea
                label="Target Audience"
                placeholder="Define your target user segment…"
                rows={3}
                value={form.target_audience}
                onChange={(e) => setForm({ ...form, target_audience: e.target.value })}
                error={errors.target_audience}
              />
              <Textarea
                label="Research Objective"
                placeholder="What do you want to learn from this research?"
                rows={3}
                value={form.research_objective}
                onChange={(e) => setForm({ ...form, research_objective: e.target.value })}
                error={errors.research_objective}
              />

              <div className="grid gap-6 sm:grid-cols-3">
                <Input
                  label="Number of Personas"
                  type="number"
                  min={1}
                  max={100}
                  value={form.number_of_personas}
                  onChange={(e) =>
                    setForm({ ...form, number_of_personas: parseInt(e.target.value, 10) || 1 })
                  }
                  error={errors.number_of_personas}
                />
                <Select
                  label="AI Provider"
                  value={form.provider}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      provider: e.target.value as 'gemini' | 'openai' | 'mock',
                      model_name: '',
                    })
                  }
                  options={[
                    { value: 'gemini', label: 'Google Gemini' },
                    { value: 'mock', label: 'Mock Model (Dev/Offline)' },
                    { value: 'openai', label: 'OpenAI GPT-4' },
                  ]}
                />
                <Select
                  label="Model"
                  value={form.model_name}
                  onChange={(e) => setForm({ ...form, model_name: e.target.value })}
                  options={PROVIDER_MODELS[form.provider as 'gemini' | 'openai'] ?? [{ value: '', label: 'Default Mock' }]}
                />
              </div>

              <div className="flex flex-wrap gap-2">
                <Badge variant="brand">1–100 personas</Badge>
                <Badge>Structured output</Badge>
                <Badge variant="accent">Validated cohort</Badge>
              </div>

              {apiError && (
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 rounded-xl bg-amber-50 p-3.5 text-xs text-amber-800 border border-amber-200 shadow-2xs">
                  <div className="flex items-center gap-2">
                    <AlertCircle className="h-4 w-4 shrink-0 text-amber-600" />
                    <span>{apiError}</span>
                  </div>
                  {form.provider !== 'mock' && (
                    <Button
                      size="sm"
                      variant="secondary"
                      className="text-xs bg-white hover:bg-amber-100 text-amber-900 border border-amber-300 shrink-0"
                      onClick={() => {
                        setForm({ ...form, provider: 'mock', model_name: '' });
                        setApiError(null);
                      }}
                    >
                      Switch to Mock Mode
                    </Button>
                  )}
                </div>
              )}


              {successCount !== null && (
                <div className="flex items-center gap-3 rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-700">
                  <CheckCircle2 className="h-5 w-5" />
                  Successfully generated {successCount} personas. Redirecting to gallery…
                </div>
              )}

              <div className="flex justify-end pt-2">
                <Button
                  size="lg"
                  onClick={handleGenerate}
                  icon={<Sparkles className="h-5 w-5" />}
                >
                  Generate Personas
                </Button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </Card>
    </div>
  );
}
