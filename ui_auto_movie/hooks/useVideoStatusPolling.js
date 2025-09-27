'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { toast } from 'react-hot-toast';

/**
 * Enhanced hook for tracking video generation progress with detailed status updates
 */
export const useVideoStatusPolling = () => {
  const [status, setStatus] = useState({
    isActive: false,
    progress: 0,
    stage: null,
    stageName: '',
    statusMessage: '',
    stepDetails: {},
    currentStep: 0,
    totalSteps: 10,
    estimatedTimeRemaining: null,
    elapsedTime: 0,
    error: null,
    videoId: null,
    taskId: null,
    outputUrl: null
  });

  const intervalRef = useRef(null);
  const startTimeRef = useRef(null);
  const onCompleteRef = useRef(null);
  const onErrorRef = useRef(null);

  // Configure callbacks
  const setCallbacks = useCallback((onComplete, onError) => {
    onCompleteRef.current = onComplete;
    onErrorRef.current = onError;
  }, []);

  // Adaptive polling intervals based on current stage
  const getPollingInterval = useCallback((stage) => {
    const intervals = {
      'initializing': 2000,           // 2 seconds - fast updates
      'script_generation': 3000,      // 3 seconds
      'voiceover_generation': 4000,   // 4 seconds - slower process  
      'social_media_generation': 3000, // 3 seconds
      'media_selection': 4000,        // 4 seconds
      'video_assembly': 3000,         // 3 seconds
      'rendering': 2000,              // 2 seconds - final steps
      'completed': 0,                 // Stop polling
      'failed': 0                     // Stop polling
    };
    return intervals[stage] || 5000;  // Default 5 seconds
  }, []);

  // Calculate elapsed time
  useEffect(() => {
    if (status.isActive && startTimeRef.current) {
      const timer = setInterval(() => {
        setStatus(prev => ({
          ...prev,
          elapsedTime: Math.floor((Date.now() - startTimeRef.current) / 1000)
        }));
      }, 1000);

      return () => clearInterval(timer);
    }
  }, [status.isActive]);

  // Estimate remaining time based on stage and progress
  const estimateRemainingTime = useCallback((stage, currentStep, totalSteps) => {
    const stageEstimates = {
      'initializing': 15,
      'script_generation': 30,
      'voiceover_generation': 60,
      'social_media_generation': 20,
      'media_selection': 45,
      'video_assembly': 90,
      'rendering': 60
    };

    const baseEstimate = stageEstimates[stage] || 30;
    const progressRatio = currentStep / totalSteps;
    const remaining = baseEstimate * (1 - progressRatio);
    
    return Math.max(remaining, 5); // Minimum 5 seconds
  }, []);

  // Poll for status updates
  const pollStatus = useCallback(async (videoId, endpoint) => {
    try {
      const url = endpoint || `http://localhost:8000/api/videos/${videoId}/processing-status`;
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      const newStatus = {
        isActive: true,
        progress: data.progress_percentage || 0,
        stage: data.stage || 'processing',
        stageName: data.stage_name || 'Processing',
        statusMessage: data.status || 'Processing video...',
        stepDetails: data.step_details || {},
        currentStep: data.current_step || 0,
        totalSteps: data.total_steps || 10,
        estimatedTimeRemaining: estimateRemainingTime(data.stage, data.current_step, data.total_steps),
        elapsedTime: startTimeRef.current ? Math.floor((Date.now() - startTimeRef.current) / 1000) : 0,
        error: data.error || null,
        videoId: videoId,
        taskId: data.task_id || null,
        outputUrl: data.output_url || null,
        lastUpdated: new Date().toISOString()
      };

      setStatus(newStatus);

      // Handle completion
      if (data.stage === 'completed' || data.status?.includes('completed')) {
        stopPolling();
        toast.success('🎉 Video generation completed!');
        
        if (onCompleteRef.current) {
          onCompleteRef.current({
            videoId: videoId,
            outputUrl: data.output_url,
            taskId: data.task_id,
            totalTime: newStatus.elapsedTime,
            ...data
          });
        }
        return;
      }

      // Handle errors
      if (data.stage === 'failed' || data.error) {
        stopPolling();
        const errorMessage = data.error || 'Video generation failed';
        toast.error(`❌ ${errorMessage}`);
        
        setStatus(prev => ({
          ...prev,
          isActive: false,
          error: errorMessage
        }));

        if (onErrorRef.current) {
          onErrorRef.current(new Error(errorMessage));
        }
        return;
      }

      // Schedule next poll with adaptive interval
      const nextInterval = getPollingInterval(data.stage);
      if (nextInterval > 0) {
        intervalRef.current = setTimeout(() => pollStatus(videoId, endpoint), nextInterval);
      }

    } catch (error) {
      console.error('Error polling video status:', error);
      
      // Retry with backoff on network errors
      const retryInterval = Math.min(intervalRef.current * 1.5 || 5000, 15000);
      intervalRef.current = setTimeout(() => pollStatus(videoId, endpoint), retryInterval);
    }
  }, [estimateRemainingTime, getPollingInterval]);

  // Start polling
  const startPolling = useCallback((videoId, statusEndpoint = null, callbacks = {}) => {
    if (status.isActive) {
      console.warn('Polling already active');
      return;
    }

    console.log(`🚀 Starting status polling for video: ${videoId}`);
    
    // Set callbacks
    if (callbacks.onComplete) onCompleteRef.current = callbacks.onComplete;
    if (callbacks.onError) onErrorRef.current = callbacks.onError;
    
    // Initialize
    startTimeRef.current = Date.now();
    setStatus({
      isActive: true,
      progress: 0,
      stage: 'initializing',
      stageName: 'Initializing',
      statusMessage: 'Starting video generation...',
      stepDetails: {},
      currentStep: 0,
      totalSteps: 10,
      estimatedTimeRemaining: 60,
      elapsedTime: 0,
      error: null,
      videoId: videoId,
      taskId: null,
      outputUrl: null,
      lastUpdated: new Date().toISOString()
    });

    // Start polling
    pollStatus(videoId, statusEndpoint);
    
    toast.success('📹 Video generation started!');
  }, [status.isActive, pollStatus]);

  // Stop polling
  const stopPolling = useCallback(() => {
    if (intervalRef.current) {
      clearTimeout(intervalRef.current);
      intervalRef.current = null;
    }
    
    setStatus(prev => ({
      ...prev,
      isActive: false
    }));
    
    console.log('⏹️ Status polling stopped');
  }, []);

  // Reset status
  const resetStatus = useCallback(() => {
    stopPolling();
    setStatus({
      isActive: false,
      progress: 0,
      stage: null,
      stageName: '',
      statusMessage: '',
      stepDetails: {},
      currentStep: 0,
      totalSteps: 10,
      estimatedTimeRemaining: null,
      elapsedTime: 0,
      error: null,
      videoId: null,
      taskId: null,
      outputUrl: null
    });
    startTimeRef.current = null;
  }, [stopPolling]);

  // Format time helper
  const formatTime = useCallback((seconds) => {
    if (seconds < 60) return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearTimeout(intervalRef.current);
      }
    };
  }, []);

  return {
    // Status data
    status,
    
    // Computed values
    isPolling: status.isActive,
    isCompleted: status.stage === 'completed',
    isFailed: status.stage === 'failed' || !!status.error,
    
    // Actions
    startPolling,
    stopPolling,
    resetStatus,
    setCallbacks,
    
    // Helpers
    formatTime,
    
    // Progress indicators
    progressPercentage: status.progress,
    currentStage: status.stage,
    stageDisplayName: status.stageName,
    statusMessage: status.statusMessage,
    timeElapsed: status.elapsedTime,
    timeRemaining: status.estimatedTimeRemaining
  };
};

export default useVideoStatusPolling;