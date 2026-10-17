import React, { Suspense, lazy } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Layout } from './components/Layout';
import { LandingPage } from './pages/LandingPage';

const LiveTestPage = lazy(() => import('./pages/LiveTestPage').then(m => ({ default: m.LiveTestPage })));
const DashboardPage = lazy(() => import('./pages/DashboardPage').then(m => ({ default: m.DashboardPage })));
const InjectionLabPage = lazy(() => import('./pages/InjectionLabPage').then(m => ({ default: m.InjectionLabPage })));
const NotFoundPage = lazy(() => import('./pages/NotFoundPage').then(m => ({ default: m.NotFoundPage })));

import { NavigationProgressBar } from './components/NavigationProgressBar';
import { RouteTitleManager } from './components/RouteTitleManager';
import { ThemeProvider } from './hooks/useTheme';
import { AppInitialLoader } from './components/AppInitialLoader';

export const App: React.FC = () => {
  return (
    <ThemeProvider>
      <AppInitialLoader>
        <BrowserRouter>
          <NavigationProgressBar />
          <RouteTitleManager />
          <Suspense fallback={<div className="min-h-screen bg-slate-950" />}>
            <Routes>
              <Route path="/" element={<Layout />}>
                <Route index element={<LandingPage />} />
                <Route path="test" element={<LiveTestPage />} />
                <Route path="live-test" element={<LiveTestPage />} />
                <Route path="dashboard" element={<DashboardPage />} />
                <Route path="injection-lab" element={<InjectionLabPage />} />
                <Route path="*" element={<NotFoundPage />} />
              </Route>
            </Routes>
          </Suspense>
        </BrowserRouter>
      </AppInitialLoader>
    </ThemeProvider>
  );
};

export default App;
