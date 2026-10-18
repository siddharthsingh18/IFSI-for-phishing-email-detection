import React, { useId } from 'react';
import { motion } from 'framer-motion';

interface ShieldProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  shouldReduceMotion?: boolean;
}

const sizeMap = {
  sm: 'h-4 w-4',
  md: 'h-6 w-6',
  lg: 'h-8 w-8',
};

/**
 * M3 Broken / Shattered Shield (Red / Evasion accent: #f43f5e)
 * Animates a quick shatter/crack displacement (scale + rotate) on scroll into view, settling broken.
 */
export const BrokenShieldIcon: React.FC<ShieldProps> = ({
  size = 'md',
  className = '',
  shouldReduceMotion = false,
}) => {
  const rawId = useId();
  const filterId = `m3-glow-${rawId.replace(/[:]/g, '')}`;

  return (
    <motion.svg
      viewBox="0 0 28 28"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: '-20px' }}
      className={`${sizeMap[size]} ${className} flex-shrink-0 select-none overflow-visible`}
      aria-label="M3 Shattered Shield: Attack Evasion"
    >
      <defs>
        <filter id={filterId} x="-30%" y="-30%" width="160%" height="160%">
          <feDropShadow dx="0" dy="0" stdDeviation="2.5" floodColor="#f43f5e" floodOpacity="0.65" />
        </filter>
      </defs>

      {/* Left Shard */}
      <motion.path
        d="M 14 3.5 L 5.5 6.8 C 5.5 14.5 13 21.5 13.8 24.5 L 11.5 18 L 16 13.5 L 11.8 8.8 L 14 3.5 Z"
        fill="rgba(244, 63, 94, 0.22)"
        stroke="#f43f5e"
        strokeWidth="1.5"
        strokeLinejoin="round"
        filter={`url(#${filterId})`}
        variants={{
          hidden: {
            x: 0,
            y: 0,
            rotate: 0,
            scale: 0.95,
            opacity: 0,
          },
          visible: {
            x: shouldReduceMotion ? 0 : [0, -3.2, -1.8],
            y: shouldReduceMotion ? 0 : [0, -1.2, 0.4],
            rotate: shouldReduceMotion ? 0 : [0, -10, -4.5],
            scale: shouldReduceMotion ? 1 : [0.95, 1.12, 1],
            opacity: 1,
            transition: {
              duration: shouldReduceMotion ? 0.2 : 0.6,
              ease: [0.16, 1, 0.3, 1],
              delay: 0.12,
            },
          },
        }}
        style={{ transformOrigin: '9px 14px' }}
      />

      {/* Right Shard */}
      <motion.path
        d="M 14 3.5 L 22.5 6.8 C 22.5 14.5 15 21.5 14.2 24.5 L 11.5 18 L 16 13.5 L 11.8 8.8 L 14 3.5 Z"
        fill="rgba(244, 63, 94, 0.22)"
        stroke="#f43f5e"
        strokeWidth="1.5"
        strokeLinejoin="round"
        filter={`url(#${filterId})`}
        variants={{
          hidden: {
            x: 0,
            y: 0,
            rotate: 0,
            scale: 0.95,
            opacity: 0,
          },
          visible: {
            x: shouldReduceMotion ? 0 : [0, 3.2, 1.8],
            y: shouldReduceMotion ? 0 : [0, 1.4, 0.7],
            rotate: shouldReduceMotion ? 0 : [0, 10, 4.5],
            scale: shouldReduceMotion ? 1 : [0.95, 1.12, 1],
            opacity: 1,
            transition: {
              duration: shouldReduceMotion ? 0.2 : 0.6,
              ease: [0.16, 1, 0.3, 1],
              delay: 0.12,
            },
          },
        }}
        style={{ transformOrigin: '19px 14px' }}
      />

      {/* Crack Sparks & Debris */}
      {!shouldReduceMotion && (
        <motion.path
          d="M 14 9 L 16 11 M 12 15 L 14 17"
          stroke="#fca5a5"
          strokeWidth="1.3"
          strokeLinecap="round"
          variants={{
            hidden: { opacity: 0, scale: 0.5 },
            visible: {
              opacity: [0, 1, 0.7],
              scale: [0.5, 1.4, 1],
              transition: { delay: 0.22, duration: 0.4 },
            },
          }}
        />
      )}
    </motion.svg>
  );
};

/**
 * M4 Strained Shield (Amber / Tradeoff accent: #f59e0b, NOT green)
 * Intact shield with a visible hairline crack that holds under pressure with a stress pulse.
 */
