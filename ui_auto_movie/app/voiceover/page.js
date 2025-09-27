"use client";

import React from 'react';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

// Redirect component to handle the correct voiceover route
const VoiceoverRedirect = () => {
  const router = useRouter();

  useEffect(() => {
    // Redirect to the correct voiceover route
    router.replace('/voicerover');
  }, [router]);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
        <p className="text-gray-600 dark:text-gray-400">Redirecting to voiceover page...</p>
      </div>
    </div>
  );
};

export default VoiceoverRedirect;