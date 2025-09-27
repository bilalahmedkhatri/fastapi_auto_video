'use client';

import { usePathname } from 'next/navigation';

// Pages that should use full-width layout without any headers
const fullWidthPages = ['/', '/multi-script-generator'];

export default function LayoutWrapper({ children }) {
  const pathname = usePathname();
  const isFullWidth = fullWidthPages.includes(pathname);

  if (isFullWidth) {
    // Full-width layout for special pages
    return (
      <div className="min-h-screen bg-gray-900">
        {children}
      </div>
    );
  }

  // Standard layout without any header/sidebar components
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <main className="w-full transition-colors duration-200">
        {children}
      </main>
    </div>
  );
}
