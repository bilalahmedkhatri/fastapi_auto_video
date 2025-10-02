'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import VideoProcessingScreen from '../../../components/VideoProcessingScreen';
import VideoDisplayComponent from '../../../components/VideoDisplayComponent';
import useVideoDisplay from '../../../hooks/useVideoDisplay';
import { toast } from 'react-hot-toast';

/**
 * Complete Video Processing to Display Workflow
 * Handles the transition from video generation to video display
 */
const VideoProcessPage = () => {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [currentView, setCurrentView] = useState('processing'); // 'processing' | 'display'
  const [videoData, setVideoData] = useState(null);
  
  // Get video ID from URL params
  const videoId = searchParams.get('id');
  
  // Video display hook for completed videos
  const {
    videoData: displayVideoData,
    videoUrl,
    fetchVideoDetails,
    downloadVideo,
    shareVideo,
    regenerateVideo
  } = useVideoDisplay();

  useEffect(() => {
    if (!videoId) {
      toast.error('No video ID provided');
      router.push('/video-builder');
      return;
    }

    // Check if video is already completed by trying to fetch details
    checkVideoStatus();
  }, [videoId]);

  const checkVideoStatus = async () => {
    try {
      // Try to fetch completed video details first
      await fetchVideoDetails(videoId);
      
      // If successful, video is completed
      setCurrentView('display');
    } catch (error) {
      // Video not ready yet, show processing screen
      console.log('Video not ready, showing processing screen');
      setCurrentView('processing');
    }
  };

  // Handle video generation completion
  const handleProcessingComplete = (result) => {
    console.log('Processing completed:', result);
    
    // Store the completion data
    setVideoData(result);
    
    // Fetch full video details for display
    setTimeout(async () => {
      try {
        await fetchVideoDetails(result.videoId || videoId);
        setCurrentView('display');
        toast.success('🎬 Video is ready to view!');
      } catch (error) {
        console.error('Error fetching video details after completion:', error);
        // Fallback: show basic display with available data
        setCurrentView('display');
      }
    }, 1000);
  };

  // Handle processing error
  const handleProcessingError = (error) => {
    console.error('Video processing failed:', error);
    toast.error(`Video generation failed: ${error.message}`);
  };

  // Handle cancel processing (return to builder)
  const handleCancelProcessing = () => {
    router.push('/video-builder');
  };

  // Handle back to builder from display
  const handleBackToBuilder = () => {
    router.push('/video-builder');
  };

  // Handle video download
  const handleDownload = () => {
    downloadVideo();
  };

  // Handle video sharing
  const handleShare = () => {
    shareVideo();
  };

  // Handle video regeneration
  const handleRegenerate = async () => {
    try {
      const result = await regenerateVideo(videoId);
      if (result?.new_video_id) {
        toast.success('Starting video regeneration...');
        router.push(`/video-process?id=${result.new_video_id}`);
      }
    } catch (error) {
      toast.error('Failed to start regeneration');
    }
  };

  // Handle edit video (return to builder with data)
  const handleEditVideo = () => {
    // Store current video data for editing
    router.push('/video-builder?mode=edit');
  };

  if (!videoId) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">⚠️</div>
          <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-200 mb-2">
            No Video ID Provided
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Please start video generation from the builder.
          </p>
          <button
            onClick={() => router.push('/video-builder')}
            className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg transition-all"
          >
            Go to Video Builder
          </button>
        </div>
      </div>
    );
  }

  return (
    <>
      {currentView === 'processing' && (
        <VideoProcessingScreen
          videoId={videoId}
          initialData={videoData}
          onComplete={handleProcessingComplete}
          onError={handleProcessingError}
          onCancel={handleCancelProcessing}
        />
      )}

      {currentView === 'display' && (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
          {displayVideoData || videoData ? (
            <VideoDisplayComponent
              videoData={displayVideoData?.frontend_data || videoData}
              videoUrl={videoUrl || videoData?.outputUrl || videoData?.video_url}
              onEdit={handleEditVideo}
              onDownload={handleDownload}
              onShare={handleShare}
              onRegenerateVideo={handleRegenerate}
              onBackToBuilder={handleBackToBuilder}
            />
          ) : (
            // Loading state for display
            <div className="flex items-center justify-center min-h-screen">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mb-4 mx-auto"></div>
                <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-2">
                  Loading Video Details...
                </h2>
                <p className="text-gray-600 dark:text-gray-400">
                  Preparing your video for viewing
                </p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Navigation Helper */}
      <div className="fixed bottom-4 left-4 bg-white dark:bg-gray-800 rounded-lg shadow-lg p-3 z-50">
        <div className="flex items-center space-x-2 text-sm">
          <div className={`w-2 h-2 rounded-full ${
            currentView === 'processing' ? 'bg-blue-500' : 'bg-gray-300'
          }`}></div>
          <span className="text-gray-600 dark:text-gray-400">Processing</span>
          <span className="text-gray-400">→</span>
          <div className={`w-2 h-2 rounded-full ${
            currentView === 'display' ? 'bg-green-500' : 'bg-gray-300'
          }`}></div>
          <span className="text-gray-600 dark:text-gray-400">Display</span>
        </div>
      </div>
    </>
  );
};

export default VideoProcessPage;