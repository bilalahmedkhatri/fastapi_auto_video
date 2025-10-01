/**
 * Simple WebSocket Hook for Video Process Updates
 */
import { useEffect, useRef } from 'react';

const WS_URL = 'ws://localhost:8000';

export const useSimpleWebSocket = (userId, onMessage) => {
  const ws = useRef(null);
  const reconnectTimer = useRef(null);

  useEffect(() => {
    if (!userId) return;

    const connect = () => {
      try {
        ws.current = new WebSocket(`${WS_URL}/ws/video-process?user_id=${userId}`);
        
        ws.current.onopen = () => {
          console.log('🔗 WebSocket connected for user:', userId);
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
          console.log('🔌 WebSocket disconnected, attempting reconnect...');
          reconnectTimer.current = setTimeout(connect, 3000);
        };
        
        ws.current.onerror = (error) => {
          console.error('❌ WebSocket error:', error);
        };
        
      } catch (error) {
        console.error('❌ WebSocket connection error:', error);
      }
    };

    connect();

    return () => {
      if (reconnectTimer.current) {
        clearTimeout(reconnectTimer.current);
      }
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [userId, onMessage]);

  return ws.current;
};

export { useSimpleWebSocket };