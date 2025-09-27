'use client';

import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import VideoDisplayComponent from '@/components/VideoDisplayComponent';
import { toast } from 'react-hot-toast';
import { getVideoUrl, fetchVideoMetadata } from '@/lib/videoUtils';

const VideoDisplayPage = () => {
  const searchParams = useSearchParams();
  const videoId = searchParams.get('id');
  
  const [videoData, setVideoData] = useState(null);
  const [videoUrl, setVideoUrl] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Fetch actual video data from API
  useEffect(() => {
    const fetchVideo = async () => {
      if (!videoId) {
        // Fallback to mock data for demonstration
        const mockData = {
          id: "video_123456",
          script_data: {
            title: "The Future of Electric Vehicles",
            category: "Technology",
            content: "Electric vehicles are revolutionizing the automotive industry with sustainable transportation solutions.",
            duration: 45
          },
          voiceover_data: {
            voice_model: "Professional Male Voice",
            duration: 42.5,
            language: "en-US",
            speed: 1.0,
            pitch: 0.0
          },
          media_data: {
            selected_media: [
              {
                type: "video",
                source: "Pixabay",
                description: "Electric car charging station",
                duration: 8
              }
            ],
            total_duration: 42
          },
          social_media_data: {
            hashtags: ["#ElectricVehicles", "#Tesla", "#SustainableTransport"],
            keywords: ["electric vehicles", "tesla", "battery technology"],
            description: "Discover the revolutionary world of electric vehicles."
          },
          video_effects_config: {
            style: "Modern Tech",
            transitions: "Smooth Fade",
            text_style: "Clean Sans-serif",
            color_scheme: "Electric Blue"
          }
        };
        setVideoData(mockData);
        setVideoUrl("https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4");
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        console.log(`🔍 Fetching video data for ID: ${videoId}`);
        
        const data = await fetchVideoMetadata(videoId);
        console.log('📊 Received video data:', data);
        
        setVideoData(data);
        
        // Generate proper video URL
        const url = getVideoUrl(data, videoId);
        console.log('🎬 Generated video URL:', url);
        setVideoUrl(url);
        
      } catch (error) {
        console.error('❌ Error fetching video:', error);
        setError('Failed to load video. Please try again.');
        toast.error('Failed to load video');
      } finally {
        setLoading(false);
      }
    };

    fetchVideo();
  }, [videoId]);

  const handleEdit = () => {
    toast.success('Redirecting to video editor...');
    console.log('Edit video:', videoData?.id || videoId);
  };

  const handleDownload = () => {
    toast.success('Download started!');
  };

  const handleShare = () => {
    console.log('Share video:', videoData?.id || videoId);
  };

  const handleRegenerateVideo = () => {
    toast.info('Redirecting to regenerate video...');
    console.log('Regenerate video:', videoData?.id || videoId);
  };

  const handleBackToBuilder = () => {
    toast.info('Returning to video builder...');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-200 mb-2">
            Loading Video...
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Fetching your generated video
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">❌</div>
          <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-200 mb-4">
            Error Loading Video
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            {error}
          </p>
          <button 
            onClick={() => window.location.reload()}
            className="bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!videoData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">🎬</div>
          <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-200 mb-4">
            No Video Found
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            The requested video could not be found.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <VideoDisplayComponent
        videoData={videoData}
        videoUrl={videoUrl}
        onEdit={handleEdit}
        onDownload={handleDownload}
        onShare={handleShare}
        onRegenerateVideo={handleRegenerateVideo}
        onBackToBuilder={handleBackToBuilder}
      />
      
      {/* Debug Info */}
      {videoId && (
        <div className="fixed bottom-4 left-4 bg-black bg-opacity-75 text-white p-3 rounded text-xs max-w-sm">
          <div><strong>Video ID:</strong> {videoId}</div>
          <div><strong>Video URL:</strong> {videoUrl || 'Not set'}</div>
          {videoData?.status && <div><strong>Status:</strong> {videoData.status}</div>}
        </div>
      )}
    </div>
  );
};

export default VideoDisplayPage;