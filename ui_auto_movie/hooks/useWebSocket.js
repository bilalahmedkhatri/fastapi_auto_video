/**
 * WebSocket Hook for Real-time Video Process Updates
 * 
 * This hook manages WebSocket connections to receive real-time updates
 * from the video generation backend. Handles connection lifecycle,
 * message parsing, and automatic reconnection.
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import { getWebSocketUrl } from '../utils/videoProcessApi';

// WebSocket connection states
const WS_STATES = {
  CONNECTING: 'connecting',
  CONNECTED: 'connected',
  DISCONNECTED: 'disconnected',
  ERROR: 'error',
  RECONNECTING: 'reconnecting',
};

// Default configuration
const DEFAULT_CONFIG = {
  reconnectInterval: 3000,
  maxReconnectAttempts: 5,
  heartbeatInterval: 30000,
  debug: false,
};

/**
 * Custom hook for managing WebSocket connections to video process updates
 * @param {number} processId - The video process ID to monitor
 * @param {Object} options - Configuration options
 * @returns {Object} WebSocket connection state and utilities
 */
export function useWebSocket(processId, options = {}) {
  const config = { ...DEFAULT_CONFIG, ...options };
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const heartbeatTimeoutRef = useRef(null);
  const reconnectAttemptsRef = useRef(0);
  const mountedRef = useRef(true);

  // Connection state
  const [connectionState, setConnectionState] = useState(WS_STATES.DISCONNECTED);
  const [lastMessage, setLastMessage] = useState(null);
  const [error, setError] = useState(null);
  const [connectionInfo, setConnectionInfo] = useState({
    connectedAt: null,
    reconnectAttempts: 0,
    totalMessages: 0,
  });

  /**
   * Log debug messages if debug mode is enabled
   */
  const debugLog = useCallback((...args) => {
    if (config.debug) {
      console.log('[useWebSocket]', ...args);
    }
  }, [config.debug]);

  /**
   * Clear all timeouts and intervals
   */
  const clearTimeouts = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (heartbeatTimeoutRef.current) {
      clearTimeout(heartbeatTimeoutRef.current);
      heartbeatTimeoutRef.current = null;
    }
  }, []);

  /**
   * Start heartbeat to keep connection alive
   */
  const startHeartbeat = useCallback(() => {
    if (heartbeatTimeoutRef.current) {
      clearTimeout(heartbeatTimeoutRef.current);
    }
    
    heartbeatTimeoutRef.current = setTimeout(() => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        debugLog('Sending heartbeat ping');
        wsRef.current.send(JSON.stringify({ type: 'ping' }));
        startHeartbeat();
      }
    }, config.heartbeatInterval);
  }, [config.heartbeatInterval, debugLog]);

  /**
   * Handle incoming WebSocket messages
   */
  const handleMessage = useCallback((event) => {
    if (!mountedRef.current) return;

    try {
      const data = JSON.parse(event.data);
      debugLog('Received message:', data);
      
      // Handle pong responses
      if (data.type === 'pong') {
        debugLog('Received heartbeat pong');
        return;
      }
      
      // Update message state
      setLastMessage({
        ...data,
        timestamp: new Date().toISOString(),
      });
      
      // Update connection info
      setConnectionInfo(prev => ({
        ...prev,
        totalMessages: prev.totalMessages + 1,
      }));
      
    } catch (error) {
      console.error('Failed to parse WebSocket message:', error);
      debugLog('Parse error for message:', event.data);
    }
  }, [debugLog]);

  /**
   * Handle WebSocket connection open
   */
  const handleOpen = useCallback(() => {
    if (!mountedRef.current) return;

    debugLog('WebSocket connection opened');
    setConnectionState(WS_STATES.CONNECTED);
    setError(null);
    reconnectAttemptsRef.current = 0;
    
    setConnectionInfo(prev => ({
      ...prev,
      connectedAt: new Date().toISOString(),
      reconnectAttempts: 0,
    }));
    
    startHeartbeat();
  }, [debugLog, startHeartbeat]);

  /**
   * Handle WebSocket connection close
   */
  const handleClose = useCallback((event) => {
    if (!mountedRef.current) return;

    debugLog('WebSocket connection closed:', event.code, event.reason);
    setConnectionState(WS_STATES.DISCONNECTED);
    clearTimeouts();
    
    // Attempt reconnection if not a normal closure
    if (event.code !== 1000 && reconnectAttemptsRef.current < config.maxReconnectAttempts) {
      attemptReconnect();
    }
  }, [debugLog, clearTimeouts, config.maxReconnectAttempts]);

  /**
   * Handle WebSocket errors
   */
  const handleError = useCallback((error) => {
    if (!mountedRef.current) return;

    console.error('WebSocket error:', error);
    debugLog('WebSocket error occurred');
    setConnectionState(WS_STATES.ERROR);
    setError({
      message: 'WebSocket connection error',
      timestamp: new Date().toISOString(),
      code: 'WS_ERROR',
    });
  }, [debugLog]);

  /**
   * Attempt to reconnect to WebSocket
   */
  const attemptReconnect = useCallback(() => {
    if (!mountedRef.current || reconnectAttemptsRef.current >= config.maxReconnectAttempts) {
      debugLog('Max reconnection attempts reached or component unmounted');
      return;
    }

    reconnectAttemptsRef.current += 1;
    setConnectionState(WS_STATES.RECONNECTING);
    
    setConnectionInfo(prev => ({
      ...prev,
      reconnectAttempts: reconnectAttemptsRef.current,
    }));
    
    debugLog(`Attempting reconnection ${reconnectAttemptsRef.current}/${config.maxReconnectAttempts}`);
    
    reconnectTimeoutRef.current = setTimeout(() => {
      if (mountedRef.current) {
        connect();
      }
    }, config.reconnectInterval);
  }, [config.maxReconnectAttempts, config.reconnectInterval, debugLog]);

  /**
   * Establish WebSocket connection
   */
  const connect = useCallback(() => {
    if (!processId || !mountedRef.current) {
      debugLog('No process ID provided or component unmounted');
      return;
    }

    // Close existing connection
    disconnect();

    debugLog(`Connecting to WebSocket for process ${processId}`);
    setConnectionState(WS_STATES.CONNECTING);
    setError(null);

    try {
      const wsUrl = getWebSocketUrl(processId);
      debugLog('WebSocket URL:', wsUrl);
      
      wsRef.current = new WebSocket(wsUrl);
      wsRef.current.onopen = handleOpen;
      wsRef.current.onmessage = handleMessage;
      wsRef.current.onclose = handleClose;
      wsRef.current.onerror = handleError;
      
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      setConnectionState(WS_STATES.ERROR);
      setError({
        message: error.message || 'Failed to create WebSocket connection',
        timestamp: new Date().toISOString(),
        code: 'WS_CREATE_ERROR',
      });
    }
  }, [processId, handleOpen, handleMessage, handleClose, handleError, debugLog]);

  /**
   * Disconnect WebSocket
   */
  const disconnect = useCallback(() => {
    debugLog('Disconnecting WebSocket');
    clearTimeouts();
    
    if (wsRef.current) {
      wsRef.current.onopen = null;
      wsRef.current.onmessage = null;
      wsRef.current.onclose = null;
      wsRef.current.onerror = null;
      
      if (wsRef.current.readyState === WebSocket.OPEN || 
          wsRef.current.readyState === WebSocket.CONNECTING) {
        wsRef.current.close(1000, 'Component unmounting');
      }
      
      wsRef.current = null;
    }
    
    setConnectionState(WS_STATES.DISCONNECTED);
  }, [debugLog, clearTimeouts]);

  /**
   * Manually reconnect WebSocket
   */
  const reconnect = useCallback(() => {
    debugLog('Manual reconnection triggered');
    reconnectAttemptsRef.current = 0;
    connect();
  }, [debugLog, connect]);

  /**
   * Send message through WebSocket
   */
  const sendMessage = useCallback((message) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      const messageString = typeof message === 'string' ? message : JSON.stringify(message);
      wsRef.current.send(messageString);
      debugLog('Sent message:', message);
      return true;
    } else {
      console.warn('WebSocket not connected, cannot send message');
      return false;
    }
  }, [debugLog]);

  // Connect on mount and when processId changes
  useEffect(() => {
    if (processId) {
      connect();
    }
    
    return () => {
      mountedRef.current = false;
      disconnect();
    };
  }, [processId, connect, disconnect]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      mountedRef.current = false;
      clearTimeouts();
    };
  }, [clearTimeouts]);

  return {
    // Connection state
    connectionState,
    isConnected: connectionState === WS_STATES.CONNECTED,
    isConnecting: connectionState === WS_STATES.CONNECTING,
    isReconnecting: connectionState === WS_STATES.RECONNECTING,
    
    // Messages and data
    lastMessage,
    error,
    connectionInfo,
    
    // Actions
    connect,
    disconnect,
    reconnect,
    sendMessage,
    
    // Constants for external use
    WS_STATES,
  };
}

/**
 * Simplified hook for just receiving process updates
 * @param {number} processId - Process ID to monitor
 * @returns {Object} Latest process update and connection status
 */
export function useProcessUpdates(processId) {
  const {
    lastMessage,
    isConnected,
    connectionState,
    error,
  } = useWebSocket(processId, { debug: false });

  // Parse and format the latest process update
  const processUpdate = lastMessage && lastMessage.type === 'process_update' 
    ? {
        status: lastMessage.status,
        currentStep: lastMessage.current_step,
        progress: lastMessage.progress || 0,
        message: lastMessage.message,
        stepDetails: lastMessage.step_details || {},
        timestamp: lastMessage.timestamp,
        processId: lastMessage.process_id,
      }
    : null;

  return {
    processUpdate,
    isConnected,
    connectionState,
    error,
    hasUpdate: Boolean(processUpdate),
  };
}

export default useWebSocket;