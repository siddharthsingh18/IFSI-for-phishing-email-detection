import React, { useEffect, useState, useRef } from 'react';
import { Link } from 'react-router-dom';
import {
  ArrowRight,
  Shield,
  Cpu,
  Bot,
  Layers,
  ShieldCheck,
  AlertTriangle,
  Sparkles,
  BookOpen,
  Database,
  Scale,
  AlertCircle,
  ShieldAlert,
  TrendingDown,
  ChevronDown,
} from 'lucide-react';
import { apiClient, type BenchmarkSummary } from '../api/client';
import { Card } from '../components/Card';
import { OfflineFallbackBanner } from '../components/OfflineFallbackBanner';
import { Badge } from '../components/Badge';
import { SkeletonCard } from '../components/Skeleton';
import { HeroNetworkIllustration } from '../components/HeroNetworkIllustration';
import { HeroFloatingRecallCard } from '../components/HeroFloatingRecallCard';
import { MagneticButton } from '../components/MagneticButton';
import { motion, AnimatePresence, useScroll, useTransform, useReducedMotion } from 'framer-motion';
import { usePrefersReducedMotion } from '../hooks/usePrefersReducedMotion';
import { fadeInUp, staggerContainer, scaleIn } from '../lib/motion';

export const LandingPage: React.FC = () => {
  const [summary, setSummary] = useState<BenchmarkSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [isUsingFallback, setIsUsingFallback] = useState(false);
  const [expandedMethodology, setExpandedMethodology] = useState<Record<string, boolean>>({});
  const [expandedLimitations, setExpandedLimitations] = useState<Record<string, boolean>>({});

  const toggleMethodology = (id: string) => {
    setExpandedMethodology((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const toggleLimitation = (id: string) => {
    setExpandedLimitations((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  useEffect(() => {
    let mounted = true;
    apiClient
      .getBenchmarkSummary()
      .then((data) => {
        if (!mounted) return;
        setSummary(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Failed to load summary stats:', err);
        if (!mounted) return;
        setIsUsingFallback(true);
        setLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, []);

  // Extract real numbers dynamically for key finding callout
  const m3UnmarkedCell = summary?.cells?.['M3_unmarked']?.metrics;
  const m4UnmarkedCell = summary?.cells?.['M4_unmarked']?.metrics;
  const m1CleanCell = summary?.cells?.['M1_clean']?.metrics;

  const m3UnmarkedRecall = m3UnmarkedCell ? (m3UnmarkedCell.recall * 100).toFixed(1) : '21.1';
  const m3EvasionRate = m3UnmarkedCell ? ((1 - m3UnmarkedCell.recall) * 100).toFixed(1) : '78.9';
  const m4UnmarkedRecall = m4UnmarkedCell ? (m4UnmarkedCell.recall * 100).toFixed(1) : '96.1';
  const m4UnmarkedFpr = m4UnmarkedCell ? (m4UnmarkedCell.fpr * 100).toFixed(1) : '72.1';
  const m1CleanAccuracy = m1CleanCell ? (m1CleanCell.accuracy * 100).toFixed(1) : '98.5';

  // Reduced motion preference check
  const framerReducedMotion = useReducedMotion();
  const prefersReducedMotion = usePrefersReducedMotion();
  const shouldReduceMotion = prefersReducedMotion || Boolean(framerReducedMotion);

  // Hero Parallax
  const heroSectionRef = useRef<HTMLElement>(null);
  const { scrollYProgress: heroScrollProgress } = useScroll({
    target: heroSectionRef,
    offset: ['start start', 'end start'],
  });
  const heroIllustrationY = useTransform(
    heroScrollProgress,
    [0, 1],
    shouldReduceMotion ? [0, 0] : [0, 60]
  );

  // Methods section scroll reveals
  const methodsSectionRef = useRef<HTMLElement>(null);
  const { scrollYProgress: methodsScrollProgress } = useScroll({
    target: methodsSectionRef,
    offset: ['start end', 'center center'],
  });

  const methodsHeadingOpacity = useTransform(
    methodsScrollProgress,
    [0, 0.4],
    shouldReduceMotion ? [1, 1] : [0, 1]
  );
  const methodsHeadingY = useTransform(
    methodsScrollProgress,
    [0, 0.4],
    shouldReduceMotion ? [0, 0] : [25, 0]
  );

  const m1Opacity = useTransform(
    methodsScrollProgress,
    [0.05, 0.55],
    shouldReduceMotion ? [1, 1] : [0, 1]
  );
  const m1Y = useTransform(
    methodsScrollProgress,
    [0.05, 0.55],
    shouldReduceMotion ? [0, 0] : [35, 0]
  );

  const m2Opacity = useTransform(
    methodsScrollProgress,
    [0.15, 0.65],
    shouldReduceMotion ? [1, 1] : [0, 1]
  );
  const m2Y = useTransform(
    methodsScrollProgress,
    [0.15, 0.65],
    shouldReduceMotion ? [0, 0] : [35, 0]
  );

  const m3Opacity = useTransform(
    methodsScrollProgress,
    [0.25, 0.75],
    shouldReduceMotion ? [1, 1] : [0, 1]
  );
  const m3Y = useTransform(
    methodsScrollProgress,
    [0.25, 0.75],
    shouldReduceMotion ? [0, 0] : [35, 0]
  );

  const m4Opacity = useTransform(
    methodsScrollProgress,
    [0.35, 0.85],
    shouldReduceMotion ? [1, 1] : [0, 1]
  );
  const m4Y = useTransform(
    methodsScrollProgress,
    [0.35, 0.85],
    shouldReduceMotion ? [0, 0] : [35, 0]
  );

  // Key Finding scroll reveals
  const keyFindingSectionRef = useRef<HTMLElement>(null);
  const { scrollYProgress: keyFindingScrollProgress } = useScroll({
    target: keyFindingSectionRef,
    offset: ['start end', 'center center'],
  });

  const keyFindingHeadingOpacity = useTransform(
    keyFindingScrollProgress,
    [0, 0.35],
    shouldReduceMotion ? [1, 1] : [0, 1]
  );
  const keyFindingHeadingY = useTransform(
    keyFindingScrollProgress,
    [0, 0.35],
    shouldReduceMotion ? [0, 0] : [20, 0]
  );

  const keyFindingCardOpacity = useTransform(
    keyFindingScrollProgress,
    [0.08, 0.75],
    shouldReduceMotion ? [1, 1] : [0, 1]
  );
  const keyFindingCardY = useTransform(
    keyFindingScrollProgress,
    [0.08, 0.75],
    shouldReduceMotion ? [0, 0] : [40, 0]
  );
  const keyFindingCardScale = useTransform(
    keyFindingScrollProgress,
    [0.08, 0.75],
    shouldReduceMotion ? [1, 1] : [0.97, 1]
  );

  const keyFindingBorder = useTransform(
    keyFindingScrollProgress,
    [0.1, 0.6, 1],
    shouldReduceMotion
      ? ['rgba(20, 184, 166, 0.4)', 'rgba(20, 184, 166, 0.4)', 'rgba(20, 184, 166, 0.4)']
      : ['rgba(20, 184, 166, 0.2)', 'rgba(45, 212, 191, 0.8)', 'rgba(20, 184, 166, 0.45)']
  );

  const keyFindingShadow = useTransform(
    keyFindingScrollProgress,
    [0.1, 0.6, 1],
    shouldReduceMotion
      ? ['none', 'none', 'none']
      : [
          '0 0 0 0 rgba(20, 184, 166, 0)',
          '0 0 25px 3px rgba(20, 184, 166, 0.35), 0 0 0 1px rgba(45, 212, 191, 0.5)',
          '0 0 12px 1px rgba(20, 184, 166, 0.2)',
        ]
  );

  const keyFindingStatsOpacity = useTransform(
    keyFindingScrollProgress,
    [0.25, 0.85],
    shouldReduceMotion ? [1, 1] : [0, 1]
  );
  const keyFindingStatsX = useTransform(
    keyFindingScrollProgress,
    [0.25, 0.85],
    shouldReduceMotion ? [0, 0] : [25, 0]
  );
  const keyFindingStatsScale = useTransform(
    keyFindingScrollProgress,
    [0.25, 0.85],
    shouldReduceMotion ? [1, 1] : [0.95, 1]
  );

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1, transition: { duration: 0.2 } }}
      exit={{ opacity: 0, y: -8, transition: { duration: 0.16 } }}
      className="space-y-16 pb-16 max-w-7xl mx-auto"
    >
      {/* Fallback Banner */}
      {isUsingFallback && (
        <OfflineFallbackBanner
          onRetry={() => window.location.reload()}
        />
      )}

      {/* =========================================================================
          SECTION 1: HERO
          ========================================================================= */}
      <motion.section
        ref={heroSectionRef}
        variants={staggerContainer}
        initial="hidden"
        animate="visible"
        className="pt-6 sm:pt-10 pb-6 relative overflow-visible"
      >
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-10 items-center">
          {/* Left Column: Headline and Call-to-Actions */}
          <motion.div variants={fadeInUp} className="lg:col-span-5 xl:col-span-5 space-y-6">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider bg-teal-950/80 text-teal-400 border border-teal-800/60 shadow-sm backdrop-blur-sm">
              <span className="h-1.5 w-1.5 rounded-full bg-teal-400 animate-pulse" />
              <span>Adversarial AI Benchmark</span>
            </div>

            <div className="space-y-3">
              <h1 className="text-3xl sm:text-5xl font-black text-white tracking-tight leading-[1.08] font-['Plus_Jakarta_Sans',sans-serif]">
                Evaluating Indirect Prompt Injections on{' '}
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-teal-400 via-emerald-300 to-cyan-400">
                  LLM Phishing Classifiers
                </span>
              </h1>
              <p className="text-lg sm:text-2xl text-slate-300 font-normal tracking-tight">
                <span className="text-slate-400 font-light">By </span>
                <span className="text-slate-100 font-medium">Siddharth Singh</span>
                <span className="text-slate-400 font-light"> &amp; </span>
                <span className="text-slate-100 font-medium">Sanchit Kukreja</span>
              </p>
            </div>

            <p className="text-sm sm:text-base text-slate-300 leading-relaxed font-normal">
              Empirical evaluation showing how monolithic RAG-combined detection (M3) collapses under natural prompt injection,
              while decoupled two-stage inference (M4) restores attack resilience at an operational false-alarm tax.
            </p>

            <motion.div
              variants={fadeInUp}
              className="flex flex-wrap items-center gap-3 pt-2"
            >
              <MagneticButton
                strength={0.2}
                className="inline-flex"
              >
                <Link
                  to="/test"
                  className="inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl font-bold text-xs sm:text-sm text-slate-950 bg-teal-400 hover:bg-teal-300 hover:scale-[1.02] active:scale-[0.98] shadow-lg shadow-teal-500/20 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 transition-all duration-150"
                >
                  <Shield className="h-4 w-4" />
                  <span>Test an Email</span>
                  <ArrowRight className="h-3.5 w-3.5" />
                </Link>
              </MagneticButton>

              <MagneticButton
                strength={0.2}
                className="inline-flex"
              >
                <Link
                  to="/dashboard"
                  className="inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl font-semibold text-xs sm:text-sm text-slate-200 bg-slate-900 border border-slate-700 hover:bg-slate-800 hover:text-white hover:border-slate-600 hover:scale-[1.02] active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 transition-all duration-150"
                >
                  <span>View Benchmark Dashboard</span>
                </Link>
              </MagneticButton>
            </motion.div>
          </motion.div>

          {/* Right Column: Floating Contrast Recall Card */}
          <div className="lg:col-span-7 xl:col-span-7 relative w-full h-full min-w-0 flex flex-col items-center justify-center">
            <div className="relative w-full flex items-center justify-center">
              <motion.div
                style={{ y: heroIllustrationY }}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.22, ease: 'easeOut' }}
                className="w-full h-full flex items-center justify-center will-change-transform"
              >
                <HeroNetworkIllustration />
              </motion.div>

              <motion.div
                variants={scaleIn}
                initial="hidden"
                animate="visible"
                transition={{ delay: 0.25, duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
                className="absolute top-2 right-1 sm:top-4 sm:right-4 lg:top-4 lg:right-6 z-20"
              >
                <HeroFloatingRecallCard summary={summary} loading={loading} />
              </motion.div>
            </div>
          </div>
        </div>
      </motion.section>

      {/* =========================================================================
          SECTION 2: THE PROBLEM
          ========================================================================= */}
      <section className="space-y-6">
        <div className="space-y-1">
          <div className="flex items-center gap-2 text-teal-400 text-xs font-semibold uppercase tracking-wider">
            <AlertTriangle className="h-4 w-4" />
            Threat Model
          </div>
          <h2 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">The Problem</h2>
        </div>

        <Card variant="default" padding="lg">
          <div className="space-y-5">
            <p className="text-base sm:text-xl font-medium text-slate-200 leading-snug">
              Indirect prompt injections trick monolithic LLM classifiers into whitelisting malicious phishing emails.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5 pt-1">
              {/* Stat Chip 1: Evasion Rate */}
              <div className="flex items-center gap-3.5 p-4 rounded-xl border border-rose-500/30 bg-rose-500/10 backdrop-blur-sm">
                <div className="p-2.5 rounded-lg bg-rose-500/20 text-rose-400 flex-shrink-0">
                  <ShieldAlert className="h-5 w-5" />
                </div>
                <div>
                  <div className="text-2xl sm:text-3xl font-black text-rose-400 tracking-tight leading-none">
                    {m3EvasionRate}%
                  </div>
                  <div className="text-xs sm:text-sm font-semibold text-slate-300 mt-1">
                    Standard RAG Evasion
                  </div>
                </div>
              </div>

              {/* Stat Chip 2: What Causes It (Monolithic Catch Collapse) */}
              <div className="flex items-center gap-3.5 p-4 rounded-xl border border-amber-500/30 bg-amber-500/10 backdrop-blur-sm">
                <div className="p-2.5 rounded-lg bg-amber-500/20 text-amber-400 flex-shrink-0">
                  <TrendingDown className="h-5 w-5" />
                </div>
                <div>
                  <div className="text-2xl sm:text-3xl font-black text-amber-400 tracking-tight leading-none">
                    {m3UnmarkedRecall}%
                  </div>
                  <div className="text-xs sm:text-sm font-semibold text-slate-300 mt-1">
                    Monolithic Catch Rate
                  </div>
                </div>
              </div>

              {/* Stat Chip 3: The Fix's Tradeoff */}
              <div className="flex items-center gap-3.5 p-4 rounded-xl border border-teal-500/30 bg-teal-500/10 backdrop-blur-sm">
                <div className="p-2.5 rounded-lg bg-teal-500/20 text-teal-400 flex-shrink-0">
                  <Scale className="h-5 w-5" />
                </div>
                <div>
                  <div className="text-2xl sm:text-3xl font-black text-teal-400 tracking-tight leading-none">
                    {m4UnmarkedFpr}%
                  </div>
                  <div className="text-xs sm:text-sm font-semibold text-slate-300 mt-1">
                    Operational False-Alarm Tax
                  </div>
                </div>
              </div>
            </div>
          </div>
        </Card>
      </section>

      {/* =========================================================================
          SECTION 3: THE APPROACH
          ========================================================================= */}
      <section id="methods-section" ref={methodsSectionRef} className="space-y-6 scroll-mt-24">
        <motion.div
          style={{ opacity: methodsHeadingOpacity, y: methodsHeadingY }}
          className="space-y-1"
        >
          <div className="flex items-center gap-2 text-teal-400 text-xs font-semibold uppercase tracking-wider">
            <Cpu className="h-4 w-4" />
            System Architecture
          </div>
          <h2 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">The Approach</h2>
          <p className="text-xs sm:text-sm text-slate-400">
            Evaluating four distinct classifier paradigms to isolate how prompt injection impacts monolithic vs. decoupled reasoning.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* M1 */}
          <motion.div style={{ opacity: m1Opacity, y: m1Y }} className="h-full">
            <Card variant="default" padding="md" className="h-full flex flex-col justify-between">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <Badge variant="neutral" size="sm">Baseline</Badge>
                  <Cpu className="h-4 w-4 text-slate-400" />
                </div>
                <h3 className="text-base font-bold text-white tracking-tight font-['Plus_Jakarta_Sans',sans-serif]">
                  M1: TF-IDF + LogReg
                </h3>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Classical linear model using bag-of-words tokens. Structurally immune to semantic prompt injections ({m1CleanAccuracy}% accuracy), but cannot reason over novel spear-phishing.
                </p>
              </div>
              <div className="pt-3 border-t border-slate-800 text-[11px] font-mono text-teal-400">
                Linear Structural Immunity
              </div>
            </Card>
          </motion.div>

          {/* M2 */}
          <motion.div style={{ opacity: m2Opacity, y: m2Y }} className="h-full">
            <Card variant="default" padding="md" className="h-full flex flex-col justify-between">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <Badge variant="neutral" size="sm">Zero-Shot</Badge>
                  <Bot className="h-4 w-4 text-cyan-400" />
                </div>
                <h3 className="text-base font-bold text-white tracking-tight font-['Plus_Jakarta_Sans',sans-serif]">
                  M2: Zero-Shot LLM
                </h3>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Direct instruction prompting without context examples. Vulnerable to administrative authority disguises, dropping recall by over 60% under unmarked injection.
                </p>
              </div>
            </Card>
          </motion.div>

          {/* M3 */}
          <motion.div style={{ opacity: m3Opacity, y: m3Y }} className="h-full">
            <Card variant="default" padding="md" className="h-full flex flex-col justify-between border-rose-500/30">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <Badge variant="phishing" size="sm">Vulnerable</Badge>
                  <Layers className="h-4 w-4 text-rose-400" />
                </div>
                <h3 className="text-base font-bold text-white tracking-tight font-['Plus_Jakarta_Sans',sans-serif]">
                  M3: RAG Combined
                </h3>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Monolithic prompt ingests email body alongside retrieved exemplar context. Attacker instructions in the email override classifier decisions, collapsing catch rate to {m3UnmarkedRecall}%.
                </p>
              </div>
              <div className="pt-3 border-t border-slate-800 text-[11px] font-mono text-rose-400 font-semibold">
                {m3EvasionRate}% Evasion Rate Collapse
              </div>
            </Card>
          </motion.div>

          {/* M4 */}
          <motion.div style={{ opacity: m4Opacity, y: m4Y }} className="h-full">
            <Card variant="elevated" padding="md" className="h-full flex flex-col justify-between border-teal-500/40 ring-1 ring-teal-500/20">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <Badge variant="legitimate" size="sm">IFSI Defense</Badge>
                  <ShieldCheck className="h-4 w-4 text-teal-400" />
                </div>
                <h3 className="text-base font-bold text-white tracking-tight font-['Plus_Jakarta_Sans',sans-serif]">
                  M4: RAG Decoupled
                </h3>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Two-stage architecture isolating untrusted text into a structured schema before validation. Recovers {m4UnmarkedRecall}% catch rate under attack, trading safety for a {m4UnmarkedFpr}% false-alarm tax.
                </p>
              </div>
              <div className="pt-3 border-t border-slate-800 text-[11px] font-mono text-teal-300 font-semibold">
                {m4UnmarkedRecall}% Catch &bull; {m4UnmarkedFpr}% FPR Tax
              </div>
            </Card>
          </motion.div>
        </div>
      </section>

      {/* =========================================================================
          SECTION 4: METHODOLOGY & LIMITATIONS
          ========================================================================= */}
      <section id="methodology-section" className="space-y-6 scroll-mt-24">
        <div className="space-y-1">
          <div className="flex items-center gap-2 text-teal-400 text-xs font-semibold uppercase tracking-wider">
            <BookOpen className="h-4 w-4" />
            Research Rigor
          </div>
          <h2 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">Methodology</h2>
          <p className="text-xs sm:text-sm text-slate-400">
            Experimental setup, adversarial attack taxonomy, and paired statistical evaluation protocols.
          </p>
        </div>

        {/* 3 Methodology Pillars (Accordion Expandable) */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Pillar 1: Dataset Size & Source */}
          <Card
            variant="default"
            padding="md"
            className="cursor-pointer transition-all duration-150 hover:border-slate-700 select-none space-y-2.5"
            onClick={() => toggleMethodology('dataset')}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs font-semibold text-teal-400 uppercase tracking-wider">
                <Database className="h-3.5 w-3.5" />
                Dataset &amp; Provenance
              </div>
              <button
                type="button"
                aria-expanded={Boolean(expandedMethodology['dataset'])}
                aria-label="Toggle dataset details"
                className="p-1 rounded-md text-slate-400 hover:text-teal-300 transition-colors"
              >
                <ChevronDown
                  className={`h-4 w-4 transition-transform duration-200 ${
                    expandedMethodology['dataset'] ? 'rotate-180 text-teal-400' : ''
                  }`}
                />
              </button>
            </div>

            <h3 className="text-sm font-bold text-white tracking-tight font-['Plus_Jakarta_Sans',sans-serif]">
              5,223 Emails (N=522 Test Split)
            </h3>

            <p className="text-xs text-slate-300 leading-relaxed">
              Curated from Nazario Phishing Archive and Enron Corpus across a frozen 80/10/10 split.
            </p>

            <AnimatePresence initial={false}>
              {expandedMethodology['dataset'] && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.2, ease: 'easeInOut' }}
                  className="overflow-hidden"
                >
                  <div className="pt-3 border-t border-slate-800 text-xs text-slate-300 leading-relaxed">
                    Curated from the verified <strong className="text-white font-medium">Nazario Phishing Archive</strong> and CMU <strong className="text-white font-medium">Enron Corporate Corpus</strong> (80/10/10 split). The frozen test split (<em>N</em>=522; 128 phishing, 394 legitimate controls) evaluates all models under identical paired conditions.
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </Card>

          {/* Pillar 2: Marked vs. Unmarked */}
          <Card
            variant="default"
            padding="md"
            className="cursor-pointer transition-all duration-150 hover:border-slate-700 select-none space-y-2.5"
            onClick={() => toggleMethodology('attack_modes')}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs font-semibold text-cyan-400 uppercase tracking-wider">
                <Layers className="h-3.5 w-3.5" />
                Attack Disguise Modes
              </div>
              <button
                type="button"
                aria-expanded={Boolean(expandedMethodology['attack_modes'])}
                aria-label="Toggle attack disguise details"
                className="p-1 rounded-md text-slate-400 hover:text-cyan-300 transition-colors"
              >
                <ChevronDown
                  className={`h-4 w-4 transition-transform duration-200 ${
                    expandedMethodology['attack_modes'] ? 'rotate-180 text-cyan-400' : ''
                  }`}
                />
              </button>
            </div>

            <h3 className="text-sm font-bold text-white tracking-tight font-['Plus_Jakarta_Sans',sans-serif]">
              Delimiters vs. Enterprise Camouflage
            </h3>

            <p className="text-xs text-slate-300 leading-relaxed">
              Contrasts synthetic bracketed delimiters against stealthy real-world enterprise camouflage.
            </p>

            <AnimatePresence initial={false}>
              {expandedMethodology['attack_modes'] && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.2, ease: 'easeInOut' }}
                  className="overflow-hidden"
                >
                  <div className="pt-3 border-t border-slate-800 text-xs text-slate-300 leading-relaxed">
                    <strong className="text-cyan-300 font-medium">Marked injections</strong> encapsulate commands within synthetic machine brackets (<code className="text-cyan-300 text-[11px] font-mono">[BEGIN MESSAGE]</code>) easily flagged by rule filters, while <strong className="text-teal-300 font-medium">unmarked injections</strong> disguise instructions as IT forward headers or legal disclaimers that blend naturally into email context.
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </Card>

          {/* Pillar 3: McNemar & Bootstrap */}
          <Card
            variant="default"
            padding="md"
            className="cursor-pointer transition-all duration-150 hover:border-slate-700 select-none space-y-2.5"
            onClick={() => toggleMethodology('statistics')}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs font-semibold text-emerald-400 uppercase tracking-wider">
                <Scale className="h-3.5 w-3.5" />
                Statistical Significance
              </div>
              <button
                type="button"
                aria-expanded={Boolean(expandedMethodology['statistics'])}
                aria-label="Toggle statistics details"
                className="p-1 rounded-md text-slate-400 hover:text-emerald-300 transition-colors"
              >
                <ChevronDown
                  className={`h-4 w-4 transition-transform duration-200 ${
                    expandedMethodology['statistics'] ? 'rotate-180 text-emerald-400' : ''
                  }`}
                />
              </button>
            </div>

            <h3 className="text-sm font-bold text-white tracking-tight font-['Plus_Jakarta_Sans',sans-serif]">
              Paired McNemar &amp; Bootstrap CIs
            </h3>

            <p className="text-xs text-slate-300 leading-relaxed">
              Evaluated with Holm-Bonferroni paired McNemar tests and 2,000-resample bootstrap intervals.
            </p>

            <AnimatePresence initial={false}>
              {expandedMethodology['statistics'] && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.2, ease: 'easeInOut' }}
                  className="overflow-hidden"
                >
                  <div className="pt-3 border-t border-slate-800 space-y-1.5 text-xs text-slate-300 leading-relaxed">
                    <p>
                      <strong className="text-white font-medium">Paired McNemar test:</strong> Measures whether two models differ significantly on the exact same emails rather than by random variance, with Holm-Bonferroni correction (<em>p</em> &lt; 0.05).
                    </p>
                    <p>
                      <strong className="text-white font-medium">Bootstrap CIs:</strong> Non-parametric 2,000-iteration resampling establishes 95% confidence intervals without assuming normal metric distributions.
                    </p>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </Card>
        </div>

        {/* Limitations Subsection (Expandable Tags/Pills) */}
        <div className="rounded-xl border border-slate-800/80 bg-slate-900/50 p-4 sm:p-5 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs font-semibold text-amber-400 uppercase tracking-wider">
              <AlertCircle className="h-3.5 w-3.5" />
              Limitations &amp; Experimental Caveats
            </div>
            <span className="text-[11px] text-slate-500 font-medium hidden sm:inline">
              Click tags to view details
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5">
            {[
              {
                id: 'scope',
                tag: 'Small-Model Scope',
                detail:
                  'Evaluated on lightweight local SLMs (Qwen2.5-0.5B, Llama-3.2-3B); larger frontier models may exhibit stronger instruction adherence, though with significantly higher latency and operational cost.',
              },
              {
                id: 'templates',
                tag: 'Fixed Attack Templates',
                detail:
                  'Adversarial injections were generated across five known attack families; real-world adversaries craft polymorphic, multi-turn, or zero-day evasion prompts.',
              },
              {
                id: 'confidence',
                tag: 'Uncalibrated Confidence',
                detail:
                  'Model confidence outputs reflect raw prompt token heuristics rather than formally calibrated posterior Bayesian probabilities.',
              },
              {
                id: 'latency',
                tag: 'Latency Overhead',
                detail:
                  'Decoupled two-stage inference (M4) doubles API request volume per email, requiring high-throughput batching or secondary triage filters in production gateways.',
              },
            ].map((item) => {
              const isExpanded = Boolean(expandedLimitations[item.id]);
              return (
                <div
                  key={item.id}
                  onClick={() => toggleLimitation(item.id)}
                  className={`p-3 rounded-xl border transition-all duration-150 cursor-pointer select-none ${
                    isExpanded
                      ? 'border-amber-500/40 bg-amber-500/10 shadow-sm'
                      : 'border-slate-800/80 hover:border-slate-700 bg-slate-950/60 hover:bg-slate-900/60'
                  }`}
                >
                  <div className="flex items-center justify-between gap-2">
                    <div className="flex items-center gap-2 min-w-0">
                      <span className="h-1.5 w-1.5 rounded-full bg-amber-400 flex-shrink-0" />
                      <strong className="text-xs font-bold text-slate-200 tracking-tight truncate">
                        {item.tag}
                      </strong>
                    </div>
                    <ChevronDown
                      className={`h-3.5 w-3.5 text-slate-400 transition-transform duration-200 flex-shrink-0 ${
                        isExpanded ? 'rotate-180 text-amber-400' : ''
                      }`}
                    />
                  </div>

                  <AnimatePresence initial={false}>
                    {isExpanded && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.2, ease: 'easeInOut' }}
                        className="overflow-hidden"
                      >
                        <p className="pt-2.5 mt-2 border-t border-slate-800 text-[11px] text-slate-300 leading-relaxed">
                          {item.detail}
                        </p>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* =========================================================================
          SECTION 5: KEY EMPIRICAL FINDING
          ========================================================================= */}
      <section ref={keyFindingSectionRef} className="space-y-4">
        <motion.div
          style={{ opacity: keyFindingHeadingOpacity, y: keyFindingHeadingY }}
          className="space-y-1"
        >
          <div className="flex items-center gap-2 text-teal-400 text-xs font-semibold uppercase tracking-wider">
            <Sparkles className="h-4 w-4" />
            Empirical Results
          </div>
          <h2 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">Key Finding</h2>
        </motion.div>

        <div className="relative">
          <AnimatePresence mode="popLayout" initial={false}>
            {loading ? (
              <motion.div
                key="key-finding-skeleton"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.25, ease: 'easeInOut' }}
                className="w-full"
              >
                <SkeletonCard height="h-48" />
              </motion.div>
            ) : (
              <motion.div
                key="key-finding-content"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.35, ease: 'easeOut' }}
                style={{
                  opacity: keyFindingCardOpacity,
                  y: keyFindingCardY,
                  scale: keyFindingCardScale,
                  borderColor: keyFindingBorder,
                  boxShadow: keyFindingShadow,
                }}
                className="rounded-2xl border bg-gradient-to-r from-teal-950/40 via-slate-900/80 to-slate-900/50 p-6 sm:p-8 elevation-card w-full"
              >
                <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
                  <div className="space-y-3 max-w-2xl">
                    <h3 className="text-lg sm:text-xl font-bold text-white tracking-tight">
                      Standard RAG suffers a {m3EvasionRate}% evasion rate under unmarked injection, while IFSI recovers catch rate to {m4UnmarkedRecall}% at a {m4UnmarkedFpr}% false-alarm tradeoff.
                    </h3>

                    <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
                      Monolithic context windows give untrusted email tokens equal attention priority to classifier directives, causing M3's catastrophic collapse under natural camouflage. Decoupled two-stage inference (M4) isolates untrusted input into a structured schema before validation, restoring attack resilience at the cost of flagging benign emails containing security notices.
                    </p>
                  </div>

                  {/* 3-Stat Tradeoff Column */}
                  <motion.div
                    style={{
                      opacity: keyFindingStatsOpacity,
                      x: keyFindingStatsX,
                      scale: keyFindingStatsScale,
                    }}
                    className="flex-shrink-0 grid grid-cols-1 sm:grid-cols-3 lg:grid-cols-1 gap-2.5 w-full lg:w-60"
                  >
                    <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-3 text-center">
                      <div className="text-[11px] font-semibold text-rose-300">M3 Attacker Evasion</div>
                      <div className="text-2xl font-black text-rose-400 mt-0.5">
                        {m3EvasionRate}%
                      </div>
                      <div className="text-[10px] text-slate-400 mt-0.5">Phishing slips past</div>
                    </div>

                    <div className="rounded-xl border border-teal-500/30 bg-teal-500/10 p-3 text-center">
                      <div className="text-[11px] font-semibold text-teal-300">M4 Catch Under Attack</div>
                      <div className="text-2xl font-black text-teal-400 mt-0.5">
                        {m4UnmarkedRecall}%
                      </div>
                      <div className="text-[10px] text-slate-400 mt-0.5">Phishing caught</div>
                    </div>

                    <div className="rounded-xl border border-amber-500/30 bg-amber-500/10 p-3 text-center">
                      <div className="text-[11px] font-semibold text-amber-300">M4 False-Alarm Tax</div>
                      <div className="text-2xl font-black text-amber-400 mt-0.5">
                        {m4UnmarkedFpr}%
                      </div>
                      <div className="text-[10px] text-slate-400 mt-0.5">Benign emails blocked</div>
                    </div>
                  </motion.div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </section>

    </motion.div>
  );
};

export default LandingPage;
