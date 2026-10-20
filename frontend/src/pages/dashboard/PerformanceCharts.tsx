import React, { useRef, useMemo } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
  LabelList,
} from 'recharts';
import { Card } from '../../components/Card';
import { SkeletonChart } from '../../components/Skeleton';
import { motion, AnimatePresence, useInView } from 'framer-motion';
import { AlertTriangle } from 'lucide-react';
import { fadeInUp, staggerContainer } from '../../lib/motion';
import type { ChartThemeColors } from '../../hooks/useTheme';
import type { GroupedBarPair } from './types';

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
    const isGrouped = Boolean(dataItem.methodFullName && dataItem.condition);

    return (
      <div className="rounded-xl border border-slate-700/80 bg-slate-900/95 p-3.5 elevation-modal backdrop-blur-md text-xs space-y-2 min-w-[220px]">
        <div className="border-b border-slate-800 pb-1.5">
          <p className="font-bold text-white text-xs">
            {isGrouped ? dataItem.methodFullName : (dataItem.fullName || label)}
          </p>
          <div className="flex items-center justify-between text-[10px] text-teal-400 font-mono mt-0.5">
            <span>{isGrouped ? `Condition: ${dataItem.condition}` : dataItem.model}</span>
            <span>{dataItem.sampleSize}</span>
          </div>
        </div>

        <div className="space-y-1">
          {payload.map((entry: any, index: number) => (
            <div key={index} className="flex items-center justify-between gap-4">
              <span style={{ color: entry.color }} className="font-medium text-[11px] flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full" style={{ backgroundColor: entry.color }} />
                {entry.name}:
              </span>
              <span className="font-mono text-white font-bold">
                {entry.value !== undefined ? entry.value.toLocaleString() : ''}
                {isLatency ? ' ms' : '%'}
              </span>
            </div>
          ))}
        </div>

        {isLatency && (dataItem.latencyMs >= 1500 || dataItem.isPilot) && (
          <div className="pt-1.5 border-t border-amber-500/30 flex items-center gap-1.5 text-[10px] text-amber-400 font-medium">
            <span className="h-1.5 w-1.5 rounded-full bg-amber-400 animate-pulse" />
            <span>Pilot Cohort: Local llama3.2:3b Ollama inference spike</span>
          </div>
        )}

        {isGrouped && dataItem.recallPct !== undefined && dataItem.fprPct !== undefined && (
          <div className="pt-1.5 border-t border-slate-800/80 flex items-center justify-between text-[10px] font-mono">
            <span className="text-slate-400">Net Catch Margin:</span>
            <span
              className={
                dataItem.recallPct - dataItem.fprPct > 50
                  ? 'text-teal-400 font-bold'
                  : dataItem.recallPct - dataItem.fprPct < 0
                  ? 'text-rose-400 font-bold'
                  : 'text-amber-400 font-semibold'
              }
            >
              {(dataItem.recallPct - dataItem.fprPct).toFixed(1)}%
            </span>
          </div>
        )}
      </div>
    );
  }
  return null;
};

interface CustomGroupedTickProps {
  x?: number;
  y?: number;
  payload?: any;
  index?: number;
  data: GroupedBarPair[];
  chartColors: ChartThemeColors;
}

