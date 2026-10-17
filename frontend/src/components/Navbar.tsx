import React, { useEffect, useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { Shield, Terminal, BarChart3, FlaskConical, Sun, Moon, Menu, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { apiClient } from '../api/client';
import { Badge } from './Badge';
import { useTheme } from '../hooks/useTheme';

const GITHUB_REPO_URL = 'https://github.com/siddharthsingh18/IFSI-for-phishing-email-detection';

const GitHubIcon: React.FC<{ className?: string }> = ({ className = 'h-4 w-4' }) => (
  <svg className={`${className} fill-current`} viewBox="0 0 24 24" aria-hidden="true">
    <path
      fillRule="evenodd"
      clipRule="evenodd"
      d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"
    />
  </svg>
);

export const Navbar: React.FC = () => {
  const { theme, toggleTheme } = useTheme();
  const location = useLocation();
  const [healthStatus, setHealthStatus] = useState<'checking' | 'online' | 'degraded' | 'offline'>('checking');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [prevPath, setPrevPath] = useState(location.pathname);
  const [isScrolled, setIsScrolled] = useState(false);

  // Close mobile menu on route change
  if (prevPath !== location.pathname) {
    setPrevPath(location.pathname);
    setMobileMenuOpen(false);
  }

  useEffect(() => {
    const handleScroll = () => {
      const scrolled = typeof window !== 'undefined' ? window.scrollY > 20 : false;
      setIsScrolled(scrolled);
    };
    handleScroll();
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    let mounted = true;
    apiClient
      .getHealth()
      .then((res) => {
        if (!mounted) return;
        setHealthStatus(res.status === 'ok' ? 'online' : 'degraded');
      })
      .catch(() => {
        if (!mounted) return;
        setHealthStatus('offline');
      });

    return () => {
      mounted = false;
    };
  }, []);

  const navItems = [
    { to: '/', label: 'About', icon: Shield },
    { to: '/test', label: 'Live Test', icon: Terminal },
    { to: '/dashboard', label: 'Dashboard', icon: BarChart3 },
    { to: '/injection-lab', label: 'Injection Lab', icon: FlaskConical },
  ];

  return (
    <header
      className={`sticky top-0 z-50 transition-all duration-200 ${
        isScrolled
          ? 'bg-slate-950/80 backdrop-blur-md border-b border-slate-800/80 elevation-card'
          : 'bg-slate-950 border-b border-transparent'
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Left: Logo & Project Name */}
        <div className="flex items-center min-w-0 lg:min-w-[190px] xl:min-w-[200px] flex-shrink-0">
          <NavLink
            to="/"
            className="flex items-center gap-3 group transition-all duration-150 hover:scale-[1.02] hover:brightness-105 active:scale-[0.97] rounded-xl focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950"
          >
            <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-teal-500 via-cyan-400 to-emerald-400 p-[1px] elevation-card group-hover:elevation-hover transition-all duration-150 flex-shrink-0">
              <div className="h-full w-full rounded-[11px] bg-slate-950 flex items-center justify-center transition-colors group-hover:bg-slate-900">
                <Shield className="h-5 w-5 text-teal-400 group-hover:text-teal-300 transition-colors" />
              </div>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-base tracking-tight text-white font-['Plus_Jakarta_Sans',sans-serif]">
                  IFSI
                </span>
                <span className="text-slate-400 font-medium text-sm hidden sm:inline">
                  Phishing Detection
                </span>
                <Badge variant="accent" size="sm" className="hidden sm:inline-flex">
                  Benchmark
                </Badge>
              </div>
              <p className="text-[11px] text-slate-400 font-mono -mt-0.5 hidden sm:block">
                Injection-First Staged Inference
              </p>
            </div>
          </NavLink>
        </div>

        {/* Center: Centered Nav Links (About / Live Test / Dashboard / Injection Lab) */}
        <nav
          className="hidden lg:flex items-center justify-center gap-1 sm:gap-2 flex-1"
          aria-label="Desktop Navigation"
        >
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === '/'}
                className={({ isActive }) =>
                  `flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs sm:text-sm font-medium border transition-all duration-150 hover:scale-[1.02] hover:brightness-110 active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 ${
                    isActive
                      ? 'bg-teal-500/10 text-teal-300 border-teal-500/30 font-semibold'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60 border-transparent'
                  }`
                }
              >
                {({ isActive }) => (
                  <>
                    <Icon className={`h-4 w-4 ${isActive ? 'text-teal-400' : 'text-slate-400'}`} />
                    <span>{item.label}</span>
                    {isActive && (
                      <span className="h-1.5 w-1.5 rounded-full bg-teal-400 animate-pulse hidden sm:inline-block" />
                    )}
                  </>
                )}
              </NavLink>
            );
          })}
        </nav>

        {/* Right: Dark filled rounded-full "View on GitHub" button + Theme Toggle & Mobile Controls */}
        <div className="flex items-center justify-end gap-2 sm:gap-3 min-w-0 lg:min-w-[190px] xl:min-w-[200px] flex-shrink-0">
          {/* Dark filled rounded-full View on GitHub button */}
          <a
            href={GITHUB_REPO_URL}
            target="_blank"
            rel="noopener noreferrer"
            aria-label="View on GitHub repository"
            className="hidden sm:inline-flex items-center gap-2 px-4 py-2 rounded-full text-xs sm:text-sm font-semibold bg-slate-900 hover:bg-slate-850 text-slate-200 hover:text-teal-300 border border-slate-700/80 hover:border-teal-500/40 transition-all duration-150 hover:scale-[1.02] active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 elevation-card hover:elevation-hover"
          >
            <GitHubIcon className="h-4 w-4" />
            <span>View on GitHub</span>
          </a>

          {/* Dark / Light Mode Toggle */}
          <button
            type="button"
            onClick={toggleTheme}
            aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
            title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode (currently ${theme})`}
            className="p-2 rounded-xl border border-slate-700/80 bg-slate-900/80 text-slate-300 hover:text-teal-400 hover:border-teal-500/40 hover:bg-slate-850 transition-all duration-150 hover:scale-[1.05] hover:brightness-110 active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 elevation-card flex items-center justify-center cursor-pointer"
          >
            {theme === 'dark' ? (
              <Sun className="h-4 w-4 text-amber-300 transition-transform duration-150" />
            ) : (
              <Moon className="h-4 w-4 text-teal-600 transition-transform duration-150" />
            )}
          </button>

          {/* Mobile Hamburger Toggle Button (< lg) */}
          <button
            type="button"
            onClick={() => setMobileMenuOpen((prev) => !prev)}
            aria-expanded={mobileMenuOpen}
            aria-controls="mobile-nav-menu"
            aria-label="Toggle navigation menu"
            className="lg:hidden p-2 rounded-xl border border-slate-700/80 bg-slate-900/80 text-slate-300 hover:text-teal-400 hover:border-teal-500/40 hover:scale-[1.05] hover:brightness-110 transition-all duration-150 active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 elevation-card flex items-center justify-center cursor-pointer"
          >
            {mobileMenuOpen ? (
              <X className="h-5 w-5 text-teal-400" />
            ) : (
              <Menu className="h-5 w-5" />
            )}
          </button>
        </div>
      </div>

      {/* Mobile Navigation Dropdown Drawer (< lg) */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div
            id="mobile-nav-menu"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2, ease: 'easeInOut' }}
            className="lg:hidden border-t border-slate-800/80 bg-slate-950/95 backdrop-blur-xl px-4 py-4 space-y-3"
          >
            <nav className="flex flex-col gap-1.5" aria-label="Mobile Navigation Drawer">
              {navItems.map((item) => {
                const Icon = item.icon;
                return (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    end={item.to === '/'}
                    onClick={() => setMobileMenuOpen(false)}
                    className={({ isActive }) =>
                      `flex items-center justify-between px-4 py-3 rounded-xl text-sm font-medium border transition-all duration-150 hover:scale-[1.01] hover:brightness-105 active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 ${
                        isActive
                          ? 'bg-teal-500/15 text-teal-300 border-teal-500/40 font-semibold'
                          : 'text-slate-300 hover:text-white hover:bg-slate-900 border-transparent'
                      }`
                    }
                  >
                    {({ isActive }) => (
                      <>
                        <div className="flex items-center gap-3">
                          <Icon className={`h-4 w-4 ${isActive ? 'text-teal-400' : 'text-slate-400'}`} />
                          <span>{item.label}</span>
                        </div>
                        {isActive && (
                          <span className="h-2 w-2 rounded-full bg-teal-400" />
                        )}
                      </>
                    )}
                  </NavLink>
                );
              })}
            </nav>

            {/* Mobile "View on GitHub" button */}
            <div className="pt-1">
              <a
                href={GITHUB_REPO_URL}
                target="_blank"
                rel="noopener noreferrer"
                onClick={() => setMobileMenuOpen(false)}
                className="flex items-center justify-center gap-2 w-full py-2.5 px-4 rounded-full text-xs font-semibold bg-slate-900 hover:bg-slate-850 text-slate-200 hover:text-teal-300 border border-slate-700/80 hover:scale-[1.02] hover:brightness-105 transition-all duration-150 active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 elevation-card"
              >
                <GitHubIcon className="h-4 w-4" />
                <span>View on GitHub</span>
              </a>
            </div>

            {/* Mobile API Health Indicator */}
            <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between px-2">
              <span className="text-xs text-slate-400">Backend API Status:</span>
              <Badge
                variant={
                  healthStatus === 'online'
                    ? 'legitimate'
                    : healthStatus === 'degraded'
                    ? 'injection'
                    : healthStatus === 'offline'
                    ? 'phishing'
                    : 'neutral'
                }
                size="sm"
                dot
                pulse={healthStatus === 'online'}
              >
                API: {healthStatus}
              </Badge>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
};

export default Navbar;
