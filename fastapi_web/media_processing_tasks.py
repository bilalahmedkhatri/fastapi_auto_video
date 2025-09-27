"""
Celery Tasks for Image and Video Processing
Handles asynchronous media processing operations
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import traceback

from celery import Celery
from celery.result import AsyncResult
from celery.exceptions import Retry

# Import the media processor
from media_processor import ImageVideoProcessor, MediaAnalysisResult
from celery_app import celery_app

logger = logging.getLogger(__name__)


class ProcessingState:
    """Media processing state constants"""
    PENDING = 'PENDING'
    STARTED = 'STARTED'
    PROCESSING = 'PROCESSING'
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'
    RETRY = 'RETRY'


@celery_app.task(bind=True, name="process_media_batch")
def process_media_batch(self, media_items: List[Dict[str, Any]], user_id: str = None) -> Dict[str, Any]:
    """
    Process multiple media items asynchronously
    
    Args:
        media_items: List of media items to process
        user_id: Optional user identifier for tracking
        
    Returns:
        Dict with processing results and metadata
    """
    task_id = self.request.id
    logger.info(f"Starting batch media processing task {task_id} for {len(media_items)} items")
    
    try:
        # Update task state
        self.update_state(
            state=ProcessingState.STARTED,
            meta={
                'status': 'Initializing media processor...',
                'progress': 0,
                'total_items': len(media_items),
                'processed_items': 0,
                'current_item': None,
                'user_id': user_id,
                'started_at': datetime.now().isoformat()
            }
        )
        
        # Initialize processor
        processor = ImageVideoProcessor()
        
        # Update state
        self.update_state(
            state=ProcessingState.PROCESSING,
            meta={
                'status': 'Processing media items...',
                'progress': 5,
                'total_items': len(media_items),
                'processed_items': 0,
                'current_item': None,
                'user_id': user_id
            }
        )
        
        # Run async processing in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            results = loop.run_until_complete(processor.analyze_media_batch(media_items))
        finally:
            loop.close()
        
        # Process results and convert to serializable format
        processed_results = {}
        successful_count = 0
        error_count = 0
        
        for media_id, result in results.items():
            # Convert MediaAnalysisResult to dict
            serializable_result = {
                'file_info': result.file_info,
                'technical_specs': result.technical_specs,
                'content_analysis': result.content_analysis,
                'quality_metrics': result.quality_metrics,
                'processing_recommendations': result.processing_recommendations,
                'errors': result.errors,
                'warnings': result.warnings,
                'processed_at': datetime.now().isoformat()
            }
            
            processed_results[media_id] = serializable_result
            
            # Count successes and errors
            if result.errors:
                error_count += 1
            else:
                successful_count += 1
        
        # Final result
        final_result = {
            'task_id': task_id,
            'status': 'completed',
            'results': processed_results,
            'summary': {
                'total_items': len(media_items),
                'successful': successful_count,
                'errors': error_count,
                'success_rate': round((successful_count / len(media_items)) * 100, 1) if media_items else 0
            },
            'completed_at': datetime.now().isoformat(),
            'user_id': user_id
        }
        
        logger.info(f"Batch processing completed: {successful_count} successful, {error_count} errors")
        
        return final_result
        
    except Exception as e:
        logger.error(f"Error in batch processing task {task_id}: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Update task state with error
        self.update_state(
            state=ProcessingState.FAILURE,
            meta={
                'status': 'Processing failed',
                'error': str(e),
                'error_type': type(e).__name__,
                'traceback': traceback.format_exc(),
                'user_id': user_id,
                'failed_at': datetime.now().isoformat()
            }
        )
        
        raise


@celery_app.task(bind=True, name="process_single_media")
def process_single_media(self, media_item: Dict[str, Any], user_id: str = None) -> Dict[str, Any]:
    """
    Process a single media item
    
    Args:
        media_item: Single media item to process
        user_id: Optional user identifier
        
    Returns:
        Processing result for the media item
    """
    task_id = self.request.id
    media_id = media_item.get('id', 'unknown')
    
    logger.info(f"Starting single media processing task {task_id} for item {media_id}")
    
    try:
        # Update task state
        self.update_state(
            state=ProcessingState.STARTED,
            meta={
                'status': f'Processing {media_id}...',
                'progress': 0,
                'media_id': media_id,
                'user_id': user_id,
                'started_at': datetime.now().isoformat()
            }
        )
        
        # Initialize processor
        processor = ImageVideoProcessor()
        
        # Update state
        self.update_state(
            state=ProcessingState.PROCESSING,
            meta={
                'status': f'Analyzing {media_id}...',
                'progress': 25,
                'media_id': media_id,
                'user_id': user_id
            }
        )
        
        # Run async processing
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(processor._analyze_single_media(media_item))
        finally:
            loop.close()
        
        # Update progress
        self.update_state(
            state=ProcessingState.PROCESSING,
            meta={
                'status': f'Finalizing results for {media_id}...',
                'progress': 90,
                'media_id': media_id,
                'user_id': user_id
            }
        )
        
        # Convert result to serializable format
        serializable_result = {
            'task_id': task_id,
            'media_id': media_id,
            'file_info': result.file_info,
            'technical_specs': result.technical_specs,
            'content_analysis': result.content_analysis,
            'quality_metrics': result.quality_metrics,
            'processing_recommendations': result.processing_recommendations,
            'errors': result.errors,
            'warnings': result.warnings,
            'processed_at': datetime.now().isoformat(),
            'user_id': user_id,
            'status': 'error' if result.errors else 'success'
        }
        
        logger.info(f"Single media processing completed for {media_id}")
        
        return serializable_result
        
    except Exception as e:
        logger.error(f"Error in single media processing task {task_id}: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Update task state with error
        self.update_state(
            state=ProcessingState.FAILURE,
            meta={
                'status': f'Processing failed for {media_id}',
                'error': str(e),
                'error_type': type(e).__name__,
                'media_id': media_id,
                'user_id': user_id,
                'failed_at': datetime.now().isoformat()
            }
        )
        
        raise


@celery_app.task(bind=True, name="generate_media_thumbnails")
def generate_media_thumbnails(self, media_items: List[Dict[str, Any]], thumbnail_size: tuple = (150, 150)) -> Dict[str, Any]:
    """
    Generate thumbnails for media items
    
    Args:
        media_items: List of media items
        thumbnail_size: Tuple of (width, height) for thumbnails
        
    Returns:
        Dict with thumbnail generation results
    """
    task_id = self.request.id
    logger.info(f"Starting thumbnail generation task {task_id} for {len(media_items)} items")
    
    try:
        from .media_processor import get_media_thumbnail
        
        # Update task state
        self.update_state(
            state=ProcessingState.STARTED,
            meta={
                'status': 'Generating thumbnails...',
                'progress': 0,
                'total_items': len(media_items),
                'processed_items': 0
            }
        )
        
        thumbnails = {}
        successful_count = 0
        error_count = 0
        
        for i, media_item in enumerate(media_items):
            media_id = media_item.get('id', f'item_{i}')
            media_path = media_item.get('data')  # Assuming data is file path
            
            try:
                # Update progress
                progress = int((i / len(media_items)) * 80) + 10
                self.update_state(
                    state=ProcessingState.PROCESSING,
                    meta={
                        'status': f'Processing {media_id}...',
                        'progress': progress,
                        'total_items': len(media_items),
                        'processed_items': i,
                        'current_item': media_id
                    }
                )
                
                # Generate thumbnail
                thumbnail_bytes = get_media_thumbnail(media_path, thumbnail_size)
                
                if thumbnail_bytes:
                    # Convert to base64 for JSON serialization
                    import base64
                    thumbnail_b64 = base64.b64encode(thumbnail_bytes).decode('utf-8')
                    
                    thumbnails[media_id] = {
                        'status': 'success',
                        'thumbnail': thumbnail_b64,
                        'size': thumbnail_size,
                        'format': 'jpeg'
                    }
                    successful_count += 1
                else:
                    thumbnails[media_id] = {
                        'status': 'error',
                        'error': 'Failed to generate thumbnail'
                    }
                    error_count += 1
                    
            except Exception as e:
                logger.warning(f"Thumbnail generation failed for {media_id}: {e}")
                thumbnails[media_id] = {
                    'status': 'error',
                    'error': str(e)
                }
                error_count += 1
        
        # Final result
        result = {
            'task_id': task_id,
            'status': 'completed',
            'thumbnails': thumbnails,
            'summary': {
                'total_items': len(media_items),
                'successful': successful_count,
                'errors': error_count,
                'success_rate': round((successful_count / len(media_items)) * 100, 1) if media_items else 0
            },
            'completed_at': datetime.now().isoformat()
        }
        
        logger.info(f"Thumbnail generation completed: {successful_count} successful, {error_count} errors")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in thumbnail generation task {task_id}: {str(e)}")
        
        # Update task state with error
        self.update_state(
            state=ProcessingState.FAILURE,
            meta={
                'status': 'Thumbnail generation failed',
                'error': str(e),
                'failed_at': datetime.now().isoformat()
            }
        )
        
        raise


@celery_app.task(bind=True, name="cleanup_temp_files")
def cleanup_temp_files(self, temp_file_paths: List[str], max_age_hours: int = 24) -> Dict[str, Any]:
    """
    Clean up temporary files created during processing
    
    Args:
        temp_file_paths: List of temporary file paths to clean up
        max_age_hours: Maximum age of files to keep (in hours)
        
    Returns:
        Cleanup result summary
    """
    task_id = self.request.id
    logger.info(f"Starting cleanup task {task_id} for {len(temp_file_paths)} files")
    
    try:
        import os
        import time
        from pathlib import Path
        
        cleaned_count = 0
        error_count = 0
        skipped_count = 0
        
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        for file_path in temp_file_paths:
            try:
                path = Path(file_path)
                
                if not path.exists():
                    skipped_count += 1
                    continue
                
                # Check file age
                file_age = current_time - path.stat().st_mtime
                
                if file_age > max_age_seconds:
                    path.unlink()  # Delete file
                    cleaned_count += 1
                    logger.debug(f"Cleaned up temp file: {file_path}")
                else:
                    skipped_count += 1
                    
            except Exception as e:
                logger.warning(f"Error cleaning up {file_path}: {e}")
                error_count += 1
        
        result = {
            'task_id': task_id,
            'status': 'completed',
            'summary': {
                'total_files': len(temp_file_paths),
                'cleaned': cleaned_count,
                'errors': error_count,
                'skipped': skipped_count
            },
            'completed_at': datetime.now().isoformat()
        }
        
        logger.info(f"Cleanup completed: {cleaned_count} cleaned, {error_count} errors, {skipped_count} skipped")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in cleanup task {task_id}: {str(e)}")
        
        self.update_state(
            state=ProcessingState.FAILURE,
            meta={
                'status': 'Cleanup failed',
                'error': str(e),
                'failed_at': datetime.now().isoformat()
            }
        )
        
        raise


# Helper functions for task management
def get_task_status(task_id: str) -> Dict[str, Any]:
    """Get the status of a processing task"""
    try:
        result = AsyncResult(task_id, app=celery_app)
        
        return {
            'task_id': task_id,
            'status': result.status,
            'result': result.result,
            'info': result.info,
            'ready': result.ready(),
            'successful': result.successful(),
            'failed': result.failed()
        }
        
    except Exception as e:
        logger.error(f"Error getting task status for {task_id}: {e}")
        return {
            'task_id': task_id,
            'status': 'UNKNOWN',
            'error': str(e)
        }


def cancel_task(task_id: str) -> bool:
    """Cancel a running task"""
    try:
        celery_app.control.revoke(task_id, terminate=True)
        logger.info(f"Task {task_id} cancelled")
        return True
    except Exception as e:
        logger.error(f"Error cancelling task {task_id}: {e}")
        return False


def get_active_tasks() -> List[Dict[str, Any]]:
    """Get list of active tasks"""
    try:
        inspect = celery_app.control.inspect()
        active_tasks = inspect.active()
        
        if active_tasks:
            all_tasks = []
            for worker, tasks in active_tasks.items():
                for task in tasks:
                    all_tasks.append({
                        'worker': worker,
                        'task_id': task['id'],
                        'name': task['name'],
                        'args': task['args'],
                        'kwargs': task['kwargs'],
                        'time_start': task.get('time_start')
                    })
            return all_tasks
        
        return []
        
    except Exception as e:
        logger.error(f"Error getting active tasks: {e}")
        return []


# Task routing and configuration
def setup_task_routes():
    """Setup task routing configuration"""
    celery_app.conf.task_routes = {
        'process_media_batch': {'queue': 'media_processing'},
        'process_single_media': {'queue': 'media_processing'},
        'generate_media_thumbnails': {'queue': 'thumbnails'},
        'cleanup_temp_files': {'queue': 'cleanup'}
    }
    
    # Task time limits (in seconds)
    celery_app.conf.task_time_limit = {
        'process_media_batch': 1800,  # 30 minutes
        'process_single_media': 300,   # 5 minutes
        'generate_media_thumbnails': 600,  # 10 minutes
        'cleanup_temp_files': 120      # 2 minutes
    }


# Initialize task routes on import
setup_task_routes()


# Example usage
if __name__ == "__main__":
    # Example of how to use these tasks
    
    # Start batch processing
    media_items = [
        {'id': 'img1', 'data': 'path/to/image1.jpg', 'type': 'image'},
        {'id': 'vid1', 'data': 'path/to/video1.mp4', 'type': 'video'}
    ]
    
    # Submit task
    task = process_media_batch.delay(media_items, user_id="user123")
    print(f"Submitted batch processing task: {task.id}")
    
    # Check status
    status = get_task_status(task.id)
    print(f"Task status: {status}")