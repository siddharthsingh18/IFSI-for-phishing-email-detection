import type { Variants, Transition } from 'framer-motion';

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
 * - Hidden: opacity 0, y 12
 * - Visible: opacity 1, y 0, duration 0.22s (under 250ms for snappy navigation)
 * - Exit: opacity 0, y -8, duration 0.16s
 */
export const fadeInUp: Variants = {
  hidden: {
    opacity: 0,
    y: 12,
  },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.22,
      ease: [0.25, 0.1, 0.25, 1],
    },
  },
  exit: {
    opacity: 0,
    y: -8,
    transition: {
      duration: 0.16,
      ease: [0.25, 0.1, 0.25, 1],
    },
  },
};

/**
 * Shared staggerContainer variant:
 * - Staggers child elements with 0.08s staggerChildren
 */
export const staggerContainer: Variants = {
  hidden: {},
  visible: {
    transition: {
      staggerChildren: 0.08,
    },
  },
};

/**
 * Shared scaleIn variant (for modals, cards, alerts, popups):
 * - Hidden: opacity 0, scale 0.95
 * - Visible: opacity 1, scale 1
 */
export const scaleIn: Variants = {
  hidden: {
    opacity: 0,
    scale: 0.95,
  },
  visible: {
    opacity: 1,
    scale: 1,
    transition: {
      duration: 0.25,
      ease: [0.16, 1, 0.3, 1],
    },
  },
  exit: {
    opacity: 0,
    scale: 0.95,
    transition: {
      duration: 0.2,
      ease: 'easeIn',
    },
  },
};

export default {
  fadeInUp,
  staggerContainer,
  scaleIn,
  transitions,
};
