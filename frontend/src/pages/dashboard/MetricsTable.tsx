import React, { useState } from 'react';
import {
  FileText,
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  ChevronDown,
  Layers,
} from 'lucide-react';
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
  const [expandedRowIds, setExpandedRowIds] = useState<Set<string>>(new Set());

  const toggleRow = (id: string) => {
    setExpandedRowIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const allExpanded = sortedRows.length > 0 && expandedRowIds.size === sortedRows.length;
  const toggleAll = () => {
    if (allExpanded) {
      setExpandedRowIds(new Set());
    } else {
      setExpandedRowIds(new Set(sortedRows.map((r) => r.id)));
    }
  };

  const renderSortHeader = (
    field: SortField,
    label: string,
    align: 'left' | 'right' = 'left',
    className?: string
  ) => {
    const isActive = sortField === field;
    return (
      <th
        tabIndex={0}
        role="columnheader"
        aria-sort={isActive ? (sortDirection === 'asc' ? 'ascending' : 'descending') : 'none'}
        onClick={() => onSort(field)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            onSort(field);
          }
        }}
        className={`px-4 py-3.5 cursor-pointer transition-all duration-150 select-none group focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-inset ${
          isActive
            ? 'text-teal-300 font-bold bg-slate-900/70'
            : 'text-slate-400 hover:text-white hover:bg-slate-800/40'
        } ${className || ''}`}
      >
        <div className={`flex items-center gap-1.5 ${align === 'right' ? 'justify-end' : 'justify-start'}`}>
          <span className="tracking-wider uppercase text-[11px] whitespace-nowrap">{label}</span>
          {isActive ? (
            sortDirection === 'asc' ? (
              <ArrowUp className="h-3.5 w-3.5 text-teal-400 stroke-[2.5]" />
            ) : (
              <ArrowDown className="h-3.5 w-3.5 text-teal-400 stroke-[2.5]" />
            )
          ) : (
            <ArrowUpDown className="h-3 w-3 text-slate-500 opacity-40 group-hover:opacity-80 transition-opacity" />
          )}
        </div>
      </th>
    );
  };

  return (
    <Card variant="elevated" padding="none">
      <div className="p-5 border-b border-slate-800 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
            <FileText className="h-4 w-4 text-teal-400" />
            Benchmark Performance Matrix ({sortedRows.length} configurations)
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Click column headers to sort. Expand any row to inspect Precision, Specificity, Accuracy, and Latency.
          </p>
        </div>

        {/* Expand/Collapse All Details Control (Replacing duplicate Active Sort text badge) */}
        {sortedRows.length > 0 && (
          <button
            type="button"
            onClick={toggleAll}
            className="text-xs text-slate-400 hover:text-teal-300 font-medium px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 hover:border-slate-700 transition-colors flex items-center gap-1.5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400"
          >
            <Layers className="h-3.5 w-3.5 text-teal-400" />
            <span>{allExpanded ? 'Collapse All Details' : 'Expand All Details'}</span>
          </button>
        )}
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-slate-950/70 border-b border-slate-800 text-[11px] font-semibold text-slate-400 uppercase tracking-wider select-none">
            <tr>
              {renderSortHeader('method', 'Method & Model', 'left')}
              {renderSortHeader('condition', 'Condition', 'left')}
              {renderSortHeader('recall', 'Recall (Catch)', 'right')}
              {renderSortHeader('fpr', 'FPR (Alarm)', 'right')}
              {renderSortHeader('f1', 'F1 Score', 'right')}
              <th className="px-3 py-3.5 text-center w-12 text-slate-500">
                <span className="sr-only">Toggle details</span>
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
                  <SkeletonTableRow key={i} columns={6} />
                ))}
              </motion.tbody>
            ) : (
              <motion.tbody
                key="matrix-rows"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.28, ease: 'easeOut' }}
                className="divide-y divide-slate-800/60 text-xs"
              >
                {sortedRows.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-8 text-center text-slate-500 font-sans">
                      No benchmark configurations match the selected filters.
                    </td>
                  </tr>
                ) : (
                  sortedRows.map((row) => {
                    const isHighF1 = row.f1 > 0.85;
                    const isLowFpr = row.fpr < 0.05;
                    const isPilot = row.sampleSize.includes('Pilot');
                    const isExpanded = expandedRowIds.has(row.id);

                    return (
                      <React.Fragment key={row.id}>
                        <tr
                          tabIndex={0}
                          role="button"
                          aria-expanded={isExpanded}
                          onClick={() => toggleRow(row.id)}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter' || e.key === ' ') {
                              e.preventDefault();
                              toggleRow(row.id);
                            }
                          }}
                          className={`cursor-pointer transition-colors duration-150 select-none ${
                            isExpanded
                              ? 'bg-slate-900/90'
                              : 'hover:bg-slate-800/50'
                          }`}
                        >
                          {/* 1. Method Name, Model & Single Consolidated Sample Badge */}
                          <td className="px-4 py-3 font-sans">
                            <div className="flex flex-col gap-0.5">
                              <span className="font-semibold text-white flex items-center gap-1.5 whitespace-nowrap">
                                {row.methodCode.startsWith('M4') && (
                                  <span className="h-1.5 w-1.5 rounded-full bg-teal-400 shrink-0" />
                                )}
                                {row.method}
                              </span>
                              <div className="flex items-center gap-2 mt-0.5">
                                <span className="text-[11px] text-slate-400 font-sans truncate">
                                  {row.model}
                                </span>
                                {/* Consolidated single badge per row */}
                                <span
                                  className={`text-[10px] px-1.5 py-0.2 rounded font-mono shrink-0 ${
                                    isPilot
                                      ? 'bg-purple-500/15 text-purple-300 border border-purple-500/30 font-semibold'
                                      : 'bg-slate-800/90 text-slate-400 border border-slate-700/60'
                                  }`}
                                >
                                  {row.sampleSize}
                                </span>
                              </div>
                            </div>
                          </td>

                          {/* 2. Condition */}
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

                          {/* 3. Recall (Catch) */}
                          <td className="px-4 py-3 text-right font-mono">
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

                          {/* 4. FPR (Alarm) */}
                          <td className="px-4 py-3 text-right font-mono">
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

                          {/* 5. F1 Score (No truncation) */}
                          <td className="px-4 py-3 text-right font-mono font-bold whitespace-nowrap">
                            <span className={isHighF1 ? 'text-teal-300' : 'text-slate-200'}>
                              {row.f1.toFixed(4)}
                            </span>
                          </td>

                          {/* 6. Expand Chevron */}
                          <td className="px-3 py-3 text-center">
                            <div className="flex items-center justify-center">
                              <ChevronDown
                                className={`h-4 w-4 text-slate-400 transition-transform duration-200 ${
                                  isExpanded ? 'rotate-180 text-teal-400' : 'group-hover:text-slate-200'
                                }`}
                              />
                            </div>
                          </td>
                        </tr>

                        {/* Inline Expandable Row Details: Precision, Specificity, Accuracy, Latency */}
                        {isExpanded && (
                          <tr className="bg-slate-950/70 border-b border-slate-800/80">
                            <td colSpan={6} className="p-0">
                              <motion.div
                                initial={{ height: 0, opacity: 0 }}
                                animate={{ height: 'auto', opacity: 1 }}
                                exit={{ height: 0, opacity: 0 }}
                                transition={{ duration: 0.2, ease: 'easeInOut' }}
                                className="overflow-hidden px-5 py-3.5 bg-slate-900/40 border-l-2 border-teal-500/80"
                              >
                                <div className="space-y-2.5">
                                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
                                    <div className="p-2.5 rounded-lg bg-slate-950/80 border border-slate-800/80">
                                      <span className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold block">
                                        Precision
                                      </span>
                                      <span className="text-sm font-bold font-mono text-slate-200">
                                        {(row.precision * 100).toFixed(2)}%
                                      </span>
                                    </div>
                                    <div className="p-2.5 rounded-lg bg-slate-950/80 border border-slate-800/80">
                                      <span className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold block">
                                        Specificity (TNR)
                                      </span>
                                      <span className="text-sm font-bold font-mono text-slate-200">
                                        {(row.specificity * 100).toFixed(2)}%
                                      </span>
                                    </div>
                                    <div className="p-2.5 rounded-lg bg-slate-950/80 border border-slate-800/80">
                                      <span className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold block">
                                        Accuracy
                                      </span>
                                      <span className="text-sm font-bold font-mono text-slate-200">
                                        {(row.accuracy * 100).toFixed(2)}%
                                      </span>
                                    </div>
                                    <div className="p-2.5 rounded-lg bg-slate-950/80 border border-slate-800/80">
                                      <span className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold block">
                                        Mean Latency
                                      </span>
                                      <span className="text-sm font-bold font-mono text-slate-300">
                                        {row.latencyDisplay}
                                      </span>
                                    </div>
                                  </div>

                                  <div className="flex flex-wrap items-center justify-between text-[11px] text-slate-400 pt-1 font-mono">
                                    <span>
                                      Cohort:{' '}
                                      <strong className="text-white font-semibold">{row.sampleSize}</strong> ({row.sampleCount} test emails)
                                    </span>
                                    <span>
                                      Runtime:{' '}
                                      <strong className="text-slate-300 font-semibold">{row.model}</strong>
                                    </span>
                                  </div>
                                </div>
                              </motion.div>
                            </td>
                          </tr>
                        )}
                      </React.Fragment>
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
