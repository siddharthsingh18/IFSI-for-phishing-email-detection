import React from 'react';
import { FileText, ArrowUpDown } from 'lucide-react';
import { Card } from '../../components/Card';
import { Badge } from '../../components/Badge';
import { SkeletonTableRow } from '../../components/Skeleton';
import { motion, AnimatePresence } from 'framer-motion';
import type { MetricTableRow, SortField } from './types';

export interface MetricsTableProps {
  isLoading: boolean;
  sortedRows: MetricTableRow[];
  sortField: SortField;
  sortDirection: 'asc' | 'desc';
  onSort: (field: SortField) => void;
}

export const MetricsTable: React.FC<MetricsTableProps> = ({
  isLoading,
  sortedRows,
  sortField,
  sortDirection,
  onSort,
}) => {
  return (
    <Card variant="elevated" padding="none">
      <div className="p-5 border-b border-slate-800 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
            <FileText className="h-4 w-4 text-teal-400" />
            Benchmark Performance Matrix ({sortedRows.length} configurations)
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Click any column header to sort ascending or descending. Sample size explicitly tagged per row.
          </p>
        </div>

        <Badge variant="neutral" size="sm">
          Active Sort: {sortField.toUpperCase()} ({sortDirection.toUpperCase()})
        </Badge>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-slate-950/70 border-b border-slate-800 text-[11px] font-semibold text-slate-400 uppercase tracking-wider select-none">
            <tr>
              <th
                tabIndex={0}
                role="button"
                onClick={() => onSort('method')}
                onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onSort('method'); } }}
                className="px-4 py-3 cursor-pointer hover:text-white hover:bg-slate-800/40 hover:brightness-105 active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-inset transition-all duration-150 select-none"
              >
                <div className="flex items-center gap-1">
                  <span>Method</span>
                  <ArrowUpDown className="h-3 w-3" />
                </div>
              </th>
              <th
                tabIndex={0}
                role="button"
                onClick={() => onSort('model')}
                onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onSort('model'); } }}
                className="px-4 py-3 cursor-pointer hover:text-white hover:bg-slate-800/40 hover:brightness-105 active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-inset transition-all duration-150 select-none"
              >
                <div className="flex items-center gap-1">
                  <span>Model &amp; Size</span>
                  <ArrowUpDown className="h-3 w-3" />
                </div>
              </th>
              <th
                tabIndex={0}
                role="button"
                onClick={() => onSort('condition')}
                onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onSort('condition'); } }}
                className="px-4 py-3 cursor-pointer hover:text-white hover:bg-slate-800/40 hover:brightness-105 active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-inset transition-all duration-150 select-none"
              >
                <div className="flex items-center gap-1">
                  <span>Condition</span>
                  <ArrowUpDown className="h-3 w-3" />
                </div>
              </th>
              <th
                tabIndex={0}
                role="button"
                onClick={() => onSort('accuracy')}
                onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onSort('accuracy'); } }}
                className="px-4 py-3 cursor-pointer hover:text-white active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-inset transition-all select-none text-right"
              >
                <div className="flex items-center justify-end gap-1">
                  <span>Accuracy</span>
                  <ArrowUpDown className="h-3 w-3" />
                </div>
              </th>
              <th
                tabIndex={0}
                role="button"
                onClick={() => onSort('recall')}
                onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onSort('recall'); } }}
                className="px-4 py-3 cursor-pointer hover:text-white active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-inset transition-all select-none text-right"
              >
                <div className="flex items-center justify-end gap-1">
                  <span>Recall (Catch)</span>
                  <ArrowUpDown className="h-3 w-3" />
                </div>
              </th>
              <th
                tabIndex={0}
                role="button"
                onClick={() => onSort('fpr')}
                onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onSort('fpr'); } }}
                className="px-4 py-3 cursor-pointer hover:text-white active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-inset transition-all select-none text-right"
              >
                <div className="flex items-center justify-end gap-1">
                  <span>FPR (Alarm)</span>
                  <ArrowUpDown className="h-3 w-3" />
                </div>
              </th>
              <th
                tabIndex={0}
                role="button"
                onClick={() => onSort('precision')}
                onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onSort('precision'); } }}
                className="px-4 py-3 cursor-pointer hover:text-white active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-inset transition-all select-none text-right"
              >
                <div className="flex items-center justify-end gap-1">
                  <span>Precision</span>
                  <ArrowUpDown className="h-3 w-3" />
                </div>
              </th>
              <th
                tabIndex={0}
                role="button"
                onClick={() => onSort('f1')}
                onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onSort('f1'); } }}
                className="px-4 py-3 cursor-pointer hover:text-white active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-inset transition-all select-none text-right"
              >
                <div className="flex items-center justify-end gap-1">
                  <span>F1 Score</span>
                  <ArrowUpDown className="h-3 w-3" />
                </div>
              </th>
              <th
                tabIndex={0}
                role="button"
                onClick={() => onSort('latencySeconds')}
                onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onSort('latencySeconds'); } }}
                className="px-4 py-3 cursor-pointer hover:text-white active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-inset transition-all select-none text-right"
              >
                <div className="flex items-center justify-end gap-1">
                  <span>Latency</span>
                  <ArrowUpDown className="h-3 w-3" />
                </div>
              </th>
            </tr>
          </thead>
          <AnimatePresence mode="wait" initial={false}>
            {isLoading ? (
              <motion.tbody
                key="matrix-skeleton"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2, ease: 'easeInOut' }}
                className="divide-y divide-slate-800/60 font-mono text-xs"
              >
                {Array.from({ length: 8 }).map((_, i) => (
                  <SkeletonTableRow key={i} columns={9} />
                ))}
              </motion.tbody>
            ) : (
              <motion.tbody
                key="matrix-rows"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.28, ease: 'easeOut' }}
                className="divide-y divide-slate-800/60 font-mono text-xs"
              >
                {sortedRows.length === 0 ? (
                  <tr>
                    <td colSpan={9} className="px-6 py-8 text-center text-slate-500 font-sans">
                      No benchmark configurations match the selected filters.
                    </td>
                  </tr>
                ) : (
                  sortedRows.map((row) => {
                    const isHighF1 = row.f1 > 0.85;
                    const isLowFpr = row.fpr < 0.05;
                    const isPilot = row.sampleSize.includes('Pilot');

                    return (
                      <tr
                        key={row.id}
                        tabIndex={0}
                        className="hover:bg-slate-800/60 hover:brightness-105 active:scale-[0.98] active:bg-slate-800/80 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-inset focus-visible:bg-slate-800/70 transition-all duration-150 group cursor-pointer"
                      >
                        <td className="px-4 py-3 font-sans font-semibold text-white whitespace-nowrap">
                          <span className="flex items-center gap-1.5">
                            {row.methodCode.startsWith('M4') && (
                              <span className="h-1.5 w-1.5 rounded-full bg-teal-400" />
                            )}
                            {row.method}
                          </span>
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap">
                          <div className="flex items-center gap-1.5">
                            <span className="text-slate-300 font-sans">{row.model}</span>
                            <span
                              className={`text-[10px] px-1.5 py-0.5 rounded font-mono ${
                                isPilot
                                  ? 'bg-purple-500/10 text-purple-300 border border-purple-500/30 font-semibold'
                                  : 'bg-slate-800 text-slate-400'
                              }`}
                            >
                              {row.sampleSize}
                            </span>
                          </div>
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap">
                          <Badge
                            variant={
                              row.condition === 'Clean'
                                ? 'neutral'
                                : row.condition === 'Marked'
                                ? 'phishing'
                                : 'injection'
                            }
                            size="sm"
                          >
                            {row.condition}
                          </Badge>
                        </td>
                        <td className="px-4 py-3 text-right text-slate-200">
                          {(row.accuracy * 100).toFixed(2)}%
                        </td>
                        <td className="px-4 py-3 text-right">
                          <span
                            className={
                              row.recall > 0.85
                                ? 'text-emerald-400 font-semibold'
                                : row.recall < 0.4
                                ? 'text-rose-400'
                                : 'text-slate-200'
                            }
                          >
                            {(row.recall * 100).toFixed(2)}%
                          </span>
                        </td>
                        <td className="px-4 py-3 text-right">
                          <span
                            className={
                              isLowFpr
                                ? 'text-teal-400 font-semibold'
                                : row.fpr > 0.6
                                ? 'text-amber-400'
                                : 'text-slate-200'
                            }
                          >
                            {(row.fpr * 100).toFixed(2)}%
                          </span>
                        </td>
                        <td className="px-4 py-3 text-right text-slate-300">
                          {(row.precision * 100).toFixed(2)}%
                        </td>
                        <td className="px-4 py-3 text-right font-bold">
                          <span className={isHighF1 ? 'text-teal-300' : 'text-slate-200'}>
                            {row.f1.toFixed(4)}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-right text-slate-400">
                          {row.latencyDisplay}
                        </td>
                      </tr>
                    );
                  })
                )}
              </motion.tbody>
            )}
          </AnimatePresence>
        </table>
      </div>
    </Card>
  );
};

export default MetricsTable;
