'use client';

import React, { useState, useRef, useEffect } from 'react';
import { toast } from 'react-hot-toast';

const VideoDisplayComponent = ({ 
  videoData,
  videoUrl,
  onEdit,
  onDownload,
  onShare,
  onRegenerateVideo,
  onBackToBuilder
}) => {
  const videoRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [showParameters, setShowParameters] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Video control handlers
  const handlePlayPause = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      setCurrentTime(videoRef.current.currentTime);
    }
  };

  const handleLoadedMetadata = () => {
    if (videoRef.current) {
      setDuration(videoRef.current.duration);
    }
  };

  const handleSeek = (e) => {
    const seekTime = (e.target.value / 100) * duration;
    if (videoRef.current) {
      videoRef.current.currentTime = seekTime;
      setCurrentTime(seekTime);
    }
  };

  const handleVolumeChange = (e) => {
    const newVolume = e.target.value / 100;
    setVolume(newVolume);
    if (videoRef.current) {
      videoRef.current.volume = newVolume;
    }
  };

  const toggleFullscreen = () => {
    if (videoRef.current) {
      if (document.fullscreenElement) {
        document.exitFullscreen();
        setIsFullscreen(false);
      } else {
        videoRef.current.requestFullscreen();
        setIsFullscreen(true);
      }
    }
  };

  const formatTime = (timeInSeconds) => {
    const minutes = Math.floor(timeInSeconds / 60);
    const seconds = Math.floor(timeInSeconds % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const handleDownload = () => {
    if (videoUrl) {
      const link = document.createElement('a');
      link.href = videoUrl;
      link.download = `${videoData?.script_data?.title || 'generated_video'}.mp4`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      toast.success('Video download started!');
    }
  };

  const handleShare = () => {
    if (navigator.share && videoUrl) {
      navigator.share({
        title: videoData?.script_data?.title || 'Generated Video',
        text: videoData?.script_data?.content || 'Check out this generated video!',
        url: videoUrl,
      }).then(() => {
        toast.success('Video shared successfully!');
      }).catch(() => {
        // Fallback to clipboard
        navigator.clipboard.writeText(videoUrl);
        toast.success('Video URL copied to clipboard!');
      });
    } else if (videoUrl) {
      // Fallback to clipboard
      navigator.clipboard.writeText(videoUrl);
      toast.success('Video URL copied to clipboard!');
    }
  };

  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => document.removeEventListener('fullscreenchange', handleFullscreenChange);
  }, []);

  return (
    <div className="max-w-6xl mx-auto p-6">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-800 dark:text-gray-200 mb-4">
          🎬 Your Video is Ready!
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          {videoData?.script_data?.title || 'Generated Video'}
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Video Player Section */}
        <div className="lg:col-span-2">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden">
            {/* Video Container */}
            <div className="relative bg-black aspect-video">
              {videoUrl ? (
                <video
                  ref={videoRef}
                  className="w-full h-full object-contain"
                  onTimeUpdate={handleTimeUpdate}
                  onLoadedMetadata={handleLoadedMetadata}
                  onEnded={() => setIsPlaying(false)}
                  poster="/api/placeholder/800/450"
                >
                  <source src={videoUrl} type="video/mp4" />
                  Your browser does not support the video tag.
                </video>
              ) : (
                <div className="w-full h-full flex items-center justify-center">
                  <div className="text-center text-gray-400">
                    <div className="text-6xl mb-4">🎬</div>
                    <p>Video not available</p>
                  </div>
                </div>
              )}
              
              {/* Play/Pause Overlay */}
              <div 
                className="absolute inset-0 flex items-center justify-center cursor-pointer opacity-0 hover:opacity-100 transition-opacity bg-black bg-opacity-30"
                onClick={handlePlayPause}
              >
                {!isPlaying && (
                  <div className="bg-white bg-opacity-20 rounded-full p-6">
                    <svg className="w-12 h-12 text-white" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M8 5v14l11-7z"/>
                    </svg>
                  </div>
                )}
              </div>
            </div>

            {/* Video Controls */}
            <div className="p-4 bg-gray-900 text-white">
              {/* Progress Bar */}
              <div className="mb-4">
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={duration ? (currentTime / duration) * 100 : 0}
                  onChange={handleSeek}
                  className="w-full h-2 bg-gray-600 rounded-lg appearance-none cursor-pointer slider"
                />
              </div>

              {/* Control Buttons */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <button
                    onClick={handlePlayPause}
                    className="p-2 hover:bg-gray-700 rounded-full transition-colors"
                  >
                    {isPlaying ? (
                      <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
                      </svg>
                    ) : (
                      <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M8 5v14l11-7z"/>
                      </svg>
                    )}
                  </button>

                  <span className="text-sm">
                    {formatTime(currentTime)} / {formatTime(duration)}
                  </span>
                </div>

                <div className="flex items-center gap-4">
                  {/* Volume Control */}
                  <div className="flex items-center gap-2">
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/>
                    </svg>
                    <input
                      type="range"
                      min="0"
                      max="100"
                      value={volume * 100}
                      onChange={handleVolumeChange}
                      className="w-20 h-1 bg-gray-600 rounded-lg appearance-none cursor-pointer"
                    />
                  </div>

                  <button
                    onClick={toggleFullscreen}
                    className="p-2 hover:bg-gray-700 rounded-full transition-colors"
                  >
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z"/>
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-wrap gap-4 mt-6">
            <button
              onClick={handleDownload}
              className="flex items-center gap-2 bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600 transition-all"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/>
              </svg>
              Download
            </button>

            <button
              onClick={handleShare}
              className="flex items-center gap-2 bg-green-500 text-white px-6 py-3 rounded-lg hover:bg-green-600 transition-all"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M18 16.08c-.76 0-1.44.3-1.96.77L8.91 12.7c.05-.23.09-.46.09-.7s-.04-.47-.09-.7l7.05-4.11c.54.5 1.25.81 2.04.81 1.66 0 3-1.34 3-3s-1.34-3-3-3-3 1.34-3 3c0 .24.04.47.09.7L8.04 9.81C7.5 9.31 6.79 9 6 9c-1.66 0-3 1.34-3 3s1.34 3 3 3c.79 0 1.50-.31 2.04-.81l7.12 4.16c-.05.21-.08.43-.08.65 0 1.61 1.31 2.92 2.92 2.92 1.61 0 2.92-1.31 2.92-2.92s-1.31-2.92-2.92-2.92z"/>
              </svg>
              Share
            </button>

            <button
              onClick={onRegenerateVideo}
              className="flex items-center gap-2 bg-purple-500 text-white px-6 py-3 rounded-lg hover:bg-purple-600 transition-all"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/>
              </svg>
              Regenerate
            </button>

            <button
              onClick={() => setShowParameters(!showParameters)}
              className="flex items-center gap-2 bg-gray-500 text-white px-6 py-3 rounded-lg hover:bg-gray-600 transition-all"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94L14.4 2.81c-.04-.24-.24-.41-.48-.41h-3.84c-.24 0-.43.17-.47.41L9.25 5.35C8.66 5.59 8.12 5.92 7.63 6.29L5.24 5.33c-.22-.08-.47 0-.59.22L2.74 8.87C2.62 9.08 2.66 9.34 2.86 9.48l2.03 1.58C4.84 11.36 4.8 11.69 4.8 12s.02.64.07.94L2.84 14.52c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61L19.14 12.94zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6s3.6 1.62 3.6 3.6S13.98 15.6 12 15.6z"/>
              </svg>
              {showParameters ? 'Hide' : 'Show'} Parameters
            </button>

            <button
              onClick={onBackToBuilder}
              className="flex items-center gap-2 bg-indigo-500 text-white px-6 py-3 rounded-lg hover:bg-indigo-600 transition-all"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/>
              </svg>
              Back to Builder
            </button>
          </div>
        </div>

        {/* Video Information & Parameters Panel */}
        <div className="lg:col-span-1">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
            <h3 className="text-xl font-bold text-gray-800 dark:text-gray-200 mb-6">
              Video Information
            </h3>

            {/* Video Stats */}
            <div className="space-y-4 mb-6">
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Duration:</span>
                <span className="font-medium">{formatTime(duration)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Resolution:</span>
                <span className="font-medium">1920x1080</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Format:</span>
                <span className="font-medium">MP4</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Created:</span>
                <span className="font-medium">{new Date().toLocaleDateString()}</span>
              </div>
            </div>

            {/* Creation Parameters */}
            {showParameters && videoData && (
              <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
                <h4 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-4">
                  Creation Parameters
                </h4>

                <div className="space-y-4 text-sm">
                  {/* Script Information */}
                  {videoData.script_data && (
                    <div>
                      <h5 className="font-medium text-gray-700 dark:text-gray-300 mb-2">📝 Script</h5>
                      <div className="bg-gray-50 dark:bg-gray-700 p-3 rounded-lg">
                        <p className="text-gray-600 dark:text-gray-400">
                          <strong>Title:</strong> {videoData.script_data.title}
                        </p>
                        <p className="text-gray-600 dark:text-gray-400 mt-1">
                          <strong>Category:</strong> {videoData.script_data.category}
                        </p>
                        {videoData.script_data.content && (
                          <p className="text-gray-600 dark:text-gray-400 mt-2 text-xs">
                            {videoData.script_data.content.substring(0, 100)}...
                          </p>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Voiceover Information */}
                  {videoData.voiceover_data && (
                    <div>
                      <h5 className="font-medium text-gray-700 dark:text-gray-300 mb-2">🎵 Voiceover</h5>
                      <div className="bg-gray-50 dark:bg-gray-700 p-3 rounded-lg">
                        <p className="text-gray-600 dark:text-gray-400">
                          <strong>Voice Model:</strong> {videoData.voiceover_data.voice_model || 'Default'}
                        </p>
                        <p className="text-gray-600 dark:text-gray-400">
                          <strong>Duration:</strong> {videoData.voiceover_data.duration || 'N/A'}s
                        </p>
                      </div>
                    </div>
                  )}

                  {/* Media Information */}
                  {videoData.media_data && videoData.media_data.selected_media && (
                    <div>
                      <h5 className="font-medium text-gray-700 dark:text-gray-300 mb-2">🎬 Media</h5>
                      <div className="bg-gray-50 dark:bg-gray-700 p-3 rounded-lg">
                        <p className="text-gray-600 dark:text-gray-400">
                          <strong>Media Files:</strong> {videoData.media_data.selected_media.length} items
                        </p>
                        {videoData.media_data.selected_media.slice(0, 3).map((media, index) => (
                          <p key={index} className="text-gray-600 dark:text-gray-400 text-xs mt-1">
                            • {media.type}: {media.source || 'Custom'}
                          </p>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Social Media Information */}
                  {videoData.social_media_data && (
                    <div>
                      <h5 className="font-medium text-gray-700 dark:text-gray-300 mb-2">📱 Social Media</h5>
                      <div className="bg-gray-50 dark:bg-gray-700 p-3 rounded-lg">
                        {videoData.social_media_data.hashtags && videoData.social_media_data.hashtags.length > 0 && (
                          <p className="text-gray-600 dark:text-gray-400">
                            <strong>Hashtags:</strong> {videoData.social_media_data.hashtags.slice(0, 3).join(', ')}
                          </p>
                        )}
                        {videoData.social_media_data.keywords && videoData.social_media_data.keywords.length > 0 && (
                          <p className="text-gray-600 dark:text-gray-400 mt-1">
                            <strong>Keywords:</strong> {videoData.social_media_data.keywords.slice(0, 3).join(', ')}
                          </p>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Video Effects */}
                  {videoData.video_effects_config && (
                    <div>
                      <h5 className="font-medium text-gray-700 dark:text-gray-300 mb-2">✨ Effects</h5>
                      <div className="bg-gray-50 dark:bg-gray-700 p-3 rounded-lg">
                        <p className="text-gray-600 dark:text-gray-400">
                          <strong>Style:</strong> {videoData.video_effects_config.style || 'Modern'}
                        </p>
                        <p className="text-gray-600 dark:text-gray-400">
                          <strong>Transitions:</strong> {videoData.video_effects_config.transitions || 'Fade'}
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default VideoDisplayComponent;