import React from 'react';
import { motion } from 'framer-motion';
import { fadeInUp } from '../lib/motion';

interface ApproachFlowDiagramProps {
  hoveredMethod?: 'M1' | 'M2' | 'M3' | 'M4' | null;
  shouldReduceMotion?: boolean;
}

export const ApproachFlowDiagram: React.FC<ApproachFlowDiagramProps> = ({
  hoveredMethod = null,
  shouldReduceMotion = false,
}) => {
  const isM3Active = hoveredMethod === 'M3';
  const isM4Active = hoveredMethod === 'M4';

  return (
    <motion.div
      variants={fadeInUp}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: '-40px' }}
      className="w-full rounded-2xl border border-slate-800/80 bg-gradient-to-b from-slate-900/90 to-slate-950/80 p-3 sm:p-4 backdrop-blur-sm shadow-xl overflow-hidden"
    >
      {/* Header Bar with Legend and Interactive Callout */}
      <div className="flex flex-wrap items-center justify-between gap-2 mb-2 px-1">
        <div className="flex items-center gap-2 text-[11px] font-semibold uppercase tracking-wider">
          <span className="text-slate-400">Pipeline Comparison:</span>
          <span className={`transition-colors duration-200 ${isM3Active ? 'text-rose-400 font-bold' : 'text-rose-400/80'}`}>
            M3 Single-Call (Vulnerable)
          </span>
          <span className="text-slate-600">vs</span>
          <span className={`transition-colors duration-200 ${isM4Active ? 'text-teal-300 font-bold' : 'text-teal-400/80'}`}>
            M4 Two-Stage (IFSI Decoupled)
          </span>
        </div>

        <span className="text-[10px] text-slate-500 hidden md:inline">
          Hover cards below to inspect attack response
        </span>
      </div>

      {/* SVG Flow Canvas */}
      <div className="w-full overflow-x-auto">
        <svg
          viewBox="0 0 860 120"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="w-full min-w-[680px] h-auto select-none"
        >
          <defs>
            {/* Gradients */}
            <linearGradient id="m3LineGradient" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor="#475569" stopOpacity="0.4" />
              <stop offset="40%" stopColor="#f43f5e" stopOpacity="0.8" />
              <stop offset="70%" stopColor="#e11d48" stopOpacity="0.9" />
              <stop offset="100%" stopColor="#fda4af" stopOpacity="0.3" />
            </linearGradient>

            <linearGradient id="m4LineGradient" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor="#475569" stopOpacity="0.4" />
              <stop offset="35%" stopColor="#0d9488" stopOpacity="0.8" />
              <stop offset="60%" stopColor="#14b8a6" stopOpacity="0.9" />
              <stop offset="100%" stopColor="#2dd4bf" stopOpacity="0.8" />
            </linearGradient>

            {/* Glowing filter for traveling particles */}
            <filter id="particleGlowRose" x="-50%" y="-50%" width="200%" height="200%">
              <feDropShadow dx="0" dy="0" stdDeviation="3" floodColor="#f43f5e" floodOpacity="0.8" />
            </filter>
            <filter id="particleGlowTeal" x="-50%" y="-50%" width="200%" height="200%">
              <feDropShadow dx="0" dy="0" stdDeviation="3" floodColor="#2dd4bf" floodOpacity="0.8" />
            </filter>

            {/* Checkpoint Radar Wave */}
            <filter id="checkpointPulse" x="-30%" y="-30%" width="160%" height="160%">
              <feDropShadow dx="0" dy="0" stdDeviation="4" floodColor="#14b8a6" floodOpacity="0.5" />
            </filter>
          </defs>

          {/* =================================================================
              1. BACKGROUND CONNECTOR LINES
              ================================================================= */}
          {/* Root to Branch Spline */}
          <path
            d="M 68 60 C 95 60, 115 35, 145 35"
            stroke="url(#m3LineGradient)"
            strokeWidth="1.5"
            strokeDasharray="3 3"
          />
          <path
            d="M 68 60 C 95 60, 115 85, 145 85"
            stroke="url(#m4LineGradient)"
            strokeWidth="1.5"
            strokeDasharray="3 3"
          />

          {/* M3 Single-Call Straight Path */}
          <line
            x1="145"
            y1="35"
            x2="520"
            y2="35"
            stroke="#f43f5e"
            strokeWidth={isM3Active ? '2.2' : '1.5'}
            strokeOpacity={isM3Active ? '0.9' : '0.6'}
            className="transition-all duration-200"
          />
          {/* M3 Broken/Flickering Attack Breakpoint Line */}
          <line
            x1="520"
            y1="35"
            x2="740"
            y2="35"
            stroke="#f43f5e"
            strokeWidth="1.5"
            strokeDasharray="4 4"
            strokeOpacity="0.35"
          />

          {/* M4 Decoupled Two-Stage Path with Checkpoint */}
          <line
            x1="145"
            y1="85"
            x2="430"
            y2="85"
            stroke="#0d9488"
            strokeWidth={isM4Active ? '2.2' : '1.5'}
            strokeOpacity={isM4Active ? '0.9' : '0.6'}
            className="transition-all duration-200"
          />
          <line
            x1="430"
            y1="85"
            x2="740"
            y2="85"
            stroke="#14b8a6"
            strokeWidth={isM4Active ? '2.2' : '1.5'}
            strokeOpacity={isM4Active ? '0.9' : '0.6'}
            className="transition-all duration-200"
          />

          {/* =================================================================
              2. COMMON ROOT NODE (EMAIL INPUT)
              ================================================================= */}
          <g transform="translate(20, 42)">
            <rect
              x="0"
              y="0"
              width="48"
              height="36"
              rx="8"
              fill="#0f172a"
              stroke="#334155"
              strokeWidth="1.2"
            />
            {/* Tiny Envelope Icon */}
            <path
              d="M 16 14 L 24 19 L 32 14"
              stroke="#94a3b8"
              strokeWidth="1.2"
              fill="none"
            />
            <rect x="14" y="12" width="20" height="14" rx="2" stroke="#94a3b8" strokeWidth="1.2" fill="none" />
            <text x="24" y="32" fill="#94a3b8" fontSize="7" fontWeight="600" textAnchor="middle">
              EMAIL
            </text>
          </g>

          {/* =================================================================
              3. M3 UPPER BRANCH (SINGLE STRAIGHT PATH)
              ================================================================= */}
          {/* M3 Node: Monolithic Single-Prompt Model */}
          <g transform="translate(260, 17)">
            <rect
              x="0"
              y="0"
              width="180"
              height="36"
              rx="8"
              fill="#1e1b2e"
              stroke={isM3Active ? '#f43f5e' : '#4c1d3d'}
              strokeWidth={isM3Active ? '1.5' : '1'}
              className="transition-all duration-200"
            />
            <circle cx="16" cy="18" r="4" fill="#f43f5e" />
            <text x="26" y="16" fill="#ffffff" fontSize="9" fontWeight="700">
              M3: Monolithic LLM
            </text>
            <text x="26" y="27" fill="#fda4af" fontSize="7.5" fontWeight="500">
              Untrusted Email + Instructions in 1 Call
            </text>
          </g>

          {/* M3 Attack Collision / Hijack Marker */}
          <g transform="translate(520, 20)">
            <rect
              x="-6"
              y="0"
              width="100"
              height="30"
              rx="6"
              fill="rgba(244, 63, 94, 0.12)"
              stroke="#f43f5e"
              strokeWidth="1"
              strokeDasharray="2 2"
            />
            <text x="44" y="14" fill="#fb7185" fontSize="8" fontWeight="700" textAnchor="middle">
              ⚡ INJECTION HIJACK
            </text>
            <text x="44" y="24" fill="#fda4af" fontSize="6.5" textAnchor="middle">
              Classifier Directives Overridden
            </text>
          </g>

          {/* M3 Verdict Node (Compromised) */}
          <g transform="translate(740, 19)">
            <rect
              x="0"
              y="0"
              width="100"
              height="32"
              rx="7"
              fill="rgba(136, 19, 55, 0.4)"
              stroke="#f43f5e"
              strokeWidth="1.2"
            />
            <text x="50" y="15" fill="#fecdd3" fontSize="8" fontWeight="700" textAnchor="middle">
              VERDICT: EVADED
            </text>
            <text x="50" y="25" fill="#fda4af" fontSize="7" fontWeight="600" textAnchor="middle">
              79.0% Attack Evasion
            </text>
          </g>

          {/* =================================================================
              4. M4 LOWER BRANCH (TWO-STAGE DECOUPLED PATH)
              ================================================================= */}
          {/* M4 Stage 1: Extractor */}
          <g transform="translate(195, 67)">
            <rect
              x="0"
              y="0"
              width="135"
              height="36"
              rx="8"
              fill="#062828"
              stroke={isM4Active ? '#2dd4bf' : '#0d9488'}
              strokeWidth={isM4Active ? '1.5' : '1'}
              className="transition-all duration-200"
            />
            <circle cx="14" cy="18" r="4" fill="#14b8a6" />
            <text x="24" y="16" fill="#ffffff" fontSize="9" fontWeight="700">
              Stage 1: Extractor
            </text>
            <text x="24" y="27" fill="#5eead4" fontSize="7.5">
              Isolates text into schema
            </text>
          </g>

          {/* M4 Checkpoint Node (Central Validation Gate) */}
          <g transform="translate(375, 67)" filter="url(#checkpointPulse)">
            <rect
              x="0"
              y="0"
              width="145"
              height="36"
              rx="8"
              fill="#083344"
              stroke="#22d3ee"
              strokeWidth="1.3"
            />
            {/* Checkpoint Shield Glyph */}
            <path
              d="M 14 11 L 22 8 L 30 11 C 30 18 22 23 22 26 C 22 23 14 18 14 11 Z"
              fill="rgba(34, 211, 238, 0.2)"
              stroke="#22d3ee"
              strokeWidth="1.2"
            />
            <text x="36" y="16" fill="#ffffff" fontSize="9" fontWeight="800" letterSpacing="0.02em">
              🛡️ Schema Checkpoint
            </text>
            <text x="36" y="27" fill="#67e8f9" fontSize="7.5" fontWeight="600">
              Pauses &amp; Validates Structure
            </text>
          </g>

          {/* M4 Stage 2: Classifier */}
          <g transform="translate(565, 67)">
            <rect
              x="0"
              y="0"
              width="135"
              height="36"
              rx="8"
              fill="#062828"
              stroke={isM4Active ? '#2dd4bf' : '#0d9488'}
              strokeWidth={isM4Active ? '1.5' : '1'}
              className="transition-all duration-200"
            />
            <circle cx="14" cy="18" r="4" fill="#14b8a6" />
            <text x="24" y="16" fill="#ffffff" fontSize="9" fontWeight="700">
              Stage 2: Classifier
            </text>
            <text x="24" y="27" fill="#5eead4" fontSize="7.5">
              Evaluates sanitized schema
            </text>
          </g>

          {/* M4 Verdict Node (Protected) */}
          <g transform="translate(740, 69)">
            <rect
              x="0"
              y="0"
              width="100"
              height="32"
              rx="7"
              fill="rgba(19, 78, 74, 0.45)"
              stroke="#14b8a6"
              strokeWidth="1.2"
            />
            <text x="50" y="15" fill="#ccfbf1" fontSize="8" fontWeight="700" textAnchor="middle">
              VERDICT: SECURED
            </text>
            <text x="50" y="25" fill="#5eead4" fontSize="7" fontWeight="600" textAnchor="middle">
              96.1% Catch Restored
            </text>
          </g>

          {/* =================================================================
              5. ANIMATED PARTICLES
              ================================================================= */}
          {!shouldReduceMotion && (
            <>
              {/* Particle M3 (Travels along upper path, flickers and breaks partway) */}
              <motion.circle
                r="4.5"
                fill="#f43f5e"
                filter="url(#particleGlowRose)"
                animate={{
                  cx: [68, 145, 260, 360, 480, 520, 535, 545, 550],
                  cy: [60, 35, 35, 35, 35, 35, 35, 35, 35],
                  opacity: [0, 1, 1, 1, 1, 0.9, 0.2, 0.8, 0],
                  scale: [0.8, 1.2, 1, 1.1, 1, 1.4, 0.4, 0.8, 0],
                }}
                transition={{
                  duration: 2.8,
                  repeat: Infinity,
                  ease: 'easeInOut',
                  times: [0, 0.15, 0.35, 0.55, 0.72, 0.82, 0.88, 0.94, 1],
                  repeatDelay: 0.8,
                }}
              />

              {/* Particle M4 (Travels along lower path, pauses at Checkpoint, then proceeds to end) */}
              <motion.circle
                r="4.5"
                fill="#2dd4bf"
                filter="url(#particleGlowTeal)"
                animate={{
                  // Starts at Email (68), goes through Extractor (195-330),
                  // reaches Checkpoint at ~447, PAUSES for 0.7s,
                  // then resumes through Classifier (565-700) to Verdict (740-790)
                  cx: [68, 145, 260, 447, 447, 447, 630, 740, 790],
                  cy: [60, 85, 85, 85, 85, 85, 85, 85, 85],
                  opacity: [0, 1, 1, 1, 1, 1, 1, 1, 0],
                  scale: [0.8, 1.2, 1, 1.4, 1.1, 1.3, 1, 1.2, 0.5],
                }}
                transition={{
                  duration: 3.6,
                  repeat: Infinity,
                  ease: 'easeInOut',
                  times: [0, 0.12, 0.28, 0.45, 0.55, 0.65, 0.8, 0.93, 1],
                  repeatDelay: 0.8,
                }}
              />

              {/* Checkpoint Ring Pulse while M4 dot pauses */}
              <motion.circle
                cx="447"
                cy="85"
                r="6"
                stroke="#22d3ee"
                strokeWidth="1.5"
                fill="none"
                animate={{
                  r: [6, 18, 22],
                  opacity: [0, 0.8, 0],
                }}
                transition={{
                  duration: 1.2,
                  repeat: Infinity,
                  ease: 'easeOut',
                  delay: 1.6, // Matches particle pause window
                }}
              />
            </>
          )}
        </svg>
      </div>
    </motion.div>
  );
};
