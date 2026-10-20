import React, { useEffect, useRef, useState } from 'react';
import { BookOpen, FlaskConical, Copy, Check, ChevronDown } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import type { AttackFamilyMeta } from './types';

const MarkedUnmarkedEnvelopeGraphic: React.FC = () => (
  <div className="w-full max-w-[330px] shrink-0" aria-label="Marked envelope with warning sticker compared with an unmarked envelope">
    <svg viewBox="0 0 330 150" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full h-auto">
      <defs>
        <filter id="markedEnvelopeGlow" x="-30%" y="-30%" width="160%" height="160%">
          <feDropShadow dx="0" dy="0" stdDeviation="3" floodColor="#ef4444" floodOpacity="0.7" />
        </filter>
      </defs>

      <text x="82" y="16" textAnchor="middle" fill="#fda4af" fontSize="10" fontWeight="700" fontFamily="ui-sans-serif, system-ui">
        MARKED
      </text>
      <text x="248" y="16" textAnchor="middle" fill="#5eead4" fontSize="10" fontWeight="700" fontFamily="ui-sans-serif, system-ui">
        UNMARKED
      </text>

      <g transform="translate(18 30)">
        <rect width="128" height="84" rx="8" fill="#172033" stroke="#475569" strokeWidth="1.5" />
        <path d="M3 5L64 51L125 5" stroke="#94a3b8" strokeWidth="2" />
        <path d="M3 79L48 39M125 79L80 39" stroke="#64748b" strokeWidth="1.5" />
        <motion.g
          initial={{ scale: 1, opacity: 1 }}
          whileInView={{ scale: [1, 1.14, 1], opacity: [1, 1, 1] }}
          viewport={{ once: true, amount: 0.8 }}
          transition={{ duration: 0.55, delay: 0.15, ease: 'easeInOut' }}
          style={{ transformOrigin: '64px 42px' }}
          filter="url(#markedEnvelopeGlow)"
        >
          <circle cx="64" cy="42" r="19" fill="#991b1b" stroke="#f87171" strokeWidth="1.5" />
          <path d="M64 30V45" stroke="#fff1f2" strokeWidth="3" strokeLinecap="round" />
          <circle cx="64" cy="52" r="2" fill="#fff1f2" />
        </motion.g>
      </g>

      <g transform="translate(184 30)">
        <rect width="128" height="84" rx="8" fill="#172033" stroke="#475569" strokeWidth="1.5" />
        <path d="M3 5L64 51L125 5" stroke="#94a3b8" strokeWidth="2" />
        <path d="M3 79L48 39M125 79L80 39" stroke="#64748b" strokeWidth="1.5" />
      </g>

      <text x="82" y="133" textAnchor="middle" fill="#fda4af" fontSize="9" fontFamily="ui-sans-serif, system-ui">
        obvious warning marker
      </text>
      <text x="248" y="133" textAnchor="middle" fill="#94a3b8" fontSize="9" fontFamily="ui-sans-serif, system-ui">
        blends into normal mail
      </text>
    </svg>
  </div>
);

interface TypingCodeBlockProps {
  content: string;
  className: string;
  seenCodeBlocks: React.MutableRefObject<Set<string>>;
}

const TypingCodeBlock: React.FC<TypingCodeBlockProps> = ({ content, className, seenCodeBlocks }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const intervalRef = useRef<number | null>(null);
  const [displayedContent, setDisplayedContent] = useState(() =>
    seenCodeBlocks.current.has(content) ? content : ''
  );
  const hasStartedTyping = useRef(seenCodeBlocks.current.has(content));

  useEffect(() => {
    if (seenCodeBlocks.current.has(content)) {
      setDisplayedContent(content);
      hasStartedTyping.current = true;
      return;
    }

    setDisplayedContent('');
    hasStartedTyping.current = false;
  }, [content, seenCodeBlocks]);

  useEffect(() => {
    const node = containerRef.current;
    if (!node || hasStartedTyping.current) return;

    const startTyping = () => {
      if (hasStartedTyping.current) return;
      hasStartedTyping.current = true;
      const intervalMs = content.length > 0 ? Math.max(4, 400 / content.length) : 4;
      let index = 0;
      intervalRef.current = window.setInterval(() => {
        index += 1;
        setDisplayedContent(content.slice(0, index));
        if (index >= content.length) {
          if (intervalRef.current !== null) window.clearInterval(intervalRef.current);
          intervalRef.current = null;
          seenCodeBlocks.current.add(content);
        }
      }, intervalMs);
    };

    if (!('IntersectionObserver' in window)) {
      return startTyping();
    }

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          const cleanup = startTyping();
          observer.disconnect();
          return cleanup;
        }
        return undefined;
      },
      { threshold: 0.2 }
    );
    observer.observe(node);
    return () => {
      observer.disconnect();
      if (intervalRef.current !== null) {
        window.clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [content, seenCodeBlocks]);

  return (
    <div ref={containerRef} className={className}>
      {displayedContent}
    </div>
  );
};

