"""
Reusable WebSocket Manager for FastAPI
GitHub Best Practice: Centralized WebSocket connection management
"""
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Any, Optional
import json
import logging
import asyncio

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Manages WebSocket connections with room-based messaging"""
    
    def __init__(self):
        # Store active connections by room/user
        self.active_connections: Dict[str, List[WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket, room: str) -> None:
        """Accept WebSocket connection and add to room"""
        await websocket.accept()
        if room not in self.active_connections:
            self.active_connections[room] = []
        self.active_connections[room].append(websocket)
        logger.info(f"Client connected to room: {room}")
        
    def disconnect(self, websocket: WebSocket, room: str) -> None:
        """Remove WebSocket from room"""
        if room in self.active_connections:
            try:
                self.active_connections[room].remove(websocket)
                if not self.active_connections[room]:
                    del self.active_connections[room]
                logger.info(f"Client disconnected from room: {room}")
            except ValueError:
                pass
                
    async def send_personal_message(self, message: Any, websocket: WebSocket) -> None:
        """Send message to specific WebSocket"""
        try:
            data = json.dumps(message) if not isinstance(message, str) else message
            await websocket.send_text(data)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            
    async def broadcast_to_room(self, message: Any, room: str) -> None:
        """Broadcast message to all connections in room"""
        if room in self.active_connections:
            data = json.dumps(message) if not isinstance(message, str) else message
            disconnected = []
            
            for websocket in self.active_connections[room]:
                try:
                    await websocket.send_text(data)
                except Exception:
                    disconnected.append(websocket)
            
            # Clean up disconnected sockets
            for websocket in disconnected:
                self.disconnect(websocket, room)
                
    async def broadcast_to_all(self, message: Any) -> None:
        """Broadcast message to all active connections"""
        for room in list(self.active_connections.keys()):
            await self.broadcast_to_room(message, room)
            
    def get_room_count(self, room: str) -> int:
        """Get number of active connections in room"""
        return len(self.active_connections.get(room, []))
        
    def get_total_connections(self) -> int:
        """Get total active connections across all rooms"""
        return sum(len(connections) for connections in self.active_connections.values())

# Global WebSocket manager instance
ws_manager = WebSocketManager()

# Convenience functions for video process updates
async def notify_video_process_update(user_id: str, process_data: Dict[str, Any]) -> None:
    """Notify user about video process updates"""
    message = {
        "type": "video_process_update",
        "userId": user_id,
        "payload": process_data,
        "timestamp": asyncio.get_event_loop().time()
    }
    await ws_manager.broadcast_to_room(message, f"user_{user_id}")

async def notify_script_update(user_id: str, script_data: Dict[str, Any]) -> None:
    """Notify user about script updates"""
    message = {
        "type": "script_update", 
        "userId": user_id,
        "payload": script_data,
        "timestamp": asyncio.get_event_loop().time()
    }
    await ws_manager.broadcast_to_room(message, f"user_{user_id}")