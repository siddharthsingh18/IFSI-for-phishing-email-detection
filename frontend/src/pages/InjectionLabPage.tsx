import React, { useEffect, useState, useMemo } from 'react';
import { FlaskConical } from 'lucide-react';
import {
  apiClient,
  type BenchmarkSummary,
  type PresetSample,
  type ClassificationResult,
  type InjectResponse,
  type AttackFamilyExample,
} from '../api/client';
import { OfflineFallbackBanner } from '../components/OfflineFallbackBanner';
import { motion } from 'framer-motion';
import { fadeInUp } from '../lib/motion';
import { useTheme } from '../hooks/useTheme';

// Subcomponents under pages/injection-lab/
import { AttackFamilyExplorer } from './injection-lab/AttackFamilyExplorer';
import { ComparisonResults } from './injection-lab/ComparisonResults';
import { SynthesisWorkbench } from './injection-lab/SynthesisWorkbench';
import {
  type AttackFamilyMeta,
  type ChartGroupRow,
  FAMILY_METADATA_REGISTRY,
  formatFamilyTitle,
  formatStyleTitle,
  DEFAULT_ATTACK_EXAMPLES,
  METHOD_NAMES,
  METHOD_DESCRIPTIONS,
} from './injection-lab/types';

export const InjectionLabPage: React.FC = () => {
  const { chartColors } = useTheme();

  // =========================================================================
  // PAGE-LEVEL DATA STATES
  // =========================================================================
  const [summary, setSummary] = useState<BenchmarkSummary | null>(null);
  const [loadingSummary, setLoadingSummary] = useState(true);
  const [summaryError, setSummaryError] = useState<string | null>(null);

  const [presets, setPresets] = useState<Record<string, PresetSample>>({});
  const [selectedPresetKey, setSelectedPresetKey] = useState<string>('');
  const [loadingPresets, setLoadingPresets] = useState(true);

  const [familyExamples, setFamilyExamples] = useState<Record<string, AttackFamilyExample> | null>(null);
  const [isUsingFallback, setIsUsingFallback] = useState<boolean>(false);

  // =========================================================================
  // SECTION 1: EXPLORER STATE
  // =========================================================================
  const [explorerFamily, setExplorerFamily] = useState<string>('label_override');
  const [explorerStyle, setExplorerStyle] = useState<string>('forwarded_notice');

  // =========================================================================
  // SECTION 3: WORKBENCH STATE
  // =========================================================================
  const [baseSubject, setBaseSubject] = useState('');
  const [baseSender, setBaseSender] = useState('');
  const [baseBody, setBaseBody] = useState('');

  const [attackFamily, setAttackFamily] = useState<string>('label_override');
  const [attackStyle, setAttackStyle] = useState<'unmarked' | 'marked'>('unmarked');
  const [attackPosition, setAttackPosition] = useState<'body_start' | 'body_middle' | 'body_end'>('body_start');
  const [evalMethod, setEvalMethod] = useState<'M3' | 'M4' | 'M1' | 'M2'>('M3');
  const [evalModel, setEvalModel] = useState('qwen2.5:0.5b');

  const [isEvaluating, setIsEvaluating] = useState(false);
  const [attackRan, setAttackRan] = useState(false);
  const [cleanResult, setCleanResult] = useState<ClassificationResult | null>(null);
  const [injectedResult, setInjectedResult] = useState<ClassificationResult | null>(null);
  const [injectDetails, setInjectDetails] = useState<InjectResponse | null>(null);
  const [cleanFullText, setCleanFullText] = useState('');
  const [injectedFullText, setInjectedFullText] = useState('');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const [showPayloadDetails, setShowPayloadDetails] = useState(true);
  const [copiedPayload, setCopiedPayload] = useState(false);

  // Load benchmark summary, authentic attack families & presets on mount
  useEffect(() => {
    let mounted = true;

    // 1. Fetch benchmark summary for Section 2 Recharts
    apiClient
      .getBenchmarkSummary()
      .then((data) => {
        if (!mounted) return;
        setSummary(data);
        setLoadingSummary(false);
      })
      .catch((err) => {
        console.error('Failed to load benchmark summary:', err);
        if (!mounted) return;
        setIsUsingFallback(true);
        setSummaryError('Failed to load benchmark summary data.');
        setLoadingSummary(false);
      });

    // 2. Fetch authentic attack family examples dynamically from backend
    apiClient
      .getInjectionExamples()
      .then((data) => {
        if (!mounted) return;
        const examplesMap = data as Record<string, AttackFamilyExample>;
        setFamilyExamples(examplesMap);
        const backendFamilyKeys = Object.keys(examplesMap);
        if (backendFamilyKeys.length > 0) {
          setExplorerFamily((prev) => (backendFamilyKeys.includes(prev) ? prev : backendFamilyKeys[0]));
          setAttackFamily((prev) => (backendFamilyKeys.includes(prev) ? prev : backendFamilyKeys[0]));
        }
      })
      .catch((err) => {
        console.warn('Could not fetch remote injection examples; using dataset fallbacks:', err);
        if (!mounted) return;
        setIsUsingFallback(true);
      });

    // 3. Fetch presets for Section 3 Workbench
    apiClient
      .getPresets()
      .then((data) => {
        if (!mounted) return;
        setPresets(data);
        setLoadingPresets(false);
        const keys = Object.keys(data);
        const firstCleanPhish = keys.find((k) => k.toLowerCase().includes('clean') && k.toLowerCase().includes('phishing')) || keys[0];
        if (firstCleanPhish && data[firstCleanPhish]) {
          const sample = data[firstCleanPhish];
          setSelectedPresetKey(firstCleanPhish);
          setBaseSubject(sample.subject || '');
          setBaseSender(sample.sender || '');
          setBaseBody(sample.body || '');
        }
      })
      .catch((err) => {
        console.error('Failed to load presets:', err);
        if (!mounted) return;
        setLoadingPresets(false);
        setIsUsingFallback(true);
      });

    return () => {
      mounted = false;
    };
  }, []);

  // Dynamic Attack Families: Derived strictly from backend response
  const attackFamilies: AttackFamilyMeta[] = useMemo(() => {
    if (familyExamples && Object.keys(familyExamples).length > 0) {
      return Object.keys(familyExamples).map((id) => {
        const meta = FAMILY_METADATA_REGISTRY[id];
        const famData = familyExamples[id];
        const baseInst =
          famData?.marked?.base_instruction ||
          famData?.marked?.injected_text?.split('\n')[1] ||
          `Direct prompt injection directive for ${formatFamilyTitle(id)}.`;

        return {
          id,
          name: formatFamilyTitle(id),
          tagline: meta?.tagline || `Attack vector: ${formatFamilyTitle(id)}`,
          description: meta?.description || `Authentic dataset attack templates under the ${id} family.`,
          directiveExample: baseInst,
        };
      });
    }

    return Object.keys(DEFAULT_ATTACK_EXAMPLES).map((id) => {
      const meta = FAMILY_METADATA_REGISTRY[id];
      return {
        id,
        name: formatFamilyTitle(id),
        tagline: meta?.tagline || `Attack vector: ${formatFamilyTitle(id)}`,
        description: meta?.description || `Authentic dataset attack templates under the ${id} family.`,
        directiveExample: DEFAULT_ATTACK_EXAMPLES[id]?.marked?.split('\n')[1] || `Directive for ${id}`,
      };
    });
  }, [familyExamples]);

  // Dynamic Unmarked Styles: Derived strictly from backend unmarked_by_style dictionary
  const availableExplorerStyles = useMemo(() => {
    if (familyExamples?.[explorerFamily]?.unmarked_by_style) {
      const styles = Object.keys(familyExamples[explorerFamily].unmarked_by_style);
      if (styles.length > 0) {
        return styles.map((st) => ({
          id: st,
          label: formatStyleTitle(st),
        }));
      }
    }

    const fallbackStyles = Object.keys(DEFAULT_ATTACK_EXAMPLES[explorerFamily]?.unmarked || {});
    return fallbackStyles.map((st) => ({
      id: st,
      label: formatStyleTitle(st),
    }));
  }, [familyExamples, explorerFamily]);

  // Explorer computed metadata & payload strings
  const currentFamilyMeta = useMemo(() => {
    return (
      attackFamilies.find((f) => f.id === explorerFamily) ||
      attackFamilies[0] || {
        id: explorerFamily,
        name: formatFamilyTitle(explorerFamily),
        tagline: '',
        description: '',
        directiveExample: '',
      }
    );
  }, [attackFamilies, explorerFamily]);

  const currentMarkedText = useMemo(() => {
    if (familyExamples?.[explorerFamily]?.marked?.injected_text) {
      return familyExamples[explorerFamily].marked.injected_text;
    }
    return DEFAULT_ATTACK_EXAMPLES[explorerFamily]?.marked || '';
  }, [familyExamples, explorerFamily]);

  const currentUnmarkedText = useMemo(() => {
    const apiStyleList = familyExamples?.[explorerFamily]?.unmarked_by_style?.[explorerStyle];
    if (apiStyleList && apiStyleList.length > 0 && apiStyleList[0].injected_text) {
      return apiStyleList[0].injected_text;
    }
    const fallbackFamily = DEFAULT_ATTACK_EXAMPLES[explorerFamily];
    if (fallbackFamily?.unmarked?.[explorerStyle]) {
      return fallbackFamily.unmarked[explorerStyle];
    }
    return fallbackFamily?.unmarked?.forwarded_notice || '';
  }, [familyExamples, explorerFamily, explorerStyle]);

  // Section 2 Computations: Grouped Bar Chart Data
  const chartData: ChartGroupRow[] = useMemo(() => {
    if (!summary?.cells) return [];

    const methods = ['M1', 'M2', 'M3', 'M4'];
    return methods.map((m) => {
      const markedCell = summary.cells[`${m}_marked`]?.metrics;
      const unmarkedCell = summary.cells[`${m}_unmarked`]?.metrics;

      const markedRecall = markedCell ? Number((markedCell.recall * 100).toFixed(1)) : 0;
      const unmarkedRecall = unmarkedCell ? Number((unmarkedCell.recall * 100).toFixed(1)) : 0;
      const deltaRecall = Number((unmarkedRecall - markedRecall).toFixed(1));

      const markedFpr = markedCell ? Number((markedCell.fpr * 100).toFixed(1)) : 0;
      const unmarkedFpr = unmarkedCell ? Number((unmarkedCell.fpr * 100).toFixed(1)) : 0;
      const deltaFpr = Number((unmarkedFpr - markedFpr).toFixed(1));

      return {
        methodCode: m,
        name: METHOD_NAMES[m] || m,
        fullName: `${METHOD_NAMES[m]} (${METHOD_DESCRIPTIONS[m]})`,
        markedRecall,
        unmarkedRecall,
        deltaRecall,
        markedFpr,
        unmarkedFpr,
        deltaFpr,
      };
    });
  }, [summary]);

  // Handlers for Workbench
  const handleSelectPreset = (key: string) => {
    const sample = presets[key];
    if (!sample) return;
    setSelectedPresetKey(key);
    setBaseSubject(sample.subject || '');
    setBaseSender(sample.sender || '');
    setBaseBody(sample.body || '');
    setErrorMessage(null);
  };

  const handleResetWorkbench = () => {
    const keys = Object.keys(presets);
    const firstCleanPhish = keys.find((k) => k.toLowerCase().includes('clean') && k.toLowerCase().includes('phishing')) || keys[0];
    if (firstCleanPhish && presets[firstCleanPhish]) {
      const sample = presets[firstCleanPhish];
      setSelectedPresetKey(firstCleanPhish);
      setBaseSubject(sample.subject || '');
      setBaseSender(sample.sender || '');
      setBaseBody(sample.body || '');
    } else {
      setSelectedPresetKey('');
      setBaseSubject('');
      setBaseSender('');
      setBaseBody('');
    }
    setAttackFamily(attackFamilies[0]?.id || 'label_override');
    setAttackStyle('unmarked');
    setAttackPosition('body_start');
    setEvalMethod('M3');
    setEvalModel('qwen2.5:0.5b');
    setAttackRan(false);
    setCleanResult(null);
    setInjectedResult(null);
    setInjectDetails(null);
    setErrorMessage(null);
  };

  const handleRunAttack = async () => {
    if (!baseBody.trim()) {
      setErrorMessage('Please provide email body text or select a curated preset from the library above.');
      return;
    }

    setIsEvaluating(true);
    setErrorMessage(null);

    try {
      const cleanFormatted = `Subject: ${baseSubject || '(None)'}\nFrom: ${baseSender || '(None)'}\n\n${baseBody}`;
      setCleanFullText(cleanFormatted);

      const injRes = await apiClient.injectEmail({
        text: baseBody,
        style: attackStyle,
        attack_family: attackFamily,
        position: attackPosition,
      });
      setInjectDetails(injRes);

      const injectedFormatted = `Subject: ${baseSubject || '(None)'}\nFrom: ${baseSender || '(None)'}\n\n${injRes.injected_text}`;
      setInjectedFullText(injectedFormatted);

      const [cResult, iResult] = await Promise.all([
        apiClient.classifyEmail({
          text: baseBody,
          subject: baseSubject,
          sender: baseSender,
          method: evalMethod,
          model: evalModel,
          k: 3,
        }),
        apiClient.classifyEmail({
          text: injRes.injected_text,
          subject: baseSubject,
          sender: baseSender,
          method: evalMethod,
          model: evalModel,
          k: 3,
        }),
      ]);

      setCleanResult(cResult);
      setInjectedResult(iResult);
      setAttackRan(true);
    } catch (err: any) {
      console.error('Adversarial workbench evaluation error:', err);
      setErrorMessage(err.message || 'Adversarial synthesis and evaluation failed. Ensure the backend server is running.');
    } finally {
      setIsEvaluating(false);
    }
  };

  const handleCopyPayload = () => {
    if (!injectDetails?.payload) return;
    navigator.clipboard.writeText(injectDetails.payload);
    setCopiedPayload(true);
    setTimeout(() => setCopiedPayload(false), 2000);
  };

  return (
    <motion.div
      variants={fadeInUp}
      initial="hidden"
      animate="visible"
      exit="exit"
      className="space-y-16 pb-16"
    >
      {/* Unmissable Fallback Warning Banner */}
      {isUsingFallback && (
        <OfflineFallbackBanner
          onRetry={() => window.location.reload()}
        />
      )}

      {/* PAGE HERO & ROUTE HEADER */}
      <div className="space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2 text-teal-400 text-xs font-semibold uppercase tracking-wider">
              <FlaskConical className="h-4 w-4" />
              <span>Route: /injection-lab</span>
              <span className="text-slate-600">&bull;</span>
              <span className="text-slate-400">Adversarial Evaluation Arena</span>
            </div>
            <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight font-['Plus_Jakarta_Sans',sans-serif]">
              Prompt Injection Lab
            </h1>
            <p className="text-sm sm:text-base text-slate-300 max-w-3xl leading-relaxed">
              Explore how indirect prompt injections fool LLMs, examine empirical resilience between synthetic marked
              tags vs. real-world unmarked enterprise camouflage across M1–M4, and test live attacks in a single workbench.
            </p>
          </div>


        </div>
      </div>

      {/* SECTION 1: PLAIN-LANGUAGE EXPLAINER & ATTACK FAMILY EXPLORER */}
      <AttackFamilyExplorer
        attackFamilies={attackFamilies}
        explorerFamily={explorerFamily}
        onSelectFamily={(id) => {
          setExplorerFamily(id);
          const famStyles = Object.keys(familyExamples?.[id]?.unmarked_by_style || {});
          if (famStyles.length > 0 && !famStyles.includes(explorerStyle)) {
            setExplorerStyle(famStyles[0]);
          }
        }}
        availableExplorerStyles={availableExplorerStyles}
        explorerStyle={explorerStyle}
        onSelectStyle={setExplorerStyle}
        currentFamilyMeta={currentFamilyMeta}
        currentMarkedText={currentMarkedText}
        currentUnmarkedText={currentUnmarkedText}
      />

      {/* SECTION 2: EMPIRICAL BENCHMARK GROUPED BAR CHARTS */}
      <ComparisonResults
        chartData={chartData}
        loadingSummary={loadingSummary}
        summaryError={summaryError}
        summary={summary}
        chartColors={chartColors}
      />

      {/* SECTION 3: LIVE ADVERSARIAL WORKBENCH */}
      <SynthesisWorkbench
        presets={presets}
        selectedPresetKey={selectedPresetKey}
        loadingPresets={loadingPresets}
        baseSubject={baseSubject}
        setBaseSubject={setBaseSubject}
        baseSender={baseSender}
        setBaseSender={setBaseSender}
        baseBody={baseBody}
        setBaseBody={setBaseBody}
        attackFamilies={attackFamilies}
        attackFamily={attackFamily}
        setAttackFamily={setAttackFamily}
        attackStyle={attackStyle}
        setAttackStyle={setAttackStyle}
        attackPosition={attackPosition}
        setAttackPosition={setAttackPosition}
        evalMethod={evalMethod}
        setEvalMethod={setEvalMethod}
        evalModel={evalModel}
        setEvalModel={setEvalModel}
        isEvaluating={isEvaluating}
        attackRan={attackRan}
        cleanResult={cleanResult}
        injectedResult={injectedResult}
        injectDetails={injectDetails}
        cleanFullText={cleanFullText}
        injectedFullText={injectedFullText}
        errorMessage={errorMessage}
        showPayloadDetails={showPayloadDetails}
        setShowPayloadDetails={setShowPayloadDetails}
        copiedPayload={copiedPayload}
        onSelectPreset={handleSelectPreset}
        onResetWorkbench={handleResetWorkbench}
        onRunAttack={handleRunAttack}
        onCopyPayload={handleCopyPayload}
      />
    </motion.div>
  );
};

export default InjectionLabPage;
