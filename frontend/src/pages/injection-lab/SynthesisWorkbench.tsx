import React from 'react';
import {
  FlaskConical,
  Play,
  RotateCcw,
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  Copy,
  Check,
  ChevronDown,
  ChevronUp,
  Loader2,
} from 'lucide-react';
import { Badge } from '../../components/Badge';
import { MethodResultCard } from '../../components/MethodResultCard';
import { Skeleton, SkeletonMethodCard } from '../../components/Skeleton';
import { motion, AnimatePresence } from 'framer-motion';
import { fadeInUp, staggerContainer } from '../../lib/motion';
import type {
  PresetSample,
  ClassificationResult,
  InjectResponse,
} from '../../api/client';
import type { AttackFamilyMeta } from './types';

export interface SynthesisWorkbenchProps {
  presets: Record<string, PresetSample>;
  selectedPresetKey: string;
  loadingPresets: boolean;
  baseSubject: string;
  setBaseSubject: (v: string) => void;
  baseSender: string;
  setBaseSender: (v: string) => void;
  baseBody: string;
  setBaseBody: (v: string) => void;
  attackFamilies: AttackFamilyMeta[];
  attackFamily: string;
  setAttackFamily: (v: string) => void;
  attackStyle: 'unmarked' | 'marked';
  setAttackStyle: (v: 'unmarked' | 'marked') => void;
  attackPosition: 'body_start' | 'body_middle' | 'body_end';
  setAttackPosition: (v: 'body_start' | 'body_middle' | 'body_end') => void;
  evalMethod: 'M3' | 'M4' | 'M1' | 'M2';
  setEvalMethod: (v: 'M3' | 'M4' | 'M1' | 'M2') => void;
  evalModel: string;
  setEvalModel: (v: string) => void;
  isEvaluating: boolean;
  attackRan: boolean;
  cleanResult: ClassificationResult | null;
  injectedResult: ClassificationResult | null;
  injectDetails: InjectResponse | null;
  cleanFullText: string;
  injectedFullText: string;
  errorMessage: string | null;
  showPayloadDetails: boolean;
  setShowPayloadDetails: React.Dispatch<React.SetStateAction<boolean>>;
  copiedPayload: boolean;
  onSelectPreset: (key: string) => void;
  onResetWorkbench: () => void;
  onRunAttack: () => void;
  onCopyPayload: () => void;
}

