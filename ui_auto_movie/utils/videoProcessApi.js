/**
 * Video Process API Helper Functions
 * 
 * This module provides helper functions for interacting with the video process backend API.
 * Handles all HTTP requests to the video process endpoints with proper error handling.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Generic API request function with error handling
 */
async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  };

  const config = {
    ...defaultOptions,
    ...options,
  };

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.detail || 
        errorData.message || 
        `HTTP ${response.status}: ${response.statusText}`
      );
    }
    
    return await response.json();
  } catch (error) {
    console.error(`API Request failed for ${endpoint}:`, error);
    throw error;
  }
}

/**
 * Start a new video generation process
 * @param {Object} processData - The video generation request data
 * @returns {Promise<Object>} Process creation response
 */
export async function startVideoProcess(processData) {
  return apiRequest('/api/video-process/start', {
    method: 'POST',
    body: JSON.stringify(processData),
  });
}

/**
 * Get the status of a video generation process
 * @param {number} processId - The process ID
 * @returns {Promise<Object>} Process status
 */
export async function getProcessStatus(processId) {
  return apiRequest(`/api/video-process/${processId}/status`);
}

/**
 * Pause a running video process
 * @param {number} processId - The process ID
 * @param {string} userId - User performing the action
 * @param {string} reason - Reason for pausing
 * @returns {Promise<Object>} Response
 */
export async function pauseVideoProcess(processId, userId, reason = '') {
  return apiRequest(`/api/video-process/${processId}/pause`, {
    method: 'POST',
    body: JSON.stringify({ user_id: userId, reason }),
  });
}

/**
 * Resume a paused video process
 * @param {number} processId - The process ID
 * @param {string} userId - User performing the action
 * @returns {Promise<Object>} Response
 */
export async function resumeVideoProcess(processId, userId) {
  return apiRequest(`/api/video-process/${processId}/resume`, {
    method: 'POST',
    body: JSON.stringify({ user_id: userId }),
  });
}

/**
 * Retry a failed step in a video process
 * @param {number} processId - The process ID
 * @param {string} stepName - The step to retry
 * @param {string} userId - User performing the action
 * @param {string} reason - Reason for retry
 * @returns {Promise<Object>} Response
 */
export async function retryProcessStep(processId, stepName, userId, reason = '') {
  return apiRequest(`/api/video-process/${processId}/retry/${stepName}`, {
    method: 'POST',
    body: JSON.stringify({ user_id: userId, reason }),
  });
}

/**
 * Cancel a video process
 * @param {number} processId - The process ID
 * @param {string} userId - User performing the action
 * @returns {Promise<Object>} Response
 */
export async function cancelVideoProcess(processId, userId) {
  return apiRequest(`/api/video-process/${processId}?user_id=${userId}`, {
    method: 'DELETE',
  });
}

/**
 * Get all video processes for a user
 * @param {string} userId - The user ID
 * @param {number} limit - Number of processes to retrieve
 * @param {string} status - Filter by status (optional)
 * @returns {Promise<Object>} User processes
 */
export async function getUserProcesses(userId, limit = 10, status = null) {
  let endpoint = `/api/video-process/user/${userId}?limit=${limit}`;
  if (status) {
    endpoint += `&status=${status}`;
  }
  return apiRequest(endpoint);
}

/**
 * Get process analytics summary
 * @returns {Promise<Object>} Analytics data
 */
export async function getProcessAnalytics() {
  return apiRequest('/api/video-process/analytics/summary');
}

/**
 * Create WebSocket URL for a process
 * @param {number} processId - The process ID
 * @returns {string} WebSocket URL
 */
export function getWebSocketUrl(processId) {
  const wsBase = API_BASE_URL.replace('http', 'ws');
  return `${wsBase}/api/video-process/ws/${processId}`;
}

/**
 * Validate process data before sending to API
 * @param {Object} processData - Process data to validate
 * @returns {Object} Validation result
 */
export function validateProcessData(processData) {
  const errors = [];
  
  if (!processData.user_id || processData.user_id.trim() === '') {
    errors.push('User ID is required');
  }
  
  if (!processData.prompt || processData.prompt.trim() === '') {
    errors.push('Prompt is required');
  }
  
  if (processData.prompt && processData.prompt.length > 2000) {
    errors.push('Prompt must be less than 2000 characters');
  }
  
  const validPriorities = ['low', 'normal', 'high'];
  if (processData.priority && !validPriorities.includes(processData.priority)) {
    errors.push('Invalid priority level');
  }
  
  const validDurations = ['short', 'medium', 'long'];
  if (processData.duration && !validDurations.includes(processData.duration)) {
    errors.push('Invalid duration setting');
  }
  
  return {
    isValid: errors.length === 0,
    errors,
  };
}

/**
 * Format process data for API request
 * @param {Object} formData - Raw form data
 * @param {string} userId - User ID
 * @param {string} sessionId - Session ID (optional)
 * @returns {Object} Formatted process data
 */
export function formatProcessData(formData, userId, sessionId = null) {
  return {
    user_id: userId,
    prompt: formData.userPrompt || formData.prompt || '',
    category: formData.category || 'General',
    language: formData.language || 'English',
    duration: formData.duration || 'medium',
    priority: formData.priority || 'normal',
    session_id: sessionId,
    additional_settings: {
      script_types: formData.scriptTypes || ['short', 'medium', 'long'],
      voice_settings: formData.audioSettings || {},
      social_platforms: formData.selectedPlatforms || ['youtube', 'instagram', 'tiktok'],
      ...formData.additional_settings,
    },
  };
}

/**
 * Error handling helper for API responses
 * @param {Error} error - The error object
 * @returns {Object} Formatted error information
 */
export function handleApiError(error) {
  console.error('API Error:', error);
  
  return {
    message: error.message || 'An unexpected error occurred',
    type: error.name || 'ApiError',
    code: error.status || 'UNKNOWN_ERROR',
    timestamp: new Date().toISOString(),
  };
}

/**
 * Check if the API is available
 * @returns {Promise<boolean>} API availability
 */
export async function checkApiHealth() {
  try {
    await fetch(`${API_BASE_URL}/`);
    return true;
  } catch (error) {
    console.warn('API health check failed:', error);
    return false;
  }
}

export default {
  startVideoProcess,
  getProcessStatus,
  pauseVideoProcess,
  resumeVideoProcess,
  retryProcessStep,
  cancelVideoProcess,
  getUserProcesses,
  getProcessAnalytics,
  getWebSocketUrl,
  validateProcessData,
  formatProcessData,
  handleApiError,
  checkApiHealth,
};