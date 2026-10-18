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
  Zap,
  ListTree,
  Edit3,
  Check,
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
import { Select, type SelectOption } from '../components/Select';
import { motion, AnimatePresence } from 'framer-motion';
import { fadeInUp, staggerContainer } from '../lib/motion';

const ARCHITECTURE_OPTIONS: SelectOption<string>[] = [
  {
    value: 'M1',
    label: 'M1: TF-IDF + Logistic Regression',
    description: 'Traditional ML Baseline (No LLM, zero injection risk)',
    badge: 'Classical ML',
  },
  {
    value: 'M2',
    label: 'M2: Zero-Shot LLM',
    description: 'Direct Prompting Baseline (Vulnerable to injection)',
    badge: 'Zero-Shot',
  },
  {
    value: 'M3',
    label: 'M3: RAG Combined (Single-Call)',
    description: 'Standard RAG (Direct context concatenation)',
    badge: 'Combined RAG',
  },
  {
    value: 'M4',
    label: 'M4: RAG Decoupled (IFSI Two-Stage)',
    description: 'IFSI Defense Architecture (Sanitizer + Isolated classifier)',
    badge: 'IFSI Decoupled',
  },
];

const MODEL_OPTIONS: SelectOption<string>[] = [
  {
    value: 'qwen2.5:0.5b',
    label: 'qwen2.5:0.5b (Default Local Model)',
    description: '0.5B parameters • Fast, lightweight inference',
    badge: 'Default',
  },
  {
    value: 'llama3.2:3b',
    label: 'llama3.2:3b (Pilot Local Model)',
    description: '3B parameters • High-capacity reasoning',
    badge: 'Pilot',
  },
];

const TOP_K_OPTIONS: SelectOption<number>[] = [
  {
    value: 1,
    label: 'k = 1',
    description: '1 exemplar retrieved from index',
  },
  {
    value: 3,
    label: 'k = 3',
    description: '3 exemplars (Recommended default)',
  },
  {
    value: 5,
    label: 'k = 5',
    description: '5 exemplars retrieved from index',
  },
];

const ATTACK_STYLE_OPTIONS: SelectOption<'unmarked' | 'marked'>[] = [
  {
    value: 'unmarked',
    label: 'Unmarked (Authentic Disguise)',
    description: 'Administrative disclaimer blended into body',
  },
  {
    value: 'marked',
    label: 'Marked (Bracketed Override)',
    description: 'Explicit [SYSTEM OVERRIDE] imperative command',
  },
];

const ATTACK_FAMILY_OPTIONS: SelectOption<string>[] = [
  {
    value: 'label_override',
    label: 'Label Override',
    description: 'Direct imperative command to output legitimate',
  },
  {
    value: 'false_authority',
    label: 'False Authority',
    description: 'IT Security Gateway impersonation notice',
  },
  {
    value: 'output_hijack',
    label: 'Output Hijack',
    description: 'JSON schema forced override format',
  },
  {
    value: 'rule_redefinition',
    label: 'Rule Redefinition',
    description: 'Policy exemption notice disclaimer',
  },
  {
    value: 'light_obfuscation',
    label: 'Light Obfuscation',
    description: 'Spaced text character evasion technique',
  },
];

const ATTACK_POSITION_OPTIONS: SelectOption<string>[] = [
  {
    value: 'body_start',
    label: 'Body Start',
    description: 'Prepend notice before email text',
  },
  {
    value: 'body_middle',
    label: 'Body Middle',
    description: 'Insert between email paragraphs',
  },
  {
    value: 'body_end',
    label: 'Body End',
    description: 'Append disclaimer after email content',
  },
];

interface CharacterCounterProps {
  count: number;
  suffix?: string;
  className?: string;
}

