'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { toast } from 'react-hot-toast';
import { useBackgroundVideoMonitor } from '../hooks/useBackgroundVideoMonitor';

const VideoDashboard = () => {
  const router = useRouter();
  const [videos, setVideos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all'); // all, completed, processing, failed
  const { backgroundJobs, removeJob } = useBackgroundVideoMonitor();

  useEffect(() => {
    fetchVideos();
  }, []);

  const fetchVideos = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/videos/user/1'); // Replace with actual user ID
      
      if (response.ok) {
        const data = await response.json();
        setVideos(data.videos || []);
      } else {
        console.error('Failed to fetch videos');
      }
    } catch (error) {
      console.error('Error fetching videos:', error);
      toast.error('Failed to load videos');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-100';
      case 'processing': return 'text-blue-600 bg-blue-100';
      case 'failed': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return '✅';
      case 'processing': return '⏳';
      case 'failed': return '❌';
      default: return '📄';
    }
  };

  const filteredVideos = videos.filter(video => {
    if (filter === 'all') return true;
    return video.status === filter;
  });

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const formatDuration = (seconds) => {
    if (!seconds) return 'Unknown';
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 p-6">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
            <span className="ml-3 text-gray-600">Loading your videos...</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-800 dark:text-white mb-2">
                🎬 My Videos
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                Manage and view your generated videos
              </p>
            </div>
            
            <button
              onClick={() => router.push('/video-builder')}
              className="bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600 transition-colors font-medium"
            >
              + Create New Video
            </button>
          </div>
        </div>

        {/* Background Jobs Alert */}
        {backgroundJobs.length > 0 && (
          <div className="bg-blue-500 text-white rounded-xl p-4 mb-6">
            <div className="flex items-center gap-3">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              <div>
                <div className="font-semibold">
                  {backgroundJobs.length} Video{backgroundJobs.length > 1 ? 's' : ''} Processing
                </div>
                <div className="text-sm text-blue-100">
                  We'll notify you when they're ready!
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Filter Tabs */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-6">
          <div className="flex gap-2 mb-4">
            {[
              { key: 'all', label: 'All Videos', count: videos.length },
              { key: 'completed', label: 'Completed', count: videos.filter(v => v.status === 'completed').length },
              { key: 'processing', label: 'Processing', count: videos.filter(v => v.status === 'processing').length },
              { key: 'failed', label: 'Failed', count: videos.filter(v => v.status === 'failed').length }
            ].map(tab => (
              <button
                key={tab.key}
                onClick={() => setFilter(tab.key)}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  filter === tab.key
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600'
                }`}
              >
                {tab.label} ({tab.count})
              </button>
            ))}
          </div>

          <button
            onClick={fetchVideos}
            className="text-blue-500 hover:text-blue-600 text-sm font-medium"
          >
            🔄 Refresh List
          </button>
        </div>

        {/* Videos Grid */}
        {filteredVideos.length === 0 ? (
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-12 text-center">
            <div className="text-6xl mb-4">🎬</div>
            <h3 className="text-xl font-semibold text-gray-800 dark:text-white mb-2">
              No videos found
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              {filter === 'all' ? 'Start creating your first video!' : `No ${filter} videos yet.`}
            </p>
            <button
              onClick={() => router.push('/video-builder')}
              className="bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600 transition-colors"
            >
              Create Your First Video
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredVideos.map((video) => (
              <div
                key={video.id}
                className="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow"
              >
                {/* Thumbnail */}
                <div className="relative h-48 bg-gray-200 dark:bg-gray-700">
                  {video.thumbnail_url ? (
                    <img
                      src={video.thumbnail_url}
                      alt={video.title}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="flex items-center justify-center h-full">
                      <div className="text-6xl">🎬</div>
                    </div>
                  )}
                  
                  {/* Status Badge */}
                  <div className={`absolute top-3 right-3 px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(video.status)}`}>
                    {getStatusIcon(video.status)} {video.status}
                  </div>

                  {/* Duration */}
                  {video.duration && (
                    <div className="absolute bottom-3 right-3 bg-black bg-opacity-75 text-white px-2 py-1 rounded text-xs">
                      {formatDuration(video.duration)}
                    </div>
                  )}
                </div>

                {/* Content */}
                <div className="p-4">
                  <h3 className="font-semibold text-gray-800 dark:text-white mb-2 truncate">
                    {video.title || 'Untitled Video'}
                  </h3>
                  
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                    Created: {formatDate(video.created_at)}
                  </p>

                  {video.category && (
                    <div className="inline-block bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 px-2 py-1 rounded text-xs mb-3">
                      {video.category}
                    </div>
                  )}

                  {/* Actions */}
                  <div className="flex gap-2">
                    {video.status === 'completed' ? (
                      <button
                        onClick={() => router.push(`/video-display?id=${video.id}`)}
                        className="flex-1 bg-green-500 text-white px-3 py-2 rounded-lg hover:bg-green-600 transition-colors text-sm font-medium"
                      >
                        View Video
                      </button>
                    ) : video.status === 'processing' ? (
                      <button
                        onClick={() => router.push(`/video-process?id=${video.id}`)}
                        className="flex-1 bg-blue-500 text-white px-3 py-2 rounded-lg hover:bg-blue-600 transition-colors text-sm font-medium"
                      >
                        View Progress
                      </button>
                    ) : (
                      <button
                        disabled
                        className="flex-1 bg-gray-400 text-white px-3 py-2 rounded-lg cursor-not-allowed text-sm font-medium"
                      >
                        {video.status === 'failed' ? 'Failed' : 'Unavailable'}
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default VideoDashboard;