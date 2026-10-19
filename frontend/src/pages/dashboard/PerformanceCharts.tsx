import React, { useRef } from 'react';
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
import { Card } from '../../components/Card';
import { SkeletonChart } from '../../components/Skeleton';
import { motion, AnimatePresence, useInView } from 'framer-motion';
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
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.35, ease: 'easeOut' }}
            className="grid grid-cols-1 lg:grid-cols-2 gap-6 w-full"
          >
            {/* Chart 1: Grouped Recall vs. FPR */}
            <Card variant="elevated" padding="md">
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
  );
};

export default PerformanceCharts;
