"""
Auto Video Generation API - Main Application

FastAPI application for automated video generation with AI-powered features.
Includes video creation, script generation, voiceover synthesis, and media processing.
"""

import uvicorn
import logging
import os
import json
import time
import mimetypes
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Query, Response, status, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlmodel import Session, select

from models.db_models import VideoCreationRequest, Video, create_db_and_tables, get_session
from celery_app import generate_video as generate_video_task, celery_app, VideoProcessingState, redis_client
from routes import load_routers
from ws_realtime.simple_manager import connect_websocket, disconnect_websocket

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/auto_video.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Auto Video Generation API",
    description="AI-powered automated video generation platform",
    version="1.0.0"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static file directories
app.mount("/api/voice-samples", StaticFiles(directory="media/voice-samples"), name="voice-samples")
app.mount("/api/voices/samples", StaticFiles(directory="media/voice-samples"), name="voices-samples-alias")
app.mount("/api/audio", StaticFiles(directory="media/audio"), name="generated-audio")
app.mount("/media", StaticFiles(directory="media"), name="media-files")

# Load all routers from configuration
loaded_count = load_routers(app)


# ============================================================================
# WebSocket Endpoints
# ============================================================================

@app.websocket("/ws/video-process")
async def websocket_video_process(websocket: WebSocket, user_id: str = "demo_user"):
    """Simple WebSocket endpoint for video process updates"""
    await connect_websocket(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"WebSocket received from {user_id}: {data}")
    except WebSocketDisconnect:
        disconnect_websocket(websocket, user_id)


# ============================================================================
# Lifecycle Events
# ============================================================================

@app.on_event("startup")
async def on_startup():
    """Initialize application on startup"""
    create_db_and_tables()
    
    # Log database connection information
    from models.database_connection import get_connection_info
    db_info = get_connection_info()
    logger.info(f"🗄️  Database: {db_info['connection_type'].upper()} - {db_info['connection_url_masked']}")
    
    logger.info(f"Application started - {loaded_count} routers loaded")
    
    # Run voice sample check in background
    from server_starting_apps.startup_tasks import startup_voice_sample_check
    await startup_voice_sample_check()
    
    # Preload Kokoro model for faster voiceover generation
    logger.info("🔄 Warming up Kokoro voice model...")
    try:
        from kokoro_82M.model_cache import get_cached_generator
        get_cached_generator()  # Loads model into memory (~8 seconds)
        logger.info("✅ Kokoro model ready - voiceover requests will be fast!")
    except Exception as e:
        logger.error(f"⚠️ Failed to preload Kokoro model: {e}")
        logger.error("Voice generation will work but first request will be slower")


# ============================================================================
# Helper Functions (TODO: Move to services layer)
# ============================================================================
async def generate_video(video_id: str, session: Session):
    """
    This function contains the actual video creation logic.
    It updates the database with the status of the video generation process.
    """
    try:
        # Get the video record from the database
        video = session.get(Video, video_id)
        if not video:
            logger.error(f"Video with id {video_id} not found")
            return
        
        # Update status to processing
        video.status = "processing"
        video.updated_at = datetime.now()
        session.add(video)
        session.commit()
        
        # Simulate video processing time
        logger.info(f"Starting video generation for '{video.title}' (ID: {video_id})")
        time.sleep(60)  # Replace with actual video generation logic
        
        # Simulated output path - replace with actual output path logic
        output_path = f"/videos/output/{video_id}_{int(time.time())}.{video.format}"
        
        # Update video with completed status and output URL
        video.status = "completed"
        video.output_url = output_path
        video.updated_at = datetime.now()
        session.add(video)
        session.commit()
        
        logger.info(f"Video generation completed for '{video.title}' (ID: {video_id})")
    except Exception as e:
        logger.error(f"Error generating video {video_id}: {str(e)}")
        # Update status to failed
        try:
            video = session.get(Video, video_id)
            if video:
                video.status = "failed"
                video.error_message = str(e)
                video.updated_at = datetime.now()
                session.add(video)
                session.commit()
        except Exception as inner_e:
            logger.error(f"Error updating video status: {str(inner_e)}")
    finally:
        session.close()


