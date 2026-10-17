import { useState, useEffect, useRef } from 'react';
import { usePrefersReducedMotion } from './usePrefersReducedMotion';

export interface UseCountUpOptions {
  duration?: number;
  start?: boolean;
  decimals?: number;
}

/**
 * Custom hook to animate a numeric value from 0 to target over ~800ms using requestAnimationFrame.
 *
 * - Uses cubic ease-out for natural deceleration.
 * - Animates once when `start` becomes true (on first appearance in view).
 * - Avoids re-animating on subsequent re-renders once finished.
 * - If prefers-reduced-motion is active, displays the target number immediately without tick animation.
 */
export function useCountUp(
  target: number,
  options?: UseCountUpOptions
): number {
  const prefersReduced = usePrefersReducedMotion();
  const duration = options?.duration ?? 800;
  const start = options?.start ?? true;
  const decimals = options?.decimals ?? 0;

  const [count, setCount] = useState<number>(0);
  const hasAnimatedRef = useRef<boolean>(false);
  const frameRef = useRef<number | null>(null);

  useEffect(() => {
    // If user prefers reduced motion, skip requestAnimationFrame loop
    if (prefersReduced) return;

    // If not triggered to start yet, stay at 0
    if (!start) return;

    // Handle 0 or NaN target immediately
    if (!target || isNaN(target)) {
      // oxlint-disable-next-line react/set-state-in-effect
      setCount(0);
      return;
    }

    // If already animated to target, don't re-animate from 0; just keep current target
    if (hasAnimatedRef.current) {
      setCount(target);
      return;
    }

    hasAnimatedRef.current = true;
    let startTimestamp: number | null = null;
    const startValue = 0;
    const diff = target - startValue;

    // Ease-out cubic curve: fast start, smooth deceleration
    const easeOutCubic = (t: number): number => {
      return 1 - Math.pow(1 - t, 3);
    };

    const step = (timestamp: number) => {
      if (!startTimestamp) {
        startTimestamp = timestamp;
      }
      const elapsed = timestamp - startTimestamp;
      const progress = Math.min(elapsed / duration, 1);
      const easedProgress = easeOutCubic(progress);
      const nextValue = startValue + diff * easedProgress;

      if (decimals > 0) {
        const factor = Math.pow(10, decimals);
        setCount(Math.round(nextValue * factor) / factor);
      } else {
        setCount(Math.round(nextValue));
      }

      if (progress < 1) {
        frameRef.current = requestAnimationFrame(step);
      } else {
        setCount(target);
      }
    };

    frameRef.current = requestAnimationFrame(step);

    return () => {
      if (frameRef.current) {
        cancelAnimationFrame(frameRef.current);
      }
    };
  }, [start, target, duration, decimals, prefersReduced]);

  if (prefersReduced) {
    return target;
  }

  return count;
}

export default useCountUp;
