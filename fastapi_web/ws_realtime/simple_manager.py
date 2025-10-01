"""
Minimal WebSocket implementation directly in main.py
"""
from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio
from typing import Dict, List

# Simple WebSocket connections store
active_connections: Dict[str, List[WebSocket]] = {}

async def connect_websocket(websocket: WebSocket, user_id: str):
    """Connect WebSocket for user"""
    await websocket.accept()
    if user_id not in active_connections:
        active_connections[user_id] = []
    active_connections[user_id].append(websocket)
    print(f"✅ WebSocket connected for user: {user_id}")

def disconnect_websocket(websocket: WebSocket, user_id: str):
    """Disconnect WebSocket for user"""
    if user_id in active_connections:
        try:
            active_connections[user_id].remove(websocket)
            if not active_connections[user_id]:
                del active_connections[user_id]
            print(f"❌ WebSocket disconnected for user: {user_id}")
        except ValueError:
            pass

async def send_video_update(user_id: str, video_data: dict):
    """Send video update to user's WebSocket connections"""
    if user_id in active_connections:
        message = json.dumps({
            "type": "video_process_update",
            "userId": user_id,
            "payload": video_data
        })
        
        disconnected = []
        for websocket in active_connections[user_id]:
            try:
                await websocket.send_text(message)
            except Exception as e:
                print(f"❌ Failed to send WebSocket message: {e}")
                disconnected.append(websocket)
        
        # Clean up disconnected sockets
        for websocket in disconnected:
            disconnect_websocket(websocket, user_id)