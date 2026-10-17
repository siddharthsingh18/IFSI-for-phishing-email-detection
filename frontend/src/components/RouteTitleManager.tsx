import React, { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

const ROUTE_TITLES: Record<string, string> = {
  '/': 'Overview · PhishBench',
  '/test': 'Live Test · PhishBench',
  '/live-test': 'Live Test · PhishBench',
  '/dashboard': 'Benchmark Dashboard · PhishBench',
  '/injection-lab': 'Injection Lab · PhishBench',
};

export const RouteTitleManager: React.FC = () => {
  const location = useLocation();

  useEffect(() => {
    const pathname = location.pathname.replace(/\/+$/, '') || '/';
    const title = ROUTE_TITLES[pathname] || '404 Not Found · PhishBench';
    document.title = title;
  }, [location.pathname]);

  return null;
};
