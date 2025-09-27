'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { toast } from 'react-hot-toast';


// Video card component
const VideoCard = ({ video, onDelete }) => {
  const handleViewDetails = () => {
    if (video.outputUrl) {
      // Open video in a new tab or window
      window.open(video.outputUrl, '_blank');
    } else {
      alert('Video is not yet available. Please wait for processing to complete.');
    }
  };

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <div className="relative h-48">
        <Image 
          src={video.thumbnail || "/placeholder-thumbnail.svg"} 
          alt={video.title || "custom view title"}
          fill
          className="object-cover"
        />
        <div className="absolute inset-0 bg-black bg-opacity-10 flex items-center justify-center">
          <button 
            onClick={handleViewDetails}
            className="bg-white bg-opacity-70 rounded-full p-3 hover:bg-opacity-90 transition-all"
            disabled={!video.outputUrl}
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-indigo-600" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
            </svg>
          </button>
        </div>
        {/* Delete button overlay */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            onDelete(video.id);
          }}
          className="absolute top-2 right-2 bg-red-500 bg-opacity-80 hover:bg-opacity-100 text-white rounded-full p-2 transition-all"
          title="Delete video"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </button>
      </div>
      <div className="p-4">
        <h3 className="text-lg font-semibold text-gray-800 mb-1">{video.title}</h3>
        <p className="text-gray-500 text-sm mb-3">Generated on {new Date(video.createdAt).toLocaleDateString()}</p>
        <div className="flex justify-between items-center">
          <span className={`px-2 py-1 rounded-full text-xs ${
            video.status === 'completed' 
              ? 'bg-green-100 text-green-800' 
              : video.status === 'processing' 
                ? 'bg-yellow-100 text-yellow-800'
                : 'bg-gray-100 text-gray-800'
          }`}>
            {video.status}
          </span>
          <button 
            onClick={handleViewDetails}
            className={`text-sm font-medium ${
              video.outputUrl 
                ? 'text-indigo-600 hover:text-indigo-800' 
                : 'text-gray-400 cursor-not-allowed'
            }`}
            disabled={!video.outputUrl}
          >
            {video.outputUrl ? 'Watch Video' : 'Processing...'}
          </button>
        </div>
      </div>
    </div>
  );
};

// View toggle component
const ViewToggle = ({ activeView, setActiveView }) => {
  const views = [
    { id: 'grid', icon: (
      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
        <path d="M5 3a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2H5zM5 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2H5zM11 5a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V5zM11 13a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
      </svg>
    ) },
    { id: 'table', icon: (
      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
        <path fillRule="evenodd" d="M5 4a3 3 0 00-3 3v6a3 3 0 003 3h10a3 3 0 003-3V7a3 3 0 00-3-3H5zm-1 9v-1h5v2H5a1 1 0 01-1-1zm7 1h4a1 1 0 001-1v-1h-5v2zm0-4h5V8h-5v2zM9 8H4v2h5V8z" clipRule="evenodd" />
      </svg>
    ) },
    { id: 'kanban', icon: (
      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
        <path d="M5 3a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2V5a2 2 0 00-2-2H5zm0 2h3v10H5V5zm5 0h5v2h-5V5zm0 4h5v6h-5V9z" />
      </svg>
    ) },
    { id: 'list', icon: (
      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
        <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
      </svg>
    ) }
  ];

  return (
    <div className="bg-white rounded-md shadow-sm inline-flex">
      {views.map((view) => (
        <button
          key={view.id}
          onClick={() => setActiveView(view.id)}
          className={`p-2 ${activeView === view.id ? 'bg-indigo-50 text-indigo-600' : 'text-gray-500 hover:text-gray-700'}`}
          title={view.id.charAt(0).toUpperCase() + view.id.slice(1)}
        >
          {view.icon}
        </button>
      ))}
    </div>
  );
};

