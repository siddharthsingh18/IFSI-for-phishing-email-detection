import React, { useId } from 'react';
import { motion } from 'framer-motion';

interface SectionTransitionDividerProps {
  className?: string;
  shouldReduceMotion?: boolean;
}

/**
 * Subtle horizontal animated divider between major landing page sections.
 * Draws itself left-to-right (stroke-dashoffset) in the teal accent color at low opacity
 * as the user scrolls into view. Understated transition cue.
 */
export const SectionTransitionDivider: React.FC<SectionTransitionDividerProps> = ({
  className = '',
  shouldReduceMotion = false,
}) => {
  const rawId = useId();
  const gradId = `divider-grad-${rawId.replace(/[:]/g, '')}`;

  return (
    <div
      aria-hidden="true"
      className={`w-full -my-4 py-2 flex items-center justify-center select-none overflow-hidden ${className}`}
    >
      <svg
        className="w-full h-[2px] max-w-5xl mx-auto overflow-visible"
        viewBox="0 0 1000 2"
        fill="none"
        preserveAspectRatio="none"
      >
        <defs>
          <linearGradient
            id={gradId}
            gradientUnits="userSpaceOnUse"
            x1="0"
            y1="1"
            x2="1000"
            y2="1"
          >
            <stop offset="0%" stopColor="#14b8a6" stopOpacity="0" />
            <stop offset="15%" stopColor="#14b8a6" stopOpacity="0.35" />
            <stop offset="50%" stopColor="#2dd4bf" stopOpacity="0.5" />
            <stop offset="85%" stopColor="#14b8a6" stopOpacity="0.35" />
            <stop offset="100%" stopColor="#14b8a6" stopOpacity="0" />
          </linearGradient>
        </defs>

        <motion.path
          d="M 0 1 L 1000 1"
          stroke={`url(#${gradId})`}
          strokeWidth="1.5"
          strokeLinecap="round"
          initial={{ pathLength: 0, opacity: 0 }}
          whileInView={{
            pathLength: 1,
            opacity: 1,
            transition: {
              pathLength: {
                duration: shouldReduceMotion ? 0.2 : 0.85,
                ease: [0.16, 1, 0.3, 1],
              },
              opacity: {
                duration: shouldReduceMotion ? 0.15 : 0.3,
              },
            },
          }}
          viewport={{ once: true, margin: '-20px' }}
        />
      </svg>
    </div>
  );
};
