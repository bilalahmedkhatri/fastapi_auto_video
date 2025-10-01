/**
 * WebSocket Test Script
 */
const testWebSocket = () => {
  const ws = new WebSocket('ws://localhost:8000/ws/video-process?user_id=demo_user');
  
  ws.onopen = () => {
    console.log('✅ WebSocket connected successfully!');
  };
  
  ws.onmessage = (event) => {
    console.log('📩 WebSocket message received:', event.data);
  };
  
  ws.onerror = (error) => {
    console.error('❌ WebSocket error:', error);
  };
  
  ws.onclose = () => {
    console.log('🔌 WebSocket disconnected');
  };
  
  // Send a test message after 2 seconds
  setTimeout(() => {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ test: 'Hello WebSocket!' }));
    }
  }, 2000);
  
  return ws;
};

// Test WebSocket connection
console.log('🧪 Testing WebSocket connection...');
const testWS = testWebSocket();

// Clean up after 10 seconds
setTimeout(() => {
  testWS.close();
  console.log('🧹 Test completed');
}, 10000);