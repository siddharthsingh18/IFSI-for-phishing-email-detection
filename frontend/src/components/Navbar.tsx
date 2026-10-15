import React, { useEffect, useState } from 'react';
import { NavLink } from 'react-router-dom';
import { Shield, Terminal, BarChart3, FlaskConical } from 'lucide-react';
import { apiClient } from '../api/client';
import { Badge } from './Badge';

export const Navbar: React.FC = () => {
  const [healthStatus, setHealthStatus] = useState<'checking' | 'online' | 'degraded' | 'offline'>('checking');

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
    { to: '/', label: 'About / Landing', icon: Shield },
    { to: '/test', label: 'Live Test', icon: Terminal },
    { to: '/dashboard', label: 'Dashboard', icon: BarChart3 },
    { to: '/injection-lab', label: 'Injection Lab', icon: FlaskConical },
  ];

  return (
    <header className="sticky top-0 z-50 border-b border-slate-800/80 bg-slate-950/85 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Project Name / Logo Text */}
        <NavLink to="/" className="flex items-center gap-3 group">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-teal-500 via-cyan-400 to-emerald-400 p-[1px] shadow-lg shadow-teal-500/20">
            <div className="h-full w-full rounded-[11px] bg-slate-950 flex items-center justify-center transition-colors group-hover:bg-slate-900">
              <Shield className="h-5 w-5 text-teal-400 group-hover:text-teal-300 transition-colors" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-base tracking-tight text-white font-['Plus_Jakarta_Sans',sans-serif]">
                IFSI
              </span>
              <span className="text-slate-400 font-medium text-sm">
                Phishing Detection
              </span>
              <Badge variant="accent" size="sm" className="hidden sm:inline-flex">
                Benchmark
              </Badge>
            </div>
            <p className="text-[11px] text-slate-400 font-mono -mt-0.5">
              Injection-First Staged Inference
            </p>
          </div>
        </NavLink>

        {/* Persistent Navigation with Active-Route Highlighting */}
        <nav className="flex items-center gap-1 sm:gap-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === '/'}
                className={({ isActive }) =>
                  `flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs sm:text-sm font-medium transition-all border ${
                    isActive
                      ? 'bg-teal-500/10 text-teal-300 border-teal-500/30 shadow-sm shadow-teal-500/10 font-semibold'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60 border-transparent'
                  }`
                }
              >
                {({ isActive }) => (
                  <>
                    <Icon className={`h-4 w-4 ${isActive ? 'text-teal-400' : 'text-slate-400'}`} />
                    <span>{item.label}</span>
                    {isActive && (
                      <span className="h-1.5 w-1.5 rounded-full bg-teal-400 shadow-sm shadow-teal-400 animate-pulse hidden sm:inline-block" />
                    )}
                  </>
                )}
              </NavLink>
            );
          })}
        </nav>

        {/* Backend API Health Badge */}
        <div className="hidden lg:flex items-center">
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
      </div>
    </header>
  );
};
