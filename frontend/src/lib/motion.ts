import type { Variants, Transition } from 'framer-motion';
import { getPrefersReducedMotion } from '../hooks/usePrefersReducedMotion';

const isReduced = () => typeof window !== 'undefined' && getPrefersReducedMotion();

/**
 * Standard transition curves for consistent motion design
 */
export const transitions = {
  default: {
    duration: 0.3,
    ease: [0.25, 0.1, 0.25, 1],
  } as Transition,
  snappy: {
    duration: 0.25,
    ease: [0.16, 1, 0.3, 1],
  } as Transition,
};

/**
 * Shared fadeInUp variant:
 * - When reduced motion is preferred: purely fast opacity fade (duration: 0.15s, no y displacement)
 * - Standard: opacity 0->1, y 12->0, duration 0.22s
 */
export const fadeInUp: Variants = {
  hidden: () => ({
    opacity: 0,
    y: isReduced() ? 0 : 12,
  }),
  visible: () => ({
    opacity: 1,
    y: 0,
    transition: {
      duration: isReduced() ? 0.15 : 0.22,
      ease: [0.25, 0.1, 0.25, 1],
    },
  }),
  exit: () => ({
    opacity: 0,
    y: isReduced() ? 0 : -8,
    transition: {
      duration: isReduced() ? 0.12 : 0.16,
      ease: [0.25, 0.1, 0.25, 1],
    },
  }),
};

/**
 * Shared staggerContainer variant:
 * - Supports optional customDelay for orchestrating staggered lists after parent entrance
 * - Disables child staggering when reduced motion is preferred
 */
export const staggerContainer: Variants = {
  hidden: {},
  visible: (customDelay?: number) => ({
    transition: {
      delayChildren: isReduced() ? 0 : (typeof customDelay === 'number' ? customDelay : 0),
      staggerChildren: isReduced() ? 0 : 0.08,
    },
  }),
};

/**
 * Shared scaleIn variant (for modals, cards, alerts, popups):
 * - When reduced motion is preferred: purely fast opacity fade (duration: 0.15s, no scale displacement)
 * - Standard: opacity 0->1, scale 0.95->1
 */
export const scaleIn: Variants = {
  hidden: () => ({
    opacity: 0,
    scale: isReduced() ? 1 : 0.95,
  }),
  visible: () => ({
    opacity: 1,
    scale: 1,
    transition: {
      duration: isReduced() ? 0.15 : 0.25,
      ease: [0.16, 1, 0.3, 1],
    },
  }),
  exit: () => ({
    opacity: 0,
    scale: isReduced() ? 1 : 0.95,
    transition: {
      duration: isReduced() ? 0.12 : 0.2,
      ease: 'easeIn',
    },
  }),
};

export default {
  fadeInUp,
  staggerContainer,
  scaleIn,
  transitions,
};
