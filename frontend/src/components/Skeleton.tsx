import React from 'react';

interface SkeletonProps {
  className?: string;
  style?: React.CSSProperties;
}

export const Skeleton: React.FC<SkeletonProps> = ({ className = '', style }) => {
  return (
    <div
      style={style}
      className={`skeleton-shimmer rounded-lg ${className}`}
      aria-hidden="true"
    />
  );
};

export const SkeletonStatTile: React.FC<{ className?: string }> = ({ className = '' }) => {
  return (
    <div
      className={`rounded-2xl border border-slate-800/80 border-t-slate-700/70 bg-slate-900/60 p-5 space-y-3 elevation-card ${className}`}
      aria-hidden="true"
    >
      <div className="flex items-center justify-between">
        <Skeleton className="h-3 w-28" />
        <Skeleton className="h-8 w-8 rounded-xl" />
      </div>
      <div className="space-y-1.5 pt-1">
        <Skeleton className="h-7 w-36" />
        <Skeleton className="h-3 w-24" />
      </div>
    </div>
  );
};

export const SkeletonCard: React.FC<{
  className?: string;
  lines?: number;
  height?: string;
}> = ({ className = '', lines = 4, height }) => {
  return (
    <div
      className={`rounded-2xl border border-slate-800/80 border-t-slate-700/70 bg-slate-900/60 p-6 space-y-4 elevation-card ${className}`}
      aria-hidden="true"
    >
      <div className="flex items-center justify-between pb-3 border-b border-slate-800/60">
        <div className="space-y-1.5">
          <Skeleton className="h-4 w-40" />
          <Skeleton className="h-3 w-64" />
        </div>
        <Skeleton className="h-6 w-20 rounded-full" />
      </div>

      {height ? (
        <Skeleton className={`w-full ${height}`} />
      ) : (
        <div className="space-y-2.5 pt-1">
          {Array.from({ length: lines }).map((_, i) => (
            <Skeleton
              key={i}
              className={`h-3.5 ${
                i === 0
                  ? 'w-full'
                  : i === 1
                  ? 'w-11/12'
                  : i === lines - 1
                  ? 'w-2/3'
                  : 'w-4/5'
              }`}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export const SkeletonTableRow: React.FC<{ columns?: number }> = ({ columns = 9 }) => {
  return (
    <tr className="border-b border-slate-800/40" aria-hidden="true">
      {Array.from({ length: columns }).map((_, idx) => (
        <td key={idx} className="px-4 py-3.5">
          <Skeleton
            className={`h-4 ${
              idx === 0
                ? 'w-32'
                : idx === 1
                ? 'w-24'
                : idx === 2
                ? 'w-16 rounded-full'
                : 'w-14 ml-auto'
            }`}
          />
        </td>
      ))}
    </tr>
  );
};

export const SkeletonChart: React.FC<{ title?: string; subtitle?: string; className?: string }> = ({
  title = 'Performance Metric Comparison',
  subtitle = 'Evaluating multi-model latency and robustness across conditions',
  className = '',
}) => {
  return (
    <div
      className={`rounded-2xl border border-slate-800/80 bg-slate-900/60 p-6 space-y-4 elevation-card ${className}`}
      aria-hidden="true"
    >
      <div className="flex items-center justify-between pb-3 border-b border-slate-800/60">
        <div className="space-y-1">
          <div className="text-sm font-bold text-slate-300">{title}</div>
          <div className="text-xs text-slate-500">{subtitle}</div>
        </div>
        <div className="flex items-center gap-2">
          <Skeleton className="h-3 w-16" />
          <Skeleton className="h-3 w-16" />
        </div>
      </div>

      {/* Chart bars simulation */}
      <div className="pt-4 h-72 flex items-end justify-between gap-4 px-4">
        {[65, 40, 85, 30, 95, 20, 75, 45, 90, 25].map((pct, idx) => (
          <div key={idx} className="flex-1 flex flex-col items-center gap-2 h-full justify-end">
            <Skeleton
              className="w-full rounded-t-md"
              style={{ height: `${pct}%` }}
            />
            <Skeleton className="h-2 w-8" />
          </div>
        ))}
      </div>
    </div>
  );
};

export const SkeletonMethodCard: React.FC<{ className?: string }> = ({ className = '' }) => {
  return (
    <div
      className={`rounded-2xl border border-slate-800/80 bg-slate-900/60 p-6 space-y-5 elevation-card ${className}`}
      aria-hidden="true"
    >
      {/* Header Badge & Tag */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800/60">
        <Skeleton className="h-4 w-32" />
        <Skeleton className="h-5 w-24 rounded-full" />
      </div>

      {/* Verdict & Probability Bar */}
      <div className="space-y-2.5">
        <Skeleton className="h-7 w-40 rounded-lg" />
        <Skeleton className="h-2.5 w-full rounded-full" />
      </div>

      {/* Metrics breakdown pills */}
      <div className="grid grid-cols-2 gap-3 pt-1">
        <div className="p-2.5 rounded-xl border border-slate-800/60 bg-slate-950/40 space-y-1">
          <Skeleton className="h-3 w-16" />
          <Skeleton className="h-4 w-20" />
        </div>
        <div className="p-2.5 rounded-xl border border-slate-800/60 bg-slate-950/40 space-y-1">
          <Skeleton className="h-3 w-16" />
          <Skeleton className="h-4 w-20" />
        </div>
      </div>

      {/* Reasoning Trace Drawer Placeholder */}
      <div className="p-3 rounded-xl border border-slate-800/60 bg-slate-950/40 space-y-2">
        <Skeleton className="h-3.5 w-36" />
        <Skeleton className="h-3 w-full" />
        <Skeleton className="h-3 w-4/5" />
      </div>
    </div>
  );
};
