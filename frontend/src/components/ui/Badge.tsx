import { cn } from '../../utils/format';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'brand' | 'accent' | 'success' | 'warning';
  className?: string;
}

const variants = {
  default: 'bg-slate-100 text-slate-700',
  brand: 'bg-brand-50 text-brand-700',
  accent: 'bg-accent-50 text-accent-700',
  success: 'bg-emerald-50 text-emerald-700',
  warning: 'bg-amber-50 text-amber-700',
};

export function Badge({ children, variant = 'default', className }: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium',
        variants[variant],
        className
      )}
    >
      {children}
    </span>
  );
}