const CustomGroupedTick: React.FC<CustomGroupedTickProps> = ({
  x = 0,
  y = 0,
  index = 0,
  data,
  chartColors,
}) => {
  const item = data[index];
  if (!item) return null;

  const isM4 = item.methodCode === 'M4';

  return (
    <g className="select-none">
      {/* 1. Condition label directly below the bar pair (Clean / Marked / Unmarked) */}
      <text
        x={x}
        y={y + 14}
        textAnchor="middle"
        fill={chartColors.text}
        fontSize={9.5}
        fontWeight={500}
        fontFamily="ui-sans-serif, system-ui, sans-serif"
      >
        {item.condition}
      </text>

      {/* 2. Vertical Divider between Method Groups on Axis */}
      {item.isGroupStart && index > 0 && (
        <line
          x1={x - 24}
          y1={y + 6}
          x2={x - 24}
          y2={y + 54}
          stroke={chartColors.grid || '#334155'}
          strokeWidth={1}
          strokeDasharray="2 2"
          strokeOpacity={0.8}
        />
      )}

      {/* 3. Method Group Header (Rendered on the center condition of each group) */}
      {item.isGroupCenter && (
        <g>
          {/* Connecting bracket spanning conditions */}
          {item.groupLength >= 3 && (
            <path
              d={`M ${x - 28} ${y + 22} L ${x - 28} ${y + 25} L ${x + 28} ${y + 25} L ${x + 28} ${y + 22}`}
              fill="none"
              stroke={isM4 ? '#14b8a6' : '#475569'}
              strokeWidth={1.5}
              strokeOpacity={0.85}
            />
          )}

          {/* Method title */}
          <text
            x={x}
            y={y + 38}
            textAnchor="middle"
            fill={isM4 ? '#2dd4bf' : '#f8fafc'}
            fontSize={11}
            fontWeight={700}
            fontFamily="ui-sans-serif, system-ui, sans-serif"
            letterSpacing="0.01em"
          >
            {item.methodLabel}
          </text>

          {/* Model / Cohort subtitle */}
          <text
            x={x}
            y={y + 51}
            textAnchor="middle"
            fill={isM4 ? '#5eead4' : '#94a3b8'}
            fontSize={9}
            fontFamily="ui-monospace, monospace"
            fillOpacity={0.85}
          >
            {item.model.split(':')[0]} • {item.sampleSize}
          </text>
        </g>
      )}
    </g>
  );
};

export interface PerformanceChartsProps {
  isLoading: boolean;
  chartData: Array<{
    name: string;
    fullName: string;
    model: string;
    sampleSize: string;
    recallPct: number;
    fprPct: number;
    accuracyPct: number;
    latencyMs: number;
    id?: string;
    isPilot?: boolean;
  }>;
  groupedChartData: GroupedBarPair[];
  chartColors: ChartThemeColors;
  filterModel: string;
}