const CharacterCounter: React.FC<CharacterCounterProps> = ({
  count,
  suffix = 'characters',
  className = '',
}) => {
  return (
    <div
      className={`inline-flex items-center gap-1 font-mono text-slate-400 select-none ${className}`}
    >
      <motion.span
        key={count}
        initial={{ scale: 1.28, color: '#2dd4bf' }}
        animate={{ scale: 1, color: '#94a3b8' }}
        transition={{ duration: 0.32, ease: [0.16, 1, 0.3, 1] }}
        className="inline-block font-semibold tabular-nums will-change-transform"
      >
        {count.toLocaleString()}
      </motion.span>
      <span className="text-slate-500">{suffix}</span>
    </div>
  );
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

  // Result Card Density: 'simple' (default, readable in <3s) or 'detailed' (full diagnostician)
  const [viewDensity, setViewDensity] = useState<'simple' | 'detailed'>('simple');

  // Email Input Source Mode: 'preset' (benchmark presets) or 'custom' (custom fields)
  const [emailInputMode, setEmailInputMode] = useState<'preset' | 'custom'>('preset');

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
    setEmailInputMode('preset');
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

    const minLoadingPromise = new Promise((resolve) => setTimeout(resolve, 450));

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

      await minLoadingPromise;
      setSingleResult(res);
      // Auto-expand details for single result
      setOpenDetailsMap({ [method]: true });
    } catch (err: any) {
      await minLoadingPromise;
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

    const minLoadingPromise = new Promise((resolve) => setTimeout(resolve, 500));

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

      await minLoadingPromise;
      setCompareResult(res);
      // Default: collapse detail drawers in 4-column compare grid to keep cards compact
      setOpenDetailsMap({});
    } catch (err: any) {
      await minLoadingPromise;
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

              {/* =========================================================================
                  SUBSECTION 1: Choose a method (Architecture + Model + k)
                  ========================================================================= */}
              <section aria-labelledby="step-1-heading" className="space-y-4">
                <div className="flex items-center gap-3">
                  <span className="flex-shrink-0 w-6 h-6 rounded-full bg-teal-500/15 text-teal-300 border border-teal-500/30 text-xs font-bold font-mono flex items-center justify-center shadow-sm">
                    1
                  </span>
                  <div>
                    <h3 id="step-1-heading" className="text-sm font-bold text-white tracking-tight flex items-center gap-2">
                      <span>Choose a method</span>
                      {executionMode === 'compare' && (
                        <span className="text-[10px] px-1.5 py-0.2 rounded bg-teal-500/10 text-teal-300 border border-teal-500/20 font-mono">
                          M1–M4 in Compare Mode
                        </span>
                      )}
                    </h3>
                    <p className="text-[11px] text-slate-400">
                      Configure target classifier architecture, local model runtime, and exemplar depth.
                    </p>
                  </div>
                </div>

                <div className="space-y-3.5 pl-9">
                  {/* Target Architecture Custom Select */}
                  <Select
                    id="architecture-select"
                    label="Target Architecture (Single Mode)"
                    options={ARCHITECTURE_OPTIONS}
                    value={method}
                    onChange={(val) => setMethod(val as any)}
                    ariaLabel="Target Architecture"
                  />

                  {/* Local LLM & RAG k Side-by-Side Custom Selects */}
                  <div className="grid grid-cols-1 sm:grid-cols-12 gap-3 items-end">
                    <div className="sm:col-span-7">
                      <Select
                        id="model-select"
                        label="Local LLM Runtime"
                        options={MODEL_OPTIONS}
                        value={model}
                        onChange={(val) => setModel(val as string)}
                        ariaLabel="Local LLM Model"
                      />
                    </div>
                    <div className="sm:col-span-5">
                      <Select
                        id="topk-select"
                        label="RAG Exemplars"
                        options={TOP_K_OPTIONS}
                        value={topK}
                        onChange={(val) => setTopK(val as number)}
                        ariaLabel="RAG Exemplar Count k"
                      />
                    </div>
                  </div>
                </div>
              </section>

              {/* Subtle Section Divider */}
              <div className="border-t border-slate-800/80 my-2" />

              {/* =========================================================================
                  SUBSECTION 2: Provide the email (Preset Selector OR Custom Fields)
                  ========================================================================= */}
              <section aria-labelledby="step-2-heading" className="space-y-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <span className="flex-shrink-0 w-6 h-6 rounded-full bg-teal-500/15 text-teal-300 border border-teal-500/30 text-xs font-bold font-mono flex items-center justify-center shadow-sm">
                      2
                    </span>
                    <div>
                      <h3 id="step-2-heading" className="text-sm font-bold text-white tracking-tight">
                        Provide the email
                      </h3>
                      <p className="text-[11px] text-slate-400">
                        Choose a benchmark preset or write custom email contents.
                      </p>
                    </div>
                  </div>

                  {/* Preset Selector vs Custom Fields Toggle Pill */}
                  <div
                    role="tablist"
                    aria-label="Email Input Source Mode"
                    className="inline-flex p-1 rounded-xl bg-slate-900 border border-slate-800/90 shadow-inner self-start sm:self-auto"
                  >
                    <button
                      type="button"
                      role="tab"
                      id="email-mode-preset"
                      aria-selected={emailInputMode === 'preset'}
                      onClick={() => setEmailInputMode('preset')}
                      className={`relative px-2.5 py-1 text-xs font-semibold rounded-lg transition-colors duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 ${
                        emailInputMode === 'preset'
                          ? 'text-white'
                          : 'text-slate-400 hover:text-slate-200'
                      }`}
                    >
                      {emailInputMode === 'preset' && (
                        <motion.span
                          layoutId="active-email-mode-pill"
                          className="absolute inset-0 rounded-lg bg-teal-500/20 border border-teal-500/40 shadow-sm"
                          transition={{ type: 'spring', stiffness: 500, damping: 35 }}
                        />
                      )}
                      <span className="relative z-10 flex items-center gap-1.5">
                        <Sparkles className="h-3.5 w-3.5 text-teal-400" />
                        Presets
                      </span>
                    </button>

                    <button
                      type="button"
                      role="tab"
                      id="email-mode-custom"
                      aria-selected={emailInputMode === 'custom'}
                      onClick={() => setEmailInputMode('custom')}
                      className={`relative px-2.5 py-1 text-xs font-semibold rounded-lg transition-colors duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 ${
                        emailInputMode === 'custom'
                          ? 'text-white'
                          : 'text-slate-400 hover:text-slate-200'
                      }`}
                    >
                      {emailInputMode === 'custom' && (
                        <motion.span
                          layoutId="active-email-mode-pill"
                          className="absolute inset-0 rounded-lg bg-teal-500/20 border border-teal-500/40 shadow-sm"
                          transition={{ type: 'spring', stiffness: 500, damping: 35 }}
                        />
                      )}
                      <span className="relative z-10 flex items-center gap-1.5">
                        <Edit3 className="h-3.5 w-3.5 text-teal-400" />
                        Custom Fields
                      </span>
                    </button>
                  </div>
                </div>

                <motion.div layout className="pl-9 space-y-3.5">
                  <AnimatePresence mode="wait" initial={false}>
                    {emailInputMode === 'preset' ? (
                      <motion.div
                        key="email-source-preset"
                        initial={{ opacity: 0, y: 8, filter: 'blur(3px)' }}
                        animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
                        exit={{
                          opacity: 0,
                          y: -8,
                          filter: 'blur(3px)',
                          transition: { duration: 0.16, ease: 'easeIn' },
                        }}
                        transition={{ duration: 0.26, ease: [0.16, 1, 0.3, 1] }}
                        className="space-y-3"
                      >
                        {/* Preset Chips Grid */}
                        <div className="space-y-1.5">
                          <div className="flex items-center justify-between">
                            <label className="block text-xs font-semibold text-slate-300">
                              Curated Benchmark Presets
                            </label>
                            <span className="text-[10px] text-slate-400 font-mono">
                              Click to populate
                            </span>
                          </div>
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                            {Object.keys(presets).map((key) => {
                              const sample = presets[key];
                              const isSelected = selectedPresetKey === key;
                              const label = key.split('(')[0].trim();
                              return (
                                <button
                                  key={key}
                                  type="button"
                                  onClick={() => handleSelectPreset(key)}
                                  className={`px-3 py-2 rounded-xl text-left transition-all duration-150 border flex items-center justify-between gap-2 active:scale-[0.98] ${
                                    isSelected
                                      ? 'bg-teal-500/15 border-teal-500/50 text-teal-200 shadow-sm ring-1 ring-teal-500/20 font-semibold'
                                      : 'bg-slate-950/80 border-slate-800 text-slate-300 hover:bg-slate-900 hover:border-slate-700'
                                  }`}
                                >
                                  <div className="min-w-0">
                                    <div className="text-xs truncate font-medium">{label}</div>
                                    <div className="text-[10px] text-slate-400 font-mono mt-0.5">
                                      {sample.condition}
                                    </div>
                                  </div>
                                  {isSelected && (
                                    <span className="flex-shrink-0 text-teal-400">
                                      <Check className="h-3.5 w-3.5" />
                                    </span>
                                  )}
                                </button>
                              );
                            })}
                          </div>
                        </div>

                        {/* Active Preset Metadata Status Box */}
                        {selectedSample && (
                          <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-2.5 flex flex-wrap items-center justify-between gap-2">
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
                            <CharacterCounter
                              count={emailText.length}
                              suffix="chars"
                              className="text-[10px]"
                            />
                          </div>
                        )}

                        {/* Email Body Preview / Editable Area */}
                        <div className="space-y-1.5">
                          <div className="flex items-center justify-between">
                            <label className="text-xs font-semibold text-slate-300">
                              Email Body Text
                            </label>
                            <CharacterCounter
                              count={emailText.length}
                              suffix="characters"
                              className="text-[11px]"
                            />
                          </div>
                          <textarea
                            rows={5}
                            value={emailText}
                            onChange={(e) => setEmailText(e.target.value)}
                            placeholder="Select a preset above to load email body..."
                            className="w-full rounded-xl bg-slate-950 border border-slate-800 p-3 text-xs sm:text-sm text-slate-200 font-mono leading-relaxed focus:outline-none focus:border-teal-500 focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 transition-colors resize-y"
                          />
                        </div>
                      </motion.div>
                    ) : (
                      <motion.div
                        key="email-source-custom"
                        initial={{ opacity: 0, y: 8, filter: 'blur(3px)' }}
                        animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
                        exit={{
                          opacity: 0,
                          y: -8,
                          filter: 'blur(3px)',
                          transition: { duration: 0.16, ease: 'easeIn' },
                        }}
                        transition={{ duration: 0.26, ease: [0.16, 1, 0.3, 1] }}
                        className="space-y-3.5"
                      >
                        {/* Custom Subject & Sender Fields */}
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
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
                            <CharacterCounter
                              count={emailText.length}
                              suffix="characters"
                              className="text-[11px]"
                            />
                          </div>
                          <textarea
                            rows={6}
                            value={emailText}
                            onChange={(e) => setEmailText(e.target.value)}
                            placeholder="Paste raw email body here, or draft custom content..."
                            className="w-full rounded-xl bg-slate-950 border border-slate-800 p-4 text-xs sm:text-sm text-slate-200 font-mono leading-relaxed focus:outline-none focus:border-teal-500 focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 transition-colors resize-y"
                          />
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </motion.div>
              </section>

              {/* Subtle Section Divider */}
              <div className="border-t border-slate-800/80 my-2" />

              {/* =========================================================================
                  SUBSECTION 3: Optional: test injection resistance (existing toggle)
                  ========================================================================= */}
              <section aria-labelledby="step-3-heading" className="space-y-4">
                <div className="flex items-center justify-between gap-4">
                  <div className="flex items-center gap-3">
                    <span className="flex-shrink-0 w-6 h-6 rounded-full bg-amber-500/15 text-amber-300 border border-amber-500/30 text-xs font-bold font-mono flex items-center justify-center shadow-sm">
                      3
                    </span>
                    <div>
                      <div className="flex items-center gap-2">
                        <FlaskConical className="h-4 w-4 text-amber-400 flex-shrink-0" />
                        <h3 id="step-3-heading" className="text-sm font-bold text-white tracking-tight">
                          Optional: test injection resistance
                        </h3>
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
                      initial={{ height: 0, opacity: 0, scale: 0.98 }}
                      animate={{
                        height: 'auto',
                        opacity: 1,
                        scale: 1,
                        transitionEnd: { overflow: 'visible' },
                      }}
                      exit={{
                        height: 0,
                        opacity: 0,
                        scale: 0.98,
                        overflow: 'hidden',
                      }}
                      transition={{
                        height: { duration: 0.32, ease: [0.16, 1, 0.3, 1] },
                        opacity: { duration: 0.26, ease: 'easeInOut' },
                        scale: { duration: 0.26, ease: 'easeOut' },
                      }}
                      className="pl-9 overflow-hidden"
                    >
                      <div className="rounded-xl border border-amber-500/30 bg-amber-500/5 p-3.5 space-y-3">
                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                          <Select
                            id="attack-style-select"
                            label="Injection Style"
                            size="sm"
                            options={ATTACK_STYLE_OPTIONS}
                            value={attackStyle}
                            onChange={(val) => setAttackStyle(val as any)}
                            ariaLabel="Injection Style"
                          />

                          <Select
                            id="attack-family-select"
                            label="Attack Family"
                            size="sm"
                            options={ATTACK_FAMILY_OPTIONS}
                            value={attackFamily}
                            onChange={(val) => setAttackFamily(val as string)}
                            ariaLabel="Attack Family"
                          />

                          <Select
                            id="attack-position-select"
                            label="Payload Placement"
                            size="sm"
                            options={ATTACK_POSITION_OPTIONS}
                            value={attackPosition}
                            onChange={(val) => setAttackPosition(val as string)}
                            ariaLabel="Payload Placement"
                          />
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
              </section>

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
                    className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-medium text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 transition-all duration-150 hover:scale-[1.02] hover:brightness-105 active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <RotateCcw className="h-3.5 w-3.5" />
                    <span>Reset</span>
                  </button>
                </div>

                <div className="flex flex-wrap items-center gap-2.5">
                  {/* Compare All Button with smooth rotational icon morph */}
                  <button
                    type="button"
                    id="compare-all-btn"
                    onClick={handleRunCompare}
                    disabled={isLoading}
                    className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-700 bg-slate-800/90 px-3.5 py-2.5 text-xs sm:text-sm font-semibold text-slate-100 elevation-card hover:elevation-hover hover:bg-slate-700 hover:border-slate-600 transition-all duration-150 hover:scale-[1.02] hover:brightness-110 active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 disabled:opacity-60 disabled:cursor-not-allowed min-w-[165px]"
                  >
                    <div className="relative w-4 h-4 flex items-center justify-center flex-shrink-0">
                      <AnimatePresence mode="wait" initial={false}>
                        {isLoading && executionMode === 'compare' ? (
                          <motion.span
                            key="spinner-compare"
                            initial={{ opacity: 0, scale: 0.5, rotate: -90 }}
                            animate={{ opacity: 1, scale: 1, rotate: 0 }}
                            exit={{ opacity: 0, scale: 0.5, rotate: 90 }}
                            transition={{ duration: 0.2, ease: 'easeOut' }}
                            className="absolute inset-0 flex items-center justify-center text-teal-400"
                          >
                            <Loader2 className="h-4 w-4 animate-spin" />
                          </motion.span>
                        ) : (
                          <motion.span
                            key="compare-icon"
                            initial={{ opacity: 0, scale: 0.5, rotate: -90 }}
                            animate={{ opacity: 1, scale: 1, rotate: 0 }}
                            exit={{ opacity: 0, scale: 0.5, rotate: 90 }}
                            transition={{ duration: 0.2, ease: 'easeOut' }}
                            className="absolute inset-0 flex items-center justify-center text-teal-400"
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
                            ? 'Classifying…'
                            : 'Compare All (M1–M4)'}
                        </motion.span>
                      </AnimatePresence>
                    </div>
                  </button>

                  {/* Single Method Classify Button with smooth rotational icon morph */}
                  <button
                    type="button"
                    id="classify-single-btn"
                    onClick={handleRunSingle}
                    disabled={isLoading}
                    className="inline-flex items-center justify-center gap-2 rounded-xl bg-teal-500 px-4 py-2.5 text-xs sm:text-sm font-bold text-slate-950 elevation-card hover:elevation-hover hover:bg-teal-400 transition-all duration-150 hover:scale-[1.02] hover:brightness-110 active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 disabled:opacity-60 disabled:cursor-not-allowed min-w-[140px]"
                  >
                    <div className="relative w-4 h-4 flex items-center justify-center flex-shrink-0">
                      <AnimatePresence mode="wait" initial={false}>
                        {isLoading && executionMode === 'single' ? (
                          <motion.span
                            key="spinner-single"
                            initial={{ opacity: 0, scale: 0.5, rotate: -90 }}
                            animate={{ opacity: 1, scale: 1, rotate: 0 }}
                            exit={{ opacity: 0, scale: 0.5, rotate: 90 }}
                            transition={{ duration: 0.2, ease: 'easeOut' }}
                            className="absolute inset-0 flex items-center justify-center text-slate-950"
                          >
                            <Loader2 className="h-4 w-4 animate-spin text-slate-950" />
                          </motion.span>
                        ) : (
                          <motion.span
                            key="play-icon"
                            initial={{ opacity: 0, scale: 0.5, rotate: -90 }}
                            animate={{ opacity: 1, scale: 1, rotate: 0 }}
                            exit={{ opacity: 0, scale: 0.5, rotate: 90 }}
                            transition={{ duration: 0.2, ease: 'easeOut' }}
                            className="absolute inset-0 flex items-center justify-center text-slate-950"
                          >
                            <Play className="h-4 w-4 fill-current" />
                          </motion.span>
                        )}
                      </AnimatePresence>
                    </div>
                    <div className="relative min-w-[70px] text-center">
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
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div className="space-y-0.5">
                <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight flex items-center gap-2 font-['Plus_Jakarta_Sans',sans-serif]">
                  <ShieldCheck className="h-5 w-5 text-teal-400" />
                  Inference Output & Model Diagnostician
                </h2>
                <p className="text-xs text-slate-400">
                  Live verdict classifications, calibrated confidence scores, and reasoning traces.
                </p>
              </div>

              {/* View Density Segmented Control (Simple vs Detailed) & Execution Mode */}
              <div className="flex items-center gap-2.5 self-start sm:self-auto">
                {executionMode && !isLoading && (
                  <Badge variant="accent" size="sm" className="hidden sm:inline-flex">
                    {executionMode === 'compare' ? 'M1–M4' : method}
                  </Badge>
                )}

                {/* Pill-Style Segmented Control with animated sliding active state */}
                <div
                  role="tablist"
                  aria-label="Result detail view density"
                  className="inline-flex p-1 rounded-xl bg-slate-900 border border-slate-800/90 shadow-inner"
                >
                  <button
                    type="button"
                    role="tab"
                    id="view-toggle-simple"
                    aria-selected={viewDensity === 'simple'}
                    onClick={() => setViewDensity('simple')}
                    className={`relative px-3 py-1 text-xs font-semibold rounded-lg transition-colors duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 ${
                      viewDensity === 'simple'
                        ? 'text-white'
                        : 'text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    {viewDensity === 'simple' && (
                      <motion.span
                        layoutId="active-view-density-pill"
                        className="absolute inset-0 rounded-lg bg-teal-500/20 border border-teal-500/40 shadow-sm"
                        transition={{ type: 'spring', stiffness: 500, damping: 35 }}
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
                    aria-selected={viewDensity === 'detailed'}
                    onClick={() => setViewDensity('detailed')}
                    className={`relative px-3 py-1 text-xs font-semibold rounded-lg transition-colors duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 ${
                      viewDensity === 'detailed'
                        ? 'text-white'
                        : 'text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    {viewDensity === 'detailed' && (
                      <motion.span
                        layoutId="active-view-density-pill"
                        className="absolute inset-0 rounded-lg bg-teal-500/20 border border-teal-500/40 shadow-sm"
                        transition={{ type: 'spring', stiffness: 500, damping: 35 }}
                      />
                    )}
                    <span className="relative z-10 flex items-center gap-1.5">
                      <ListTree className="h-3.5 w-3.5 text-teal-400" />
                      Detailed
                    </span>
                  </button>
                </div>
              </div>
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

                {/* 4-Card Result Grid: Staggers cards after consensus banner slides down */}
                <motion.div
                  variants={staggerContainer}
                  custom={0.28}
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
                          viewDensity={viewDensity}
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
                variants={fadeInUp}
                initial="hidden"
                animate="visible"
                exit="exit"
                className="w-full"
              >
                <MethodResultCard
                  result={singleResult}
                  isOpenDetails={Boolean(openDetailsMap[singleResult.method])}
                  onToggleDetails={() => toggleDetails(singleResult.method)}
                  onCopySnippet={handleCopySnippet}
                  copiedKey={copiedKey}
                  viewDensity={viewDensity}
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
