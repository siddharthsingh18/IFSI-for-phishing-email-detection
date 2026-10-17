import React from 'react';
import { BarChart3, AlertTriangle, ShieldCheck } from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { Badge } from '../../components/Badge';
import { SkeletonChart } from '../../components/Skeleton';
import { motion, AnimatePresence } from 'framer-motion';
import type { BenchmarkSummary } from '../../api/client';
import type { ChartThemeColors } from '../../hooks/useTheme';
import type { ChartGroupRow } from './types';

// =========================================================================
// CUSTOM GROUPED TOOLTIP FOR RECHARTS
// =========================================================================

interface CustomGroupedTooltipProps {
  active?: boolean;
  payload?: any[];
  label?: string;
  metricType?: 'recall' | 'fpr';
}

const CustomGroupedTooltip: React.FC<CustomGroupedTooltipProps> = ({
  active,
  payload,
  label,
  metricType = 'recall',
}) => {
  if (active && payload && payload.length) {
    const dataItem = payload[0].payload as ChartGroupRow;
    const isRecall = metricType === 'recall';
    const delta = isRecall ? dataItem.deltaRecall : dataItem.deltaFpr;

    return (
      <div className="rounded-xl border border-slate-700/80 bg-slate-900/95 p-3.5 elevation-modal backdrop-blur-md text-xs space-y-2 min-w-[220px]">
        <div className="border-b border-slate-800 pb-1.5">
          <p className="font-bold text-white text-xs">{dataItem.fullName || label}</p>
          <p className="text-[10px] text-teal-400 font-mono">Benchmark Dataset &bull; N=522</p>
        </div>

        <div className="space-y-1">
          {payload.map((entry: any, index: number) => (
            <div key={index} className="flex items-center justify-between gap-4">
              <span style={{ color: entry.color }} className="font-medium text-[11px]">
                {entry.name}:
              </span>
              <span className="font-mono text-white font-bold">
                {entry.value !== undefined ? `${entry.value}%` : ''}
              </span>
            </div>
          ))}
        </div>

        <div className="border-t border-slate-800 pt-1.5 flex items-center justify-between text-[11px]">
          <span className="text-slate-400">Shift (Δ = Unmarked &minus; Marked):</span>
          <span
            className={`font-mono font-bold ${
              isRecall
                ? delta >= 0
                  ? 'text-teal-400'
                  : 'text-rose-400'
                : delta <= 0
                ? 'text-emerald-400'
                : 'text-rose-400'
            }`}
          >
            {delta >= 0 ? `+${delta}` : delta}%
          </span>
        </div>
      </div>
    );
  }
  return null;
};

export interface ComparisonResultsProps {
  chartData: ChartGroupRow[];
  loadingSummary: boolean;
  summaryError: string | null;
  summary?: BenchmarkSummary | null;
  chartColors: ChartThemeColors;
}

