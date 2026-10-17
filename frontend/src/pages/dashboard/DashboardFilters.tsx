import React from 'react';
import { Filter, RotateCcw } from 'lucide-react';
import { Card } from '../../components/Card';

export interface DashboardFiltersProps {
  filterMethod: string;
  setFilterMethod: (v: string) => void;
  filterCondition: string;
  setFilterCondition: (v: string) => void;
  filterModel: string;
  setFilterModel: (v: string) => void;
  onResetFilters: () => void;
}

export const DashboardFilters: React.FC<DashboardFiltersProps> = ({
  filterMethod,
  setFilterMethod,
  filterCondition,
  setFilterCondition,
  filterModel,
  setFilterModel,
  onResetFilters,
}) => {
  return (
    <Card variant="default" padding="md">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-center gap-2 text-xs font-semibold text-slate-300">
          <Filter className="h-4 w-4 text-teal-400" />
          <span>Reactive Benchmark Filters:</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 w-full md:w-auto flex-1 max-w-3xl">
          {/* Method Filter */}
          <div>
            <label className="block text-[11px] font-semibold text-slate-400 mb-1">
              Architecture Method
            </label>
            <select
              value={filterMethod}
              onChange={(e) => setFilterMethod(e.target.value)}
              className="w-full rounded-xl bg-slate-950 border border-slate-800 px-3 py-1.5 text-xs text-slate-200 hover:border-slate-700 hover:bg-slate-900/50 active:scale-[0.98] focus:outline-none focus:border-teal-500 focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 transition-all duration-150 cursor-pointer"
            >
              <option value="all">All Methods (M1–M4)</option>
              <option value="M1">M1: TF-IDF + LogReg</option>
              <option value="M2">M2: Zero-Shot LLM</option>
              <option value="M3">M3: RAG Combined</option>
              <option value="M4">M4: RAG Decoupled (IFSI)</option>
            </select>
          </div>

          {/* Condition Filter */}
          <div>
            <label className="block text-[11px] font-semibold text-slate-400 mb-1">
              Adversarial Condition
            </label>
            <select
              value={filterCondition}
              onChange={(e) => setFilterCondition(e.target.value)}
              className="w-full rounded-xl bg-slate-950 border border-slate-800 px-3 py-1.5 text-xs text-slate-200 hover:border-slate-700 hover:bg-slate-900/50 active:scale-[0.98] focus:outline-none focus:border-teal-500 focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 transition-all duration-150 cursor-pointer"
            >
              <option value="all">All Conditions (Clean, Marked, Unmarked)</option>
              <option value="clean">Clean (No Injections)</option>
              <option value="marked">Marked (Explicit Delimiters)</option>
              <option value="unmarked">Unmarked (Natural Disguises)</option>
            </select>
          </div>

          {/* Model Filter */}
          <div>
            <label className="block text-[11px] font-semibold text-slate-400 mb-1">
              Model &amp; Cohort
            </label>
            <select
              value={filterModel}
              onChange={(e) => setFilterModel(e.target.value)}
              className="w-full rounded-xl bg-slate-950 border border-slate-800 px-3 py-1.5 text-xs text-slate-200 hover:border-slate-700 hover:bg-slate-900/50 active:scale-[0.98] focus:outline-none focus:border-teal-500 focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 transition-all duration-150 cursor-pointer"
            >
              <option value="all">All Models [N=522 &amp; Pilot N=50]</option>
              <option value="qwen">qwen2.5:0.5b [Full Split N=522]</option>
              <option value="llama">llama3.2:3b [Pilot Cohort N=50]</option>
              <option value="tfidf">TF-IDF Linear Baseline</option>
            </select>
          </div>
        </div>

        {(filterMethod !== 'all' || filterCondition !== 'all' || filterModel !== 'all') && (
          <button
            type="button"
            onClick={onResetFilters}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium text-slate-400 hover:text-white bg-slate-800 hover:bg-slate-700 hover:scale-[1.02] hover:brightness-105 active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 transition-all duration-150 self-end md:self-center"
          >
            <RotateCcw className="h-3.5 w-3.5" />
            <span>Reset</span>
          </button>
        )}
      </div>
    </Card>
  );
};

export default DashboardFilters;
