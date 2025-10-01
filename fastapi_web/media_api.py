"""
FastAPI endpoints for media processing and analysis
"""

import logging
import tempfile
import base64
import mimetypes
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from sqlmodel import Session, select

# Import database and Celery tasks
from models.db_models import get_session
from media_processing_tasks import (
    process_media_batch,
    process_single_media,
    generate_media_thumbnails,
    get_task_status,
    cancel_task,
    get_active_tasks
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/media", tags=["media-processing"])


# Pydantic models for request/response
class MediaItem(BaseModel):
    """Media item for processing"""
    id: str
    data: str  # File path, base64 data URL, or upload ID
    type: str = Field(..., pattern="^(image|video)$")
    metadata: Optional[Dict[str, Any]] = {}


class BatchProcessingRequest(BaseModel):
    """Request model for batch processing"""
    media_items: List[MediaItem]
    user_id: Optional[str] = None
    processing_options: Optional[Dict[str, Any]] = {}


class ProcessingResponse(BaseModel):
    """Response model for processing requests"""
    task_id: str
    status: str
    message: str
    estimated_completion_time: Optional[str] = None


class TaskStatusResponse(BaseModel):
    """Response model for task status"""
    task_id: str
    status: str
    progress: Optional[int] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


class MediaAnalysisResult(BaseModel):
    """Media analysis result model"""
    media_id: str
    file_info: Dict[str, Any]
    technical_specs: Dict[str, Any]
    content_analysis: Dict[str, Any]
    quality_metrics: Dict[str, Any]
    processing_recommendations: Dict[str, Any]
    errors: List[str]
    warnings: List[str]
    processed_at: str


@router.post("/upload", response_model=Dict[str, Any])
async def upload_media_files(
    files: List[UploadFile] = File(...),
    user_id: Optional[str] = Form(None),
    auto_process: bool = Form(False),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Upload media files and optionally start processing
    
    Args:
        files: List of uploaded files
        user_id: Optional user identifier
        auto_process: Whether to automatically start processing
        background_tasks: Background tasks handler
        
    Returns:
        Upload results and optional processing task info
    """
    logger.info(f"Uploading {len(files)} files for user {user_id}")
    
    try:
        uploaded_files = []
        temp_files = []
        
        # Process each uploaded file
        for file in files:
            # Validate file type
            content_type = file.content_type or 'application/octet-stream'
            
            if not content_type.startswith(('image/', 'video/')):
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type: {content_type}"
                )
            
            # Create temporary file
            suffix = Path(file.filename).suffix if file.filename else '.tmp'
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            temp_files.append(temp_file.name)
            
            try:
                # Write file content
                content = await file.read()
                temp_file.write(content)
                temp_file.close()
                
                # Create media item
                media_item = {
                    'id': f"{file.filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    'data': temp_file.name,
                    'type': 'image' if content_type.startswith('image/') else 'video',
                    'original_filename': file.filename,
                    'content_type': content_type,
                    'size_bytes': len(content),
                    'temp_file': temp_file.name
                }
                
                uploaded_files.append(media_item)
                
            except Exception as e:
                logger.error(f"Error processing file {file.filename}: {e}")
                # Clean up temp file on error
                try:
                    Path(temp_file.name).unlink()
                except:
                    pass
                raise HTTPException(
                    status_code=500,
                    detail=f"Error processing file {file.filename}: {str(e)}"
                )
        
        response_data = {
            'status': 'success',
            'uploaded_files': len(uploaded_files),
            'files': [
                {
                    'id': item['id'],
                    'filename': item['original_filename'],
                    'type': item['type'],
                    'size_bytes': item['size_bytes']
                }
                for item in uploaded_files
            ],
            'uploaded_at': datetime.now().isoformat()
        }
        
        # Optionally start processing
        if auto_process and uploaded_files:
            logger.info(f"Auto-starting processing for {len(uploaded_files)} files")
            
            # Prepare media items for processing
            media_items = [
                {
                    'id': item['id'],
                    'data': item['data'],
                    'type': item['type']
                }
                for item in uploaded_files
            ]
            
            # Start batch processing task
            task = process_media_batch.delay(media_items, user_id)
            
            response_data['processing'] = {
                'task_id': task.id,
                'status': 'started',
                'message': 'Processing started automatically'
            }
            
            # Schedule cleanup of temp files
            background_tasks.add_task(
                _schedule_temp_file_cleanup,
                temp_files,
                delay_hours=2
            )
        else:
            # Schedule cleanup for later
            background_tasks.add_task(
                _schedule_temp_file_cleanup,
                temp_files,
                delay_hours=24
            )
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/process/batch", response_model=ProcessingResponse)
async def start_batch_processing(request: BatchProcessingRequest):
    """
    Start batch processing of media items
    
    Args:
        request: Batch processing request with media items
        
    Returns:
        Processing task information
    """
    logger.info(f"Starting batch processing for {len(request.media_items)} items")
    
    try:
        if not request.media_items:
            raise HTTPException(status_code=400, detail="No media items provided")
        
        # Convert Pydantic models to dicts
        media_items = [item.dict() for item in request.media_items]
        
        # Start Celery task
        task = process_media_batch.delay(media_items, request.user_id)
        
        # Estimate completion time (rough calculation)
        estimated_seconds = len(media_items) * 30  # ~30 seconds per item
        estimated_completion = datetime.now().timestamp() + estimated_seconds
        
        # Minimal update: mark 'media' step as completed in VideoGenerationProcess if active
        try:
            from models.db_models import VideoGenerationProcess
            from models.video_process_manager import VideoGenerationProcessManager
            if request.user_id and VideoGenerationProcess:
                process_query = select(VideoGenerationProcess).where(
                    VideoGenerationProcess.user_id == request.user_id,
                    VideoGenerationProcess.status == "active"
                ).order_by(VideoGenerationProcess.started_at.desc())
                session = next(get_session())
                active_process = session.exec(process_query).first()
                if active_process:
                    manager = VideoGenerationProcessManager(session)
                    if manager.load_process(active_process.id):
                        manager.update_step_progress(
                            step_name="media",
                            status="completed",
                            data={"media_count": len(media_items) if 'media_items' in locals() else 1}
                        )
        except Exception as step_error:
            logger.warning(f"Failed to update process step for media: {step_error}")
        
        return ProcessingResponse(
            task_id=task.id,
            status="started",
            message=f"Batch processing started for {len(media_items)} items",
            estimated_completion_time=datetime.fromtimestamp(estimated_completion).isoformat()
        )
        
    except Exception as e:
        logger.error(f"Batch processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/process/single", response_model=ProcessingResponse)
async def start_single_processing(media_item: MediaItem, user_id: Optional[str] = None):
    """
    Start processing of a single media item
    
    Args:
        media_item: Media item to process
        user_id: Optional user identifier
        
    Returns:
        Processing task information
    """
    logger.info(f"Starting single processing for item {media_item.id}")
    
    try:
        # Start Celery task
        task = process_single_media.delay(media_item.dict(), user_id)
        
        # Minimal update: mark 'media' step as completed in VideoGenerationProcess if active
        try:
            from models.db_models import VideoGenerationProcess
            from models.video_process_manager import VideoGenerationProcessManager
            if user_id and VideoGenerationProcess:
                process_query = select(VideoGenerationProcess).where(
                    VideoGenerationProcess.user_id == user_id,
                    VideoGenerationProcess.status == "active"
                ).order_by(VideoGenerationProcess.started_at.desc())
                session = next(get_session())
                active_process = session.exec(process_query).first()
                if active_process:
                    manager = VideoGenerationProcessManager(session)
                    if manager.load_process(active_process.id):
                        manager.update_step_progress(
                            step_name="media",
                            status="completed",
                            data={"media_count": 1}
                        )
        except Exception as step_error:
            logger.warning(f"Failed to update process step for media: {step_error}")
        
        return ProcessingResponse(
            task_id=task.id,
            status="started",
            message=f"Processing started for {media_item.id}"
        )
        
    except Exception as e:
        logger.error(f"Single processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/task/{task_id}/status", response_model=TaskStatusResponse)
async def get_processing_status(task_id: str):
    """
    Get the status of a processing task
    
    Args:
        task_id: Task identifier
        
    Returns:
        Task status information
    """
    try:
        status_info = get_task_status(task_id)
        
        response = TaskStatusResponse(
            task_id=task_id,
            status=status_info['status'],
            result=status_info.get('result'),
            error=status_info.get('info', {}).get('error') if status_info['status'] == 'FAILURE' else None
        )
        
        # Add additional info if available
        if isinstance(status_info.get('info'), dict):
            info = status_info['info']
            response.progress = info.get('progress')
            response.started_at = info.get('started_at')
            response.completed_at = info.get('completed_at')
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting task status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/task/{task_id}/result")
async def get_processing_result(task_id: str):
    """
    Get the complete result of a processing task
    
    Args:
        task_id: Task identifier
        
    Returns:
        Complete processing results
    """
    try:
        status_info = get_task_status(task_id)
        
        if not status_info['ready']:
            raise HTTPException(
                status_code=202,
                detail="Task is still processing"
            )
        
        if status_info['failed']:
            raise HTTPException(
                status_code=500,
                detail=f"Task failed: {status_info.get('result', 'Unknown error')}"
            )
        
        return status_info['result']
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task result: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/task/{task_id}")
async def cancel_processing_task(task_id: str):
    """
    Cancel a running processing task
    
    Args:
        task_id: Task identifier
        
    Returns:
        Cancellation result
    """
    try:
        success = cancel_task(task_id)
        
        if success:
            return {"message": f"Task {task_id} cancelled successfully"}
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to cancel task {task_id}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/active")
async def get_active_processing_tasks():
    """
    Get list of currently active processing tasks
    
    Returns:
        List of active tasks
    """
    try:
        active_tasks = get_active_tasks()
        
        return {
            'active_tasks': len(active_tasks),
            'tasks': active_tasks
        }
        
    except Exception as e:
        logger.error(f"Error getting active tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/thumbnails/generate", response_model=ProcessingResponse)
async def generate_thumbnails(
    media_items: List[MediaItem],
    thumbnail_size: Optional[List[int]] = [150, 150]
):
    """
    Generate thumbnails for media items
    
    Args:
        media_items: List of media items
        thumbnail_size: Thumbnail dimensions [width, height]
        
    Returns:
        Thumbnail generation task information
    """
    logger.info(f"Starting thumbnail generation for {len(media_items)} items")
    
    try:
        if not media_items:
            raise HTTPException(status_code=400, detail="No media items provided")
        
        # Convert to dicts and validate thumbnail size
        media_dicts = [item.dict() for item in media_items]
        size_tuple = tuple(thumbnail_size) if len(thumbnail_size) == 2 else (150, 150)
        
        # Start Celery task
        task = generate_media_thumbnails.delay(media_dicts, size_tuple)
        
        return ProcessingResponse(
            task_id=task.id,
            status="started",
            message=f"Thumbnail generation started for {len(media_items)} items"
        )
        
    except Exception as e:
        logger.error(f"Thumbnail generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analyze/{media_id}")
async def get_media_analysis(
    media_id: str,
    session: Session = Depends(get_session)
):
    """
    Get analysis results for a specific media item
    
    Args:
        media_id: Media identifier
        session: Database session
        
    Returns:
        Media analysis results
    """
    try:
        # This would typically query your database for stored analysis results
        # For now, return a placeholder response
        
        # TODO: Implement database storage and retrieval of analysis results
        
        return {
            'message': 'Media analysis retrieval not yet implemented',
            'media_id': media_id,
            'note': 'Analysis results should be stored in database after processing'
        }
        
    except Exception as e:
        logger.error(f"Error retrieving analysis for {media_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """
    Health check endpoint for media processing service
    
    Returns:
        Service health status
    """
    try:
        # Check if Celery is running
        active_tasks = get_active_tasks()
        
        return {
            'status': 'healthy',
            'service': 'media-processing',
            'celery_active': True,
            'active_tasks': len(active_tasks),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.warning(f"Health check warning: {e}")
        return {
            'status': 'degraded',
            'service': 'media-processing',
            'celery_active': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


# Helper functions
async def _schedule_temp_file_cleanup(file_paths: List[str], delay_hours: int = 24):
    """Schedule cleanup of temporary files"""
    try:
        from .media_processing_tasks import cleanup_temp_files
        
        # Schedule cleanup task
        cleanup_temp_files.apply_async(
            args=[file_paths, delay_hours],
            countdown=delay_hours * 3600  # Convert hours to seconds
        )
        
        logger.info(f"Scheduled cleanup for {len(file_paths)} temp files in {delay_hours} hours")
        
    except Exception as e:
        logger.error(f"Error scheduling temp file cleanup: {e}")


def _validate_media_file(file_path: str) -> bool:
    """Validate that a media file exists and is accessible"""
    try:
        path = Path(file_path)
        return path.exists() and path.is_file()
    except Exception:
        return False


def _get_file_info(file_path: str) -> Dict[str, Any]:
    """Get basic file information"""
    try:
        path = Path(file_path)
        stat = path.stat()
        
        return {
            'filename': path.name,
            'size_bytes': stat.st_size,
            'modified_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'extension': path.suffix.lower()
        }
        
    except Exception as e:
        logger.error(f"Error getting file info for {file_path}: {e}")
        return {}


# Export router for main app
__all__ = ['router']