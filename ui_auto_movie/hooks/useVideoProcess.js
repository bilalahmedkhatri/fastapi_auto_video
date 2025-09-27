/**
 * Video Process Management Hook
 * 
 * This hook provides a comprehensive interface for managing video generation processes.
 * It handles process creation, monitoring, control operations (pause/resume/cancel),
 * and integrates with WebSocket for real-time updates.
 */

import { useState, useCallback, useEffect, useRef } from 'react';
import { useProcessUpdates } from './useWebSocket';
import {
  startVideoProcess,
  getProcessStatus,
  pauseVideoProcess,
  resumeVideoProcess,
  retryProcessStep,
  cancelVideoProcess,
  getUserProcesses,
  validateProcessData,
  formatProcessData,
  handleApiError,
} from '../utils/videoProcessApi';

// Process states
const PROCESS_STATES = {
  IDLE: 'idle',
  STARTING: 'starting',
  RUNNING: 'running',
  PAUSED: 'paused',
  COMPLETED: 'completed',
  FAILED: 'failed',
  CANCELLED: 'cancelled',
};

// Process steps mapping
const PROCESS_STEPS = {
  INPUT_PROCESSING: 'input_processing',
  SCRIPT_GENERATION: 'script_generation',
  VOICEOVER_GENERATION: 'voiceover_generation',
  SOCIAL_MEDIA_CONTENT: 'social_media_content',
  MEDIA_COLLECTION: 'media_collection',
  EFFECTS_PROCESSING: 'effects_processing',
  FINAL_ASSEMBLY: 'final_assembly',
};

/**
 * Custom hook for video process management
 * @param {string} userId - User ID for process ownership
 * @param {Object} options - Configuration options
 * @returns {Object} Process management interface
 */
