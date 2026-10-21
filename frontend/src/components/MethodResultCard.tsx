import React, { useState } from 'react';
import {
  Clock,
  Database,
  ChevronDown,
  ChevronUp,
  Copy,
  Check,
  Cpu,
  MessageSquare,
  Layers,
  ShieldCheck,
  ShieldAlert,
  Info,
  AlertTriangle,
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { type ClassificationResult } from '../api/client';
import { Card, type CardVariant } from './Card';
import { Badge } from './Badge';
import { usePrefersReducedMotion } from '../hooks/usePrefersReducedMotion';

export interface MethodVisualMeta {
  code: 'M1' | 'M2' | 'M3' | 'M4';
  name: string;
  badgeLabel: string;
  icon: (props?: { className?: string }) => React.ReactNode;
  iconContainerClass: string;
  badgeClass: string;
  cardBorderClass: string;
  accentGlowClass: string;
  tagClass: string;
}

const METHOD_VISUAL_CONFIG: Record<string, MethodVisualMeta> = {
  M1: {
    code: 'M1',
    name: 'TF-IDF + Logistic Regression',
    badgeLabel: 'Classical ML',
    icon: (props) => <Cpu className={props?.className || 'h-4 w-4'} />,
    iconContainerClass: 'bg-slate-800/90 text-slate-300 border-slate-700/80 shadow-sm shadow-slate-950/60',
    badgeClass: 'bg-slate-800/80 text-slate-300 border-slate-700/70',
    cardBorderClass: 'border-slate-800/80 hover:border-slate-700',
    accentGlowClass: 'from-slate-700/15 via-slate-800/10 to-transparent',
    tagClass: 'text-slate-400',
  },
  M2: {
    code: 'M2',
    name: 'Zero-Shot LLM',
    badgeLabel: 'Zero-Shot',
    icon: (props) => <MessageSquare className={props?.className || 'h-4 w-4'} />,
    iconContainerClass: 'bg-sky-500/15 text-sky-400 border-sky-500/30 shadow-sm shadow-sky-500/10',
    badgeClass: 'bg-sky-500/10 text-sky-300 border-sky-500/25',
    cardBorderClass: 'border-slate-800/80 hover:border-sky-500/40',
    accentGlowClass: 'from-sky-500/10 via-sky-500/5 to-transparent',
    tagClass: 'text-sky-400/80',
  },
  M3: {
    code: 'M3',
    name: 'RAG Combined (Single-Call)',
    badgeLabel: 'Combined RAG',
    icon: (props) => <Layers className={props?.className || 'h-4 w-4'} />,
    iconContainerClass: 'bg-rose-500/15 text-rose-400 border-rose-500/30 shadow-sm shadow-rose-500/10',
    badgeClass: 'bg-rose-500/10 text-rose-300 border-rose-500/25',
    cardBorderClass: 'border-slate-800/80 hover:border-rose-500/40',
    accentGlowClass: 'from-rose-500/10 via-rose-500/5 to-transparent',
    tagClass: 'text-rose-400/80',
  },
  M4: {
    code: 'M4',
    name: 'RAG Decoupled (IFSI Two-Stage)',
    badgeLabel: 'IFSI Defense',
    icon: (props) => <ShieldCheck className={props?.className || 'h-4 w-4'} />,
    iconContainerClass: 'bg-teal-500/15 text-teal-400 border-teal-500/30 shadow-sm shadow-teal-500/10 ring-1 ring-teal-500/20',
    badgeClass: 'bg-teal-500/10 text-teal-300 border-teal-500/25',
    cardBorderClass: 'border-teal-500/30 ring-1 ring-teal-500/20 hover:border-teal-400/50',
    accentGlowClass: 'from-teal-500/15 via-teal-500/5 to-transparent',
    tagClass: 'text-teal-400/80',
  },
};

const getMethodMeta = (methodStr: string): MethodVisualMeta => {
  const code = (methodStr.match(/\bM[1-4]\b/i)?.[0] || 'M1').toUpperCase();
  return METHOD_VISUAL_CONFIG[code] || METHOD_VISUAL_CONFIG.M1;
};

export interface MethodResultCardProps {
  result: ClassificationResult;
  consensusNote?: string;
  consensusStatusLabel?: string;
  isDissenting?: boolean;
  isOpenDetails?: boolean;
  onToggleDetails?: () => void;
  onCopySnippet?: (key: string, text: string) => void;
  copiedKey?: string | null;
  cardVariant?: CardVariant;
  headerTag?: string;
  emailSnippet?: string;
  emailLabel?: string;
  viewDensity?: 'simple' | 'detailed';
  verdictEffect?: 'evasion' | 'false_positive';
}

export const MethodResultCard: React.FC<MethodResultCardProps> = ({
  result,
  consensusNote,
  consensusStatusLabel,
  isDissenting = false,
  isOpenDetails: controlledIsOpen,
  onToggleDetails: controlledOnToggle,
  onCopySnippet,
  copiedKey,
  cardVariant,
  headerTag,
  emailSnippet,
  emailLabel,
  viewDensity = 'simple',
  verdictEffect,
}) => {
  // Support both controlled and uncontrolled open states
  const [internalIsOpen, setInternalIsOpen] = useState(false);
  const isOpen = controlledIsOpen !== undefined ? controlledIsOpen : internalIsOpen;
  const toggleDetails = controlledOnToggle || (() => setInternalIsOpen(!internalIsOpen));

  const [internalCopied, setInternalCopied] = useState<string | null>(null);
  const handleCopy = (key: string, text: string) => {
    if (onCopySnippet) {
      onCopySnippet(key, text);
    } else {
      navigator.clipboard.writeText(text);
      setInternalCopied(key);
      setTimeout(() => setInternalCopied(null), 2000);
    }
  };
  const isCopied = copiedKey ? copiedKey === result.method : internalCopied === result.method;

  const isPhishing = result.is_phishing;
  const isDecoupledM4 = result.method.includes('M4');
  const confidencePercent = (result.confidence * 100).toFixed(1);
  const isSimple = viewDensity === 'simple';
  const shortMethodMatch = result.method.match(/\bM[1-4]\b/i);
  const shortMethodName = shortMethodMatch ? shortMethodMatch[0].toUpperCase() : result.method.split(/[:(]/)[0].trim();
  const methodMeta = getMethodMeta(result.method);
  const shouldReduceMotion = usePrefersReducedMotion();

  const chosenVariant = cardVariant || (isDecoupledM4 ? 'accent' : 'default');

  return (
    <Card
      variant={chosenVariant}
      padding="none"
      tilt={true}
      className={`flex flex-col justify-between overflow-hidden transition-all duration-200 ${
        methodMeta.cardBorderClass
      } ${
        isDissenting
          ? 'ring-2 ring-amber-500/50 border-amber-500/50 shadow-xl shadow-amber-500/10'
          : ''
      }`}
    >
      <motion.div layout transition={{ duration: 0.28, ease: [0.16, 1, 0.3, 1] }}>
        <AnimatePresence mode="wait" initial={false}>
          {isSimple ? (
            /* =========================================================
               SIMPLE VIEW: High-density, readable in under 3 seconds
               - Distinct M1-M4 icon badge with method role pill
               - Verdict badge (large, prominent)
               - One-line confidence bar
               - Injection-detected status icon only (nothing else)
               ========================================================= */
            <motion.div
              key="simple-view"
              initial={{ opacity: 0, y: 4 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -4 }}
              transition={{ duration: 0.18, ease: 'easeOut' }}
              className="p-5 space-y-4"
            >
              {/* Header: Distinct Method Icon Badge + Method Name + Role Pill + Status */}
              <div className="flex items-center justify-between pb-3 border-b border-slate-800/80 gap-2">
                <div className="flex items-center gap-2.5 min-w-0">
                  <div
                    className={`p-1.5 rounded-lg border flex items-center justify-center shrink-0 shadow-sm ${methodMeta.iconContainerClass}`}
                    title={`${methodMeta.code}: ${methodMeta.name} (${methodMeta.badgeLabel})`}
                  >
                    {methodMeta.icon({ className: 'h-4 w-4' })}
                  </div>
                  <div className="flex items-center gap-1.5 flex-wrap min-w-0">
                    <span className="text-sm font-bold text-white tracking-tight truncate">
                      {shortMethodName}
                    </span>
                    <span
                      className={`text-[10px] font-semibold px-1.5 py-0.5 rounded-md border tracking-tight ${methodMeta.badgeClass}`}
                    >
                      {methodMeta.badgeLabel}
                    </span>
                    {isDissenting && (
                      <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded-md bg-amber-500/20 text-amber-300 border border-amber-500/40 inline-flex items-center gap-1 shadow-sm ${shouldReduceMotion ? '' : 'animate-pulse'}`}>
                        <AlertTriangle className="h-2.5 w-2.5 text-amber-400" />
                        Dissenting
                      </span>
                    )}
                  </div>
                </div>

                {/* Injection-detected status icon only */}
                <div className="flex items-center shrink-0">
                  {result.has_prompt_injection ? (
                    <div
                      title="Prompt Injection DETECTED"
                      className="p-1 rounded-lg bg-amber-500/20 text-amber-400 border border-amber-500/50 shadow-sm shadow-amber-500/20"
                    >
                      <ShieldAlert className={`h-4 w-4 ${shouldReduceMotion ? '' : 'animate-pulse'}`} />
                    </div>
                  ) : result.method.startsWith('M1') ? (
                    <span
                      title="Prompt Injection: N/A (Linear Classifier)"
                      className="text-slate-600 text-xs font-mono px-1 select-none"
                    >
                      —
                    </span>
                  ) : (
                    <div
                      title="Prompt Injection: Clean / None Detected"
                      className="p-1 rounded-lg text-slate-500"
                    >
                      <ShieldCheck className="h-4 w-4" />
                    </div>
                  )}
                </div>
              </div>

              {/* Large, Prominent Verdict Badge with scale-in pop (1.0 -> 1.08 -> 1.0) */}
              <div className="py-2.5 flex items-center justify-center">
                <motion.div
                  initial={shouldReduceMotion ? { scale: 1, opacity: 1 } : { scale: 1.0, opacity: 0 }}
                  animate={
                    verdictEffect === 'evasion'
                      ? { x: [0, -4, 4, -3, 3, 0], opacity: 1 }
                      : verdictEffect === 'false_positive'
                      ? { scale: [1, 1.06, 1], opacity: 1 }
                      : shouldReduceMotion
                      ? { scale: 1, opacity: 1 }
                      : { scale: [1.0, 1.08, 1.0], opacity: 1 }
                  }
                  transition={
                    verdictEffect
                      ? { duration: shouldReduceMotion ? 0 : 0.45, ease: 'easeInOut' }
                      : shouldReduceMotion
                      ? { duration: 0 }
                      : {
                          scale: { duration: 0.42, times: [0, 0.5, 1], ease: [0.16, 1, 0.3, 1], delay: 0.1 },
                          opacity: { duration: 0.2, ease: 'easeOut' },
                        }
                  }
                  className={`w-full flex items-center justify-center ${
                    verdictEffect === 'evasion'
                      ? 'rounded-lg ring-2 ring-rose-400/70 shadow-[0_0_18px_rgba(244,63,94,0.55)]'
                      : verdictEffect === 'false_positive'
                      ? 'rounded-lg ring-2 ring-amber-400/70 shadow-[0_0_18px_rgba(245,158,11,0.45)]'
                      : ''
                  }`}
                >
                  <Badge
                    variant={!result.is_valid ? 'neutral' : isPhishing ? 'phishing' : 'legitimate'}
                    size="lg"
                    dot
                    className="w-full justify-center py-2.5 text-sm font-extrabold tracking-wider shadow-lg"
                  >
                    {!result.is_valid ? 'FALLBACK' : isPhishing ? 'PHISHING' : 'LEGITIMATE'}
                  </Badge>
                </motion.div>
              </div>

              {/* One-Line Confidence Bar (no numbers, clean visual bar) */}
              <div className="pt-1">
                <div
                  title={`Confidence: ${confidencePercent}%`}
                  className="h-2 w-full bg-slate-950 rounded-full overflow-hidden border border-slate-800"
                >
                  <motion.div
                    initial={{ width: '0%' }}
                    animate={{
                      width: `${Math.max(
                        result.is_valid ? 5 : 0,
                        Math.min(100, Number(confidencePercent))
                      )}%`,
                    }}
                    transition={shouldReduceMotion ? { duration: 0 } : { duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
                    className={`h-full rounded-full ${
                      !result.is_valid
                        ? 'bg-amber-500/40'
                        : isPhishing
                        ? 'bg-gradient-to-r from-rose-500 to-red-400'
                        : 'bg-gradient-to-r from-teal-500 to-emerald-400'
                    }`}
                  />
                </div>
              </div>
            </motion.div>
          ) : (
            /* =========================================================
               DETAILED VIEW: Full diagnostician inspection
               - Latency, full reasoning trace, retrieved exemplars
               - Two-call breakdown (M4), raw confidence alongside bar
               - Details & Reasoning accordion drawer preserved
               ========================================================= */
            <motion.div
              key="detailed-view"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.18, ease: 'easeOut' }}
            >
              <div className="p-5 space-y-4">
                {/* Method Title Header with Distinct Icon Badge, Type Badge, Latency Badge and Subtitle */}
                <div className="flex items-center justify-between pb-3 border-b border-slate-800/80 gap-3">
                  <div className="flex items-center gap-2.5 min-w-0">
                    <div
                      className={`p-1.5 rounded-lg border flex items-center justify-center shrink-0 shadow-sm ${methodMeta.iconContainerClass}`}
                      title={`${methodMeta.code}: ${methodMeta.name} (${methodMeta.badgeLabel})`}
                    >
                      {methodMeta.icon({ className: 'h-4 w-4' })}
                    </div>
                    <div className="min-w-0">
                      <div className="text-sm font-bold text-white tracking-tight flex items-center gap-1.5 flex-wrap">
                        <span className="truncate">{result.method.split('(')[0].trim()}</span>
                        <span
                          className={`text-[10px] font-semibold px-1.5 py-0.5 rounded-md border tracking-tight ${methodMeta.badgeClass}`}
                        >
                          {methodMeta.badgeLabel}
                        </span>
                        {isDissenting && (
                          <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded-md bg-amber-500/20 text-amber-300 border border-amber-500/40 inline-flex items-center gap-1 shadow-sm ${shouldReduceMotion ? '' : 'animate-pulse'}`}>
                            <AlertTriangle className="h-2.5 w-2.5 text-amber-400" />
                            Dissenting
                          </span>
                        )}
                        {headerTag && (
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-teal-500/10 text-teal-300 border border-teal-500/20 font-semibold">
                            {headerTag}
                          </span>
                        )}
                      </div>
                      <div className="text-[11px] text-slate-400 font-mono truncate">
                        {result.method.includes('(')
                          ? result.method.split('(')[1].replace(')', '')
                          : result.method}
                      </div>
                    </div>
                  </div>

                  <Badge variant="neutral" size="sm">
                    <Clock className="h-3 w-3 mr-1 inline" />
                    {result.latency_ms < 1
                      ? `${result.latency_ms.toFixed(2)} ms`
                      : `${(result.latency_ms / 1000).toFixed(3)} s`}
                  </Badge>
                </div>

                {/* Optional Email Preview Box */}
                {emailSnippet && (
                  <div className="rounded-xl border border-slate-800 bg-slate-950/70 p-3 space-y-1.5">
                    <div className="flex items-center justify-between text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
                      <span>{emailLabel || 'Evaluated Email Text'}</span>
                      <span className="font-mono text-slate-500">{emailSnippet.length} chars</span>
                    </div>
                    <p className="text-[11px] font-mono text-slate-300 leading-relaxed max-h-24 overflow-y-auto whitespace-pre-wrap select-text">
                      {emailSnippet}
                    </p>
                  </div>
                )}

                {/* Consensus Annotation (When Compare Mode active) */}
                {consensusStatusLabel && (
                  <div
                    className={`px-2.5 py-1 rounded-lg text-[11px] font-semibold border ${
                      consensusStatusLabel.includes('Dissenting')
                        ? 'bg-rose-500/10 text-rose-300 border-rose-500/30'
                        : 'bg-teal-500/10 text-teal-300 border-teal-500/30'
                    }`}
                  >
                    {consensusStatusLabel}
                    {consensusNote && (
                      <span className="block font-normal opacity-80 text-[10px] mt-0.5">
                        {consensusNote}
                      </span>
                    )}
                  </div>
                )}

                {/* Verdict Badge & Prompt Injection Indicator */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                      Verdict:
                    </span>
                    <div className="flex items-center gap-1.5">
                      {!result.is_valid && (
                        <span
                          title="Model response could not be parsed or service was offline; default fallback verdict applied."
                          className="text-[10px] px-1.5 py-0.5 rounded bg-amber-500/15 text-amber-300 border border-amber-500/40 font-medium inline-flex items-center gap-1"
                        >
                          <AlertTriangle className="h-2.5 w-2.5 text-amber-400" />
                          Fallback
                        </span>
                      )}
                      <motion.div
                        initial={shouldReduceMotion ? { scale: 1, opacity: 1 } : { scale: 1.0, opacity: 0 }}
                        animate={shouldReduceMotion ? { scale: 1, opacity: 1 } : { scale: [1.0, 1.08, 1.0], opacity: 1 }}
                        transition={shouldReduceMotion ? { duration: 0 } : {
                          scale: { duration: 0.42, times: [0, 0.5, 1], ease: [0.16, 1, 0.3, 1], delay: 0.1 },
                          opacity: { duration: 0.2, ease: 'easeOut' },
                        }}
                        className="inline-flex items-center"
                      >
                        <Badge
                          variant={!result.is_valid ? 'neutral' : isPhishing ? 'phishing' : 'legitimate'}
                          size="md"
                          dot
                        >
                          {isPhishing ? 'PHISHING' : 'LEGITIMATE'}
                        </Badge>
                      </motion.div>
                    </div>
                  </div>

                  <div className="flex items-center justify-between pt-1">
                    <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                      Prompt Injection:
                    </span>
                    {result.has_prompt_injection ? (
                      <Badge variant="injection" size="sm" dot pulse>
                        DETECTED
                      </Badge>
                    ) : result.method.startsWith('M1') ? (
                      <Badge variant="neutral" size="sm">
                        N/A (Linear)
                      </Badge>
                    ) : (
                      <Badge variant="neutral" size="sm">
                        None Detected
                      </Badge>
                    )}
                  </div>
                </div>

                {/* Confidence Progress Bar with raw confidence alongside bar */}
                <div className="space-y-1.5 pt-1">
                  <div className="flex justify-between items-center text-xs">
                    <div className="flex items-center gap-1.5 text-slate-400">
                      <span>Confidence Score:</span>
                      <div className="relative group inline-flex items-center">
                        <button
                          type="button"
                          tabIndex={0}
                          aria-label="Confidence score explanation"
                          className="text-slate-400 hover:text-teal-300 focus:outline-none focus:text-teal-300 transition-colors cursor-help p-0.5 rounded"
                        >
                          <Info className="h-3 w-3" />
                        </button>
                        <div
                          role="tooltip"
                          className="pointer-events-none absolute bottom-full left-0 mb-2 w-72 p-2.5 rounded-xl bg-slate-900 border border-slate-700/90 text-[11px] text-slate-300 shadow-2xl opacity-0 group-hover:opacity-100 group-focus-within:opacity-100 transition-opacity duration-150 z-40 leading-relaxed font-normal"
                        >
                          <div className="font-semibold text-white mb-1 flex items-center gap-1.5">
                            <Info className="h-3.5 w-3.5 text-teal-400 flex-shrink-0" />
                            <span>Verdict Confidence Metric</span>
                          </div>
                          <p className="text-slate-300">
                            Measures estimated posterior certainty for the predicted verdict (<span className="text-slate-100 font-medium">{isPhishing ? 'Phishing' : 'Legitimate'}</span>), not raw phishing likelihood.
                          </p>
                          <p className="text-slate-400 mt-1">
                            M1 uses logistic probability, M2/M3 use self-assessed LLM certainty, and M4 combines isolated pipeline stages. A score of 0.0% reflects model parse failure or offline service fallback.
                          </p>
                          <div className="absolute top-full left-3 -mt-1 border-4 border-transparent border-t-slate-700/90" />
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-1.5">
                      {!result.is_valid && (
                        <span className="text-[10px] text-amber-400/90 font-mono">(Fallback)</span>
                      )}
                      <span className="font-bold font-mono text-white">
                        {confidencePercent}%
                      </span>
                    </div>
                  </div>
                  <div className="h-2 w-full bg-slate-950 rounded-full overflow-hidden border border-slate-800">
                    <motion.div
                      initial={{ width: '0%' }}
                      animate={{ width: `${Math.max(result.is_valid ? 5 : 0, Math.min(100, Number(confidencePercent)))}%` }}
                      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
                      className={`h-full rounded-full ${
                        !result.is_valid
                          ? 'bg-amber-500/40'
                          : isPhishing
                          ? 'bg-gradient-to-r from-rose-500 to-red-400'
                          : 'bg-gradient-to-r from-teal-500 to-emerald-400'
                      }`}
                    />
                  </div>
                </div>
              </div>

              {/* Collapsible Details Drawer Trigger */}
              <div className="border-t border-slate-800/80 bg-slate-950/40">
                <button
                  type="button"
                  onClick={toggleDetails}
                  className="w-full px-4 py-2.5 flex items-center justify-between text-xs font-medium text-slate-300 hover:text-teal-300 hover:bg-slate-900/70 hover:brightness-105 active:scale-[0.97] active:bg-slate-900/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-inset transition-all duration-150"
                >
                  <span className="flex items-center gap-1.5">
                    <Database className="h-3.5 w-3.5 text-teal-400" />
                    <span>Details & Reasoning</span>
                  </span>
                  {isOpen ? (
                    <ChevronUp className="h-3.5 w-3.5" />
                  ) : (
                    <ChevronDown className="h-3.5 w-3.5" />
                  )}
                </button>

                {/* Collapsible Content */}
                {isOpen && (
                  <div className="p-4 pt-3 space-y-3.5 text-xs text-slate-200 border-t border-slate-800/80 bg-slate-950/85 backdrop-blur-md max-h-96 overflow-y-auto">
                    {/* 1. Reasoning Tokens / Points */}
                    {result.reasons && result.reasons.length > 0 && (
                      <div className="space-y-1.5">
                        <span className="text-[11px] font-semibold text-slate-300 uppercase tracking-wider block">
                          Model Reasoning Tokens:
                        </span>
                        <ul className="space-y-1 text-slate-200 text-xs">
                          {result.reasons.map((r, i) => (
                            <li key={i} className="flex items-start gap-1.5 leading-relaxed">
                              <span className="text-teal-400 font-bold">&bull;</span>
                              <span>{r}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* 2. M4 Two-Call Pipeline Breakdown */}
                    {result.method.startsWith('M4') && (
                      <div className="space-y-2 pt-2 border-t border-slate-800/80">
                        <span className="text-[11px] font-semibold text-teal-300 uppercase tracking-wider block">
                          Two-Stage Isolated Execution Trace:
                        </span>
                        <div className="rounded-lg bg-slate-900/80 backdrop-blur-sm p-2.5 border border-slate-800/80 border-t-slate-700/60 space-y-1">
                          <div className="font-semibold text-slate-100">
                            Stage 1: Prompt Injection Detector
                          </div>
                          <div className="text-[11px] text-slate-300">
                            Injection Detected: <span className="font-mono text-white font-medium">{result.has_injection ? 'TRUE' : 'FALSE'}</span>
                          </div>
                          {result.raw_response_call1 && (
                            <div className="text-[10px] font-mono text-slate-300 break-words mt-1 bg-slate-950/85 backdrop-blur-sm p-1.5 rounded border border-slate-800/60">
                              {result.raw_response_call1}
                            </div>
                          )}
                        </div>

                        <div className="rounded-lg bg-slate-900/80 backdrop-blur-sm p-2.5 border border-slate-800/80 border-t-slate-700/60 space-y-1">
                          <div className="font-semibold text-slate-100">
                            Stage 2: Boolean Phishing Classifier
                          </div>
                          <div className="text-[11px] text-slate-300">
                            Phishing Verdict: <span className="font-mono text-white font-medium">{result.is_phishing_only ? 'TRUE (PHISHING)' : 'FALSE (LEGITIMATE)'}</span>
                          </div>
                          {result.raw_response_call2 && (
                            <div className="text-[10px] font-mono text-slate-300 break-words mt-1 bg-slate-950/85 backdrop-blur-sm p-1.5 rounded border border-slate-800/60">
                              {result.raw_response_call2}
                            </div>
                          )}
                        </div>
                      </div>
                    )}

                    {/* 3. Retrieved FAISS Exemplars (For M3 & M4) */}
                    {result.retrieved_samples && result.retrieved_samples.length > 0 && (
                      <div className="space-y-2 pt-2 border-t border-slate-800/80">
                        <span className="text-[11px] font-semibold text-slate-300 uppercase tracking-wider block">
                          Retrieved FAISS Exemplars (Top {result.retrieved_samples.length}):
                        </span>
                        <div className="space-y-2">
                          {result.retrieved_samples.map((sample: any, idx: number) => {
                            const sampleId = sample.id || `sample-${idx}`;
                            const score = sample.similarity_score !== undefined
                              ? (sample.similarity_score * 100).toFixed(1)
                              : null;
                            return (
                              <div
                                key={idx}
                                className="rounded-lg bg-slate-900/80 backdrop-blur-sm p-2 border border-slate-800/80 border-t-slate-700/60 text-[11px] space-y-1"
                              >
                                <div className="flex items-center justify-between text-[10px]">
                                  <span className="font-mono text-slate-300">{sampleId}</span>
                                  <div className="flex items-center gap-1.5">
                                    {score && (
                                      <span className="text-slate-400">Similarity: {score}%</span>
                                    )}
                                    <Badge
                                      variant={sample.label === 1 || sample.label_name === 'phishing' ? 'phishing' : 'legitimate'}
                                      size="sm"
                                    >
                                      {sample.label === 1 || sample.label_name === 'phishing' ? 'PHISH' : 'LEGIT'}
                                    </Badge>
                                  </div>
                                </div>
                                {sample.text && (
                                  <p className="text-slate-300 font-mono text-[10px] line-clamp-2">
                                    {sample.text}
                                  </p>
                                )}
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    )}

                    {/* 4. Raw Response Snippet */}
                    {result.raw_response && (
                      <div className="pt-2 border-t border-slate-800/80 space-y-1">
                        <div className="flex items-center justify-between">
                          <span className="text-[10px] text-slate-400 uppercase font-mono">
                            Raw Completion String:
                          </span>
                          <button
                            type="button"
                            onClick={() => handleCopy(result.method, result.raw_response || '')}
                            className="text-[10px] text-teal-400 hover:text-teal-300 hover:scale-[1.05] hover:brightness-110 active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-offset-1 rounded px-1.5 py-0.5 inline-flex items-center gap-1 transition-all duration-150"
                          >
                            {isCopied ? (
                              <>
                                <Check className="h-3 w-3" /> Copied
                              </>
                            ) : (
                              <>
                                <Copy className="h-3 w-3" /> Copy
                              </>
                            )}
                          </button>
                        </div>
                        <pre className="p-2.5 rounded-lg bg-slate-950/85 backdrop-blur-sm border border-slate-800/80 border-t-slate-700/60 text-[10px] font-mono text-slate-200 whitespace-pre-wrap break-all shadow-inner">
                          {result.raw_response}
                        </pre>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </Card>
  );
};
