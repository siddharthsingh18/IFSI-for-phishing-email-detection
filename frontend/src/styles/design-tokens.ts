/**
 * IFSI Frontend Design System Tokens
 *
 * Dark Slate Foundation with a unified Cybernetic Teal Accent.
 * Tailored for high-density analytical dashboards and security research interfaces.
 */

export const colors = {
  // Dark Slate Background Hierarchy
  slate: {
    950: '#020617', // Canvas base background
    900: '#0b1120', // Card / Surface background
    850: '#0f172a', // Elevated surface background
    800: '#1e293b', // Primary borders & divider lines
    700: '#334155', // Secondary borders & muted elements
    600: '#475569', // Subtle icons & inactive states
    500: '#64748b', // Secondary body text
    400: '#94a3b8', // Muted headings & subtitles
    300: '#cbd5e1', // Primary body text
    200: '#e2e8f0', // Crisp high-contrast text
    100: '#f1f5f9', // Headings & active labels
    50: '#f8fafc',  // Pure highlights
  },

  // Primary Accent: Cybernetic Teal
  accent: {
    50: '#f0fdfa',
    100: '#ccfbf1',
    200: '#99f6e4',
    300: '#5eead4',
    400: '#2dd4bf', // Accent highlight
    500: '#14b8a6', // Primary Brand Accent
    600: '#0d9488', // Accent hover / active
    700: '#0f766e',
    800: '#115e59',
    900: '#134e4a',
    950: '#042f2e',
    glow: 'rgba(20, 184, 166, 0.25)',
    subtle: 'rgba(20, 184, 166, 0.08)',
    border: 'rgba(20, 184, 166, 0.25)',
  },

  // Semantic Status & Verdict Colors
  semantic: {
    // Phishing / Malicious Verdict
    phishing: {
      text: '#fb7185',
      bg: 'rgba(244, 63, 94, 0.1)',
      border: 'rgba(244, 63, 94, 0.3)',
      solid: '#f43f5e',
      glow: 'rgba(244, 63, 94, 0.25)',
    },
    // Legitimate / Safe Verdict
    legitimate: {
      text: '#34d399',
      bg: 'rgba(16, 185, 129, 0.1)',
      border: 'rgba(16, 185, 129, 0.3)',
      solid: '#10b981',
      glow: 'rgba(16, 185, 129, 0.25)',
    },
    // Prompt Injection / Attack Alert
    injection: {
      text: '#fbbf24',
      bg: 'rgba(245, 158, 11, 0.1)',
      border: 'rgba(245, 158, 11, 0.3)',
      solid: '#f59e0b',
      glow: 'rgba(245, 158, 11, 0.25)',
    },
    // Neutral / Informational
    neutral: {
      text: '#94a3b8',
      bg: 'rgba(148, 163, 184, 0.1)',
      border: 'rgba(148, 163, 184, 0.2)',
      solid: '#64748b',
      glow: 'rgba(148, 163, 184, 0.15)',
    },
  },
} as const;

export const typography = {
  fonts: {
    heading: "'Plus Jakarta Sans', system-ui, -apple-system, sans-serif",
    body: "'Inter', system-ui, -apple-system, sans-serif",
    mono: "'JetBrains Mono', ui-monospace, SFMono-Regular, monospace",
  },
  sizes: {
    xs: { size: '0.75rem', lineHeight: '1rem' },         // 12px
    sm: { size: '0.875rem', lineHeight: '1.25rem' },     // 14px
    base: { size: '1rem', lineHeight: '1.5rem' },         // 16px
    lg: { size: '1.125rem', lineHeight: '1.75rem' },     // 18px
    xl: { size: '1.25rem', lineHeight: '1.75rem' },      // 20px
    '2xl': { size: '1.5rem', lineHeight: '2rem' },       // 24px
    '3xl': { size: '1.875rem', lineHeight: '2.25rem' },  // 30px
    '4xl': { size: '2.25rem', lineHeight: '2.5rem' },    // 36px
    '5xl': { size: '3rem', lineHeight: '1' },            // 48px
  },
  weights: {
    regular: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
    extrabold: 800,
  },
} as const;

export const spacing = {
  1: '0.25rem',  // 4px
  2: '0.5rem',   // 8px
  3: '0.75rem',  // 12px
  4: '1rem',     // 16px
  5: '1.25rem',  // 20px
  6: '1.5rem',   // 24px
  8: '2rem',     // 32px
  10: '2.5rem',  // 40px
  12: '3rem',    // 48px
  16: '4rem',    // 64px
} as const;

export const radii = {
  sm: '0.375rem', // 6px
  md: '0.5rem',   // 8px
  lg: '0.75rem',  // 12px
  xl: '1rem',     // 16px
  '2xl': '1.25rem', // 20px
  full: '9999px',
} as const;

