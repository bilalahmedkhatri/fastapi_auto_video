'use client';

import { createContext, useContext, useEffect, useState } from 'react';

// Theme context to be used throughout the app
const ThemeContext = createContext({
  theme: 'light',
  setTheme: () => {},
});

export function ThemeProvider({ children }) {
  // Initialize theme from localStorage or default to 'light'
  const [theme, setTheme] = useState('light');
  const [mounted, setMounted] = useState(false);

  // Only execute on client-side to avoid SSR hydration issues
  useEffect(() => {
    setMounted(true);
    
    // Get theme from localStorage or user preferences
    const storedTheme = localStorage.getItem('theme');
    
    if (storedTheme) {
      setTheme(storedTheme);
    } else {
      // Check system preference
      if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        setTheme('dark');
      }
    }
  }, []);

  // Apply theme to document
  useEffect(() => {
    if (!mounted) return;
    
    // Remove all theme classes first
    document.documentElement.classList.remove(
      'theme-light', 
      'theme-dark', 
      'theme-advanced-dark', 
      'theme-modern-dark',
      'dark'
    );
    
    // Log current theme for debugging
    console.log('Current theme:', theme);
    
    // Apply the selected theme
    switch (theme) {
      case 'dark':
        document.documentElement.classList.add('dark', 'theme-dark');
        localStorage.setItem('theme', 'dark');
        break;
      case 'advanced-dark':
        document.documentElement.classList.add('dark', 'theme-advanced-dark');
        localStorage.setItem('theme', 'advanced-dark');
        break;
      case 'modern-dark':
        document.documentElement.classList.add('dark', 'theme-modern-dark');
        localStorage.setItem('theme', 'modern-dark');
        break;
      case 'system':
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
          document.documentElement.classList.add('dark', 'theme-dark');
        } else {
          document.documentElement.classList.add('theme-light');
        }
        localStorage.setItem('theme', 'system');
        break;
      default:
        document.documentElement.classList.add('theme-light');
        localStorage.setItem('theme', 'light');
    }
  }, [theme, mounted]);

  // Watch for system preference changes when in system mode
  useEffect(() => {
    if (!mounted || theme !== 'system') return;
    
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    const handleChange = (e) => {
      if (e.matches) {
        document.documentElement.classList.add('dark', 'theme-dark');
        document.documentElement.classList.remove('theme-light');
      } else {
        document.documentElement.classList.remove('dark', 'theme-dark');
        document.documentElement.classList.add('theme-light');
      }
    };
    
    mediaQuery.addEventListener('change', handleChange);
    
    return () => {
      mediaQuery.removeEventListener('change', handleChange);
    };
  }, [theme, mounted]);

  // Sync theme when profile is updated
  const updateTheme = (newTheme) => {
    setTheme(newTheme);
  };

  return (
    <ThemeContext.Provider value={{ theme, setTheme: updateTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

// Custom hook to use theme throughout the app
export function useTheme() {
  return useContext(ThemeContext);
}
