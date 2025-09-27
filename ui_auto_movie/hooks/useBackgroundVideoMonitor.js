'use client';

import { useEffect, useState } from 'react';
import { toast } from 'react-hot-toast';
import { useRouter } from 'next/navigation';
import { notificationManager } from '../lib/videoNotifications';

/**
 * Background Video Job Monitor
 * Checks for videos that were set to generate in background
 */
export const useBackgroundVideoMonitor = () => {
  const router = useRouter();
  const [backgroundJobs, setBackgroundJobs] = useState([]);
  const [isMonitoring, setIsMonitoring] = useState(false);

  useEffect(() => {
    startMonitoring();
    return () => stopMonitoring();
  }, []);

  const startMonitoring = () => {
    if (isMonitoring) return;
    
    setIsMonitoring(true);
    
    // Check immediately
    checkBackgroundJobs();
    
    // Then check every 30 seconds
    const interval = setInterval(() => {
      checkBackgroundJobs();
    }, 30000);

    return () => clearInterval(interval);
  };

  const stopMonitoring = () => {
    setIsMonitoring(false);
  };

  const checkBackgroundJobs = async () => {
    try {
      const jobs = JSON.parse(localStorage.getItem('backgroundVideoJobs') || '[]');
      if (jobs.length === 0) return;

      console.log(`🔍 Checking ${jobs.length} background video jobs...`);
      
      const updatedJobs = [];
      const completedJobs = [];

      for (const job of jobs) {
        try {
          const response = await fetch(`http://localhost:8000/api/videos/${job.videoId}/processing-status`);
          
          if (response.ok) {
            const status = await response.json();
            
            if (status.stage === 'completed') {
              completedJobs.push({...job, status});
            } else if (status.stage === 'failed') {
              // Remove failed jobs and notify
              toast.error(`Background video "${job.initialData?.script_data?.title || 'Unknown'}" failed to generate`);
            } else {
              // Still processing
              updatedJobs.push(job);
            }
          } else {
            // Keep job if we can't check status
            updatedJobs.push(job);
          }
        } catch (error) {
          // Keep job on error
          updatedJobs.push(job);
        }
      }

      // Update localStorage with remaining jobs
      localStorage.setItem('backgroundVideoJobs', JSON.stringify(updatedJobs));
      setBackgroundJobs(updatedJobs);

      // Handle completed jobs
      if (completedJobs.length > 0) {
        handleCompletedJobs(completedJobs);
      }

    } catch (error) {
      console.error('Error checking background jobs:', error);
    }
  };

  const handleCompletedJobs = async (completedJobs) => {
    for (const job of completedJobs) {
      try {
        const title = job.initialData?.script_data?.title || 'Your Video';
        
        // Try to get additional video metadata
        let videoData = {
          videoId: job.videoId,
          title: title,
          thumbnail: null,
          duration: null
        };

        try {
          const response = await fetch(`http://localhost:8000/api/videos/${job.videoId}`);
          if (response.ok) {
            const metadata = await response.json();
            videoData = {
              ...videoData,
              thumbnail: metadata.thumbnail_url,
              duration: metadata.duration,
              title: metadata.title || title
            };
          }
        } catch (error) {
          console.log('Could not fetch video metadata:', error);
        }

        // Use notification manager for consistent notifications
        notificationManager.showCompletionNotification(videoData);
        
      } catch (error) {
        console.error('Error handling completed job:', error);
      }
    }
  };

  const clearBackgroundJobs = () => {
    localStorage.removeItem('backgroundVideoJobs');
    setBackgroundJobs([]);
  };

  const removeJob = (videoId) => {
    const jobs = JSON.parse(localStorage.getItem('backgroundVideoJobs') || '[]');
    const filteredJobs = jobs.filter(job => job.videoId !== videoId);
    localStorage.setItem('backgroundVideoJobs', JSON.stringify(filteredJobs));
    setBackgroundJobs(filteredJobs);
  };

  return {
    backgroundJobs,
    isMonitoring,
    clearBackgroundJobs,
    removeJob,
    checkBackgroundJobs: () => checkBackgroundJobs()
  };
};

/**
 * Background Video Job Indicator Component
 * Shows active background jobs to user
 */
export const BackgroundJobsIndicator = () => {
  const { backgroundJobs, clearBackgroundJobs } = useBackgroundVideoMonitor();

  if (backgroundJobs.length === 0) return null;

  return (
    <div className="fixed top-4 right-4 bg-blue-500 text-white rounded-lg shadow-lg p-4 max-w-sm z-50">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
          <span className="font-semibold text-sm">Background Jobs</span>
        </div>
        <button
          onClick={clearBackgroundJobs}
          className="text-white hover:text-gray-200 text-xs"
        >
          Clear All
        </button>
      </div>
      
      <div className="space-y-2">
        {backgroundJobs.map((job, index) => (
          <div key={job.videoId} className="bg-blue-600 rounded p-2 text-xs">
            <div className="font-medium">
              {job.initialData?.script_data?.title || `Video ${index + 1}`}
            </div>
            <div className="text-blue-200">
              Started: {new Date(job.startedAt).toLocaleTimeString()}
            </div>
          </div>
        ))}
      </div>
      
      <div className="text-xs text-blue-200 mt-2">
        We'll notify you when videos are ready!
      </div>
    </div>
  );
};

/**
 * Request notification permissions on app load
 */
export const requestNotificationPermission = () => {
  if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission().then(permission => {
      if (permission === 'granted') {
        console.log('✅ Notification permission granted');
      }
    });
  }
};

export default useBackgroundVideoMonitor;