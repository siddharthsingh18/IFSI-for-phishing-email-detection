import React from 'react';
import { ArrowUpRight, ArrowDownRight, Minus } from 'lucide-react';

export type StatTileVariant = 'default' | 'accent' | 'phishing' | 'legitimate';
export type StatTileTrend = 'up' | 'down' | 'neutral';

export interface StatTileProps extends React.HTMLAttributes<HTMLDivElement> {
  label: string;
  value: string | number;
  unit?: string;
  subtext?: string;
  trend?: StatTileTrend;
  trendText?: string;
  icon?: React.ReactNode;
  variant?: StatTileVariant;
}

export const StatTile: React.FC<StatTileProps> = ({
  label,
  value,
  unit,
  subtext,
  trend,
  trendText,
  icon,
  variant = 'default',
  className = '',
  ...props
}) => {
  const variantStyles: Record<StatTileVariant, { container: string; valueText: string; iconBox: string }> = {
    default: {
      container: 'bg-slate-900/60 border-slate-800/80 hover:border-slate-700/80',
      valueText: 'text-white',
      iconBox: 'bg-slate-800/60 text-slate-400 border-slate-700/50',
    },
    accent: {
      container:
        'bg-slate-900/80 border-teal-500/30 hover:border-teal-500/50 shadow-lg shadow-teal-500/5',
      valueText: 'text-teal-300',
      iconBox: 'bg-teal-500/10 text-teal-400 border-teal-500/20',
    },
    phishing: {
      container:
        'bg-slate-900/80 border-rose-500/30 hover:border-rose-500/50 shadow-lg shadow-rose-500/5',
      valueText: 'text-rose-400',
      iconBox: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
    },
    legitimate: {
      container:
        'bg-slate-900/80 border-emerald-500/30 hover:border-emerald-500/50 shadow-lg shadow-emerald-500/5',
      valueText: 'text-emerald-400',
      iconBox: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    },
  };

  const currentVariant = variantStyles[variant];

  return (
    <div
      className={`rounded-xl border p-5 transition-all backdrop-blur-sm ${currentVariant.container} ${className}`}
      {...props}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="space-y-1">
          <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">
            {label}
          </p>
          <div className="flex items-baseline gap-1.5">
            <span className={`text-2xl sm:text-3xl font-extrabold tracking-tight ${currentVariant.valueText}`}>
              {value}
            </span>
            {unit && (
              <span className="text-xs font-semibold text-slate-400">
                {unit}
              </span>
            )}
          </div>
        </div>
        {icon && (
          <div className={`rounded-lg border p-2.5 flex-shrink-0 ${currentVariant.iconBox}`}>
            {icon}
          </div>
        )}
      </div>

      {(subtext || trend || trendText) && (
        <div className="mt-3 flex items-center justify-between text-xs text-slate-500 pt-3 border-t border-slate-800/60">
          {subtext && <span>{subtext}</span>}
          {trend && (
            <span
              className={`inline-flex items-center gap-0.5 font-medium ${
                trend === 'up'
                  ? 'text-emerald-400'
                  : trend === 'down'
                  ? 'text-rose-400'
                  : 'text-slate-400'
              }`}
            >
              {trend === 'up' && <ArrowUpRight className="h-3.5 w-3.5" />}
              {trend === 'down' && <ArrowDownRight className="h-3.5 w-3.5" />}
              {trend === 'neutral' && <Minus className="h-3.5 w-3.5" />}
              {trendText}
            </span>
          )}
        </div>
      )}
    </div>
  );
};
