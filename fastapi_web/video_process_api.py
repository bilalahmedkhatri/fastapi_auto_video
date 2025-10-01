#!/usr/bin/env python3
"""
Video Process API Endpoints

This module provides FastAPI endpoints for managing video generation processes,
integrating with Celery tasks and VideoGenerationProcessManager for comprehensive
workflow orchestration and status tracking.

Endpoints:
- POST /api/video-process/start - Start new video generation
- GET /api/video-process/{process_id}/status - Get process status
- POST /api/video-process/{process_id}/pause - Pause process
- POST /api/video-process/{process_id}/resume - Resume process  
- POST /api/video-process/{process_id}/retry - Retry failed step
- GET /api/video-process/user/{user_id} - Get user's processes
- DELETE /api/video-process/{process_id} - Cancel process
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import asyncio

from models.db_models import get_session
from models.video_process_manager import VideoGenerationProcessManager, get_active_processes_for_user
from video_process_tasks import (
    start_video_generation_workflow,
    get_process_status_task,
    cleanup_completed_processes_task
)
from celery_app import celery_app


# Pydantic models for request/response validation
class VideoProcessStartRequest(BaseModel):
    """Request model for starting video process."""
    user_id: str = Field(..., description="User ID starting the process")
    prompt: str = Field(..., min_length=1, max_length=2000, description="Video generation prompt")
    category: Optional[str] = Field("General", description="Video category")
    language: Optional[str] = Field("English", description="Video language")
    duration: Optional[str] = Field("medium", description="Video duration: short, medium, long")
    priority: Optional[str] = Field("normal", description="Process priority: low, normal, high")
    session_id: Optional[str] = Field(None, description="Browser session ID")
    additional_settings: Optional[Dict[str, Any]] = Field({}, description="Additional configuration")
    frontend_data: Optional[Dict[str, Any]] = Field(None, description="Structured data from frontend workflow")


class VideoProcessStatusResponse(BaseModel):
    """Response model for process status."""
    process_id: int
    status: str
    current_step: str
    overall_progress: int
    step_progress: Dict[str, str]
    started_at: str
    estimated_completion: Optional[str]
    error_message: Optional[str] = None
    step_details: Optional[Dict[str, Any]] = None


class VideoProcessListResponse(BaseModel):
    """Response model for process list."""
    processes: List[Dict[str, Any]]
    total_count: int
    active_count: int
    completed_count: int
    failed_count: int


class StepActionRequest(BaseModel):
    """Request model for step actions (pause, resume, retry)."""
    reason: Optional[str] = Field(None, description="Reason for action")
    user_id: str = Field(..., description="User performing action")



# Create router for video process endpoints
video_process_router = APIRouter(prefix="/api/video-process", tags=["Video Process"])


@video_process_router.post("/start", response_model=Dict[str, Any])
async def start_video_process(request: VideoProcessStartRequest, background_tasks: BackgroundTasks):
    """
    Start a new video generation process.
    
    This endpoint initializes a new video generation workflow using Celery tasks
    and returns the process ID for tracking.
    """
    try:
        # Check if frontend data is provided
        if request.frontend_data and request.additional_settings.get("use_frontend_data"):
            # Use the direct generate_video task for frontend data
            from celery_app import generate_video as generate_video_task
            import uuid
            from models.db_models import Video, get_session
            from datetime import datetime
            
            # Generate a video ID and create database record for frontend workflow
            video_id = str(uuid.uuid4())
            
            # Create video record in database
            session_gen = get_session()
            session = next(session_gen)
            try:
                new_video = Video(
                    id=video_id,
                    user_id=request.user_id,
                    title=request.frontend_data.get('script_data', {}).get('title', 'Frontend Generated Video'),
                    description=request.prompt,
                    prompt=request.prompt,
                    duration=request.frontend_data.get('video_effects_config', {}).get('duration', 30),
                    resolution=request.frontend_data.get('video_effects_config', {}).get('resolution', '1920x1080'),
                    format=request.frontend_data.get('video_effects_config', {}).get('format', 'mp4'),
                    content_type=request.category or 'General',
                    style=request.frontend_data.get('video_effects_config', {}).get('style', 'modern'),
                    audio_type='voiceover',
                    aspect_ratio=request.frontend_data.get('video_effects_config', {}).get('aspect_ratio', '16:9'),
                    fps=request.frontend_data.get('video_effects_config', {}).get('fps', 24),
                    quality=request.frontend_data.get('video_effects_config', {}).get('quality', 'high'),
                    use_ai=True,
                    include_audio=True,
                    text_overlay_style=request.frontend_data.get('video_effects_config', {}).get('text_overlay_style', 'modern'),
                    transitions=request.frontend_data.get('video_effects_config', {}).get('transitions', 'fade'),
                    generate_type='frontend',
                    priority=request.priority,
                    status="pending",
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                session.add(new_video)
                session.commit()
            finally:
                session.close()
            
            # Create video settings from request
            video_settings = {
                "video_id": video_id,
                "category": request.category,
                "language": request.language,
                "duration": request.duration,
                "priority": request.priority,
                **request.additional_settings
            }
            
            # Start video generation with frontend data
            task_result = generate_video_task.delay(
                user_id=request.user_id,
                video_settings=video_settings,
                frontend_data=request.frontend_data
            )
            
            return {
                "success": True,
                "task_id": task_result.id,
                "video_id": video_id,
                "message": "Video generation started with frontend data",
                "estimated_completion_minutes": 3,
                "status_endpoint": f"/api/video-process/task/{task_result.id}/status",
                "task_type": "frontend_video_generation"
            }
        
        else:
            # Use traditional workflow for generated content
            input_data = {
                "prompt": request.prompt,
                "category": request.category,
                "language": request.language,
                "duration": request.duration,
                "additional_settings": request.additional_settings
            }
            
            # Start the workflow using Celery
            workflow_result = start_video_generation_workflow.delay(
                user_id=request.user_id,
                input_data=input_data,
                session_id=request.session_id,
                priority=request.priority
            )
            
            # Get the result to extract process_id
            try:
                # Wait briefly for workflow initialization 
                result = workflow_result.get(timeout=5)
                process_id = result.get("process_id")
                workflow_task_id = result.get("workflow_task_id")
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to start video generation workflow: {str(e)}"
                )
            
            return {
                "success": True,
                "process_id": process_id,
                "workflow_task_id": workflow_task_id,
                "message": "Video generation started successfully",
                "estimated_completion_minutes": 5,
                "status_endpoint": f"/api/video-process/{process_id}/status",
                "websocket_endpoint": f"/ws/video-process/{process_id}"
            }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start video process: {str(e)}"
        )


@video_process_router.get("/{process_id}/status", response_model=VideoProcessStatusResponse)
async def get_video_process_status(process_id: int):
    """
    Get current status of a video generation process.
    
    Returns detailed information about process progress, current step,
    and any errors or issues.
    """
    try:
        # Use Celery task to get status (handles database session properly)
        status_task = get_process_status_task.delay(process_id)
        status_result = status_task.get(timeout=10)
        
        if "error" in status_result:
            raise HTTPException(
                status_code=404,
                detail=f"Process {process_id} not found or error occurred: {status_result['error']}"
            )
        
        current_step_info = status_result.get("current_step_info", {})
        
        return VideoProcessStatusResponse(
            process_id=process_id,
            status=current_step_info.get("status", "unknown"),
            current_step=current_step_info.get("current_step", "unknown"),
            overall_progress=current_step_info.get("overall_progress", 0),
            step_progress=current_step_info.get("step_progress", {}),
            started_at=current_step_info.get("started_at", ""),
            estimated_completion=current_step_info.get("estimated_completion"),
            error_message=current_step_info.get("error_messages", [None])[-1],
            step_details=current_step_info.get("step_details", {})
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get process status: {str(e)}"
        )


@video_process_router.get("/task/{task_id}/status")
async def get_task_status(task_id: str):
    """
    Get status of a Celery task (for frontend video generation).
    """
    try:
        from celery_app import celery_app
        
        # Get task result
        task_result = celery_app.AsyncResult(task_id)
        
        if task_result.state == 'PENDING':
            response = {
                'task_id': task_id,
                'status': 'PENDING',
                'progress': 0,
                'message': 'Task is waiting to be processed'
            }
        elif task_result.state == 'PROGRESS':
            response = {
                'task_id': task_id,
                'status': 'IN_PROGRESS',
                'progress': task_result.info.get('progress', 0),
                'message': task_result.info.get('message', 'Processing...'),
                'stage': task_result.info.get('stage', 'unknown')
            }
        elif task_result.state == 'SUCCESS':
            result = task_result.result
            response = {
                'task_id': task_id,
                'status': 'SUCCESS',
                'progress': 100,
                'message': 'Video generation completed successfully',
                'result': result
            }
        else:  # FAILURE
            response = {
                'task_id': task_id,
                'status': 'FAILURE',
                'progress': 0,
                'message': f'Task failed: {str(task_result.info)}',
                'error': str(task_result.info)
            }
            
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get task status: {str(e)}"
        )


@video_process_router.post("/{process_id}/pause")
async def pause_video_process(process_id: int, request: StepActionRequest):
    """
    Pause a running video generation process.
    
    This will pause the process at the current step and can be resumed later.
    """
    try:
        session = next(get_session())
        manager = VideoGenerationProcessManager(session)
        
        if not manager.load_process(process_id):
            raise HTTPException(status_code=404, detail=f"Process {process_id} not found")
        
        success = manager.pause_process(reason=request.reason)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to pause process")
        
        # Log user action
        manager._log_user_action("process_paused", {
            "user_id": request.user_id,
            "reason": request.reason,
            "paused_at": datetime.utcnow().isoformat()
        })
        
        return {
            "success": True,
            "message": "Process paused successfully",
            "process_id": process_id
        }
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Failed to pause process: {str(e)}")


@video_process_router.post("/{process_id}/resume")
async def resume_video_process(process_id: int, request: StepActionRequest):
    """
    Resume a paused video generation process.
    
    This will continue the process from where it was paused.
    """
    try:
        session = next(get_session())
        manager = VideoGenerationProcessManager(session)
        
        if not manager.load_process(process_id):
            raise HTTPException(status_code=404, detail=f"Process {process_id} not found")
        
        success = manager.resume_process()
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to resume process")
        
        # Log user action
        manager._log_user_action("process_resumed", {
            "user_id": request.user_id,
            "resumed_at": datetime.utcnow().isoformat()
        })
        
        return {
            "success": True,
            "message": "Process resumed successfully",
            "process_id": process_id
        }
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Failed to resume process: {str(e)}")


@video_process_router.post("/{process_id}/retry/{step_name}")
async def retry_failed_step(process_id: int, step_name: str, request: StepActionRequest):
    """
    Retry a failed step in the video generation process.
    
    This will attempt to re-run the specified failed step.
    """
    try:
        session = next(get_session())
        manager = VideoGenerationProcessManager(session)
        
        if not manager.load_process(process_id):
            raise HTTPException(status_code=404, detail=f"Process {process_id} not found")
        
        success = manager.retry_failed_step(step_name)
        
        if not success:
            raise HTTPException(
                status_code=400, 
                detail=f"Failed to retry step '{step_name}'. Step may not be in failed state."
            )
        
        # Log user action
        manager._log_user_action("step_retry", {
            "user_id": request.user_id,
            "step_name": step_name,
            "retried_at": datetime.utcnow().isoformat()
        })
        
        return {
            "success": True,
            "message": f"Step '{step_name}' retry initiated successfully",
            "process_id": process_id,
            "step_name": step_name
        }
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Failed to retry step: {str(e)}")


@video_process_router.get("/user/{user_id}", response_model=VideoProcessListResponse)
async def get_user_processes(user_id: str, limit: int = 10, status: Optional[str] = None):
    """
    Get all video generation processes for a specific user.
    
    Optionally filter by status (active, completed, failed, paused).
    """
    try:
        session = next(get_session())
        
        # Get active processes using existing utility function
        processes = get_active_processes_for_user(session, user_id, limit)
        
        # Filter by status if provided
        if status:
            processes = [p for p in processes if p.get("status") == status]
        
        # Count by status
        status_counts = {"active": 0, "completed": 0, "failed": 0, "paused": 0}
        for process in processes:
            proc_status = process.get("status", "unknown")
            if proc_status in status_counts:
                status_counts[proc_status] += 1
        
        return VideoProcessListResponse(
            processes=processes,
            total_count=len(processes),
            active_count=status_counts["active"],
            completed_count=status_counts["completed"],
            failed_count=status_counts["failed"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get user processes: {str(e)}"
        )


@video_process_router.delete("/{process_id}")
async def cancel_video_process(process_id: int, user_id: str):
    """
    Cancel a running video generation process.
    
    This will stop the process and mark it as cancelled.
    """
    try:
        session = next(get_session())
        manager = VideoGenerationProcessManager(session)
        
        if not manager.load_process(process_id):
            raise HTTPException(status_code=404, detail=f"Process {process_id} not found")
        
        # Mark process as cancelled
        success = manager.handle_step_failure(
            step_name=manager.current_process.current_step,
            error_message="Process cancelled by user",
            error_details={"cancelled_by": user_id, "cancelled_at": datetime.utcnow().isoformat()},
            is_critical=True
        )
        
        if success:
            # Try to revoke any running Celery tasks (best effort)
            try:
                # This would need the task IDs, which we'd need to store in the process
                pass  # Implementation depends on how we track task IDs
            except:
                pass  # Task revocation is best effort
            
            return {
                "success": True,
                "message": "Process cancelled successfully",
                "process_id": process_id
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to cancel process")
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Failed to cancel process: {str(e)}")


@video_process_router.get("/analytics/summary")
async def get_process_analytics_summary():
    """
    Get summary analytics for all video generation processes.
    
    Returns aggregate statistics for monitoring and reporting.
    """
    try:
        session = next(get_session())
        
        # This would need additional database queries for full analytics
        # For now, return basic structure
        return {
            "total_processes": 0,
            "processes_today": 0,
            "average_completion_time": 0,
            "success_rate": 0,
            "most_common_failures": [],
            "peak_usage_hours": [],
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get analytics: {str(e)}"
        )


@video_process_router.post("/cleanup")
async def cleanup_old_processes(background_tasks: BackgroundTasks, days_old: int = 7):
    """
    Clean up old completed video generation processes.
    
    This removes processes older than the specified number of days.
    """
    try:
        # Run cleanup in background
        cleanup_task = cleanup_completed_processes_task.delay(days_old)
        
        return {
            "success": True,
            "message": f"Cleanup task started for processes older than {days_old} days",
            "cleanup_task_id": cleanup_task.id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start cleanup: {str(e)}"
        )


# WebSocket connection manager for real-time updates
class VideoProcessConnectionManager:
    """Manages WebSocket connections for real-time video process updates."""
    
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, process_id: int):
        """Accept new WebSocket connection for a process."""
        await websocket.accept()
        if process_id not in self.active_connections:
            self.active_connections[process_id] = []
        self.active_connections[process_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, process_id: int):
        """Remove WebSocket connection."""
        if process_id in self.active_connections:
            if websocket in self.active_connections[process_id]:
                self.active_connections[process_id].remove(websocket)
            if not self.active_connections[process_id]:
                del self.active_connections[process_id]
    
    async def send_process_update(self, process_id: int, data: Dict[str, Any]):
        """Send update to all connections watching a process."""
        if process_id in self.active_connections:
            connections_to_remove = []
            for websocket in self.active_connections[process_id]:
                try:
                    await websocket.send_json(data)
                except:
                    connections_to_remove.append(websocket)
            
            # Remove failed connections
            for websocket in connections_to_remove:
                self.disconnect(websocket, process_id)


# Global connection manager
connection_manager = VideoProcessConnectionManager()


@video_process_router.websocket("/ws/{process_id}")
async def websocket_process_status(websocket: WebSocket, process_id: int):
    """
    WebSocket endpoint for real-time video process status updates.
    
    Clients can connect to receive live updates about process progress,
    step changes, errors, and completion status.
    """
    await connection_manager.connect(websocket, process_id)
    
    try:
        while True:
            # Send periodic status updates
            try:
                # Get current status
                status_task = get_process_status_task.delay(process_id)
                status_result = status_task.get(timeout=5)
                
                if "error" not in status_result:
                    current_step_info = status_result.get("current_step_info", {})
                    
                    update_data = {
                        "type": "status_update",
                        "process_id": process_id,
                        "status": current_step_info.get("status", "unknown"),
                        "current_step": current_step_info.get("current_step", "unknown"),
                        "overall_progress": current_step_info.get("overall_progress", 0),
                        "step_progress": current_step_info.get("step_progress", {}),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                    await websocket.send_json(update_data)
                
                # Wait before next update
                await asyncio.sleep(2)  # Update every 2 seconds
                
            except Exception as e:
                # Send error update
                error_data = {
                    "type": "error",
                    "process_id": process_id,
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
                await websocket.send_json(error_data)
                break
                
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, process_id)
    except Exception as e:
        print(f"WebSocket error for process {process_id}: {e}")
        connection_manager.disconnect(websocket, process_id)


# Helper function to send updates to WebSocket clients (for use by Celery tasks)
async def notify_process_update(process_id: int, update_data: Dict[str, Any]):
    """Send process update to all connected WebSocket clients."""
    await connection_manager.send_process_update(process_id, update_data)


# Export the router for inclusion in main FastAPI app
__all__ = ["video_process_router", "notify_process_update"]