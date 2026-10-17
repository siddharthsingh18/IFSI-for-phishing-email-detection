import React from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, RefreshCw, WifiOff } from 'lucide-react';

export interface OfflineFallbackBannerProps {
  message?: string;
  details?: string;
  onRetry?: () => void;
  className?: string;
}

/**
 * High-visibility unmissable banner displayed when a page is showing fallback or cached data
 * because the FastAPI backend server is unreachable.
 */
export const OfflineFallbackBanner: React.FC<OfflineFallbackBannerProps> = ({
  message = 'Showing cached/offline data — backend unreachable',
  details = 'The local FastAPI backend (http://localhost:8000) could not be contacted. Displaying pre-computed snapshot data instead of live model inference.',
  onRetry,
  className = '',
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: -12, scale: 0.99 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.35, ease: 'easeOut' }}
      role="alert"
      aria-live="assertive"
      className={"relative overflow-hidden rounded-2xl border-2 border-amber-500/90 bg-gradient-to-r from-amber-950/95 via-orange-950/90 to-amber-950/95 p-4 sm:p-5 shadow-[0_0_35px_rgba(245,158,11,0.3)] backdrop-blur-md mb-8 ring-1 ring-amber-400/40 " + className}
    >
      {/* Top glowing animated warning stripe */}
      <div className="absolute top-0 left-0 right-0 h-1.5 bg-gradient-to-r from-amber-400 via-orange-400 to-amber-500 animate-pulse" />

      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-start sm:items-center gap-3.5">
          {/* Animated Pulsing Icon */}
          <div className="relative flex-shrink-0 mt-0.5 sm:mt-0">
            <span className="absolute -inset-1 rounded-xl bg-amber-500/40 blur-sm animate-pulse" />
            <div className="relative rounded-xl border border-amber-400/60 bg-amber-500/25 p-2.5 text-amber-300 shadow-inner">
              <AlertTriangle className="h-6 w-6 stroke-[2.2]" />
            </div>
          </div>

          <div className="space-y-1">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-md bg-amber-500/25 border border-amber-400/50 text-[11px] font-black tracking-wider uppercase text-amber-300">
                <WifiOff className="h-3 w-3" />
                Offline Snapshot
              </span>
              <h3 className="text-base sm:text-lg font-black tracking-tight text-white drop-shadow">
                {message}
              </h3>
            </div>
            {details && (
              <p className="text-xs sm:text-sm text-amber-200/90 font-medium leading-relaxed max-w-3xl">
                {details}
              </p>
            )}
          </div>
        </div>

        {/* Action Button */}
        {onRetry && (
          <button
            type="button"
            onClick={onRetry}
            className="flex-shrink-0 inline-flex items-center gap-2 px-4 py-2 rounded-xl border border-amber-400/50 bg-amber-500/25 text-xs font-bold text-amber-100 hover:bg-amber-500/40 hover:border-amber-300 hover:text-white active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-400 transition-all duration-150 cursor-pointer shadow-md"
          >
            <RefreshCw className="h-3.5 w-3.5 animate-spin-slow" />
            Retry Connection
          </button>
        )}
      </div>
    </motion.div>
  );
};

export default OfflineFallbackBanner;
