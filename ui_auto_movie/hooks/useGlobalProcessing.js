'use client';

import { useState, useEffect, useCallback } from 'react';

export const useGlobalProcessing = () => {
  const [activeProcessing, setActiveProcessing] = useState(null);

  // Function to start tracking a new processing job
  const startProcessing = useCallback((videoId, taskId) => {
    const processingData = {
      videoId,
      taskId,
      startedAt: new Date().toISOString()
    };

    localStorage.setItem(`processing_${videoId}`, JSON.stringify(processingData));

    setActiveProcessing(processingData);
  }, []);

  // Function to stop tracking a processing job
  const stopProcessing = useCallback((videoId) => {
    localStorage.removeItem(`processing_${videoId}`);
    setActiveProcessing(null);
  }, []);

  // Function to check for existing processing jobs
  const checkExistingProcessing = useCallback(() => {
    const processingJobs = Object.keys(localStorage).filter(key => 
      key.startsWith('processing_')
    );
    
    if (processingJobs.length > 0) {
      const latestJobKey = processingJobs[processingJobs.length - 1];
      const jobData = JSON.parse(localStorage.getItem(latestJobKey) || '{}');
      setActiveProcessing(jobData);
      return jobData;
    }
    
    setActiveProcessing(null);
    return null;
  }, []);

  // Check for existing processing on mount
  useEffect(() => {
    checkExistingProcessing();
  }, [checkExistingProcessing]);

  // Listen for localStorage changes (for cross-tab communication)
  useEffect(() => {
    const handleStorageChange = (e) => {
      if (e.key && e.key.startsWith('processing_')) {
        checkExistingProcessing();
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, [checkExistingProcessing]);

  return {
    activeProcessing,
    startProcessing,
    stopProcessing,
    checkExistingProcessing
  };
};
