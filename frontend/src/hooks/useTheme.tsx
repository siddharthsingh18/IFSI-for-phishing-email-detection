import React, { createContext, useContext, useEffect, useState, useMemo } from 'react';
import { themes } from '../styles/design-tokens';

export type ThemeMode = 'dark' | 'light';

export interface ChartThemeColors {
  grid: string;
  text: string;
  axis: string;
  tooltipBg: string;
  tooltipBorder: string;
  tooltipText: string;
  legendText: string;
}

export interface ThemeContextType {
  theme: ThemeMode;
  isDark: boolean;
  toggleTheme: () => void;
  setTheme: (theme: ThemeMode) => void;
  chartColors: ChartThemeColors;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

const STORAGE_KEY = 'ifsi_theme';

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [theme, setThemeState] = useState<ThemeMode>(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored === 'light' || stored === 'dark') {
        return stored;
      }
    } catch {
      // In case localStorage is unavailable in iframe or security sandbox
    }
    // Default to 'dark' mode (Dark Slate foundation)
    return 'dark';
  });

  const isDark = theme === 'dark';

  const setTheme = (newTheme: ThemeMode) => {
    setThemeState(newTheme);
    try {
      localStorage.setItem(STORAGE_KEY, newTheme);
    } catch (e) {
      console.warn('Failed to persist theme to localStorage:', e);
    }
  };

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  };

  useEffect(() => {
    const root = document.documentElement;
    if (theme === 'dark') {
      root.classList.remove('light');
      root.classList.add('dark');
      root.setAttribute('data-theme', 'dark');
      root.style.colorScheme = 'dark';
    } else {
      root.classList.remove('dark');
      root.classList.add('light');
      root.setAttribute('data-theme', 'light');
      root.style.colorScheme = 'light';
    }
  }, [theme]);

  const chartColors = useMemo(() => {
    return isDark ? themes.dark.chart : themes.light.chart;
  }, [isDark]);

  return (
    <ThemeContext.Provider value={{ theme, isDark, toggleTheme, setTheme, chartColors }}>
      {children}
    </ThemeContext.Provider>
  );
};

// eslint-disable-next-line react-refresh/only-export-components
export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};
