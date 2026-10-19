import React from 'react';
import {
  AlertCircle,
  GitCompare,
  ChevronDown,
  ChevronUp,
  CheckCircle2,
  Table,
} from 'lucide-react';
import { Card } from '../../components/Card';
import { Badge } from '../../components/Badge';
import { SkeletonTableRow } from '../../components/Skeleton';
import { motion, AnimatePresence } from 'framer-motion';
import type { MistakeRecord, McNemarResponse, McNemarTestResult } from '../../api/client';
import { COMPARISON_LABELS } from './types';
import { SignificanceStripChart } from './SignificanceStripChart';

export interface MistakesAndHypothesisTestsProps {
  isLoading: boolean;
  mistakes: MistakeRecord[];
  showMistakes: boolean;
  setShowMistakes: React.Dispatch<React.SetStateAction<boolean>>;
  expandedMistakeId: string | null;
  setExpandedMistakeId: React.Dispatch<React.SetStateAction<string | null>>;
  mcnemar: McNemarResponse | null;
  showMcNemar: boolean;
  setShowMcNemar: React.Dispatch<React.SetStateAction<boolean>>;
  sortedMcNemar: Array<[string, McNemarTestResult]>;
}

export const MistakesAndHypothesisTests: React.FC<MistakesAndHypothesisTestsProps> = ({
  isLoading,
  mistakes,
  showMistakes,
  setShowMistakes,
  expandedMistakeId,
  setExpandedMistakeId,
  showMcNemar,
  setShowMcNemar,
  sortedMcNemar,
}) => {
  const [showAllMistakes, setShowAllMistakes] = React.useState(false);
  const [showFullTable, setShowFullTable] = React.useState(false);
  const displayedMistakes = showAllMistakes ? mistakes : mistakes.slice(0, 10);

  return (
    <>
      {/* =========================================================================
          SECTION 5: COLLAPSIBLE WORST MISTAKES (Animated Height+Opacity & Inline Row)
          ========================================================================= */}
      <Card variant="default" padding="none">
        <div
          role="button"
          tabIndex={0}
          onClick={() => setShowMistakes(!showMistakes)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              setShowMistakes(!showMistakes);
            }
          }}
          className="p-5 flex items-center justify-between cursor-pointer hover:bg-slate-850/60 hover:scale-[1.005] hover:brightness-105 active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-inset transition-all duration-150 select-none"
        >
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-rose-500/10 text-rose-400 border border-rose-500/20">
              <AlertCircle className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white tracking-tight">
                Worst High-Confidence Misclassifications ({displayedMistakes.length} of {mistakes.length} cases)
              </h3>
              <p className="text-xs text-slate-400">
                Top high-confidence model errors. Click any row to expand the full email text inline.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 text-slate-400">
            <span className="text-xs">{showMistakes ? 'Collapse' : 'Expand'}</span>
            {showMistakes ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
          </div>
        </div>

        <AnimatePresence initial={false}>
          {showMistakes && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.25, ease: 'easeInOut' }}
              className="overflow-hidden border-t border-slate-800"
            >
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-slate-300">
                  <thead className="bg-slate-950/70 border-b border-slate-800 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                    <tr>
                      <th className="px-4 py-3">Method</th>
                      <th className="px-4 py-3">Condition</th>
                      <th className="px-4 py-3">Model</th>
                      <th className="px-4 py-3">True Label</th>
                      <th className="px-4 py-3">Predicted</th>
                      <th className="px-4 py-3 text-right">Confidence</th>
                      <th className="px-4 py-3">Snippet Preview</th>
                    </tr>
                  </thead>
                  <AnimatePresence mode="wait" initial={false}>
                    {isLoading ? (
                      <motion.tbody
                        key="mistakes-skeleton"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 0.2, ease: 'easeInOut' }}
                        className="divide-y divide-slate-800/60 font-sans text-xs"
                      >
                        {Array.from({ length: 5 }).map((_, i) => (
                          <SkeletonTableRow key={i} columns={7} />
                        ))}
                      </motion.tbody>
                    ) : (
                      <motion.tbody
                        key="mistakes-rows"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 0.28, ease: 'easeOut' }}
                        className="divide-y divide-slate-800/60 font-sans text-xs"
                      >
                        {displayedMistakes.map((m, idx) => {
                          const isExpanded = expandedMistakeId === `${m.id}-${m.method}-${idx}`;
                          const rowKey = `${m.id}-${m.method}-${idx}`;

                          return (
                            <React.Fragment key={rowKey}>
                              <tr
                                role="button"
                                tabIndex={0}
                                onClick={() =>
                                  setExpandedMistakeId(isExpanded ? null : rowKey)
                                }
                                onKeyDown={(e) => {
                                  if (e.key === 'Enter' || e.key === ' ') {
                                    e.preventDefault();
                                    setExpandedMistakeId(isExpanded ? null : rowKey);
                                  }
                                }}
                                className={`cursor-pointer transition-all duration-150 active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-inset ${
                                  isExpanded
                                    ? 'bg-slate-800 border-l-2 border-teal-400'
                                    : 'hover:bg-slate-800/60 hover:brightness-105'
                                }`}
                              >
                                <td className="px-4 py-3 font-semibold text-white whitespace-nowrap">
                                  {m.method}
                                </td>
                                <td className="px-4 py-3 whitespace-nowrap">
                                  <Badge
                                    variant={m.condition.toLowerCase() === 'clean' ? 'neutral' : 'phishing'}
                                    size="sm"
                                  >
                                    {m.condition}
                                  </Badge>
                                </td>
                                <td className="px-4 py-3 text-slate-400 font-mono text-[11px] whitespace-nowrap">
                                  {m.model}
                                </td>
                                <td className="px-4 py-3 whitespace-nowrap">
                                  <Badge
                                    variant={m.true_label.toLowerCase() === 'phishing' ? 'phishing' : 'legitimate'}
                                    size="sm"
                                  >
                                    {m.true_label}
                                  </Badge>
                                </td>
                                <td className="px-4 py-3 whitespace-nowrap">
                                  <Badge
                                    variant={m.predicted_label.toLowerCase() === 'phishing' ? 'phishing' : 'legitimate'}
                                    size="sm"
                                  >
                                    {m.predicted_label}
                                  </Badge>
                                </td>
                                <td className="px-4 py-3 text-right font-mono font-bold text-rose-300">
                                  {(m.confidence * 100).toFixed(1)}%
                                </td>
                                <td className="px-4 py-3 max-w-xs truncate text-slate-400 font-mono text-[11px]">
                                  {m.snippet}
                                </td>
                              </tr>

                              {/* Inline Expanded Full Email Text with smooth height+opacity animation */}
                              {isExpanded && (
                                <tr className="bg-slate-950/85 backdrop-blur-md border-b border-slate-800/80">
                                  <td colSpan={7} className="p-0 bg-slate-950/85 backdrop-blur-md">
                                    <motion.div
                                      initial={{ height: 0, opacity: 0 }}
                                      animate={{ height: 'auto', opacity: 1 }}
                                      exit={{ height: 0, opacity: 0 }}
                                      transition={{ duration: 0.25, ease: 'easeInOut' }}
                                      className="overflow-hidden px-6 py-4"
                                    >
                                      <div className="space-y-2 max-w-4xl">
                                        <div className="flex items-center justify-between text-xs font-mono text-slate-300 pb-2 border-b border-slate-800/80">
                                          <span>Email ID: <strong className="text-white font-semibold">{m.id}</strong></span>
                                          <span>Ground Truth: <strong className="text-rose-400 font-semibold">{m.true_label}</strong> &bull; Model Output: <strong className="text-teal-400 font-semibold">{m.predicted_label}</strong></span>
                                        </div>
                                        <p className="text-xs text-slate-200 font-mono leading-relaxed whitespace-pre-wrap bg-slate-900/80 backdrop-blur-sm p-3.5 rounded-lg border border-slate-800/80 border-t-slate-700/60 shadow-inner">
                                          {m.snippet}
                                        </p>
                                      </div>
                                    </motion.div>
                                  </td>
                                </tr>
                              )}
                            </React.Fragment>
                          );
                        })}
                      </motion.tbody>
                    )}
                  </AnimatePresence>
                </table>

                {/* Show All / Show Top 10 Expand Control */}
                {mistakes.length > 10 && (
                  <div className="p-3 bg-slate-950/60 border-t border-slate-800 flex items-center justify-between gap-4">
                    <span className="text-xs text-slate-400">
                      Showing <strong className="text-white font-semibold">{displayedMistakes.length}</strong> of{' '}
                      <strong className="text-white font-semibold">{mistakes.length}</strong> worst misclassifications
                    </span>
                    <button
                      type="button"
                      onClick={() => setShowAllMistakes(!showAllMistakes)}
                      className="px-3.5 py-1.5 text-xs font-semibold rounded-lg bg-slate-900 hover:bg-slate-800 text-teal-300 hover:text-teal-200 border border-slate-800 hover:border-slate-700 transition-all flex items-center gap-1.5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400"
                    >
                      {showAllMistakes ? (
                        <>
                          <span>Show top 10 only</span>
                          <ChevronUp className="h-3.5 w-3.5" />
                        </>
                      ) : (
                        <>
                          <span>Show all {mistakes.length} cases</span>
                          <ChevronDown className="h-3.5 w-3.5" />
                        </>
                      )}
                    </button>
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </Card>

      {/* =========================================================================
          SECTION 6: COLLAPSIBLE STATISTICAL TESTS (Animated Height+Opacity)
          ========================================================================= */}
      <Card variant="default" padding="none">
        <div
          role="button"
          tabIndex={0}
          onClick={() => setShowMcNemar(!showMcNemar)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              setShowMcNemar(!showMcNemar);
            }
          }}
          className="p-5 flex items-center justify-between cursor-pointer hover:bg-slate-800/60 hover:scale-[1.005] hover:brightness-105 active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-inset transition-all duration-150 select-none"
        >
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-teal-500/10 text-teal-400 border border-teal-500/20">
              <GitCompare className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white tracking-tight">
                Paired McNemar Hypothesis Tests with Holm-Bonferroni Correction ({sortedMcNemar.length} tests)
              </h3>
              <p className="text-xs text-slate-400">
                Exact two-sided binomial tests on discordant pairs across matching test emails (FWER controlled at α=0.05).
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 text-slate-400">
            <span className="text-xs">{showMcNemar ? 'Collapse' : 'Expand'}</span>
            {showMcNemar ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
          </div>
        </div>

        <AnimatePresence initial={false}>
          {showMcNemar && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.25, ease: 'easeInOut' }}
              className="overflow-hidden border-t border-slate-800"
            >
              {/* 1. Horizontal Significance Strip Chart (Visible at a Glance) */}
              <SignificanceStripChart
                sortedMcNemar={sortedMcNemar}
                isLoading={isLoading}
              />

              {/* 2. Full Table Toggle Control */}
              <div className="px-5 sm:px-6 py-3.5 bg-slate-950/70 border-t border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="flex items-center gap-2 text-xs text-slate-400">
                  <Table className="w-4 h-4 text-teal-400 shrink-0" />
                  <span>
                    Detailed hypothesis metrics (raw discordant pairs, raw p, multipliers, exact thresholds)
                  </span>
                </div>
                <button
                  type="button"
                  onClick={() => setShowFullTable(!showFullTable)}
                  className="self-start sm:self-auto px-3.5 py-1.5 text-xs font-semibold rounded-lg bg-slate-900 hover:bg-slate-800 text-teal-300 hover:text-teal-200 border border-slate-800 hover:border-slate-700 transition-all flex items-center gap-1.5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400"
                >
                  {showFullTable ? (
                    <>
                      <span>Hide details table</span>
                      <ChevronUp className="h-3.5 w-3.5" />
                    </>
                  ) : (
                    <>
                      <span>Show full table ({sortedMcNemar.length} comparisons)</span>
                      <ChevronDown className="h-3.5 w-3.5" />
                    </>
                  )}
                </button>
              </div>

              {/* 3. Collapsible Full Details Table (Collapsed by Default) */}
              <AnimatePresence initial={false}>
                {showFullTable && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.25, ease: 'easeInOut' }}
                    className="overflow-hidden border-t border-slate-800"
                  >
                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-xs text-slate-300">
                        <thead className="bg-slate-950/70 border-b border-slate-800 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                          <tr>
                            <th className="px-4 py-3">Rank (k)</th>
                            <th className="px-4 py-3">Hypothesis Comparison</th>
                            <th className="px-4 py-3 text-right">Discordant (b / c)</th>
                            <th className="px-4 py-3 text-right">Raw p-value</th>
                            <th className="px-4 py-3 text-right">Multiplier</th>
                            <th className="px-4 py-3 text-right">Corrected p-value</th>
                            <th className="px-4 py-3 text-center">Decision (α=0.05)</th>
                          </tr>
                        </thead>
                        <AnimatePresence mode="wait" initial={false}>
                          {isLoading ? (
                            <motion.tbody
                              key="mcnemar-skeleton"
                              initial={{ opacity: 0 }}
                              animate={{ opacity: 1 }}
                              exit={{ opacity: 0 }}
                              transition={{ duration: 0.2, ease: 'easeInOut' }}
                              className="divide-y divide-slate-800/60 font-mono text-xs"
                            >
                              {Array.from({ length: 6 }).map((_, i) => (
                                <SkeletonTableRow key={i} columns={7} />
                              ))}
                            </motion.tbody>
                          ) : (
                            <motion.tbody
                              key="mcnemar-rows"
                              initial={{ opacity: 0 }}
                              animate={{ opacity: 1 }}
                              exit={{ opacity: 0 }}
                              transition={{ duration: 0.28, ease: 'easeOut' }}
                              className="divide-y divide-slate-800/60 font-mono text-xs"
                            >
                              {sortedMcNemar.map(([key, test]) => {
                                const isSig = test.significant_after_holm_bonferroni;
                                const rawP = test.raw_p_value ?? test.p_value;
                                const hbP = test.holm_bonferroni_p_value ?? test.p_value;
                                const rank = test.holm_bonferroni_rank ?? '-';
                                const factor = test.holm_bonferroni_factor ?? '-';
                                const compLabel = COMPARISON_LABELS[key] || key;

                                return (
                                  <tr
                                    key={key}
                                    tabIndex={0}
                                    className="hover:bg-slate-800/60 hover:brightness-105 active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-inset focus-visible:bg-slate-800/50 transition-all duration-150 cursor-pointer"
                                  >
                                    <td className="px-4 py-3 font-bold text-slate-400 font-sans">
                                      #{rank}
                                    </td>
                                    <td className="px-4 py-3 font-sans font-medium text-white whitespace-nowrap">
                                      {compLabel}
                                    </td>
                                    <td className="px-4 py-3 text-right text-slate-300">
                                      {test['a_correct_b_wrong (b)']} / {test['a_wrong_b_correct (c)']}
                                    </td>
                                    <td className="px-4 py-3 text-right text-slate-400">
                                      {rawP < 0.0001 ? rawP.toExponential(3) : rawP.toFixed(4)}
                                    </td>
                                    <td className="px-4 py-3 text-right text-slate-400">
                                      {factor}
                                    </td>
                                    <td className="px-4 py-3 text-right font-bold">
                                      <span className={isSig ? 'text-teal-300' : 'text-slate-400'}>
                                        {hbP < 0.0001 ? hbP.toExponential(3) : hbP.toFixed(4)}
                                      </span>
                                    </td>
                                    <td className="px-4 py-3 text-center">
                                      {isSig ? (
                                        <Badge variant="legitimate" size="sm" dot>
                                          <CheckCircle2 className="h-3 w-3 mr-1 inline" />
                                          Reject H0 (Significant)
                                        </Badge>
                                      ) : (
                                        <Badge variant="neutral" size="sm">
                                          Fail to Reject
                                        </Badge>
                                      )}
                                    </td>
                                  </tr>
                                );
                              })}
                            </motion.tbody>
                          )}
                        </AnimatePresence>
                      </table>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          )}
        </AnimatePresence>
      </Card>
    </>
  );
};

export default MistakesAndHypothesisTests;