// Table view component
const TableView = ({ videos }) => {
  return (
    <div className="overflow-x-auto mt-4">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Title
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Status
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Created At
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Duration
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {videos.map((video) => (
            <tr key={video.id} className="hover:bg-gray-50">
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="flex items-center">
                  <div className="h-10 w-16 flex-shrink-0 relative overflow-hidden rounded">
                    <Image 
                      src={video.thumbnail || "/placeholder-thumbnail.svg"}
                      alt={video.title}
                      fill
                      className="object-cover"
                    />
                  </div>
                  <div className="ml-4">
                    <div className="text-sm font-medium text-gray-900">{video.title}</div>
                  </div>
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                  video.status === 'completed' 
                    ? 'bg-green-100 text-green-800' 
                    : video.status === 'processing' 
                      ? 'bg-yellow-100 text-yellow-800'
                      : 'bg-gray-100 text-gray-800'
                }`}>
                  {video.status}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {new Date(video.createdAt).toLocaleDateString()}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {video.duration}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button className="text-indigo-600 hover:text-indigo-900 mr-4">View</button>
                <button className="text-indigo-600 hover:text-indigo-900">Share</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

// Kanban view component
const KanbanView = ({ videos }) => {
  // Group videos by status
  const groupedVideos = videos.reduce((acc, video) => {
    const status = video.status;
    if (!acc[status]) {
      acc[status] = [];
    }
    acc[status].push(video);
    return acc;
  }, {});

  // Define columns and their order
  const columns = [
    { id: 'draft', label: 'Draft' },
    { id: 'processing', label: 'Processing' },
    { id: 'completed', label: 'Completed' }
  ];

  return (
    <div className="flex flex-col md:flex-row gap-6 mt-4 overflow-x-auto pb-4">
      {columns.map((column) => (
        <div key={column.id} className="flex-shrink-0 w-full md:w-80">
          <div className="bg-gray-50 rounded-t-lg p-3 border border-gray-200">
            <h3 className="font-medium text-gray-700 flex items-center justify-between">
              {column.label}
              <span className="bg-gray-200 text-gray-700 px-2 py-1 text-xs rounded-full">
                {groupedVideos[column.id]?.length || 0}
              </span>
            </h3>
          </div>
          <div className="bg-gray-50 rounded-b-lg p-3 min-h-[300px] border-l border-r border-b border-gray-200">
            {groupedVideos[column.id]?.map((video) => (
              <div key={video.id} className="bg-white rounded-lg p-3 shadow-sm mb-3 cursor-pointer hover:shadow-md transition-shadow">
                <div className="relative h-32 mb-2 rounded overflow-hidden">
                  <Image 
                    src={video.thumbnail || "/placeholder-thumbnail.svg"} 
                    alt={video.title}
                    fill
                    className="object-cover"
                  />
                </div>
                <h4 className="font-medium text-gray-800">{video.title}</h4>
                <p className="text-xs text-gray-500 mt-1">Created: {new Date(video.createdAt).toLocaleDateString()}</p>
              </div>
            ))}
            {(!groupedVideos[column.id] || groupedVideos[column.id].length === 0) && (
              <div className="flex items-center justify-center h-20 border-2 border-dashed border-gray-200 rounded-lg">
                <p className="text-sm text-gray-400">No videos</p>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

// List view component
const ListView = ({ videos }) => {
  return (
    <div className="mt-4">
      <ul className="divide-y divide-gray-200 bg-white shadow overflow-hidden rounded-md">
        {videos.map((video) => (
          <li key={video.id} className="px-6 py-4 hover:bg-gray-50">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <div className="h-12 w-20 flex-shrink-0 relative overflow-hidden rounded">
                  <Image 
                    src={video.thumbnail || "/placeholder-thumbnail.svg"} 
                    alt={video.title}
                    fill
                    className="object-cover"
                  />
                </div>
                <div className="ml-4">
                  <div className="text-sm font-medium text-gray-900">{video.title}</div>
                  <div className="text-sm text-gray-500">{video.description}</div>
                </div>
              </div>
              <div className="flex items-center">
                <span className={`px-2 py-1 text-xs rounded-full ${
                  video.status === 'completed' 
                    ? 'bg-green-100 text-green-800' 
                    : video.status === 'processing' 
                      ? 'bg-yellow-100 text-yellow-800'
                      : 'bg-gray-100 text-gray-800'
                } mr-4`}>
                  {video.status}
                </span>
                <span className="text-sm text-gray-500 mr-4">
                  {new Date(video.createdAt).toLocaleDateString()}
                </span>
                <button className="text-indigo-600 hover:text-indigo-900 text-sm font-medium">
                  View Details
                </button>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

// Main dashboard page
export default function Dashboard() {
  const router = useRouter();
  const [videos, setVideos] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeView, setActiveView] = useState('grid');
  const [user, setUser] = useState(null);
  const [authChecking, setAuthChecking] = useState(true);
  
  // Dashboard analytics state
  const [dashboardStats, setDashboardStats] = useState({
    totalScripts: 0,
    totalVoiceovers: 0,
    totalSocialPosts: 0,
    totalVideos: 0
  });
  const [recentActivity, setRecentActivity] = useState([]);
  const [dashboardLoading, setDashboardLoading] = useState(true);
  
  // Performance metrics state
  const [performanceMetrics, setPerformanceMetrics] = useState({
    thisWeekActivity: 0,
    mostUsedVoice: 'N/A',
    avgVideoLength: 0,
    completionRate: 0
  });
  
  // Check if user is authenticated and load videos
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const response = await fetch('/api/auth/me', {
          credentials: 'include' // Include cookies for authentication
        });
        if (response.ok) {
          const userData = await response.json();
          setUser(userData);
          // Load videos and dashboard data after authentication
          await Promise.all([
            loadVideos(userData),
            loadDashboardData(userData)
          ]);
        } else {
          // Redirect to login if not authenticated
          router.push('/login');
        }
      } catch (error) {
        console.error('Authentication check failed:', error);
        router.push('/login');
      } finally {
        setAuthChecking(false);
      }
    };
    
    checkAuth();
  }, [router]);

  // Auto-refresh videos every 30 seconds if there are processing videos
  useEffect(() => {
    const hasProcessingVideos = videos.some(video => video.status === 'processing');
    
    if (hasProcessingVideos && user) {
      const interval = setInterval(() => {
        loadVideos(user);
      }, 30000); // Refresh every 30 seconds

      return () => clearInterval(interval);
    }
  }, [videos, user]);

  // Load videos from FastAPI backend
  const loadVideos = async (userData) => {
    setIsLoading(true);
    try {
      // Fetch videos from FastAPI backend
      const response = await fetch(`http://localhost:8000/api/videos?user_id=${userData?.id || 'anonymous_user'}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        throw new Error('Failed to load videos');
      }

      const videosData = await response.json();

      // Transform backend data to frontend format
      const transformedVideos = videosData.map(video => ({
        id: video.video_id || video.id,
        title: video.title || 'Untitled Video',
        description: video.description || video.prompt || '',
        thumbnail: video.thumbnail || '/placeholder-thumbnail.svg',
        status: video.status || 'unknown',
        createdAt: video.created_at,
        duration: video.duration ? `${Math.floor(video.duration / 60)}:${String(video.duration % 60).padStart(2, '0')}` : 'N/A',
        outputUrl: video.output_url,
        prompt: video.prompt
      }));

      setVideos(transformedVideos);
    } catch (error) {
      console.error('Failed to load videos:', error);
      setError('Failed to load videos. Please try again.');
      // Fallback to empty array instead of mock data
      setVideos([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await fetch('/api/auth/logout', { method: 'POST' });
      // Optionally clear user state here if using global state
      window.location.href = '/login';
    } catch (err) {
      alert('Logout failed');
    }
  };

  const handleDeleteVideo = async (videoId) => {
    if (!confirm('Are you sure you want to delete this video? This action cannot be undone.')) {
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/api/videos/${videoId}?user_id=${user?.id || 'anonymous_user'}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to delete video');
      }

      // Remove video from local state
      setVideos(videos.filter(video => video.id !== videoId));
      
    } catch (error) {
      console.error('Failed to delete video:', error);
      alert(`Failed to delete video: ${error.message}`);
    }
  };

  const handleRefresh = () => {
    if (user) {
      loadVideos(user);
      loadDashboardData(user);
    }
  };

  // Load dashboard analytics data
  const loadDashboardData = async (userData) => {
    if (!userData?.id) return;
    
    setDashboardLoading(true);
    try {
      // Fetch all dashboard data in parallel
      const [scriptsRes, voiceoversRes, socialRes, videosRes] = await Promise.all([
        fetch(`http://localhost:8000/api/scripts?user_id=${userData.id}&limit=100`).catch(() => ({ ok: false })),
        fetch(`http://localhost:8000/api/voiceovers?user_id=${userData.id}&limit=100`).catch(() => ({ ok: false })),
        fetch(`http://localhost:8000/api/social-content?user_id=${userData.id}&limit=100`).catch(() => ({ ok: false })),
        fetch(`http://localhost:8000/api/videos?user_id=${userData.id}&limit=100`).catch(() => ({ ok: false }))
      ]);

      const [scriptsResponse, voiceoversResponse, socialResponse, videosResponse] = await Promise.all([
        scriptsRes.ok ? scriptsRes.json().catch(() => ({})) : {},
        voiceoversRes.ok ? voiceoversRes.json().catch(() => ({})) : {},
        socialRes.ok ? socialRes.json().catch(() => ({})) : {},
        videosRes.ok ? videosRes.json().catch(() => ({})) : {}
      ]);

      // Extract actual data arrays from API response format
      const scriptsData = scriptsResponse.scripts || [];
      const voiceoversData = voiceoversResponse.voiceovers || [];
      const socialData = socialResponse.social_posts || [];
      const videosData = videosResponse.videos || videosResponse || []; // Handle both formats

      console.log('Dashboard data loaded:', {
        scripts: scriptsData.length,
        voiceovers: voiceoversData.length,
        social: socialData.length,
        videos: videosData.length
      });

      // Update stats
      setDashboardStats({
        totalScripts: Array.isArray(scriptsData) ? scriptsData.length : 0,
        totalVoiceovers: Array.isArray(voiceoversData) ? voiceoversData.length : 0,
        totalSocialPosts: Array.isArray(socialData) ? socialData.length : 0,
        totalVideos: Array.isArray(videosData) ? videosData.length : 0
      });

      // Create recent activity feed
      const allActivity = [];
      
      if (Array.isArray(scriptsData)) {
        scriptsData.slice(0, 5).forEach(script => {
          allActivity.push({
            type: 'script',
            title: script.title || script.script_topic || 'Script Generated',
            description: `Generated script for ${script.script_topic || 'content creation'}`,
            time: script.created_at,
            id: script.id,
            icon: '📝'
          });
        });
      }

      if (Array.isArray(voiceoversData)) {
        voiceoversData.slice(0, 5).forEach(voiceover => {
          allActivity.push({
            type: 'voiceover',
            title: voiceover.voice_name || 'Generated Voiceover',
            description: `Created voiceover with ${voiceover.voice_name || 'AI voice'}`,
            time: voiceover.created_at,
            id: voiceover.id,
            icon: '🎤'
          });
        });
      }

      if (Array.isArray(socialData)) {
        socialData.slice(0, 5).forEach(post => {
          allActivity.push({
            type: 'social',
            title: post.platform || 'Social Media Post',
            description: `Created ${post.platform || 'social media'} content`,
            time: post.created_at,
            id: post.id,
            icon: '📱'
          });
        });
      }

      if (Array.isArray(videosData)) {
        videosData.slice(0, 5).forEach(video => {
          allActivity.push({
            type: 'video',
            title: video.title || 'New Video',
            description: `Generated video: ${video.title || 'Untitled'}`,
            time: video.created_at,
            id: video.id,
            icon: '🎥'
          });
        });
      }

      // Sort by time and take latest 10
      allActivity.sort((a, b) => new Date(b.time) - new Date(a.time));
      setRecentActivity(allActivity.slice(0, 10));

      // Calculate performance metrics
      const now = new Date();
      const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
      
      // This week's activity
      const thisWeekActivity = allActivity.filter(activity => 
        activity.time && new Date(activity.time) >= weekAgo
      ).length;

      // Most used voice (from voiceovers data)
      let mostUsedVoice = 'N/A';
      if (Array.isArray(voiceoversData) && voiceoversData.length > 0) {
        const voiceCount = {};
        voiceoversData.forEach(vo => {
          const voice = vo.voice_name || 'Unknown';
          voiceCount[voice] = (voiceCount[voice] || 0) + 1;
        });
        mostUsedVoice = Object.keys(voiceCount).reduce((a, b) => 
          voiceCount[a] > voiceCount[b] ? a : b
        );
      }

      // Average video length (if duration data available)
      let avgVideoLength = 0;
      if (Array.isArray(videosData) && videosData.length > 0) {
        const validDurations = videosData.filter(v => v.duration && v.duration > 0);
        if (validDurations.length > 0) {
          avgVideoLength = validDurations.reduce((sum, v) => sum + v.duration, 0) / validDurations.length;
        }
      }

      // Completion rate (completed videos vs total)
      let completionRate = 0;
      if (Array.isArray(videosData) && videosData.length > 0) {
        const completedVideos = videosData.filter(v => v.status === 'completed' || v.output_url).length;
        completionRate = Math.round((completedVideos / videosData.length) * 100);
      }

      setPerformanceMetrics({
        thisWeekActivity,
        mostUsedVoice,
        avgVideoLength: Math.round(avgVideoLength),
        completionRate
      });
      
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setDashboardLoading(false);
    }
  };

  const renderVideosView = () => {
    if (isLoading) {
      return (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your videos...</p>
        </div>
      );
    }

    if (error) {
      return (
        <div className="bg-white rounded-lg shadow p-6 text-center">
          <div className="text-red-600 mb-4">
            <svg className="w-12 h-12 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Error Loading Videos</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <button 
            onClick={() => user && loadVideos(user)}
            className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
          >
            Try Again
          </button>
        </div>
      );
    }

    if (videos.length === 0) {
      return (
        <div className="bg-white rounded-lg shadow p-6 text-center">
          <h3 className="text-lg font-medium text-gray-900 mb-2">No videos yet</h3>
          <p className="text-gray-500 mb-4">Start creating your first AI-generated video now!</p>
          <Link href="/create-video" className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 inline-flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
            </svg>
            Create First Video
          </Link>
        </div>
      );
    }

    switch (activeView) {
      case 'table':
        return <TableView videos={videos} />;
      case 'kanban':
        return <KanbanView videos={videos} />;
      case 'list':
        return <ListView videos={videos} />;
      case 'grid':
      default:
        return (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {videos.map((video) => (
              <VideoCard key={video.id} video={video} onDelete={handleDeleteVideo} />
            ))}
          </div>
        );
    }
  };

  // Show loading state while checking authentication
  if (authChecking) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }
  
  // If no user after authentication check (should have redirected, but just in case)
  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-100">
      {/* Background Pattern */}
      <div className="absolute inset-0 bg-grid-pattern opacity-5 pointer-events-none"></div>
      
      <main className="relative max-w-7xl mx-auto py-8 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center mb-10 gap-6">
            <div className="space-y-2">
              <h1 className="text-4xl font-bold bg-gradient-to-r from-gray-900 via-gray-800 to-gray-600 bg-clip-text text-transparent">
                Dashboard
              </h1>
              <p className="text-lg text-gray-600">Manage your AI video creation workflow</p>
              <div className="flex items-center space-x-4 text-sm text-gray-500">
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse"></div>
                  Live Data
                </div>
                <div className="flex items-center">
                  <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Last updated: {new Date().toLocaleTimeString()}
                </div>
              </div>
            </div>
            <div className="flex flex-col sm:flex-row gap-3 w-full lg:w-auto">
              <button
                onClick={handleRefresh}
                disabled={isLoading}
                className="group px-6 py-3 bg-white border border-gray-200 text-gray-700 rounded-xl hover:bg-gray-50 hover:border-gray-300 disabled:opacity-50 flex items-center justify-center sm:justify-start w-full sm:w-auto transition-all duration-200 shadow-sm hover:shadow"
              >
                <svg className={`h-5 w-5 mr-2 text-gray-500 group-hover:text-gray-700 ${isLoading ? 'animate-spin' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                <span className="font-medium">{isLoading ? 'Refreshing...' : 'Refresh'}</span>
              </button>
              <Link href="/create-video" className="group px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl hover:from-indigo-700 hover:to-purple-700 flex items-center justify-center sm:justify-start w-full sm:w-auto transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105">
                <svg className="h-5 w-5 mr-2 group-hover:rotate-90 transition-transform duration-200" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
                </svg>
                <span className="font-semibold">Create New Video</span>
              </Link>
            </div>
          </div>

          {/* Modern Analytics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6 mb-8">
            {dashboardLoading ? (
              // Enhanced loading placeholders
              [...Array(4)].map((_, i) => (
                <div key={i} className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 animate-pulse">
                  <div className="flex items-center justify-between">
                    <div className="space-y-3">
                      <div className="h-4 bg-gray-200 rounded w-24"></div>
                      <div className="h-8 bg-gray-200 rounded w-16"></div>
                    </div>
                    <div className="w-12 h-12 bg-gray-200 rounded-lg"></div>
                  </div>
                  <div className="mt-4 h-3 bg-gray-200 rounded w-32"></div>
                </div>
              ))
            ) : (
              <>
                <div className="group bg-white rounded-xl shadow-sm hover:shadow-md border border-gray-100 p-6 transition-all duration-200 hover:border-blue-200">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-500 mb-2">Total Scripts</p>
                      <p className="text-3xl font-bold text-gray-900 group-hover:text-blue-600 transition-colors">
                        {dashboardStats.totalScripts}
                      </p>
                    </div>
                    <div className="p-3 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg group-hover:from-blue-100 group-hover:to-blue-200 transition-all">
                      <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </div>
                  </div>
                  <div className="mt-4">
                    <Link href="/create-video" className="inline-flex items-center text-sm font-medium text-blue-600 hover:text-blue-700 group-hover:gap-2 transition-all">
                      Generate new script
                      <svg className="w-4 h-4 ml-1 group-hover:ml-0 transition-all" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </Link>
                  </div>
                </div>

                <div className="group bg-white rounded-xl shadow-sm hover:shadow-md border border-gray-100 p-6 transition-all duration-200 hover:border-purple-200">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-500 mb-2">Voiceovers</p>
                      <p className="text-3xl font-bold text-gray-900 group-hover:text-purple-600 transition-colors">
                        {dashboardStats.totalVoiceovers}
                      </p>
                    </div>
                    <div className="p-3 bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg group-hover:from-purple-100 group-hover:to-purple-200 transition-all">
                      <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                      </svg>
                    </div>
                  </div>
                  <div className="mt-4">
                    <Link href="/voicerover" className="inline-flex items-center text-sm font-medium text-purple-600 hover:text-purple-700 group-hover:gap-2 transition-all">
                      Create voiceover
                      <svg className="w-4 h-4 ml-1 group-hover:ml-0 transition-all" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </Link>
                  </div>
                </div>

                <div className="group bg-white rounded-xl shadow-sm hover:shadow-md border border-gray-100 p-6 transition-all duration-200 hover:border-green-200">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-500 mb-2">Social Posts</p>
                      <p className="text-3xl font-bold text-gray-900 group-hover:text-green-600 transition-colors">
                        {dashboardStats.totalSocialPosts}
                      </p>
                    </div>
                    <div className="p-3 bg-gradient-to-br from-green-50 to-green-100 rounded-lg group-hover:from-green-100 group-hover:to-green-200 transition-all">
                      <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
                      </svg>
                    </div>
                  </div>
                  <div className="mt-4">
                    <span className="inline-flex items-center text-sm font-medium text-green-600">
                      Coming soon...
                      <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </span>
                  </div>
                </div>

                <div className="group bg-white rounded-xl shadow-sm hover:shadow-md border border-gray-100 p-6 transition-all duration-200 hover:border-indigo-200">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-500 mb-2">Total Videos</p>
                      <p className="text-3xl font-bold text-gray-900 group-hover:text-indigo-600 transition-colors">
                        {dashboardStats.totalVideos}
                      </p>
                    </div>
                    <div className="p-3 bg-gradient-to-br from-indigo-50 to-indigo-100 rounded-lg group-hover:from-indigo-100 group-hover:to-indigo-200 transition-all">
                      <svg className="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                    </div>
                  </div>
                  <div className="mt-4">
                    <Link href="/create-video" className="inline-flex items-center text-sm font-medium text-indigo-600 hover:text-indigo-700 group-hover:gap-2 transition-all">
                      Create new video
                      <svg className="w-4 h-4 ml-1 group-hover:ml-0 transition-all" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </Link>
                  </div>
                </div>
              </>
            )}
          </div>

          {/* Advanced Performance Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6 mb-8">
            <div className="relative overflow-hidden bg-gradient-to-br from-blue-500 via-blue-600 to-blue-700 rounded-2xl p-6 text-white">
              <div className="absolute top-0 right-0 -mt-4 -mr-4 w-20 h-20 bg-white bg-opacity-10 rounded-full"></div>
              <div className="relative">
                <div className="flex items-center justify-between mb-4">
                  <div className="p-2 bg-white bg-opacity-20 rounded-lg">
                    <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                    </svg>
                  </div>
                  <div className="text-right">
                    <p className="text-blue-200 text-sm">This Week</p>
                  </div>
                </div>
                <div className="mb-2">
                  <p className="text-3xl font-bold">{performanceMetrics.thisWeekActivity}</p>
                  <p className="text-blue-200 text-sm">New items created</p>
                </div>
                <div className="flex items-center">
                  <div className="flex-1 bg-white bg-opacity-20 rounded-full h-2 mr-3">
                    <div className="bg-white rounded-full h-2" style={{width: `${Math.min(performanceMetrics.thisWeekActivity * 10, 100)}%`}}></div>
                  </div>
                  <span className="text-sm">+{performanceMetrics.thisWeekActivity}</span>
                </div>
              </div>
            </div>

            <div className="relative overflow-hidden bg-gradient-to-br from-purple-500 via-purple-600 to-purple-700 rounded-2xl p-6 text-white">
              <div className="absolute top-0 right-0 -mt-4 -mr-4 w-20 h-20 bg-white bg-opacity-10 rounded-full"></div>
              <div className="relative">
                <div className="flex items-center justify-between mb-4">
                  <div className="p-2 bg-white bg-opacity-20 rounded-lg">
                    <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.196-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                    </svg>
                  </div>
                  <div className="text-right">
                    <p className="text-purple-200 text-sm">Popular Voice</p>
                  </div>
                </div>
                <div className="mb-2">
                  <p className="text-xl font-bold truncate">{performanceMetrics.mostUsedVoice}</p>
                  <p className="text-purple-200 text-sm">Most frequently used</p>
                </div>
                <div className="flex items-center">
                  <div className="p-1 bg-white bg-opacity-20 rounded-full">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                    </svg>
                  </div>
                  <span className="ml-2 text-sm">Voice Leader</span>
                </div>
              </div>
            </div>

            <div className="relative overflow-hidden bg-gradient-to-br from-emerald-500 via-emerald-600 to-emerald-700 rounded-2xl p-6 text-white">
              <div className="absolute top-0 right-0 -mt-4 -mr-4 w-20 h-20 bg-white bg-opacity-10 rounded-full"></div>
              <div className="relative">
                <div className="flex items-center justify-between mb-4">
                  <div className="p-2 bg-white bg-opacity-20 rounded-lg">
                    <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div className="text-right">
                    <p className="text-emerald-200 text-sm">Avg Duration</p>
                  </div>
                </div>
                <div className="mb-2">
                  <p className="text-3xl font-bold">{performanceMetrics.avgVideoLength}<span className="text-lg">s</span></p>
                  <p className="text-emerald-200 text-sm">Video length</p>
                </div>
                <div className="flex items-center">
                  <div className="flex-1 bg-white bg-opacity-20 rounded-full h-2 mr-3">
                    <div className="bg-white rounded-full h-2" style={{width: `${Math.min(performanceMetrics.avgVideoLength / 2, 100)}%`}}></div>
                  </div>
                  <span className="text-sm">Optimal</span>
                </div>
              </div>
            </div>

            <div className="relative overflow-hidden bg-gradient-to-br from-orange-500 via-orange-600 to-orange-700 rounded-2xl p-6 text-white">
              <div className="absolute top-0 right-0 -mt-4 -mr-4 w-20 h-20 bg-white bg-opacity-10 rounded-full"></div>
              <div className="relative">
                <div className="flex items-center justify-between mb-4">
                  <div className="p-2 bg-white bg-opacity-20 rounded-lg">
                    <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div className="text-right">
                    <p className="text-orange-200 text-sm">Success Rate</p>
                  </div>
                </div>
                <div className="mb-2">
                  <p className="text-3xl font-bold">{performanceMetrics.completionRate}<span className="text-lg">%</span></p>
                  <p className="text-orange-200 text-sm">Completed videos</p>
                </div>
                <div className="flex items-center">
                  <div className="flex-1 bg-white bg-opacity-20 rounded-full h-2 mr-3">
                    <div className="bg-white rounded-full h-2" style={{width: `${performanceMetrics.completionRate}%`}}></div>
                  </div>
                  <span className="text-sm">{performanceMetrics.completionRate >= 80 ? 'Excellent' : 'Good'}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Modern Activity & Actions Layout */}
          <div className="grid grid-cols-1 xl:grid-cols-3 gap-8 mb-8">
            <div className="xl:col-span-2 bg-white rounded-2xl shadow-sm border border-gray-100">
              <div className="p-6 border-b border-gray-100">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900">Recent Activity</h3>
                    <p className="text-sm text-gray-500 mt-1">Latest updates across your workflow</p>
                  </div>
                  <div className="p-2 bg-gray-50 rounded-lg">
                    <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                </div>
              </div>
              <div className="p-6">
                {dashboardLoading ? (
                  <div className="space-y-6">
                    {[...Array(5)].map((_, i) => (
                      <div key={i} className="animate-pulse flex items-center space-x-4">
                        <div className="w-12 h-12 bg-gray-200 rounded-xl"></div>
                        <div className="flex-1">
                          <div className="h-4 bg-gray-200 rounded mb-2"></div>
                          <div className="h-3 bg-gray-200 rounded w-3/4"></div>
                          <div className="h-3 bg-gray-200 rounded w-1/2 mt-1"></div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : recentActivity.length > 0 ? (
                  <div className="space-y-6">
                    {recentActivity.map((activity, index) => (
                      <div key={index} className="group flex items-center space-x-4 p-3 -m-3 rounded-xl hover:bg-gray-50 transition-colors">
                        <div className={`w-12 h-12 rounded-xl flex items-center justify-center text-lg font-medium shadow-sm ${
                          activity.type === 'script' ? 'bg-gradient-to-br from-blue-400 to-blue-600 text-white' :
                          activity.type === 'voiceover' ? 'bg-gradient-to-br from-purple-400 to-purple-600 text-white' :
                          activity.type === 'social' ? 'bg-gradient-to-br from-green-400 to-green-600 text-white' :
                          'bg-gradient-to-br from-indigo-400 to-indigo-600 text-white'
                        }`}>
                          {activity.icon}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-semibold text-gray-900 truncate group-hover:text-gray-700">
                            {activity.title}
                          </p>
                          <p className="text-sm text-gray-600 truncate">
                            {activity.description}
                          </p>
                          <div className="flex items-center mt-1">
                            <svg className="w-3 h-3 text-gray-400 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            <p className="text-xs text-gray-400">
                              {activity.time ? new Date(activity.time).toLocaleDateString('en-US', { 
                                month: 'short', 
                                day: 'numeric', 
                                hour: '2-digit', 
                                minute: '2-digit' 
                              }) : 'Recently'}
                            </p>
                          </div>
                        </div>
                        <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                          <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                          </svg>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <div className="w-24 h-24 mx-auto bg-gray-100 rounded-full flex items-center justify-center mb-4">
                      <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <p className="text-gray-500 font-medium">No recent activity</p>
                    <p className="text-sm text-gray-400 mt-1">Start creating content to see activity here</p>
                  </div>
                )}
              </div>
            </div>

            {/* Enhanced Quick Actions Panel */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100">
              <div className="p-6 border-b border-gray-100">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900">Quick Actions</h3>
                    <p className="text-sm text-gray-500 mt-1">Fast access to key features</p>
                  </div>
                  <div className="p-2 bg-gray-50 rounded-lg">
                    <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                </div>
              </div>
              <div className="p-6 space-y-4">
                <Link href="/create-video" className="group relative block">
                  <div className="flex items-center p-4 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 text-white hover:from-indigo-600 hover:to-purple-700 transition-all duration-300 transform hover:scale-105">
                    <div className="p-2 bg-white bg-opacity-20 rounded-lg mr-4">
                      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                    </div>
                    <div className="flex-1">
                      <p className="font-semibold">Create Video</p>
                      <p className="text-sm text-white text-opacity-80">Generate new content</p>
                    </div>
                    <svg className="w-5 h-5 text-white text-opacity-60 group-hover:text-opacity-100 group-hover:translate-x-1 transition-all" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </Link>

                <Link href="/voicerover" className="group relative block">
                  <div className="flex items-center p-4 rounded-xl bg-gradient-to-r from-purple-500 to-pink-600 text-white hover:from-purple-600 hover:to-pink-700 transition-all duration-300 transform hover:scale-105">
                    <div className="p-2 bg-white bg-opacity-20 rounded-lg mr-4">
                      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                      </svg>
                    </div>
                    <div className="flex-1">
                      <p className="font-semibold">Generate Voice</p>
                      <p className="text-sm text-white text-opacity-80">Create voiceover</p>
                    </div>
                    <svg className="w-5 h-5 text-white text-opacity-60 group-hover:text-opacity-100 group-hover:translate-x-1 transition-all" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </Link>

                <Link href="/generated-voiceovers" className="group relative block">
                  <div className="flex items-center p-4 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 text-white hover:from-emerald-600 hover:to-teal-700 transition-all duration-300 transform hover:scale-105">
                    <div className="p-2 bg-white bg-opacity-20 rounded-lg mr-4">
                      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                      </svg>
                    </div>
                    <div className="flex-1">
                      <p className="font-semibold">Generated Voiceovers</p>
                      <p className="text-sm text-white text-opacity-80">Manage AI voices</p>
                    </div>
                    <svg className="w-5 h-5 text-white text-opacity-60 group-hover:text-opacity-100 group-hover:translate-x-1 transition-all" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </Link>

                <button
                  onClick={handleRefresh}
                  className="group relative w-full"
                  disabled={dashboardLoading}
                >
                  <div className={`flex items-center p-4 rounded-xl text-white transition-all duration-300 transform hover:scale-105 ${
                    dashboardLoading 
                      ? 'bg-gradient-to-r from-gray-400 to-gray-500 cursor-not-allowed' 
                      : 'bg-gradient-to-r from-blue-500 to-cyan-600 hover:from-blue-600 hover:to-cyan-700'
                  }`}>
                    <div className="p-2 bg-white bg-opacity-20 rounded-lg mr-4">
                      <svg className={`w-6 h-6 ${dashboardLoading ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                      </svg>
                    </div>
                    <div className="flex-1">
                      <p className="font-semibold">{dashboardLoading ? 'Refreshing...' : 'Refresh Data'}</p>
                      <p className="text-sm text-white text-opacity-80">Update dashboard</p>
                    </div>
                    {!dashboardLoading && (
                      <svg className="w-5 h-5 text-white text-opacity-60 group-hover:text-opacity-100 group-hover:translate-x-1 transition-all" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    )}
                  </div>
                </button>
              </div>
            </div>
          </div>

          {/* Videos Section */}
          <div className="mb-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold text-gray-900">Your Videos</h2>
              <ViewToggle activeView={activeView} setActiveView={setActiveView} />
            </div>
          </div>

          {isLoading ? (
            <div className="flex justify-center items-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
            </div>
          ) : error ? (
            <div className="bg-red-50 border-l-4 border-red-500 p-4">
              <p className="text-red-700">{error}</p>
            </div>
          ) : renderVideosView()}
        </div>
      </main>
    </div>
  );
}
