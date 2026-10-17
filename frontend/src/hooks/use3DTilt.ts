import { useRef, useCallback, useEffect } from 'react';
import { usePrefersReducedMotion } from './usePrefersReducedMotion';

export interface Use3DTiltOptions {
  /** Maximum tilt angle in degrees (default: 6) */
  maxTilt?: number;
  /** Perspective distance in pixels (default: 1000) */
  perspective?: number;
  /** Scale on hover/tilt (default: 1.015) */
  scale?: number;
  /** Invert tilt direction (default: false) */
  reverse?: boolean;
}

/**
 * Lightweight 3D tilt hook that tilts a card toward the cursor position
 * (max ~6 degrees) and returns smoothly on mouse leave using direct DOM
 * style calculations to avoid React re-render overhead.
 * Automatically disabled when prefers-reduced-motion is active.
 */
export function use3DTilt(options?: Use3DTiltOptions) {
  const prefersReducedMotion = usePrefersReducedMotion();
  const maxTilt = options?.maxTilt ?? 6;
  const perspective = options?.perspective ?? 1000;
  const scale = options?.scale ?? 1.015;
  const reverse = options?.reverse ?? false;

  const ref = useRef<HTMLDivElement>(null);

  // Clear any existing transform if reduced motion preference is turned on
  useEffect(() => {
    if (prefersReducedMotion && ref.current) {
      ref.current.style.transform = 'none';
      ref.current.style.transition = 'none';
    }
  }, [prefersReducedMotion]);

  const onMouseMove = useCallback(
    (e: React.MouseEvent<HTMLDivElement>) => {
      if (prefersReducedMotion) return;
      const el = ref.current;
      if (!el) return;

      const rect = el.getBoundingClientRect();
      const width = rect.width;
      const height = rect.height;

      // Mouse position relative to card center
      const x = e.clientX - (rect.left + width / 2);
      const y = e.clientY - (rect.top + height / 2);

      // Normalized coordinates in range [-1, 1]
      const normX = Math.max(-1, Math.min(1, x / (width / 2)));
      const normY = Math.max(-1, Math.min(1, y / (height / 2)));

      // Tilt slightly toward cursor position (max ~6 degrees)
      const factor = reverse ? -1 : 1;
      const rotateX = normY * maxTilt * factor;
      const rotateY = -normX * maxTilt * factor;

      el.style.transform = `perspective(${perspective}px) rotateX(${rotateX.toFixed(2)}deg) rotateY(${rotateY.toFixed(2)}deg) scale3d(${scale}, ${scale}, ${scale})`;
      el.style.transition = 'transform 100ms ease-out';
    },
    [prefersReducedMotion, maxTilt, perspective, scale, reverse]
  );

  const onMouseLeave = useCallback(() => {
    if (prefersReducedMotion) return;
    const el = ref.current;
    if (!el) return;

    el.style.transform = `perspective(${perspective}px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)`;
    el.style.transition = 'transform 400ms cubic-bezier(0.16, 1, 0.3, 1)';
  }, [prefersReducedMotion, perspective]);

  return {
    ref,
    onMouseMove,
    onMouseLeave,
    style: prefersReducedMotion
      ? {}
      : {
          transformStyle: 'preserve-3d' as const,
          willChange: 'transform',
        },
  };
}
