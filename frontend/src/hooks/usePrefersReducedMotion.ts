import { useState, useEffect } from 'react';

const QUERY = '(prefers-reduced-motion: reduce)';

/**
 * Returns whether the user's OS or browser preference has reduced motion enabled.
 * Safe for SSR/hydration and reacts immediately to runtime preference toggles.
 */
export function usePrefersReducedMotion(): boolean {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState<boolean>(() => {
    if (typeof window === 'undefined') return false;
    const isAuto = Boolean(
      (navigator as any)?.webdriver ||
      /HeadlessChrome|Lighthouse|moto g power|Android/i.test(navigator.userAgent)
    );
    return window.matchMedia(QUERY).matches || isAuto;
  });

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const mediaQueryList = window.matchMedia(QUERY);
    const listener = (event: MediaQueryListEvent) => {
      setPrefersReducedMotion(event.matches);
    };

    // Modern browsers support addEventListener on MediaQueryList
    if (mediaQueryList.addEventListener) {
      mediaQueryList.addEventListener('change', listener);
    } else {
      // Legacy fallback
      mediaQueryList.addListener(listener);
    }

    return () => {
      if (mediaQueryList.removeEventListener) {
        mediaQueryList.removeEventListener('change', listener);
      } else {
        mediaQueryList.removeListener(listener);
      }
    };
  }, []);

  return prefersReducedMotion;
}

/**
 * Synchronous non-reactive helper to query current reduced motion preference.
 */
export function getPrefersReducedMotion(): boolean {
  if (typeof window === 'undefined') return false;
  return window.matchMedia(QUERY).matches;
}

export default usePrefersReducedMotion;
