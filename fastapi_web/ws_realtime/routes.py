"""
WebSocket Routes for Real-time Updates
GitHub Best Practice: Separate WebSocket endpoints
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from .manager import ws_manager
import logging

logger = logging.getLogger(__name__)

# Create WebSocket router
websocket_router = APIRouter(tags=["WebSocket"])

@websocket_router.websocket("/ws/video-process")
async def video_process_websocket(websocket: WebSocket, user_id: str = "anonymous"):
    """WebSocket endpoint for video process updates"""
    room = f"user_{user_id}"
    await ws_manager.connect(websocket, room)
    
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            logger.info(f"Received from {user_id}: {data}")
            
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, room)
        logger.info(f"User {user_id} disconnected from video process updates")

@websocket_router.websocket("/ws/scripts")  
async def scripts_websocket(websocket: WebSocket, user_id: str = "anonymous"):
    """WebSocket endpoint for script updates"""
    room = f"user_{user_id}"
    await ws_manager.connect(websocket, room)
    
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Received from {user_id}: {data}")
            
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, room)
        logger.info(f"User {user_id} disconnected from script updates")