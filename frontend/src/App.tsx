import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/Layout';
import { LandingPage } from './pages/LandingPage';
import { LiveTestPage } from './pages/LiveTestPage';
import { DashboardPage } from './pages/DashboardPage';
import { InjectionLabPage } from './pages/InjectionLabPage';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<LandingPage />} />
          <Route path="test" element={<LiveTestPage />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="injection-lab" element={<InjectionLabPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

export default App;
