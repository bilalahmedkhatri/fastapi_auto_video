'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import useVideoStatusPolling from '../hooks/useVideoStatusPolling';
import { toast } from 'react-hot-toast';

const VideoProcessingScreen = ({ 
  videoId, 
  initialData = {},
  onComplete,
  onError,
  onCancel
}) => {
  const router = useRouter();
  const [showAdvancedView, setShowAdvancedView] = useState(false);
  const [canContinueInBackground, setCanContinueInBackground] = useState(false);
  
  const {
    status,
    isPolling,
    isCompleted,
    isFailed,
    startPolling,
    stopPolling,
    resetStatus,
    formatTime,
    progressPercentage,
    currentStage,
    stageDisplayName,
    statusMessage,
    timeElapsed,
    timeRemaining
  } = useVideoStatusPolling();

  // Stage-specific configurations
  const stageConfig = {
    'initializing': {
      icon: '🚀',
      title: 'Initializing',
      description: 'Setting up your video generation environment',
      color: 'blue'
    },
    'script_generation': {
      icon: '📝',
      title: 'Script Generation', 
      description: 'Creating AI-powered script content',
      color: 'green'
    },
    'voiceover_generation': {
      icon: '🎵',
      title: 'Voiceover Generation',
      description: 'Generating natural AI voiceover',
      color: 'purple'
    },
    'social_media_generation': {
      icon: '📱',
      title: 'Social Media Optimization',
      description: 'Creating platform-specific content and hashtags',
      color: 'pink'
    },
    'media_selection': {
      icon: '🔍',
      title: 'Media Selection',
      description: 'Finding and downloading relevant media content',
      color: 'yellow'
    },
    'video_assembly': {
      icon: '🎞️',
      title: 'Video Assembly',
      description: 'Combining all elements into your video',
      color: 'indigo'
    },
    'rendering': {
      icon: '⚡',
      title: 'Final Rendering',
      description: 'Encoding and optimizing your video',
      color: 'orange'
    },
    'completed': {
      icon: '🎉',
      title: 'Completed',
      description: 'Your video is ready!',
      color: 'green'
    },
    'failed': {
      icon: '❌',
      title: 'Failed',
      description: 'Something went wrong',
      color: 'red'
    }
  };

  // Initialize polling when component mounts
  useEffect(() => {
    if (videoId && !isPolling) {
      startPolling(videoId, null, {
        onComplete: handleComplete,
        onError: handleError
      });
    }

    return () => {
      if (isPolling) {
        stopPolling();
      }
    };
  }, [videoId]);

  // Handle completion
  const handleComplete = (result) => {
    console.log('Video generation completed:', result);
    
    // Store result in localStorage for video display
    localStorage.setItem('completedVideoData', JSON.stringify({
      videoId: result.videoId,
      outputUrl: result.outputUrl,
      taskId: result.taskId,
      completedAt: new Date().toISOString(),
      ...initialData
    }));

    // Show completion message briefly, then redirect
    toast.success('🎬 Video ready! Redirecting to player...', { duration: 2000 });
    
    setTimeout(() => {
      if (onComplete) {
        onComplete(result);
      } else {
        // Default redirect to video display
        router.push(`/video-display?id=${result.videoId}`);
      }
    }, 2000);
  };

  // Handle error
  const handleError = (error) => {
    console.error('Video generation failed:', error);
    
    if (onError) {
      onError(error);
    } else {
      // Show error with retry option
      toast.error(
        (t) => (
          <div>
            <div className="font-semibold">Video generation failed</div>
            <div className="text-sm">{error.message}</div>
            <div className="mt-2 flex gap-2">
              <button 
                onClick={() => {
                  toast.dismiss(t.id);
                  resetStatus();
                  router.back();
                }}
                className="px-3 py-1 bg-gray-500 text-white rounded text-sm"
              >
                Back to Builder
              </button>
              <button
                onClick={() => {
                  toast.dismiss(t.id);
                  resetStatus();
                  startPolling(videoId, null, { onComplete: handleComplete, onError: handleError });
                }}
                className="px-3 py-1 bg-blue-500 text-white rounded text-sm"
              >
                Try Again
              </button>
            </div>
          </div>
        ),
        { duration: 0 } // Keep open until dismissed
      );
    }
  };

  // Handle cancel/continue in background
  const handleContinueInBackground = () => {
    setCanContinueInBackground(true);
    toast.success('Video generation continues in background. We\'ll notify you when ready!');
    
    // Store the video ID for later checking
    const backgroundJobs = JSON.parse(localStorage.getItem('backgroundVideoJobs') || '[]');
    backgroundJobs.push({
      videoId: videoId,
      startedAt: new Date().toISOString(),
      initialData: initialData
    });
    localStorage.setItem('backgroundVideoJobs', JSON.stringify(backgroundJobs));
    
    if (onCancel) {
      onCancel();
    } else {
      router.back();
    }
  };

  // Get current stage configuration
  const currentStageConfig = stageConfig[currentStage] || stageConfig['initializing'];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center p-4">
      <div className="max-w-2xl w-full">
        {/* Main Processing Card */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="text-6xl mb-4 animate-bounce">
              {currentStageConfig.icon}
            </div>
            <h1 className="text-3xl font-bold text-gray-800 dark:text-gray-200 mb-2">
              {isCompleted ? '🎉 Video Ready!' : 'Creating Your Video'}
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              {isCompleted 
                ? 'Your video has been generated successfully!' 
                : 'Please wait while we generate your amazing video content'
              }
            </p>
          </div>

          {/* Progress Section */}
          <div className="mb-8">
            {/* Progress Bar */}
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-4 mb-4">
              <div 
                className={`h-4 rounded-full transition-all duration-1000 ease-out ${
                  isCompleted ? 'bg-green-500' : 
                  isFailed ? 'bg-red-500' : 
                  'bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500'
                }`}
                style={{ width: `${Math.min(progressPercentage, 100)}%` }}
              >
                <div className="h-full rounded-full bg-white bg-opacity-30 animate-pulse"></div>
              </div>
            </div>

            {/* Progress Stats */}
            <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400 mb-4">
              <span>{progressPercentage}% Complete</span>
              <span>
                {timeElapsed > 0 && `⏱️ ${formatTime(timeElapsed)}`}
                {timeRemaining && ` • ~${formatTime(timeRemaining)} remaining`}
              </span>
            </div>
          </div>

          {/* Current Stage */}
          <div className="bg-gray-50 dark:bg-gray-700 rounded-xl p-6 mb-6">
            <div className="flex items-center gap-4 mb-3">
              <div className="text-3xl">{currentStageConfig.icon}</div>
              <div>
                <h3 className="text-xl font-semibold text-gray-800 dark:text-gray-200">
                  {currentStageConfig.title}
                </h3>
                <p className="text-gray-600 dark:text-gray-400 text-sm">
                  {currentStageConfig.description}
                </p>
              </div>
              {isPolling && !isCompleted && !isFailed && (
                <div className="ml-auto">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                </div>
              )}
            </div>

            {/* Detailed Status */}
            <div className="bg-white dark:bg-gray-800 rounded-lg p-4">
              <p className="text-gray-700 dark:text-gray-300 font-medium mb-2">
                {statusMessage}
              </p>
              
              {/* Step Details */}
              {status.stepDetails?.message && (
                <p className="text-gray-600 dark:text-gray-400 text-sm">
                  {status.stepDetails.message}
                </p>
              )}

              {status.stepDetails?.current_action && (
                <p className="text-blue-600 dark:text-blue-400 text-sm font-medium mt-1">
                  → {status.stepDetails.current_action}
                </p>
              )}
            </div>
          </div>

          {/* Stage Progress Indicators */}
          <div className="mb-8">
            <div className="flex justify-between items-center">
              {Object.entries(stageConfig).slice(0, -2).map(([stageKey, config], index) => {
                const isActive = currentStage === stageKey;
                const isCompleted = status.currentStep > index;
                
                return (
                  <div key={stageKey} className="flex flex-col items-center flex-1">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-all ${
                      isCompleted ? 'bg-green-500 text-white' :
                      isActive ? 'bg-blue-500 text-white animate-pulse' :
                      'bg-gray-300 dark:bg-gray-600 text-gray-600 dark:text-gray-400'
                    }`}>
                      {isCompleted ? '✓' : index + 1}
                    </div>
                    <div className={`text-xs mt-1 text-center transition-all ${
                      isActive ? 'text-blue-600 dark:text-blue-400 font-semibold' :
                      isCompleted ? 'text-green-600 dark:text-green-400' :
                      'text-gray-500 dark:text-gray-500'
                    }`}>
                      {config.title}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Advanced Details Toggle */}
          <div className="mb-6">
            <button
              onClick={() => setShowAdvancedView(!showAdvancedView)}
              className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 text-sm font-medium transition-colors"
            >
              {showAdvancedView ? '▼ Hide Details' : '▶ Show Advanced Details'}
            </button>

            {showAdvancedView && (
              <div className="mt-4 bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium text-gray-700 dark:text-gray-300">Video ID:</span>
                    <p className="text-gray-600 dark:text-gray-400 font-mono text-xs">{status.videoId}</p>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700 dark:text-gray-300">Task ID:</span>
                    <p className="text-gray-600 dark:text-gray-400 font-mono text-xs">{status.taskId || 'Pending'}</p>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700 dark:text-gray-300">Current Step:</span>
                    <p className="text-gray-600 dark:text-gray-400">{status.currentStep} / {status.totalSteps}</p>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700 dark:text-gray-300">Last Updated:</span>
                    <p className="text-gray-600 dark:text-gray-400 text-xs">
                      {status.lastUpdated ? new Date(status.lastUpdated).toLocaleTimeString() : 'Never'}
                    </p>
                  </div>
                </div>

                {/* Step Details */}
                {status.stepDetails && Object.keys(status.stepDetails).length > 0 && (
                  <div className="mt-4">
                    <span className="font-medium text-gray-700 dark:text-gray-300 text-sm">Step Details:</span>
                    <pre className="bg-gray-800 text-green-400 text-xs p-2 rounded mt-1 overflow-auto">
                      {JSON.stringify(status.stepDetails, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex justify-center gap-4">
            {!isCompleted && !isFailed && isPolling && (
              <button
                onClick={handleContinueInBackground}
                className="bg-gray-500 hover:bg-gray-600 text-white px-6 py-3 rounded-lg transition-all"
              >
                📱 Continue in Background
              </button>
            )}

            {isFailed && (
              <>
                <button
                  onClick={() => {
                    resetStatus();
                    router.back();
                  }}
                  className="bg-gray-500 hover:bg-gray-600 text-white px-6 py-3 rounded-lg transition-all"
                >
                  ← Back to Builder
                </button>
                <button
                  onClick={() => {
                    resetStatus();
                    startPolling(videoId, null, { 
                      onComplete: handleComplete, 
                      onError: handleError 
                    });
                  }}
                  className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg transition-all"
                >
                  🔄 Try Again
                </button>
              </>
            )}

            {isCompleted && (
              <button
                onClick={() => router.push(`/video-display?id=${status.videoId}`)}
                className="bg-green-500 hover:bg-green-600 text-white px-6 py-3 rounded-lg transition-all animate-pulse"
              >
                🎬 View Your Video
              </button>
            )}
          </div>

          {/* Estimated Completion Time */}
          {!isCompleted && !isFailed && timeRemaining && (
            <div className="text-center mt-6 text-sm text-gray-600 dark:text-gray-400">
              <div className="bg-blue-50 dark:bg-blue-900 rounded-lg p-3">
                ⏰ Estimated completion: {formatTime(timeRemaining)}
                <div className="text-xs mt-1">
                  Processing times may vary based on video complexity and current server load
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Quick Tips */}
        <div className="mt-6 bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-4">
            💡 While you wait...
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div className="flex items-start gap-3">
              <div className="text-blue-500">📱</div>
              <div>
                <div className="font-medium text-gray-800 dark:text-gray-200">Continue in Background</div>
                <div className="text-gray-600 dark:text-gray-400">Your video will keep generating even if you navigate away</div>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="text-green-500">🔔</div>
              <div>
                <div className="font-medium text-gray-800 dark:text-gray-200">Get Notified</div>
                <div className="text-gray-600 dark:text-gray-400">We'll notify you when your video is ready to view</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VideoProcessingScreen;