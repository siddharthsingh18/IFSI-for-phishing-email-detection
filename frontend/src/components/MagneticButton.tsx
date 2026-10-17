import React, { useRef, useState } from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import { usePrefersReducedMotion } from '../hooks/usePrefersReducedMotion';

export interface MagneticButtonProps {
  children: React.ReactNode;
  className?: string;
  /** Maximum magnetic displacement in pixels (default: 10) */
  maxDistance?: number;
  /** Magnetic pull strength factor (default: 0.28) */
  strength?: number;
  /** Radius in pixels around button where nearby hovering attracts the button (default: 20) */
  radius?: number;
}

/**
 * Magnetic button wrapper that shifts slightly toward the cursor within a small radius
 * when hovered nearby or over the button, smoothly snapping back on mouse leave using
 * Framer Motion springs.
 * Automatically disabled when prefers-reduced-motion is active.
 */
export const MagneticButton: React.FC<MagneticButtonProps> = ({
  children,
  className = '',
  maxDistance = 10,
  strength = 0.28,
  radius = 20,
}) => {
  const framerReducedMotion = useReducedMotion();
  const prefersReducedMotion = usePrefersReducedMotion();
  const shouldReduceMotion = prefersReducedMotion || Boolean(framerReducedMotion);
  const containerRef = useRef<HTMLDivElement>(null);
  const [position, setPosition] = useState({ x: 0, y: 0 });

  // If reduced motion is requested, render children directly without magnetic offset
  if (shouldReduceMotion) {
    return <div className={`inline-flex items-center justify-center ${className}`}>{children}</div>;
  }

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;

    const deltaX = e.clientX - centerX;
    const deltaY = e.clientY - centerY;

    // Shift toward cursor, clamped to maxDistance
    const x = Math.max(-maxDistance, Math.min(maxDistance, deltaX * strength));
    const y = Math.max(-maxDistance, Math.min(maxDistance, deltaY * strength));

    setPosition({ x, y });
  };

  const handleMouseLeave = () => {
    setPosition({ x: 0, y: 0 });
  };

  return (
    <div
      ref={containerRef}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      style={{
        padding: radius,
        margin: -radius,
      }}
      className={`relative inline-flex items-center justify-center ${className}`}
    >
      <motion.div
        animate={{ x: position.x, y: position.y }}
        transition={{ type: 'spring', stiffness: 350, damping: 20, mass: 0.5 }}
        className="inline-block pointer-events-auto"
      >
        {children}
      </motion.div>
    </div>
  );
};
