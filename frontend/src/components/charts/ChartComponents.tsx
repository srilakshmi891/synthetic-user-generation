import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area,
} from 'recharts';

const COLORS = ['#6366f1', '#8b5cf6', '#a855f7', '#c084fc', '#818cf8', '#4f46e5', '#9333ea', '#7c3aed'];

interface ChartCardProps {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  height?: number;
}

export function ChartCard({ title, subtitle, children, height = 280 }: ChartCardProps) {
  return (
    <div className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-card">
      <h3 className="text-base font-semibold text-slate-900">{title}</h3>
      {subtitle && <p className="mt-1 text-sm text-slate-500">{subtitle}</p>}
      <div className="mt-4" style={{ height }}>
        {children}
      </div>
    </div>
  );
}

interface DistributionChartProps {
  data: { name: string; value: number }[];
  type?: 'bar' | 'pie' | 'area';
}

export function DistributionChart({ data, type = 'bar' }: DistributionChartProps) {
  if (!data.length) {
    return (
      <div className="flex h-full items-center justify-center text-sm text-slate-400">
        No data available
      </div>
    );
  }

  if (type === 'pie') {
    return (
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            dataKey="value"
            nameKey="name"
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={90}
            paddingAngle={3}
          >
            {data.map((_, i) => (
              <Cell key={i} fill={COLORS[i % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              borderRadius: '12px',
              border: '1px solid #e2e8f0',
              boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.06)',
            }}
          />
        </PieChart>
      </ResponsiveContainer>
    );
  }

  if (type === 'area') {
    return (
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data}>
          <defs>
            <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#6366f1" stopOpacity={0.3} />
              <stop offset="100%" stopColor="#6366f1" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
          <XAxis dataKey="name" tick={{ fontSize: 12, fill: '#64748b' }} />
          <YAxis tick={{ fontSize: 12, fill: '#64748b' }} allowDecimals={false} />
          <Tooltip
            contentStyle={{
              borderRadius: '12px',
              border: '1px solid #e2e8f0',
            }}
          />
          <Area type="monotone" dataKey="value" stroke="#6366f1" fill="url(#areaGrad)" strokeWidth={2} />
        </AreaChart>
      </ResponsiveContainer>
    );
  }

  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={data} layout={data.some((d) => d.name.length > 20) ? 'vertical' : 'horizontal'}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
        {data.some((d) => d.name.length > 20) ? (
          <>
            <XAxis type="number" tick={{ fontSize: 12, fill: '#64748b' }} allowDecimals={false} />
            <YAxis
              type="category"
              dataKey="name"
              width={120}
              tick={{ fontSize: 11, fill: '#64748b' }}
            />
          </>
        ) : (
          <>
            <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#64748b' }} />
            <YAxis tick={{ fontSize: 12, fill: '#64748b' }} allowDecimals={false} />
          </>
        )}
        <Tooltip
          contentStyle={{
            borderRadius: '12px',
            border: '1px solid #e2e8f0',
          }}
        />
        <Bar dataKey="value" radius={[6, 6, 0, 0]}>
          {data.map((_, i) => (
            <Cell key={i} fill={COLORS[i % COLORS.length]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

export function PieLegend({ data }: { data: { name: string; value: number }[] }) {
  return (
    <div className="mt-2 flex flex-wrap justify-center gap-x-4 gap-y-1">
      {data.map((item, i) => (
        <div key={item.name} className="flex items-center gap-1.5 text-xs text-slate-600">
          <span
            className="h-2.5 w-2.5 rounded-full"
            style={{ backgroundColor: COLORS[i % COLORS.length] }}
          />
          {item.name} ({item.value})
        </div>
      ))}
    </div>
  );
}
