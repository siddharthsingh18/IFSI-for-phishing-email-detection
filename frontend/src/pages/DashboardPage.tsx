import React, { useEffect, useState, useMemo, useRef } from 'react';
import { BarChart3 } from 'lucide-react';
import {
  apiClient,
  type BenchmarkSummary,
  type McNemarResponse,
  type MistakeRecord,
  type McNemarTestResult,
} from '../api/client';
import { OfflineFallbackBanner } from '../components/OfflineFallbackBanner';
import { motion, useInView } from 'framer-motion';
import { fadeInUp } from '../lib/motion';
import { useCountUp } from '../hooks/useCountUp';
import { useTheme } from '../hooks/useTheme';

import {
  METHOD_LABELS,
  PILOT_ROWS,
  type MetricTableRow,
  type SortField,
  type GroupedBarPair,
  buildGroupedChartData,
} from './dashboard/types';
import { DashboardKpiTiles } from './dashboard/DashboardKpiTiles';
import { DashboardFilters } from './dashboard/DashboardFilters';
import { ConfusionMatrixHeatmap } from './dashboard/ConfusionMatrixHeatmap';
import { MetricsTable } from './dashboard/MetricsTable';
import { PerformanceCharts } from './dashboard/PerformanceCharts';
import {
  WorstMistakesCard,
  HypothesisTestsCard,
} from './dashboard/MistakesAndHypothesisTests';

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
        specificity: met.specificity ?? (1 - met.fpr),
        f1: met.f1,
        invalidRate: Number((met as any).invalid_schema_rate || 0),
        latencySeconds: latSec,
        latencyDisplay: latStr,
        tp: met.true_positives ?? 0,
        fp: met.false_positives ?? 0,
        tn: met.true_negatives ?? 0,
        fn: met.false_negatives ?? 0,
      });
    });

    return [...rows, ...PILOT_ROWS];
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

  // Recharts Data Transformation (Operational Latency)
  const chartData = useMemo(() => {
    return sortedRows.map((r) => {
      const isPilot = r.sampleSize.includes('Pilot');
      return {
        id: r.id,
        name: isPilot ? `${r.methodCode} (${r.condition}) [Pilot]` : `${r.methodCode} (${r.condition})`,
        fullName: `${r.method} - ${r.condition}`,
        model: r.model,
        sampleSize: r.sampleSize,
        recallPct: Number((r.recall * 100).toFixed(1)),
        fprPct: Number((r.fpr * 100).toFixed(1)),
        accuracyPct: Number((r.accuracy * 100).toFixed(1)),
        latencyMs: Number((r.latencySeconds * 1000).toFixed(1)),
        isPilot,
      };
    });
  }, [sortedRows]);

  // Grouped Bar Chart Data (Recall vs FPR grouped by method M1-M4 with 3 bar-pairs Clean/Marked/Unmarked)
  const groupedChartData: GroupedBarPair[] = useMemo(() => {
    return buildGroupedChartData(allRows, filterMethod, filterCondition, filterModel);
  }, [allRows, filterMethod, filterCondition, filterModel]);

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

    const bestF1Row = [...allRows].sort((a, b) => b.f1 - a.f1)[0];
    const lowestFprRow = [...allRows].sort((a, b) => a.fpr - b.fpr)[0];
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

  // Reference and scroll-in-view detection for KPI stat tiles
  const kpiRef = useRef<HTMLDivElement>(null);
  const isKpiInView = useInView(kpiRef, { once: true, amount: 0.1 });
  const startCountUp = !isLoading && isKpiInView;

  // Count-up hooks for KPI stat tiles on scroll into view
  const animatedBestF1 = useCountUp(topStats.bestF1Num, {
    start: startCountUp,
    duration: 800,
    decimals: 4,
  });
  const animatedLowestFpr = useCountUp(topStats.lowestFprNum, {
    start: startCountUp,
    duration: 800,
    decimals: 2,
  });
  const animatedFastestLat = useCountUp(topStats.fastestLatNum, {
    start: startCountUp,
    duration: 800,
    decimals: 2,
  });
  const animatedTotalEmails = useCountUp(topStats.totalEmailsNum, {
    start: startCountUp,
    duration: 800,
    decimals: 0,
  });

  // Sorted McNemar tests
  const sortedMcNemar = useMemo(() => {
    if (!mcnemar?.tests) return [];
    return (Object.entries(mcnemar.tests) as Array<[string, McNemarTestResult]>).sort(
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

      {/* SECTION 1: TOP 4 STAT TILES (Staggered count-up on scroll into view) */}
      <motion.section
        variants={fadeInUp}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.15 }}
      >
        <DashboardKpiTiles
          ref={kpiRef}
          isLoading={isLoading}
          animatedBestF1={animatedBestF1}
          animatedLowestFpr={animatedLowestFpr}
          animatedFastestLat={animatedFastestLat}
          animatedTotalEmails={animatedTotalEmails}
          topStats={topStats}
        />
      </motion.section>

      {/* SECTION 2: FILTERS ROW */}
      <motion.section
        variants={fadeInUp}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.15 }}
      >
        <DashboardFilters
          filterMethod={filterMethod}
          setFilterMethod={setFilterMethod}
          filterCondition={filterCondition}
          setFilterCondition={setFilterCondition}
          filterModel={filterModel}
          setFilterModel={setFilterModel}
          onResetFilters={handleResetFilters}
        />
      </motion.section>

      {/* SECTION 3: METRICS TABLE */}
      <motion.section
        variants={fadeInUp}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.08, margin: "-20px" }}
      >
        <div key={`table-${filterKey}`} className="transition-opacity duration-200">
          <MetricsTable
            isLoading={isLoading}
            sortedRows={sortedRows}
            sortField={sortField}
            sortDirection={sortDirection}
            onSort={handleSort}
          />
        </div>
      </motion.section>

      {/* SECTION 4: PERFORMANCE CHARTS (With Visible On-Chart Latency Pilot Spike Callout) */}
      <motion.section
        variants={fadeInUp}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.08, margin: "-20px" }}
      >
        <div key={`charts-${filterKey}`} className="transition-opacity duration-200">
          <PerformanceCharts
            isLoading={isLoading}
            chartData={chartData}
            groupedChartData={groupedChartData}
            chartColors={chartColors}
            filterModel={filterModel}
          />
        </div>
      </motion.section>

      {/* SECTION 5: CONFUSION MATRIX HEATMAP */}
      <motion.section
        variants={fadeInUp}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.08, margin: "-20px" }}
      >
        <div key={`heatmap-${filterKey}`} className="transition-opacity duration-200">
          <ConfusionMatrixHeatmap
            isLoading={isLoading}
            filteredRows={filteredRows}
            filterMethod={filterMethod}
            setFilterMethod={setFilterMethod}
            filterCondition={filterCondition}
            setFilterCondition={setFilterCondition}
            filterModel={filterModel}
          />
        </div>
      </motion.section>

      {/* SECTION 6: COLLAPSIBLE WORST MISTAKES */}
      <motion.section
        variants={fadeInUp}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.08, margin: "-20px" }}
      >
        <WorstMistakesCard
          isLoading={isLoading}
          mistakes={mistakes}
          showMistakes={showMistakes}
          setShowMistakes={setShowMistakes}
          expandedMistakeId={expandedMistakeId}
          setExpandedMistakeId={setExpandedMistakeId}
        />
      </motion.section>

      {/* SECTION 7: SIGNIFICANCE STRIP & MCNEMAR HYPOTHESIS TESTS */}
      <motion.section
        variants={fadeInUp}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.08, margin: "-20px" }}
      >
        <HypothesisTestsCard
          isLoading={isLoading}
          showMcNemar={showMcNemar}
          setShowMcNemar={setShowMcNemar}
          sortedMcNemar={sortedMcNemar}
        />
      </motion.section>
    </motion.div>
  );
};

export default DashboardPage;