# ============================================================================
# Video Status & Processing Endpoints
# ============================================================================

@app.get("/api/health")
async def health_check_endpoint():
    """
    Health check endpoint to verify application and database status
    """
    from models.database_connection import health_check, get_connection_info
    
    db_health = health_check()
    db_info = get_connection_info()
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": {
            "status": db_health["status"],
            "connection_type": db_info["connection_type"],
            "message": db_health.get("message", "")
        },
        "application": {
            "name": "Auto Video Generation API",
            "version": "1.0.0"
        }
    }

@app.get("/api/videos/status/{video_id}", response_model=Dict[str, Any])
async def get_video_status(video_id: str, user_id: Optional[str] = None, session: Session = Depends(get_session)):
    video = session.get(Video, video_id)
    if not video:
        raise HTTPException(status_code=404, detail=f"Video with ID {video_id} not found")
    
    # Check user ownership if user_id is provided
    if user_id and video.user_id != user_id:
        raise HTTPException(status_code=403, detail="You don't have permission to access this video")
    
    result = {
        "video_id": video.id,
        "title": video.title,
        "description": video.description,
        "prompt": video.prompt,
        "status": video.status,
        "duration": video.duration,
        "resolution": video.resolution,
        "format": video.format,
        "content_type": video.content_type,
        "style": video.style,
        "audio_type": video.audio_type,
        "aspect_ratio": video.aspect_ratio,
        "fps": video.fps,
        "quality": video.quality,
        "use_ai": video.use_ai,
        "include_audio": video.include_audio,
        "music_type": video.music_type,
        "custom_audio": video.custom_audio,
        "color_grading": video.color_grading,
        "visual_effects": video.visual_effects,
        "transition_effects": video.transition_effects,
        "target_audience": video.target_audience,
        "model": video.model,
        "priority": video.priority,
        "user_id": video.user_id,
        "created_at": video.created_at.isoformat(),
        "updated_at": video.updated_at.isoformat()
    }
    
    if video.output_url and video.status == "completed":
        result["output_url"] = video.output_url
    
    if video.thumbnail:
        result["thumbnail"] = video.thumbnail
        
    if video.error_message and video.status == "failed":
        result["error"] = video.error_message
        
    return result

# ============================================================================
# Celery Task Management Endpoints
# ============================================================================

@app.get("/api/celery/task/{task_id}")
async def get_task_status(task_id: str):
    """Get the status and result of a Celery task"""
    try:
        task_result = celery_app.AsyncResult(task_id)
        
        if task_result.state == 'PENDING':
            response = {
                'task_id': task_id,
                'state': task_result.state,
                'status': 'Task is waiting to be processed'
            }
        elif task_result.state == 'PROGRESS':
            response = {
                'task_id': task_id,
                'state': task_result.state,
                'current_step': task_result.info.get('current_step', 0),
                'total_steps': task_result.info.get('total_steps', 0),
                'status': task_result.info.get('status', 'Processing...')
            }
        elif task_result.state == 'SUCCESS':
            response = {
                'task_id': task_id,
                'state': task_result.state,
                'result': task_result.result
            }
        else:  # FAILURE
            response = {
                'task_id': task_id,
                'state': task_result.state,
                'error': str(task_result.info)
            }
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting task status: {str(e)}")

@app.get("/api/celery/worker/status")
async def get_worker_status():
    """Check if Celery workers are running and their status"""
    try:
        # Get active workers
        inspect = celery_app.control.inspect()
        active_workers = inspect.active()
        registered_tasks = inspect.registered()
        stats = inspect.stats()
        
        if not active_workers:
            return {
                "status": "no_workers",
                "message": "No Celery workers are currently active",
                "workers": [],
                "tasks": []
            }
        
        worker_info = []
        for worker_name, worker_stats in (stats or {}).items():
            worker_info.append({
                "name": worker_name,
                "status": "active",
                "pool": worker_stats.get("pool", {}),
                "rusage": worker_stats.get("rusage", {}),
                "clock": worker_stats.get("clock", 0)
            })
        
        all_tasks = []
        for worker_name, tasks in (registered_tasks or {}).items():
            all_tasks.extend(tasks)
        
        return {
            "status": "active",
            "message": f"Found {len(worker_info)} active worker(s)",
            "workers": worker_info,
            "registered_tasks": list(set(all_tasks))
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error checking worker status: {str(e)}",
            "workers": [],
            "tasks": []
        }

