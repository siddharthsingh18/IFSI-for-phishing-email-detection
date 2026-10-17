import React, { useEffect, useState, useMemo } from 'react';
import {
  BarChart3,
  Database,
  GitCompare,
  Zap,
  Target,
  ShieldAlert,
  ChevronDown,
  ChevronUp,
  Filter,
  ArrowUpDown,
  RotateCcw,
  CheckCircle2,
  AlertCircle,
  FileText,
} from 'lucide-react';
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
import {
  apiClient,
  type BenchmarkSummary,
  type McNemarResponse,
  type MistakeRecord,
} from '../api/client';
import { Card } from '../components/Card';
import { OfflineFallbackBanner } from '../components/OfflineFallbackBanner';
import { Badge } from '../components/Badge';
import { StatTile } from '../components/StatTile';
import { SkeletonStatTile, SkeletonTableRow, SkeletonChart } from '../components/Skeleton';
import { motion, AnimatePresence } from 'framer-motion';
import { fadeInUp } from '../lib/motion';
import { useCountUp } from '../hooks/useCountUp';
import { useTheme } from '../hooks/useTheme';

// Human-friendly label mapping for methods
const METHOD_LABELS: Record<string, string> = {
  M1: 'M1: TF-IDF + LogReg',
  M2: 'M2: Zero-Shot LLM',
  M3: 'M3: RAG Combined',
  M4: 'M4: RAG Decoupled (IFSI)',
};

// McNemar comparison labels
const COMPARISON_LABELS: Record<string, string> = {
  M2_vs_M3__clean: 'M2 vs M3 (Clean)',
  M2_vs_M3__marked: 'M2 vs M3 (Marked Attack)',
  M2_vs_M3__unmarked: 'M2 vs M3 (Unmarked Attack)',
  marked_vs_unmarked__M1: 'M1 (Marked vs Unmarked)',
  marked_vs_unmarked__M2: 'M2 (Marked vs Unmarked)',
  marked_vs_unmarked__M3: 'M3 (Marked vs Unmarked)',
  marked_vs_unmarked__M4: 'M4 (Marked vs Unmarked)',
  combined_vs_decoupled_M3_vs_M4__clean: 'M3 vs M4 (Clean)',
  combined_vs_decoupled_M3_vs_M4__marked: 'M3 vs M4 (Marked Attack)',
  combined_vs_decoupled_M3_vs_M4__unmarked: 'M3 vs M4 (Unmarked Attack)',
};

interface MetricTableRow {
  id: string;
  method: string;
  methodCode: string;
  model: string;
  condition: string;
  sampleSize: string;
  sampleCount: number;
  accuracy: number;
  recall: number;
  fpr: number;
  precision: number;
  f1: number;
  invalidRate: number;
  latencySeconds: number;
  latencyDisplay: string;
}

type SortField = 'method' | 'condition' | 'model' | 'accuracy' | 'recall' | 'fpr' | 'precision' | 'f1' | 'latencySeconds';

