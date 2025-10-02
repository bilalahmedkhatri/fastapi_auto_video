/**
 * Simple WebSocket Hook - Direct Implementation
 * Located in hooks directory for easy import
 */
import { useEffect, useRef, useCallback } from 'react';
import { useRouter } from 'next/navigation';

const WS_URL = 'ws://localhost:8000';
const WS_ENABLED = process.env.NEXT_PUBLIC_WS_ENABLED !== 'false'; // Allow disabling via env var

export const useVideoWebSocket = (userId, onMessage) => {
  const router = useRouter();
  const ws = useRef(null);
  const reconnectTimer = useRef(null);
  const shouldConnect = useRef(true);
  const isVisible = useRef(true);
  const connectionAttempts = useRef(0);
  const maxConnectionAttempts = 3; // Stop trying after 3 failed attempts

  const disconnect = useCallback(() => {
    shouldConnect.current = false;
    if (reconnectTimer.current) {
      clearTimeout(reconnectTimer.current);
      reconnectTimer.current = null;
    }
    if (ws.current && ws.current.readyState !== WebSocket.CLOSED) {
      console.log('🔌 Closing WebSocket connection...');
      ws.current.close();
      ws.current = null;
    }
  }, []);

  const connect = useCallback(() => {
    // Don't connect if disabled, max attempts reached, or conditions not met
    if (!WS_ENABLED) {
      console.log('🚫 WebSocket disabled via environment variable');
      return;
    }
    
    if (connectionAttempts.current >= maxConnectionAttempts) {
      console.log('🚫 Max WebSocket connection attempts reached. Server may not be running.');
      return;
    }
    
    if (!shouldConnect.current || !isVisible.current || !userId) return;
    
    try {
      connectionAttempts.current += 1;
      console.log(`🔌 WebSocket connection attempt ${connectionAttempts.current}/${maxConnectionAttempts}`);
      
      ws.current = new WebSocket(`${WS_URL}/ws/video-process?user_id=${userId}`);
      
      ws.current.onopen = () => {
        console.log('🔗 WebSocket connected for user:', userId);
        connectionAttempts.current = 0; // Reset on successful connection
      };
      
      ws.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('📩 WebSocket message:', data);
          if (data.type === 'video_process_update' && data.userId === userId) {
            onMessage(data.payload);
          }
        } catch (error) {
          console.error('❌ WebSocket message error:', error);
        }
      };
      
      ws.current.onclose = () => {
        console.log('🔌 WebSocket disconnected');
        if (shouldConnect.current && isVisible.current && connectionAttempts.current < maxConnectionAttempts) {
          const retryDelay = Math.min(3000 * connectionAttempts.current, 10000); // Progressive backoff
          console.log(`🔄 Attempting reconnect in ${retryDelay/1000} seconds...`);
          reconnectTimer.current = setTimeout(connect, retryDelay);
        } else if (connectionAttempts.current >= maxConnectionAttempts) {
          console.log('⚠️ WebSocket server appears to be unavailable. Real-time updates disabled.');
        }
      };
      
      ws.current.onerror = (error) => {
        // Only log WebSocket errors if it's not a connection refused error
        // This prevents console spam when the WebSocket server is not running
        if (ws.current && ws.current.readyState !== WebSocket.CONNECTING) {
          console.warn('⚠️ WebSocket error (server may not be running)');
        }
      };
      
    } catch (error) {
      console.warn('⚠️ WebSocket connection error:', error.message);
    }
  }, [userId, onMessage]);

  useEffect(() => {
    if (!userId) return;
    shouldConnect.current = true;
    
    // Handle page visibility changes
    const handleVisibilityChange = () => {
      isVisible.current = !document.hidden;
      
      if (document.hidden) {
        console.log('📱 Page hidden - disconnecting WebSocket');
        disconnect();
      } else if (shouldConnect.current) {
        console.log('📱 Page visible - reconnecting WebSocket');
        connect();
      }
    };

    // Handle page unload
    const handleBeforeUnload = () => {
      console.log('🚪 Page unloading - closing WebSocket');
      disconnect();
    };

    // Handle router navigation
    const handleRouteChange = () => {
      console.log('🚪 Route changing - closing WebSocket');
      disconnect();
    };

    // Add event listeners
    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('beforeunload', handleBeforeUnload);
    
    // Listen for route changes (Next.js specific)
    const handleRouteChangeStart = () => handleRouteChange();
    if (typeof window !== 'undefined') {
      window.addEventListener('popstate', handleRouteChange);
    }
    
    // Initial connection
    connect();

    return () => {
      // Cleanup event listeners
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('beforeunload', handleBeforeUnload);
      if (typeof window !== 'undefined') {
        window.removeEventListener('popstate', handleRouteChange);
      }
      
      // Disconnect WebSocket
      disconnect();
    };
  }, [userId, connect, disconnect]);

  return ws.current;
};