@app.get("/api/videos/{video_id}/processing-status")
async def get_video_processing_status(video_id: str):
    """Get real-time processing status from Redis with enhanced detailed information"""
    try:
        processing_state = VideoProcessingState.get_state(video_id)
        
        if not processing_state:
            # Fallback to database status
            from models.db_models import get_session
            session_gen = get_session()
            session = next(session_gen)
            try:
                video = session.get(Video, video_id)
                if not video:
                    raise HTTPException(status_code=404, detail=f"Video with ID {video_id} not found")
                
                return {
                    "video_id": video_id,
                    "status": f"📋 Video is {video.status}",
                    "source": "database",
                    "current_step": 10 if video.status == "completed" else (0 if video.status == "pending" else 5),
                    "total_steps": 10,
                    "progress_percentage": 100.0 if video.status == "completed" else (0.0 if video.status == "pending" else 50.0),
                    "stage": video.status,
                    "stage_name": video.status.title().replace('_', ' '),
                    "step_details": {
                        "message": f"Video is currently {video.status}",
                        "current_action": "Check back shortly for updates" if video.status == "pending" else "Video ready!" if video.status == "completed" else "Processing..."
                    },
                    "message": f"Video status: {video.status}",
                    "output_url": video.output_url if video.status == "completed" else None,
                    "error": video.error_message if video.status == "failed" else None,
                    "updated_at": video.updated_at.timestamp() if video.updated_at else None,
                    "database_fallback": True,
                    "is_processing": video.status in ["pending", "processing"],
                    "can_redirect": video.status == "completed",
                    "estimated_time_remaining": 0 if video.status == "completed" else 300
                }
            finally:
                session.close()
        
        # Add estimated time remaining based on stage for Redis state
        estimated_remaining = 0
        current_stage = processing_state.get('stage', 'unknown')
        if current_stage in ['initializing', 'script_generation']:
            estimated_remaining = 180  # 3 minutes
        elif current_stage in ['voiceover_generation']:
            estimated_remaining = 120  # 2 minutes  
        elif current_stage in ['social_media_generation', 'media_selection']:
            estimated_remaining = 90   # 1.5 minutes
        elif current_stage in ['video_assembly', 'rendering']:
            estimated_remaining = 60   # 1 minute
        
        # Calculate progress percentage from detailed status if available
        progress_percentage = processing_state.get('progress_percentage')
        if progress_percentage is None:
            # Fallback calculation
            progress_percentage = round((processing_state.get('current_step', 0) / processing_state.get('total_steps', 10)) * 100, 2) if processing_state.get('total_steps', 0) > 0 else 0
        
        # Return enhanced Redis processing state
        return {
            "video_id": video_id,
            "source": "redis",
            "current_step": processing_state.get('current_step', 0),
            "total_steps": processing_state.get('total_steps', 10),
            "status": processing_state.get('status', '🔄 Processing...'),
            "stage": current_stage,
            "stage_name": processing_state.get('stage_name', current_stage.replace('_', ' ').title()),
            "progress_percentage": progress_percentage,
            "step_details": processing_state.get('step_details', {}),
            "updated_at": processing_state.get('updated_at'),
            "task_id": processing_state.get('task_id'),
            "output_url": f"/api/videos/{video_id}/file" if processing_state.get('output_url') and processing_state.get('stage') == 'completed' else processing_state.get('output_url'),
            "error": processing_state.get('error'),
            "completed_at": processing_state.get('completed_at'),
            "failed_at": processing_state.get('failed_at'),
            "estimated_time_remaining": estimated_remaining,
            "is_processing": current_stage not in ['completed', 'failed'],
            "can_redirect": current_stage == 'completed',
            "database_fallback": False
        }
        
    except Exception as e:
        logger.error(f"Error getting processing status for video {video_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting processing status: {str(e)}")

