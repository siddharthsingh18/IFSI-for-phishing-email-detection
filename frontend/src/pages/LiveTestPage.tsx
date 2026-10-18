import React, { useEffect, useState } from 'react';
import {
  Terminal,
  Play,
  GitCompare,
  RotateCcw,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  ShieldCheck,
  Inbox,
  FlaskConical,
  Loader2,
} from 'lucide-react';
import {
  apiClient,
  type ClassificationResult,
  type CompareResponse,
  type PresetSample,
} from '../api/client';
import { Card } from '../components/Card';
import { OfflineFallbackBanner } from '../components/OfflineFallbackBanner';
import { Badge } from '../components/Badge';
import { MethodResultCard } from '../components/MethodResultCard';
import { Skeleton, SkeletonMethodCard } from '../components/Skeleton';
import { motion, AnimatePresence } from 'framer-motion';
import { fadeInUp, staggerContainer } from '../lib/motion';

const ARCHITECTURE_TOOLTIPS: Record<string, string> = {
  M1: 'M1: TF-IDF + Logistic Regression (Traditional ML Baseline)',
  M2: 'M2: Zero-Shot LLM (Direct Prompting Baseline)',
  M3: 'M3: RAG Combined (Standard Single-Call RAG)',
  M4: 'M4: RAG Decoupled (IFSI Two-Stage Robust Architecture)',
};

const MODEL_TOOLTIPS: Record<string, string> = {
  'qwen2.5:0.5b': 'qwen2.5:0.5b (Default Local Model - 0.5B Parameters)',
  'llama3.2:3b': 'llama3.2:3b (Pilot Local Model - 3B Parameters)',
};

