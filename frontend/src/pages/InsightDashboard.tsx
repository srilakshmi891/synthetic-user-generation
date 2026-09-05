import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  BarChart3,
  Sparkles,
  Users,
  TrendingUp,
  ThumbsUp,
  ThumbsDown,
  HelpCircle,
  CheckCircle2,
  AlertTriangle,
  Lightbulb,
  ArrowRight,
  RefreshCw,
  Sliders,
  Layers,
  MessageSquare,
} from 'lucide-react';
import { usePersonas } from '../context/PersonaContext';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { api, ApiError } from '../services/api';
import type { InsightResult } from '../types/persona';

export function InsightDashboard() {
  const navigate = useNavigate();
  const { personas, isLoading: isContextLoading } = usePersonas();

  const [provider, setProvider] = useState<'gemini' | 'mock' | 'openai'>('gemini');
  const [productContext, setProductContext] = useState<string>('Online Food Delivery Application');
  const [insights, setInsights] = useState<InsightResult | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleRunAnalysis = async () => {
    if (personas.length === 0) return;
    setLoading(true);
    setError(null);

    try {
      const res = await api.extractInsights({
        personas: personas,
        product_context: productContext,
        provider: provider,
      });
      setInsights(res);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.detail ?? err.message);
      } else {
        setError('Failed to extract insights. Ensure FastAPI server is running on port 8000.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (personas.length > 0 && !insights && !loading) {
      handleRunAnalysis();
    }
  }, [personas]);

  if (isContextLoading) {
    return <LoadingSpinner message="Loading personas for insight synthesis..." />;
  }

  if (personas.length === 0) {
    return (
      <div className="mx-auto max-w-2xl py-12 text-center">
        <Card className="p-8">
          <BarChart3 className="mx-auto h-12 w-12 text-brand-500" />
          <h2 className="mt-4 text-xl font-bold text-slate-900">No Personas Available for Insight Extraction</h2>
          <p className="mt-2 text-sm text-slate-600">
            Generate synthetic user personas in the Research Workspace first before synthesizing cohort insights.
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
      {/* Header Bar */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-slate-900">Insight Extraction & Usage Analytics</h1>
            <span className="rounded-full bg-brand-100 px-3 py-1 text-xs font-semibold text-brand-700">
              Milestone 3
            </span>
          </div>
          <p className="mt-1 text-sm text-slate-500">
            Synthesize themes, sentiment breakdown, agreement patterns, and product usage scores (0–10) across persona cohorts.
          </p>
        </div>

        {/* Controls */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2">
            <label className="text-xs font-semibold uppercase tracking-wider text-slate-500">
              Provider:
            </label>
            <select
              value={provider}
              onChange={(e) => setProvider(e.target.value as any)}
              className="rounded-xl border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-800 shadow-sm focus:border-brand-400 focus:outline-none"
            >
              <option value="gemini">Gemini (Google AI)</option>
              <option value="mock">Mock Engine (Deterministic)</option>
              <option value="openai">OpenAI</option>
            </select>
          </div>

          <Button
            onClick={handleRunAnalysis}
            disabled={loading}
            icon={loading ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
          >
            {loading ? 'Synthesizing...' : 'Re-Run Insights'}
          </Button>
        </div>
      </div>

      {/* Product Domain Input Bar */}
      <Card className="p-4 bg-slate-50 border-slate-200/80">
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
          <label className="text-xs font-bold uppercase tracking-wider text-slate-600 shrink-0">
            Research Context / Product:
          </label>
          <input
            type="text"
            value={productContext}
            onChange={(e) => setProductContext(e.target.value)}
            placeholder="Describe the product or research objective..."
            className="flex-1 rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 focus:border-brand-400 focus:outline-none"
          />
          <Button size="sm" variant="secondary" onClick={handleRunAnalysis} disabled={loading}>
            Update Context
          </Button>
        </div>
      </Card>

      {error && (
        <div className="rounded-xl bg-amber-50 p-4 text-xs text-amber-800 border border-amber-200 flex items-center justify-between">
          <span>{error}</span>
          {provider !== 'mock' && (
            <Button size="sm" variant="outline" onClick={() => { setProvider('mock'); handleRunAnalysis(); }}>
              Switch to Mock Mode
            </Button>
          )}
        </div>
      )}

      {loading ? (
        <div className="py-16">
          <LoadingSpinner message="Extracting themes, sentiment, agreement patterns, and persona scores..." />
        </div>
      ) : insights ? (
        <div className="space-y-8">
          {/* Top Level Summary Cards */}
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            <Card className="p-5 border-l-4 border-l-brand-500">
              <p className="text-xs font-semibold uppercase text-slate-400">Overall Product Score</p>
              <div className="mt-2 flex items-baseline gap-2">
                <span className="text-3xl font-extrabold text-slate-900">
                  {insights.aggregate_score.overall_score}
                </span>
                <span className="text-sm font-semibold text-slate-400">/ 10</span>
              </div>
              <p className="mt-1 text-xs text-brand-600 font-medium">
                {insights.aggregate_score.percentage_likely_to_use}% likely to adopt
              </p>
            </Card>

            <Card className="p-5 border-l-4 border-l-indigo-500">
              <p className="text-xs font-semibold uppercase text-slate-400">Personas Analyzed</p>
              <div className="mt-2 flex items-baseline gap-2">
                <span className="text-3xl font-extrabold text-slate-900">
                  {insights.aggregate_score.total_personas_analyzed}
                </span>
                <span className="text-sm text-slate-400">synthetic users</span>
              </div>
              <p className="mt-1 text-xs text-slate-500">Across {insights.segment_scores.length} market segments</p>
            </Card>

            <Card className="p-5 border-l-4 border-l-emerald-500">
              <p className="text-xs font-semibold uppercase text-slate-400">Top Scoring Segment</p>
              <div className="mt-2">
                <span className="text-xl font-bold text-emerald-700">
                  {insights.aggregate_score.highest_scoring_segment}
                </span>
              </div>
              <p className="mt-1 text-xs text-slate-500">Highest adoption propensity</p>
            </Card>

            <Card className="p-5 border-l-4 border-l-rose-500">
              <p className="text-xs font-semibold uppercase text-slate-400">Lowest Scoring Segment</p>
              <div className="mt-2">
                <span className="text-xl font-bold text-rose-700">
                  {insights.aggregate_score.lowest_scoring_segment}
                </span>
              </div>
              <p className="mt-1 text-xs text-slate-500">Requires targeted feature adjustments</p>
            </Card>
          </div>

          {/* Executive Summary */}
          <Card className="p-6 bg-gradient-to-r from-brand-900 to-slate-900 text-white shadow-md">
            <div className="flex items-center gap-2 text-brand-300 mb-2">
              <Sparkles className="h-5 w-5" />
              <h3 className="text-base font-bold text-white">Executive Synthesis Summary</h3>
            </div>
            <p className="text-sm text-brand-100 leading-relaxed">{insights.summary}</p>
          </Card>

          {/* Section 1: "Would Use This Product?" Persona Scoring & Segment Breakdown */}
          <div className="space-y-4">
            <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-brand-600" />
              1. "Would Use This Product?" Scoring & Persona Intent
            </h2>

            <div className="grid gap-6 lg:grid-cols-3">
              {/* Persona-Level Scores List */}
              <div className="lg:col-span-2 space-y-4">
                {insights.persona_scores.map((ps) => (
                  <Card key={ps.persona_id} className="p-5 hover:shadow-md transition-shadow">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-3">
                      <div>
                        <h4 className="text-base font-bold text-slate-900">{ps.persona_name}</h4>
                        <span className="inline-block rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-700 mt-1">
                          {ps.decision}
                        </span>
                      </div>
                      <div className="flex items-center gap-2 self-start sm:self-auto">
                        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-50 text-brand-700 font-extrabold text-lg border border-brand-200">
                          {ps.score}
                        </div>
                        <span className="text-xs font-semibold text-slate-400">/ 10</span>
                      </div>
                    </div>

                    <p className="mt-3 text-xs text-slate-600 leading-relaxed">{ps.reasoning}</p>

                    <div className="mt-4 grid gap-3 sm:grid-cols-2 text-xs">
                      <div className="rounded-lg bg-emerald-50/80 p-3 border border-emerald-100">
                        <p className="font-bold text-emerald-800 flex items-center gap-1.5 mb-1">
                          <ThumbsUp className="h-3.5 w-3.5 text-emerald-600" /> Key Positive Factors
                        </p>
                        <ul className="list-disc list-inside space-y-0.5 text-emerald-900">
                          {ps.positive_factors.map((factor, idx) => (
                            <li key={idx}>{factor}</li>
                          ))}
                        </ul>
                      </div>

                      <div className="rounded-lg bg-rose-50/80 p-3 border border-rose-100">
                        <p className="font-bold text-rose-800 flex items-center gap-1.5 mb-1">
                          <ThumbsDown className="h-3.5 w-3.5 text-rose-600" /> Key Negative Factors / Blockers
                        </p>
                        <ul className="list-disc list-inside space-y-0.5 text-rose-900">
                          {ps.negative_factors.map((factor, idx) => (
                            <li key={idx}>{factor}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>

              {/* Segment-Level Breakdown */}
              <div className="space-y-4">
                <Card className="p-5 space-y-4 sticky top-6">
                  <h3 className="text-base font-bold text-slate-900 flex items-center gap-2 border-b border-slate-100 pb-3">
                    <Layers className="h-4 w-4 text-brand-600" /> Segment Analysis
                  </h3>

                  {insights.segment_scores.map((seg, idx) => (
                    <div key={idx} className="rounded-xl bg-slate-50 p-4 border border-slate-200/70 space-y-2">
                      <div className="flex items-center justify-between">
                        <h4 className="text-sm font-bold text-slate-800">{seg.segment_name}</h4>
                        <span className="rounded-lg bg-brand-100 px-2 py-0.5 text-xs font-bold text-brand-800">
                          {seg.average_score} / 10
                        </span>
                      </div>
                      <p className="text-xs text-slate-500">{seg.reasoning}</p>
                      <div className="flex flex-wrap gap-1 pt-1">
                        {seg.personas.map((pName, pIdx) => (
                          <span key={pIdx} className="rounded-md bg-white border border-slate-200 px-2 py-0.5 text-[10px] text-slate-700 font-medium">
                            {pName}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </Card>
              </div>
            </div>
          </div>

          {/* Section 2: Sentiment & Recurring Themes */}
          <div className="grid gap-6 lg:grid-cols-2">
            {/* Sentiment Breakdown */}
            <Card className="p-6 space-y-4">
              <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <Sliders className="h-5 w-5 text-brand-600" /> Sentiment Breakdown
              </h3>
              <p className="text-xs text-slate-500">Semantic evaluation of persona reactions across research prompts.</p>

              <div className="space-y-3 pt-2">
                <div>
                  <div className="flex justify-between text-xs font-semibold mb-1">
                    <span className="text-emerald-700">Positive ({insights.sentiment.positive}%)</span>
                    <span className="text-slate-500">{insights.sentiment.positive_count ?? 0} personas</span>
                  </div>
                  <div className="h-3 w-full rounded-full bg-slate-100 overflow-hidden">
                    <div className="h-full bg-emerald-500 transition-all duration-500" style={{ width: `${insights.sentiment.positive}%` }} />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-xs font-semibold mb-1">
                    <span className="text-amber-700">Neutral ({insights.sentiment.neutral}%)</span>
                    <span className="text-slate-500">{insights.sentiment.neutral_count ?? 0} personas</span>
                  </div>
                  <div className="h-3 w-full rounded-full bg-slate-100 overflow-hidden">
                    <div className="h-full bg-amber-400 transition-all duration-500" style={{ width: `${insights.sentiment.neutral}%` }} />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-xs font-semibold mb-1">
                    <span className="text-rose-700">Negative ({insights.sentiment.negative}%)</span>
                    <span className="text-slate-500">{insights.sentiment.negative_count ?? 0} personas</span>
                  </div>
                  <div className="h-3 w-full rounded-full bg-slate-100 overflow-hidden">
                    <div className="h-full bg-rose-500 transition-all duration-500" style={{ width: `${insights.sentiment.negative}%` }} />
                  </div>
                </div>
              </div>
            </Card>

            {/* Recurring Themes */}
            <Card className="p-6 space-y-4">
              <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-brand-600" /> Recurring Research Themes
              </h3>
              <p className="text-xs text-slate-500">Core topics consistently emerging across synthetic interviews.</p>

              <div className="space-y-3 pt-1">
                {insights.recurring_themes.map((theme, idx) => (
                  <div key={idx} className="rounded-xl border border-slate-200/80 bg-slate-50/50 p-3.5 space-y-1.5">
                    <div className="flex items-center justify-between">
                      <h4 className="text-xs font-bold text-slate-800">{theme.theme}</h4>
                      <span className="rounded-full bg-brand-100 px-2 py-0.5 text-[11px] font-semibold text-brand-800">
                        {theme.frequency}/{insights.aggregate_score.total_personas_analyzed} ({theme.percentage}%)
                      </span>
                    </div>
                    <p className="text-xs text-slate-600">{theme.description}</p>
                    <div className="flex flex-wrap gap-1 pt-1">
                      {theme.supporting_personas.map((name, nIdx) => (
                        <span key={nIdx} className="rounded bg-white border border-slate-200 px-1.5 py-0.5 text-[10px] text-slate-600">
                          {name}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>

          {/* Section 3: Agreement Patterns & Behavioral Trends */}
          <div className="grid gap-6 lg:grid-cols-2">
            {/* Agreement Patterns */}
            <Card className="p-6 space-y-4">
              <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-emerald-600" /> Agreement & Disagreement Patterns
              </h3>
              <div className="space-y-4">
                {insights.agreement_patterns.map((item, idx) => (
                  <div key={idx} className="rounded-xl border border-slate-200 p-4 space-y-2">
                    <div className="flex items-center justify-between">
                      <h4 className="text-xs font-bold text-slate-800">{item.question_or_topic}</h4>
                      <span className="text-xs font-bold text-emerald-700">{item.agreement_percentage}% Agreement</span>
                    </div>
                    <div className="text-xs space-y-1">
                      <p><span className="font-semibold text-slate-700">Majority View:</span> {item.majority_response}</p>
                      <p><span className="font-semibold text-slate-700">Minority View:</span> {item.minority_response}</p>
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            {/* Behavioral Trends */}
            <Card className="p-6 space-y-4">
              <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <BarChart3 className="h-5 w-5 text-indigo-600" /> Observed Behavioral Trends
              </h3>
              <div className="space-y-4">
                {insights.behavioral_trends.map((bt, idx) => (
                  <div key={idx} className="rounded-xl border border-slate-200 p-4 space-y-1.5">
                    <div className="flex items-center justify-between">
                      <h4 className="text-xs font-bold text-slate-800">{bt.trend}</h4>
                      <span className="rounded bg-indigo-50 px-2 py-0.5 text-[10px] font-bold text-indigo-700">
                        {bt.percentage}% of cohort
                      </span>
                    </div>
                    <p className="text-xs text-slate-600">{bt.description}</p>
                  </div>
                ))}
              </div>
            </Card>
          </div>

          {/* Section 4: Key Findings & Strategic Recommendations */}
          <div className="grid gap-6 lg:grid-cols-2">
            <Card className="p-6 space-y-3 bg-brand-50/50 border-brand-200">
              <h3 className="text-base font-bold text-brand-900 flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-brand-600" /> Key Research Findings
              </h3>
              <ul className="space-y-2 text-xs text-brand-950">
                {insights.key_findings.map((finding, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="h-1.5 w-1.5 rounded-full bg-brand-600 mt-1.5 shrink-0" />
                    <span>{finding}</span>
                  </li>
                ))}
              </ul>
            </Card>

            <Card className="p-6 space-y-3 bg-amber-50/50 border-amber-200">
              <h3 className="text-base font-bold text-amber-900 flex items-center gap-2">
                <Lightbulb className="h-5 w-5 text-amber-600" /> Strategic Product Recommendations
              </h3>
              <ul className="space-y-2 text-xs text-amber-950">
                {insights.recommendations.map((rec, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="h-1.5 w-1.5 rounded-full bg-amber-600 mt-1.5 shrink-0" />
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </Card>
          </div>
        </div>
      ) : null}
    </div>
  );
}
