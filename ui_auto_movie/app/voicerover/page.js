"use client";

import React, { useState, useEffect } from 'react';
import VoiceSelectionStep from './components/VoiceSelectionStep';
import ThemeToggle from './components/ThemeToggle';
import { ThemeProvider } from './components/ThemeProvider';
import { Toaster } from 'react-hot-toast';
import { useRouter } from 'next/navigation';

const VoiceSelectionDemo = () => {
  const [voiceoverData, setVoiceoverData] = useState(null);
  const [scriptData, setScriptData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  // Load script data from localStorage
  useEffect(() => {
    try {
      const savedScriptData = localStorage.getItem('selectedScriptData');
      if (savedScriptData) {
        const parsedData = JSON.parse(savedScriptData);
        setScriptData(parsedData);
      } else {
        // If no script data found, redirect back to video-builder
        router.push('/video-builder');
        return;
      }
    } catch (error) {
      console.error('Error loading script data:', error);
      // Fallback to sample data if there's an error
      setScriptData({
        id: "demo-script-123",
        title: "AI Revolution 2025: What's Next?",
        description: "Explore the cutting-edge developments in artificial intelligence that will shape our future",
        voiceover_script: "Hey tech enthusiasts! Welcome back to TechTalk. Today we're diving deep into the AI revolution of 2025. From quantum computing breakthroughs to neural interface technology, this year is bringing innovations that seemed impossible just a decade ago. Are you ready to discover what's coming next? Let's jump in and explore the future of artificial intelligence together!",
        category: "Technology",
        language: "English",
        script_type: "medium",
        tags: ["AI", "Technology", "Future", "Innovation", "2025"],
        word_count: 67
      });
    } finally {
      setIsLoading(false);
    }
  }, [router]);

  const handleNext = (data) => {
    setVoiceoverData(data);
    console.log('Voiceover data:', data);
    // Clear the localStorage data after successful generation
    localStorage.removeItem('selectedScriptData');
    // You can add navigation to next step here or show success message
    alert('Voice selection completed! Check console for data.');
  };

  const handleBack = () => {
    // Clear localStorage and go back to video-builder
    localStorage.removeItem('selectedScriptData');
    router.push('/video-builder');
  };

  return (
    <ThemeProvider>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
        {/* Header with theme toggle */}
        <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4">
          <div className="max-w-6xl mx-auto flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                Generate Voiceover
              </h1>
              <p className="text-gray-600 dark:text-gray-400 mt-1">
                {scriptData ? `Creating voiceover for: ${scriptData.title}` : 'Select voice and generate audio for your script'}
              </p>
            </div>
            <ThemeToggle />
          </div>
        </div>

        {/* Main content */}
        <div className="py-8">
          {isLoading ? (
            <div className="flex justify-center items-center min-h-64">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
                <p className="text-gray-600 dark:text-gray-400">Loading script data...</p>
              </div>
            </div>
          ) : scriptData ? (
            <VoiceSelectionStep
              scriptData={scriptData}
              onNext={handleNext}
              onBack={handleBack}
              userId="demo_user_123"
            />
          ) : (
            <div className="text-center py-12">
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                No script data found. Please select a script first.
              </p>
              <button
                onClick={() => router.push('/video-builder')}
                className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-all"
              >
                Go to Script Generator
              </button>
            </div>
          )}
        </div>

        {/* Toast notifications */}
        <Toaster 
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: 'var(--card)',
              color: 'var(--text)',
              border: '1px solid var(--border)'
            },
            success: {
              style: {
                background: '#10B981',
                color: '#FFFFFF',
              },
            },
            error: {
              style: {
                background: '#EF4444',
                color: '#FFFFFF',
              },
            },
          }}
        />

        {/* Debug info */}
        {voiceoverData && (
          <div className="fixed bottom-4 right-4 max-w-sm">
            <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 shadow-lg">
              <h4 className="font-semibold text-gray-900 dark:text-gray-100 mb-2">
                Generated Data:
              </h4>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                <p>Voice: {voiceoverData.voice?.name}</p>
                <p>Speed: {voiceoverData.audio_settings?.speed?.[0]}x</p>
                <p>Duration: {voiceoverData.generated_audio?.duration}s</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </ThemeProvider>
  );
};

export default VoiceSelectionDemo;