export function useVideoProcess(userId, options = {}) {
  const {
    autoStart = false,
    pollingInterval = 5000,
    enableWebSocket = true,
    onProcessComplete,
    onProcessError,
    onStepChange,
  } = options;

  // Process state
  const [currentProcess, setCurrentProcess] = useState(null);
  const [processState, setProcessState] = useState(PROCESS_STATES.IDLE);
  const [currentStep, setCurrentStep] = useState(null);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  
  // Process history and management
  const [processHistory, setProcessHistory] = useState([]);
  const [retryCount, setRetryCount] = useState(0);
  const pollingTimeoutRef = useRef(null);
  const processStartTimeRef = useRef(null);

  // WebSocket integration for real-time updates
  const {
    processUpdate,
    isConnected: wsConnected,
    error: wsError,
  } = useProcessUpdates(currentProcess?.id, { enabled: enableWebSocket });

  /**
   * Clear polling timeout
   */
  const clearPolling = useCallback(() => {
    if (pollingTimeoutRef.current) {
      clearTimeout(pollingTimeoutRef.current);
      pollingTimeoutRef.current = null;
    }
  }, []);

  /**
   * Start polling for process status
   */
  const startPolling = useCallback(() => {
    if (!currentProcess?.id || wsConnected) {
      return; // Skip polling if WebSocket is connected
    }

    clearPolling();
    pollingTimeoutRef.current = setTimeout(async () => {
      try {
        const status = await getProcessStatus(currentProcess.id);
        updateProcessState(status);
        
        // Continue polling if process is still running
        if (status.status === 'running' || status.status === 'paused') {
          startPolling();
        }
      } catch (error) {
        console.error('Polling error:', error);
        // Continue polling on error, but with longer interval
        pollingTimeoutRef.current = setTimeout(startPolling, pollingInterval * 2);
      }
    }, pollingInterval);
  }, [currentProcess?.id, wsConnected, pollingInterval, clearPolling]);

  /**
   * Update process state from status data
   */
  const updateProcessState = useCallback((statusData) => {
    setProcessState(statusData.status || PROCESS_STATES.IDLE);
    setCurrentStep(statusData.current_step);
    setProgress(statusData.progress || 0);
    
    if (statusData.error) {
      setError({
        message: statusData.error,
        step: statusData.current_step,
        timestamp: new Date().toISOString(),
      });
    } else {
      setError(null);
    }

    // Trigger step change callback
    if (onStepChange && statusData.current_step !== currentStep) {
      onStepChange(statusData.current_step, statusData);
    }

    // Check for completion or failure
    if (statusData.status === 'completed' && onProcessComplete) {
      onProcessComplete(statusData);
    } else if (statusData.status === 'failed' && onProcessError) {
      onProcessError(statusData);
    }
  }, [currentStep, onStepChange, onProcessComplete, onProcessError]);

  /**
   * Handle WebSocket updates
   */
  useEffect(() => {
    if (processUpdate && currentProcess?.id === processUpdate.processId) {
      updateProcessState({
        status: processUpdate.status,
        current_step: processUpdate.currentStep,
        progress: processUpdate.progress,
        message: processUpdate.message,
        step_details: processUpdate.stepDetails,
      });
    }
  }, [processUpdate, currentProcess?.id, updateProcessState]);

  /**
   * Start a new video generation process
   */
  const startProcess = useCallback(async (formData, sessionId = null) => {
    if (!userId) {
      throw new Error('User ID is required to start process');
    }

    setIsLoading(true);
    setError(null);

    try {
      // Format and validate process data
      const processData = formatProcessData(formData, userId, sessionId);
      const validation = validateProcessData(processData);
      
      if (!validation.isValid) {
        throw new Error(`Validation failed: ${validation.errors.join(', ')}`);
      }

      console.log('Starting video process with data:', processData);
      
      // Start the process
      const response = await startVideoProcess(processData);
      
      setCurrentProcess({
        id: response.process_id,
        ...processData,
        started_at: new Date().toISOString(),
      });
      
      setProcessState(PROCESS_STATES.STARTING);
      setRetryCount(0);
      processStartTimeRef.current = Date.now();
      
      // Add to history
      setProcessHistory(prev => [response, ...prev.slice(0, 9)]); // Keep last 10
      
      // Start monitoring if WebSocket is not available
      if (!enableWebSocket) {
        startPolling();
      }

      return response;
    } catch (error) {
      const formattedError = handleApiError(error);
      setError(formattedError);
      setProcessState(PROCESS_STATES.FAILED);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [userId, enableWebSocket, startPolling]);

  /**
   * Pause the current process
   */
  const pauseProcess = useCallback(async (reason = '') => {
    if (!currentProcess?.id) {
      throw new Error('No active process to pause');
    }

    setIsLoading(true);
    try {
      const response = await pauseVideoProcess(currentProcess.id, userId, reason);
      setProcessState(PROCESS_STATES.PAUSED);
      clearPolling();
      return response;
    } catch (error) {
      const formattedError = handleApiError(error);
      setError(formattedError);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [currentProcess?.id, userId, clearPolling]);

  /**
   * Resume the current paused process
   */
  const resumeProcess = useCallback(async () => {
    if (!currentProcess?.id) {
      throw new Error('No process to resume');
    }

    setIsLoading(true);
    try {
      const response = await resumeVideoProcess(currentProcess.id, userId);
      setProcessState(PROCESS_STATES.RUNNING);
      
      // Restart monitoring if needed
      if (!enableWebSocket) {
        startPolling();
      }
      
      return response;
    } catch (error) {
      const formattedError = handleApiError(error);
      setError(formattedError);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [currentProcess?.id, userId, enableWebSocket, startPolling]);

  /**
   * Cancel the current process
   */
  const cancelProcess = useCallback(async () => {
    if (!currentProcess?.id) {
      throw new Error('No active process to cancel');
    }

    setIsLoading(true);
    try {
      const response = await cancelVideoProcess(currentProcess.id, userId);
      setProcessState(PROCESS_STATES.CANCELLED);
      setCurrentProcess(null);
      setCurrentStep(null);
      setProgress(0);
      clearPolling();
      return response;
    } catch (error) {
      const formattedError = handleApiError(error);
      setError(formattedError);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [currentProcess?.id, userId, clearPolling]);

  /**
   * Retry a failed step
   */
  const retryStep = useCallback(async (stepName = null, reason = '') => {
    if (!currentProcess?.id) {
      throw new Error('No process to retry');
    }

    const targetStep = stepName || currentStep;
    if (!targetStep) {
      throw new Error('No step specified for retry');
    }

    setIsLoading(true);
    try {
      const response = await retryProcessStep(currentProcess.id, targetStep, userId, reason);
      setRetryCount(prev => prev + 1);
      setError(null);
      
      // Restart monitoring if needed
      if (!enableWebSocket) {
        startPolling();
      }
      
      return response;
    } catch (error) {
      const formattedError = handleApiError(error);
      setError(formattedError);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [currentProcess?.id, currentStep, userId, enableWebSocket, startPolling]);

  /**
   * Load user's process history
   */
  const loadProcessHistory = useCallback(async (limit = 10) => {
    if (!userId) return;

    try {
      const response = await getUserProcesses(userId, limit);
      setProcessHistory(response.processes || []);
    } catch (error) {
      console.error('Failed to load process history:', error);
    }
  }, [userId]);

  /**
   * Reset process state
   */
  const resetProcess = useCallback(() => {
    setCurrentProcess(null);
    setProcessState(PROCESS_STATES.IDLE);
    setCurrentStep(null);
    setProgress(0);
    setError(null);
    setRetryCount(0);
    clearPolling();
    processStartTimeRef.current = null;
  }, [clearPolling]);

  /**
   * Get process duration
   */
  const getProcessDuration = useCallback(() => {
    if (!processStartTimeRef.current) return 0;
    return Date.now() - processStartTimeRef.current;
  }, []);

  /**
   * Check if process can be controlled
   */
  const canControl = useCallback((action) => {
    switch (action) {
      case 'pause':
        return processState === PROCESS_STATES.RUNNING && !isLoading;
      case 'resume':
        return processState === PROCESS_STATES.PAUSED && !isLoading;
      case 'cancel':
        return [PROCESS_STATES.RUNNING, PROCESS_STATES.PAUSED, PROCESS_STATES.STARTING].includes(processState) && !isLoading;
      case 'retry':
        return processState === PROCESS_STATES.FAILED && !isLoading;
      default:
        return false;
    }
  }, [processState, isLoading]);

  // Load process history on mount
  useEffect(() => {
    if (userId) {
      loadProcessHistory();
    }
  }, [userId, loadProcessHistory]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      clearPolling();
    };
  }, [clearPolling]);

  // Auto-start if configured and data provided
  useEffect(() => {
    if (autoStart && userId && !currentProcess) {
      // Auto-start logic would go here if needed
    }
  }, [autoStart, userId, currentProcess]);

  return {
    // Process state
    currentProcess,
    processState,
    currentStep,
    progress,
    error,
    isLoading,
    retryCount,
    processHistory,
    
    // WebSocket state
    wsConnected,
    wsError,
    
    // Actions
    startProcess,
    pauseProcess,
    resumeProcess,
    cancelProcess,
    retryStep,
    resetProcess,
    loadProcessHistory,
    
    // Utilities
    getProcessDuration,
    canControl,
    
    // Constants
    PROCESS_STATES,
    PROCESS_STEPS,
    
    // Computed state
    isActive: [PROCESS_STATES.STARTING, PROCESS_STATES.RUNNING, PROCESS_STATES.PAUSED].includes(processState),
    isCompleted: processState === PROCESS_STATES.COMPLETED,
    isFailed: processState === PROCESS_STATES.FAILED,
    isCancelled: processState === PROCESS_STATES.CANCELLED,
    hasError: Boolean(error),
  };
}

export default useVideoProcess;