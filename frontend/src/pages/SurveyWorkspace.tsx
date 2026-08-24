import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  FileQuestion,
  Users,
  Sparkles,
  Plus,
  Trash2,
  AlertCircle,
  ArrowLeft,
  CheckSquare,
  Square,
} from 'lucide-react';
import { usePersonas } from '../context/PersonaContext';
import { Card, CardHeader } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Textarea } from '../components/ui/Textarea';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { api, ApiError } from '../services/api';
import type { SurveyResponse, SurveyPersonaResult } from '../types/persona';

export function SurveyWorkspace() {
  const navigate = useNavigate();
  const { personas, isLoading: isContextLoading } = usePersonas();

  const [selectedPersonaIds, setSelectedPersonaIds] = useState<string[]>(
    personas.map((p) => p.id)
  );
  const [questions, setQuestions] = useState<string[]>([
    'What is your biggest frustration when adopting new technology or software?',
  ]);
  const [productContext, setProductContext] = useState<string>('');

  const [provider, setProvider] = useState<'gemini' | 'mock' | 'openai'>('gemini');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [surveyResponse, setSurveyResponse] = useState<SurveyResponse | null>(null);

  // Sync selection if personas load asynchronously
  if (selectedPersonaIds.length === 0 && personas.length > 0 && !surveyResponse) {
    setSelectedPersonaIds(personas.map((p) => p.id));
  }

  const togglePersona = (id: string) => {
    setSelectedPersonaIds((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
    );
  };

  const selectAll = () => {
    setSelectedPersonaIds(personas.map((p) => p.id));
  };

  const clearSelection = () => {
    setSelectedPersonaIds([]);
  };

  const handleAddQuestion = () => {
    setQuestions((prev) => [...prev, '']);
  };

  const handleRemoveQuestion = (index: number) => {
    setQuestions((prev) => prev.filter((_, i) => i !== index));
  };

  const handleQuestionChange = (index: number, val: string) => {
    setQuestions((prev) => {
      const copy = [...prev];
      copy[index] = val;
      return copy;
    });
  };

  const handleRunSurvey = async () => {
    const validQuestions = questions.map((q) => q.trim()).filter((q) => q.length > 0);
    const selectedPersonas = personas.filter((p) => selectedPersonaIds.includes(p.id));

    if (selectedPersonas.length === 0) {
      setError('Please select at least one persona to survey.');
      return;
    }
    if (validQuestions.length === 0) {
      setError('Please provide at least one valid survey question.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await api.survey({
        personas: selectedPersonas,
        questions: validQuestions,
        product_context: productContext.trim() || undefined,
        provider: provider,
      });
      setSurveyResponse(res);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.detail ?? err.message);
      } else {
        setError('Survey execution failed. Ensure backend server is running.');
      }
    } finally {
      setLoading(false);
    }
  };

  if (isContextLoading) {
    return <LoadingSpinner message="Loading personas..." />;
  }

  if (personas.length === 0) {
    return (
      <div className="mx-auto max-w-2xl py-12 text-center">
        <Card className="p-8">
          <FileQuestion className="mx-auto h-12 w-12 text-brand-500" />
          <h2 className="mt-4 text-xl font-bold text-slate-900">No Personas Available</h2>
          <p className="mt-2 text-sm text-slate-600">
            Generate synthetic user personas in the Research Workspace first before running a cohort survey.
          </p>
          <Button className="mt-6" onClick={() => navigate('/workspace')}>
            Go to Research Workspace
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-6xl space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Side-by-Side Persona Survey</h1>
          <p className="mt-1 text-sm text-slate-500">
            Ask identical research questions across multiple personas simultaneously to compare cohort responses.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <label className="text-xs font-semibold uppercase tracking-wider text-slate-500">
              Provider:
            </label>
            <select
              value={provider}
              onChange={(e) => setProvider(e.target.value as any)}
              className="rounded-xl border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-800 shadow-sm transition-colors focus:border-brand-400 focus:outline-none"
            >
              <option value="gemini">Gemini (Google AI)</option>
              <option value="mock">Mock Model (Dev/Offline)</option>
              <option value="openai">OpenAI</option>
            </select>
          </div>

          {surveyResponse && (
            <Button variant="outline" size="sm" onClick={() => setSurveyResponse(null)}>
              <ArrowLeft className="mr-1.5 h-4 w-4" /> Edit Survey
            </Button>
          )}
        </div>
      </div>


      {!surveyResponse ? (
        <div className="grid gap-6 lg:grid-cols-3">
          {/* Persona Selection Panel */}
          <Card className="lg:col-span-1 space-y-4">
            <CardHeader
              title="Select Cohort"
              subtitle={`${selectedPersonaIds.length} of ${personas.length} personas selected`}
            />

            <div className="flex gap-2 text-xs font-semibold">
              <button
                onClick={selectAll}
                className="text-brand-600 hover:underline flex items-center gap-1"
              >
                <CheckSquare className="h-3.5 w-3.5" /> Select All
              </button>
              <span className="text-slate-300">|</span>
              <button
                onClick={clearSelection}
                className="text-slate-500 hover:underline flex items-center gap-1"
              >
                <Square className="h-3.5 w-3.5" /> Clear All
              </button>
            </div>

            <div className="space-y-2 max-h-[380px] overflow-y-auto pr-1">
              {personas.map((persona) => {
                const isSelected = selectedPersonaIds.includes(persona.id);
                return (
                  <div
                    key={persona.id}
                    onClick={() => togglePersona(persona.id)}
                    className={`flex items-center gap-3 rounded-xl border p-3 cursor-pointer transition-all ${
                      isSelected
                        ? 'border-brand-300 bg-brand-50/60 shadow-2xs'
                        : 'border-slate-200/80 bg-white hover:bg-slate-50'
                    }`}
                  >
                    <div
                      className={`flex h-5 w-5 shrink-0 items-center justify-center rounded-md border ${
                        isSelected
                          ? 'border-brand-600 bg-brand-600 text-white'
                          : 'border-slate-300 bg-white'
                      }`}
                    >
                      {isSelected && <CheckSquare className="h-3.5 w-3.5" />}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-bold text-slate-900 truncate">
                        {persona.basic_info.full_name}
                      </p>
                      <p className="text-xs text-slate-500 truncate">
                        {persona.occupation.job_title} ({persona.demographics.age}y)
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
          </Card>

          {/* Survey Questions Form */}
          <Card className="lg:col-span-2 space-y-6">
            <CardHeader
              title="Survey Questions"
              subtitle="Enter one or more questions to pose to all selected personas"
            />

            <Textarea
              label="Optional Product Context"
              placeholder="e.g. An AI-powered personal finance mobile app automated investing platform"
              rows={2}
              value={productContext}
              onChange={(e) => setProductContext(e.target.value)}
            />

            <div className="space-y-4">
              <label className="block text-sm font-semibold text-slate-800">
                Questions ({questions.length})
              </label>

              {questions.map((q, idx) => (
                <div key={idx} className="flex gap-2 items-start">
                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-slate-100 font-bold text-xs text-slate-600 mt-1">
                    Q{idx + 1}
                  </div>
                  <input
                    type="text"
                    placeholder={`Enter survey question #${idx + 1}...`}
                    value={q}
                    onChange={(e) => handleQuestionChange(idx, e.target.value)}
                    className="flex-1 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm text-slate-900 focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-500/20"
                  />
                  {questions.length > 1 && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleRemoveQuestion(idx)}
                      className="text-slate-400 hover:text-red-600 mt-1"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              ))}

              <Button
                variant="outline"
                size="sm"
                onClick={handleAddQuestion}
                icon={<Plus className="h-4 w-4" />}
              >
                Add Another Question
              </Button>
            </div>

            {error && (
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 rounded-xl bg-amber-50 p-3.5 text-xs text-amber-800 border border-amber-200 shadow-2xs">
                <div className="flex items-center gap-2">
                  <AlertCircle className="h-4 w-4 shrink-0 text-amber-600" />
                  <span>{error}</span>
                </div>
                {provider !== 'mock' && (
                  <Button
                    size="sm"
                    variant="secondary"
                    className="text-xs bg-white hover:bg-amber-100 text-amber-900 border border-amber-300 shrink-0"
                    onClick={() => {
                      setProvider('mock');
                      setError(null);
                    }}
                  >
                    Switch to Mock Mode
                  </Button>
                )}
              </div>
            )}


            <div className="pt-2 flex justify-end">
              <Button
                size="lg"
                onClick={handleRunSurvey}
                disabled={loading}
                icon={<Sparkles className="h-5 w-5" />}
              >
                {loading ? 'Simulating Cohort Survey...' : 'Run Comparative Survey'}
              </Button>
            </div>
          </Card>
        </div>
      ) : (
        /* Results View: Side by Side Cards */
        <div className="space-y-8">
          {surveyResponse.questions.map((q, qIdx) => (
            <div key={qIdx} className="space-y-4">
              <div className="flex items-center gap-3 rounded-2xl bg-gradient-to-r from-slate-900 to-slate-800 p-5 text-white shadow-md">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-brand-500 font-bold text-white">
                  Q{qIdx + 1}
                </div>
                <h3 className="text-lg font-bold">{q}</h3>
              </div>

              <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {surveyResponse.results.map((res: SurveyPersonaResult) => {
                  const answerObj = res.answers.find((a) => a.question === q) || res.answers[qIdx];
                  return (
                    <Card key={res.persona_id} className="flex flex-col justify-between p-5 space-y-4 border-slate-200/90 shadow-sm hover:shadow-md transition-shadow">
                      <div>
                        {/* Persona Profile Header */}
                        <div className="flex items-center gap-3 border-b border-slate-100 pb-3">
                          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-tr from-brand-600 to-accent-600 font-bold text-white text-base shadow-xs">
                            {res.persona_name.charAt(0)}
                          </div>
                          <div className="min-w-0">
                            <h4 className="font-bold text-slate-900 truncate">{res.persona_name}</h4>
                            <p className="text-xs text-brand-600 font-medium truncate">{res.occupation}</p>
                            <p className="text-[11px] text-slate-400">{res.age} years old</p>
                          </div>
                        </div>

                        {/* Survey Response */}
                        <div className="mt-4">
                          <p className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5">
                            Persona Response:
                          </p>
                          <div className="rounded-xl bg-slate-50 p-4 text-sm text-slate-800 leading-relaxed border border-slate-100">
                            "{answerObj?.answer ?? 'No response'}"
                          </div>
                        </div>
                      </div>

                      {/* Mindset Quote Footer */}
                      <div className="border-t border-slate-100 pt-3 text-[11px] text-slate-500 italic">
                        Quote: "{res.quote}"
                      </div>
                    </Card>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
