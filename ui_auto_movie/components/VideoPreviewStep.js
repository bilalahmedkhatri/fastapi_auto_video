'use client';

import React, { useState, useRef, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import { getVideoUrl } from '@/lib/videoUtils';

const VideoPreviewStep = ({ 
  generatedVideo, 
  onRegenerate, 
  onDownload, 
  onNewVideo, 
  onBack 
}) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);
  const videoRef = useRef(null);

  // Format time display
  const formatTime = (timeInSeconds) => {
    const minutes = Math.floor(timeInSeconds / 60);
    const seconds = Math.floor(timeInSeconds % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  // Handle video play/pause
  const togglePlayPause = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  // Handle seek
  const handleSeek = (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const percent = (e.clientX - rect.left) / rect.width;
    const newTime = percent * duration;
    
    if (videoRef.current) {
      videoRef.current.currentTime = newTime;
      setCurrentTime(newTime);
    }
  };

  // Handle volume change
  const handleVolumeChange = (e) => {
    const newVolume = parseFloat(e.target.value);
    setVolume(newVolume);
    if (videoRef.current) {
      videoRef.current.volume = newVolume;
    }
    setIsMuted(newVolume === 0);
  };

  // Toggle mute
  const toggleMute = () => {
    if (videoRef.current) {
      if (isMuted) {
        videoRef.current.volume = volume;
        setIsMuted(false);
      } else {
        videoRef.current.volume = 0;
        setIsMuted(true);
      }
    }
  };

  // Handle video events
  const handleLoadedMetadata = () => {
    if (videoRef.current) {
      setDuration(videoRef.current.duration);
    }
  };

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      setCurrentTime(videoRef.current.currentTime);
    }
  };

  const handleEnded = () => {
    setIsPlaying(false);
    setCurrentTime(0);
  };

  // Download video
  const handleDownload = async () => {
    try {
      if (generatedVideo?.url) {
        // Create a temporary link to trigger download
        const link = document.createElement('a');
        link.href = generatedVideo.url;
        link.download = `generated-video-${Date.now()}.mp4`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        toast.success('Download started!');
        
        if (onDownload) {
          onDownload(generatedVideo);
        }
      }
    } catch (error) {
      console.error('Error downloading video:', error);
      toast.error('Failed to download video');
    }
  };

  // Share video (copy link to clipboard)
  const handleShare = async () => {
    try {
      if (generatedVideo?.url) {
        await navigator.clipboard.writeText(generatedVideo.url);
        toast.success('Video link copied to clipboard!');
      }
    } catch (error) {
      console.error('Error copying to clipboard:', error);
      toast.error('Failed to copy link');
    }
  };

  useEffect(() => {
    const video = videoRef.current;
    if (video) {
      video.addEventListener('loadedmetadata', handleLoadedMetadata);
      video.addEventListener('timeupdate', handleTimeUpdate);
      video.addEventListener('ended', handleEnded);

      return () => {
        video.removeEventListener('loadedmetadata', handleLoadedMetadata);
        video.removeEventListener('timeupdate', handleTimeUpdate);
        video.removeEventListener('ended', handleEnded);
      };
    }
  }, []);

  if (!generatedVideo) {
    return (
      <div className="max-w-4xl mx-auto p-6 text-center">
        <div className="text-6xl mb-4">❌</div>
        <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-200 mb-4">
          No Video Available
        </h2>
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          There was an issue generating your video. Please try again.
        </p>
        <button
          onClick={onBack}
          className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 transition-all"
        >
          ← Go Back
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-800 dark:text-gray-200 mb-4">
          🎬 Your Video is Ready!
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          Preview your generated video and download it when you're satisfied.
        </p>
      </div>

      {/* Video Player Section */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden border border-gray-200 dark:border-gray-700 mb-6">
        
        {/* Video Container */}
        <div className="relative bg-black aspect-video">
                <video
                  ref={videoRef}
                  src={getVideoUrl(generatedVideo, generatedVideo?.id) || generatedVideo.url}
                  className="w-full h-full object-contain"
                  onClick={togglePlayPause}
                >
                  Your browser does not support the video tag.
                </video>          {/* Play/Pause Overlay */}
          {!isPlaying && (
            <div 
              className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-30 cursor-pointer"
              onClick={togglePlayPause}
            >
              <div className="bg-white bg-opacity-90 rounded-full p-4 hover:bg-opacity-100 transition-all">
                <svg className="w-12 h-12 text-gray-800" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
                </svg>
              </div>
            </div>
          )}
        </div>

        {/* Video Controls */}
        <div className="p-4 bg-gray-50 dark:bg-gray-700">
          
          {/* Progress Bar */}
          <div className="mb-4">
            <div 
              className="w-full bg-gray-300 dark:bg-gray-600 rounded-full h-2 cursor-pointer"
              onClick={handleSeek}
            >
              <div 
                className="bg-blue-500 h-2 rounded-full transition-all"
                style={{ width: `${duration ? (currentTime / duration) * 100 : 0}%` }}
              ></div>
            </div>
            <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400 mt-1">
              <span>{formatTime(currentTime)}</span>
              <span>{formatTime(duration)}</span>
            </div>
          </div>

          {/* Control Buttons */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              {/* Play/Pause Button */}
              <button
                onClick={togglePlayPause}
                className="bg-blue-500 text-white p-2 rounded-lg hover:bg-blue-600 transition-all"
              >
                {isPlaying ? (
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                ) : (
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
                  </svg>
                )}
              </button>

              {/* Volume Controls */}
              <div className="flex items-center gap-2">
                <button
                  onClick={toggleMute}
                  className="text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 transition-all"
                >
                  {isMuted || volume === 0 ? (
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M9.383 3.076A1 1 0 0110 4v12a1 1 0 01-1.617.816L4.269 13H2a1 1 0 01-1-1V8a1 1 0 011-1h2.269l4.114-3.816zM15.854 6.146a.5.5 0 010 .708L14.207 8.5l1.647 1.646a.5.5 0 01-.708.708L13.5 9.207l-1.646 1.647a.5.5 0 01-.708-.708L12.793 8.5l-1.647-1.646a.5.5 0 01.708-.708L13.5 7.793l1.646-1.647a.5.5 0 01.708 0z" clipRule="evenodd" />
                    </svg>
                  ) : (
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M9.383 3.076A1 1 0 0110 4v12a1 1 0 01-1.617.816L4.269 13H2a1 1 0 01-1-1V8a1 1 0 011-1h2.269l4.114-3.816a1 1 0 011.617.816zM12 5a1 1 0 011.414 0A7.025 7.025 0 0115.5 10a7.025 7.025 0 01-2.086 5A1 1 0 1112 13.586 5.025 5.025 0 0013.5 10c0-1.38-.559-2.63-1.464-3.536A1 1 0 0112 5z" clipRule="evenodd" />
                    </svg>
                  )}
                </button>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={isMuted ? 0 : volume}
                  onChange={handleVolumeChange}
                  className="w-20 h-2 bg-gray-300 dark:bg-gray-600 rounded-lg appearance-none cursor-pointer"
                />
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center gap-2">
              <button
                onClick={handleShare}
                className="bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600 transition-all"
              >
                📤 Share
              </button>
              <button
                onClick={handleDownload}
                className="bg-purple-500 text-white px-4 py-2 rounded-lg hover:bg-purple-600 transition-all"
              >
                💾 Download
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Video Information */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-bold text-gray-800 dark:text-gray-200 mb-2">📊 Video Stats</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Duration:</span>
              <span className="font-medium">{formatTime(duration)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Size:</span>
              <span className="font-medium">
                {generatedVideo.file_size ? `${(generatedVideo.file_size / 1024 / 1024).toFixed(1)} MB` : 'Unknown'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Quality:</span>
              <span className="font-medium">HD 1080p</span>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-bold text-gray-800 dark:text-gray-200 mb-2">🎬 Generation Info</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Task ID:</span>
              <span className="font-medium text-xs">{generatedVideo.task_id?.slice(0, 8)}...</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Status:</span>
              <span className="font-medium text-green-600">Completed</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Created:</span>
              <span className="font-medium">{new Date().toLocaleDateString()}</span>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-bold text-gray-800 dark:text-gray-200 mb-2">🛠️ Actions</h3>
          <div className="space-y-3">
            <button
              onClick={onRegenerate}
              className="w-full bg-orange-500 text-white py-2 px-4 rounded-lg hover:bg-orange-600 transition-all"
            >
              🔄 Regenerate Video
            </button>
            <button
              onClick={onNewVideo}
              className="w-full bg-blue-500 text-white py-2 px-4 rounded-lg hover:bg-blue-600 transition-all"
            >
              ✨ Create New Video
            </button>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex justify-center gap-4">
        <button
          onClick={onBack}
          className="bg-gray-500 text-white px-6 py-2 rounded-lg hover:bg-gray-600 transition-all"
        >
          ← Back to Generation
        </button>
        <button
          onClick={onNewVideo}
          className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-8 py-2 rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all"
        >
          🎬 Create Another Video
        </button>
      </div>
    </div>
  );
};

export default VideoPreviewStep;