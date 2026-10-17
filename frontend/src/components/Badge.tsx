import React from 'react';
import { AlertTriangle, CheckCircle2, ShieldAlert } from 'lucide-react';

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
  // Accessible Verdict System: Color + Default Icon + Shape
  // Phishing = Angular tag shape + AlertTriangle + Rose color
  // Legitimate = Rounded pill capsule + CheckCircle2 + Emerald color
  // Injection = Dashed border shape + ShieldAlert + Amber color
  const variantStyles: Record<
    BadgeVariant,
    {
      container: string;
      shape: string;
      dot: string;
      defaultIcon?: React.ReactNode;
    }
  > = {
    phishing: {
      shape: 'rounded-sm border-2 font-mono font-bold uppercase tracking-wider',
      container:
        'bg-rose-500/15 text-rose-700 dark:text-rose-200 border-rose-500/60 hover:bg-rose-500/25',
      dot: 'bg-rose-500 dark:bg-rose-400',
      defaultIcon: <AlertTriangle className="h-3 w-3 flex-shrink-0 text-rose-600 dark:text-rose-400" aria-hidden="true" />,
    },
    legitimate: {
      shape: 'rounded-full border font-semibold px-3',
      container:
        'bg-emerald-500/15 text-emerald-800 dark:text-emerald-200 border-emerald-500/60 hover:bg-emerald-500/25',
      dot: 'bg-emerald-500 dark:bg-emerald-400',
      defaultIcon: <CheckCircle2 className="h-3 w-3 flex-shrink-0 text-emerald-600 dark:text-emerald-400" aria-hidden="true" />,
    },
    injection: {
      shape: 'rounded-md border-2 border-dashed font-semibold',
      container:
        'bg-amber-500/15 text-amber-800 dark:text-amber-200 border-amber-500/70 hover:bg-amber-500/25',
      dot: 'bg-amber-500 dark:bg-amber-400',
      defaultIcon: <ShieldAlert className="h-3 w-3 flex-shrink-0 text-amber-600 dark:text-amber-400" aria-hidden="true" />,
    },
    accent: {
      shape: 'rounded-md border font-semibold',
      container:
        'bg-teal-500/10 text-teal-800 dark:text-teal-300 border-teal-500/30 hover:bg-teal-500/20',
      dot: 'bg-teal-600 dark:bg-teal-400',
    },
    neutral: {
      shape: 'rounded-md border font-medium',
      container:
        'bg-slate-200/80 dark:bg-slate-800/80 text-slate-700 dark:text-slate-300 border-slate-300 dark:border-slate-700/60 hover:bg-slate-300/80 dark:hover:bg-slate-800',
      dot: 'bg-slate-500 dark:bg-slate-400',
    },
    outline: {
      shape: 'rounded-md border font-medium',
      container:
        'bg-transparent text-slate-600 dark:text-slate-400 border-slate-300 dark:border-slate-700/80 hover:text-slate-900 dark:hover:text-slate-300',
      dot: 'bg-slate-500 dark:bg-slate-400',
    },
  };

  const sizeStyles: Record<BadgeSize, string> = {
    sm: 'text-[11px] px-2 py-0.5 gap-1.5',
    md: 'text-xs px-2.5 py-1 gap-1.5',
    lg: 'text-sm px-3.5 py-1.5 gap-2',
  };

  const currentVariant = variantStyles[variant];
  const renderedIcon = icon !== undefined ? icon : currentVariant.defaultIcon;

  return (
    <span
      role="status"
      className={`inline-flex items-center tracking-tight transition-all duration-150 ${currentVariant.shape} ${currentVariant.container} ${sizeStyles[size]} ${className}`}
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
      {renderedIcon && <span className="flex-shrink-0">{renderedIcon}</span>}
      <span>{children}</span>
    </span>
  );
};

