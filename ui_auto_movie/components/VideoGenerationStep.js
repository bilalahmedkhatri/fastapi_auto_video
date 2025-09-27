'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { toast } from 'react-hot-toast';
import VideoProcessingScreen from './VideoProcessingScreen';

const VideoGenerationStep = ({ 
  scriptData, 
  voiceoverData, 
  socialMediaContent, 
  selectedMedia,
  videoEffectsConfig,
  onComplete,
  onBack,
  onError
}) => {
  const router = useRouter();
  const [progress, setProgress] = useState(0);
  const [currentStatus, setCurrentStatus] = useState('Preparing video generation...');
  const [taskId, setTaskId] = useState(null);
  const [videoId, setVideoId] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [showProcessingScreen, setShowProcessingScreen] = useState(false);
  const [backgroundMode, setBackgroundMode] = useState(false);

  // Helper function to extract audio file path from voiceover data
  const getAudioFilePath = (voiceoverData) => {
    if (!voiceoverData) return null;
    
    // Try different possible audio path locations
    const audioPath = voiceoverData?.generated_audio?.audio_url || 
                      voiceoverData?.audio_url || 
                      voiceoverData?.file_path ||
                      voiceoverData?.generated_audio?.file_path;
    
    if (!audioPath) return null;
    
    // If it's a relative path starting with /, convert to full URL
    if (audioPath.startsWith('/') && !audioPath.startsWith('http')) {
      return `http://localhost:8000${audioPath}`;
    }
    
    return audioPath;
  };

  // Aggregate all frontend data for the backend
  const aggregateVideoData = () => {
    return {
      script_data: {
        title: scriptData?.title || 'Generated Video',
        content: scriptData?.content || 'Default video content generated from user selection',
        voiceover_script: scriptData?.voiceover_script || scriptData?.content || 'Default video content generated from user selection',
        category: scriptData?.category || 'General'
      },
      voiceover_data: {
        audio_file_path: getAudioFilePath(voiceoverData),
        transcript: voiceoverData?.generated_audio?.transcript || voiceoverData?.transcript || {},
        voice_model: voiceoverData?.voice?.name || voiceoverData?.voice_model || 'default',
        duration: voiceoverData?.generated_audio?.duration || voiceoverData?.duration || 0
      },
      social_media_data: {
        platform_descriptions: socialMediaContent?.platform_descriptions || [],
        hashtags: extractHashtagsFromContent(socialMediaContent),
        keywords: extractKeywordsFromContent(socialMediaContent),
        tags: generateTagsFromContent(socialMediaContent)
      },
      media_data: {
        selected_media: selectedMedia?.map(media => ({
          id: media.id,
          type: media.type,
          file_path: media.url || media.file_path,
          sequence_number: media.sequenceNumber || 0,
          source: media.source
        })) || []
      },
      video_effects_config: videoEffectsConfig || {},
      user_id: 'frontend_user', // This should come from auth context
      video_id: `frontend_${Date.now()}`
    };
  };

  // Helper functions to extract data from social media content
  const extractHashtagsFromContent = (socialContent) => {
    if (!socialContent?.platform_descriptions) return [];
    const hashtags = [];
    socialContent.platform_descriptions.forEach(platform => {
      if (platform.hashtags) {
        hashtags.push(...platform.hashtags);
      }
    });
    return [...new Set(hashtags)]; // Remove duplicates
  };

  const extractKeywordsFromContent = (socialContent) => {
    if (!socialContent?.platform_descriptions) return [];
    const keywords = [];
    socialContent.platform_descriptions.forEach(platform => {
      if (platform.seo_keywords) {
        keywords.push(...platform.seo_keywords);
      }
    });
    return [...new Set(keywords)]; // Remove duplicates
  };

  const generateTagsFromContent = (socialContent) => {
    const hashtags = extractHashtagsFromContent(socialContent);
    return hashtags.map(tag => tag.replace('#', ''));
  };

  // Start video generation
  const startVideoGeneration = async () => {
    try {
      setIsGenerating(true);
      setCurrentStatus('Starting video generation...');
      
      const videoData = aggregateVideoData();
      
      // Debug logging
      console.log('🔍 Debug - Raw voiceoverData:', voiceoverData);
      console.log('🔍 Debug - Processed voiceover_data:', videoData.voiceover_data);
      console.log('🔍 Debug - Audio file path:', videoData.voiceover_data.audio_file_path);
      
      // Debug API payload
      const apiPayload = {
        user_id: videoData.user_id,
        prompt: videoData.script_data.content,
        category: videoData.script_data.category,
        language: 'English',
        duration: 'medium',
        priority: 'normal',
        frontend_data: videoData,
        additional_settings: {
          use_frontend_data: true,
          video_effects: videoData.video_effects_config
        }
      };
      console.log('🔍 Debug - API Payload:', apiPayload);
      console.log('🔍 Debug - Prompt length:', apiPayload.prompt?.length);
      
      // Validate required data
      if (!videoData.voiceover_data.audio_file_path) {
        console.error('❌ Missing audio file path in voiceover data');
        throw new Error('Voiceover audio file is required. Please generate voiceover first.');
      }
      
      if (!videoData.media_data.selected_media.length) {
        throw new Error('At least one media file is required');
      }
      const FASTAPI_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

      // Call the existing video process API
      const response = await fetch(`${FASTAPI_BASE_URL}/api/video-process/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(apiPayload)
      });

      if (!response.ok) {
        let errorMessage = `HTTP error! status: ${response.status}`;
        try {
          const errorData = await response.json();
          console.error('❌ API Error Details:', errorData);
          if (errorData.detail) {
            errorMessage += ` - ${JSON.stringify(errorData.detail)}`;
          }
        } catch (e) {
          console.error('❌ Could not parse error response');
        }
        throw new Error(errorMessage);
      }

      const result = await response.json();
      
      // Handle both old and new response formats
      const processId = result.process_id || result.task_id || result.video_id;
      const returnedVideoId = result.video_id || result.id;
      
      if (processId) {
        setTaskId(processId);
        setVideoId(returnedVideoId || processId);
        
        // Store initial data for processing screen
        const initialData = {
          script_data: scriptData,
          voiceover_data: voiceoverData,
          social_media_data: socialMediaContent,
          selected_media: selectedMedia,
          video_effects_config: videoEffectsConfig,
          generation_started_at: new Date().toISOString()
        };
        
        if (backgroundMode) {
          // Store job for background monitoring
          const backgroundJobs = JSON.parse(localStorage.getItem('backgroundVideoJobs') || '[]');
          backgroundJobs.push({
            videoId: returnedVideoId || processId,
            taskId: processId,
            startedAt: new Date().toISOString(),
            initialData: initialData
          });
          localStorage.setItem('backgroundVideoJobs', JSON.stringify(backgroundJobs));
          
          toast.success('🚀 Video generation started in background! We\'ll notify you when it\'s ready.');
          
          // Return to main dashboard/previous screen
          if (onComplete) {
            onComplete({ background: true, videoId: returnedVideoId || processId });
          }
        } else {
          // Switch to processing screen
          setShowProcessingScreen(true);
          toast.success('🚀 Video generation started!');
        }
      } else {
        throw new Error('No process ID or video ID returned from server');
      }

    } catch (error) {
      console.error('Error starting video generation:', error);
      setIsGenerating(false);
      toast.error(`Failed to start video generation: ${error.message}`);
      setCurrentStatus(`Error: ${error.message}`);
      if (onError) onError(error);
    }
  };

  // Track progress with polling
  const startProgressTracking = (processId) => {
    const pollProgress = async () => {
      try {
        const response = await fetch(`/api/video-process/${processId}/status`);
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const status = await response.json();
        
        // Update progress
        const progressPercent = Math.round((status.current_step / status.total_steps) * 100);
        console.log('check progress', status.current_step, progressPercent)
        setProgress(progressPercent);
        setCurrentStatus(status.status || 'Processing...');

        // Check if completed
        if (status.stage === 'completed' || status.status?.includes('completed')) {
          setIsGenerating(false);
          toast.success('Video generation completed!');
          
          if (onComplete && status.output_url) {
            onComplete({
              url: status.output_url,
              task_id: processId,
              ...status
            });
          }
          return; // Stop polling
        }

        // Check if failed
        if (status.stage === 'failed' || status.error) {
          setIsGenerating(false);
          const errorMsg = status.error || 'Video generation failed';
          toast.error(errorMsg);
          setCurrentStatus(`Failed: ${errorMsg}`);
          if (onError) onError(new Error(errorMsg));
          return; // Stop polling
        }

        // Continue polling if still processing
        if (isGenerating) {
          setTimeout(pollProgress, 3000); // Poll every 3 seconds
        }

      } catch (error) {
        console.error('Error checking progress:', error);
        if (isGenerating) {
          setTimeout(pollProgress, 5000); // Retry after 5 seconds on error
        }
      }
    };

    // Start polling
    pollProgress();
  };

  // Handle video generation completion
  const handleVideoComplete = (result) => {
    console.log('Video generation completed:', result);
    setIsGenerating(false);
    
    // Store completion data
    localStorage.setItem('lastCompletedVideo', JSON.stringify({
      ...result,
      completedAt: new Date().toISOString(),
      originalData: {
        script_data: scriptData,
        voiceover_data: voiceoverData,
        social_media_data: socialMediaContent,
        selected_media: selectedMedia,
        video_effects_config: videoEffectsConfig
      }
    }));

    // Call parent completion handler if provided
    if (onComplete) {
      onComplete(result);
    } else {
      // Default redirect to video display
      toast.success('🎬 Redirecting to your video...', { duration: 1500 });
      setTimeout(() => {
        router.push(`/video-display?id=${result.videoId}`);
      }, 1500);
    }
  };

  // Handle video generation error
  const handleVideoError = (error) => {
    console.error('Video generation failed:', error);
    setIsGenerating(false);
    setShowProcessingScreen(false);
    
    if (onError) {
      onError(error);
    }
  };

  // Handle cancel processing screen
  const handleCancelProcessing = () => {
    setShowProcessingScreen(false);
    setIsGenerating(false);
    toast.info('Returned to video builder. Generation continues in background.');
  };

  // Track progress using specific status endpoint
  const startProgressTrackingWithEndpoint = (statusEndpoint) => {
    const pollProgress = async () => {
      try {
        const response = await fetch(statusEndpoint);
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const status = await response.json();
        
        // Update progress based on new task format
        const progressPercent = status.progress || 0;
        setProgress(progressPercent);
        setCurrentStatus(status.message || 'Processing...');

        console.log('📊 Task Status Update:', status);

        // Check if completed
        if (status.status === 'SUCCESS' && status.result) {
          setIsGenerating(false);
          setProgress(100);
          toast.success('Video generation completed!');
          
          if (onComplete && status.result) {
            onComplete({
              url: status.result.output_url || status.result.video_url,
              task_id: status.task_id,
              result: status.result
            });
          }
          return; // Stop polling
        }

        // Check if failed
        if (status.status === 'FAILURE') {
          setIsGenerating(false);
          const errorMsg = status.error || status.message || 'Video generation failed';
          toast.error(errorMsg);
          setCurrentStatus(`Failed: ${errorMsg}`);
          if (onError) onError(new Error(errorMsg));
          return; // Stop polling
        }

        // Continue polling if still processing
        if (isGenerating && (status.status === 'PENDING' || status.status === 'IN_PROGRESS')) {
          setTimeout(pollProgress, 3000); // Poll every 3 seconds
        }

      } catch (error) {
        console.error('Error checking task progress:', error);
        if (isGenerating) {
          setTimeout(pollProgress, 5000); // Retry after 5 seconds on error
        }
      }
    };

    // Start polling
    pollProgress();
  };

  // Auto-start generation when component mounts
  useEffect(() => {
    if (!isGenerating && !taskId) {
      startVideoGeneration();
    }
  }, []);

  // Show processing screen when video generation starts
  if (showProcessingScreen && videoId) {
    return (
      <VideoProcessingScreen
        videoId={videoId}
        initialData={{
          script_data: scriptData,
          voiceover_data: voiceoverData,
          social_media_data: socialMediaContent,
          selected_media: selectedMedia,
          video_effects_config: videoEffectsConfig
        }}
        onComplete={handleVideoComplete}
        onError={handleVideoError}
        onCancel={handleCancelProcessing}
      />
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-800 dark:text-gray-200 mb-4">
          🎬 Generating Your Video
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          Creating your video from selected content. This may take a few minutes...
        </p>
      </div>

      {/* Progress Section */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8 border border-gray-200 dark:border-gray-700">
        
        {/* Progress Bar */}
        <div className="mb-6">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Progress
            </span>
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              {progress}%
            </span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
            <div 
              className="bg-gradient-to-r from-blue-500 to-purple-600 h-3 rounded-full transition-all duration-1000 ease-out"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        </div>

        {/* Status Message */}
        <div className="text-center mb-6">
          <div className="flex items-center justify-center gap-3 mb-2">
            {isGenerating && (
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
            )}
            <p className="text-lg font-medium text-gray-800 dark:text-gray-200">
              {currentStatus}
            </p>
          </div>
        </div>

        {/* Generation Info */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div className="text-2xl mb-1">📝</div>
            <div className="font-medium text-gray-800 dark:text-gray-200">Script</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">
              {scriptData?.title || 'Ready'}
            </div>
          </div>
          
          <div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div className="text-2xl mb-1">🎵</div>
            <div className="font-medium text-gray-800 dark:text-gray-200">Audio</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">
              {getAudioFilePath(voiceoverData) ? 'Ready' : 'Missing'}
            </div>
          </div>
          
          <div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div className="text-2xl mb-1">📱</div>
            <div className="font-medium text-gray-800 dark:text-gray-200">Social Media</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">
              {socialMediaContent ? 'Ready' : 'Missing'}
            </div>
          </div>
          
          <div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div className="text-2xl mb-1">🎬</div>
            <div className="font-medium text-gray-800 dark:text-gray-200">Media</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">
              {selectedMedia?.length || 0} items
            </div>
          </div>
        </div>

        {/* Background Mode Toggle */}
        <div className="flex justify-center mb-4">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={backgroundMode}
              onChange={(e) => setBackgroundMode(e.target.checked)}
              disabled={isGenerating}
              className="rounded"
            />
            <span className="text-sm text-gray-600 dark:text-gray-400">
              Generate in background (get notified when ready)
            </span>
          </label>
        </div>

        {/* Control Buttons */}
        <div className="flex justify-center gap-4">
          <button
            onClick={onBack}
            disabled={isGenerating}
            className="bg-gray-500 text-white px-6 py-2 rounded-lg hover:bg-gray-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            ← Back to Effects
          </button>
          
          {!isGenerating && progress < 100 && (
            <button
              onClick={startVideoGeneration}
              className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 transition-all"
            >
              {backgroundMode ? '🚀 Start in Background' : '🔄 Start Generation'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default VideoGenerationStep;