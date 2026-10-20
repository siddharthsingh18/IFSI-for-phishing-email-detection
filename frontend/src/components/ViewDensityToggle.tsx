import React from 'react';
import { ListTree, Zap } from 'lucide-react';
import { motion } from 'framer-motion';
import { usePrefersReducedMotion } from '../hooks/usePrefersReducedMotion';

export type ViewDensity = 'simple' | 'detailed';

interface ViewDensityToggleProps {
  value: ViewDensity;
  onChange: (value: ViewDensity) => void;
}

export const ViewDensityToggle: React.FC<ViewDensityToggleProps> = ({ value, onChange }) => {
  const shouldReduceMotion = usePrefersReducedMotion();

  return (
    <div
      role="tablist"
      aria-label="Result detail view density"
      className="inline-flex p-1 rounded-xl bg-slate-900 border border-slate-800/90 shadow-inner w-full sm:w-auto"
    >
      <button
        type="button"
        role="tab"
        id="view-toggle-simple"
        aria-selected={value === 'simple'}
        onClick={() => onChange('simple')}
        className={`relative flex-1 sm:flex-initial px-3.5 py-2 sm:py-1.5 min-h-[38px] sm:min-h-0 flex items-center justify-center text-xs font-semibold rounded-lg transition-colors duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 touch-manipulation ${
          value === 'simple' ? 'text-white' : 'text-slate-400 hover:text-slate-200'
        }`}
      >
        {value === 'simple' && (
          <motion.span
            layoutId="active-view-density-pill"
            className="absolute inset-0 rounded-lg bg-teal-500/20 border border-teal-500/40 shadow-sm"
            transition={shouldReduceMotion ? { duration: 0 } : { type: 'spring', stiffness: 500, damping: 35 }}
          />
        )}
        <span className="relative z-10 flex items-center gap-1.5">
          <Zap className="h-3.5 w-3.5 text-teal-400" />
          Simple
        </span>
      </button>

      <button
        type="button"
        role="tab"
        id="view-toggle-detailed"
        aria-selected={value === 'detailed'}
        onClick={() => onChange('detailed')}
        className={`relative flex-1 sm:flex-initial px-3.5 py-2 sm:py-1.5 min-h-[38px] sm:min-h-0 flex items-center justify-center text-xs font-semibold rounded-lg transition-colors duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 touch-manipulation ${
          value === 'detailed' ? 'text-white' : 'text-slate-400 hover:text-slate-200'
        }`}
      >
        {value === 'detailed' && (
          <motion.span
            layoutId="active-view-density-pill"
            className="absolute inset-0 rounded-lg bg-teal-500/20 border border-teal-500/40 shadow-sm"
            transition={shouldReduceMotion ? { duration: 0 } : { type: 'spring', stiffness: 500, damping: 35 }}
          />
        )}
        <span className="relative z-10 flex items-center gap-1.5">
          <ListTree className="h-3.5 w-3.5 text-teal-400" />
          Detailed
        </span>
      </button>
    </div>
  );
};

export default ViewDensityToggle;
