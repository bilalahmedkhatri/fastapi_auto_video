# 🔗 WebSocket Real-time Module (ws_realtime)

This directory contains all WebSocket-related functionality for real-time updates between frontend and backend.

## 📁 Directory Structure

### Frontend Files:
- **`useWebSocket.js`** - Advanced WebSocket hook with room management
- **`useVideoWebSocket.js`** - Simple WebSocket hook for video process updates
- **`simple.js`** - Basic WebSocket connection utilities
- **`index.js`** - Centralized exports for all WebSocket hooks

### Backend Files:
- **`manager.py`** - Advanced WebSocket connection manager with rooms
- **`routes.py`** - FastAPI WebSocket endpoint definitions
- **`simple_manager.py`** - Simple WebSocket connection utilities
- **`__init__.py`** - Python module exports

### Test Files:
- **`test_websocket.js`** - Basic WebSocket connection tests
- **`test_websocket_behavior.js`** - Tab change behavior tests
- **`monitor_websockets.js`** - Browser console monitoring script
- **`websocket_test.html`** - Interactive WebSocket test page

## 🚀 Usage

### Frontend (React/Next.js):
```javascript
// Import from centralized index
import { useVideoWebSocket } from '@/ws_realtime';

// Or import specific hooks
import { useVideoWebSocket } from '@/ws_realtime/useVideoWebSocket';
import { useWebSocket } from '@/ws_realtime/useWebSocket';

// Usage in component
const MyComponent = () => {
  useVideoWebSocket(userId, (processData) => {
    console.log('Video process update:', processData);
  });
};
```

### Backend (FastAPI):
```python
# Import WebSocket utilities
from ws_realtime.simple_manager import send_video_update
from ws_realtime.manager import notify_video_process_update
from ws_realtime.routes import websocket_router

# Send real-time updates
await send_video_update(user_id, video_data)
await notify_video_process_update(user_id, process_data)
```

## 🔧 Features

### ✅ Auto-cleanup on Tab Changes
- WebSocket disconnects when user switches tabs
- Automatically reconnects when user returns
- Prevents memory leaks and unnecessary connections

### ✅ Reconnection Logic
- Automatic reconnection on connection loss
- Exponential backoff for failed connections
- Maximum retry attempts configuration

### ✅ Room-based Messaging
- User-specific message routing
- Broadcast capabilities
- Connection management by user/room

### ✅ Error Handling
- Graceful fallbacks when WebSocket unavailable
- Comprehensive error logging
- Connection state management

## 🧪 Testing

### Browser Console Test:
```javascript
// Run in browser console on Generated Scripts page
const script = document.createElement('script');
script.src = '/ws_realtime/monitor_websockets.js';
document.head.appendChild(script);
```

### Interactive Test Page:
Visit: `http://localhost:3000/ws_realtime/websocket_test.html`

## 📊 Endpoints

### WebSocket Endpoints:
- `ws://localhost:8000/ws/video-process?user_id={user_id}` - Video process updates
- `ws://localhost:8000/ws/scripts?user_id={user_id}` - Script updates

### Message Format:
```json
{
  "type": "video_process_update",
  "userId": "user_123",
  "payload": {
    "process_id": 1,
    "status": "active",
    "current_step": "voiceover",
    "overall_progress": 45
  },
  "timestamp": 1695123456.789
}
```

## 🔒 Security Considerations
- User ID validation on connection
- Rate limiting on message frequency
- Connection timeout management
- Proper cleanup on disconnection

## 📈 Performance
- Minimal resource usage when inactive
- Efficient message routing
- Connection pooling for scalability
- Automatic cleanup prevents memory leaks