export const ComparisonResults: React.FC<ComparisonResultsProps> = ({
  chartData,
  loadingSummary,
  summaryError,
  summary: _summary,
  chartColors,
}) => {
  return (
    <section id="benchmark-charts-section" className="space-y-6 scroll-mt-20">
      <div className="border-b border-slate-800 pb-4">
        <div className="flex items-center gap-2 text-teal-400 text-xs font-semibold uppercase tracking-wider">
          <BarChart3 className="h-4 w-4" />
          <span>Section 2 &bull; Empirical Benchmark (N=522)</span>
        </div>
        <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight mt-1 font-['Plus_Jakarta_Sans',sans-serif]">
          Marked vs. Unmarked Attack Resilience Across Architectures
        </h2>
        <p className="text-xs sm:text-sm text-slate-400 mt-0.5">
          Side-by-side empirical performance metrics demonstrating the collapse of standard RAG pipelines under natural
          enterprise camouflage.
        </p>
      </div>

      <div className="relative">
        <AnimatePresence mode="popLayout" initial={false}>
          {loadingSummary ? (
            <motion.div
              key="charts-skeleton"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.25, ease: 'easeInOut' }}
              className="grid grid-cols-1 lg:grid-cols-2 gap-6 w-full"
            >
              <SkeletonChart />
              <SkeletonChart />
            </motion.div>
          ) : summaryError ? (
            <motion.div
              key="charts-error"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="rounded-2xl border border-rose-500/30 bg-rose-500/10 p-6 text-center text-rose-300 text-sm space-y-2"
            >
              <AlertTriangle className="h-6 w-6 mx-auto text-rose-400" />
              <p className="font-semibold">Unable to load live benchmark data</p>
              <span className="text-xs text-rose-400/80">{summaryError}</span>
            </motion.div>
          ) : (
            <motion.div
              key="charts-content"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.35, ease: 'easeOut' }}
              className="space-y-6 w-full"
            >
              {/* Top Summary Stat Callouts for Section 2 */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="rounded-xl border border-rose-500/30 bg-slate-900/80 p-4 space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-mono text-rose-400 uppercase tracking-wider font-semibold">
                      The Evasion Catastrophe
                    </span>
                    <Badge variant="phishing" size="sm">
                      M3 RAG Combined
                    </Badge>
                  </div>
                  <div className="flex items-baseline gap-2">
                    <span className="text-2xl sm:text-3xl font-extrabold text-white">89.8% &rarr; 21.1%</span>
                    <span className="text-xs font-bold text-rose-400 font-mono">(&minus;68.7% Drop)</span>
                  </div>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    Standard RAG achieves near 90% recall under clean conditions, but collapses to 21.1% when indirect prompt
                    injections are unmarked. Over 78.9% of attacks evade detection completely.
                  </p>
                </div>

                <div className="rounded-xl border border-teal-500/30 bg-slate-900/80 p-4 space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-mono text-teal-400 uppercase tracking-wider font-semibold">
                      The IFSI Recovery &amp; Tax
                    </span>
                    <Badge variant="accent" size="sm">
                      M4 RAG Decoupled
                    </Badge>
                  </div>
                  <div className="flex items-baseline gap-2">
                    <span className="text-2xl sm:text-3xl font-extrabold text-white">96.1% Recall</span>
                    <span className="text-xs font-bold text-teal-400 font-mono">(Robust)</span>
                  </div>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    Two-stage decoupled inspection restores 96.1% recall against stealthy unmarked injections, but incurs a
                    severe <strong className="text-rose-300">72.08% False Alarm Tax</strong> on clean emails containing defensive notices.
                  </p>
                </div>
              </div>

              {/* Grouped Bar Charts Grid */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* CHART 1: RECALL (CATCH RATE) */}
                <div className="rounded-2xl border border-slate-800/80 bg-slate-900/70 p-5 elevation-card backdrop-blur-sm space-y-4">
                  <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                    <div>
                      <h3 className="text-sm font-bold text-white tracking-tight flex items-center gap-2">
                        <span>🎯</span> Phishing Catch Rate (Recall %)
                      </h3>
                      <p className="text-[11px] text-slate-400 mt-0.5">
                        Higher is better. Comparison of attack detection rate across conditions.
                      </p>
                    </div>
                    <Badge variant="neutral" size="sm">
                      Higher = Safer
                    </Badge>
                  </div>

                  <div className="h-72 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart
                        data={chartData}
                        margin={{ top: 10, right: 10, left: -20, bottom: 20 }}
                        barGap={4}
                      >
                        <CartesianGrid strokeDasharray="3 3" stroke={chartColors.grid} vertical={false} />
                        <XAxis
                          dataKey="name"
                          stroke={chartColors.text}
                          fontSize={11}
                          tickLine={false}
                          interval={0}
                        />
                        <YAxis
                          stroke={chartColors.text}
                          fontSize={11}
                          domain={[0, 100]}
                          tickLine={false}
                          unit="%"
                        />
                        <Tooltip content={<CustomGroupedTooltip metricType="recall" />} />
                        <Legend
                          wrapperStyle={{ paddingTop: '10px', fontSize: '11px' }}
                          formatter={(val) => <span className="text-slate-300">{val}</span>}
                        />
                        <Bar
                          dataKey="markedRecall"
                          name="Marked Recall (%)"
                          fill="#06b6d4"
                          radius={[4, 4, 0, 0]}
                          maxBarSize={32}
                        />
                        <Bar
                          dataKey="unmarkedRecall"
                          name="Unmarked Recall (%)"
                          fill="#f43f5e"
                          radius={[4, 4, 0, 0]}
                          maxBarSize={32}
                        />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>

                </div>

                {/* CHART 2: FALSE POSITIVE RATE (FALSE ALARMS) */}
                <div className="rounded-2xl border border-slate-800/80 bg-slate-900/70 p-5 elevation-card backdrop-blur-sm space-y-4">
                  <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                    <div>
                      <h3 className="text-sm font-bold text-white tracking-tight flex items-center gap-2">
                        <span>🚨</span> False Positive Rate (FPR %)
                      </h3>
                      <p className="text-[11px] text-slate-400 mt-0.5">
                        Lower is better. Ratio of benign emails erroneously flagged as phishing.
                      </p>
                    </div>

                  </div>

                  <div className="h-72 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart
                        data={chartData}
                        margin={{ top: 10, right: 10, left: -20, bottom: 20 }}
                        barGap={4}
                      >
                        <CartesianGrid strokeDasharray="3 3" stroke={chartColors.grid} vertical={false} />
                        <XAxis
                          dataKey="name"
                          stroke={chartColors.text}
                          fontSize={11}
                          tickLine={false}
                          interval={0}
                        />
                        <YAxis
                          stroke={chartColors.text}
                          fontSize={11}
                          domain={[0, 100]}
                          tickLine={false}
                          unit="%"
                        />
                        <Tooltip content={<CustomGroupedTooltip metricType="fpr" />} />
                        <Legend
                          wrapperStyle={{ paddingTop: '10px', fontSize: '11px' }}
                          formatter={(val) => <span className="text-slate-300">{val}</span>}
                        />
                        <Bar
                          dataKey="markedFpr"
                          name="Marked FPR (%)"
                          fill="#f59e0b"
                          radius={[4, 4, 0, 0]}
                          maxBarSize={32}
                        />
                        <Bar
                          dataKey="unmarkedFpr"
                          name="Unmarked FPR (%)"
                          fill="#f43f5e"
                          radius={[4, 4, 0, 0]}
                          maxBarSize={32}
                        />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>

                </div>
              </div>

              {/* Key Empirical Takeaways */}
              <div className="rounded-xl bg-slate-950/60 border border-slate-800 p-4 space-y-2 text-xs text-slate-300">
                <div className="font-semibold text-white flex items-center gap-2">
                  <ShieldCheck className="h-4 w-4 text-teal-400" />
                  <span>Key Empirical Takeaways from Prompt 8 &amp; 9 Benchmarks:</span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1 text-[11px] leading-relaxed">
                  <div className="space-y-1">
                    <strong className="text-teal-300 block">1. Linear Models (M1) are structurally immune to semantic overrides:</strong>
                    <span>
                      TF-IDF bag-of-words ignores grammar and semantic directives entirely, catching phishing based on vocabulary alone
                      (99.2% clean recall, 99.2% unmarked recall).
                    </span>
                  </div>
                  <div className="space-y-1">
                    <strong className="text-cyan-300 block">2. Single-Prompt RAG (M3) suffers from instruction confusion:</strong>
                    <span>
                      Retrieving authentic context examples inside the same prompt window gives injected instructions higher priority,
                      causing massive 78.9% evasion rates.
                    </span>
                  </div>
                  <div className="space-y-1">
                    <strong className="text-rose-300 block">3. Zero-Shot LLMs (M2) are easily fooled by administrative disguise:</strong>
                    <span>
                      When prompt instructions emulate IT routing administrators or legal disclaimers, zero-shot LLM recall drops
                      from 88.2% to 23.5% (a 64.7% drop).
                    </span>
                  </div>
                  <div className="space-y-1">
                    <strong className="text-emerald-300 block">4. Decoupled Two-Stage Inference (M4) trades False Alarms for Safety:</strong>
                    <span>
                      Restores strong phishing catch rate (89.8% &rarr; 96.1%), but incurs a severe{' '}
                      <strong>72.08% False Alarm Tax</strong> on clean emails containing defensive notices.
                    </span>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </section>
  );
};

export default ComparisonResults;
