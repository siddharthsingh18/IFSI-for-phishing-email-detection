import React, { useRef } from 'react';
import { useInView, motion, AnimatePresence } from 'framer-motion';
import { Cpu, Bot, Layers, ShieldCheck, ArrowDownRight } from 'lucide-react';
import { useCountUp } from '../hooks/useCountUp';
import type { BenchmarkSummary } from '../api/client';

export interface HeroTestSetMetricProps {
  summary: BenchmarkSummary | null;
  loading?: boolean;
  variant?: 'white' | 'dark';
}

interface MethodBadge {
  id: string;
  name: string;
  title: string;
  icon: React.ComponentType<{ className?: string }>;
  isHero?: boolean;
}

const METHODS: MethodBadge[] = [
  {
    id: 'M1',
    name: 'LogReg',
    title: 'M1: TF-IDF + Logistic Regression (Classical Linear Baseline)',
    icon: Cpu,
  },
  {
    id: 'M2',
    name: 'Zero-Shot',
    title: 'M2: Direct Instruction Prompting (Zero-Shot LLM)',
    icon: Bot,
  },
  {
    id: 'M3',
    name: 'RAG',
    title: 'M3: Standard RAG Combined (FAISS + LLM)',
    icon: Layers,
  },
  {
    id: 'M4',
    name: 'IFSI',
    title: 'M4: Decoupled Staged Inference (Injection-First Defense)',
    icon: ShieldCheck,
    isHero: true,
  },
];

export const HeroTestSetMetric: React.FC<HeroTestSetMetricProps> = ({
  summary,
  loading = false,
  variant = 'white',
}) => {
  // Pull live test set size from GET /results/summary (summary.dataset.test_size)
  const testSize = summary?.dataset?.test_size ?? 522;

  // Animate number count-up on scroll into view
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once: true, amount: 0.2 });
  const count = useCountUp(testSize, {
    start: isInView && !loading,
    duration: 500,
  });

  const scrollToMethods = (e: React.MouseEvent) => {
    e.preventDefault();
    document.getElementById('methods-section')?.scrollIntoView({ behavior: 'smooth' });
  };

  if (variant === 'dark') {
    return (
      <div ref={ref} className="rounded-2xl bg-slate-900/85 backdrop-blur-md border border-slate-800/80 border-t-slate-700/70 elevation-modal p-3.5 sm:p-5 w-full max-w-[320px] sm:w-[285px] transition-all duration-150 hover:border-slate-700/80 hover:elevation-hover select-none">
        <div className="space-y-3">
          <div>
            <div className="relative text-3xl sm:text-4xl font-black text-white tracking-tight font-['Plus_Jakarta_Sans',sans-serif] min-h-[2.25rem] flex items-center">
              <AnimatePresence mode="popLayout" initial={false}>
                {loading ? (
                  <motion.span
                    key="count-skeleton"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.22, ease: 'easeInOut' }}
                  >
                    --
                  </motion.span>
                ) : (
                  <motion.span
                    key="count-content"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.32, ease: 'easeOut' }}
                  >
                    {count.toLocaleString()}
                  </motion.span>
                )}
              </AnimatePresence>
            </div>
            <p className="text-[11px] sm:text-xs font-semibold text-slate-400 uppercase tracking-wider mt-0.5">
              Test Emails Evaluated
            </p>
          </div>

          <div className="pt-2.5 border-t border-slate-800/80 flex items-center justify-between gap-1.5">
            <div className="flex items-center gap-1.5">
              {METHODS.map((m) => (
                <div
                  key={m.id}
                  title={m.title}
                  className={`inline-flex items-center gap-1 px-2 py-1 rounded-md text-xs font-bold transition-colors select-none ${
                    m.isHero
                      ? 'bg-teal-950/80 text-teal-300 border border-teal-500/50 ring-1 ring-teal-500/30'
                      : 'bg-slate-800/80 text-slate-300 border border-slate-700/60'
                  }`}
                >
                  <m.icon className={`h-3 w-3 ${m.isHero ? 'text-teal-400' : 'text-slate-400'}`} />
                  <span>{m.id}</span>
                </div>
              ))}
            </div>

            <a
              href="#methods-section"
              onClick={scrollToMethods}
              title="Explore all 4 methods in detail"
              aria-label="Scroll to methods section"
              className="inline-flex items-center justify-center h-7 w-7 rounded-lg bg-teal-500/10 hover:bg-teal-500/20 text-teal-400 hover:text-teal-300 border border-teal-500/30 hover:border-teal-400 hover:scale-[1.05] hover:brightness-110 active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 transition-all group flex-shrink-0 cursor-pointer"
            >
              <ArrowDownRight className="h-3.5 w-3.5 group-hover:translate-x-0.5 group-hover:translate-y-0.5 transition-transform" />
            </a>
          </div>
        </div>
      </div>
    );
  }

  // Default: White card with drop shadow (harmonizing with the other two floating hero cards)
  return (
    <div ref={ref} className="rounded-2xl bg-white text-slate-900 border border-slate-100 elevation-modal p-3.5 sm:p-5 w-full max-w-[320px] sm:w-[285px] transition-all duration-150 hover:elevation-hover select-none">
      <div className="space-y-3">
        <div>
          <div className="relative text-3xl sm:text-4xl font-extrabold text-slate-950 tracking-tight font-['Plus_Jakarta_Sans',sans-serif] min-h-[2.25rem] flex items-center">
            <AnimatePresence mode="popLayout" initial={false}>
              {loading ? (
                <motion.span
                  key="count-skeleton-light"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.22, ease: 'easeInOut' }}
                >
                  --
                </motion.span>
              ) : (
                <motion.span
                  key="count-content-light"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.32, ease: 'easeOut' }}
                >
                  {count.toLocaleString()}
                </motion.span>
              )}
            </AnimatePresence>
          </div>
          <p className="text-xs sm:text-[13px] font-semibold text-slate-500 tracking-tight mt-0.5">
            Test Emails Evaluated
          </p>
        </div>

        <div className="pt-2.5 border-t border-slate-100 flex items-center justify-between gap-1.5">
          <div className="flex items-center gap-1.5">
            {METHODS.map((m) => (
              <div
                key={m.id}
                title={m.title}
                className={`inline-flex items-center gap-1 px-2 py-1 rounded-md text-xs font-bold transition-colors select-none ${
                  m.isHero
                    ? 'bg-teal-50 text-teal-800 border border-teal-200 ring-1 ring-teal-500/20'
                    : 'bg-slate-100 text-slate-700 border border-slate-200'
                }`}
              >
                <m.icon className={`h-3 w-3 ${m.isHero ? 'text-teal-600' : 'text-slate-500'}`} />
                <span>{m.id}</span>
              </div>
            ))}
          </div>

          <a
            href="#methods-section"
            onClick={scrollToMethods}
            title="Explore all 4 methods in detail"
            aria-label="Scroll to methods section"
            className="inline-flex items-center justify-center h-7 w-7 rounded-lg bg-teal-50 hover:bg-teal-100 text-teal-700 border border-teal-200 hover:scale-[1.05] hover:brightness-105 active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-600 focus-visible:ring-offset-2 transition-all group flex-shrink-0 cursor-pointer"
          >
            <ArrowDownRight className="h-3.5 w-3.5 group-hover:translate-x-0.5 group-hover:translate-y-0.5 transition-transform" />
          </a>
        </div>
      </div>
    </div>
  );
};

export default HeroTestSetMetric;
