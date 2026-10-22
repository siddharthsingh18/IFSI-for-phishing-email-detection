import React, { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

const ROUTE_TITLES: Record<string, string> = {
  '/': 'Overview · IFSI Phishing Detection',
  '/test': 'Live Test · IFSI Phishing Detection',
  '/live-test': 'Live Test · IFSI Phishing Detection',
  '/dashboard': 'Benchmark Dashboard · IFSI Phishing Detection',
  '/injection-lab': 'Injection Lab · IFSI Phishing Detection',
};

export const RouteTitleManager: React.FC = () => {
  const location = useLocation();

  useEffect(() => {
    const pathname = location.pathname.replace(/\/+$/, '') || '/';
    const title = ROUTE_TITLES[pathname] || '404 Not Found · IFSI Phishing Detection';
    document.title = title;
  }, [location.pathname]);

  return null;
};
