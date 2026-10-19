import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Badge } from '../../components/Badge';
import { CheckCircle2, XCircle, Info, Sparkles } from 'lucide-react';
import type { McNemarTestResult } from '../../api/client';
import { COMPARISON_LABELS } from './types';

export interface SignificanceStripChartProps {
  sortedMcNemar: Array<[string, McNemarTestResult]>;
  isLoading?: boolean;
}

const ALPHA = 0.05;
const THRESHOLD_NEG_LOG10 = -Math.log10(ALPHA); // ~1.30103
const MAX_AXIS_NEG_LOG10 = 24; // accommodates highest -log10(p) ~22.46 with breathing room

export const SignificanceStripChart: React.FC<SignificanceStripChartProps> = ({
  sortedMcNemar,
  isLoading = false,
}) => {
  const [hoveredKey, setHoveredKey] = useState<string | null>(null);

  const thresholdPct = (THRESHOLD_NEG_LOG10 / MAX_AXIS_NEG_LOG10) * 100; // ~5.42%

  const significantCount = sortedMcNemar.filter(
    ([, t]) => t.significant_after_holm_bonferroni
  ).length;

  if (isLoading) {
    return (
      <div className="p-6 space-y-3 animate-pulse">
        <div className="h-4 bg-slate-800 rounded w-1/3 mb-4" />
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="h-8 bg-slate-900/60 rounded-lg border border-slate-800/60" />
        ))}
      </div>
    );
  }

  return (
    <div className="p-5 sm:p-6 space-y-6">
      {/* Top Summary & Legend Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 border-b border-slate-800/80 gap-3">
        <div className="flex flex-wrap items-center gap-2.5">
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold bg-teal-500/10 text-teal-300 border border-teal-500/25">
            <Sparkles className="w-3.5 h-3.5 text-teal-400" />
            <strong className="text-white">{significantCount}</strong> of{' '}
            <strong className="text-white">{sortedMcNemar.length}</strong> Comparisons Significant
          </span>
          <span className="px-2 py-0.5 rounded text-[11px] font-mono bg-slate-900 text-slate-400 border border-slate-800">
            FWER α=0.05 (Holm-Bonferroni)
          </span>
        </div>

        {/* Legend */}
        <div className="flex flex-wrap items-center gap-3 text-[11px] font-mono text-slate-400">
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-2 rounded bg-gradient-to-r from-teal-500 to-emerald-400 shadow-sm" />
            <span className="text-teal-300 font-medium">Significant (p ≤ 0.05)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-2 rounded bg-slate-700" />
            <span className="text-slate-400">Not Significant</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-2.5 h-2.5 border-l-2 border-dashed border-amber-400" />
            <span className="text-amber-300 font-bold">α=0.05 Threshold</span>
          </div>
        </div>
      </div>

      {/* Main Chart Area */}
      <div className="overflow-x-auto pb-2">
        <div className="min-w-[680px] space-y-2.5">
          {/* Axis Scale Header */}
          <div className="grid grid-cols-[220px_1fr_170px] gap-3 text-[10px] font-mono text-slate-400 items-end pb-1 border-b border-slate-800/60">
            <div className="uppercase tracking-wider font-semibold text-slate-400">
              Hypothesis Comparison
            </div>

            {/* Horizontal Axis Marks */}
            <div className="relative h-6 flex items-end">
              {/* Reference Threshold Indicator Badge */}
              <div
                className="absolute -top-1 -translate-x-1/2 flex flex-col items-center pointer-events-none z-20"
                style={{ left: `${thresholdPct}%` }}
              >
                <span className="px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/40 text-[9.5px] font-mono font-bold whitespace-nowrap shadow-sm">
                  α = 0.05 (-log₁₀ = 1.30)
                </span>
              </div>

              {/* Ticks along the axis */}
              <div className="w-full flex justify-between text-slate-400 px-0.5 pb-0.5 text-[9px]">
                <span>0 (p=1.0)</span>
                <span className="hidden sm:inline">5 (p=10⁻⁵)</span>
                <span>10 (p=10⁻¹⁰)</span>
                <span className="hidden sm:inline">15 (p=10⁻¹⁵)</span>
                <span>20 (p=10⁻²⁰)</span>
                <span>24 (-log₁₀)</span>
              </div>
            </div>

            <div className="text-right uppercase tracking-wider font-semibold text-slate-400">
              Corrected p &amp; Verdict
            </div>
          </div>

          {/* Rows */}
          {sortedMcNemar.map(([key, test], index) => {
            const rawP = test.raw_p_value ?? test.p_value ?? 1;
            const corrP = test.holm_bonferroni_p_value ?? test.p_value ?? 1;
            const isSig = test.significant_after_holm_bonferroni;
            const rank = test.holm_bonferroni_rank ?? index + 1;
            const compLabel = COMPARISON_LABELS[key] || key;

            const safeP = Math.min(1.0, Math.max(1e-25, corrP));
            const negLog10 = -Math.log10(safeP);

            // Calculate bar width percentage (0 to 100%)
            const barPct = Math.min(100, Math.max(0.6, (negLog10 / MAX_AXIS_NEG_LOG10) * 100));

            const isHovered = hoveredKey === key;

            return (
              <div
                key={key}
                onMouseEnter={() => setHoveredKey(key)}
                onMouseLeave={() => setHoveredKey(null)}
                className={`grid grid-cols-[220px_1fr_170px] gap-3 items-center py-2 px-2.5 rounded-xl transition-all duration-150 ${
                  isHovered
                    ? 'bg-slate-800/60 ring-1 ring-slate-700'
                    : isSig
                    ? 'bg-slate-900/40 hover:bg-slate-800/40'
                    : 'bg-slate-950/30 hover:bg-slate-900/40'
                }`}
              >
                {/* 1. Comparison Title & Rank */}
                <div className="flex items-center gap-2 overflow-hidden">
                  <span
                    className={`px-1.5 py-0.5 rounded text-[10px] font-mono font-bold shrink-0 ${
                      isSig
                        ? 'bg-teal-500/15 text-teal-300 border border-teal-500/30'
                        : 'bg-slate-800 text-slate-400 border border-slate-700'
                    }`}
                  >
                    #{rank}
                  </span>
                  <div className="truncate">
                    <p className="text-xs font-semibold text-white truncate" title={compLabel}>
                      {compLabel}
                    </p>
                    <p className="text-[10px] text-slate-400 font-mono">
                      Discordant: {test['a_correct_b_wrong (b)']}/{test['a_wrong_b_correct (c)']}
                    </p>
                  </div>
                </div>

                {/* 2. Horizontal Significance Strip with Reference Line */}
                <div className="relative h-7 flex items-center bg-slate-950/60 rounded-lg p-1 border border-slate-800/80 overflow-hidden">
                  {/* Significant zone background tint (right of threshold line) */}
                  <div
                    className="absolute top-0 bottom-0 right-0 bg-teal-500/[0.04] pointer-events-none"
                    style={{ left: `${thresholdPct}%` }}
                  />

                  {/* Vertical Reference Threshold Line (α=0.05) */}
                  <div
                    className="absolute top-0 bottom-0 z-20 pointer-events-none border-l-2 border-dashed border-amber-400/80 shadow-[0_0_6px_rgba(251,191,36,0.35)]"
                    style={{ left: `${thresholdPct}%` }}
                  />

                  {/* The Horizontal Bar */}
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${barPct}%` }}
                    transition={{
                      duration: 0.55,
                      delay: Math.min(0.4, index * 0.04),
                      ease: 'easeOut',
                    }}
                    className={`relative h-full rounded-md flex items-center justify-end pr-2 transition-colors ${
                      isSig
                        ? 'bg-gradient-to-r from-teal-600 via-teal-500 to-emerald-400 shadow-[0_0_12px_rgba(20,184,166,0.35)]'
                        : 'bg-gradient-to-r from-slate-700 to-slate-600'
                    }`}
                  >
                    {/* Value text inside bar if bar is wide enough */}
                    {barPct > 12 && (
                      <span className="text-[10px] font-mono font-bold text-slate-950 drop-shadow-sm select-none">
                        {negLog10.toFixed(1)}
                      </span>
                    )}
                  </motion.div>

                  {/* Value text outside bar if bar is too short */}
                  {barPct <= 12 && (
                    <span
                      className={`text-[10px] font-mono font-semibold ml-1.5 select-none ${
                        isSig ? 'text-teal-300' : 'text-slate-400'
                      }`}
                    >
                      {negLog10.toFixed(2)}
                    </span>
                  )}
                </div>

                {/* 3. Corrected p-value & Decision Badge */}
                <div className="flex items-center justify-end gap-2 text-right">
                  <div className="font-mono text-xs">
                    <p className={`font-bold ${isSig ? 'text-teal-300' : 'text-slate-400'}`}>
                      {corrP < 1e-4 ? corrP.toExponential(2) : corrP.toFixed(4)}
                    </p>
                    <p className="text-[10px] text-slate-400">
                      raw: {rawP < 1e-4 ? rawP.toExponential(2) : rawP.toFixed(4)}
                    </p>
                  </div>

                  <div className="shrink-0 w-24 flex justify-end">
                    {isSig ? (
                      <Badge variant="legitimate" size="sm" dot>
                        <CheckCircle2 className="h-3 w-3 mr-1 inline" />
                        Reject H0
                      </Badge>
                    ) : (
                      <Badge variant="neutral" size="sm">
                        <XCircle className="h-3 w-3 mr-1 inline opacity-60" />
                        ns
                      </Badge>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Explanatory Footnote */}
      <div className="pt-2 border-t border-slate-800/60 flex items-start gap-2 text-[11px] text-slate-400 font-mono">
        <Info className="w-3.5 h-3.5 text-teal-400 shrink-0 mt-0.5" />
        <p>
          Bars depict statistical power as <strong className="text-white font-mono">-log₁₀(p_corrected)</strong>. Bars crossing the vertical gold line (<span className="text-amber-300 font-bold">-log₁₀(0.05) ≈ 1.30</span>) achieve statistical significance at family-wise error rate α=0.05 under Holm-Bonferroni step-down correction.
        </p>
      </div>
    </div>
  );
};

export default SignificanceStripChart;
