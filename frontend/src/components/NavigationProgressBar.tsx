import React, { useEffect, useState, useRef } from 'react';
import { useLocation } from 'react-router-dom';

/**
 * Subtle top loading progress bar that animates during route navigation,
 * similar to the top navigation bars on GitHub and YouTube.
 */
export const NavigationProgressBar: React.FC = () => {
  const location = useLocation();
  const [progress, setProgress] = useState(0);
  const [isVisible, setIsVisible] = useState(false);
  const isFirstMount = useRef(true);

  useEffect(() => {
    // Avoid triggering on initial mount
    if (isFirstMount.current) {
      isFirstMount.current = false;
      return;
    }

    // Route changed: kick off the progress animation
    setIsVisible(true);
    setProgress(25);

    const step1 = setTimeout(() => {
      setProgress(75);
    }, 80);

    const step2 = setTimeout(() => {
      setProgress(100);
    }, 220);

    const step3 = setTimeout(() => {
      setIsVisible(false);
      setProgress(0);
    }, 450);

    return () => {
      clearTimeout(step1);
      clearTimeout(step2);
      clearTimeout(step3);
    };
  }, [location.pathname, location.search]);

  if (!isVisible && progress === 0) {
    return null;
  }

  return (
    <div
      role="progressbar"
      aria-label="Page navigation progress"
      aria-valuenow={progress}
      aria-valuemin={0}
      aria-valuemax={100}
      className="fixed top-0 left-0 right-0 z-[9999] pointer-events-none h-[2.5px] overflow-hidden"
    >
      <div
        className="h-full bg-gradient-to-r from-teal-400 via-cyan-400 to-emerald-400 transition-all duration-200 ease-out shadow-[0_0_12px_rgba(45,212,191,0.8)]"
        style={{
          width: `${progress}%`,
          opacity: progress === 100 ? 0 : 1,
          transitionProperty: 'width, opacity',
          transitionDuration: progress === 100 ? '250ms' : '180ms',
        }}
      />
    </div>
  );
};
