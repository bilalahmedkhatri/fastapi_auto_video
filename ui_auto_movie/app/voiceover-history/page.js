"use client";

import React from 'react';
import VoiceoverHistory from '../voicerover/components/VoiceoverHistory';
import { Toaster } from 'react-hot-toast';

export default function VoiceoverHistoryPage() {
  // In a real app, you'd get this from authentication context
  const userId = "demo-user-123";

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <VoiceoverHistory userId={userId} />
      </div>
      <Toaster />
    </div>
  );
}
