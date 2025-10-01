/**
 * Reusable WebSocket Hook for Real-time Updates
 * GitHub Best Practice: Centralized WebSocket management
 */
import { useEffect, useRef, useCallback } from 'react';

const WEBSOCKET_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';
const RECONNECT_INTERVAL = 3000;
const MAX_RECONNECT_ATTEMPTS = 5;

export const useWebSocket = (endpoint, options = {}) => {
  const {
    onMessage = () => {},
    onConnect = () => {},
    onDisconnect = () => {},
    onError = () => {},
    autoReconnect = true,
    reconnectInterval = RECONNECT_INTERVAL,
    maxReconnectAttempts = MAX_RECONNECT_ATTEMPTS
  } = options;

  const ws = useRef(null);
  const reconnectAttempts = useRef(0);
  const reconnectTimer = useRef(null);
  const isConnected = useRef(false);

  const connect = useCallback(() => {
    try {
      ws.current = new WebSocket(`${WEBSOCKET_URL}${endpoint}`);
      
      ws.current.onopen = () => {
        isConnected.current = true;
        reconnectAttempts.current = 0;
        onConnect();
      };
      
      ws.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          onMessage(data);
        } catch (error) {
          onMessage(event.data);
        }
      };
      
      ws.current.onclose = () => {
        isConnected.current = false;
        onDisconnect();
        
        if (autoReconnect && reconnectAttempts.current < maxReconnectAttempts) {
          reconnectAttempts.current++;
          reconnectTimer.current = setTimeout(connect, reconnectInterval);
        }
      };
      
      ws.current.onerror = (error) => {
        onError(error);
      };
    } catch (error) {
      onError(error);
    }
  }, [endpoint, onMessage, onConnect, onDisconnect, onError, autoReconnect, reconnectInterval, maxReconnectAttempts]);

  const disconnect = useCallback(() => {
    if (reconnectTimer.current) {
      clearTimeout(reconnectTimer.current);
    }
    if (ws.current) {
      ws.current.close();
    }
  }, []);

  const sendMessage = useCallback((message) => {
    if (ws.current && isConnected.current) {
      const data = typeof message === 'string' ? message : JSON.stringify(message);
      ws.current.send(data);
      return true;
    }
    return false;
  }, []);

  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect]);

  return {
    sendMessage,
    disconnect,
    reconnect: connect,
    isConnected: isConnected.current
  };
};

// Specific hook for video process updates
export const useVideoProcessWebSocket = (userId, onUpdate) => {
  return useWebSocket('/ws/video-process', {
    onMessage: (data) => {
      if (data.userId === userId && data.type === 'video_process_update') {
        onUpdate(data.payload);
      }
    },
    onConnect: () => console.log('🔗 Video process WebSocket connected'),
    onDisconnect: () => console.log('🔌 Video process WebSocket disconnected'),
    onError: (error) => console.error('❌ Video process WebSocket error:', error)
  });
};