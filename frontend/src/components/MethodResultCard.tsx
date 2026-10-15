import React, { useState } from 'react';
import {
  Clock,
  Database,
  ChevronDown,
  ChevronUp,
  Copy,
  Check,
  Cpu,
  Bot,
  Layers,
  ShieldCheck,
} from 'lucide-react';
import { motion } from 'framer-motion';
import { type ClassificationResult } from '../api/client';
import { Card, type CardVariant } from './Card';
import { Badge } from './Badge';

export interface MethodResultCardProps {
  result: ClassificationResult;
  consensusNote?: string;
  consensusStatusLabel?: string;
  isOpenDetails?: boolean;
  onToggleDetails?: () => void;
  onCopySnippet?: (key: string, text: string) => void;
  copiedKey?: string | null;
  cardVariant?: CardVariant;
  headerTag?: string;
  emailSnippet?: string;
  emailLabel?: string;
}

export const MethodResultCard: React.FC<MethodResultCardProps> = ({
  result,
  consensusNote,
  consensusStatusLabel,
  isOpenDetails: controlledIsOpen,
  onToggleDetails: controlledOnToggle,
  onCopySnippet,
  copiedKey,
  cardVariant,
  headerTag,
  emailSnippet,
  emailLabel,
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

  // Method Icon
  const getMethodIcon = () => {
    if (result.method.startsWith('M1')) return <Cpu className="h-4 w-4" />;
    if (result.method.startsWith('M2')) return <Bot className="h-4 w-4" />;
    if (result.method.startsWith('M3')) return <Layers className="h-4 w-4" />;
    return <ShieldCheck className="h-4 w-4" />;
  };

  const chosenVariant = cardVariant || (isDecoupledM4 ? 'accent' : 'default');

  return (
    <Card
      variant={chosenVariant}
      padding="none"
      className="flex flex-col justify-between overflow-hidden"
    >
      <div className="p-5 space-y-4">
        {/* Method Title Header */}
        <div className="flex items-center justify-between pb-3 border-b border-slate-800/80">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-slate-800 text-teal-400">
              {getMethodIcon()}
            </div>
            <div>
              <div className="text-sm font-bold text-white tracking-tight flex items-center gap-2">
                <span>{result.method.split('(')[0].trim()}</span>
                {headerTag && (
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-teal-500/10 text-teal-300 border border-teal-500/20 font-semibold">
                    {headerTag}
                  </span>
                )}
              </div>
              <div className="text-[11px] text-slate-400 font-mono">
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
            <Badge
              variant={isPhishing ? 'phishing' : 'legitimate'}
              size="md"
              dot
            >
              {isPhishing ? 'PHISHING' : 'LEGITIMATE'}
            </Badge>
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

        {/* Confidence Progress Bar */}
        <div className="space-y-1.5 pt-1">
          <div className="flex justify-between text-xs">
            <span className="text-slate-400">Confidence Score:</span>
            <span className="font-bold font-mono text-white">
              {confidencePercent}%
            </span>
          </div>
          <div className="h-2 w-full bg-slate-950 rounded-full overflow-hidden border border-slate-800">
            <motion.div
              initial={{ width: '0%' }}
              animate={{ width: `${Math.max(5, Math.min(100, Number(confidencePercent)))}%` }}
              transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
              className={`h-full rounded-full ${
                isPhishing
                  ? 'bg-gradient-to-r from-rose-500 to-red-400 shadow-sm shadow-rose-500/40'
                  : 'bg-gradient-to-r from-teal-500 to-emerald-400 shadow-sm shadow-teal-500/40'
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
          className="w-full px-4 py-2.5 flex items-center justify-between text-xs font-medium text-slate-300 hover:text-teal-300 hover:bg-slate-900/60 transition-colors"
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
          <div className="p-4 pt-2 space-y-3.5 text-xs text-slate-300 border-t border-slate-800/60 bg-slate-950/80 max-h-96 overflow-y-auto">
            {/* 1. Reasoning Tokens / Points */}
            {result.reasons && result.reasons.length > 0 && (
              <div className="space-y-1.5">
                <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">
                  Model Reasoning Tokens:
                </span>
                <ul className="space-y-1 text-slate-300 text-xs">
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
              <div className="space-y-2 pt-2 border-t border-slate-800/60">
                <span className="text-[11px] font-semibold text-teal-300 uppercase tracking-wider block">
                  Two-Stage Isolated Execution Trace:
                </span>
                <div className="rounded-lg bg-slate-900/80 p-2.5 border border-slate-800 space-y-1">
                  <div className="font-semibold text-slate-200">
                    Stage 1: Prompt Injection Detector
                  </div>
                  <div className="text-[11px] text-slate-400">
                    Injection Detected: <span className="font-mono text-white">{result.has_injection ? 'TRUE' : 'FALSE'}</span>
                  </div>
                  {result.raw_response_call1 && (
                    <div className="text-[10px] font-mono text-slate-400 break-words mt-1 bg-slate-950 p-1.5 rounded">
                      {result.raw_response_call1}
                    </div>
                  )}
                </div>

                <div className="rounded-lg bg-slate-900/80 p-2.5 border border-slate-800 space-y-1">
                  <div className="font-semibold text-slate-200">
                    Stage 2: Boolean Phishing Classifier
                  </div>
                  <div className="text-[11px] text-slate-400">
                    Phishing Verdict: <span className="font-mono text-white">{result.is_phishing_only ? 'TRUE (PHISHING)' : 'FALSE (LEGITIMATE)'}</span>
                  </div>
                  {result.raw_response_call2 && (
                    <div className="text-[10px] font-mono text-slate-400 break-words mt-1 bg-slate-950 p-1.5 rounded">
                      {result.raw_response_call2}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* 3. Retrieved FAISS Exemplars (For M3 & M4) */}
            {result.retrieved_samples && result.retrieved_samples.length > 0 && (
              <div className="space-y-2 pt-2 border-t border-slate-800/60">
                <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">
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
                        className="rounded-lg bg-slate-900/80 p-2 border border-slate-800 text-[11px] space-y-1"
                      >
                        <div className="flex items-center justify-between text-[10px]">
                          <span className="font-mono text-slate-400">{sampleId}</span>
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
                          <p className="text-slate-400 font-mono text-[10px] line-clamp-2">
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
              <div className="pt-2 border-t border-slate-800/60 space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] text-slate-400 uppercase font-mono">
                    Raw Completion String:
                  </span>
                  <button
                    type="button"
                    onClick={() => handleCopy(result.method, result.raw_response || '')}
                    className="text-[10px] text-teal-400 hover:text-teal-300 inline-flex items-center gap-1"
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
                <pre className="p-2 rounded bg-slate-950 border border-slate-800 text-[10px] font-mono text-slate-300 whitespace-pre-wrap break-all">
                  {result.raw_response}
                </pre>
              </div>
            )}
          </div>
        )}
      </div>
    </Card>
  );
};
