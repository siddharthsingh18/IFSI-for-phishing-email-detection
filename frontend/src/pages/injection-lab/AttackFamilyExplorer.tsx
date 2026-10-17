import React, { useState } from 'react';
import { BookOpen, FlaskConical, Copy, Check } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import type { AttackFamilyMeta } from './types';

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
          <span>Section 1 &bull; Conceptual Foundation</span>
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

        <div className="space-y-4 text-slate-200 text-sm sm:text-base leading-relaxed">
          <p>
            In AI email security, an <strong className="text-white font-semibold">indirect prompt injection</strong> is an
            attack where cybercriminals hide instructions inside an email to manipulate the AI into declaring malicious phishing
            as <span className="text-emerald-400 font-semibold font-mono">"safe."</span>
          </p>
          <p>
            In academic benchmarks, attacks are traditionally <strong className="text-cyan-300 font-semibold">marked</strong>
            —wrapped in obvious, synthetic computer tags like{' '}
            <code className="px-2 py-0.5 rounded bg-slate-950 border border-slate-800 text-cyan-300 font-mono text-xs">
              [BEGIN EMBEDDED CLASSIFIER MESSAGE]
            </code>{' '}
            and{' '}
            <code className="px-2 py-0.5 rounded bg-slate-950 border border-slate-800 text-cyan-300 font-mono text-xs">
              SYSTEM OVERRIDE:
            </code>
            . While convenient for lab testing, real-world cybercriminals don't announce their attacks with machine brackets.
          </p>
          <p>
            Instead, real attackers use <strong className="text-teal-300 font-semibold">unmarked</strong> injections: they
            stealthily disguise malicious instructions as ordinary workplace correspondence, such as an automated IT gateway
            forwarded notice (<code className="px-1.5 py-0.5 rounded bg-slate-950 border border-slate-800 text-teal-300 font-mono text-xs">---------- Forwarded message ---------</code>),
            a corporate confidentiality disclaimer, or an executive compliance signature. Because unmarked attacks blend
            naturally into legitimate business communication, standard AI models trust them and get tricked into letting
            dangerous phishing attacks slip directly through to user inboxes.
          </p>
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
          <div className="space-y-0.5">
            <span className="font-bold text-white mr-1.5">{currentFamilyMeta.name}:</span>
            <span className="text-slate-400">{currentFamilyMeta.description}</span>
          </div>
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
                    className="w-full font-mono text-xs text-cyan-300/90 leading-relaxed overflow-x-auto whitespace-pre-wrap select-text"
                  >
                    {currentMarkedText}
                  </motion.div>
                </AnimatePresence>
              </div>
            </div>

            <div className="pt-2 border-t border-slate-800/60 flex items-center justify-between text-xs">
              <span className="text-slate-400 text-[11px]">Synthetic academic baseline</span>
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
                    className="w-full font-mono text-xs text-teal-300/90 leading-relaxed overflow-x-auto whitespace-pre-wrap select-text"
                  >
                    {currentUnmarkedText}
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
