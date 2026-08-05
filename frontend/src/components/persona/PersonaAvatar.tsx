import { getInitials } from '../../utils/format';
import { cn } from '../../utils/format';

interface PersonaAvatarProps {
  name: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}

const sizes = {
  sm: 'h-9 w-9 text-xs',
  md: 'h-12 w-12 text-sm',
  lg: 'h-16 w-16 text-lg',
  xl: 'h-24 w-24 text-2xl',
};

export function PersonaAvatar({ name, size = 'md', className }: PersonaAvatarProps) {
  return (
    <div
      className={cn(
        'flex shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-brand-500 to-accent-500 font-semibold text-white shadow-md',
        sizes[size],
        className
      )}
      aria-label={name}
    >
      {getInitials(name)}
    </div>
  );
}