export const StrainedShieldIcon: React.FC<ShieldProps> = ({
  size = 'md',
  className = '',
  shouldReduceMotion = false,
}) => {
  const rawId = useId();
  const filterId = `m4-glow-${rawId.replace(/[:]/g, '')}`;

  return (
    <motion.svg
      viewBox="0 0 28 28"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: '-20px' }}
      className={`${sizeMap[size]} ${className} flex-shrink-0 select-none overflow-visible`}
      aria-label="M4 Strained Shield: Holds with False-Alarm Tradeoff"
    >
      <defs>
        <filter id={filterId} x="-30%" y="-30%" width="160%" height="160%">
          <feDropShadow dx="0" dy="0" stdDeviation="2.5" floodColor="#f59e0b" floodOpacity="0.55" />
        </filter>
      </defs>

      {/* Main Intact Shield Body */}
      <motion.path
        d="M 14 3.5 L 22.5 6.8 C 22.5 15.5 14 24.5 14 24.5 C 14 24.5 5.5 15.5 5.5 6.8 L 14 3.5 Z"
        fill="rgba(245, 158, 11, 0.18)"
        stroke="#f59e0b"
        strokeWidth="1.6"
        strokeLinejoin="round"
        filter={`url(#${filterId})`}
        variants={{
          hidden: {
            scale: 0.9,
            opacity: 0,
          },
          visible: {
            scale: shouldReduceMotion ? 1 : [1, 1.15, 0.96, 1.05, 1],
            opacity: 1,
            transition: {
              duration: shouldReduceMotion ? 0.2 : 0.7,
              ease: [0.25, 0.1, 0.25, 1],
              delay: 0.18,
            },
          },
        }}
        style={{ transformOrigin: '14px 14px' }}
      />

      {/* Hairline Internal Crack (Stops halfway, doesn't break through) */}
      <motion.path
        d="M 14 4 L 11.8 8.8 L 16 13.5 L 12.8 17"
        stroke="#fcd34d"
        strokeWidth="1.3"
        strokeLinecap="round"
        strokeLinejoin="round"
        variants={{
          hidden: { pathLength: 0, opacity: 0 },
          visible: {
            pathLength: 1,
            opacity: [0, 1, 0.9],
            transition: {
              duration: shouldReduceMotion ? 0.15 : 0.45,
              delay: shouldReduceMotion ? 0.05 : 0.32,
              ease: 'easeOut',
            },
          },
        }}
      />

      {/* Stress Tension Arc Indicator */}
      {!shouldReduceMotion && (
        <motion.path
          d="M 8.2 11.5 C 7.5 13.5 7.5 16 8.2 18"
          stroke="#fbbf24"
          strokeWidth="1.1"
          strokeDasharray="2 2"
          strokeLinecap="round"
          variants={{
            hidden: { opacity: 0 },
            visible: {
              opacity: [0, 0.85, 0.45],
              transition: { delay: 0.38, duration: 0.5 },
            },
          }}
        />
      )}
    </motion.svg>
  );
};

/**
 * Side-by-side pair of labeled shield badges for Key Finding
 */
interface KeyFindingShieldComparisonProps {
  m3EvasionRate: string;
  m4UnmarkedFpr: string;
  shouldReduceMotion?: boolean;
}

export const KeyFindingShieldComparison: React.FC<KeyFindingShieldComparisonProps> = ({
  m3EvasionRate,
  m4UnmarkedFpr,
  shouldReduceMotion = false,
}) => {
  return (
    <motion.div
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: '-30px' }}
      className="flex flex-wrap items-center gap-3 pt-1 select-none"
    >
      {/* M3 Shield: Defense Shatters */}
      <div className="inline-flex items-center gap-3 px-3.5 py-2 rounded-xl border border-rose-500/30 bg-rose-950/40 backdrop-blur-sm shadow-sm hover:border-rose-500/50 transition-colors">
        <BrokenShieldIcon size="md" shouldReduceMotion={shouldReduceMotion} />
        <div>
          <div className="text-xs font-bold text-rose-300 tracking-tight leading-tight flex items-center gap-1.5">
            <span>M3 Monolithic</span>
            <span className="text-[10px] px-1.5 py-0.2 rounded bg-rose-500/20 text-rose-400 font-mono font-semibold">
              Shattered
            </span>
          </div>
          <div className="text-[11px] text-slate-300 mt-0.5">
            {m3EvasionRate}% Evasion Under Attack
          </div>
        </div>
      </div>

      {/* M4 Shield: Defense Strained */}
      <div className="inline-flex items-center gap-3 px-3.5 py-2 rounded-xl border border-amber-500/30 bg-amber-950/40 backdrop-blur-sm shadow-sm hover:border-amber-500/50 transition-colors">
        <StrainedShieldIcon size="md" shouldReduceMotion={shouldReduceMotion} />
        <div>
          <div className="text-xs font-bold text-amber-300 tracking-tight leading-tight flex items-center gap-1.5">
            <span>M4 Decoupled</span>
            <span className="text-[10px] px-1.5 py-0.2 rounded bg-amber-500/20 text-amber-400 font-mono font-semibold">
              Strained
            </span>
          </div>
          <div className="text-[11px] text-slate-300 mt-0.5">
            Holds at {m4UnmarkedFpr}% False-Alarm Tax
          </div>
        </div>
      </div>
    </motion.div>
  );
};
