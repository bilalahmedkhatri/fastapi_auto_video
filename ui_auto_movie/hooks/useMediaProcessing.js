/**
 * React Hook for Media Processing
 * Manages media upload, processing, and status tracking
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import mediaAPI from '@/lib/mediaAPI';

export const useMediaProcessing = () => {
  // Processing state
  const [isUploading, setIsUploading] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingTasks, setProcessingTasks] = useState(new Map());
  const [processingProgress, setProcessingProgress] = useState(new Map());
  const [processingResults, setProcessingResults] = useState(new Map());
  
  // Polling refs
  const pollingRefs = useRef(new Map());
  const abortControllers = useRef(new Map());

  /**
   * Upload files to backend with optional auto-processing
   */
  const uploadFiles = useCallback(async (files, options = {}) => {
    const {
      userId = null,
      autoProcess = true,
      onProgress = null,
      onComplete = null,
      onError = null
    } = options;

    setIsUploading(true);
    
    try {
      // Convert files to array if needed
      const fileArray = Array.from(files);
      
      // Upload files
      const uploadResponse = await mediaAPI.uploadFiles(fileArray, userId, autoProcess);
      
      toast.success(`Uploaded ${uploadResponse.uploaded_files} file(s) successfully`);
      
      // If auto-processing is enabled and we got a task ID
      if (autoProcess && uploadResponse.processing?.task_id) {
        const taskId = uploadResponse.processing.task_id;
        
        // Start monitoring the processing task
        await startTaskMonitoring(taskId, {
          onProgress,
          onComplete: (result) => {
            toast.success('Media processing completed!');
            if (onComplete) onComplete(result, uploadResponse);
          },
          onError: (error) => {
            toast.error(`Processing failed: ${error.message}`);
            if (onError) onError(error, uploadResponse);
          }
        });
      } else {
        // No auto-processing, just return upload results
        if (onComplete) onComplete(null, uploadResponse);
      }
      
      return uploadResponse;
      
    } catch (error) {
      const errorMessage = error.message || 'Upload failed';
      toast.error(errorMessage);
      if (onError) onError(error);
      throw error;
    } finally {
      setIsUploading(false);
    }
  }, []);

  /**
   * Process media items that are already uploaded
   */
  const processMedia = useCallback(async (mediaItems, options = {}) => {
    const {
      userId = null,
      onProgress = null,
      onComplete = null,
      onError = null
    } = options;

    setIsProcessing(true);

    try {
      let response;
      
      if (Array.isArray(mediaItems) && mediaItems.length > 1) {
        // Batch processing
        response = await mediaAPI.startBatchProcessing(mediaItems, userId);
      } else {
        // Single media processing
        const mediaItem = Array.isArray(mediaItems) ? mediaItems[0] : mediaItems;
        response = await mediaAPI.processSingleMedia(mediaItem, userId);
      }

      const taskId = response.task_id;
      
      // Start monitoring the processing task
      await startTaskMonitoring(taskId, {
        onProgress,
        onComplete: (result) => {
          toast.success('Media processing completed!');
          if (onComplete) onComplete(result);
        },
        onError: (error) => {
          toast.error(`Processing failed: ${error.message}`);
          if (onError) onError(error);
        }
      });

      return response;

    } catch (error) {
      const errorMessage = error.message || 'Processing failed';
      toast.error(errorMessage);
      if (onError) onError(error);
      throw error;
    } finally {
      setIsProcessing(false);
    }
  }, []);

  /**
   * Start monitoring a processing task
   */
  const startTaskMonitoring = useCallback(async (taskId, callbacks = {}) => {
    const { onProgress, onComplete, onError } = callbacks;

    // Create abort controller for this task
    const abortController = new AbortController();
    abortControllers.current.set(taskId, abortController);

    // Add task to processing tasks map
    setProcessingTasks(prev => new Map(prev.set(taskId, {
      id: taskId,
      startTime: Date.now(),
      status: 'PENDING'
    })));

    try {
      // Start polling for task completion
      const result = await mediaAPI.pollTaskCompletion(
        taskId,
        (status) => {
          // Update progress
          setProcessingProgress(prev => new Map(prev.set(taskId, status)));
          
          // Update task status
          setProcessingTasks(prev => {
            const updated = new Map(prev);
            const task = updated.get(taskId);
            if (task) {
              updated.set(taskId, { ...task, status: status.status });
            }
            return updated;
          });
          
          // Call progress callback
          if (onProgress) onProgress(status);
        },
        120, // max attempts
        2000 // 2 second interval
      );

      // Store final results
      setProcessingResults(prev => new Map(prev.set(taskId, result)));
      
      // Call completion callback
      if (onComplete) onComplete(result);
      
      return result;

    } catch (error) {
      // Update task status to failed
      setProcessingTasks(prev => {
        const updated = new Map(prev);
        const task = updated.get(taskId);
        if (task) {
          updated.set(taskId, { ...task, status: 'FAILURE', error: error.message });
        }
        return updated;
      });
      
      if (onError) onError(error);
      throw error;
      
    } finally {
      // Cleanup
      abortControllers.current.delete(taskId);
      pollingRefs.current.delete(taskId);
    }
  }, []);

  /**
   * Cancel a processing task
   */
  const cancelTask = useCallback(async (taskId) => {
    try {
      // Cancel via API
      await mediaAPI.cancelTask(taskId);
      
      // Abort local polling
      const abortController = abortControllers.current.get(taskId);
      if (abortController) {
        abortController.abort();
      }
      
      // Update task status
      setProcessingTasks(prev => {
        const updated = new Map(prev);
        const task = updated.get(taskId);
        if (task) {
          updated.set(taskId, { ...task, status: 'CANCELLED' });
        }
        return updated;
      });
      
      toast.success('Task cancelled successfully');
      
    } catch (error) {
      toast.error(`Failed to cancel task: ${error.message}`);
      throw error;
    }
  }, []);

  /**
   * Get processing status for a task
   */
  const getTaskStatus = useCallback(async (taskId) => {
    try {
      return await mediaAPI.getTaskStatus(taskId);
    } catch (error) {
      console.error('Failed to get task status:', error);
      return null;
    }
  }, []);

  /**
   * Get processing results for a task
   */
  const getTaskResult = useCallback(async (taskId) => {
    try {
      return await mediaAPI.getTaskResult(taskId);
    } catch (error) {
      console.error('Failed to get task result:', error);
      return null;
    }
  }, []);

  /**
   * Generate thumbnails for media items
   */
  const generateThumbnails = useCallback(async (mediaItems, thumbnailSize = [150, 150]) => {
    try {
      const response = await mediaAPI.generateThumbnails(mediaItems, thumbnailSize);
      
      // Start monitoring thumbnail generation task
      const taskId = response.task_id;
      await startTaskMonitoring(taskId, {
        onComplete: (result) => {
          toast.success('Thumbnails generated successfully!');
        },
        onError: (error) => {
          toast.error(`Thumbnail generation failed: ${error.message}`);
        }
      });
      
      return response;
      
    } catch (error) {
      toast.error(`Failed to generate thumbnails: ${error.message}`);
      throw error;
    }
  }, [startTaskMonitoring]);

  /**
   * Clear completed tasks from state
   */
  const clearCompletedTasks = useCallback(() => {
    setProcessingTasks(prev => {
      const updated = new Map();
      prev.forEach((task, id) => {
        if (!['SUCCESS', 'FAILURE', 'CANCELLED'].includes(task.status)) {
          updated.set(id, task);
        }
      });
      return updated;
    });
    
    // Clear associated progress and results for completed tasks
    setProcessingProgress(prev => {
      const updated = new Map();
      processingTasks.forEach((task, id) => {
        if (!['SUCCESS', 'FAILURE', 'CANCELLED'].includes(task.status) && prev.has(id)) {
          updated.set(id, prev.get(id));
        }
      });
      return updated;
    });
  }, [processingTasks]);

  /**
   * Get processing statistics
   */
  const getProcessingStats = useCallback(() => {
    const tasks = Array.from(processingTasks.values());
    
    return {
      total: tasks.length,
      pending: tasks.filter(t => t.status === 'PENDING').length,
      processing: tasks.filter(t => ['STARTED', 'PROCESSING'].includes(t.status)).length,
      completed: tasks.filter(t => t.status === 'SUCCESS').length,
      failed: tasks.filter(t => t.status === 'FAILURE').length,
      cancelled: tasks.filter(t => t.status === 'CANCELLED').length
    };
  }, [processingTasks]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      // Abort all active requests
      abortControllers.current.forEach(controller => {
        controller.abort();
      });
      abortControllers.current.clear();
      pollingRefs.current.clear();
    };
  }, []);

  return {
    // States
    isUploading,
    isProcessing,
    processingTasks,
    processingProgress,
    processingResults,
    
    // Actions
    uploadFiles,
    processMedia,
    startTaskMonitoring,
    cancelTask,
    generateThumbnails,
    clearCompletedTasks,
    
    // Getters
    getTaskStatus,
    getTaskResult,
    getProcessingStats
  };
};

export default useMediaProcessing;