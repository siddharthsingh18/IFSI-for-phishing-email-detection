import React from 'react';
import { use3DTilt } from '../hooks/use3DTilt';

export type CardVariant = 'default' | 'elevated' | 'accent' | 'outline' | 'interactive';
export type CardPadding = 'none' | 'sm' | 'md' | 'lg';

export interface CardProps extends Omit<React.HTMLAttributes<HTMLDivElement>, 'title'> {
  variant?: CardVariant;
  padding?: CardPadding;
  tilt?: boolean;
  maxTilt?: number;
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
  tilt = false,
  maxTilt = 6,
  title,
  subtitle,
  icon,
  action,
  footer,
  children,
  className = '',
  style,
  onMouseMove,
  onMouseLeave,
  ...props
}) => {
  const tiltHook = use3DTilt({ maxTilt });

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (tilt) tiltHook.onMouseMove(e);
    onMouseMove?.(e);
  };

  const handleMouseLeave = (e: React.MouseEvent<HTMLDivElement>) => {
    if (tilt) tiltHook.onMouseLeave();
    onMouseLeave?.(e);
  };

  const combinedStyle: React.CSSProperties = {
    ...(tilt ? tiltHook.style : {}),
    ...style,
  };

  const variantStyles: Record<CardVariant, string> = {
    default:
      'bg-slate-900/70 border-slate-800/80 border-t-slate-700/70 elevation-card backdrop-blur-sm',
    elevated:
      'bg-slate-850/80 border-slate-700/60 border-t-slate-600/70 elevation-modal backdrop-blur-md',
    accent:
      'bg-slate-900/90 border-teal-500/30 border-t-teal-400/40 elevation-card backdrop-blur-md ring-1 ring-teal-500/20',
    outline:
      'bg-transparent border-slate-800/80 border-t-slate-700/60',
    interactive:
      'bg-slate-900/60 border-slate-800/80 border-t-slate-700/70 hover:border-teal-500/40 hover:border-t-teal-400/60 hover:bg-slate-900/90 elevation-card hover:elevation-hover hover:scale-[1.01] hover:brightness-105 active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 transition-all duration-150 cursor-pointer',
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
      ref={tilt ? tiltHook.ref : undefined}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      style={combinedStyle}
      className={`rounded-2xl border text-slate-200 ${variantStyles[variant]} ${tilt ? '[transform-style:preserve-3d]' : 'transition-all'} ${className}`}
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
