import React from 'react';

/**
 * Geometric Abstract Network Illustration for Hero Right Column.
 * Features:
 * - Geometric connected nodes and data pipelines in teal/cyan/emerald accent colors.
 * - Central hero node styled with an intricate geometric shield & lock icon.
 * - Soft diffuse radial ambient glow.
 * - IMPORTANT CONSTRAINT SATISFIED: The top-right third (X: 330 to 600, Y: 0 to 220)
 *   is kept completely empty with zero visual elements to host the upcoming floating card.
 */
export const HeroNetworkIllustration: React.FC = () => {
  return (
    <div className="relative w-full max-w-full h-full min-w-0 min-h-[240px] sm:min-h-[380px] lg:min-h-[460px] flex items-center justify-center overflow-hidden">
      <svg
        viewBox="0 0 600 480"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="w-full max-w-full h-auto max-h-[480px] select-none"
        aria-hidden="true"
      >
        <defs>
          {/* Ambient Glows */}
          <radialGradient id="heroNetGlow" cx="35%" cy="52%" r="55%" fx="35%" fy="52%">
            <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.24" />
            <stop offset="45%" stopColor="#14b8a6" stopOpacity="0.09" />
            <stop offset="85%" stopColor="#020617" stopOpacity="0" />
          </radialGradient>

          <radialGradient id="shieldCoreGlow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#2dd4bf" stopOpacity="0.6" />
            <stop offset="60%" stopColor="#14b8a6" stopOpacity="0.2" />
            <stop offset="100%" stopColor="#0f172a" stopOpacity="0" />
          </radialGradient>

          {/* Connection Line Gradients */}
          <linearGradient id="gradTealCyan" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.75" />
            <stop offset="100%" stopColor="#10b981" stopOpacity="0.75" />
          </linearGradient>

          <linearGradient id="gradCyanMuted" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#22d3ee" stopOpacity="0.45" />
            <stop offset="100%" stopColor="#0d9488" stopOpacity="0.2" />
          </linearGradient>

          <linearGradient id="shieldMetalGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#0f172a" />
            <stop offset="100%" stopColor="#042f2e" />
          </linearGradient>

          {/* Node Gradients */}
          <linearGradient id="nodeActiveGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#34d399" />
            <stop offset="100%" stopColor="#06b6d4" />
          </linearGradient>
        </defs>

        {/* Ambient Glow Backdrop (Centered on left/middle network cluster) */}
        <ellipse cx="220" cy="240" rx="210" ry="180" fill="url(#heroNetGlow)" />

        {/* =====================================================================
            1. GEOMETRIC BACKGROUND GUIDES (Left & Lower Canvas Only)
            ===================================================================== */}
        {/* Subtle grid lines strictly within bottom/left half */}
        <g stroke="#0f766e" strokeOpacity="0.12" strokeWidth="0.8">
          <line x1="60" y1="120" x2="300" y2="120" strokeDasharray="3 6" />
          <line x1="60" y1="240" x2="320" y2="240" strokeDasharray="3 6" />
          <line x1="60" y1="360" x2="480" y2="360" strokeDasharray="3 6" />
          <line x1="120" y1="80" x2="120" y2="400" strokeDasharray="3 6" />
          <line x1="240" y1="80" x2="240" y2="420" strokeDasharray="3 6" />
          <line x1="360" y1="240" x2="360" y2="420" strokeDasharray="3 6" />
        </g>

        {/* Cybernetic Accent Crosshairs & Hex Coordinates */}
        <g stroke="#14b8a6" strokeOpacity="0.4" strokeWidth="1">
          {/* Crosshair 1 (Far Left) */}
          <path d="M50 80 H60 M55 75 V85" />
          {/* Crosshair 2 (Bottom Left) */}
          <path d="M70 380 H80 M75 375 V385" />
          {/* Crosshair 3 (Bottom Center) */}
          <path d="M250 430 H260 M255 425 V435" />
          {/* Crosshair 4 (Mid Lower) */}
          <path d="M430 420 H440 M435 415 V425" />
        </g>

        {/* Small Technical Annotations */}
        <text x="60" y="65" fill="#2dd4bf" fillOpacity="0.45" fontSize="9" fontFamily="monospace" letterSpacing="0.1em">
          SYS.INFERENCE // M1_M4
        </text>
        <text x="60" y="415" fill="#14b8a6" fillOpacity="0.4" fontSize="8" fontFamily="monospace" letterSpacing="0.08em">
          FAISS_VEC_IDX : 4178 EX
        </text>
        <text x="360" y="440" fill="#2dd4bf" fillOpacity="0.4" fontSize="8" fontFamily="monospace" letterSpacing="0.08em">
          DECOUPLED_VERIFY [STAGED]
        </text>

        {/* =====================================================================
            2. NETWORK CONNECTION EDGES (All stay strictly out of top-right third)
            ===================================================================== */}
        {/* Secondary / Data flow paths */}
        <g stroke="url(#gradCyanMuted)" strokeWidth="1.2">
          {/* Cluster Left */}
          <line x1="80" y1="140" x2="150" y2="90" />
          <line x1="80" y1="140" x2="110" y2="260" strokeDasharray="4 4" />
          <line x1="150" y1="90" x2="230" y2="80" />
          <line x1="230" y1="80" x2="280" y2="140" />
          <line x1="110" y1="260" x2="160" y2="360" />
          <line x1="160" y1="360" x2="280" y2="380" strokeDasharray="3 3" />
          <line x1="280" y1="380" x2="370" y2="360" />
          
          {/* Bottom Right Pipeline */}
          <line x1="370" y1="360" x2="460" y2="370" />
          <line x1="460" y1="370" x2="470" y2="300" strokeDasharray="4 4" />
          <line x1="470" y1="300" x2="530" y2="350" />
        </g>

        {/* Primary High-Priority Neural Connections (Leading into Shield Node) */}
        <g stroke="url(#gradTealCyan)" strokeWidth="1.8">
          <line x1="150" y1="90" x2="210" y2="210" />
          <line x1="110" y1="260" x2="210" y2="210" />
          <line x1="160" y1="360" x2="210" y2="210" />
          <line x1="280" y1="140" x2="210" y2="210" />
          <line x1="210" y1="210" x2="310" y2="240" />
          <line x1="210" y1="210" x2="280" y2="380" />
          <line x1="310" y1="240" x2="370" y2="360" />
          <line x1="310" y1="240" x2="390" y2="270" />
          <line x1="390" y1="270" x2="470" y2="300" />
        </g>

        {/* Data pulse packet dots moving along main pipelines */}
        <circle cx="178" cy="154" r="2.5" fill="#a7f3d0" />
        <circle cx="162" cy="236" r="2.5" fill="#67e8f9" />
        <circle cx="260" cy="225" r="2.5" fill="#34d399" />
        <circle cx="350" cy="255" r="2" fill="#22d3ee" />
        <circle cx="430" cy="285" r="2" fill="#34d399" />
        <circle cx="328" cy="370" r="2" fill="#5eead4" />

        {/* =====================================================================
            3. SECONDARY NODES (Concentric geometric rings & glowing cores)
            ===================================================================== */}
        {/* Node: Ingestion Point (80, 140) */}
        <g transform="translate(80, 140)">
          <circle cx="0" cy="0" r="10" stroke="#0e7490" strokeOpacity="0.4" strokeDasharray="2 2" />
          <circle cx="0" cy="0" r="5" fill="#090d16" stroke="#06b6d4" strokeWidth="1.5" />
          <circle cx="0" cy="0" r="2" fill="#22d3ee" />
        </g>

        {/* Node: Header Parser (150, 90) */}
        <g transform="translate(150, 90)">
          <circle cx="0" cy="0" r="11" stroke="#0f766e" strokeOpacity="0.5" strokeDasharray="3 3" />
          <circle cx="0" cy="0" r="6" fill="#090d16" stroke="#14b8a6" strokeWidth="1.5" />
          <circle cx="0" cy="0" r="2.5" fill="#34d399" />
        </g>

        {/* Node: Upper Constellation Anchor (230, 80) */}
        <g transform="translate(230, 80)">
          <circle cx="0" cy="0" r="4" fill="#090d16" stroke="#06b6d4" strokeWidth="1.2" />
          <circle cx="0" cy="0" r="1.5" fill="#67e8f9" />
        </g>

        {/* Node: Tokenizer Matrix (280, 140) */}
        <g transform="translate(280, 140)">
          <circle cx="0" cy="0" r="12" stroke="#14b8a6" strokeOpacity="0.4" />
          <circle cx="0" cy="0" r="6" fill="#090d16" stroke="#2dd4bf" strokeWidth="1.5" />
          <circle cx="0" cy="0" r="2.5" fill="#a7f3d0" />
        </g>

        {/* Node: Vector Encoder (110, 260) */}
        <g transform="translate(110, 260)">
          <circle cx="0" cy="0" r="12" stroke="#0f766e" strokeOpacity="0.5" strokeDasharray="2 2" />
          <circle cx="0" cy="0" r="6" fill="#090d16" stroke="#14b8a6" strokeWidth="1.5" />
          <circle cx="0" cy="0" r="2.5" fill="#2dd4bf" />
        </g>

        {/* Node: Embedding Cluster (160, 360) */}
        <g transform="translate(160, 360)">
          <circle cx="0" cy="0" r="14" stroke="#0891b2" strokeOpacity="0.4" />
          <circle cx="0" cy="0" r="7" fill="#090d16" stroke="#06b6d4" strokeWidth="1.5" />
          <circle cx="0" cy="0" r="3" fill="#38bdf8" />
        </g>

        {/* Node: FAISS Vector Retriever (280, 380) */}
        <g transform="translate(280, 380)">
          <circle cx="0" cy="0" r="15" stroke="#059669" strokeOpacity="0.4" strokeDasharray="3 3" />
          <circle cx="0" cy="0" r="7" fill="#090d16" stroke="#10b981" strokeWidth="1.6" />
          <circle cx="0" cy="0" r="3" fill="#34d399" />
        </g>

        {/* Node: Staged Inference Evaluator (310, 240) */}
        <g transform="translate(310, 240)">
          <circle cx="0" cy="0" r="14" stroke="#0d9488" strokeOpacity="0.5" />
          <circle cx="0" cy="0" r="7" fill="#090d16" stroke="#2dd4bf" strokeWidth="1.6" />
          <circle cx="0" cy="0" r="3" fill="#5eead4" />
        </g>

        {/* Node: Exemplar Correlator (370, 360) */}
        <g transform="translate(370, 360)">
          <circle cx="0" cy="0" r="11" stroke="#0f766e" strokeOpacity="0.4" strokeDasharray="2 2" />
          <circle cx="0" cy="0" r="5.5" fill="#090d16" stroke="#14b8a6" strokeWidth="1.4" />
          <circle cx="0" cy="0" r="2" fill="#2dd4bf" />
        </g>

        {/* Node: Cross-Model Validator (390, 270) */}
        <g transform="translate(390, 270)">
          <circle cx="0" cy="0" r="12" stroke="#0284c7" strokeOpacity="0.4" />
          <circle cx="0" cy="0" r="6" fill="#090d16" stroke="#38bdf8" strokeWidth="1.5" />
          <circle cx="0" cy="0" r="2.5" fill="#7dd3fc" />
        </g>

        {/* Node: Confidence Arbiter (460, 370) */}
        <g transform="translate(460, 370)">
          <circle cx="0" cy="0" r="10" stroke="#059669" strokeOpacity="0.4" strokeDasharray="2 2" />
          <circle cx="0" cy="0" r="5" fill="#090d16" stroke="#10b981" strokeWidth="1.4" />
          <circle cx="0" cy="0" r="2" fill="#34d399" />
        </g>

        {/* Node: Output Filter Gateway (470, 300) */}
        <g transform="translate(470, 300)">
          <circle cx="0" cy="0" r="14" stroke="#0f766e" strokeOpacity="0.5" strokeDasharray="3 3" />
          <circle cx="0" cy="0" r="7" fill="#090d16" stroke="#14b8a6" strokeWidth="1.6" />
          <circle cx="0" cy="0" r="3" fill="#2dd4bf" />
        </g>

        {/* Node: Clean Delivery Terminal (530, 350) */}
        <g transform="translate(530, 350)">
          <circle cx="0" cy="0" r="11" stroke="#0891b2" strokeOpacity="0.4" />
          <circle cx="0" cy="0" r="5" fill="#090d16" stroke="#06b6d4" strokeWidth="1.5" />
          <circle cx="0" cy="0" r="2" fill="#67e8f9" />
        </g>

        {/* =====================================================================
            4. HERO NODE: THE GEOMETRIC SHIELD & LOCK NODE (210, 210)
            ===================================================================== */}
        <g transform="translate(210, 210)">
          {/* Outer Pulsing Aura */}
          <circle cx="0" cy="0" r="44" fill="url(#shieldCoreGlow)" />
          
          {/* Geometric Concentric Rings */}
          <circle cx="0" cy="0" r="38" stroke="#06b6d4" strokeOpacity="0.3" strokeDasharray="4 4" strokeWidth="1" />
          <circle cx="0" cy="0" r="29" stroke="#14b8a6" strokeOpacity="0.5" strokeDasharray="6 3" strokeWidth="1.2" />
          
          {/* Hexagonal Protective Housing */}
          <path
            d="M0 -22 L19 -11 L19 11 L0 22 L-19 11 L-19 -11 Z"
            fill="url(#shieldMetalGrad)"
            stroke="url(#nodeActiveGrad)"
            strokeWidth="2"
            strokeLinejoin="round"
          />

          {/* Geometric Inner Shield Contour */}
          <path
            d="M0 -12 L10 -7.5 V0 C10 6.5 6 11 0 13 C-6 11 -10 6.5 -10 0 V-7.5 Z"
            fill="#090d16"
            stroke="#2dd4bf"
            strokeWidth="1.4"
            strokeLinejoin="round"
          />

          {/* Precision Lock Icon Geometry inside the Shield */}
          {/* Shackle */}
          <path
            d="M-3 -1 V-3.5 C-3 -5.2 -1.7 -6.5 0 -6.5 C1.7 -6.5 3 -5.2 3 -3.5 V-1"
            stroke="#67e8f9"
            strokeWidth="1.3"
            strokeLinecap="round"
            fill="none"
          />
          {/* Lock Body */}
          <rect
            x="-4.5"
            y="-1"
            width="9"
            height="7"
            rx="1.5"
            fill="#10b981"
            stroke="#34d399"
            strokeWidth="0.8"
          />
          {/* Keyhole */}
          <circle cx="0" cy="1.8" r="1" fill="#022c22" />
          <line x1="0" y1="2.2" x2="0" y2="4" stroke="#022c22" strokeWidth="0.8" />

          {/* Radiating Signal Markers */}
          <path d="M-28 0 A28 28 0 0 1 -20 -20" stroke="#22d3ee" strokeOpacity="0.7" strokeWidth="1.5" fill="none" />
          <path d="M28 0 A28 28 0 0 1 20 20" stroke="#34d399" strokeOpacity="0.7" strokeWidth="1.5" fill="none" />
        </g>

        {/* =====================================================================
            5. VERIFICATION: TOP-RIGHT THIRD (X: 330–600, Y: 0–220)
               Strictly empty space — reserved for the floating card overlay.
            ===================================================================== */}
      </svg>
    </div>
  );
};

export default HeroNetworkIllustration;
