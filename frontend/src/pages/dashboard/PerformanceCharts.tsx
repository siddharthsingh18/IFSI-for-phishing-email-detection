import React from 'react';
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
import { motion, AnimatePresence } from 'framer-motion';
import type { ChartThemeColors } from '../../hooks/useTheme';

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
              {entry.value !== undefined ? entry.value.toLocaleString() : ""}
              {isLatency ? ' ms' : '%'}
            </span>
          </div>
        ))}
      </div>
    );
  }
  return null;
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
  chartColors: ChartThemeColors;
}

export const PerformanceCharts: React.FC<PerformanceChartsProps> = ({
  isLoading,
  chartData,
  chartColors,
}) => {
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
  );
};

export default PerformanceCharts;
