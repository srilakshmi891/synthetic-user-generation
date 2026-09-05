import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  FlaskConical,
  Users,
  MessageSquare,
  FileQuestion,
  BarChart3,
  Sparkles,
} from 'lucide-react';
import { cn } from '../../utils/format';

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/workspace', icon: FlaskConical, label: 'Research Workspace' },
  { to: '/personas', icon: Users, label: 'Persona Gallery' },
  { to: '/interview', icon: MessageSquare, label: 'Interview Mode' },
  { to: '/survey', icon: FileQuestion, label: 'Survey Mode' },
  { to: '/insights', icon: BarChart3, label: 'Insight Dashboard' },
];



export function Sidebar() {
  return (
    <aside className="fixed inset-y-0 left-0 z-30 flex w-64 flex-col border-r border-slate-200/80 bg-white/80 backdrop-blur-xl">
      <div className="flex h-16 items-center gap-3 border-b border-slate-200/80 px-6">
        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-brand-600 to-accent-600 shadow-md">
          <Sparkles className="h-5 w-5 text-white" />
        </div>
        <div>
          <p className="text-sm font-bold text-slate-900">SynthResearch</p>
          <p className="text-[10px] font-medium uppercase tracking-wider text-slate-400">
            Enterprise
          </p>
        </div>
      </div>

      <nav className="flex-1 space-y-1 p-4">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all',
                isActive
                  ? 'bg-gradient-to-r from-brand-50 to-accent-50 text-brand-700 shadow-sm'
                  : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
              )
            }
          >
            <Icon className="h-5 w-5 shrink-0" />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="border-t border-slate-200/80 p-4">
        <div className="rounded-xl bg-gradient-to-br from-brand-600 to-accent-600 p-4 text-white shadow-glow">
          <MessageSquare className="h-5 w-5 opacity-90" />
          <p className="mt-2 text-sm font-semibold">AI Interviews</p>
          <p className="mt-1 text-xs text-white/80">
            Conduct synthetic user interviews from any persona profile.
          </p>
        </div>
      </div>
    </aside>
  );
}
