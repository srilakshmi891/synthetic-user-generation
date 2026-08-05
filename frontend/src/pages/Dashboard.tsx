import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Users,
  FlaskConical,
  TrendingUp,
  Building2,
  ArrowRight,
  Sparkles,
} from 'lucide-react';
import { usePersonas } from '../context/PersonaContext';
import { StatCard } from '../components/ui/StatCard';
import { Card, CardHeader } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { PersonaCard } from '../components/persona/PersonaCard';
import { ChartCard, DistributionChart } from '../components/charts/ChartComponents';
import {
  averageAge,
  generationTrend,
  countBy,
  uniqueIndustries,
} from '../utils/analytics';
import { EmptyState } from '../components/ui/EmptyState';

export function Dashboard() {
  const { personas } = usePersonas();

  const recent = personas.slice(0, personas.length);
  const genderData = countBy(personas, (p) => p.demographics.gender);
  const trendData = generationTrend(personas);

  return (
    <div className="space-y-8">
      <motion.div
        initial={{ opacity: 0, y: -8 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-brand-600 via-brand-700 to-accent-600 p-8 text-white shadow-glow"
      >
        <div className="absolute -right-8 -top-8 h-40 w-40 rounded-full bg-white/10 blur-3xl" />
        <div className="relative flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
          <div>
            <div className="mb-2 flex items-center gap-2 text-brand-100">
              <Sparkles className="h-4 w-4" />
              <span className="text-sm font-medium">Research Overview</span>
            </div>
            <h2 className="text-2xl font-bold md:text-3xl">
              Welcome to your synthetic research hub
            </h2>
            <p className="mt-2 max-w-xl text-sm text-brand-100">
              Generate diverse user personas, analyze cohort insights, and conduct AI-powered
              interviews — all in one enterprise workspace.
            </p>
          </div>
          <Link to="/workspace">
            <Button
              variant="secondary"
              size="lg"
              className="bg-white text-brand-700 hover:bg-brand-50"
            >
              Start New Research
              <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
        </div>
      </motion.div>

      <div className="grid gap-6 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          title="Total Personas"
          value={personas.length}
          change={personas.length ? `${personas.length} in library` : 'Generate your first cohort'}
          icon={Users}
          trend="neutral"
        />
        <StatCard
          title="Research Sessions"
          value={new Set(personas.map((p) => p.researchSession?.productDescription)).size || 0}
          change="Unique product studies"
          icon={FlaskConical}
        />
        <StatCard
          title="Average Age"
          value={personas.length ? averageAge(personas) : '—'}
          change={personas.length ? 'Across all personas' : 'No data yet'}
          icon={TrendingUp}
        />
        <StatCard
          title="Industries Covered"
          value={personas.length ? uniqueIndustries(personas) : '—'}
          change="Occupational diversity"
          icon={Building2}
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <ChartCard title="Generation Activity" subtitle="Personas created over time">
          <DistributionChart data={trendData} type="area" />
        </ChartCard>
        <ChartCard title="Gender Distribution" subtitle="Cohort demographic breakdown">
          <DistributionChart data={genderData} type="pie" />
        </ChartCard>
      </div>

      <Card>
        <CardHeader
          title="Recent Personas"
          subtitle="Latest synthetic users from your research sessions"
          action={
            personas.length > 0 ? (
              <Link to="/">
                <Button variant="ghost" size="sm">
                  View all
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </Link>
            ) : undefined
          }
        />
        {recent.length > 0 ? (
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {recent.map((persona) => (
              <PersonaCard key={persona.id} persona={persona} />
            ))}
          </div>
        ) : (
          <EmptyState
            icon={Users}
            title="No personas yet"
            description="Generate your first cohort of synthetic users in the Research Workspace."
            actionLabel="Go to Workspace"
            onAction={() => (window.location.href = '/workspace')}
          />
        )}
      </Card>
    </div>
  );
}