@app.get("/api/videos/{video_id}/processing-history")
async def get_video_processing_history(video_id: str):
    """Get processing history and timeline with detailed status information"""
    try:
        # Get processing state from Redis
        processing_state = VideoProcessingState.get_state(video_id)
        
        # Get final state from database
        from models.db_models import get_session
        session_gen = get_session()
        session = next(session_gen)
        try:
            video = session.get(Video, video_id)
            if not video:
                raise HTTPException(status_code=404, detail=f"Video with ID {video_id} not found")
            
            database_state = {
                "video_id": video.id,
                "title": video.title,
                "status": video.status,
                "created_at": video.created_at.isoformat(),
                "updated_at": video.updated_at.isoformat(),
                "output_url": video.output_url,
                "error_message": video.error_message
            }
        finally:
            session.close()
        
        # Build processing timeline
        timeline = [
            {
                "stage": "created", 
                "timestamp": database_state["created_at"],
                "message": "Video creation request received",
                "source": "database"
            }
        ]
        
        # Calculate processing times
        total_processing_time = None
        start_time = processing_state.get('start_time') if processing_state else None
        
        if start_time:
            current_time = time.time()
            total_processing_time = round(current_time - start_time, 1)
            
            # Add processing start to timeline
            timeline.append({
                "stage": "processing_started",
                "timestamp": datetime.fromtimestamp(start_time).isoformat(),
                "message": "Video generation processing started",
                "source": "redis"
            })
        
        # Add current stage to timeline if available
        if processing_state and processing_state.get('stage') and processing_state.get('updated_at'):
            timeline.append({
                "stage": processing_state.get('stage'),
                "timestamp": datetime.fromtimestamp(processing_state.get('updated_at')).isoformat(),
                "message": processing_state.get('status', 'Processing...'),
                "details": processing_state.get('step_details', {}),
                "progress": processing_state.get('progress_percentage', 0),
                "source": "redis"
            })
        
        # Add final database state if different from processing state
        if not processing_state or processing_state.get('stage') != database_state["status"]:
            timeline.append({
                "stage": database_state["status"],
                "timestamp": database_state["updated_at"],
                "message": f"Final status: {database_state['status']}",
                "source": "database"
            })
        
        return {
            "video_id": video_id,
            "database_state": database_state,
            "processing_state": processing_state if processing_state else None,
            "processing_timeline": timeline,
            "summary": {
                "is_processing": bool(processing_state and processing_state.get('stage') not in ['completed', 'failed']),
                "current_stage": processing_state.get('stage') if processing_state else database_state["status"],
                "progress_percentage": processing_state.get('progress_percentage', 0) if processing_state else (100 if database_state["status"] == "completed" else 0),
                "total_processing_time_seconds": total_processing_time,
                "has_redis_state": bool(processing_state),
                "last_updated": processing_state.get('updated_at') if processing_state else None,
                "can_redirect": (processing_state and processing_state.get('stage') == 'completed') or database_state["status"] == "completed"
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting processing history for video {video_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting processing history: {str(e)}")

# ============================================================================
# Redis Processing State Endpoints
# ============================================================================

@app.delete("/api/videos/{video_id}/processing-state")
async def clear_video_processing_state(video_id: str):
    """Manually clear Redis processing state (admin endpoint)"""
    try:
        VideoProcessingState.delete_state(video_id)
        return {"message": f"Processing state cleared for video {video_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing processing state: {str(e)}")

@app.get("/api/redis/processing/status")
async def get_redis_processing_status():
    """Get overview of all processing states in Redis"""
    try:
        # Get all video processing keys
        pattern = f"{VideoProcessingState.key_prefix}*"
        keys = redis_client.keys(pattern)
        
        active_processing = []
        for key in keys:
            video_id = key.decode().replace(VideoProcessingState.key_prefix, "")
            state = VideoProcessingState.get_state(video_id)
            if state:
                active_processing.append({
                    "video_id": video_id,
                    "status": state.get('status', 'Unknown'),
                    "current_step": state.get('current_step', 0),
                    "total_steps": state.get('total_steps', 10),
                    "progress_percentage": round((state.get('current_step', 0) / state.get('total_steps', 10)) * 100, 2) if state.get('total_steps', 0) > 0 else 0,
                    "updated_at": state.get('updated_at')
                })
        
        return {
            "status": "connected",
            "active_processing_count": len(active_processing),
            "active_processing": active_processing,
            "message": f"Found {len(active_processing)} videos currently processing"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error connecting to Redis: {str(e)}",
            "active_processing_count": 0,
            "active_processing": []
        }

@app.get("/api/redis/processing/{video_id}")
async def get_redis_processing_video(video_id: str):
    """Get Redis processing state for specific video"""
    try:
        processing_state = VideoProcessingState.get_state(video_id)
        
        if not processing_state:
            return {
                "video_id": video_id,
                "found": False,
                "message": "No processing state found in Redis for this video"
            }
        
        return {
            "video_id": video_id,
            "found": True,
            "state": processing_state
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting Redis state: {str(e)}")


# ============================================================================
# Video CRUD Endpoints
# ============================================================================

@app.get("/api/videos", response_model=List[Dict[str, Any]])
async def list_videos(
    skip: int = 0, 
    limit: int = 10, 
    status: Optional[str] = None,
    user_id: Optional[str] = None,
    session: Session = Depends(get_session)
):
    query = select(Video)
    if status:
        query = query.where(Video.status == status)
    if user_id:
        query = query.where(Video.user_id == user_id)
    
    query = query.order_by(Video.created_at.desc())
    videos = session.exec(query.offset(skip).limit(limit)).all()
    
    result = []
    for video in videos:
        video_dict = {
            "id": video.id,
            "title": video.title,
            "description": video.description,
            "status": video.status,
            "content_type": video.content_type,
            "style": video.style,
            "duration": video.duration,
            "user_id": video.user_id,
            "created_at": video.created_at.isoformat(),
            "updated_at": video.updated_at.isoformat(),
        }
        if video.output_url:
            video_dict["output_url"] = video.output_url
        if video.thumbnail:
            video_dict["thumbnail"] = video.thumbnail
        result.append(video_dict)
    
    return result

@app.post("/api/videos", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_video(
    request: Request,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session)
):
    # Parse the request body
    try:
        video_data = await request.json()
        logger.info(f"Received raw video data: {json.dumps(video_data)}")
    except Exception as e:
        logger.error(f"Error parsing request body: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")
    
    try:
        # Use Pydantic validation to handle mixed case fields
        try:
            # Try to parse using VideoCreationRequest model to get benefits of validation
            video_request = VideoCreationRequest(**video_data)
            # Convert to dict for easier access
            snake_case_data = video_request.model_dump(exclude_none=True)
        except Exception as e:
            # If validation fails, fall back to manual conversion
            logger.error(f"Validation error: {str(e)}, falling back to manual conversion")
            snake_case_data = {}
            for key, value in video_data.items():
                # Convert camelCase to snake_case (e.g., contentType -> content_type)
                snake_key = ''.join(['_' + c.lower() if c.isupper() else c for c in key]).lstrip('_')
                snake_case_data[snake_key] = value
        
        logger.info(f"Processed request data: {json.dumps(snake_case_data)}")
        
        # Required fields with defaults
        if not snake_case_data.get("title") and snake_case_data.get("prompt"):
            snake_case_data["title"] = f"Video: {snake_case_data['prompt'][:30]}{'...' if len(snake_case_data['prompt']) > 30 else ''}"
        elif not snake_case_data.get("title"):
            snake_case_data["title"] = "Untitled Video"
            
        if not snake_case_data.get("description") and snake_case_data.get("prompt"):
            snake_case_data["description"] = snake_case_data["prompt"]
        elif not snake_case_data.get("description"):
            snake_case_data["description"] = ""
            
        if not snake_case_data.get("user_id"):
            raise HTTPException(status_code=400, detail="User ID is required")
            
        # No need to verify user existence - we trust the frontend to send valid user IDs
        logger.info(f"Creating video for user_id: {snake_case_data['user_id']}")
        
        # Convert dictionary to Video model with explicit defaults to ensure required fields are present
        new_video = Video(
            title=snake_case_data["title"],  # Now we know this exists from earlier code
            description=snake_case_data.get("description", ""),
            prompt=snake_case_data.get("prompt", ""),
            duration=snake_case_data.get("duration"),
            resolution=snake_case_data.get("resolution", "720p"),
            format=snake_case_data.get("format", "mp4"),
            content_type=snake_case_data.get("content_type", "general"),
            style=snake_case_data.get("style", "standard"),
            audio_type=snake_case_data.get("audio_type", "voiceover"),
            aspect_ratio=snake_case_data.get("aspect_ratio", "16:9"),
            fps=snake_case_data.get("fps", 24),
            quality=snake_case_data.get("quality", "high"),
            use_ai=snake_case_data.get("use_ai", True),
            include_audio=snake_case_data.get("include_audio", True),
            music_type=snake_case_data.get("music_type", "ambient"),
            custom_audio=snake_case_data.get("custom_audio"),
            color_grading=snake_case_data.get("color_grading", "natural"),
            visual_effects=json.dumps(snake_case_data.get("visual_effects", [])) if snake_case_data.get("visual_effects") else None,
            transition_effects=snake_case_data.get("transition_effects", "smooth"),
            target_audience=snake_case_data.get("target_audience", ""),
            script=snake_case_data.get("script", ""),
            media_urls=json.dumps(snake_case_data.get("media_urls", [])) if snake_case_data.get("media_urls") else None,
            background_music=snake_case_data.get("background_music", ""),
            text_overlay_style=snake_case_data.get("text_overlay_style", "minimal"),
            transitions=snake_case_data.get("transitions", "fade"),
            generate_type=snake_case_data.get("generate_type", "full"),
            model=snake_case_data.get("model", "standard"),
            priority=snake_case_data.get("priority", "normal"),
            content_data=json.dumps(snake_case_data.get("content_data", {})) if snake_case_data.get("content_data") else None,
            status=snake_case_data.get("status", "pending"),
            thumbnail=snake_case_data.get("thumbnail", ""),
            user_id=snake_case_data["user_id"]
        )
        
        # Add to database
        try:
            session.add(new_video)
            session.commit()
            session.refresh(new_video)
            logger.info(f"Successfully created video with ID: {new_video.id}")
            # Start video generation task using Celery
            try:
                # Prepare video settings for the Celery task
                video_settings = {
                    "video_id": new_video.id,
                    "title": new_video.title,
                    "description": new_video.description,
                    "prompt": new_video.prompt,
                    "resolution": new_video.resolution,
                    "format": new_video.format,
                    "content_type": new_video.content_type,
                    "style": new_video.style,
                    "duration": new_video.duration
                }
                
                # Prepare frontend data from content_data if available
                frontend_data = None
                if snake_case_data.get("content_data"):
                    frontend_data = snake_case_data["content_data"]
                    logger.info(f"✅ Frontend data available - using provided script/voiceover/media")
                else:
                    logger.info(f"⚠️  No frontend data - will use traditional AI generation")
                
                # Call the Celery task with frontend data
                task = generate_video_task.delay(
                    new_video.user_id, 
                    video_settings, 
                    frontend_data=frontend_data
                )
                logger.info(f"Celery task started with ID: {task.id}")
                
                # Optionally store task ID in database for tracking
                new_video.status = "queued"
                session.commit()
                
            except Exception as e:
                logger.error(f"Error starting Celery task: {e}")
                # Update video status to failed
                new_video.status = "failed"
                new_video.error_message = f"Failed to start background task: {str(e)}"
                session.commit()
                raise HTTPException(status_code=500, detail=f"Failed to start video generation: {str(e)}")
            
            print('task details:', task.id)
                    
            # Return the created video with task ID
            return {
                "video_id": new_video.id,
                "task_id": task.id,
                "title": new_video.title,
                "description": new_video.description,
                "status": new_video.status,
                "created_at": new_video.created_at.isoformat(),
                "message": "Video creation started successfully"
            }
        except Exception as e:
            logger.error(f"Database error when creating video: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Error creating video: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating video: {str(e)}")

@app.delete("/api/videos/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_video(video_id: str, user_id: str, session: Session = Depends(get_session)):
    video = session.get(Video, video_id)
    if not video:
        raise HTTPException(status_code=404, detail=f"Video with ID {video_id} not found")
    
    # Check user ownership
    if video.user_id != user_id:
        raise HTTPException(status_code=403, detail="You don't have permission to delete this video")
    
    # Delete the video record
    session.delete(video)
    session.commit()
    
    # Return no content
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# ============================================================================
# Video File Serving Endpoints
# ============================================================================

@app.get("/api/videos/{video_id}/file")
async def get_video_file(
    video_id: str,
    user_id: Optional[str] = None,
    download: bool = False,
    session: Session = Depends(get_session)
):
    """
    Serve the actual video file for playback.
    """
    video = session.get(Video, video_id)
    if not video:
        raise HTTPException(status_code=404, detail=f"Video with ID {video_id} not found")
    
    # Optional user ownership check
    if user_id and video.user_id != user_id:
        raise HTTPException(status_code=403, detail="You don't have permission to access this video")
    
    if not video.output_url:
        raise HTTPException(status_code=404, detail="Video file not available")
    
    # Check if file exists locally
    if os.path.exists(video.output_url):
        # Determine MIME type
        mime_type, _ = mimetypes.guess_type(video.output_url)
        if not mime_type:
            mime_type = "video/mp4"  # Default fallback
        
        # Set appropriate headers for download or streaming
        headers = {
            "Accept-Ranges": "bytes",
            "Cache-Control": "public, max-age=3600"
        }
        
        # Add download headers if requested
        if download:
            filename = f"video_{video_id}.mp4"
            headers["Content-Disposition"] = f'attachment; filename="{filename}"'
        
        return FileResponse(
            video.output_url,
            media_type=mime_type,
            headers=headers
        )
    else:
        # If it's an external URL, redirect to it
        if video.output_url.startswith(('http://', 'https://')):
            return Response(
                status_code=302,
                headers={"Location": video.output_url}
            )
        else:
            raise HTTPException(status_code=404, detail="Video file not found")

@app.get("/api/videos/{video_id}/thumbnail")
async def get_video_thumbnail(
    video_id: str,
    user_id: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """
    Serve the video thumbnail image.
    """
    video = session.get(Video, video_id)
    if not video:
        raise HTTPException(status_code=404, detail=f"Video with ID {video_id} not found")
    
    # Optional user ownership check
    if user_id and video.user_id != user_id:
        raise HTTPException(status_code=403, detail="You don't have permission to access this video")
    
    if not video.thumbnail:
        raise HTTPException(status_code=404, detail="Thumbnail not available")
    
    # Check if thumbnail exists locally
    if os.path.exists(video.thumbnail):
        mime_type, _ = mimetypes.guess_type(video.thumbnail)
        if not mime_type:
            mime_type = "image/jpeg"  # Default fallback
        
        return FileResponse(
            video.thumbnail,
            media_type=mime_type,
            headers={"Cache-Control": "public, max-age=86400"}  # 24 hours cache
        )
    else:
        # If it's an external URL, redirect to it
        if video.thumbnail.startswith(('http://', 'https://')):
            return Response(
                status_code=302,
                headers={"Location": video.thumbnail}
            )
        else:
            raise HTTPException(status_code=404, detail="Thumbnail not found")

@app.post("/api/videos/{video_id}/regenerate")
async def regenerate_video(
    video_id: str,
    background_tasks: BackgroundTasks,
    user_id: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """
    Regenerate video with the same parameters.
    """
    video = session.get(Video, video_id)
    if not video:
        raise HTTPException(status_code=404, detail=f"Video with ID {video_id} not found")
    
    # Optional user ownership check
    if user_id and video.user_id != user_id:
        raise HTTPException(status_code=403, detail="You don't have permission to regenerate this video")
    
    try:
        # Create new video with same parameters
        new_video_id = str(uuid.uuid4())
        
        # Copy all original video data
        new_video = Video(
            id=new_video_id,
            title=f"{video.title} (Regenerated)",
            description=video.description,
            prompt=video.prompt,
            duration=video.duration,
            resolution=video.resolution,
            format=video.format,
            content_type=video.content_type,
            style=video.style,
            audio_type=video.audio_type,
            aspect_ratio=video.aspect_ratio,
            fps=video.fps,
            quality=video.quality,
            use_ai=video.use_ai,
            include_audio=video.include_audio,
            music_type=video.music_type,
            custom_audio=video.custom_audio,
            color_grading=video.color_grading,
            visual_effects=video.visual_effects,
            transition_effects=video.transition_effects,
            target_audience=video.target_audience,
            script=video.script,
            media_urls=video.media_urls,
            background_music=video.background_music,
            text_overlay_style=video.text_overlay_style,
            transitions=video.transitions,
            generate_type=video.generate_type,
            model=video.model,
            priority=video.priority,
            content_data=video.content_data,  # This contains frontend_data
            status="pending",
            user_id=video.user_id,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        session.add(new_video)
        session.commit()
        session.refresh(new_video)
        
        # Trigger video generation in background
        background_tasks.add_task(generate_video, new_video_id, session)
        
        return {
            "message": "Video regeneration started",
            "original_video_id": video_id,
            "new_video_id": new_video_id,
            "status": "processing"
        }
        
    except Exception as e:
        logger.error(f"Error regenerating video: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error regenerating video: {str(e)}")

@app.put("/api/videos/{video_id}", response_model=Dict[str, Any])
async def update_video_metadata(
    video_id: str,
    request: Request,
    user_id: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """
    Update video metadata (title, description, etc.)
    """
    video = session.get(Video, video_id)
    if not video:
        raise HTTPException(status_code=404, detail=f"Video with ID {video_id} not found")
    
    # Optional user ownership check
    if user_id and video.user_id != user_id:
        raise HTTPException(status_code=403, detail="You don't have permission to update this video")
    
    try:
        update_data = await request.json()
        
        # Update allowed fields
        allowed_fields = ['title', 'description', 'target_audience']
        for field in allowed_fields:
            if field in update_data:
                setattr(video, field, update_data[field])
        
        video.updated_at = datetime.now()
        session.add(video)
        session.commit()
        session.refresh(video)
        
        return {
            "message": "Video updated successfully",
            "video_id": video_id,
            "updated_fields": list(update_data.keys())
        }
        
    except Exception as e:
        logger.error(f"Error updating video: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating video: {str(e)}")

# ============================================================================
# User Video Endpoints
# ============================================================================

@app.get("/api/user/{user_id}/videos", response_model=List[Dict[str, Any]])
async def get_user_videos(
    user_id: str,
    skip: int = 0,
    limit: int = 20,
    status: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """
    Get all videos belonging to a specific user.
    """
    query = select(Video).where(Video.user_id == user_id)
    
    if status:
        query = query.where(Video.status == status)
    
    query = query.order_by(Video.created_at.desc())
    videos = session.exec(query.offset(skip).limit(limit)).all()
    
    result = []
    for video in videos:
        # Parse frontend_data if available
        frontend_data = {}
        if video.content_data:
            try:
                frontend_data = json.loads(video.content_data)
            except json.JSONDecodeError:
                pass
        
        # Build video and thumbnail URLs
        video_url = None
        if video.output_url:
            if video.output_url.startswith(('http://', 'https://')):
                video_url = video.output_url
            else:
                video_url = f"/api/videos/{video.id}/file"
        
        thumbnail_url = None
        if video.thumbnail:
            if video.thumbnail.startswith(('http://', 'https://')):
                thumbnail_url = video.thumbnail
            else:
                thumbnail_url = f"/api/videos/{video.id}/thumbnail"
        
        result.append({
            "id": video.id,
            "title": video.title,
            "description": video.description,
            "video_url": video_url,
            "thumbnail_url": thumbnail_url,
            "duration": video.duration,
            "resolution": video.resolution,
            "format": video.format,
            "content_type": video.content_type,
            "style": video.style,
            "status": video.status,
            "created_at": video.created_at.isoformat(),
            "updated_at": video.updated_at.isoformat(),
            "frontend_data": frontend_data
        })
    
    return result


# ============================================================================
# Health Check Endpoint
# ============================================================================

@app.get("/api/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "routers_loaded": loaded_count
    }


# ============================================================================
# Application Entry Point
# ============================================================================

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
