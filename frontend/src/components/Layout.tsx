import React from 'react';
import { useLocation, useOutlet } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';
import { Navbar } from './Navbar';

export const Layout: React.FC = () => {
  const location = useLocation();
  const outlet = useOutlet();

  return (
    <div className="min-h-screen w-full max-w-full overflow-x-clip bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-teal-500/30 selection:text-teal-200">
      {/* Page-wide subtle noise/grain texture overlay (pure SVG, low opacity) */}
      <div className="grain-overlay" aria-hidden="true" />
      <Navbar />
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <AnimatePresence mode="wait">
          {outlet && React.cloneElement(outlet, { key: location.pathname })}
        </AnimatePresence>
      </main>
      <footer className="border-t border-slate-900 bg-slate-950/60 py-6 text-xs text-slate-400">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-slate-300 font-['Plus_Jakarta_Sans',sans-serif]">IFSI</span>
            <span>&bull;</span>
            <span>Created by <strong className="text-slate-200 font-medium">Siddharth Singh</strong></span>
          </div>
          <div className="flex items-center gap-4 text-slate-400">
            <a
              href="https://github.com/siddharthsingh18/IFSI-for-phishing-email-detection"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-teal-400 transition-colors"
            >
              GitHub
            </a>
            <span>&bull;</span>
            <span>FastAPI + Vite React TS</span>
          </div>
        </div>
      </footer>
    </div>
  );
};