export const SynthesisWorkbench: React.FC<SynthesisWorkbenchProps> = ({
  presets,
  selectedPresetKey,
  loadingPresets,
  baseSubject,
  setBaseSubject,
  baseSender,
  setBaseSender,
  baseBody,
  setBaseBody,
  attackFamilies,
  attackFamily,
  setAttackFamily,
  attackStyle,
  setAttackStyle,
  attackPosition,
  setAttackPosition,
  evalMethod,
  setEvalMethod,
  evalModel,
  setEvalModel,
  isEvaluating,
  attackRan,
  cleanResult,
  injectedResult,
  injectDetails,
  cleanFullText,
  injectedFullText,
  errorMessage,
  showPayloadDetails,
  setShowPayloadDetails,
  copiedPayload,
  onSelectPreset,
  onResetWorkbench,
  onRunAttack,
  onCopyPayload,
}) => {
  const getAttackOutcome = () => {
    if (!cleanResult || !injectedResult) return null;
    const cleanPhish = cleanResult.is_phishing;
    const injPhish = injectedResult.is_phishing;

    if (cleanPhish && !injPhish) {
      return {
        type: 'evasion_success',
        title: 'Attack Succeeded (Evasion Collapse)',
        desc: 'The injected instruction successfully fooled the classifier into declaring this malicious phishing message as legitimate.',
        color: 'rose',
      };
    }
    if (cleanPhish && injPhish) {
      return {
        type: 'evasion_blocked',
        title: 'Attack Defeated (Robust Detection)',
        desc: 'The model successfully resisted the prompt injection payload and correctly flagged the underlying phishing threat.',
        color: 'emerald',
      };
    }
    if (!cleanPhish && injPhish) {
      return {
        type: 'false_positive',
        title: 'Incurred False Positive',
        desc: 'The benign email was marked as phishing due to the presence of the security text instruction.',
        color: 'amber',
      };
    }
    return {
      type: 'neutral',
      title: 'Neutral Classification',
      desc: 'The model maintained its legitimate verdict across both clean and injected conditions.',
      color: 'slate',
    };
  };

  const outcome = getAttackOutcome();

  return (
    <section id="workbench-section" className="space-y-6 scroll-mt-20">
      <div className="border-b border-slate-800 pb-4">
        <div className="flex items-center gap-2 text-teal-400 text-xs font-semibold uppercase tracking-wider">
          <FlaskConical className="h-4 w-4" />
          <span>Live Adversarial Workbench</span>
        </div>
        <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight mt-1 font-['Plus_Jakarta_Sans',sans-serif]">
          Try an Attack
        </h2>
        <p className="text-xs sm:text-sm text-slate-400 mt-0.5">
          Synthesize adversarial emails using authentic attack families to compare clean baseline vs. injected classification across M1–M4, testing whether M3 is evaded or M4 triggers false alarms in real time.
        </p>
      </div>

      {/* Preset Library Quick Bar */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4 space-y-2">
        <div className="flex items-center justify-between text-xs text-slate-400">
          <span className="font-semibold text-slate-300 flex items-center gap-1.5">
            <span>📚</span> Curated Benchmark Presets:
          </span>
        </div>

        <div className="flex flex-wrap gap-2">
          {loadingPresets ? (
            <div className="flex gap-2">
              <Skeleton className="h-8 w-28 rounded-lg" />
              <Skeleton className="h-8 w-32 rounded-lg" />
              <Skeleton className="h-8 w-24 rounded-lg" />
            </div>
          ) : (
            Object.keys(presets).map((pKey) => {
              const sample = presets[pKey];
              const isSelected = selectedPresetKey === pKey;
              const isPhish = sample.label === 'phishing';
              return (
                <button
                  key={pKey}
                  type="button"
                  onClick={() => onSelectPreset(pKey)}
                  className={`px-3 py-1.5 rounded-lg border text-xs font-medium transition-all duration-150 hover:scale-[1.02] hover:brightness-105 active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 flex items-center gap-1.5 ${
                    isSelected
                      ? 'border-teal-500 bg-teal-500/15 text-white font-semibold ring-1 ring-teal-500/30'
                      : 'border-slate-800 bg-slate-950/60 text-slate-400 hover:border-slate-700 hover:text-slate-200'
                  }`}
                >
                  <span className={`h-1.5 w-1.5 rounded-full ${isPhish ? 'bg-rose-400' : 'bg-emerald-400'}`} />
                  <span className="truncate max-w-[220px]">{pKey}</span>

                </button>
              );
            })
          )}
        </div>
      </div>

      {/* Main Interactive Workbench Card */}
      <div className="rounded-2xl border border-slate-800/80 bg-slate-900/60 p-5 sm:p-7 elevation-card backdrop-blur-sm space-y-6">
        {/* 1. Base Email Inputs */}
        <div className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-semibold text-slate-300 block mb-1.5">
                Subject Line:
              </label>
              <input
                type="text"
                value={baseSubject}
                onChange={(e) => setBaseSubject(e.target.value)}
                placeholder="e.g. Urgent Security Advisory: Password Verification Required"
                className="w-full rounded-xl bg-slate-950 border border-slate-800 p-2.5 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-teal-500 focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 transition-colors"
              />
            </div>
            <div>
              <label className="text-xs font-semibold text-slate-300 block mb-1.5">
                From / Sender Address:
              </label>
              <input
                type="text"
                value={baseSender}
                onChange={(e) => setBaseSender(e.target.value)}
                placeholder="e.g. IT Helpdesk Security <helpdesk@corporate-support.org>"
                className="w-full rounded-xl bg-slate-950 border border-slate-800 p-2.5 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-teal-500 focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 transition-colors"
              />
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="text-xs font-semibold text-slate-300">
                Email Body Text (Clean Baseline):
              </label>

            </div>
            <textarea
              rows={4}
              value={baseBody}
              onChange={(e) => setBaseBody(e.target.value)}
              placeholder="Paste raw email body here or select a curated preset from the bar above..."
              className="w-full rounded-xl bg-slate-950 border border-slate-800 p-3 text-xs font-mono text-slate-200 placeholder-slate-600 focus:outline-none focus:border-teal-500 focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 transition-colors"
            />
          </div>
        </div>

        {/* 2. Attack Parameters Row: Family, Style, Position, and Architecture */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 pt-4 border-t border-slate-800">
          {/* Attack Family Selector */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300 block">
              2. Attack Family:
            </label>
            <select
              value={attackFamily}
              onChange={(e) => setAttackFamily(e.target.value)}
              className="w-full rounded-xl bg-slate-950 border border-slate-800 p-2.5 text-xs text-slate-200 font-medium hover:border-slate-700 hover:bg-slate-900/50 active:scale-[0.98] focus:outline-none focus:border-teal-500 focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 transition-all duration-150 cursor-pointer"
            >
              {attackFamilies.map((fam) => (
                <option key={fam.id} value={fam.id}>
                  {fam.name}
                </option>
              ))}
            </select>
            <span className="text-[11px] text-slate-500 block leading-tight">
              {attackFamilies.find((f) => f.id === attackFamily)?.tagline}
            </span>
          </div>

          {/* Style Selector: Marked vs Unmarked */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300 block">
              3. Disguise Style:
            </label>
            <div className="grid grid-cols-2 gap-1.5 p-1 bg-slate-950 rounded-xl border border-slate-800">
              <button
                type="button"
                onClick={() => setAttackStyle('unmarked')}
                className={`py-1.5 text-xs font-semibold rounded-lg transition-all duration-150 hover:scale-[1.02] hover:brightness-105 active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 ${
                  attackStyle === 'unmarked'
                    ? 'bg-teal-500 text-slate-950 shadow font-bold'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
                }`}
              >
                Unmarked (Real)
              </button>
              <button
                type="button"
                onClick={() => setAttackStyle('marked')}
                className={`py-1.5 text-xs font-semibold rounded-lg transition-all duration-150 hover:scale-[1.02] hover:brightness-105 active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 ${
                  attackStyle === 'marked'
                    ? 'bg-cyan-500 text-slate-950 shadow font-bold'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
                }`}
              >
                Marked (Tags)
              </button>
            </div>
            <span className="text-[11px] text-slate-500 block leading-tight">
              {attackStyle === 'unmarked' ? 'Disguised as IT Forwarded / Legal Header' : 'Synthetic machine bracket syntax'}
            </span>
          </div>

          {/* Position Selector */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300 block">
              4. Placement Position:
            </label>
            <select
              value={attackPosition}
              onChange={(e) => setAttackPosition(e.target.value as 'body_start' | 'body_middle' | 'body_end')}
              className="w-full rounded-xl bg-slate-950 border border-slate-800 p-2.5 text-xs text-slate-200 font-medium hover:border-slate-700 hover:bg-slate-900/50 active:scale-[0.98] focus:outline-none focus:border-teal-500 focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 transition-all duration-150 cursor-pointer"
            >
              <option value="body_start">Start / Header (Prepend)</option>
              <option value="body_middle">Middle of Body</option>
              <option value="body_end">End / Footer (Append)</option>
            </select>

          </div>

          {/* Evaluation Architecture */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300 block">
              5. Evaluate Architecture:
            </label>
            <select
              value={evalMethod}
              onChange={(e) => setEvalMethod(e.target.value as 'M3' | 'M4' | 'M1' | 'M2')}
              className="w-full rounded-xl bg-slate-950 border border-slate-800 p-2.5 text-xs text-slate-200 font-medium hover:border-slate-700 hover:bg-slate-900/50 active:scale-[0.98] focus:outline-none focus:border-teal-500 focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 transition-all duration-150 cursor-pointer"
            >
              <option value="M3">M3: RAG Combined (Vulnerable to Evasion)</option>
              <option value="M4">M4: RAG Decoupled (IFSI Robust Pipeline)</option>
              <option value="M1">M1: TF-IDF (Linear Classical Baseline)</option>
              <option value="M2">M2: Zero-Shot LLM (Prompt Baseline)</option>
            </select>
            <div className="flex items-center gap-1.5 pt-1">
              <span className="text-[10px] text-slate-400 font-mono">LLM:</span>
              <select
                value={evalModel}
                onChange={(e) => setEvalModel(e.target.value)}
                className="rounded-lg bg-slate-900 border border-slate-800 px-2 py-0.5 text-[11px] text-teal-300 font-mono hover:border-slate-700 hover:bg-slate-850 active:scale-[0.98] focus:outline-none focus:border-teal-500 focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-offset-1 transition-all duration-150 cursor-pointer"
              >
                <option value="qwen2.5:0.5b">qwen2.5:0.5b (Fast)</option>
                <option value="llama3.2:3b">llama3.2:3b</option>
              </select>
            </div>
          </div>
        </div>

        {/* Error Message Alert */}
        {errorMessage && (
          <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-3.5 flex items-center gap-3 text-xs text-rose-300">
            <AlertTriangle className="h-4 w-4 flex-shrink-0 text-rose-400" />
            <span>{errorMessage}</span>
          </div>
        )}

        {/* Action Controls Bar */}
        <div className="flex flex-wrap items-center justify-between gap-3 pt-4 border-t border-slate-800">


          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={onResetWorkbench}
              disabled={isEvaluating}
              className="px-3.5 py-2 rounded-xl border border-slate-800 bg-slate-950/80 text-xs font-semibold text-slate-300 hover:bg-slate-900 hover:text-white hover:border-slate-700 active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 transition-all duration-150 cursor-pointer flex items-center gap-1.5"
            >
              <RotateCcw className="h-3.5 w-3.5" />
              <span>Reset</span>
            </button>

            <button
              type="button"
              onClick={onRunAttack}
              disabled={isEvaluating}
              className="px-6 py-2.5 rounded-xl border border-teal-400/40 bg-gradient-to-r from-teal-500 to-cyan-500 text-xs font-bold text-slate-950 shadow-lg shadow-teal-500/20 hover:brightness-110 active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 transition-all duration-150 cursor-pointer flex items-center gap-2 disabled:opacity-50"
            >
              {isEvaluating ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin text-slate-950" />
                  <span>Synthesizing &amp; Evaluating...</span>
                </>
              ) : (
                <>
                  <Play className="h-4 w-4 fill-slate-950 text-slate-950" />
                  <span>Run Attack &bull; Dual Evaluate</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* RESULTS AREA: Side-by-Side Clean vs. Injected */}
        <div className="space-y-6 pt-4 border-t border-slate-800/80">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold uppercase tracking-wider text-teal-400">
                Evaluation Results
              </span>
              <span className="text-slate-600">&bull;</span>
              <span className="text-xs text-slate-400">
                {attackRan ? 'Clean Baseline vs. Injected Email' : 'Awaiting Execution'}
              </span>
            </div>
          </div>

          <div className="relative">
            <AnimatePresence mode="popLayout" initial={false}>
              {isEvaluating ? (
                <motion.div
                  key="workbench-loading"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full"
                >
                  <SkeletonMethodCard />
                  <SkeletonMethodCard />
                </motion.div>
              ) : !attackRan ? (
                <motion.div
                  key="workbench-placeholder"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="rounded-2xl border border-dashed border-slate-800 bg-slate-950/40 p-12 text-center text-xs text-slate-500 space-y-2"
                >
                  <FlaskConical className="h-8 w-8 mx-auto text-slate-600" />
                  <p className="font-medium text-slate-400">Awaiting Adversarial Evaluation</p>
                  <p>Select an attack template and click "Run Attack &bull; Dual Evaluate" to test whether M3 evades or M4 detects the injection.</p>
                </motion.div>
              ) : (
                <motion.div
                  key="workbench-results"
                  variants={staggerContainer}
                  initial="hidden"
                  animate="visible"
                  exit={{ opacity: 0 }}
                  className="space-y-6 w-full"
                >
                  {/* Outcome Highlight Callout */}
                  {outcome && (
                    <motion.div
                      variants={fadeInUp}
                      className={`rounded-xl border p-4 flex items-center justify-between gap-4 ${
                        outcome.color === 'rose'
                          ? 'border-rose-500/40 bg-rose-500/10 text-rose-200'
                          : outcome.color === 'emerald'
                          ? 'border-emerald-500/40 bg-emerald-500/10 text-emerald-200'
                          : 'border-amber-500/40 bg-amber-500/10 text-amber-200'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        {outcome.color === 'rose' ? (
                          <ShieldAlert className="h-5 w-5 text-rose-400 flex-shrink-0" />
                        ) : (
                          <ShieldCheck className="h-5 w-5 text-emerald-400 flex-shrink-0" />
                        )}
                        <div>
                          <div className="font-bold text-sm tracking-tight">{outcome.title}</div>
                          <div className="text-xs opacity-90 mt-0.5 leading-relaxed">{outcome.desc}</div>
                        </div>
                      </div>
                      <Badge variant={outcome.color === 'emerald' ? 'legitimate' : 'phishing'} size="sm">
                        {outcome.type === 'evasion_success' ? 'Evasion Succeeded' : 'Defense Passed'}
                      </Badge>
                    </motion.div>
                  )}

                  {/* Dual Result Cards Grid */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* LEFT: Clean Baseline Result */}
                    {cleanResult && (
                      <motion.div variants={fadeInUp} className="space-y-2">
                        <div className="flex items-center justify-between text-xs font-semibold text-slate-300 px-1">
                          <span className="flex items-center gap-1.5">
                            <span className="h-2 w-2 rounded-full bg-slate-400" />
                            Clean Baseline Email ({cleanResult.method})
                          </span>
                          <span className="text-[11px] font-mono text-slate-500">Unmodified</span>
                        </div>
                        <MethodResultCard
                          result={cleanResult}
                          emailSnippet={cleanFullText}
                        />
                      </motion.div>
                    )}

                    {/* RIGHT: Injected Email Result */}
                    {injectedResult && (
                      <motion.div variants={fadeInUp} className="space-y-2">
                        <div className="flex items-center justify-between text-xs font-semibold text-slate-300 px-1">
                          <span className="flex items-center gap-1.5">
                            <span className={`h-2 w-2 rounded-full ${injectedResult.is_phishing ? 'bg-emerald-400' : 'bg-rose-400'}`} />
                            Injected Email ({injectedResult.method})
                          </span>
                          {injectDetails && (
                            <span className="text-[11px] font-mono text-teal-400">
                              ({injectDetails.attack_family} &bull; {injectDetails.style})
                            </span>
                          )}
                        </div>
                        <MethodResultCard
                          result={injectedResult}
                          emailSnippet={injectedFullText}
                        />
                      </motion.div>
                    )}
                  </div>

                  {/* Synthesized Injection Payload Inspect Accordion */}
                  {injectDetails && (
                    <motion.div
                      variants={fadeInUp}
                      className="rounded-xl border border-slate-800 bg-slate-950/70 p-4 space-y-3"
                    >
                      <div className="flex items-center justify-between">
                        <button
                          type="button"
                          onClick={() => setShowPayloadDetails((prev) => !prev)}
                          className="flex items-center gap-2 text-xs font-bold text-slate-300 hover:text-white transition-colors"
                        >
                          {showPayloadDetails ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                          <span>Inspect Synthesized Injection Payload Alone</span>
                          <span className="text-[11px] font-mono text-teal-400">
                            ({injectDetails.payload.length} chars)
                          </span>
                        </button>

                        <button
                          type="button"
                          onClick={onCopyPayload}
                          className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg border border-slate-700 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium transition-all duration-150 hover:scale-[1.02] hover:brightness-105 active:scale-[0.97]"
                        >
                          {copiedPayload ? (
                            <>
                              <Check className="h-3 w-3 text-emerald-400" />
                              <span className="text-emerald-400">Copied</span>
                            </>
                          ) : (
                            <>
                              <Copy className="h-3 w-3 text-slate-400" />
                              <span>Copy Payload</span>
                            </>
                          )}
                        </button>
                      </div>

                      {showPayloadDetails && (
                        <div className="space-y-2 pt-2 border-t border-slate-800/80">
                          <pre className="p-3 rounded-lg bg-slate-950 border border-slate-800 font-mono text-xs text-teal-300 whitespace-pre-wrap select-text leading-relaxed">
                            {injectDetails.payload}
                          </pre>
                          <div className="flex flex-wrap items-center gap-3 text-[11px] text-slate-400 font-mono">
                            <span>Style: <strong className="text-slate-200">{injectDetails.style}</strong></span>
                            <span>&bull;</span>
                            <span>Family: <strong className="text-slate-200">{injectDetails.attack_family}</strong></span>
                            <span>&bull;</span>
                            <span>Position: <strong className="text-slate-200">{injectDetails.position}</strong></span>
                          </div>
                        </div>
                      )}
                    </motion.div>
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </section>
  );
};

export default SynthesisWorkbench;