export const DashboardPage: React.FC = () => {
  const { chartColors } = useTheme();
  // Data States
  const [summary, setSummary] = useState<BenchmarkSummary | null>(null);
  const [mcnemar, setMcnemar] = useState<McNemarResponse | null>(null);
  const [mistakes, setMistakes] = useState<MistakeRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isUsingFallback, setIsUsingFallback] = useState(false);

  // Reactive Filter States
  const [filterMethod, setFilterMethod] = useState<string>('all');
  const [filterCondition, setFilterCondition] = useState<string>('all');
  const [filterModel, setFilterModel] = useState<string>('all');

  // Sorting State for Metrics Table
  const [sortField, setSortField] = useState<SortField>('f1');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');

  // Collapsible Sections States
  const [showMistakes, setShowMistakes] = useState(true);
  const [showMcNemar, setShowMcNemar] = useState(true);
  const [expandedMistakeId, setExpandedMistakeId] = useState<string | null>(null);

  // Fetch benchmark data on mount
  useEffect(() => {
    let mounted = true;
    Promise.all([
      apiClient.getBenchmarkSummary(),
      apiClient.getMcNemarResults(),
      apiClient.getWorstMistakes({ limit: 10 }),
    ])
      .then(([summaryData, mcnemarData, mistakesData]) => {
        if (!mounted) return;
        setSummary(summaryData);
        setMcnemar(mcnemarData);
        setMistakes(mistakesData);
        setIsLoading(false);
      })
      .catch((err) => {
        console.error('Failed to load dashboard benchmark data:', err);
        if (!mounted) return;
        setIsUsingFallback(true);
        setIsLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, []);

  // Format precomputed metrics into unified rows
  const allRows: MetricTableRow[] = useMemo(() => {
    if (!summary?.cells) return [];
    const rows: MetricTableRow[] = [];

    // 1. Full benchmark cells (N=522)
    Object.entries(summary.cells).forEach(([cellKey, cell]) => {
      const m = cell.method;
      const c = cell.condition;
      const met = cell.metrics;
      const modelName = m === 'M1' ? 'TF-IDF + LogReg' : 'qwen2.5:0.5b';
      const latSec = met.mean_latency_seconds || 0;
      const latStr = latSec < 0.001 ? `${(latSec * 1000).toFixed(2)} ms` : `${latSec.toFixed(3)} s`;

      rows.push({
        id: cellKey,
        method: METHOD_LABELS[m] || m,
        methodCode: m,
        model: modelName,
        condition: c.charAt(0).toUpperCase() + c.slice(1),
        sampleSize: 'N=522',
        sampleCount: 522,
        accuracy: met.accuracy,
        recall: met.recall,
        fpr: met.fpr,
        precision: met.precision,
        f1: met.f1,
        invalidRate: Number((met as any).invalid_schema_rate || 0),
        latencySeconds: latSec,
        latencyDisplay: latStr,
      });
    });

    // 2. Pilot comparison cells (N=50) for Llama-3.2:3b comparison
    const pilotRows: MetricTableRow[] = [
      {
        id: 'pilot_m2_clean_llama',
        method: METHOD_LABELS['M2'],
        methodCode: 'M2',
        model: 'llama3.2:3b',
        condition: 'Clean',
        sampleSize: 'Pilot N=50',
        sampleCount: 50,
        accuracy: 0.940,
        recall: 0.882,
        fpr: 0.030,
        precision: 0.938,
        f1: 0.909,
        invalidRate: 0.0,
        latencySeconds: 1.150,
        latencyDisplay: '1.150 s',
      },
      {
        id: 'pilot_m2_unmarked_llama',
        method: METHOD_LABELS['M2'],
        methodCode: 'M2',
        model: 'llama3.2:3b',
        condition: 'Unmarked',
        sampleSize: 'Pilot N=50',
        sampleCount: 50,
        accuracy: 0.440,
        recall: 0.235,
        fpr: 0.455,
        precision: 0.211,
        f1: 0.222,
        invalidRate: 0.0,
        latencySeconds: 1.190,
        latencyDisplay: '1.190 s',
      },
      {
        id: 'pilot_m3_unmarked_llama',
        method: METHOD_LABELS['M3'],
        methodCode: 'M3',
        model: 'llama3.2:3b',
        condition: 'Unmarked',
        sampleSize: 'Pilot N=50',
        sampleCount: 50,
        accuracy: 0.380,
        recall: 0.176,
        fpr: 0.515,
        precision: 0.158,
        f1: 0.167,
        invalidRate: 0.0,
        latencySeconds: 2.140,
        latencyDisplay: '2.140 s',
      },
      {
        id: 'pilot_m4_unmarked_llama',
        method: METHOD_LABELS['M4'],
        methodCode: 'M4',
        model: 'llama3.2:3b',
        condition: 'Unmarked',
        sampleSize: 'Pilot N=50',
        sampleCount: 50,
        accuracy: 0.720,
        recall: 0.941,
        fpr: 0.394,
        precision: 0.552,
        f1: 0.696,
        invalidRate: 0.0,
        latencySeconds: 2.650,
        latencyDisplay: '2.650 s',
      },
    ];

    return [...rows, ...pilotRows];
  }, [summary]);

  // Reactive Filtering
  const filteredRows = useMemo(() => {
    return allRows.filter((r) => {
      // 1. Method Filter
      if (filterMethod !== 'all' && r.methodCode !== filterMethod) {
        return false;
      }

      // 2. Condition Filter
      if (filterCondition !== 'all') {
        const condLower = r.condition.toLowerCase();
        if (condLower !== filterCondition.toLowerCase()) return false;
      }

      // 3. Model Filter
      if (filterModel !== 'all') {
        if (filterModel === 'qwen' && !r.model.includes('qwen')) return false;
        if (filterModel === 'llama' && !r.model.includes('llama')) return false;
        if (filterModel === 'tfidf' && !r.model.includes('TF-IDF')) return false;
      }

      return true;
    });
  }, [allRows, filterMethod, filterCondition, filterModel]);

  // Filter combination key for AnimatePresence cross-fading
  const filterKey = `${filterMethod}_${filterCondition}_${filterModel}`;

  // Sorting Handler
  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection((prev) => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  // Sorted Rows
  const sortedRows = useMemo(() => {
    return [...filteredRows].sort((a, b) => {
      let aVal = a[sortField];
      let bVal = b[sortField];

      if (typeof aVal === 'string') {
        aVal = (aVal as string).toLowerCase();
        bVal = (bVal as string).toLowerCase();
      }

      if (aVal < bVal) return sortDirection === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });
  }, [filteredRows, sortField, sortDirection]);

  // Reset Filters
  const handleResetFilters = () => {
    setFilterMethod('all');
    setFilterCondition('all');
    setFilterModel('all');
  };

  // Recharts Data Transformation
  const chartData = useMemo(() => {
    return sortedRows.map((r) => ({
      name: `${r.methodCode} (${r.condition})`,
      fullName: `${r.method} - ${r.condition}`,
      model: r.model,
      sampleSize: r.sampleSize,
      recallPct: Number((r.recall * 100).toFixed(1)),
      fprPct: Number((r.fpr * 100).toFixed(1)),
      accuracyPct: Number((r.accuracy * 100).toFixed(1)),
      latencyMs: Number((r.latencySeconds * 1000).toFixed(1)),
    }));
  }, [sortedRows]);

  // Top KPI calculations
  const topStats = useMemo(() => {
    if (allRows.length === 0) {
      return {
        bestF1Num: 0.968,
        lowestFprNum: 0.25,
        fastestLatNum: 0.28,
        totalEmailsNum: 522,
        bestF1: { value: '0.968', sub: 'M1 Clean', sample: 'N=522' },
        lowestFpr: { value: '0.25%', sub: 'M1 Baseline', sample: 'N=522' },
        fastestLatency: { value: '0.28 ms', sub: 'M1 TF-IDF', sample: 'N=522' },
        totalEmails: { value: '522', sub: 'Full Test Split', sample: 'N=522' },
      };
    }

    // Best F1
    const bestF1Row = [...allRows].sort((a, b) => b.f1 - a.f1)[0];
    // Lowest FPR
    const lowestFprRow = [...allRows].sort((a, b) => a.fpr - b.fpr)[0];
    // Fastest Latency
    const fastestRow = [...allRows].sort((a, b) => a.latencySeconds - b.latencySeconds)[0];

    const bestF1Num = bestF1Row ? bestF1Row.f1 : 0.968;
    const lowestFprNum = lowestFprRow ? Number((lowestFprRow.fpr * 100).toFixed(2)) : 0.25;
    const fastestLatNum = fastestRow ? Number((fastestRow.latencySeconds * 1000).toFixed(2)) : 0.28;
    const totalEmailsNum = 522;

    return {
      bestF1Num,
      lowestFprNum,
      fastestLatNum,
      totalEmailsNum,
      bestF1: {
        value: bestF1Row.f1.toFixed(4),
        sub: `${bestF1Row.methodCode} (${bestF1Row.condition}) - ${bestF1Row.model}`,
        sample: bestF1Row.sampleSize,
      },
      lowestFpr: {
        value: `${(lowestFprRow.fpr * 100).toFixed(2)}%`,
        sub: `${lowestFprRow.methodCode} (${lowestFprRow.condition})`,
        sample: lowestFprRow.sampleSize,
      },
      fastestLatency: {
        value: fastestRow.latencyDisplay,
        sub: `${fastestRow.methodCode} (${fastestRow.model})`,
        sample: fastestRow.sampleSize,
      },
      totalEmails: {
        value: '522',
        sub: 'Benchmark Holdout Test Corpus',
        sample: 'N=522 (+50 Pilot)',
      },
    };
  }, [allRows]);

  // Count-up hooks for KPI stat tiles on mount (reuse useCountUp)
  const animatedBestF1 = useCountUp(topStats.bestF1Num, {
    start: !isLoading,
    duration: 800,
    decimals: 4,
  });
  const animatedLowestFpr = useCountUp(topStats.lowestFprNum, {
    start: !isLoading,
    duration: 800,
    decimals: 2,
  });
  const animatedFastestLat = useCountUp(topStats.fastestLatNum, {
    start: !isLoading,
    duration: 800,
    decimals: 2,
  });
  const animatedTotalEmails = useCountUp(topStats.totalEmailsNum, {
    start: !isLoading,
    duration: 800,
    decimals: 0,
  });

  // Sorted McNemar tests
  const sortedMcNemar = useMemo(() => {
    if (!mcnemar?.tests) return [];
    return Object.entries(mcnemar.tests).sort(
      (a, b) => (a[1].holm_bonferroni_rank || 99) - (b[1].holm_bonferroni_rank || 99)
    );
  }, [mcnemar]);

  return (
    <motion.div
      variants={fadeInUp}
      initial="hidden"
      animate="visible"
      exit="exit"
      className="space-y-16 pb-16 max-w-7xl mx-auto"
    >
      {/* Unmissable Fallback Warning Banner */}
      {isUsingFallback && (
        <OfflineFallbackBanner
          onRetry={() => window.location.reload()}
        />
      )}

      {/* Page Header */}
      <div>
        <div className="flex items-center gap-2 text-teal-400 text-xs font-semibold uppercase tracking-wider">
          <BarChart3 className="h-4 w-4" />
          Empirical Benchmark Diagnostics
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight mt-1 font-['Plus_Jakarta_Sans',sans-serif]">
          Benchmark Performance Dashboard
        </h1>
        <p className="text-slate-400 text-sm mt-1 max-w-3xl leading-relaxed">
          Comprehensive empirical results evaluating M1–M4 across Clean, Marked, and Unmarked prompt injections. Features interactive filtering, comparative performance charts, high-confidence mistake logs, and McNemar hypothesis tests.
        </p>
      </div>

      {/* =========================================================================
          SECTION 1: TOP 4 STAT TILES (Count up on mount with explicit sample tags)
          ========================================================================= */}
      <div className="relative">
        <AnimatePresence mode="popLayout" initial={false}>
          {isLoading ? (
            <motion.div
              key="stats-skeleton"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.25, ease: 'easeInOut' }}
              className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 w-full"
            >
              {Array.from({ length: 4 }).map((_, i) => (
                <SkeletonStatTile key={i} />
              ))}
            </motion.div>
          ) : (
            <motion.div
              key="stats-content"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.35, ease: 'easeOut' }}
              className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 w-full"
            >
              <StatTile
                label="Best F1 Score"
                value={animatedBestF1.toFixed(4)}
                subtext={`${topStats.bestF1.sub} • [${topStats.bestF1.sample}]`}
                variant="legitimate"
                icon={<Target className="h-5 w-5" />}
              />

              <StatTile
                label="Lowest False Alarm (FPR)"
                value={`${animatedLowestFpr.toFixed(2)}%`}
                subtext={`${topStats.lowestFpr.sub} • [${topStats.lowestFpr.sample}]`}
                variant="accent"
                icon={<ShieldAlert className="h-5 w-5" />}
              />

              <StatTile
                label="Fastest Inference"
                value={`${animatedFastestLat.toFixed(2)} ms`}
                subtext={`${topStats.fastestLatency.sub} • [${topStats.fastestLatency.sample}]`}
                variant="default"
                icon={<Zap className="h-5 w-5" />}
              />

              <StatTile
                label="Benchmark Test Emails"
                value={Math.round(animatedTotalEmails).toLocaleString()}
                unit="emails"
                subtext={`[${topStats.totalEmails.sample}]`}
                variant="default"
                icon={<Database className="h-5 w-5" />}
              />
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* =========================================================================
          SECTION 2: FILTERS ROW (Reactive Filtering)
          ========================================================================= */}
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
              onClick={handleResetFilters}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium text-slate-400 hover:text-white bg-slate-800 hover:bg-slate-700 hover:scale-[1.02] hover:brightness-105 active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 transition-all duration-150 self-end md:self-center"
            >
              <RotateCcw className="h-3.5 w-3.5" />
              <span>Reset</span>
            </button>
          )}
        </div>
      </Card>

      {/* =========================================================================
          SECTIONS 3 & 4: DATA-DEPENDENT TABLE & CHARTS (Cross-fades on filter change)
          ========================================================================= */}
      <AnimatePresence mode="wait" initial={false}>
        <motion.div
          key={filterKey}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.2, ease: 'easeInOut' }}
          className="space-y-10"
        >
          {/* SECTION 3: METRICS TABLE (Sortable) */}
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
                      onClick={() => handleSort('method')}
                      onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); handleSort('method'); } }}
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
                      onClick={() => handleSort('model')}
                      onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); handleSort('model'); } }}
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
                      onClick={() => handleSort('condition')}
                      onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); handleSort('condition'); } }}
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
                      onClick={() => handleSort('accuracy')}
                      onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); handleSort('accuracy'); } }}
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
                      onClick={() => handleSort('recall')}
                      onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); handleSort('recall'); } }}
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
                      onClick={() => handleSort('fpr')}
                      onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); handleSort('fpr'); } }}
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
                      onClick={() => handleSort('precision')}
                      onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); handleSort('precision'); } }}
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
                      onClick={() => handleSort('f1')}
                      onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); handleSort('f1'); } }}
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
                      onClick={() => handleSort('latencySeconds')}
                      onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); handleSort('latencySeconds'); } }}
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

          {/* SECTION 4: TWO RECHARTS BAR CHARTS (Horizontally scroll below 640px) */}
          <div className="relative">
            <AnimatePresence mode="popLayout" initial={false}>
              {isLoading ? (
                <motion.div
                  key="charts-skeleton"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.25, ease: 'easeInOut' }}
                  className="grid grid-cols-1 lg:grid-cols-2 gap-6 w-full"
                >
                <SkeletonChart
                  title="Recall (Catch Rate) vs. FPR (False Alarms)"
                  subtitle="Evaluating evasion resistance across configurations"
                />
                <SkeletonChart
                  title="Operational Latency per Method & Condition"
                  subtitle="Mean per-email inference latency in milliseconds"
                />
              </motion.div>
            ) : (
              <motion.div
                key="charts-content"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.35, ease: 'easeOut' }}
                className="grid grid-cols-1 lg:grid-cols-2 gap-6 w-full"
              >
              {/* Chart 1: Recall vs. FPR */}
              <Card variant="elevated" padding="md">
                <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                  <div>
                    <h3 className="text-base font-bold text-white tracking-tight">
                      Recall (Phishing Catch) vs. FPR (False Alarms)
                    </h3>
                    <p className="text-xs text-slate-400">
                      Evaluating evasion resistance vs false-alarm tax across filtered configurations [N=522 &amp; Pilot N=50].
                    </p>
                  </div>
                </div>

                <div className="overflow-x-auto pt-4 pb-2">
                  <div className="min-w-[560px] h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart
                        data={chartData}
                        margin={{ top: 10, right: 10, left: -10, bottom: 35 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" stroke={chartColors.grid} vertical={false} />
                        <XAxis
                          dataKey="name"
                          stroke={chartColors.axis}
                          tick={{ fill: chartColors.text, fontSize: 10 }}
                          angle={-25}
                          textAnchor="end"
                          interval={0}
                        />
                        <YAxis
                          stroke={chartColors.axis}
                          tick={{ fill: chartColors.text, fontSize: 10 }}
                          unit="%"
                          domain={[0, 100]}
                        />
                        <Tooltip content={<CustomChartTooltip />} />
                        <Legend
                          verticalAlign="top"
                          align="right"
                          wrapperStyle={{ paddingBottom: 10, fontSize: 11, color: chartColors.legendText }}
                        />
                        <Bar
                          dataKey="recallPct"
                          name="Recall (Catch Rate %)"
                          fill="#14b8a6"
                          radius={[4, 4, 0, 0]}
                          isAnimationActive={true}
                          animationDuration={800}
                          animationEasing="ease-out"
                        />
                        <Bar
                          dataKey="fprPct"
                          name="FPR (False Alarm %)"
                          fill="#f43f5e"
                          radius={[4, 4, 0, 0]}
                          isAnimationActive={true}
                          animationDuration={800}
                          animationEasing="ease-out"
                        />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </Card>

              {/* Chart 2: Operational Latency */}
              <Card variant="elevated" padding="md">
                <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                  <div>
                    <h3 className="text-base font-bold text-white tracking-tight">
                      Operational Latency per Method &amp; Condition
                    </h3>
                    <p className="text-xs text-slate-400">
                      Mean per-email inference latency in milliseconds [Labeled N=522 / N=50].
                    </p>
                  </div>
                </div>

                <div className="overflow-x-auto pt-4 pb-2">
                  <div className="min-w-[560px] h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart
                        data={chartData}
                        margin={{ top: 10, right: 10, left: -5, bottom: 35 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" stroke={chartColors.grid} vertical={false} />
                        <XAxis
                          dataKey="name"
                          stroke={chartColors.axis}
                          tick={{ fill: chartColors.text, fontSize: 10 }}
                          angle={-25}
                          textAnchor="end"
                          interval={0}
                        />
                        <YAxis
                          stroke={chartColors.axis}
                          tick={{ fill: chartColors.text, fontSize: 10 }}
                          unit="ms"
                        />
                        <Tooltip content={<CustomChartTooltip isLatency />} />
                        <Legend
                          verticalAlign="top"
                          align="right"
                          wrapperStyle={{ paddingBottom: 10, fontSize: 11, color: chartColors.legendText }}
                        />
                        <Bar
                          dataKey="latencyMs"
                          name="Mean Latency (ms)"
                          fill="#0ea5e9"
                          radius={[4, 4, 0, 0]}
                          isAnimationActive={true}
                          animationDuration={800}
                          animationEasing="ease-out"
                        />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </Card>
            </motion.div>
          )}
        </AnimatePresence>
          </div>
        </motion.div>
      </AnimatePresence>

      {/* =========================================================================
          SECTION 5: COLLAPSIBLE WORST MISTAKES (Animated Height+Opacity & Inline Row)
          ========================================================================= */}
      <Card variant="default" padding="none">
        <div
          role="button"
          tabIndex={0}
          onClick={() => setShowMistakes(!showMistakes)}
          onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); setShowMistakes(!showMistakes); } }}
          className="p-5 flex items-center justify-between cursor-pointer hover:bg-slate-850/60 hover:scale-[1.005] hover:brightness-105 active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-inset transition-all duration-150 select-none"
        >
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-rose-500/10 text-rose-400 border border-rose-500/20">
              <AlertCircle className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white tracking-tight">
                Worst High-Confidence Misclassifications ({mistakes.length} cases)
              </h3>
              <p className="text-xs text-slate-400">
                Table only. Click any row to expand the full email text inline.
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
                        {mistakes.map((m, idx) => {
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
      </Card>
    </motion.div>
  );
};

// =========================================================================
// CUSTOM CHART TOOLTIP COMPONENT
// =========================================================================

interface CustomChartTooltipProps {
  active?: boolean;
  payload?: any[];
  label?: string;
  isLatency?: boolean;
}

const CustomChartTooltip: React.FC<CustomChartTooltipProps> = ({
  active,
  payload,
  label,
  isLatency = false,
}) => {
  if (active && payload && payload.length) {
    const dataItem = payload[0].payload;
    return (
      <div className="rounded-xl border border-slate-700/80 bg-slate-900/95 p-3.5 elevation-modal backdrop-blur-md text-xs space-y-1.5 min-w-[200px]">
        <div className="border-b border-slate-800 pb-1.5">
          <p className="font-bold text-white text-xs">{dataItem.fullName || label}</p>
          <p className="text-[10px] text-teal-400 font-mono">
            {dataItem.model} &bull; {dataItem.sampleSize}
          </p>
        </div>

        {payload.map((entry: any, index: number) => (
          <div key={index} className="flex items-center justify-between gap-4">
            <span style={{ color: entry.color }} className="font-medium text-[11px]">
              {entry.name}:
            </span>
            <span className="font-mono text-white font-bold">
              {entry.value !== undefined ? entry.value.toLocaleString() : ''}
              {isLatency ? ' ms' : '%'}
            </span>
          </div>
        ))}
      </div>
    );
  }
  return null;
};

export default DashboardPage;
