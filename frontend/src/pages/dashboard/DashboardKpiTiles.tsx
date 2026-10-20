import React from 'react';
import { Target, ShieldAlert, Zap, Database } from 'lucide-react';
import { StatTile } from '../../components/StatTile';
import { SkeletonStatTile } from '../../components/Skeleton';
import { motion, AnimatePresence } from 'framer-motion';
import { fadeInUp, staggerContainer } from '../../lib/motion';

export interface DashboardKpiTilesProps {
  isLoading: boolean;
  animatedBestF1: number;
  animatedLowestFpr: number;
  animatedFastestLat: number;
  animatedTotalEmails: number;
  topStats: {
    bestF1: { value: string; sub: string; sample: string };
    lowestFpr: { value: string; sub: string; sample: string };
    fastestLatency: { value: string; sub: string; sample: string };
    totalEmails: { value: string; sub: string; sample: string };
  };
}

export const DashboardKpiTiles = React.forwardRef<HTMLDivElement, DashboardKpiTilesProps>(
  (
    {
      isLoading,
      animatedBestF1,
      animatedLowestFpr,
      animatedFastestLat,
      animatedTotalEmails,
      topStats,
    },
    ref
  ) => {
    return (
      <div ref={ref} className="relative">
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
            variants={staggerContainer}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.15 }}
            className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 w-full"
          >
            <motion.div variants={fadeInUp}>
              <StatTile
                label="Best F1 Score"
                value={animatedBestF1.toFixed(4)}
                subtext={`${topStats.bestF1.sub} • [${topStats.bestF1.sample}]`}
                variant="legitimate"
                icon={<Target className="h-5 w-5" />}
              />
            </motion.div>

            <motion.div variants={fadeInUp}>
              <StatTile
                label="Lowest False Alarm (FPR)"
                value={`${animatedLowestFpr.toFixed(2)}%`}
                subtext={`${topStats.lowestFpr.sub} • [${topStats.lowestFpr.sample}]`}
                variant="accent"
                icon={<ShieldAlert className="h-5 w-5" />}
              />
            </motion.div>

            <motion.div variants={fadeInUp}>
              <StatTile
                label="Fastest Inference"
                value={`${animatedFastestLat.toFixed(2)} ms`}
                subtext={`${topStats.fastestLatency.sub} • [${topStats.fastestLatency.sample}]`}
                variant="default"
                icon={<Zap className="h-5 w-5" />}
              />
            </motion.div>

            <motion.div variants={fadeInUp}>
              <StatTile
                label="Benchmark Test Emails"
                value={Math.round(animatedTotalEmails).toLocaleString()}
                unit="emails"
                subtext={`[${topStats.totalEmails.sample}]`}
                variant="default"
                icon={<Database className="h-5 w-5" />}
              />
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
});

DashboardKpiTiles.displayName = 'DashboardKpiTiles';

export default DashboardKpiTiles;
