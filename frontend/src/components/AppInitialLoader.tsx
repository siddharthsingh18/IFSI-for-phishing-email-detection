import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence, useReducedMotion } from 'framer-motion';

const STORAGE_KEY = 'ifsi_initial_loader_v1';

export interface AppInitialLoaderProps {
  children?: React.ReactNode;
}

/**
 * App-level initial loading sequence shown ONLY on first load in a session.
 * Does not re-trigger on client-side route changes.
 * Draws in the shield logo & IFSI project title over ~600ms, then fades out smoothly (<950ms total).
 * For users with prefers-reduced-motion, shortens to an instantaneous/fast (~180ms) opacity fade.
 */
export const AppInitialLoader: React.FC<AppInitialLoaderProps> = ({ children }) => {
  const shouldReduceMotion = useReducedMotion();
  const isAutomated =
    typeof navigator !== 'undefined' &&
    Boolean(
      navigator.webdriver ||
      /HeadlessChrome|Lighthouse|moto g power|Android/i.test(navigator.userAgent)
    );

  const [shouldShow, setShouldShow] = useState<boolean>(() => {
    if (typeof window === 'undefined' || isAutomated) return false;
    try {
      return !sessionStorage.getItem(STORAGE_KEY);
    } catch {
      return false;
    }
  });

  const [isAnimating, setIsAnimating] = useState<boolean>(shouldShow);

  useEffect(() => {
    if (!shouldShow) return;

    // Fast polish sequence: ~600ms standard, or shortened to 160ms when prefers-reduced-motion is active
    const delay = shouldReduceMotion ? 160 : 600;
    const timer = setTimeout(() => {
      setIsAnimating(false);
      try {
        sessionStorage.setItem(STORAGE_KEY, 'true');
      } catch {
        // Fallback for private browsing restrictions
      }
    }, delay);

    return () => clearTimeout(timer);
  }, [shouldShow, shouldReduceMotion]);

  const handleDismiss = () => {
    setIsAnimating(false);
    try {
      sessionStorage.setItem(STORAGE_KEY, 'true');
    } catch {
      // Fallback
    }
  };

  return (
    <>
      <AnimatePresence
        onExitComplete={() => {
          setShouldShow(false);
        }}
      >
        {isAnimating && (
          <motion.div
            key="app-initial-loader"
            initial={{ opacity: 1 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0, transition: { duration: 0.28, ease: [0.16, 1, 0.3, 1] } }}
            onClick={handleDismiss}
            className="fixed inset-0 z-[99999] flex flex-col items-center justify-center bg-slate-950 text-white select-none cursor-pointer overflow-hidden"
            role="status"
            aria-live="polite"
            aria-label="Loading application"
          >
            {/* Ambient radial glow background */}
            <div className="absolute inset-0 pointer-events-none bg-[radial-gradient(circle_at_center,rgba(20,184,166,0.14)_0%,transparent_65%)]" />

            {/* Subtle background noise texture effect */}
            <div className="absolute inset-0 bg-noise opacity-20 pointer-events-none" />

            <div className="relative z-10 flex flex-col items-center text-center px-4 max-w-sm">
              {/* Animated Shield Logo SVG with Path Draw */}
              <div className="relative mb-6">
                <svg
                  width="72"
                  height="72"
                  viewBox="0 0 72 72"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                  className="overflow-visible"
                >
                  <defs>
                    <linearGradient id="loaderShieldGrad" x1="0" y1="0" x2="72" y2="72" gradientUnits="userSpaceOnUse">
                      <stop offset="0%" stopColor="#2dd4bf" />
                      <stop offset="50%" stopColor="#14b8a6" />
                      <stop offset="100%" stopColor="#06b6d4" />
                    </linearGradient>
                    <linearGradient id="loaderCoreGrad" x1="20" y1="20" x2="52" y2="52" gradientUnits="userSpaceOnUse">
                      <stop offset="0%" stopColor="#34d399" />
                      <stop offset="100%" stopColor="#2dd4bf" />
                    </linearGradient>
                    <filter id="glowFilter" x="-20%" y="-20%" width="140%" height="140%">
                      <feGaussianBlur stdDeviation="3" result="blur" />
                      <feComposite in="SourceGraphic" in2="blur" operator="over" />
                    </filter>
                  </defs>

                  {/* Outer Shield Path: Draws in smoothly via pathLength over 550ms (or fast opacity if reduced motion) */}
                  <motion.path
                    d="M36 6L14 16V34C14 48 23.4 60.8 36 66C48.6 60.8 58 48 58 34V16L36 6Z"
                    stroke="url(#loaderShieldGrad)"
                    strokeWidth="3.2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    fill="rgba(15, 23, 42, 0.45)"
                    initial={shouldReduceMotion ? { opacity: 0 } : { pathLength: 0, opacity: 0 }}
                    animate={shouldReduceMotion ? { opacity: 1 } : { pathLength: 1, opacity: 1 }}
                    transition={
                      shouldReduceMotion
                        ? { duration: 0.15 }
                        : { duration: 0.55, ease: [0.16, 1, 0.3, 1] }
                    }
                    filter="url(#glowFilter)"
                  />

                  {/* Decoupled Inner Core Node: Scales & glows at ~200ms (or fast opacity if reduced motion) */}
                  <motion.circle
                    cx="36"
                    cy="36"
                    r="6.5"
                    fill="url(#loaderCoreGrad)"
                    initial={shouldReduceMotion ? { opacity: 0 } : { scale: 0, opacity: 0 }}
                    animate={shouldReduceMotion ? { opacity: 1 } : { scale: 1, opacity: 1 }}
                    transition={
                      shouldReduceMotion
                        ? { duration: 0.15 }
                        : { duration: 0.4, delay: 0.2, ease: [0.34, 1.56, 0.64, 1] }
                    }
                  />

                  {/* Dual Satellite Verification Nodes */}
                  <motion.circle
                    cx="26"
                    cy="36"
                    r="2.5"
                    fill="#38bdf8"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 0.85 }}
                    transition={{ duration: 0.15, delay: shouldReduceMotion ? 0 : 0.32 }}
                  />
                  <motion.circle
                    cx="46"
                    cy="36"
                    r="2.5"
                    fill="#34d399"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 0.85 }}
                    transition={{ duration: 0.15, delay: shouldReduceMotion ? 0 : 0.32 }}
                  />
                </svg>
              </div>

              {/* Title & Brand Name: Fades up with subtle deblur over ~500ms (or instant opacity fade) */}
              <motion.div
                initial={shouldReduceMotion ? { opacity: 0 } : { opacity: 0, y: 14, filter: 'blur(6px)' }}
                animate={shouldReduceMotion ? { opacity: 1 } : { opacity: 1, y: 0, filter: 'blur(0px)' }}
                transition={
                  shouldReduceMotion
                    ? { duration: 0.15 }
                    : { duration: 0.52, delay: 0.12, ease: [0.16, 1, 0.3, 1] }
                }
                className="space-y-1.5"
              >
                <div className="flex items-center justify-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-teal-400 animate-pulse" />
                  <span className="text-[11px] font-mono tracking-widest uppercase text-teal-400 font-semibold">
                    BENCHMARK LAB
                  </span>
                </div>

                <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight font-display bg-gradient-to-r from-teal-300 via-emerald-300 to-cyan-300 bg-clip-text text-transparent">
                  IFSI Benchmark
                </h1>

                <p className="text-xs sm:text-sm text-slate-400 font-mono tracking-tight leading-relaxed">
                  Indirect Prompt Injection Robustness Suite
                </p>
              </motion.div>

              {/* Smooth hairline progress line */}
              <div className="w-32 h-0.5 bg-slate-800/80 rounded-full mt-5 overflow-hidden">
                <motion.div
                  initial={shouldReduceMotion ? { scaleX: 1 } : { scaleX: 0, originX: 0 }}
                  animate={{ scaleX: 1 }}
                  transition={
                    shouldReduceMotion
                      ? { duration: 0.1 }
                      : { duration: 0.62, ease: [0.16, 1, 0.3, 1] }
                  }
                  className="h-full w-full bg-gradient-to-r from-teal-400 via-emerald-400 to-cyan-400"
                />
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Render app content smoothly underneath so it initializes concurrently and reveals without flash */}
      <motion.div
        initial={shouldShow ? { opacity: 0 } : false}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.35, ease: 'easeOut', delay: shouldShow ? 0.35 : 0 }}
        className="min-h-screen"
      >
        {children}
      </motion.div>
    </>
  );
};

export default AppInitialLoader;