// Unified Depth System: 3 Consistent Multi-Layered Tokens (Light source: top-left -> down-right)
// Layer 0: 1px inner top highlight to simulate light catching an edge (Stripe/Linear bevel)
// Layers 1-3: Contact shadow, mid-dispersion, and deep ambient plume falling down-right
export const shadows = {
  card: 'inset 0 1px 0 0 rgba(255, 255, 255, 0.07), 1px 2px 4px rgba(0, 0, 0, 0.35), 3px 6px 16px rgba(0, 0, 0, 0.30), 6px 16px 36px rgba(0, 0, 0, 0.25)',
  hover: 'inset 0 1px 0 0 rgba(255, 255, 255, 0.11), 2px 4px 8px rgba(0, 0, 0, 0.40), 6px 14px 28px rgba(0, 0, 0, 0.35), 12px 28px 52px rgba(0, 0, 0, 0.35)',
  modal: 'inset 0 1px 0 0 rgba(255, 255, 255, 0.14), 3px 6px 12px rgba(0, 0, 0, 0.45), 10px 20px 40px rgba(0, 0, 0, 0.45), 20px 40px 80px rgba(0, 0, 0, 0.55)',
} as const;

export const transitions = {
  hover: '150ms cubic-bezier(0.16, 1, 0.3, 1)',
  standard: '200ms cubic-bezier(0.16, 1, 0.3, 1)',
} as const;

// Dual-Theme System: Dark Slate Foundation (Prompt 28) and Light Slate Foundation
export const themes = {
  dark: {
    name: 'dark' as const,
    surfaces: {
      canvas: '#020617',          // Midnight Dark Slate (not pure black)
      card: '#0b1120',            // Surface base
      elevated: '#0f172a',        // Elevated surface / modals
      subtle: '#1e293b',          // Inset panels / preview wells
    },
    borders: {
      primary: '#1e293b',
      subtle: '#334155',
    },
    text: {
      primary: '#f8fafc',
      secondary: '#cbd5e1',
      muted: '#94a3b8',
      faint: '#64748b',
    },
    accent: {
      primary: '#14b8a6',
      hover: '#0d9488',
      light: '#2dd4bf',
      glow: 'rgba(20, 184, 166, 0.25)',
    },
    chart: {
      grid: '#1e293b',
      text: '#94a3b8',
      axis: '#475569',
      tooltipBg: '#0b1120',
      tooltipBorder: '#334155',
      tooltipText: '#f8fafc',
      legendText: '#cbd5e1',
    },
    shadows: {
      card: 'inset 0 1px 0 0 rgba(255, 255, 255, 0.07), 1px 2px 4px rgba(0, 0, 0, 0.35), 3px 6px 16px rgba(0, 0, 0, 0.30), 6px 16px 36px rgba(0, 0, 0, 0.25)',
      hover: 'inset 0 1px 0 0 rgba(255, 255, 255, 0.11), 2px 4px 8px rgba(0, 0, 0, 0.40), 6px 14px 28px rgba(0, 0, 0, 0.35), 12px 28px 52px rgba(0, 0, 0, 0.35)',
      modal: 'inset 0 1px 0 0 rgba(255, 255, 255, 0.14), 3px 6px 12px rgba(0, 0, 0, 0.45), 10px 20px 40px rgba(0, 0, 0, 0.45), 20px 40px 80px rgba(0, 0, 0, 0.55)',
    },
  },
  light: {
    name: 'light' as const,
    surfaces: {
      canvas: '#f8fafc',          // Clean light slate canvas (slate-50)
      card: '#ffffff',            // Crisp white surface
      elevated: '#f1f5f9',        // Light slate elevated / modals (slate-100)
      subtle: '#f1f5f9',          // Inset panels / preview wells
    },
    borders: {
      primary: '#e2e8f0',         // Slate 200 primary borders
      subtle: '#cbd5e1',          // Slate 300 secondary borders
    },
    text: {
      primary: '#0f172a',         // Slate 900 primary text
      secondary: '#334155',       // Slate 700 body text
      muted: '#64748b',           // Slate 500 subtitles & captions
      faint: '#94a3b8',           // Slate 400 inactive text
    },
    accent: {
      primary: '#0d9488',         // Teal 600 - deeper for high contrast on light
      hover: '#0f766e',
      light: '#14b8a6',
      glow: 'rgba(13, 148, 136, 0.18)',
    },
    chart: {
      grid: '#e2e8f0',
      text: '#475569',
      axis: '#cbd5e1',
      tooltipBg: '#ffffff',
      tooltipBorder: '#e2e8f0',
      tooltipText: '#0f172a',
      legendText: '#334155',
    },
    shadows: {
      card: 'inset 0 1px 0 0 rgba(255, 255, 255, 0.9), 1px 2px 4px rgba(15, 23, 42, 0.04), 3px 6px 14px rgba(15, 23, 42, 0.06), 6px 16px 28px rgba(15, 23, 42, 0.04)',
      hover: 'inset 0 1px 0 0 rgba(255, 255, 255, 1), 2px 4px 8px rgba(15, 23, 42, 0.06), 6px 14px 24px rgba(15, 23, 42, 0.08), 12px 28px 44px rgba(15, 23, 42, 0.06)',
      modal: 'inset 0 1px 0 0 rgba(255, 255, 255, 1), 3px 6px 12px rgba(15, 23, 42, 0.08), 10px 20px 36px rgba(15, 23, 42, 0.12), 20px 40px 72px rgba(15, 23, 42, 0.10)',
    },
  },
} as const;


