import { useState, useEffect, useRef } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  MessageSquare,
  Send,
  Trash2,
  UserCheck,
  Sparkles,
  Bot,
  User,
  AlertCircle,
  ArrowLeft,
} from 'lucide-react';
import { usePersonas } from '../context/PersonaContext';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { api, ApiError } from '../services/api';
import type { ChatMessage, ComprehensivePersona } from '../types/persona';

const SUGGESTED_PROMPTS = [
  'What is your current job and daily workflow?',
  'What is your biggest frustration when using new software?',
  'What features do you value most in a product?',
  'Why is flexibility and ease of use important to you?',
];

export function InterviewWorkspace() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { personas, isLoading: isContextLoading } = usePersonas();

  const [selectedPersonaId, setSelectedPersonaId] = useState<string>('');
  const [provider, setProvider] = useState<'gemini' | 'mock' | 'openai'>('gemini');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputQuestion, setInputQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize selected persona from URL query param or first available persona
  useEffect(() => {
    const paramId = searchParams.get('personaId');
    if (paramId && personas.some((p) => p.id === paramId)) {
      setSelectedPersonaId(paramId);
    } else if (personas.length > 0 && !selectedPersonaId) {
      setSelectedPersonaId(personas[0].id);
    }
  }, [personas, searchParams]);

  const selectedPersona: ComprehensivePersona | undefined = personas.find(
    (p) => p.id === selectedPersonaId
  );

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (questionToSend?: string) => {
    const query = (questionToSend ?? inputQuestion).trim();
    if (!query || !selectedPersona || loading) return;

    setInputQuestion('');
    setError(null);

    const userMessage: ChatMessage = {
      id: `usr_${Date.now()}`,
      role: 'user',
      content: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
      const res = await api.interview({
        persona: selectedPersona,
        session_id: `session_${selectedPersonaId}`,
        user_question: query,
        provider: provider,
      });

      setMessages(res.history);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.detail ?? err.message);
      } else {
        setError('Failed to reach backend server. Ensure Uvicorn is running on port 8000.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleClearHistory = async () => {
    if (!selectedPersona) return;
    try {
      const personaIdSlug =
        selectedPersona.basic_info.persona_id ||
        selectedPersona.basic_info.full_name.toLowerCase().replace(/\s+/g, '_');
      await api.clearInterviewMemory({
        persona_id: personaIdSlug,
        session_id: `session_${selectedPersonaId}`,
      });
      setMessages([]);
      setError(null);
    } catch (err) {
      console.error('Failed to clear memory:', err);
    }
  };

  if (isContextLoading) {
    return <LoadingSpinner message="Loading personas..." />;
  }

  if (personas.length === 0) {
    return (
      <div className="mx-auto max-w-2xl py-12 text-center">
        <Card className="p-8">
          <MessageSquare className="mx-auto h-12 w-12 text-brand-500" />
          <h2 className="mt-4 text-xl font-bold text-slate-900">No Personas Available</h2>
          <p className="mt-2 text-sm text-slate-600">
            Generate synthetic user personas in the Research Workspace first before starting an interview session.
          </p>
          <Button className="mt-6" onClick={() => navigate('/workspace')}>
            Go to Research Workspace
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      {/* Header Bar */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" onClick={() => navigate('/personas')}>
              <ArrowLeft className="h-4 w-4" />
            </Button>
            <h1 className="text-2xl font-bold text-slate-900">Interactive Persona Interview</h1>
          </div>
          <p className="mt-1 text-sm text-slate-500">
            Conduct multi-turn research interviews with synthetic user personas with persistent memory.
          </p>
        </div>

        {/* Controls: Provider & Persona Selector */}
        <div className="flex flex-wrap items-center gap-3">
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

          <div className="flex items-center gap-2">
            <label className="text-xs font-semibold uppercase tracking-wider text-slate-500">
              Persona:
            </label>
            <select
              value={selectedPersonaId}
              onChange={(e) => {
                setSelectedPersonaId(e.target.value);
                setMessages([]);
              }}
              className="rounded-xl border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-800 shadow-sm transition-colors focus:border-brand-400 focus:outline-none"
            >
              {personas.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.basic_info.full_name} ({p.occupation.job_title})
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>


      {selectedPersona && (
        <div className="grid gap-6 lg:grid-cols-4">
          {/* Persona Sidebar Profile */}
          <Card className="lg:col-span-1 space-y-4 p-5">
            <div className="flex flex-col items-center text-center">
              <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-tr from-brand-600 to-accent-600 text-xl font-bold text-white shadow-md">
                {selectedPersona.basic_info.full_name.charAt(0)}
              </div>
              <h3 className="mt-3 text-lg font-bold text-slate-900">
                {selectedPersona.basic_info.full_name}
              </h3>
              <p className="text-xs font-medium text-brand-600">
                {selectedPersona.occupation.job_title}
              </p>
              <p className="text-xs text-slate-500">
                {selectedPersona.demographics.age} yrs • {selectedPersona.demographics.location}
              </p>
            </div>

            <div className="border-t border-slate-100 pt-3 space-y-2 text-xs text-slate-600">
              <div>
                <span className="font-semibold text-slate-800">Bio:</span>{' '}
                <p className="mt-0.5 line-clamp-3 text-slate-500">{selectedPersona.basic_info.bio}</p>
              </div>
              <div>
                <span className="font-semibold text-slate-800">Primary Goal:</span>{' '}
                <p className="mt-0.5 text-slate-500">
                  {selectedPersona.goals.primary_goals[0] ?? 'N/A'}
                </p>
              </div>
              <div>
                <span className="font-semibold text-slate-800">Key Pain Point:</span>{' '}
                <p className="mt-0.5 text-slate-500">
                  {selectedPersona.challenges.pain_points[0] ?? 'N/A'}
                </p>
              </div>
              <div className="rounded-lg bg-brand-50 p-2.5 text-[11px] font-medium text-brand-800 italic border border-brand-100">
                "{selectedPersona.quote}"
              </div>
            </div>

            <Button
              variant="outline"
              size="sm"
              className="w-full text-xs text-red-600 hover:bg-red-50 hover:border-red-200"
              onClick={handleClearHistory}
            >
              <Trash2 className="mr-1.5 h-3.5 w-3.5" /> Clear Session Memory
            </Button>
          </Card>

          {/* Main Chat Interface */}
          <Card className="flex h-[600px] flex-col lg:col-span-3 p-0 overflow-hidden">
            {/* Chat Messages Stream */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-slate-50/50">
              {messages.length === 0 ? (
                <div className="flex h-full flex-col items-center justify-center text-center p-6">
                  <div className="rounded-2xl bg-brand-100 p-4 text-brand-600 mb-3">
                    <Sparkles className="h-8 w-8" />
                  </div>
                  <h4 className="text-base font-bold text-slate-800">
                    Start Interviewing {selectedPersona.basic_info.full_name}
                  </h4>
                  <p className="mt-1 max-w-sm text-xs text-slate-500">
                    Ask questions regarding workflow, priorities, security concerns, or product opinions. Memory is maintained automatically.
                  </p>

                  <div className="mt-6 flex flex-wrap justify-center gap-2 max-w-md">
                    {SUGGESTED_PROMPTS.map((prompt, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleSend(prompt)}
                        className="rounded-xl border border-slate-200 bg-white px-3 py-1.5 text-xs text-slate-700 hover:border-brand-400 hover:bg-brand-50 hover:text-brand-700 transition-all shadow-2xs"
                      >
                        "{prompt}"
                      </button>
                    ))}
                  </div>
                </div>
              ) : (
                messages.map((msg, idx) => (
                  <motion.div
                    key={msg.id ?? idx}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`flex gap-3 ${
                      msg.role === 'user' ? 'justify-end' : 'justify-start'
                    }`}
                  >
                    {msg.role === 'assistant' && (
                      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-brand-600 text-white font-bold text-xs shadow-sm">
                        {selectedPersona.basic_info.full_name.charAt(0)}
                      </div>
                    )}

                    <div
                      className={`max-w-lg rounded-2xl px-4 py-3 text-sm shadow-2xs ${
                        msg.role === 'user'
                          ? 'bg-gradient-to-r from-brand-600 to-accent-600 text-white rounded-br-none'
                          : 'bg-white text-slate-800 border border-slate-200/80 rounded-bl-none'
                      }`}
                    >
                      {msg.role === 'assistant' && (
                        <p className="mb-1 text-[10px] font-bold uppercase tracking-wider text-brand-600">
                          {selectedPersona.basic_info.full_name}
                        </p>
                      )}
                      <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
                    </div>

                    {msg.role === 'user' && (
                      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-slate-800 text-white font-bold text-xs">
                        <User className="h-4 w-4" />
                      </div>
                    )}
                  </motion.div>
                ))
              )}

              {loading && (
                <div className="flex items-center gap-3 text-xs text-slate-500 pl-2">
                  <LoadingSpinner size="sm" />
                  <span>{selectedPersona.basic_info.full_name} is typing a response...</span>
                </div>
              )}

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


              <div ref={messagesEndRef} />
            </div>

            {/* Input Bar */}
            <div className="border-t border-slate-200 bg-white p-4">
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleSend();
                }}
                className="flex gap-2"
              >
                <input
                  type="text"
                  placeholder={`Ask ${selectedPersona.basic_info.full_name} a question...`}
                  value={inputQuestion}
                  onChange={(e) => setInputQuestion(e.target.value)}
                  disabled={loading}
                  className="flex-1 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-500/20"
                />
                <Button type="submit" disabled={loading || !inputQuestion.trim()} icon={<Send className="h-4 w-4" />}>
                  Send
                </Button>
              </form>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
