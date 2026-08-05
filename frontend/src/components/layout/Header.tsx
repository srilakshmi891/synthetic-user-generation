import { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { Bell, Circle } from 'lucide-react';
import { api } from '../../services/api';

const pageTitles: Record<string, string> = {
  '/': 'Dashboard',
  '/workspace': 'Research Workspace',
  '/personas': 'Persona Gallery',
  '/analytics': 'Analytics',
};

export function Header() {
  const location = useLocation();
  const [apiOnline, setApiOnline] = useState<boolean | null>(null);

  useEffect(() => {
    api.health()
      .then(() => setApiOnline(true))
      .catch(() => setApiOnline(false));
  }, []);

  const title =
    pageTitles[location.pathname] ??
    (location.pathname.startsWith('/personas/') ? 'Persona Details' : 'AI Interview');

  return (
    <header className="sticky top-0 z-20 flex h-16 items-center justify-between border-b border-slate-200/80 bg-white/70 px-8 backdrop-blur-xl">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">{title}</h1>
        <p className="text-xs text-slate-500">Synthetic User Research Platform</p>
      </div>
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs">
          <Circle
            className={`h-2 w-2 fill-current ${
              apiOnline === null
                ? 'text-amber-400'
                : apiOnline
                  ? 'text-emerald-500'
                  : 'text-red-500'
            }`}
          />
          <span className="text-slate-600">
            API {apiOnline === null ? 'Checking…' : apiOnline ? 'Online' : 'Offline'}
          </span>
        </div>
        <button
          type="button"
          className="relative rounded-xl p-2 text-slate-500 transition-colors hover:bg-slate-100 hover:text-slate-700"
          aria-label="Notifications"
        >
          <Bell className="h-5 w-5" />
        </button>
        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-brand-500 to-accent-500 text-sm font-semibold text-white">
          SR
        </div>
      </div>
    </header>
  );
}
