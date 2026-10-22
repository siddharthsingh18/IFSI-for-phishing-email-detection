import React, { useEffect, useState, useRef } from 'react';
import { Link } from 'react-router-dom';
import {
  ArrowRight,
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
  Network,
} from 'lucide-react';
import { apiClient, type BenchmarkSummary } from '../api/client';
import { Card } from '../components/Card';
import { OfflineFallbackBanner } from '../components/OfflineFallbackBanner';
import { Badge } from '../components/Badge';
import { SkeletonCard } from '../components/Skeleton';
import { InjectedEmailGraphic } from '../components/InjectedEmailGraphic';
import { ApproachFlowDiagram } from '../components/ApproachFlowDiagram';
import {
  KeyFindingShieldComparison,
  BrokenShieldIcon,
  StrainedShieldIcon,
} from '../components/KeyFindingShields';
import { SectionTransitionDivider } from '../components/SectionTransitionDivider';
import { motion, AnimatePresence, useScroll, useTransform, useReducedMotion } from 'framer-motion';
import { usePrefersReducedMotion } from '../hooks/usePrefersReducedMotion';
import { useCountUp } from '../hooks/useCountUp';
import { fadeInUp } from '../lib/motion';
import {
  Area,
  AreaChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

const M1_TRAINING_EMAIL_COUNT = 4_881;

export const LandingPage: React.FC = () => {
  const [summary, setSummary] = useState<BenchmarkSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [isUsingFallback, setIsUsingFallback] = useState(false);
  const [hoveredMethod, setHoveredMethod] = useState<'M1' | 'M2' | 'M3' | 'M4' | null>(null);
  const [expandedMethodology, setExpandedMethodology] = useState<Record<string, boolean>>({});
  const [expandedLimitations, setExpandedLimitations] = useState<Record<string, boolean>>({});
  const [heroInView, setHeroInView] = useState(false);
  const heroRef = useRef<HTMLElement>(null);

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
  const animatedTrainingEmailCount = useCountUp(M1_TRAINING_EMAIL_COUNT, {
    start: heroInView,
    duration: 700,
  });
  const recallSeries = ['clean', 'marked', 'unmarked'].map((condition) => {
    const metrics = summary?.cells?.[`M4_${condition}`]?.metrics;
    return {
      condition: condition[0].toUpperCase() + condition.slice(1),
      recall: metrics ? Number((metrics.recall * 100).toFixed(1)) : null,
    };
  });
  const hasRecallData = recallSeries.every((point) => point.recall !== null);
  const strongestRecall = recallSeries.reduce((best, point) => (
    point.recall !== null && (best === null || (best.recall !== null && point.recall > best.recall)) ? point : best
  ), null as (typeof recallSeries)[number] | null);

  useEffect(() => {
    const element = heroRef.current;
    if (!element || typeof IntersectionObserver === 'undefined') {
      setHeroInView(true);
      return;
    }
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) {
        setHeroInView(true);
        observer.disconnect();
      }
    }, { threshold: 0.2 });
    observer.observe(element);
    return () => observer.disconnect();
  }, []);

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
          SECTION 2: THE PROBLEM
          ========================================================================= */}
      <motion.section
        ref={heroRef}
        initial="hidden"
        animate="visible"
        className="landing-hero grid grid-cols-1 lg:grid-cols-[.9fr_1.1fr] gap-10 lg:gap-14 items-center"
      >
        <div className="space-y-6">
          <motion.div variants={fadeInUp} className="space-y-5">
            <div className="text-xs font-semibold uppercase tracking-[.14em] text-teal-400">IFSI Phishing Detection · Benchmark</div>
            <h1 className="text-4xl sm:text-6xl font-black leading-[1.02] tracking-[-0.025em] text-white">
              Phishing emails can fool the model, too.
            </h1>
            <p className="max-w-xl text-base sm:text-lg leading-relaxed text-slate-300">
              Measure whether LLM-based detectors keep the right verdict when malicious instructions are hidden inside the email.
            </p>
          </motion.div>
          <motion.div variants={fadeInUp} className="flex flex-wrap gap-3">
            <Link to="/test" className="inline-flex min-h-11 items-center justify-center gap-2 rounded-full bg-teal-500 px-5 py-2.5 text-sm font-bold text-slate-950 transition hover:bg-teal-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-300">
              Try Live Test <ArrowRight className="h-4 w-4" />
            </Link>
            <Link to="/dashboard" className="inline-flex min-h-11 items-center justify-center rounded-full border border-slate-600 px-5 py-2.5 text-sm font-semibold text-slate-200 transition hover:border-teal-400 hover:text-teal-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-300">
              View Results
            </Link>
          </motion.div>
          <motion.div variants={fadeInUp} className="landing-method-card">
            <div className="landing-method-icon"><Network className="h-5 w-5" /></div>
            <div className="min-w-0">
              <strong>4 methods compared head-to-head</strong>
              <span>From a linear baseline to decoupled RAG.</span>
              <a href="#methods-section">More Details <ArrowRight className="inline h-3 w-3" /></a>
            </div>
          </motion.div>
        </div>

        <motion.div variants={fadeInUp} className="landing-hero-visual">
          <svg className="landing-network" viewBox="0 0 620 440" role="img" aria-label="Abstract network of connected phishing detection methods">
            <defs>
              <radialGradient id="networkGlow">
                <stop offset="0" stopColor="#14b8a6" stopOpacity=".3" />
                <stop offset=".55" stopColor="#0e7490" stopOpacity=".1" />
                <stop offset="1" stopColor="#14b8a6" stopOpacity="0" />
              </radialGradient>
              <linearGradient id="networkLine" x1="0" x2="1">
                <stop stopColor="#14b8a6" stopOpacity=".2" />
                <stop offset=".5" stopColor="#2dd4bf" stopOpacity=".9" />
                <stop offset="1" stopColor="#0d9488" stopOpacity=".2" />
              </linearGradient>
              <radialGradient id="networkOrbFill" cx="35%" cy="24%" r="78%">
                <stop offset="0" stopColor="#99f6e4" stopOpacity=".52" />
                <stop offset=".35" stopColor="#0f766e" stopOpacity=".88" />
                <stop offset="1" stopColor="#07111f" />
              </radialGradient>
              <radialGradient id="networkShieldFill" cx="36%" cy="20%" r="82%">
                <stop offset="0" stopColor="#ccfbf1" stopOpacity=".7" />
                <stop offset=".38" stopColor="#115e59" />
                <stop offset="1" stopColor="#06101b" />
              </radialGradient>
              <linearGradient id="networkOrbRim" x1="0" y1="0" x2="1" y2="1">
                <stop stopColor="#ecfeff" stopOpacity=".95" />
                <stop offset=".38" stopColor="#5eead4" stopOpacity=".58" />
                <stop offset="1" stopColor="#0f766e" stopOpacity=".08" />
              </linearGradient>
              <filter id="networkOrbShadow" x="-80%" y="-80%" width="260%" height="280%">
                <feDropShadow dx="0" dy="5" stdDeviation="4" floodColor="#020617" floodOpacity=".72" />
                <feDropShadow dx="-1" dy="-1" stdDeviation="1.2" floodColor="#99f6e4" floodOpacity=".24" />
              </filter>
              <filter id="networkShieldGlow" x="-100%" y="-100%" width="300%" height="300%">
                <feGaussianBlur stdDeviation="10" />
              </filter>
            </defs>
            <circle className="landing-network-core-glow" cx="300" cy="220" r="190" fill="url(#networkGlow)" />
            <circle className="landing-network-atmosphere" cx="300" cy="220" r="128" fill="#14b8a6" opacity=".12" filter="url(#networkShieldGlow)" />
            <circle className="landing-network-atmosphere landing-network-atmosphere--one" cx="105" cy="105" r="40" fill="#22d3ee" opacity=".12" filter="url(#networkShieldGlow)" />
            <circle className="landing-network-atmosphere landing-network-atmosphere--two" cx="490" cy="335" r="52" fill="#10b981" opacity=".1" filter="url(#networkShieldGlow)" />
            <circle className="landing-network-atmosphere landing-network-atmosphere--three" cx="505" cy="130" r="30" fill="#38bdf8" opacity=".1" filter="url(#networkShieldGlow)" />
            <g fill="none" stroke="url(#networkLine)" strokeWidth="2">
              <path d="M90 250 190 155 300 225 420 145 520 250" />
              <path d="M190 155 230 315 300 225 390 320 420 145" />
              <path d="M90 250 230 315 390 320 520 250" />
            </g>
            <g className="landing-network-flow" fill="none" stroke="#a7f3d0" strokeWidth="3" strokeLinecap="round" strokeDasharray="2 20">
              <path d="M90 250 190 155 300 225" />
              <path d="M300 225 420 145 520 250" />
              <path d="M230 315 300 225 390 320" />
            </g>
            <g fill="none" stroke="#5eead4" strokeOpacity=".2" strokeWidth="1.2">
              <path d="M470 90 420 145" />
              <path d="M80 350 145 318" />
              <path d="M490 365 450 320" />
            </g>
            <g className="landing-network-particles">
              <circle cx="470" cy="90" r="5" fill="url(#networkOrbFill)" stroke="url(#networkOrbRim)" filter="url(#networkOrbShadow)" opacity=".72" />
              <circle cx="80" cy="350" r="9" fill="url(#networkOrbFill)" stroke="url(#networkOrbRim)" filter="url(#networkOrbShadow)" />
              <circle cx="490" cy="365" r="6" fill="url(#networkOrbFill)" stroke="url(#networkOrbRim)" filter="url(#networkOrbShadow)" opacity=".78" />
              <circle cx="555" cy="175" r="4" fill="url(#networkOrbFill)" stroke="url(#networkOrbRim)" filter="url(#networkOrbShadow)" opacity=".54" />
              <circle cx="350" cy="72" r="3" fill="#a7f3d0" opacity=".62" filter="url(#networkShieldGlow)" />
            </g>
            <g filter="url(#networkOrbShadow)" stroke="url(#networkOrbRim)">
              <circle cx="90" cy="250" r="11" fill="url(#networkOrbFill)" />
              <circle cx="190" cy="155" r="11" fill="url(#networkOrbFill)" />
              <circle cx="230" cy="315" r="11" fill="url(#networkOrbFill)" />
              <circle cx="390" cy="320" r="11" fill="url(#networkOrbFill)" />
              <circle cx="420" cy="145" r="11" fill="url(#networkOrbFill)" />
              <circle cx="520" cy="250" r="11" fill="url(#networkOrbFill)" />
            </g>
            <g transform="translate(267 192)">
              <circle className="landing-network-shield-halo" r="50" fill="#14b8a6" opacity=".3" filter="url(#networkShieldGlow)" />
              <circle r="38" fill="url(#networkShieldFill)" stroke="url(#networkOrbRim)" strokeWidth="2.5" filter="url(#networkOrbShadow)" />
              <circle r="31" fill="none" stroke="#5eead4" strokeOpacity=".18" strokeWidth="1" />
              <path d="M0-16 13-10v12C13 12 6 19 0 22-6 19-13 12-13 2v-12z" fill="none" stroke="#5eead4" strokeWidth="2" />
              <path d="M-5 1h10M0-4v10" stroke="#5eead4" strokeWidth="2" strokeLinecap="round" />
            </g>
            <g fill="#ccfbf1" opacity=".8"><circle cx="155" cy="90" r="2" /><circle cx="475" cy="95" r="2" /><circle cx="555" cy="175" r="1.5" /></g>
          </svg>
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.2 }}
            variants={{
              hidden: shouldReduceMotion
                ? { opacity: 0 }
                : { opacity: 0, scale: 0.95, rotateX: 8 },
              visible: {
                opacity: 1,
                scale: 1,
                rotateX: 0,
                transition: { duration: shouldReduceMotion ? 0.18 : 0.55, ease: [0.16, 1, 0.3, 1] },
              },
            }}
            style={shouldReduceMotion ? undefined : { transformPerspective: 900, transformOrigin: '50% 100%' }}
            className="landing-recall-card"
          >
            <div className="flex items-center justify-between">
              <span>Recall across conditions</span>
              <span className="landing-chart-label">M4</span>
            </div>
            {hasRecallData ? (
              <div className="landing-chart-wrap h-32">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={recallSeries} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
                    <defs><linearGradient id="recallFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#14b8a6" stopOpacity=".35" /><stop offset="1" stopColor="#14b8a6" stopOpacity="0" /></linearGradient></defs>
                    <XAxis dataKey="condition" interval={0} tick={{ fontSize: 9 }} axisLine={false} tickLine={false} />
                    <YAxis domain={[0, 100]} hide />
                    <Tooltip formatter={(value) => [`${value ?? 0}%`, 'Recall']} />
                    <Area type="monotone" dataKey="recall" stroke="#0d9488" strokeWidth={3} fill="url(#recallFill)" dot={{ r: 4, fill: '#0d9488' }} activeDot={{ r: 6 }} />
                  </AreaChart>
                </ResponsiveContainer>
                {strongestRecall && <span className="landing-chart-callout">{strongestRecall.condition}: {strongestRecall.recall}%</span>}
              </div>
            ) : <div className="landing-chart-empty">Live benchmark data unavailable.</div>}
          </motion.div>
          <div className="landing-hero-prompt-badge" aria-label="Prompt-injection tested across four methods">
            <span className="landing-hero-prompt-icon"><ShieldCheck className="h-4 w-4" /></span>
            <span>
              <strong>Prompt-Injection Tested</strong>
              <small>4 methods · 3 conditions</small>
            </span>
          </div>
          <div className="landing-hero-stat">
            <strong>{animatedTrainingEmailCount || '—'}</strong>
            <span>Emails Used to Train M1</span>
            <div className="landing-method-badges" aria-label="Four benchmark methods">
              {['M1', 'M2', 'M3', 'M4'].map((method) => <span key={method}>{method}</span>)}
              <a href="#methods-section" aria-label="See all methods"><ArrowRight className="h-3 w-3" /></a>
            </div>
          </div>
        </motion.div>
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
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center">
            {/* Left Column: Headline and 3 Stat Chips */}
            <div className="lg:col-span-8 xl:col-span-8 space-y-5">
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

            {/* Right Column: Compact SVG Email Graphic with Injected Payload */}
            <div className="lg:col-span-4 xl:col-span-4 flex items-center justify-center lg:justify-end pt-2 lg:pt-0">
              <InjectedEmailGraphic shouldReduceMotion={shouldReduceMotion} />
            </div>
          </div>
        </Card>
      </section>

      {/* Transition Cue: Problem → Approach */}
      <SectionTransitionDivider shouldReduceMotion={shouldReduceMotion} />

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
        </motion.div>

        {/* Animated Particle / Line Flow Diagram */}
        <ApproachFlowDiagram
          hoveredMethod={hoveredMethod}
          shouldReduceMotion={shouldReduceMotion}
        />

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* M1 */}
          <motion.div
            style={{ opacity: m1Opacity, y: m1Y }}
            className="h-full"
            onMouseEnter={() => setHoveredMethod('M1')}
            onMouseLeave={() => setHoveredMethod(null)}
          >
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
                  Structurally immune to prompt injection ({m1CleanAccuracy}% accuracy), but fails on novel spear-phishing.
                </p>
              </div>
              <div className="pt-3 border-t border-slate-800 text-[11px] font-mono text-teal-400">
                Linear Structural Immunity
              </div>
            </Card>
          </motion.div>

          {/* M2 */}
          <motion.div
            style={{ opacity: m2Opacity, y: m2Y }}
            className="h-full"
            onMouseEnter={() => setHoveredMethod('M2')}
            onMouseLeave={() => setHoveredMethod(null)}
          >
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
                  Direct prompt instruction without context; recall drops by over 60% under unmarked injection.
                </p>
              </div>
            </Card>
          </motion.div>

          {/* M3 */}
          <motion.div
            style={{ opacity: m3Opacity, y: m3Y }}
            className="h-full"
            onMouseEnter={() => setHoveredMethod('M3')}
            onMouseLeave={() => setHoveredMethod(null)}
          >
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
                  Standard single-prompt RAG; injected instructions override decisions, collapsing catch rate to {m3UnmarkedRecall}%.
                </p>
              </div>
              <div className="pt-3 border-t border-slate-800 text-[11px] font-mono text-rose-400 font-semibold">
                {m3EvasionRate}% Evasion Rate Collapse
              </div>
            </Card>
          </motion.div>

          {/* M4 */}
          <motion.div
            style={{ opacity: m4Opacity, y: m4Y }}
            className="h-full"
            onMouseEnter={() => setHoveredMethod('M4')}
            onMouseLeave={() => setHoveredMethod(null)}
          >
            <Card variant="elevated" padding="md" className="h-full flex flex-col justify-between border-teal-500/40 ring-1 ring-teal-500/20">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <Badge variant="legitimate" size="sm">IFSI Phishing Detection</Badge>
                  <ShieldCheck className="h-4 w-4 text-teal-400" />
                </div>
                <h3 className="text-base font-bold text-white tracking-tight font-['Plus_Jakarta_Sans',sans-serif]">
                  M4: RAG Decoupled
                </h3>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Decoupled two-stage inference; restores catch rate to {m4UnmarkedRecall}% at a {m4UnmarkedFpr}% false-alarm tax.
                </p>
              </div>
              <div className="pt-3 border-t border-slate-800 text-[11px] font-mono text-teal-300 font-semibold">
                {m4UnmarkedRecall}% Catch &bull; {m4UnmarkedFpr}% FPR Tax
              </div>
            </Card>
          </motion.div>
        </div>
      </section>

      {/* Transition Cue: Approach → Methodology */}
      <SectionTransitionDivider shouldReduceMotion={shouldReduceMotion} />

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

      {/* Transition Cue: Methodology → Key Finding */}
      <SectionTransitionDivider shouldReduceMotion={shouldReduceMotion} />

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
                  <div className="max-w-2xl space-y-4">
                    <h3 className="text-lg sm:text-xl font-bold text-white tracking-tight leading-snug">
                      Standard RAG suffers a {m3EvasionRate}% evasion rate under unmarked injection, while IFSI Phishing Detection recovers catch rate to {m4UnmarkedRecall}% at a {m4UnmarkedFpr}% false-alarm tradeoff.
                    </h3>

                    {/* Side-by-side pair of animated shield icons: M3 shattered vs M4 strained */}
                    <KeyFindingShieldComparison
                      m3EvasionRate={m3EvasionRate}
                      m4UnmarkedFpr={m4UnmarkedFpr}
                      shouldReduceMotion={shouldReduceMotion}
                    />
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
                      <div className="flex items-center justify-center gap-1.5 text-[11px] font-semibold text-rose-300">
                        <BrokenShieldIcon size="sm" shouldReduceMotion={shouldReduceMotion} />
                        <span>M3 Attacker Evasion</span>
                      </div>
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
                      <div className="flex items-center justify-center gap-1.5 text-[11px] font-semibold text-amber-300">
                        <StrainedShieldIcon size="sm" shouldReduceMotion={shouldReduceMotion} />
                        <span>M4 False-Alarm Tax</span>
                      </div>
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
