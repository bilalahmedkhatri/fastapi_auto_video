'use client';

import React, { useState } from 'react';
import VideoGenerationStep from '../../components/VideoGenerationStep';
import VideoDisplayComponent from '../../components/VideoDisplayComponent';
import useVideoDisplay from '../../hooks/useVideoDisplay';
import { toast } from 'react-hot-toast';

/**
 * Complete Video Generation Workflow Integration
 * Shows how to connect video generation with video display
 */
const VideoWorkflowPage = () => {
  const [currentStep, setCurrentStep] = useState('generation'); // 'generation' | 'display'
  const [generationResult, setGenerationResult] = useState(null);
  
  const {
    videoData,
    videoUrl,
    isLoading,
    initializeFromGenerationResult,
    regenerateVideo,
    downloadVideo,
    shareVideo,
    saveToCollection
  } = useVideoDisplay();

  // Handle successful video generation
  const handleGenerationSuccess = (result) => {
    console.log('Video generation completed:', result);
    
    // Initialize video display with generation result
    initializeFromGenerationResult(result);
    setGenerationResult(result);
    
    // Switch to display step
    setCurrentStep('display');
    
    toast.success('Video generated successfully! 🎬');
  };

  // Handle generation error
  const handleGenerationError = (error) => {
    console.error('Video generation failed:', error);
    toast.error('Video generation failed. Please try again.');
  };

  // Handle back to builder
  const handleBackToBuilder = () => {
    setCurrentStep('generation');
    toast.success('Returning to video builder...');
  };

  // Handle edit video (reload builder with existing data)
  const handleEditVideo = () => {
    if (videoData) {
      // You could pre-populate the builder with existing data
      setCurrentStep('generation');
      toast.success('Loading video data for editing...');
    }
  };

  // Handle regenerate with same parameters
  const handleRegenerate = async () => {
    try {
      const result = await regenerateVideo();
      if (result) {
        toast.success('Video regeneration started! Check back in a few minutes.');
        // Optionally redirect to status page or show progress
      }
    } catch (error) {
      // Error already handled in hook
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {currentStep === 'generation' && (
        <div className="container mx-auto px-4 py-8">
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-8">
              <h1 className="text-4xl font-bold text-gray-800 dark:text-gray-200 mb-4">
                🎬 AI Video Generator
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                Create engaging videos with AI-powered content generation
              </p>
            </div>

            <VideoGenerationStep
              onGenerationSuccess={handleGenerationSuccess}
              onGenerationError={handleGenerationError}
              initialData={videoData} // Pre-populate if editing
            />
          </div>
        </div>
      )}

      {currentStep === 'display' && videoData && (
        <VideoDisplayComponent
          videoData={videoData}
          videoUrl={videoUrl}
          onEdit={handleEditVideo}
          onDownload={() => downloadVideo()}
          onShare={shareVideo}
          onRegenerateVideo={handleRegenerate}
          onBackToBuilder={handleBackToBuilder}
        />
      )}

      {/* Loading Overlay */}
      {isLoading && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-xl">
            <div className="flex items-center space-x-4">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
              <span className="text-gray-700 dark:text-gray-300">Processing video...</span>
            </div>
          </div>
        </div>
      )}

      {/* Navigation Breadcrumb */}
      <div className="fixed top-4 left-4 bg-white dark:bg-gray-800 rounded-lg shadow-lg p-3 z-40">
        <div className="flex items-center space-x-2 text-sm">
          <button
            onClick={() => setCurrentStep('generation')}
            className={`px-3 py-1 rounded ${
              currentStep === 'generation' 
                ? 'bg-blue-500 text-white' 
                : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
          >
            1. Generate
          </button>
          <span className="text-gray-400">→</span>
          <button
            onClick={() => videoData && setCurrentStep('display')}
            className={`px-3 py-1 rounded ${
              currentStep === 'display' 
                ? 'bg-blue-500 text-white' 
                : videoData 
                  ? 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700' 
                  : 'text-gray-400 cursor-not-allowed'
            }`}
            disabled={!videoData}
          >
            2. Display
          </button>
        </div>
      </div>

      {/* Quick Actions Menu (when video is available) */}
      {videoData && (
        <div className="fixed bottom-4 right-4 bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4 z-40">
          <div className="flex flex-col space-y-2">
            <button
              onClick={downloadVideo}
              className="flex items-center space-x-2 text-sm text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900 px-3 py-2 rounded"
            >
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                <path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/>
              </svg>
              <span>Quick Download</span>
            </button>
            
            <button
              onClick={shareVideo}
              className="flex items-center space-x-2 text-sm text-green-600 hover:bg-green-50 dark:hover:bg-green-900 px-3 py-2 rounded"
            >
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                <path d="M18 16.08c-.76 0-1.44.3-1.96.77L8.91 12.7c.05-.23.09-.46.09-.7s-.04-.47-.09-.7l7.05-4.11c.54.5 1.25.81 2.04.81 1.66 0 3-1.34 3-3s-1.34-3-3-3-3 1.34-3 3c0 .24.04.47.09.7L8.04 9.81C7.5 9.31 6.79 9 6 9c-1.66 0-3 1.34-3 3s1.34 3 3 3c.79 0 1.50-.31 2.04-.81l7.12 4.16c-.05.21-.08.43-.08.65 0 1.61 1.31 2.92 2.92 2.92 1.61 0 2.92-1.31 2.92-2.92s-1.31-2.92-2.92-2.92z"/>
              </svg>
              <span>Quick Share</span>
            </button>
            
            <button
              onClick={saveToCollection}
              className="flex items-center space-x-2 text-sm text-purple-600 hover:bg-purple-50 dark:hover:bg-purple-900 px-3 py-2 rounded"
            >
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                <path d="M17 3H7c-1.1 0-1.99.9-1.99 2L5 21l7-3 7 3V5c0-1.1-.9-2-2-2z"/>
              </svg>
              <span>Save Video</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default VideoWorkflowPage;