export const PerformanceCharts: React.FC<PerformanceChartsProps> = ({
  isLoading,
  chartData,
  groupedChartData,
  chartColors,
  filterModel,
}) => {
  const chartRef = useRef<HTMLDivElement>(null);
  const isChartInView = useInView(chartRef, { once: true, amount: 0.2 });

  // Dynamically find tallest bar in latency chart for visible on-chart annotation
  const tallestLatencyIndex = useMemo(() => {
    if (!chartData || chartData.length === 0) return -1;
    let maxIdx = 0;
    let maxVal = chartData[0].latencyMs;
    for (let i = 1; i < chartData.length; i++) {
      if (chartData[i].latencyMs > maxVal) {
        maxVal = chartData[i].latencyMs;
        maxIdx = i;
      }
    }
    // Only flag if it's the significant pilot spike (> 1500ms)
    return maxVal >= 1500 ? maxIdx : -1;
  }, [chartData]);

  const tallestLatencyItem = tallestLatencyIndex >= 0 ? chartData[tallestLatencyIndex] : null;

  // Custom on-chart SVG callout rendered directly above the tallest bar
  const renderLatencyCallout = (props: any) => {
    const { x, y, width, index, value } = props;
    if (index !== tallestLatencyIndex || !tallestLatencyItem) return null;
    if (typeof x !== 'number' || typeof y !== 'number') return null;

    const cx = x + (width || 0) / 2;
    const barTop = y;

    // Callout box dimensions
    const boxW = 208;
    const boxH = 48;

    // Center horizontally on bar, clamp within SVG boundary
    const minX = 8;
    const maxX = 540 - boxW;
    const boxX = Math.max(minX, Math.min(cx - boxW / 2, maxX));
    const boxY = Math.max(4, barTop - boxH - 12);

    return (
      <g className="select-none pointer-events-none" key="pilot-latency-callout">
        <defs>
          <filter id="spikeGlow" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="1" stdDeviation="3" floodColor="#f59e0b" floodOpacity="0.55" />
          </filter>
        </defs>

        {/* Dotted connector line from callout to bar top */}
        <line
          x1={cx}
          y1={boxY + boxH}
          x2={cx}
          y2={barTop - 4}
          stroke="#f59e0b"
          strokeWidth={1.5}
          strokeDasharray="2 2"
        />

        {/* Arrow pointer head directly touching top of bar */}
        <polygon
          points={`${cx - 4},${barTop - 5} ${cx + 4},${barTop - 5} ${cx},${barTop - 1}`}
          fill="#f59e0b"
        />

        {/* Pulsing beacon circle on the bar cap */}
        <circle
          cx={cx}
          cy={barTop}
          r={3.5}
          fill="#fbbf24"
          stroke="#78350f"
          strokeWidth={1.5}
        />

        {/* Callout box background */}
        <rect
          x={boxX}
          y={boxY}
          width={boxW}
          height={boxH}
          rx={8}
          fill="#090d16"
          stroke="#f59e0b"
          strokeWidth={1.5}
          filter="url(#spikeGlow)"
        />
        <rect
          x={boxX}
          y={boxY}
          width={boxW}
          height={boxH}
          rx={8}
          fill="rgba(245, 158, 11, 0.08)"
        />

        {/* Warning dot icon */}
        <circle cx={boxX + 13} cy={boxY + 15} r={4.5} fill="#f59e0b" />
        <text
          x={boxX + 13}
          y={boxY + 18}
          textAnchor="middle"
          fill="#000"
          fontSize={8}
          fontWeight="900"
        >
          !
        </text>

        {/* Line 1: Header title with exact latency */}
        <text
          x={boxX + 22}
          y={boxY + 17}
          fill="#fbbf24"
          fontSize={10.5}
          fontWeight="700"
          fontFamily="ui-sans-serif, system-ui, sans-serif"
        >
          Pilot Spike: ~2,800ms ({Number(value || tallestLatencyItem.latencyMs).toLocaleString()} ms)
        </text>

        {/* Line 2: Model and cohort explanation */}
        <text
          x={boxX + 11}
          y={boxY + 31}
          fill="#cbd5e1"
          fontSize={9}
          fontWeight="500"
          fontFamily="ui-sans-serif, system-ui, sans-serif"
        >
          llama3.2:3b local 3B model (Ollama)
        </text>

        {/* Line 3: Why it spikes */}
        <text
          x={boxX + 11}
          y={boxY + 41}
          fill="#38bdf8"
          fontSize={8.5}
          fontWeight="600"
          fontFamily="ui-sans-serif, system-ui, sans-serif"
        >
          2-call decoupled pipeline overhead
        </text>
      </g>
    );
  };

  return (
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
            variants={staggerContainer}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.1 }}
            className="grid grid-cols-1 lg:grid-cols-2 gap-6 w-full"
          >
            {/* Chart 1: Grouped Recall vs. FPR */}
            <motion.div variants={fadeInUp} className="h-full">
              <Card variant="elevated" padding="md" className="h-full flex flex-col justify-between">
                <div>
                  <div className="flex flex-wrap items-center justify-between pb-3 border-b border-slate-800 gap-3">
                    <div>
                      <h3 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
                        Recall (Phishing Catch) vs. FPR (False Alarms)
                        {filterModel === 'llama' ? (
                          <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-purple-500/15 text-purple-300 border border-purple-500/30 font-semibold">
                            Pilot Cohort N=50
                          </span>
                        ) : filterModel === 'qwen' ? (
                          <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-teal-500/15 text-teal-300 border border-teal-500/30 font-semibold">
                            qwen2.5:0.5b N=522
                          </span>
                        ) : filterModel === 'tfidf' ? (
                          <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-slate-300 border border-slate-700 font-semibold">
                            TF-IDF Baseline
                          </span>
                        ) : (
                          <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-slate-300 border border-slate-700/80">
                            Full Benchmark Split [N=522]
                          </span>
                        )}
                      </h3>
                      <p className="text-xs text-slate-400 mt-0.5">
                        Grouped by method (M1–M4), with Clean, Marked, and Unmarked bar-pairs side by side.
                      </p>
                    </div>
                  </div>

                  <div ref={chartRef} className="overflow-x-auto pt-4 pb-2">
                    <div className="w-full min-w-[560px] h-96">
                      {groupedChartData.length === 0 ? (
                        <div className="flex items-center justify-center h-full text-xs text-slate-500">
                          No benchmark configurations match the selected filters.
                        </div>
                      ) : (
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart
                            data={groupedChartData}
                            margin={{ top: 12, right: 16, left: -14, bottom: 58 }}
                            barGap={2}
                            barCategoryGap="16%"
                          >
                            <CartesianGrid strokeDasharray="3 3" stroke={chartColors.grid} vertical={false} />
                            <XAxis
                              dataKey="id"
                              stroke={chartColors.axis}
                              interval={0}
                              height={65}
                              tick={
                                <CustomGroupedTick
                                  data={groupedChartData}
                                  chartColors={chartColors}
                                />
                              }
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
                              wrapperStyle={{
                                paddingBottom: 14,
                                fontSize: 11,
                                color: chartColors.legendText,
                              }}
                              iconType="circle"
                              iconSize={7}
                            />
                            <Bar
                              dataKey="recallPct"
                              name="Recall (Catch %)"
                              fill="#14b8a6"
                              radius={[3, 3, 0, 0]}
                              isAnimationActive={isChartInView}
                              animationDuration={900}
                              animationEasing="ease-out"
                            />
                            <Bar
                              dataKey="fprPct"
                              name="FPR (False Alarm %)"
                              fill="#f43f5e"
                              radius={[3, 3, 0, 0]}
                              isAnimationActive={isChartInView}
                              animationDuration={900}
                              animationEasing="ease-out"
                            />
                          </BarChart>
                        </ResponsiveContainer>
                      )}
                    </div>
                  </div>
                </div>
              </Card>
            </motion.div>

            {/* Chart 2: Operational Latency */}
            <motion.div variants={fadeInUp} className="h-full">
              <Card variant="elevated" padding="md" className="h-full flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                    <div>
                      <h3 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
                        Operational Latency per Method &amp; Condition
                        {tallestLatencyItem && (
                          <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-amber-500/15 text-amber-300 border border-amber-500/30 font-semibold">
                            Peak ~2.8s
                          </span>
                        )}
                      </h3>
                      <p className="text-xs text-slate-400">
                        Mean per-email inference latency in milliseconds [Labeled N=522 / N=50].
                      </p>
                    </div>
                  </div>

                  <div className="overflow-x-auto pt-4 pb-2">
                    <div className="min-w-[560px] h-84">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart
                          data={chartData}
                          margin={{ top: 54, right: 16, left: -5, bottom: 42 }}
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
                            domain={[0, (dataMax: number) => Math.ceil(dataMax * 1.25)]}
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
                            radius={[4, 4, 0, 0]}
                            isAnimationActive={true}
                            animationDuration={800}
                            animationEasing="ease-out"
                          >
                            {chartData.map((_entry, index) => {
                              const isSpike = index === tallestLatencyIndex;
                              return (
                                <Cell
                                  key={`cell-lat-${index}`}
                                  fill={isSpike ? '#f59e0b' : '#0ea5e9'}
                                  stroke={isSpike ? '#fbbf24' : undefined}
                                  strokeWidth={isSpike ? 1.5 : 0}
                                />
                              );
                            })}
                            <LabelList
                              dataKey="latencyMs"
                              content={renderLatencyCallout}
                            />
                          </Bar>
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                </div>

                {/* Visible Explanatory Banner Directly Accompanying the Latency Chart */}
                {tallestLatencyItem && tallestLatencyItem.latencyMs >= 1500 && (
                  <div className="mt-3 p-3 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-start gap-2.5 text-xs text-slate-300">
                    <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                    <div className="leading-relaxed">
                      <span className="font-bold text-amber-300">Pilot Latency Spike (~2,800ms): </span>
                      The tallest bar ({tallestLatencyItem.fullName} at{' '}
                      <span className="font-mono font-bold text-amber-200">
                        {tallestLatencyItem.latencyMs.toLocaleString()} ms
                      </span>
                      ) represents the local <span className="font-semibold text-white">llama3.2:3b</span> model run via Ollama on the 50-email pilot cohort. Unlike the lightweight <span className="text-teal-300">qwen2.5:0.5b</span> (~400–870ms) or <span className="text-teal-300">TF-IDF</span> (0.28ms), running unquantized 3B inference with multi-call decoupled prompt decomposition incurs a 4–5× latency multiplier per email.
                    </div>
                  </div>
                )}
              </Card>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default PerformanceCharts;
