import React from 'react';

export type BadgeVariant =
  | 'phishing'
  | 'legitimate'
  | 'injection'
  | 'neutral'
  | 'accent'
  | 'outline';

export type BadgeSize = 'sm' | 'md' | 'lg';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant;
  size?: BadgeSize;
  dot?: boolean;
  pulse?: boolean;
  icon?: React.ReactNode;
  children: React.ReactNode;
}

export const Badge: React.FC<BadgeProps> = ({
  variant = 'neutral',
  size = 'md',
  dot = false,
  pulse = false,
  icon,
  children,
  className = '',
  ...props
}) => {
  // Variant styles mapped to design tokens
  const variantStyles: Record<BadgeVariant, { container: string; dot: string }> = {
    phishing: {
      container:
        'bg-rose-500/10 text-rose-300 border-rose-500/30 hover:bg-rose-500/15',
      dot: 'bg-rose-400',
    },
    legitimate: {
      container:
        'bg-emerald-500/10 text-emerald-300 border-emerald-500/30 hover:bg-emerald-500/15',
      dot: 'bg-emerald-400',
    },
    injection: {
      container:
        'bg-amber-500/10 text-amber-300 border-amber-500/30 hover:bg-amber-500/15',
      dot: 'bg-amber-400',
    },
    accent: {
      container:
        'bg-teal-500/10 text-teal-300 border-teal-500/30 hover:bg-teal-500/15 shadow-sm shadow-teal-500/10',
      dot: 'bg-teal-400',
    },
    neutral: {
      container:
        'bg-slate-800/80 text-slate-300 border-slate-700/60 hover:bg-slate-800',
      dot: 'bg-slate-400',
    },
    outline: {
      container:
        'bg-transparent text-slate-400 border-slate-700/80 hover:text-slate-300',
      dot: 'bg-slate-400',
    },
  };

  const sizeStyles: Record<BadgeSize, string> = {
    sm: 'text-[11px] px-2 py-0.5 gap-1.5 font-medium rounded',
    md: 'text-xs px-2.5 py-1 gap-1.5 font-semibold rounded-md',
    lg: 'text-sm px-3.5 py-1.5 gap-2 font-semibold rounded-lg',
  };

  const currentVariant = variantStyles[variant];

  return (
    <span
      className={`inline-flex items-center border tracking-tight transition-colors ${currentVariant.container} ${sizeStyles[size]} ${className}`}
      {...props}
    >
      {dot && (
        <span className="relative flex h-1.5 w-1.5 flex-shrink-0">
          {pulse && (
            <span
              className={`absolute inline-flex h-full w-full rounded-full opacity-75 animate-ping ${currentVariant.dot}`}
            />
          )}
          <span
            className={`relative inline-flex h-1.5 w-1.5 rounded-full ${currentVariant.dot}`}
          />
        </span>
      )}
      {icon && <span className="flex-shrink-0">{icon}</span>}
      <span>{children}</span>
    </span>
  );
};
