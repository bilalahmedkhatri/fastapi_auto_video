import './globals.css';
import { Inter } from 'next/font/google';
import { ThemeProvider } from '@/components/ThemeProvider';
import { AuthProvider } from '@/contexts/AuthContext';
import { Toaster } from 'react-hot-toast';
import LayoutWrapper from '@/components/Layout/LayoutWrapper';

const inter = Inter({ subsets: ['latin'] });

export const metadata = {
  title: 'AI Video Generator - Create Amazing Videos with AI',
  description: 'Transform your ideas into professional videos with our AI-powered platform. Generate scripts, create videos, and manage your content all in one place.',
  keywords: 'AI video generator, script generator, video creation, content automation, video editing, AI content creation',
  author: 'AI Video Generator',
  robots: 'index, follow',
  openGraph: {
    title: 'AI Video Generator - Create Amazing Videos with AI',
    description: 'Transform your ideas into professional videos with our AI-powered platform',
    type: 'website',
    locale: 'en_US',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'AI Video Generator - Create Amazing Videos with AI',
    description: 'Transform your ideas into professional videos with our AI-powered platform',
  },
};

export const viewport = {
  width: 'device-width',
  initialScale: 1.0,
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="canonical" href="https://your-domain.com" />
        <meta name="theme-color" content="#1f2937" />
        <link rel="icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
        <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" />
        <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png" />
        <link rel="manifest" href="/site.webmanifest" />
      </head>
      <body className={inter.className}>
        <ThemeProvider>
          <AuthProvider>
            <LayoutWrapper>
              {children}
            </LayoutWrapper>
            <Toaster 
              position="top-right"
              toastOptions={{
                duration: 4000,
                style: {
                  background: 'var(--toast-bg)',
                  color: 'var(--toast-color)',
                  border: '1px solid var(--toast-border)',
                },
                success: {
                  duration: 3000,
                  iconTheme: {
                    primary: 'var(--success-color)',
                    secondary: 'white',
                  },
                },
                error: {
                  duration: 5000,
                  iconTheme: {
                    primary: 'var(--error-color)',
                    secondary: 'white',
                  },
                },
              }}
            />
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
