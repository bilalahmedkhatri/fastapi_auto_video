'use client';

import { useState, useEffect, useCallback } from 'react';
import { toast } from 'react-hot-toast';

/**
 * Hook to manage video display functionality and integration with video generation system
 */
export const useVideoDisplay = (videoId = null) => {
  const [videoData, setVideoData] = useState(null);
  const [videoUrl, setVideoUrl] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch video details from your API
  const fetchVideoDetails = useCallback(async (id) => {
    if (!id) return;

    setIsLoading(true);
    setError(null);

    try {
      // Use the new backend API endpoint
      const response = await fetch(`http://localhost:8000/api/videos/${id}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch video: ${response.status}`);
      }

      const data = await response.json();
      setVideoData(data.frontend_data || data);
      setVideoUrl(data.video_url);
    } catch (err) {
      console.error('Error fetching video details:', err);
      setError(err.message);
      toast.error('Failed to load video details');
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Initialize video data from generation result
  const initializeFromGenerationResult = useCallback((generationResult) => {
    if (generationResult) {
      setVideoData(generationResult.frontend_data || generationResult);
      setVideoUrl(generationResult.video_url || generationResult.url);
      
      // Store in localStorage for persistence
      localStorage.setItem('currentVideoData', JSON.stringify(generationResult));
    }
  }, []);

  // Load video data from localStorage if available
  const loadFromStorage = useCallback(() => {
    try {
      const stored = localStorage.getItem('currentVideoData');
      if (stored) {
        const data = JSON.parse(stored);
        setVideoData(data.frontend_data || data);
        setVideoUrl(data.video_url || data.url);
      }
    } catch (err) {
      console.error('Error loading from storage:', err);
    }
  }, []);

  // Regenerate video with same parameters
  const regenerateVideo = useCallback(async (videoId) => {
    if (!videoId) {
      toast.error('No video ID available for regeneration');
      return;
    }

    setIsLoading(true);
    
    try {
      toast.loading('Regenerating video...', { id: 'regenerate' });

      const response = await fetch(`http://localhost:8000/api/videos/${videoId}/regenerate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Regeneration failed: ${response.status}`);
      }

      const result = await response.json();
      toast.success('Video regeneration started!', { id: 'regenerate' });
      
      // Optionally poll for completion or redirect to status page
      return result;
    } catch (err) {
      console.error('Error regenerating video:', err);
      toast.error('Failed to regenerate video', { id: 'regenerate' });
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Download video file
  const downloadVideo = useCallback((filename) => {
    if (!videoUrl) {
      toast.error('No video URL available for download');
      return;
    }

    try {
      const link = document.createElement('a');
      link.href = videoUrl;
      link.download = filename || `${videoData?.script_data?.title || 'generated_video'}.mp4`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      toast.success('Download started!');
    } catch (err) {
      console.error('Error downloading video:', err);
      toast.error('Failed to download video');
    }
  }, [videoUrl, videoData]);

  // Share video
  const shareVideo = useCallback(async () => {
    if (!videoUrl) {
      toast.error('No video URL available for sharing');
      return;
    }

    const shareData = {
      title: videoData?.script_data?.title || 'Generated Video',
      text: videoData?.script_data?.content?.substring(0, 100) || 'Check out this generated video!',
      url: videoUrl,
    };

    try {
      if (navigator.share) {
        await navigator.share(shareData);
        toast.success('Video shared successfully!');
      } else {
        // Fallback to clipboard
        await navigator.clipboard.writeText(videoUrl);
        toast.success('Video URL copied to clipboard!');
      }
    } catch (err) {
      console.error('Error sharing video:', err);
      // Silent fallback to clipboard
      try {
        await navigator.clipboard.writeText(videoUrl);
        toast.success('Video URL copied to clipboard!');
      } catch (clipErr) {
        toast.error('Failed to share video');
      }
    }
  }, [videoUrl, videoData]);

  // Save video to user's collection (Note: Video is already saved when created)
  const saveToCollection = useCallback(async (userId) => {
    if (!videoData || !userId) {
      toast.error('No video data or user ID to save');
      return;
    }

    try {
      // For now, just show success since videos are automatically saved
      // In future, this could mark video as "favorite" or add to specific collection
      toast.success('Video is already in your collection!');
      
      // Optional: Could call an endpoint to mark as favorite
      // const response = await fetch(`http://localhost:8000/api/videos/${videoId}/favorite`, {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ user_id: userId })
      // });
    } catch (err) {
      console.error('Error saving video:', err);
      toast.error('Failed to save video');
    }
  }, [videoData]);

  // Initialize on mount
  useEffect(() => {
    if (videoId) {
      fetchVideoDetails(videoId);
    } else {
      loadFromStorage();
    }
  }, [videoId, fetchVideoDetails, loadFromStorage]);

  return {
    // State
    videoData,
    videoUrl,
    isLoading,
    error,
    
    // Actions
    fetchVideoDetails,
    initializeFromGenerationResult,
    regenerateVideo,
    downloadVideo,
    shareVideo,
    saveToCollection,
    
    // Utilities
    setVideoData,
    setVideoUrl,
  };
};

export default useVideoDisplay;