export interface AttackFamilyExplorerProps {
  attackFamilies: AttackFamilyMeta[];
  explorerFamily: string;
  onSelectFamily: (id: string) => void;
  availableExplorerStyles: Array<{ id: string; label: string }>;
  explorerStyle: string;
  onSelectStyle: (id: string) => void;
  currentFamilyMeta: AttackFamilyMeta;
  currentMarkedText: string;
  currentUnmarkedText: string;
}

export const AttackFamilyExplorer: React.FC<AttackFamilyExplorerProps> = ({
  attackFamilies,
  explorerFamily,
  onSelectFamily,
  availableExplorerStyles,
  explorerStyle,
  onSelectStyle,
  currentFamilyMeta,
  currentMarkedText,
  currentUnmarkedText,
}) => {
  const [copiedSnippetKey, setCopiedSnippetKey] = useState<'marked' | 'unmarked' | null>(null);
  const [isDifferenceExpanded, setIsDifferenceExpanded] = useState(false);
  const seenCodeBlocks = useRef<Set<string>>(new Set());

  const handleCopy = (key: 'marked' | 'unmarked', text: string) => {
    if (!text) return;
    navigator.clipboard.writeText(text);
    setCopiedSnippetKey(key);
    setTimeout(() => {
      setCopiedSnippetKey(null);
    }, 1500);
  };

  return (
    <section id="explainer-section" className="space-y-6 scroll-mt-20">
      <div className="border-b border-slate-800 pb-4">
        <div className="flex items-center gap-2 text-teal-400 text-xs font-semibold uppercase tracking-wider">
          <BookOpen className="h-4 w-4" />
          <span>Attack Mechanism &bull; Delimiter vs. Camouflage</span>
        </div>
        <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight mt-1 font-['Plus_Jakarta_Sans',sans-serif]">
          What is the Difference Between "Marked" and "Unmarked" Prompt Injections?
        </h2>
        <p className="text-xs sm:text-sm text-slate-400 mt-0.5">
          Understanding why academic attack benchmarks fail to anticipate real-world cybercrime tactics.
        </p>
      </div>

      {/* Primary Explainer Box */}
      <div className="relative rounded-2xl border border-teal-500/30 bg-gradient-to-br from-teal-950/20 via-slate-900/90 to-slate-900/80 p-6 sm:p-8 elevation-card backdrop-blur-md overflow-hidden">
        <div className="absolute top-0 left-0 h-full w-1.5 bg-gradient-to-b from-teal-400 to-cyan-500" />

        <div className="flex flex-col lg:flex-row lg:items-center gap-6">
          <div className="text-slate-200 text-sm sm:text-base leading-relaxed flex-1 min-w-0">
            <p>
              <strong className="text-cyan-300 font-semibold">Marked</strong> injections use synthetic delimiters, while <strong className="text-teal-300 font-semibold">unmarked</strong> injections disguise directives as ordinary enterprise email.
              Unmarked attacks can trigger catastrophic evasion in monolithic RAG (M3), while decoupled IFSI (M4) preserves detection.
            </p>

            <button
              type="button"
              onClick={() => setIsDifferenceExpanded((expanded) => !expanded)}
              aria-expanded={isDifferenceExpanded}
              className="mt-3 inline-flex items-center gap-1.5 text-xs font-semibold text-teal-300 hover:text-teal-200 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 rounded"
            >
              Read more
              <ChevronDown
                className={`h-3.5 w-3.5 transition-transform duration-200 ${
                  isDifferenceExpanded ? 'rotate-180' : ''
                }`}
              />
            </button>

            <AnimatePresence initial={false}>
              {isDifferenceExpanded && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.2, ease: 'easeInOut' }}
                  className="overflow-hidden"
                >
                  <div className="pt-3 mt-3 border-t border-slate-800 text-xs sm:text-sm text-slate-300">
                    Marked payloads often include tags such as{' '}
                    <code className="px-1.5 py-0.5 rounded bg-slate-950 border border-slate-800 text-cyan-300 font-mono text-xs">
                      [BEGIN EMBEDDED CLASSIFIER MESSAGE]
                    </code>
                    , making them easier for structural heuristic filters to intercept. Unmarked payloads instead blend into
                    forwarded notices, IT instructions, or compliance disclaimers, so M3 can ingest them as legitimate context;
                    M4 isolates untrusted input before classification.
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
          <MarkedUnmarkedEnvelopeGraphic />
        </div>
      </div>

      {/* ATTACK FAMILY EXPLORER: Interactive Side-by-Side Comparison */}
      <div className="rounded-2xl border border-slate-800/80 bg-slate-900/60 p-5 sm:p-7 elevation-card backdrop-blur-sm space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
          <div>
            <div className="flex items-center gap-1.5 text-xs text-teal-400 font-semibold uppercase tracking-wider">
              <FlaskConical className="h-3.5 w-3.5" />
              <span>Attack Family Explorer</span>
            </div>
            <h3 className="text-base font-bold text-white tracking-tight mt-0.5">
              Authentic Marked vs. Unmarked Attack Payloads
            </h3>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-400">Unmarked Style:</span>
            <div className="inline-flex rounded-lg bg-slate-950 border border-slate-800 p-0.5 text-xs">
              {availableExplorerStyles.map((st) => (
                <button
                  key={st.id}
                  type="button"
                  onClick={() => onSelectStyle(st.id)}
                  className={`px-2.5 py-1 rounded-md text-xs font-medium transition-all duration-150 hover:scale-[1.02] hover:brightness-105 active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 ${
                    explorerStyle === st.id
                      ? 'bg-teal-500/20 text-teal-300 font-semibold'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
                  }`}
                >
                  {st.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Attack Family Selector Tabs */}
        <div className="flex flex-wrap gap-2">
          {attackFamilies.map((fam) => {
            const isSelected = explorerFamily === fam.id;
            return (
              <button
                key={fam.id}
                type="button"
                onClick={() => onSelectFamily(fam.id)}
                className={`px-3 py-2 rounded-xl border text-xs font-medium transition-all duration-150 hover:scale-[1.02] hover:brightness-105 active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 text-left ${
                  isSelected
                    ? 'border-teal-500 bg-teal-500/15 text-white ring-1 ring-teal-500/30 font-semibold'
                    : 'border-slate-800 bg-slate-950/60 text-slate-400 hover:border-slate-700 hover:text-slate-200'
                }`}
              >
                <div className="flex items-center gap-1.5">
                  <span className={`h-2 w-2 rounded-full ${isSelected ? 'bg-teal-400' : 'bg-slate-600'}`} />
                  <span>{fam.name}</span>
                </div>
              </button>
            );
          })}
        </div>

        {/* Active Family Metadata */}
        <div className="rounded-xl bg-slate-950/80 border border-slate-800/80 p-3 text-xs text-slate-300 flex items-center justify-between gap-4">
          <AnimatePresence mode="wait" initial={false}>
            <motion.div
              key={explorerFamily}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.25, ease: 'easeInOut' }}
              className="space-y-0.5"
            >
              <span className="font-bold text-white mr-1.5">{currentFamilyMeta.name}:</span>
              <span className="text-slate-400">{currentFamilyMeta.description}</span>
            </motion.div>
          </AnimatePresence>
        </div>

        {/* Side-by-Side Marked vs. Unmarked Comparison Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* LEFT: Marked Injection */}
          <div className="rounded-xl border border-cyan-500/30 bg-slate-900/80 p-4 space-y-3 flex flex-col justify-between">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <div>
                  <span className="text-[11px] font-mono uppercase tracking-wider text-cyan-400 font-semibold">
                    Academic Artifact
                  </span>
                  <h3 className="text-lg font-bold text-white flex items-center gap-2">
                    <span>🏷️</span> Marked Injections
                  </h3>
                </div>

              </div>

              <p className="text-xs text-slate-300 leading-relaxed">
                Surrounded by synthetic delimiter tokens like <code className="text-cyan-300">[BEGIN EMBEDDED CLASSIFIER MESSAGE]</code>.
                Easily caught by structural heuristic checks.
              </p>

              {/* Marked Example Box */}
              <div className="relative min-h-[140px] rounded-xl bg-slate-950 border border-slate-800/80 p-3.5 overflow-hidden flex flex-col justify-center">
                <AnimatePresence mode="popLayout" initial={false}>
                  <motion.div
                    key={explorerFamily}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.25, ease: 'easeInOut' }}
                    className="w-full"
                  >
                    <TypingCodeBlock
                      content={currentMarkedText}
                      seenCodeBlocks={seenCodeBlocks}
                      className="font-mono text-xs text-cyan-300/90 leading-relaxed overflow-x-auto whitespace-pre-wrap select-text"
                    />
                  </motion.div>
                </AnimatePresence>
              </div>
            </div>

            <div className="pt-2 border-t border-slate-800/60 flex items-center justify-end text-xs">
              <button
                type="button"
                onClick={() => handleCopy('marked', currentMarkedText)}
                className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg border border-slate-700 bg-slate-800/80 hover:bg-slate-700 text-slate-300 text-xs font-medium transition-all duration-150 hover:scale-[1.02] hover:brightness-105 active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-400"
              >
                {copiedSnippetKey === 'marked' ? (
                  <>
                    <Check className="h-3 w-3 text-emerald-400" />
                    <span className="text-emerald-400">Copied</span>
                  </>
                ) : (
                  <>
                    <Copy className="h-3 w-3 text-slate-400" />
                    <span>Copy Snippet</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* RIGHT: Unmarked Injection */}
          <div className="rounded-xl border border-teal-500/40 bg-slate-900/90 p-4 space-y-3 flex flex-col justify-between ring-1 ring-teal-500/20">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <div>
                  <span className="text-[11px] font-mono uppercase tracking-wider text-teal-400 font-semibold">
                    Real-World Threat
                  </span>
                  <h3 className="text-lg font-bold text-white flex items-center gap-2">
                    <span>🎭</span> Unmarked Injections
                  </h3>
                </div>

              </div>

              <p className="text-xs text-slate-300 leading-relaxed">
                Disguised as standard corporate communication artefacts. Semantic reasoning models ingest these as authentic
                email context, rendering keyword filters obsolete.
              </p>

              {/* Unmarked Example Box */}
              <div className="relative min-h-[140px] rounded-xl bg-slate-950 border border-slate-800/80 p-3.5 overflow-hidden flex flex-col justify-center">
                <AnimatePresence mode="popLayout" initial={false}>
                  <motion.div
                    key={`${explorerFamily}-${explorerStyle}`}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.25, ease: 'easeInOut' }}
                    className="w-full"
                  >
                    <TypingCodeBlock
                      content={currentUnmarkedText}
                      seenCodeBlocks={seenCodeBlocks}
                      className="font-mono text-xs text-teal-300/90 leading-relaxed overflow-x-auto whitespace-pre-wrap select-text"
                    />
                  </motion.div>
                </AnimatePresence>
              </div>
            </div>

            <ul className="space-y-1.5 text-xs text-slate-400 pt-2 border-t border-slate-800/60">
              <li className="flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-teal-400 flex-shrink-0" />
                <span>Indistinguishable from legitimate IT headers and email signatures</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-teal-400 flex-shrink-0" />
                <span>Causes catastrophic 78%+ evasion collapse in standard RAG pipelines</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
};

export default AttackFamilyExplorer;
