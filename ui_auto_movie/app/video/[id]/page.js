'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';

export default function VideoDetail() {
  const router = useRouter();
  const params = useParams();
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [videoData, setVideoData] = useState(null);
  const [error, setError] = useState(null);
  
  const videoId = params.id;

  // Check if user is authenticated
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const response = await fetch('/api/auth/me', {
          credentials: 'include'
        });
        if (response.ok) {
          const userData = await response.json();
          setUser(userData);
        } else {
          router.push('/login');
        }
      } catch (error) {
        console.error('Authentication check failed:', error);
        router.push('/login');
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, [router]);

  // Fetch video details
  useEffect(() => {
    if (!videoId || isLoading) return;

    const fetchVideoDetails = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/videos/${videoId}`);
        if (response.ok) {
          const data = await response.json();
          setVideoData(data);
        } else {
          setError('Video not found or failed to load');
        }
      } catch (error) {
        console.error('Error fetching video details:', error);
        setError('Failed to load video details');
      }
    };

    fetchVideoDetails();
  }, [videoId, isLoading]);

  const handleLogout = async () => {
    try {
      await fetch('/api/auth/logout', {
        method: 'POST'
      });
      window.location.href = '/login';
    } catch (err) {
      alert('Logout failed');
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="bg-white shadow rounded-lg p-6">
            <div className="mb-6">
              <h1 className="text-3xl font-bold text-gray-900">Video Details</h1>
              <p className="text-gray-600 mt-2">Video ID: {videoId}</p>
            </div>

            {error ? (
              <div className="text-center py-12">
                <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.664-.833-2.464 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Video</h3>
                <p className="text-gray-600 mb-6">{error}</p>
                <button
                  onClick={() => router.push('/dashboard')}
                  className="bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 transition-colors"
                >
                  Back to Dashboard
                </button>
              </div>
            ) : videoData ? (
              <div className="space-y-6">
                <div>
                  <h2 className="text-xl font-semibold text-gray-900 mb-2">{videoData.title}</h2>
                  <p className="text-gray-600">{videoData.description}</p>
                </div>

                {videoData.output_url && (
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-2">Generated Video</h3>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <p className="text-sm text-gray-500 mb-2">Output URL:</p>
                      <a 
                        href={videoData.output_url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-indigo-600 hover:text-indigo-800 break-all"
                      >
                        {videoData.output_url}
                      </a>
                    </div>
                  </div>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-2">Video Information</h3>
                    <dl className="space-y-2">
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Status</dt>
                        <dd className="text-sm text-gray-900">{videoData.status}</dd>
                      </div>
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Duration</dt>
                        <dd className="text-sm text-gray-900">{videoData.duration}s</dd>
                      </div>
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Resolution</dt>
                        <dd className="text-sm text-gray-900">{videoData.resolution}</dd>
                      </div>
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Style</dt>
                        <dd className="text-sm text-gray-900">{videoData.style}</dd>
                      </div>
                    </dl>
                  </div>

                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-2">Creation Details</h3>
                    <dl className="space-y-2">
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Created</dt>
                        <dd className="text-sm text-gray-900">
                          {videoData.created_at ? new Date(videoData.created_at).toLocaleString() : 'N/A'}
                        </dd>
                      </div>
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Updated</dt>
                        <dd className="text-sm text-gray-900">
                          {videoData.updated_at ? new Date(videoData.updated_at).toLocaleString() : 'N/A'}
                        </dd>
                      </div>
                    </dl>
                  </div>
                </div>

                <div className="flex gap-3 pt-6">
                  <button
                    onClick={() => router.push('/dashboard')}
                    className="bg-gray-200 text-gray-800 py-2 px-4 rounded-md hover:bg-gray-300 transition-colors"
                  >
                    Back to Dashboard
                  </button>
                  {videoData.output_url && (
                    <a
                      href={videoData.output_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 transition-colors"
                    >
                      Download Video
                    </a>
                  )}
                </div>
              </div>
            ) : (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto mb-4"></div>
                <p className="text-gray-600">Loading video details...</p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
