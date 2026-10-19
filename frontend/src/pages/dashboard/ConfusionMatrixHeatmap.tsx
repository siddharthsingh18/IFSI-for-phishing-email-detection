import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card } from '../../components/Card';
import { ShieldCheck, AlertTriangle, CheckCircle2, XCircle, Grid2X2 } from 'lucide-react';
import type { MetricTableRow } from './types';
import { METHOD_LABELS } from './types';

export interface ConfusionMatrixHeatmapProps {
  isLoading: boolean;
  filteredRows: MetricTableRow[];
  filterMethod: string;
  setFilterMethod: (method: string) => void;
  filterCondition: string;
  setFilterCondition: (condition: string) => void;
  filterModel: string;
}

export const ConfusionMatrixHeatmap: React.FC<ConfusionMatrixHeatmapProps> = ({
  isLoading,
  filteredRows,
  filterMethod,
  setFilterMethod,
  filterCondition,
  setFilterCondition,
  filterModel,
}) => {
  // Determine which row to display in the confusion matrix heatmap
  // 1. If filteredRows has exactly 1 row, use it
  // 2. If multiple rows match, prefer M4 with priority, or the first matching row
  const activeRow: MetricTableRow | undefined = React.useMemo(() => {
    if (filteredRows.length === 0) return undefined;
    if (filteredRows.length === 1) return filteredRows[0];

    // If method is filtered to a specific method, pick the first matching (or prefer unmarked/clean)
    if (filterMethod !== 'all') {
      const matchCond = filteredRows.find(
        (r) => filterCondition !== 'all' && r.condition.toLowerCase() === filterCondition.toLowerCase()
      );
      return matchCond || filteredRows[0];
    }

    // When filterMethod is 'all', default to M4 (IFSI) to showcase the primary proposed architecture
    const m4Row = filteredRows.find((r) => r.methodCode === 'M4' && (r.sampleSize === 'N=522' || filterModel === 'llama'));
    if (m4Row) return m4Row;

    return filteredRows[0];
  }, [filteredRows, filterMethod, filterCondition, filterModel]);

  const tp = activeRow?.tp ?? 0;
  const fp = activeRow?.fp ?? 0;
  const tn = activeRow?.tn ?? 0;
  const fn = activeRow?.fn ?? 0;

  const actualPhishing = tp + fn;
  const actualLegitimate = fp + tn;
  const totalSamples = actualPhishing + actualLegitimate || 1;

  // Normalized rates for color intensity calculation (0.0 to 1.0)
  const tpRate = actualPhishing > 0 ? tp / actualPhishing : 0;
  const fnRate = actualPhishing > 0 ? fn / actualPhishing : 0;
  const fpRate = actualLegitimate > 0 ? fp / actualLegitimate : 0;
  const tnRate = actualLegitimate > 0 ? tn / actualLegitimate : 0;

  // Formatting helpers
  const toPct = (val: number) => (val * 100).toFixed(1) + '%';

  const transitionConfig = {
    duration: 0.2,
    ease: 'easeInOut' as const,
  };

  const matrixKey = activeRow
    ? `${activeRow.id}_${activeRow.model}_${activeRow.condition}`
    : 'no_data';

  return (
    <Card variant="elevated" padding="lg" className="border border-slate-800/90 relative overflow-hidden">
      {/* Background ambient glow */}
      <div className="absolute -top-24 -right-24 w-96 h-96 bg-teal-500/5 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute -bottom-24 -left-24 w-96 h-96 bg-indigo-500/5 rounded-full blur-3xl pointer-events-none" />

      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between pb-5 border-b border-slate-800/80 gap-4">
        <div>
          <div className="flex items-center gap-2.5">
            <div className="p-1.5 rounded-lg bg-teal-500/10 text-teal-400 border border-teal-500/20">
              <Grid2X2 className="w-4 h-4" />
            </div>
            <h3 className="text-base sm:text-lg font-bold text-white tracking-tight flex items-center gap-2">
              Confusion Matrix Heatmap
              {activeRow && (
                <span className="hidden sm:inline-flex items-center px-2.5 py-0.5 rounded-md text-[11px] font-mono bg-slate-800/90 text-teal-300 border border-teal-500/30">
                  {METHOD_LABELS[activeRow.methodCode] || activeRow.methodCode} • {activeRow.condition}
                </span>
              )}
            </h3>
          </div>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl">
            Empirical distribution of True Positives, False Positives, True Negatives, and False Negatives for the filtered configuration. Cell color intensity reflects relative magnitude.
          </p>
        </div>

        {/* Filter Indicator / Method & Condition Quick-Toggles */}
        <div className="flex flex-wrap items-center gap-2 self-start lg:self-auto">
          {filterMethod === 'all' && (
            <div className="flex items-center gap-1 bg-slate-900/90 p-1 rounded-lg border border-slate-800 text-xs">
              <span className="text-[10px] uppercase font-mono text-slate-400 px-1.5 font-semibold">Method:</span>
              {(['M1', 'M2', 'M3', 'M4'] as const).map((mCode) => {
                const isSelected = activeRow?.methodCode === mCode;
                return (
                  <button
                    key={mCode}
                    onClick={() => setFilterMethod(mCode)}
                    className={`px-2 py-1 rounded text-xs font-semibold transition-all ${
                      isSelected
                        ? 'bg-teal-500 text-slate-950 shadow-sm font-bold'
                        : 'text-slate-400 hover:text-white hover:bg-slate-800'
                    }`}
                  >
                    {mCode}
                  </button>
                );
              })}
            </div>
          )}

          {filterCondition === 'all' && (
            <div className="flex items-center gap-1 bg-slate-900/90 p-1 rounded-lg border border-slate-800 text-xs">
              <span className="text-[10px] uppercase font-mono text-slate-400 px-1.5 font-semibold">Cond:</span>
              {(['Clean', 'Marked', 'Unmarked'] as const).map((cName) => {
                const isSelected = activeRow?.condition.toLowerCase() === cName.toLowerCase();
                return (
                  <button
                    key={cName}
                    onClick={() => setFilterCondition(cName.toLowerCase())}
                    className={`px-2 py-1 rounded text-xs font-semibold transition-all ${
                      isSelected
                        ? 'bg-indigo-500 text-white shadow-sm font-bold'
                        : 'text-slate-400 hover:text-white hover:bg-slate-800'
                    }`}
                  >
                    {cName}
                  </button>
                );
              })}
            </div>
          )}

          {activeRow && (
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900/80 border border-slate-800 text-[11px] font-mono text-slate-300">
              <span className="text-slate-500">Model:</span>
              <span className="text-white font-medium">{activeRow.model}</span>
              <span className="text-slate-600">•</span>
              <span className="text-teal-400 font-bold">{activeRow.sampleSize}</span>
            </div>
          )}
        </div>
      </div>

      {isLoading ? (
        <div className="py-16 flex items-center justify-center">
          <div className="flex flex-col items-center gap-3">
            <div className="w-8 h-8 rounded-full border-2 border-teal-500/30 border-t-teal-400 animate-spin" />
            <p className="text-xs text-slate-400 font-mono">Loading confusion matrix cells...</p>
          </div>
        </div>
      ) : !activeRow ? (
        <div className="py-16 text-center text-xs text-slate-500 font-mono">
          No benchmark configurations match the selected filters.
        </div>
      ) : (
        <div className="pt-6 space-y-6">
          {/* Main 2x2 Heatmap Matrix with Axes */}
          <div className="overflow-x-auto pb-2">
            <div className="min-w-[580px]">
              {/* Top Axis: Predicted Labels */}
              <div className="grid grid-cols-[130px_1fr_1fr] gap-3 mb-2 text-center">
                <div className="flex items-end justify-center pb-1 text-[11px] font-bold font-mono text-slate-400 uppercase tracking-wider">
                  Actual \ Predicted
                </div>
                <div className="py-1.5 px-3 rounded-lg bg-slate-900/60 border border-slate-800 text-xs font-bold text-slate-300 flex items-center justify-center gap-1.5">
                  <span className="h-2 w-2 rounded-full bg-rose-500" />
                  PREDICTED PHISHING
                </div>
                <div className="py-1.5 px-3 rounded-lg bg-slate-900/60 border border-slate-800 text-xs font-bold text-slate-300 flex items-center justify-center gap-1.5">
                  <span className="h-2 w-2 rounded-full bg-teal-500" />
                  PREDICTED LEGITIMATE
                </div>
              </div>

              {/* Matrix Rows with 200ms Crossfade Transition */}
              <AnimatePresence mode="wait" initial={false}>
                <motion.div
                  key={matrixKey}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={transitionConfig}
                  className="space-y-3"
                >
                  {/* ROW 1: ACTUAL PHISHING */}
                  <div className="grid grid-cols-[130px_1fr_1fr] gap-3 items-stretch">
                    {/* Row Header */}
                    <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 flex flex-col justify-center items-center text-center">
                      <div className="text-[11px] font-bold font-mono text-rose-300 flex items-center gap-1">
                        <AlertTriangle className="w-3.5 h-3.5 text-rose-400 shrink-0" />
                        ACTUAL PHISHING
                      </div>
                      <div className="text-[10px] text-slate-400 font-mono mt-0.5">
                        Total: <span className="text-white font-bold">{actualPhishing}</span>
                      </div>
                    </div>

                    {/* Cell 1: True Positive (TP) */}
                    <div
                      className="relative rounded-xl p-4 border transition-all duration-300 flex flex-col justify-between overflow-hidden"
                      style={{
                        backgroundColor: `rgba(13, 148, 136, ${Math.max(0.12, 0.12 + tpRate * 0.52)})`,
                        borderColor: `rgba(45, 212, 191, ${Math.max(0.25, 0.25 + tpRate * 0.65)})`,
                        boxShadow: tpRate > 0.4 ? `0 0 24px rgba(20, 184, 166, ${tpRate * 0.28})` : 'none',
                      }}
                    >
                      <div className="flex items-center justify-between gap-2">
                        <span className="inline-flex items-center gap-1 text-[10px] font-mono font-bold uppercase tracking-wider text-teal-300 bg-teal-950/70 border border-teal-500/30 px-2 py-0.5 rounded">
                          <CheckCircle2 className="w-3 h-3 text-teal-400" />
                          True Positive (TP)
                        </span>
                        <span className="text-[11px] font-mono font-bold text-teal-200">
                          {toPct(tpRate)}
                        </span>
                      </div>

                      <div className="my-3 flex items-baseline gap-2">
                        <span className="text-3xl font-extrabold font-mono text-white tracking-tight">
                          {tp.toLocaleString()}
                        </span>
                        <span className="text-xs text-teal-300 font-medium">
                          phishing caught
                        </span>
                      </div>

                      {/* Magnitude intensity bar */}
                      <div className="w-full bg-slate-900/60 rounded-full h-1.5 overflow-hidden border border-teal-500/20">
                        <motion.div
                          className="h-full bg-gradient-to-r from-teal-500 to-emerald-400 rounded-full"
                          initial={{ width: 0 }}
                          animate={{ width: `${tpRate * 100}%` }}
                          transition={transitionConfig}
                        />
                      </div>
                    </div>

                    {/* Cell 2: False Negative (FN) */}
                    <div
                      className="relative rounded-xl p-4 border transition-all duration-300 flex flex-col justify-between overflow-hidden"
                      style={{
                        backgroundColor: `rgba(225, 29, 72, ${Math.max(0.10, 0.10 + fnRate * 0.58)})`,
                        borderColor: `rgba(251, 113, 133, ${Math.max(0.25, 0.25 + fnRate * 0.65)})`,
                        boxShadow: fnRate > 0.3 ? `0 0 24px rgba(225, 29, 72, ${fnRate * 0.35})` : 'none',
                      }}
                    >
                      <div className="flex items-center justify-between gap-2">
                        <span className="inline-flex items-center gap-1 text-[10px] font-mono font-bold uppercase tracking-wider text-rose-300 bg-rose-950/70 border border-rose-500/30 px-2 py-0.5 rounded">
                          <XCircle className="w-3 h-3 text-rose-400" />
                          False Negative (FN)
                        </span>
                        <span className="text-[11px] font-mono font-bold text-rose-200">
                          {toPct(fnRate)}
                        </span>
                      </div>

                      <div className="my-3 flex items-baseline gap-2">
                        <span className="text-3xl font-extrabold font-mono text-white tracking-tight">
                          {fn.toLocaleString()}
                        </span>
                        <span className="text-xs text-rose-300 font-medium">
                          evaded detection
                        </span>
                      </div>

                      {/* Magnitude intensity bar */}
                      <div className="w-full bg-slate-900/60 rounded-full h-1.5 overflow-hidden border border-rose-500/20">
                        <motion.div
                          className="h-full bg-gradient-to-r from-rose-500 to-red-400 rounded-full"
                          initial={{ width: 0 }}
                          animate={{ width: `${fnRate * 100}%` }}
                          transition={transitionConfig}
                        />
                      </div>
                    </div>
                  </div>

                  {/* ROW 2: ACTUAL LEGITIMATE */}
                  <div className="grid grid-cols-[130px_1fr_1fr] gap-3 items-stretch">
                    {/* Row Header */}
                    <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 flex flex-col justify-center items-center text-center">
                      <div className="text-[11px] font-bold font-mono text-teal-300 flex items-center gap-1">
                        <ShieldCheck className="w-3.5 h-3.5 text-teal-400 shrink-0" />
                        ACTUAL LEGIT
                      </div>
                      <div className="text-[10px] text-slate-400 font-mono mt-0.5">
                        Total: <span className="text-white font-bold">{actualLegitimate}</span>
                      </div>
                    </div>

                    {/* Cell 3: False Positive (FP) */}
                    <div
                      className="relative rounded-xl p-4 border transition-all duration-300 flex flex-col justify-between overflow-hidden"
                      style={{
                        backgroundColor: `rgba(245, 158, 11, ${Math.max(0.10, 0.10 + fpRate * 0.55)})`,
                        borderColor: `rgba(251, 191, 36, ${Math.max(0.25, 0.25 + fpRate * 0.65)})`,
                        boxShadow: fpRate > 0.3 ? `0 0 24px rgba(245, 158, 11, ${fpRate * 0.3})` : 'none',
                      }}
                    >
                      <div className="flex items-center justify-between gap-2">
                        <span className="inline-flex items-center gap-1 text-[10px] font-mono font-bold uppercase tracking-wider text-amber-300 bg-amber-950/70 border border-amber-500/30 px-2 py-0.5 rounded">
                          <AlertTriangle className="w-3 h-3 text-amber-400" />
                          False Positive (FP)
                        </span>
                        <span className="text-[11px] font-mono font-bold text-amber-200">
                          {toPct(fpRate)}
                        </span>
                      </div>

                      <div className="my-3 flex items-baseline gap-2">
                        <span className="text-3xl font-extrabold font-mono text-white tracking-tight">
                          {fp.toLocaleString()}
                        </span>
                        <span className="text-xs text-amber-300 font-medium">
                          false alarms
                        </span>
                      </div>

                      {/* Magnitude intensity bar */}
                      <div className="w-full bg-slate-900/60 rounded-full h-1.5 overflow-hidden border border-amber-500/20">
                        <motion.div
                          className="h-full bg-gradient-to-r from-amber-500 to-orange-400 rounded-full"
                          initial={{ width: 0 }}
                          animate={{ width: `${fpRate * 100}%` }}
                          transition={transitionConfig}
                        />
                      </div>
                    </div>

                    {/* Cell 4: True Negative (TN) */}
                    <div
                      className="relative rounded-xl p-4 border transition-all duration-300 flex flex-col justify-between overflow-hidden"
                      style={{
                        backgroundColor: `rgba(14, 165, 233, ${Math.max(0.12, 0.12 + tnRate * 0.50)})`,
                        borderColor: `rgba(56, 189, 248, ${Math.max(0.25, 0.25 + tnRate * 0.65)})`,
                        boxShadow: tnRate > 0.4 ? `0 0 24px rgba(14, 165, 233, ${tnRate * 0.28})` : 'none',
                      }}
                    >
                      <div className="flex items-center justify-between gap-2">
                        <span className="inline-flex items-center gap-1 text-[10px] font-mono font-bold uppercase tracking-wider text-sky-300 bg-sky-950/70 border border-sky-500/30 px-2 py-0.5 rounded">
                          <ShieldCheck className="w-3 h-3 text-sky-400" />
                          True Negative (TN)
                        </span>
                        <span className="text-[11px] font-mono font-bold text-sky-200">
                          {toPct(tnRate)}
                        </span>
                      </div>

                      <div className="my-3 flex items-baseline gap-2">
                        <span className="text-3xl font-extrabold font-mono text-white tracking-tight">
                          {tn.toLocaleString()}
                        </span>
                        <span className="text-xs text-sky-300 font-medium">
                          cleared legitimate
                        </span>
                      </div>

                      {/* Magnitude intensity bar */}
                      <div className="w-full bg-slate-900/60 rounded-full h-1.5 overflow-hidden border border-sky-500/20">
                        <motion.div
                          className="h-full bg-gradient-to-r from-sky-500 to-cyan-400 rounded-full"
                          initial={{ width: 0 }}
                          animate={{ width: `${tnRate * 100}%` }}
                          transition={transitionConfig}
                        />
                      </div>
                    </div>
                  </div>
                </motion.div>
              </AnimatePresence>
            </div>
          </div>

          {/* Diagnostic Metrics Strip & Color Scale Legend */}
          <div className="pt-4 border-t border-slate-800/80 flex flex-col md:flex-row items-center justify-between gap-4 text-xs">
            {/* Quick Diagnostic Metrics */}
            <div className="flex flex-wrap items-center gap-2 font-mono">
              <span className="text-[11px] text-slate-400 uppercase font-semibold">Slice Metrics:</span>
              <div className="px-2.5 py-1 rounded-md bg-slate-900 border border-slate-800 text-slate-300">
                Recall: <span className="text-teal-400 font-bold">{toPct(tpRate)}</span>
              </div>
              <div className="px-2.5 py-1 rounded-md bg-slate-900 border border-slate-800 text-slate-300">
                FPR: <span className="text-rose-400 font-bold">{toPct(fpRate)}</span>
              </div>
              <div className="px-2.5 py-1 rounded-md bg-slate-900 border border-slate-800 text-slate-300">
                Specificity: <span className="text-sky-400 font-bold">{toPct(tnRate)}</span>
              </div>
              <div className="px-2.5 py-1 rounded-md bg-slate-900 border border-slate-800 text-slate-300">
                Accuracy: <span className="text-white font-bold">{toPct((tp + tn) / totalSamples)}</span>
              </div>
            </div>

            {/* Heatmap Legend */}
            <div className="flex items-center gap-3 text-[11px] font-mono text-slate-400">
              <span>Heatmap Intensity:</span>
              <div className="flex items-center gap-1.5">
                <span className="text-[10px] text-slate-500">0%</span>
                <div className="w-24 h-2 rounded-full bg-gradient-to-r from-slate-800 via-teal-700/60 to-teal-400 border border-slate-700" />
                <span className="text-[10px] text-teal-300 font-bold">100%</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </Card>
  );
};

export default ConfusionMatrixHeatmap;
