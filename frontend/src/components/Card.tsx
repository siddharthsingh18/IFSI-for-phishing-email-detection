import React from 'react';

export type CardVariant = 'default' | 'elevated' | 'accent' | 'outline' | 'interactive';
export type CardPadding = 'none' | 'sm' | 'md' | 'lg';

export interface CardProps extends Omit<React.HTMLAttributes<HTMLDivElement>, 'title'> {
  variant?: CardVariant;
  padding?: CardPadding;
  title?: React.ReactNode;
  subtitle?: React.ReactNode;
  icon?: React.ReactNode;
  action?: React.ReactNode;
  footer?: React.ReactNode;
  children: React.ReactNode;
}

export const Card: React.FC<CardProps> = ({
  variant = 'default',
  padding = 'md',
  title,
  subtitle,
  icon,
  action,
  footer,
  children,
  className = '',
  ...props
}) => {
  const variantStyles: Record<CardVariant, string> = {
    default:
      'bg-slate-900/70 border-slate-800/80 shadow-lg shadow-black/40 backdrop-blur-sm',
    elevated:
      'bg-slate-850/80 border-slate-700/60 shadow-xl shadow-black/50 backdrop-blur-md',
    accent:
      'bg-slate-900/90 border-teal-500/30 shadow-xl shadow-teal-500/5 backdrop-blur-md ring-1 ring-teal-500/20',
    outline:
      'bg-transparent border-slate-800/80',
    interactive:
      'bg-slate-900/60 border-slate-800/80 hover:border-teal-500/40 hover:bg-slate-900/90 hover:shadow-xl hover:shadow-teal-500/5 transition-all cursor-pointer',
  };

  const paddingStyles: Record<CardPadding, string> = {
    none: 'p-0',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  };

  const hasHeader = Boolean(title || subtitle || icon || action);

  return (
    <div
      className={`rounded-2xl border text-slate-200 transition-all ${variantStyles[variant]} ${className}`}
      {...props}
    >
      {/* Optional Card Header */}
      {hasHeader && (
        <div className="flex items-start justify-between gap-4 px-6 pt-6 pb-4 border-b border-slate-800/60">
          <div className="flex items-start gap-3">
            {icon && (
              <div className="flex-shrink-0 mt-0.5 rounded-lg bg-teal-500/10 border border-teal-500/20 p-2 text-teal-400">
                {icon}
              </div>
            )}
            <div>
              {title && (
                <div className="text-base font-semibold text-white tracking-tight">
                  {title}
                </div>
              )}
              {subtitle && (
                <div className="text-xs text-slate-400 mt-0.5 leading-relaxed">
                  {subtitle}
                </div>
              )}
            </div>
          </div>
          {action && <div className="flex-shrink-0 flex items-center gap-2">{action}</div>}
        </div>
      )}

      {/* Main Card Body */}
      <div className={hasHeader && padding === 'md' ? 'p-6 pt-5' : paddingStyles[padding]}>
        {children}
      </div>

      {/* Optional Card Footer */}
      {footer && (
        <div className="px-6 py-3.5 bg-slate-950/40 border-t border-slate-800/60 rounded-b-2xl text-xs text-slate-400">
          {footer}
        </div>
      )}
    </div>
  );
};
