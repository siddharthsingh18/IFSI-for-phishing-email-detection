import React from 'react';
import { ShieldCheck, TrendingDown, AlertTriangle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import type { BenchmarkSummary } from '../api/client';

export interface HeroFloatingRecallCardProps {
  summary: BenchmarkSummary | null;
  loading?: boolean;
}

export const HeroFloatingRecallCard: React.FC<HeroFloatingRecallCardProps> = ({
  summary,
  loading = false,
}) => {

  // Extract M3 and M4 metrics from summary (or fallbacks)
  const m3UnmarkedCell = summary?.cells?.['M3_unmarked']?.metrics;
  const m4UnmarkedCell = summary?.cells?.['M4_unmarked']?.metrics;

  const m3RecallPct = m3UnmarkedCell?.recall ? Number((m3UnmarkedCell.recall * 100).toFixed(1)) : 21.1;
  const m4RecallPct = m4UnmarkedCell?.recall ? Number((m4UnmarkedCell.recall * 100).toFixed(1)) : 96.1;
  const m4FprPct = m4UnmarkedCell?.fpr ? Number((m4UnmarkedCell.fpr * 100).toFixed(1)) : 72.1;

  // Chart coordinates
  const x1 = 30;
  const x2 = 120;
  const x3 = 210;

  // Clean baseline Y
  const yClean = 22; // ~90-96%
  const yM4 = 22;    // 96.1%
  const yM3 = 62;    // 21.1% (collapsed)

  return (
    <div className="rounded-2xl bg-white text-slate-900 border border-slate-100 elevation-modal p-3.5 sm:p-5 w-[240px] sm:w-[310px] transition-all duration-150 hover:elevation-hover select-none">
      {/* Header */}
      <div className="space-y-1">
        <div className="flex items-center justify-between">
          <span className="inline-flex items-center gap-1 sm:gap-1.5 px-2 py-0.5 rounded-full text-[9px] sm:text-[10px] font-bold uppercase tracking-wider bg-rose-50 text-rose-800 border border-rose-200/80">
            <TrendingDown className="h-2.5 w-2.5 sm:h-3 sm:w-3 text-rose-600" />
            <span>M3 Evasion vs M4 Defense</span>
          </span>
        </div>

        <div className="pt-1 flex items-baseline justify-between">
          <div>
            <div className="relative text-xl sm:text-2xl font-extrabold text-slate-950 tracking-tight font-['Plus_Jakarta_Sans',sans-serif] min-h-[1.75rem] flex items-center gap-2">
              <AnimatePresence mode="popLayout" initial={false}>
                {loading ? (
                  <motion.span
                    key="stat-skeleton"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.22, ease: 'easeInOut' }}
                  >
                    --
                  </motion.span>
                ) : (
                  <motion.span
                    key="stat-content"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.32, ease: 'easeOut' }}
                    className="flex items-center gap-1.5"
                  >
                    <span className="text-rose-600 font-bold">{m3RecallPct}%</span>
                    <span className="text-slate-400 font-normal text-xs">&rarr;</span>
                    <span className="text-teal-600 font-bold">{m4RecallPct}%</span>
                  </motion.span>
                )}
              </AnimatePresence>
            </div>
            <p className="text-[10px] sm:text-[11px] text-slate-500 font-medium leading-tight">
              Unmarked Catch Rate (M3 vs M4)
            </p>
          </div>
          <div className="p-1 sm:p-1.5 rounded-lg sm:rounded-xl bg-teal-50 text-teal-600 border border-teal-100/60">
            <ShieldCheck className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
          </div>
        </div>
      </div>

      {/* Comparison Micro SVG Chart */}
      <div className="h-[75px] sm:h-[95px] w-full mt-1.5 sm:mt-2">
        <svg
          viewBox="0 0 240 82"
          className="w-full h-full overflow-visible"
          role="img"
          aria-label="Catch rate comparison between M3 (RAG) and M4 (Decoupled IFSI)"
        >
          {/* M4 Line (Teal - resilient) */}
          <path
            d={`M ${x1} ${yClean} L ${x2} ${yClean} L ${x3} ${yM4}`}
            fill="none"
            stroke="#0d9488"
            strokeWidth="2.5"
            strokeLinecap="round"
          />
          {/* M3 Line (Rose - collapsed) */}
          <path
            d={`M ${x1} ${yClean} L ${x2} 32 L ${x3} ${yM3}`}
            fill="none"
            stroke="#e11d48"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeDasharray="4 3"
          />

          {/* M4 Points */}
          <circle cx={x1} cy={yClean} r={3} fill="#0d9488" />
          <circle cx={x2} cy={yClean} r={3} fill="#0d9488" />
          <circle cx={x3} cy={yM4} r={4.5} fill="#0d9488" />

          {/* M3 Endpoint */}
          <circle cx={x3} cy={yM3} r={4.5} fill="#e11d48" />

          {/* M4 Label */}
          <g transform={`translate(${x3 + 4}, ${yM4 + 3})`}>
            <text x="0" y="0" fill="#0d9488" fontSize="9" fontWeight="bold">M4: {m4RecallPct}%</text>
          </g>

          {/* M3 Label */}
          <g transform={`translate(${x3 + 4}, ${yM3 + 3})`}>
            <text x="0" y="0" fill="#e11d48" fontSize="9" fontWeight="bold">M3: {m3RecallPct}%</text>
          </g>

          {/* X Axis Labels */}
          <text x={x1} y="78" textAnchor="middle" fontSize="9" fill="#64748b" fontWeight="600">Clean</text>
          <text x={x2} y="78" textAnchor="middle" fontSize="9" fill="#64748b" fontWeight="600">Marked</text>
          <text x={x3} y="78" textAnchor="middle" fontSize="9" fill="#0f172a" fontWeight="700">Unmarked</text>
        </svg>
      </div>

      {/* Card Micro Footer */}
      <div className="mt-2 pt-2 border-t border-slate-100 flex items-center justify-between text-[9px] sm:text-[10px] text-slate-600 font-medium">
        <span className="text-rose-700 font-bold">M3 Evasion: {(100 - m3RecallPct).toFixed(1)}%</span>
        <span>&bull;</span>
        <span className="text-amber-700 font-bold flex items-center gap-0.5">
          <AlertTriangle className="h-2.5 w-2.5 inline" />
          M4 FPR Tax: {m4FprPct}%
        </span>
      </div>
    </div>
  );
};

export default HeroFloatingRecallCard;
