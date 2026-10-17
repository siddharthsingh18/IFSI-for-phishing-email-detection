import React from 'react';
import { Link } from 'react-router-dom';
import { Home, Terminal, BarChart3, FlaskConical, AlertTriangle, ArrowRight } from 'lucide-react';
import { Card } from '../components/Card';
import { Badge } from '../components/Badge';

export const NotFoundPage: React.FC = () => {
  const quickLinks = [
    {
      to: '/',
      title: 'Benchmark Overview',
      desc: 'Dataset metrics, empirical results, and architecture pipelines.',
      icon: Home,
    },
    {
      to: '/test',
      title: 'Live Inference Studio',
      desc: 'Interactive email composer with live multi-model detection.',
      icon: Terminal,
    },
    {
      to: '/dashboard',
      title: 'Benchmark Dashboard',
      desc: 'Comprehensive performance matrices, McNemar tests, and mistake review.',
      icon: BarChart3,
    },
    {
      to: '/injection-lab',
      title: 'Injection Lab',
      desc: 'Adversarial prompt injection taxonomy, payloads, and synthesis workbench.',
      icon: FlaskConical,
    },
  ];

  return (
    <div className="min-h-[75vh] flex flex-col items-center justify-center px-4 py-12">
      <div className="max-w-2xl w-full text-center space-y-6">
        {/* Glowing 404 Badge */}
        <div className="inline-flex items-center justify-center">
          <Badge variant="injection" size="md" className="gap-2 px-3.5 py-1 text-sm font-mono">
            <AlertTriangle className="h-4 w-4" />
            HTTP 404 · ROUTE NOT FOUND
          </Badge>
        </div>

        {/* Hero 404 Display */}
        <div className="space-y-2">
          <h1 className="text-7xl sm:text-8xl font-black tracking-tight font-display bg-clip-text text-transparent bg-gradient-to-r from-teal-400 via-cyan-400 to-emerald-400">
            404
          </h1>
          <h2 className="text-2xl sm:text-3xl font-bold text-slate-100 font-display">
            Page Not Found
          </h2>
          <p className="text-sm sm:text-base text-slate-400 max-w-lg mx-auto leading-relaxed">
            The page or benchmark resource you navigated to does not exist. Use the shortcuts below to return to the active evaluation environment.
          </p>
        </div>

        {/* Primary CTA */}
        <div className="pt-2 flex flex-wrap items-center justify-center gap-3">
          <Link
            to="/"
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-teal-500 hover:bg-teal-400 text-slate-950 font-semibold text-sm transition-all duration-150 hover:scale-[1.02] active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 elevation-card hover:elevation-hover shadow-lg shadow-teal-500/20"
          >
            <Home className="h-4 w-4" />
            <span>Return to Overview</span>
          </Link>
          <Link
            to="/test"
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl border border-slate-700 hover:border-slate-600 bg-slate-900/60 hover:bg-slate-800/80 text-slate-200 font-semibold text-sm transition-all duration-150 hover:scale-[1.02] active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950"
          >
            <Terminal className="h-4 w-4 text-cyan-400" />
            <span>Open Live Studio</span>
          </Link>
        </div>

        {/* Quick Link Cards */}
        <div className="pt-8 text-left">
          <div className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3 px-1">
            Available Benchmark Sections
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {quickLinks.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.to}
                  to={item.to}
                  className="group block rounded-2xl transition-all duration-150 hover:scale-[1.01] hover:brightness-105 active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950"
                >
                  <Card variant="interactive" padding="sm" className="h-full">
                    <div className="flex items-start gap-3">
                      <div className="p-2 rounded-lg bg-teal-500/10 text-teal-400 group-hover:bg-teal-500/20 group-hover:text-teal-300 transition-colors flex-shrink-0">
                        <Icon className="h-4 w-4" />
                      </div>
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center justify-between text-sm font-semibold text-slate-200 group-hover:text-teal-300 transition-colors">
                          <span>{item.title}</span>
                          <ArrowRight className="h-3.5 w-3.5 text-slate-500 group-hover:text-teal-400 group-hover:translate-x-0.5 transition-all" />
                        </div>
                        <p className="text-xs text-slate-400 mt-0.5 line-clamp-2">
                          {item.desc}
                        </p>
                      </div>
                    </div>
                  </Card>
                </Link>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};