export const LiveTestPage: React.FC = () => {
  // Input Form States
  const [subject, setSubject] = useState('');
  const [sender, setSender] = useState('');
  const [emailText, setEmailText] = useState('');
  const [method, setMethod] = useState<'M1' | 'M2' | 'M3' | 'M4'>('M1');
  const [model, setModel] = useState('qwen2.5:0.5b');
  const [topK, setTopK] = useState(3);

  // Adversarial Prompt Injection Testbed State
  const [isInjectEnabled, setIsInjectEnabled] = useState(false);
  const [attackStyle, setAttackStyle] = useState<'unmarked' | 'marked'>('unmarked');
  const [attackFamily, setAttackFamily] = useState<string>('label_override');
  const [attackPosition, setAttackPosition] = useState<string>('body_start');

  // Preset Samples State
  const [presets, setPresets] = useState<Record<string, PresetSample>>({});
  const [selectedPresetKey, setSelectedPresetKey] = useState<string>('');
  const [loadingPresets, setLoadingPresets] = useState(true);
  const [isUsingFallback, setIsUsingFallback] = useState(false);

  // Execution & Output States
  const [isLoading, setIsLoading] = useState(false);
  const [executionMode, setExecutionMode] = useState<'single' | 'compare' | null>(null);
  const [singleResult, setSingleResult] = useState<ClassificationResult | null>(null);
  const [compareResult, setCompareResult] = useState<CompareResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Collapsible Accordion State for result details
  const [openDetailsMap, setOpenDetailsMap] = useState<Record<string, boolean>>({});
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  // Load curated presets on mount
  useEffect(() => {
    let mounted = true;
    apiClient
      .getPresets()
      .then((data) => {
        if (mounted) {
          setPresets(data);
          setLoadingPresets(false);
        }
      })
      .catch((err) => {
        console.error('Failed to load preset emails:', err);
        if (mounted) {
          setLoadingPresets(false);
          setIsUsingFallback(true);
        }
      });

    return () => {
      mounted = false;
    };
  }, []);

  const handleSelectPreset = (key: string) => {
    const sample = presets[key];
    if (!sample) return;
    setSelectedPresetKey(key);
    setSubject(sample.subject || '');
    setSender(sample.sender || '');
    setEmailText(sample.body || '');
    setErrorMessage(null);
  };

  const handleResetForm = () => {
    setSubject('');
    setSender('');
    setEmailText('');
    setSelectedPresetKey('');
    setIsInjectEnabled(false);
    setSingleResult(null);
    setCompareResult(null);
    setExecutionMode(null);
    setErrorMessage(null);
  };

  // Run Single Architecture Evaluation
  const handleRunSingle = async () => {
    if (!emailText.trim()) {
      setErrorMessage('Please enter email body content or select a curated preset.');
      return;
    }
    setErrorMessage(null);
    setIsLoading(true);
    setExecutionMode('single');
    setSingleResult(null);
    setCompareResult(null);

    try {
      let textToClassify = emailText;
      if (isInjectEnabled) {
        try {
          const injRes = await apiClient.injectEmail({
            text: emailText,
            style: attackStyle,
            attack_family: attackFamily,
            position: attackPosition,
          });
          textToClassify = injRes.injected_text;
        } catch (injectErr) {
          console.warn('Injection synthesis failed, using raw body:', injectErr);
        }
      }

      const res = await apiClient.classifyEmail({
        text: textToClassify,
        subject,
        sender,
        method,
        model,
        k: topK,
      });
      setSingleResult(res);
      // Auto-expand details for single result
      setOpenDetailsMap({ [method]: true });
    } catch (err: any) {
      console.error('Inference error:', err);
      setErrorMessage(err.message || 'Classification request failed.');
    } finally {
      setIsLoading(false);
    }
  };

  // Run Compare All Architectures
  const handleRunCompare = async () => {
    if (!emailText.trim()) {
      setErrorMessage('Please enter email body content or select a curated preset.');
      return;
    }
    setErrorMessage(null);
    setIsLoading(true);
    setExecutionMode('compare');
    setSingleResult(null);
    setCompareResult(null);

    try {
      let textToClassify = emailText;
      if (isInjectEnabled) {
        try {
          const injRes = await apiClient.injectEmail({
            text: emailText,
            style: attackStyle,
            attack_family: attackFamily,
            position: attackPosition,
          });
          textToClassify = injRes.injected_text;
        } catch (injectErr) {
          console.warn('Injection synthesis failed, using raw body:', injectErr);
        }
      }

      const res = await apiClient.classifyCompare({
        text: textToClassify,
        subject,
        sender,
        model,
        k: topK,
      });
      setCompareResult(res);
      // Default: collapse detail drawers in 4-column compare grid to keep cards compact
      setOpenDetailsMap({});
    } catch (err: any) {
      console.error('Comparison inference error:', err);
      setErrorMessage(err.message || 'Comparison request failed.');
    } finally {
      setIsLoading(false);
    }
  };

  const toggleDetails = (methodKey: string) => {
    setOpenDetailsMap((prev) => ({
      ...prev,
      [methodKey]: !prev[methodKey],
    }));
  };

  const handleCopySnippet = (snippetKey: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(snippetKey);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  const selectedSample = selectedPresetKey ? presets[selectedPresetKey] : null;

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

      {/* Page Title & Context Header */}
      <div>
        <div className="flex items-center gap-2 text-teal-400 text-xs font-semibold uppercase tracking-wider">
          <Terminal className="h-4 w-4" />
          Interactive Evaluation Sandbox
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight mt-1 font-['Plus_Jakarta_Sans',sans-serif]">
          Live Email Phishing &amp; Injection Test
        </h1>
        <p className="text-slate-400 text-sm mt-1 max-w-3xl leading-relaxed">
          Evaluate incoming emails in real-time across four classifier architectures. Submit an email below to inspect phishing verdicts, confidence scores, prompt injection detection, and full reasoning traces.
        </p>
      </div>

      {/* Preset Library Quick Bar */}
      <Card variant="default" padding="sm">
        <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-3 px-2 py-1.5">
          <div className="flex items-center gap-2 text-xs font-semibold text-slate-300 flex-shrink-0">
            <Sparkles className="h-4 w-4 text-teal-400 flex-shrink-0" />
            <span>Curated Benchmark Presets:</span>
          </div>
          <div className="w-full lg:w-auto flex-1 flex justify-start lg:justify-end">
            <AnimatePresence mode="popLayout" initial={false}>
              {loadingPresets ? (
                <motion.div
                  key="presets-skeleton"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.22, ease: 'easeInOut' }}
                  className="flex flex-wrap items-center gap-1.5"
                >
                  {[1, 2, 3, 4, 5].map((i) => (
                    <Skeleton key={i} className="h-7 w-28 rounded-lg" />
                  ))}
                </motion.div>
              ) : (
                <motion.div
                  key="presets-loaded"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.32, ease: 'easeOut' }}
                  className="flex flex-wrap items-center gap-1.5 w-full lg:w-auto"
                >
                  {Object.keys(presets).map((key) => {
                    const sample = presets[key];
                    const isSelected = selectedPresetKey === key;
                    const label = key.split('(')[0].trim();
                    return (
                      <button
                        key={key}
                        type="button"
                        onClick={() => handleSelectPreset(key)}
                        title={`${key} (Condition: ${sample.condition})`}
                        className={`px-2.5 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-all duration-150 hover:scale-[1.02] hover:brightness-105 active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 ${
                          isSelected
                            ? 'bg-teal-500/20 text-teal-200 border border-teal-500/50 font-semibold shadow-sm'
                            : 'bg-slate-800/80 text-slate-300 border border-slate-700/60 hover:bg-slate-800 hover:text-white'
                        }`}
                      >
                        <span>{label}</span>
                        <span className="ml-1 text-[10px] opacity-70">
                          ({sample.condition})
                        </span>
                      </button>
                    );
                  })}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </Card>

      {/* =========================================================================
          INPUT / OUTPUT SPLIT WORKSPACE
          Stacks vertically below 1024px (lg), side-by-side on desktop (1024px+)
          ========================================================================= */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: Email Composer & Configuration Workspace (5 cols on lg) */}
        <div className="lg:col-span-5 space-y-6 lg:sticky lg:top-24">
          <Card variant="elevated" padding="lg">
            <div className="space-y-6">
              {/* Header & Preset Status Badge */}
              <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-800/80">
                <div className="space-y-1">
                  <h2 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
                    <Terminal className="h-4 w-4 text-teal-400" />
                    Email Input & Inference Controls
                  </h2>
                  <p className="text-xs text-slate-400">
                    Configure subject, sender, and body content for inference.
                  </p>
                </div>

                {selectedSample && (
                  <div className="flex items-center gap-2">
                    <Badge
                      variant={selectedSample.label === 'phishing' ? 'phishing' : 'legitimate'}
                      size="sm"
                      dot
                    >
                      Ground Truth: {selectedSample.label.toUpperCase()}
                    </Badge>
                    <Badge variant="neutral" size="sm">
                      Condition: {selectedSample.condition.toUpperCase()}
                    </Badge>
                  </div>
                )}
              </div>

              {/* Model & Header Fields */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                <div className="sm:col-span-2">
                  <div className="flex items-center justify-between mb-1.5">
                    <label className="block text-xs font-semibold text-slate-300">
                      Target Architecture (Single Mode)
                    </label>
                    <span
                      title={ARCHITECTURE_TOOLTIPS[method] || method}
                      className="text-[10px] text-slate-400 font-mono hidden sm:inline-block cursor-help max-w-[260px] truncate"
                    >
                      {ARCHITECTURE_TOOLTIPS[method]?.split('(')[1]?.replace(')', '') || ''}
                    </span>
                  </div>
                  <select
                    value={method}
                    onChange={(e) => setMethod(e.target.value as any)}
                    title={ARCHITECTURE_TOOLTIPS[method] || method}
                    className="w-full rounded-xl bg-slate-950 border border-slate-800 px-3.5 py-2 text-xs sm:text-sm text-slate-200 truncate hover:border-slate-700 hover:bg-slate-900/50 active:scale-[0.98] focus:outline-none focus:border-teal-500 focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 transition-all duration-150 cursor-pointer"
                  >
                    <option value="M1" title="M1: TF-IDF + Logistic Regression (Traditional ML Baseline)">M1: TF-IDF + Logistic Regression</option>
                    <option value="M2" title="M2: Zero-Shot LLM (Direct Prompting Baseline)">M2: Zero-Shot LLM</option>
                    <option value="M3" title="M3: RAG Combined (Standard Single-Call RAG)">M3: RAG Combined (Single-Call)</option>
                    <option value="M4" title="M4: RAG Decoupled (IFSI Two-Stage Robust Architecture)">M4: RAG Decoupled (IFSI Two-Stage)</option>
                  </select>
                </div>

                <div className="sm:col-span-2">
                  <div className="flex items-center justify-between mb-1.5">
                    <label className="block text-xs font-semibold text-slate-300">
                      Local LLM &amp; RAG k
                    </label>
                    <span
                      title={MODEL_TOOLTIPS[model] || model}
                      className="text-[10px] text-teal-400 font-mono cursor-help"
                    >
                      k={topK} &bull; {model.split(':')[0]}
                    </span>
                  </div>
                  <div className="flex gap-2">
                    <select
                      value={model}
                      onChange={(e) => setModel(e.target.value)}
                      title={MODEL_TOOLTIPS[model] || model}
                      className="flex-1 min-w-0 rounded-xl bg-slate-950 border border-slate-800 px-3 py-2 text-xs sm:text-sm text-slate-200 truncate hover:border-slate-700 hover:bg-slate-900/50 active:scale-[0.98] focus:outline-none focus:border-teal-500 focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 transition-all duration-150 cursor-pointer"
                    >
                      <option value="qwen2.5:0.5b" title="qwen2.5:0.5b (Default Local Model - 0.5B Parameters)">qwen2.5:0.5b (Default)</option>
                      <option value="llama3.2:3b" title="llama3.2:3b (Pilot Local Model - 3B Parameters)">llama3.2:3b (Pilot)</option>
                    </select>
                    <select
                      value={topK}
                      onChange={(e) => setTopK(Number(e.target.value))}
                      title={`Top-${topK} RAG Exemplars: retrieves ${topK} most similar training emails from the FAISS index`}
                      className="w-20 flex-shrink-0 rounded-xl bg-slate-950 border border-slate-800 px-2 py-2 text-xs text-slate-200 text-center hover:border-slate-700 hover:bg-slate-900/50 active:scale-[0.98] focus:outline-none focus:border-teal-500 focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 transition-all duration-150 cursor-pointer"
                    >
                      <option value={1} title="k=1 exemplar">k=1</option>
                      <option value={3} title="k=3 exemplars">k=3</option>
                      <option value={5} title="k=5 exemplars">k=5</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                    Email Subject
                  </label>
                  <input
                    type="text"
                    value={subject}
                    onChange={(e) => setSubject(e.target.value)}
                    placeholder="e.g. Account Security Alert"
                    className="w-full rounded-xl bg-slate-950 border border-slate-800 px-3.5 py-2 text-xs sm:text-sm text-slate-200 focus:outline-none focus:border-teal-500 focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 transition-colors"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                    Sender / From Address
                  </label>
                  <input
                    type="text"
                    value={sender}
                    onChange={(e) => setSender(e.target.value)}
                    placeholder="e.g. security-alerts@bank.com"
                    className="w-full rounded-xl bg-slate-950 border border-slate-800 px-3.5 py-2 text-xs sm:text-sm text-slate-200 focus:outline-none focus:border-teal-500 focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 transition-colors"
                  />
                </div>
              </div>

              {/* Email Body Textarea */}
              <div className="space-y-1.5">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-semibold text-slate-300">
                    Email Body Text <span className="text-teal-400">*</span>
                  </label>
                  <span className="text-[11px] text-slate-500 font-mono">
                    {emailText.length} characters
                  </span>
                </div>
                <textarea
                  rows={6}
                  value={emailText}
                  onChange={(e) => setEmailText(e.target.value)}
                  placeholder="Paste raw email body here, or load a curated preset from the bar above..."
                  className="w-full rounded-xl bg-slate-950 border border-slate-800 p-4 text-xs sm:text-sm text-slate-200 font-mono leading-relaxed focus:outline-none focus:border-teal-500 focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 transition-colors resize-y"
                />
              </div>

              {/* =========================================================================
                  ADVERSARIAL PROMPT INJECTION TESTBED (Smooth height+opacity reveal)
                  ========================================================================= */}
              <div className="rounded-xl border border-slate-800 bg-slate-950/40 p-3.5 space-y-3">
                <div className="flex items-center justify-between gap-4">
                  <div className="flex items-center gap-3">
                    <div
                      className={`p-2 rounded-lg border transition-colors ${
                        isInjectEnabled
                          ? 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                          : 'bg-slate-800/60 text-slate-400 border-slate-700/50'
                      }`}
                    >
                      <FlaskConical className="h-4 w-4" />
                    </div>
                    <div>
                      <div className="text-xs font-bold text-white flex items-center gap-2">
                        <span>Adversarial Prompt Injection Simulator</span>
                        {isInjectEnabled && (
                          <Badge variant="injection" size="sm" dot pulse>
                            ACTIVE
                          </Badge>
                        )}
                      </div>
                      <p className="text-[11px] text-slate-400">
                        Embed an authentic adversarial injection payload into the email body before classifying.
                      </p>
                    </div>
                  </div>

                  {/* Animated Switch Toggle (Smooth thumb translation & active scale) */}
                  <button
                    type="button"
                    role="switch"
                    aria-checked={isInjectEnabled}
                    aria-label="Toggle Adversarial Prompt Injection"
                    onClick={() => setIsInjectEnabled(!isInjectEnabled)}
                    className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-all duration-300 ease-[cubic-bezier(0.16,1,0.3,1)] hover:brightness-110 hover:scale-[1.03] active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 ${
                      isInjectEnabled ? 'bg-amber-500' : 'bg-slate-800'
                    }`}
                  >
                    <span
                      aria-hidden="true"
                      className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-slate-950 shadow-md ring-0 transition-transform duration-300 ease-[cubic-bezier(0.34,1.56,0.64,1)] will-change-transform ${
                        isInjectEnabled ? 'translate-x-5' : 'translate-x-0'
                      }`}
                    />
                  </button>
                </div>

                {/* Height + Opacity Animated Disclosure for Attack Style & Family */}
                <AnimatePresence initial={false}>
                  {isInjectEnabled && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.25, ease: 'easeInOut' }}
                      className="overflow-hidden"
                    >
                      <div className="pt-2 border-t border-slate-800/60 space-y-3">
                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                          <div>
                            <label className="block text-[11px] font-semibold text-amber-200 uppercase tracking-wider mb-1">
                              Injection Style
                            </label>
                            <select
                              value={attackStyle}
                              onChange={(e) => setAttackStyle(e.target.value as any)}
                              className="w-full rounded-lg bg-slate-950 border border-slate-800 px-3 py-1.5 text-xs text-slate-200 hover:border-slate-700 hover:bg-slate-900/50 active:scale-[0.98] focus:outline-none focus:border-amber-500 focus-visible:ring-2 focus-visible:ring-amber-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 transition-all duration-150 cursor-pointer"
                            >
                              <option value="unmarked">Unmarked (Authentic Disguise)</option>
                              <option value="marked">Marked (Bracketed Override)</option>
                            </select>
                          </div>

                          <div>
                            <label className="block text-[11px] font-semibold text-amber-200 uppercase tracking-wider mb-1">
                              Attack Family
                            </label>
                            <select
                              value={attackFamily}
                              onChange={(e) => setAttackFamily(e.target.value)}
                              className="w-full rounded-lg bg-slate-950 border border-slate-800 px-3 py-1.5 text-xs text-slate-200 hover:border-slate-700 hover:bg-slate-900/50 active:scale-[0.98] focus:outline-none focus:border-amber-500 focus-visible:ring-2 focus-visible:ring-amber-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 transition-all duration-150 cursor-pointer"
                            >
                              <option value="label_override">Label Override (Direct imperative command)</option>
                              <option value="false_authority">False Authority (IT Security Gateway impersonation)</option>
                              <option value="output_hijack">Output Hijack (JSON schema forced override)</option>
                              <option value="rule_redefinition">Rule Redefinition (Policy exemption notice)</option>
                              <option value="light_obfuscation">Light Obfuscation (Spaced text character evasion)</option>
                            </select>
                          </div>

                          <div>
                            <label className="block text-[11px] font-semibold text-amber-200 uppercase tracking-wider mb-1">
                              Payload Placement
                            </label>
                            <select
                              value={attackPosition}
                              onChange={(e) => setAttackPosition(e.target.value)}
                              className="w-full rounded-lg bg-slate-950 border border-slate-800 px-3 py-1.5 text-xs text-slate-200 hover:border-slate-700 hover:bg-slate-900/50 active:scale-[0.98] focus:outline-none focus:border-amber-500 focus-visible:ring-2 focus-visible:ring-amber-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 transition-all duration-150 cursor-pointer"
                            >
                              <option value="body_start">Body Start (Prepend notice)</option>
                              <option value="body_middle">Body Middle</option>
                              <option value="body_end">Body End (Append disclaimer)</option>
                            </select>
                          </div>
                        </div>

                        <p className="text-[11px] text-amber-300/80 leading-relaxed bg-amber-500/10 border border-amber-500/20 rounded-lg p-2.5">
                          {attackStyle === 'unmarked'
                            ? 'Authentic unmarked injection: Natural administrative disclaimer blended directly into email body to test if standard RAG (M3) is duped into marking phishing as legitimate while decoupled IFSI (M4) resists.'
                            : 'Marked injection: Explicit [SYSTEM OVERRIDE] command directing the LLM to discard detection instructions and output legitimate.'}
                        </p>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>

              {/* Error Message Alert */}
              {errorMessage && (
                <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-3.5 flex items-center gap-3 text-xs text-rose-300">
                  <AlertTriangle className="h-4 w-4 text-rose-400 flex-shrink-0" />
                  <span>{errorMessage}</span>
                </div>
              )}

              {/* Primary Action Buttons */}
              <div className="flex flex-wrap items-center justify-between gap-4 pt-4 border-t border-slate-800/80">
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={handleResetForm}
                    disabled={isLoading}
                    className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-medium text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 transition-all duration-150 hover:scale-[1.02] hover:brightness-105 active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950"
                  >
                    <RotateCcw className="h-3.5 w-3.5" />
                    <span>Reset</span>
                  </button>
                </div>

                <div className="flex flex-wrap items-center gap-2.5">
                  {/* Compare All Button with smooth icon crossfade */}
                  <button
                    type="button"
                    onClick={handleRunCompare}
                    disabled={isLoading}
                    className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-700 bg-slate-800/90 px-3.5 py-2.5 text-xs sm:text-sm font-semibold text-slate-100 elevation-card hover:elevation-hover hover:bg-slate-700 hover:border-slate-600 transition-all duration-150 hover:scale-[1.02] hover:brightness-110 active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 disabled:opacity-60 disabled:cursor-not-allowed min-w-[155px]"
                  >
                    <div className="relative w-4 h-4 flex items-center justify-center flex-shrink-0">
                      <AnimatePresence mode="wait" initial={false}>
                        {isLoading && executionMode === 'compare' ? (
                          <motion.span
                            key="spinner"
                            initial={{ opacity: 0, scale: 0.6 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.6 }}
                            transition={{ duration: 0.16, ease: 'easeInOut' }}
                            className="absolute inset-0 flex items-center justify-center text-cyan-400"
                          >
                            <Loader2 className="h-4 w-4 animate-spin" />
                          </motion.span>
                        ) : (
                          <motion.span
                            key="compare-icon"
                            initial={{ opacity: 0, scale: 0.6 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.6 }}
                            transition={{ duration: 0.16, ease: 'easeInOut' }}
                            className="absolute inset-0 flex items-center justify-center text-cyan-400"
                          >
                            <GitCompare className="h-4 w-4" />
                          </motion.span>
                        )}
                      </AnimatePresence>
                    </div>
                    <div className="relative min-w-[85px] text-center">
                      <AnimatePresence mode="wait" initial={false}>
                        <motion.span
                          key={isLoading && executionMode === 'compare' ? 'loading' : 'idle'}
                          initial={{ opacity: 0, y: -2 }}
                          animate={{ opacity: 1, y: 0 }}
                          exit={{ opacity: 0, y: 2 }}
                          transition={{ duration: 0.16 }}
                          className="block"
                        >
                          {isLoading && executionMode === 'compare'
                            ? 'Comparing…'
                            : 'Compare All (M1–M4)'}
                        </motion.span>
                      </AnimatePresence>
                    </div>
                  </button>

                  {/* Single Method Classify Button with smooth icon crossfade */}
                  <button
                    type="button"
                    onClick={handleRunSingle}
                    disabled={isLoading}
                    className="inline-flex items-center justify-center gap-2 rounded-xl bg-teal-500 px-4 py-2.5 text-xs sm:text-sm font-bold text-slate-950 elevation-card hover:elevation-hover hover:bg-teal-400 transition-all duration-150 hover:scale-[1.02] hover:brightness-110 active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 disabled:opacity-60 disabled:cursor-not-allowed min-w-[130px]"
                  >
                    <div className="relative w-4 h-4 flex items-center justify-center flex-shrink-0">
                      <AnimatePresence mode="wait" initial={false}>
                        {isLoading && executionMode === 'single' ? (
                          <motion.span
                            key="spinner"
                            initial={{ opacity: 0, scale: 0.6 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.6 }}
                            transition={{ duration: 0.16, ease: 'easeInOut' }}
                            className="absolute inset-0 flex items-center justify-center"
                          >
                            <Loader2 className="h-4 w-4 animate-spin text-slate-950" />
                          </motion.span>
                        ) : (
                          <motion.span
                            key="play"
                            initial={{ opacity: 0, scale: 0.6 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.6 }}
                            transition={{ duration: 0.16, ease: 'easeInOut' }}
                            className="absolute inset-0 flex items-center justify-center"
                          >
                            <Play className="h-4 w-4 fill-current" />
                          </motion.span>
                        )}
                      </AnimatePresence>
                    </div>
                    <div className="relative min-w-[65px] text-center">
                      <AnimatePresence mode="wait" initial={false}>
                        <motion.span
                          key={isLoading && executionMode === 'single' ? 'loading' : 'idle'}
                          initial={{ opacity: 0, y: -2 }}
                          animate={{ opacity: 1, y: 0 }}
                          exit={{ opacity: 0, y: 2 }}
                          transition={{ duration: 0.16 }}
                          className="block"
                        >
                          {isLoading && executionMode === 'single'
                            ? 'Classifying…'
                            : `Classify (${method})`}
                        </motion.span>
                      </AnimatePresence>
                    </div>
                  </button>
                </div>
              </div>
            </div>
          </Card>
        </div>

        {/* Right Column: Inference Output & Model Diagnostician (7 cols on lg) */}
        <div className="lg:col-span-7 space-y-6">
          <section className="space-y-6">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight flex items-center gap-2 font-['Plus_Jakarta_Sans',sans-serif]">
                  <ShieldCheck className="h-5 w-5 text-teal-400" />
                  Inference Output & Model Diagnostician
                </h2>
                <p className="text-xs text-slate-400">
                  Live verdict classifications, calibrated confidence scores, and reasoning traces.
                </p>
              </div>

              {executionMode && !isLoading && (
                <Badge variant="accent" size="sm">
                  Mode: {executionMode === 'compare' ? 'M1–M4 Comparison' : `Single Architecture (${method})`}
                </Badge>
              )}
            </div>

            <div className="relative min-h-[280px]">
              <AnimatePresence mode="popLayout" initial={false}>
                {/* 1. STATE: LOADING (Skeleton Shimmer Loaders) */}
                {isLoading && (
                  <motion.div
                    key="results-skeleton"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.25, ease: 'easeInOut' }}
                    className="space-y-6 w-full"
                  >
                  {executionMode === 'compare' && (
                    <div className="h-24 rounded-2xl border border-slate-800/80 bg-slate-900/60 p-6 flex items-center gap-4 elevation-card">
                      <Skeleton className="h-10 w-10 rounded-xl flex-shrink-0" />
                      <div className="space-y-2 flex-1">
                        <Skeleton className="h-4 w-48" />
                        <Skeleton className="h-3 w-80 max-w-full" />
                      </div>
                    </div>
                  )}

                  <div
                    className={`grid gap-4 ${
                      executionMode === 'compare'
                        ? 'grid-cols-1 sm:grid-cols-2'
                        : 'grid-cols-1 w-full'
                    }`}
                  >
                    {Array.from({ length: executionMode === 'compare' ? 4 : 1 }).map((_, i) => (
                      <SkeletonMethodCard key={i} />
                    ))}
                  </div>
                </motion.div>
              )}

              {/* 2. STATE: EMPTY STATE (Before Submission) */}
              {!isLoading && !singleResult && !compareResult && (
                <motion.div
                  key="results-empty"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.28, ease: 'easeInOut' }}
                  className="rounded-2xl border border-dashed border-slate-800 bg-slate-900/30 p-10 sm:p-14 text-center space-y-4 w-full"
                >
                  <div className="h-14 w-14 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-center mx-auto text-slate-500 shadow-inner">
                    <Inbox className="h-7 w-7 text-slate-400" />
                  </div>
                  <div className="space-y-1.5 max-w-md mx-auto">
                    <h3 className="text-base sm:text-lg font-bold text-slate-200 font-['Plus_Jakarta_Sans',sans-serif]">
                      Submit an email to see results
                    </h3>
                    <p className="text-xs text-slate-400 leading-relaxed">
                      Choose an architecture and click <strong className="text-slate-300">Classify</strong> for individual evaluation, or click <strong className="text-slate-300">Compare All (M1–M4)</strong> to trigger real-time cross-architecture disagreement detection.
                    </p>
                  </div>
                </motion.div>
            )}

            {/* 3. STATE: COMPARE ALL RESULTS */}
            {!isLoading && compareResult && (
              <motion.div
                key="results-compare"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.35, ease: 'easeOut' }}
                className="space-y-6 w-full"
              >
                {/* Consensus / Disagreement Banner */}
                {(() => {
                  const isDisagreement = compareResult.consensus.has_disagreement;
                  return (
                    <motion.div
                      initial={{ opacity: 0, y: -24 }}
                      animate={
                        isDisagreement
                          ? {
                              opacity: 1,
                              y: 0,
                              x: [0, -6, 6, -4, 4, -2, 2, 0],
                              borderColor: [
                                'rgba(245, 158, 11, 0.4)',
                                'rgba(245, 158, 11, 0.9)',
                                'rgba(245, 158, 11, 0.4)',
                              ],
                              boxShadow: [
                                '0 0 0 0 rgba(245, 158, 11, 0)',
                                '0 0 24px 2px rgba(245, 158, 11, 0.3)',
                                '0 0 0 0 rgba(245, 158, 11, 0)',
                              ],
                            }
                          : { opacity: 1, y: 0 }
                      }
                      transition={
                        isDisagreement
                          ? {
                              duration: 0.55,
                              ease: [0.25, 0.1, 0.25, 1],
                              times: [0, 0.2, 0.35, 0.5, 0.65, 0.8, 0.9, 1],
                            }
                          : { duration: 0.35, ease: [0.16, 1, 0.3, 1] }
                      }
                      className={`rounded-2xl border p-5 transition-colors elevation-card backdrop-blur-md ${
                        isDisagreement
                          ? 'border-amber-500/40 bg-gradient-to-r from-amber-950/30 via-slate-900/80 to-slate-900/60'
                          : 'border-teal-500/40 bg-gradient-to-r from-teal-950/30 via-slate-900/80 to-slate-900/60'
                      }`}
                    >
                      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                        <div className="flex items-start gap-3.5">
                          <div
                            className={`p-2 rounded-xl border flex-shrink-0 mt-0.5 ${
                              isDisagreement
                                ? 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                                : 'bg-teal-500/10 text-teal-400 border-teal-500/30'
                            }`}
                          >
                            {isDisagreement ? (
                              <AlertTriangle className="h-5 w-5" />
                            ) : (
                              <CheckCircle2 className="h-5 w-5" />
                            )}
                          </div>
                          <div className="space-y-1">
                            <h3 className="text-base sm:text-lg font-bold text-white tracking-tight">
                              {compareResult.consensus.summary_title}
                            </h3>
                            <p className="text-xs sm:text-sm text-slate-300 leading-relaxed max-w-2xl">
                              {compareResult.consensus.summary_detail}
                            </p>
                          </div>
                        </div>

                        <div className="flex flex-wrap items-center gap-2 self-end sm:self-center">
                          <Badge variant="phishing" size="sm" dot>
                            {compareResult.consensus.num_phishing} Phishing
                          </Badge>
                          <Badge variant="legitimate" size="sm" dot>
                            {compareResult.consensus.num_legitimate} Legitimate
                          </Badge>
                          <Badge
                            variant={isDisagreement ? 'injection' : 'accent'}
                            size="sm"
                          >
                            {isDisagreement
                              ? 'Disagreement'
                              : 'Agreement'}
                          </Badge>
                        </div>
                      </div>
                    </motion.div>
                  );
                })()}

                {/* 4-Card Result Grid */}
                <motion.div
                  variants={staggerContainer}
                  initial="hidden"
                  animate="visible"
                  className="grid grid-cols-1 sm:grid-cols-2 gap-4"
                >
                  {compareResult.results.map((res) => {
                    const methodCode = res.method.split(' ')[0]; // M1, M2, M3, M4
                    const styleMeta = compareResult.consensus.method_styles[methodCode];
                    return (
                      <motion.div key={res.method} variants={fadeInUp} className="h-full">
                        <MethodResultCard
                          result={res}
                          consensusNote={styleMeta?.note}
                          consensusStatusLabel={styleMeta?.status_label}
                          isOpenDetails={Boolean(openDetailsMap[res.method])}
                          onToggleDetails={() => toggleDetails(res.method)}
                          onCopySnippet={handleCopySnippet}
                          copiedKey={copiedKey}
                        />
                      </motion.div>
                    );
                  })}
                </motion.div>
              </motion.div>
            )}

            {/* 4. STATE: SINGLE METHOD RESULT (Stagger/FadeInUp) */}
            {!isLoading && singleResult && (
              <motion.div
                key="results-single"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.35, ease: 'easeOut' }}
                className="w-full"
              >
                <MethodResultCard
                  result={singleResult}
                  isOpenDetails={Boolean(openDetailsMap[singleResult.method])}
                  onToggleDetails={() => toggleDetails(singleResult.method)}
                  onCopySnippet={handleCopySnippet}
                  copiedKey={copiedKey}
                />
              </motion.div>
            )}
              </AnimatePresence>
            </div>
          </section>
        </div>
      </div>
    </motion.div>
  );
};

export default LiveTestPage;
