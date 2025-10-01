# 🔗 WebSocket Real-time Module (ws_realtime)

This directory contains all WebSocket-related functionality for real-time updates between frontend and backend.

## 📁 Directory Structure

### Core Files:
- **`manager.py`** - Advanced WebSocket connection manager with rooms
- **`routes.py`** - FastAPI WebSocket endpoint definitions  
- **`simple_manager.py`** - Simple WebSocket connection utilities
- **`__init__.py`** - Python module exports

## 🚀 Usage

### Basic WebSocket Integration:
```python
from ws_realtime.simple_manager import send_video_update
from ws_realtime.manager import notify_video_process_update

# Send real-time updates
await send_video_update(user_id, video_data)
await notify_video_process_update(user_id, process_data)
```

### FastAPI Integration:
```python
from ws_realtime.routes import websocket_router

# Include in main.py
app.include_router(websocket_router)
```

## 🔧 Features

### ✅ Room-based Messaging
- User-specific message routing: `user_{user_id}`
- Broadcast capabilities to all rooms
- Connection management by user/room

### ✅ Connection Management
- Automatic cleanup on disconnection
- Connection state tracking
- Error handling and logging

### ✅ Message Types
- `video_process_update` - Video generation progress
- `script_update` - Script changes and updates
- Custom message types supported

## 📊 WebSocket Endpoints

### Available Endpoints:
- `/ws/video-process?user_id={user_id}` - Video process updates
- `/ws/scripts?user_id={user_id}` - Script updates

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

## 🔒 Security & Performance
- User ID validation on connection
- Automatic connection cleanup
- Efficient message routing
- Memory leak prevention