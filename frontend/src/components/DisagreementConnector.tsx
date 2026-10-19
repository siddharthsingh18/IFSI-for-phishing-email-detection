import React, { useEffect, useState, useLayoutEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertTriangle, GitCompare } from 'lucide-react';
import { type CompareResponse } from '../api/client';

export interface DisagreementConnectorProps {
  containerRef: React.RefObject<HTMLDivElement | null>;
  cardRefs: React.MutableRefObject<Record<string, HTMLDivElement | null>>;
  compareResult: CompareResponse;
  viewDensity?: 'simple' | 'detailed';
}

interface CardBox {
  code: string;
  left: number;
  right: number;
  top: number;
  bottom: number;
  width: number;
  height: number;
  centerX: number;
  centerY: number;
}

export const DisagreementConnector: React.FC<DisagreementConnectorProps> = ({
  containerRef,
  cardRefs,
  compareResult,
  viewDensity = 'simple',
}) => {
  const [boxes, setBoxes] = useState<Record<string, CardBox>>({});
  const [containerDimensions, setContainerDimensions] = useState<{ width: number; height: number }>({
    width: 0,
    height: 0,
  });

  const updateMeasurements = useCallback(() => {
    if (!containerRef.current) return;
    const containerRect = containerRef.current.getBoundingClientRect();
    if (containerRect.width === 0 && containerRect.height === 0) return;

    setContainerDimensions({
      width: containerRect.width,
      height: containerRect.height,
    });

    const nextBoxes: Record<string, CardBox> = {};
    for (const [code, el] of Object.entries(cardRefs.current)) {
      if (!el) continue;
      const r = el.getBoundingClientRect();
      nextBoxes[code] = {
        code,
        left: r.left - containerRect.left,
        right: r.right - containerRect.left,
        top: r.top - containerRect.top,
        bottom: r.bottom - containerRect.top,
        width: r.width,
        height: r.height,
        centerX: r.left - containerRect.left + r.width / 2,
        centerY: r.top - containerRect.top + r.height / 2,
      };
    }
    setBoxes(nextBoxes);
  }, [containerRef, cardRefs]);

  useLayoutEffect(() => {
    updateMeasurements();
    // Fire after small delays so layout & staggered entrance transitions settle
    const t1 = setTimeout(updateMeasurements, 80);
    const t2 = setTimeout(updateMeasurements, 320);
    const t3 = setTimeout(updateMeasurements, 600);

    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
      clearTimeout(t3);
    };
  }, [updateMeasurements, compareResult, viewDensity]);

  useEffect(() => {
    const handleResize = () => updateMeasurements();
    window.addEventListener('resize', handleResize);
    window.addEventListener('scroll', handleResize, true);

    let ro: ResizeObserver | null = null;
    if (containerRef.current && typeof ResizeObserver !== 'undefined') {
      ro = new ResizeObserver(() => updateMeasurements());
      ro.observe(containerRef.current);
    }

    return () => {
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('scroll', handleResize, true);
      ro?.disconnect();
    };
  }, [containerRef, updateMeasurements]);

  const consensus = compareResult.consensus;
  if (!consensus.has_disagreement) return null;

  // Identify dissenting methods vs majority methods
  const allCodes = compareResult.results.map((r) => r.method.split(' ')[0]);
  const dissentingCodes = allCodes.filter((code) => {
    const styleMeta = consensus.method_styles[code];
    return (
      styleMeta?.card_class?.includes('disagreement') ||
      styleMeta?.status_label?.toLowerCase().includes('dissenting')
    );
  });
  const majorityCodes = allCodes.filter((code) => !dissentingCodes.includes(code));

  // If not all 4 cards measured yet, wait for layout
  if (Object.keys(boxes).length < 2 || containerDimensions.width === 0) {
    return null;
  }

  const isSplit = consensus.majority_verdict === 'split' || dissentingCodes.length === 2;

  // Render 2 vs 2 Split layout connector
  if (isSplit && dissentingCodes.length >= 2) {
    const groupA = dissentingCodes.map((c) => boxes[c]).filter(Boolean);
    const groupB = majorityCodes.map((c) => boxes[c]).filter(Boolean);

    if (groupA.length === 0 || groupB.length === 0) return null;

    const centerA = {
      x: groupA.reduce((sum, b) => sum + b.centerX, 0) / groupA.length,
      y: groupA.reduce((sum, b) => sum + b.centerY, 0) / groupA.length,
    };
    const centerB = {
      x: groupB.reduce((sum, b) => sum + b.centerX, 0) / groupB.length,
      y: groupB.reduce((sum, b) => sum + b.centerY, 0) / groupB.length,
    };
    const midX = (centerA.x + centerB.x) / 2;
    const midY = (centerA.y + centerB.y) / 2;

    return (
      <div className="absolute inset-0 pointer-events-none z-10 overflow-visible">
        <svg
          className="w-full h-full overflow-visible select-none"
          viewBox={`0 0 ${containerDimensions.width} ${containerDimensions.height}`}
        >
          <defs>
            <linearGradient id="splitGradient" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor="#f59e0b" stopOpacity="0.8" />
              <stop offset="50%" stopColor="#ef4444" stopOpacity="0.9" />
              <stop offset="100%" stopColor="#14b8a6" stopOpacity="0.8" />
            </linearGradient>
            <filter id="splitGlow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="3" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          {/* Dividing dashed bridge */}
          <motion.line
            x1={centerA.x}
            y1={centerA.y}
            x2={centerB.x}
            y2={centerB.y}
            stroke="url(#splitGradient)"
            strokeWidth={2}
            strokeDasharray="6 4"
            filter="url(#splitGlow)"
            initial={{ pathLength: 0, opacity: 0 }}
            animate={{ pathLength: 1, opacity: 0.85 }}
            transition={{ duration: 0.65, ease: [0.16, 1, 0.3, 1], delay: 0.2 }}
          />

          {/* Group Nodes */}
          <circle cx={centerA.x} cy={centerA.y} r={5} fill="#f59e0b" stroke="#0f172a" strokeWidth={2} />
          <circle cx={centerB.x} cy={centerB.y} r={5} fill="#14b8a6" stroke="#0f172a" strokeWidth={2} />
        </svg>

        {/* Center Pill */}
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.35, delay: 0.4 }}
          style={{
            position: 'absolute',
            left: midX,
            top: midY,
            transform: 'translate(-50%, -50%)',
          }}
          className="pointer-events-auto flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-900/95 border border-amber-500/50 shadow-xl shadow-amber-500/10 text-[11px] font-bold text-amber-300 backdrop-blur-md whitespace-nowrap"
        >
          <GitCompare className="h-3.5 w-3.5 text-amber-400" />
          <span>2 vs 2 Split Decision</span>
        </motion.div>
      </div>
    );
  }

  // Canonical Case: 1 Dissenting card vs 3 Majority cards
  const dissentCode = dissentingCodes[0] || allCodes[0];
  const dissentBox = boxes[dissentCode];
  if (!dissentBox) return null;

  const majorityBoxes = majorityCodes.map((c) => boxes[c]).filter(Boolean);
  if (majorityBoxes.length === 0) return null;

  // Determine whether grid is 2-column or 1-column
  const allCardBoxes = Object.values(boxes);
  const minLeft = Math.min(...allCardBoxes.map((b) => b.left));
  const maxLeft = Math.max(...allCardBoxes.map((b) => b.left));
  const isTwoColumn = maxLeft - minLeft > 80;

  // Calculate central gap coordinates
  let centerJunctionX: number;
  let centerJunctionY: number;

  if (isTwoColumn) {
    // Find column split X and row split Y
    const col0Cards = allCardBoxes.filter((b) => Math.abs(b.left - minLeft) < 30);
    const col1Cards = allCardBoxes.filter((b) => b.left > minLeft + 30);
    const col0Right = col0Cards.length > 0 ? Math.max(...col0Cards.map((b) => b.right)) : dissentBox.right;
    const col1Left = col1Cards.length > 0 ? Math.min(...col1Cards.map((b) => b.left)) : dissentBox.right + 16;
    centerJunctionX = (col0Right + col1Left) / 2;

    const row0Cards = allCardBoxes.filter((b) => b.top < (containerDimensions.height / 2));
    const row1Cards = allCardBoxes.filter((b) => b.top >= (containerDimensions.height / 2));
    const row0Bottom = row0Cards.length > 0 ? Math.max(...row0Cards.map((b) => b.bottom)) : containerDimensions.height / 2 - 8;
    const row1Top = row1Cards.length > 0 ? Math.min(...row1Cards.map((b) => b.top)) : containerDimensions.height / 2 + 8;
    centerJunctionY = (row0Bottom + row1Top) / 2;
  } else {
    // Single column: center line along right or left edge
    centerJunctionX = dissentBox.right - 4;
    centerJunctionY = dissentBox.centerY;
  }

  // Anchor on the dissenting card facing the center junction
  const dissentAnchor = {
    x: isTwoColumn
      ? dissentBox.centerX < centerJunctionX
        ? dissentBox.right
        : dissentBox.left
      : dissentBox.right - 10,
    y: isTwoColumn
      ? dissentBox.centerY < centerJunctionY
        ? dissentBox.bottom - Math.min(28, dissentBox.height / 3)
        : dissentBox.top + Math.min(28, dissentBox.height / 3)
      : dissentBox.centerY,
  };

  // Anchors for each majority card facing the junction
  const majorityAnchors = majorityBoxes.map((mBox) => {
    return {
      code: mBox.code,
      x: isTwoColumn
        ? mBox.centerX < centerJunctionX
          ? mBox.right
          : mBox.left
        : mBox.right - 10,
      y: isTwoColumn
        ? mBox.centerY < centerJunctionY
          ? mBox.bottom - Math.min(28, mBox.height / 3)
          : mBox.top + Math.min(28, mBox.height / 3)
        : mBox.centerY,
    };
  });

  // Calculate bracket bounding curve for majority cluster
  const minMajY = Math.min(...majorityAnchors.map((a) => a.y));
  const maxMajY = Math.max(...majorityAnchors.map((a) => a.y));
  const bracketMidY = (minMajY + maxMajY) / 2;

  // Bracket spine path coordinates
  // Generates an SVG bracket grouping the majority cards and pointing to the dissenting card
  const bracketOffsetX = isTwoColumn ? (centerJunctionX - dissentAnchor.x) * 0.35 : 12;
  const bracketSpineX = centerJunctionX + bracketOffsetX;

  // Bracket Path: An elegant bracket spanning majority nodes with a center cusp pointing to dissenting card
  const bracketPath = `M ${majorityAnchors[0].x} ${majorityAnchors[0].y} Q ${bracketSpineX} ${majorityAnchors[0].y}, ${bracketSpineX} ${(majorityAnchors[0].y + bracketMidY) / 2} T ${bracketSpineX} ${bracketMidY} L ${dissentAnchor.x} ${dissentAnchor.y}`;

  // Midpoint for floating badge
  const calloutX = isTwoColumn
    ? (dissentAnchor.x + centerJunctionX) / 2
    : dissentAnchor.x - 40;
  const calloutY = isTwoColumn
    ? (dissentAnchor.y + centerJunctionY) / 2
    : dissentAnchor.y;

  return (
    <div className="absolute inset-0 pointer-events-none z-20 overflow-visible">
      <svg
        className="w-full h-full overflow-visible select-none"
        viewBox={`0 0 ${containerDimensions.width} ${containerDimensions.height}`}
      >
        <defs>
          {/* Gradient radiating from Dissenting card (amber/coral) to Majority cards (teal/cyan) */}
          <linearGradient
            id="dissentLineGradient"
            x1={dissentAnchor.x}
            y1={dissentAnchor.y}
            x2={centerJunctionX}
            y2={centerJunctionY}
            gradientUnits="userSpaceOnUse"
          >
            <stop offset="0%" stopColor="#f59e0b" stopOpacity="0.95" />
            <stop offset="45%" stopColor="#f43f5e" stopOpacity="0.75" />
            <stop offset="100%" stopColor="#14b8a6" stopOpacity="0.85" />
          </linearGradient>

          {/* Subtle line glow */}
          <filter id="dissentGlow" x="-30%" y="-30%" width="160%" height="160%">
            <feGaussianBlur stdDeviation="2.5" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* 1. Connecting curved lines from Dissenting card to each Majority card */}
        {majorityAnchors.map((maj) => {
          // Bezier control points bending gently through central gap
          const cp1x = isTwoColumn
            ? dissentAnchor.x + (centerJunctionX - dissentAnchor.x) * 0.7
            : dissentAnchor.x + 18;
          const cp1y = isTwoColumn ? dissentAnchor.y : (dissentAnchor.y + maj.y) / 2;

          const cp2x = isTwoColumn
            ? maj.x - (maj.x - centerJunctionX) * 0.7
            : maj.x + 18;
          const cp2y = isTwoColumn ? maj.y : (dissentAnchor.y + maj.y) / 2;

          const pathD = `M ${dissentAnchor.x} ${dissentAnchor.y} C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${maj.x} ${maj.y}`;

          return (
            <g key={`connector-${maj.code}`}>
              {/* Outer soft glow trace */}
              <motion.path
                d={pathD}
                fill="none"
                stroke="#f59e0b"
                strokeWidth={3.5}
                strokeOpacity={0.25}
                filter="url(#dissentGlow)"
                initial={{ pathLength: 0, opacity: 0 }}
                animate={{ pathLength: 1, opacity: 0.35 }}
                transition={{
                  duration: 0.7,
                  ease: [0.16, 1, 0.3, 1],
                  delay: 0.15,
                }}
              />

              {/* Main animated drawn path */}
              <motion.path
                d={pathD}
                fill="none"
                stroke="url(#dissentLineGradient)"
                strokeWidth={2}
                strokeDasharray="6 3.5"
                initial={{ pathLength: 0, opacity: 0 }}
                animate={{ pathLength: 1, opacity: 0.9 }}
                transition={{
                  duration: 0.75,
                  ease: [0.16, 1, 0.3, 1],
                  delay: 0.2,
                }}
              />

              {/* Majority consensus node */}
              <motion.circle
                cx={maj.x}
                cy={maj.y}
                r={4}
                fill="#14b8a6"
                stroke="#0f172a"
                strokeWidth={1.5}
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ duration: 0.3, delay: 0.55 }}
              />
            </g>
          );
        })}

        {/* 2. Grouping Bracket Spine connecting Majority Cards */}
        {isTwoColumn && majorityAnchors.length >= 2 && (
          <motion.path
            d={bracketPath}
            fill="none"
            stroke="#14b8a6"
            strokeWidth={1.5}
            strokeOpacity={0.4}
            strokeDasharray="4 2"
            initial={{ pathLength: 0, opacity: 0 }}
            animate={{ pathLength: 1, opacity: 0.5 }}
            transition={{ duration: 0.6, delay: 0.35 }}
          />
        )}

        {/* 3. Dissenting Card Origin Node: Glowing pulse ring & core */}
        <g>
          {/* Pulsing ripple ring */}
          <motion.circle
            cx={dissentAnchor.x}
            cy={dissentAnchor.y}
            r={11}
            fill="none"
            stroke="#f59e0b"
            strokeWidth={1.5}
            initial={{ scale: 0.8, opacity: 0.8 }}
            animate={{ scale: [1, 1.45, 1], opacity: [0.7, 0.15, 0.7] }}
            transition={{
              duration: 2.2,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
          />

          {/* Dissenting anchor core */}
          <motion.circle
            cx={dissentAnchor.x}
            cy={dissentAnchor.y}
            r={6}
            fill="#f59e0b"
            stroke="#0f172a"
            strokeWidth={2}
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', stiffness: 350, damping: 20, delay: 0.2 }}
          />

          <circle cx={dissentAnchor.x} cy={dissentAnchor.y} r={2} fill="#ffffff" />
        </g>
      </svg>

      {/* 4. Glassmorphic Connecting Callout Pill */}
      <AnimatePresence>
        <motion.div
          initial={{ scale: 0.85, opacity: 0, y: -6 }}
          animate={{ scale: 1, opacity: 1, y: 0 }}
          exit={{ scale: 0.85, opacity: 0 }}
          transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1], delay: 0.4 }}
          style={{
            position: 'absolute',
            left: calloutX,
            top: calloutY,
            transform: 'translate(-50%, -50%)',
          }}
          className="pointer-events-auto flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-900/95 border border-amber-500/40 shadow-xl shadow-amber-500/15 text-[11px] font-bold text-amber-300 backdrop-blur-md select-none will-change-transform"
        >
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75" />
            <span className="relative inline-flex rounded-full h-2 w-2 bg-amber-500" />
          </span>
          <AlertTriangle className="h-3 w-3 text-amber-400 shrink-0" />
          <span className="tracking-tight">{dissentCode} Dissents</span>
          <span className="text-[10px] text-slate-400 font-mono font-normal border-l border-slate-700/80 pl-1.5">
            {consensus.num_phishing} vs {consensus.num_legitimate}
          </span>
        </motion.div>
      </AnimatePresence>
    </div>
  );
};
