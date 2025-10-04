import time, os, json
from datetime import datetime
from celery import Celery
from dotenv import load_dotenv
import redis
from models.db_models import Video, get_session

# Import video builder function at module level
try:
    from video_builder.video_builder import generate_video_from_frontend
    VIDEO_BUILDER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import video_builder: {e}")
    VIDEO_BUILDER_AVAILABLE = False
    generate_video_from_frontend = None

# Load environment variables from a .env file if present
load_dotenv()

# Redis connection for processing state management
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=2,  # Use db=2 for processing state (separate from Celery broker/result)
    decode_responses=True
)

class VideoProcessingState:
    """Helper class to manage video processing state in Redis"""
    
    key_prefix = "video:processing:"
    
    @staticmethod
    def get_key(video_id: str) -> str:
        """Generate Redis key for video processing state"""
        return f"{VideoProcessingState.key_prefix}{video_id}"
    
    @staticmethod
    def set_state(video_id: str, state_data: dict, expire_seconds: int = 3600):
        """Store processing state in Redis"""
        key = VideoProcessingState.get_key(video_id)
        redis_client.setex(key, expire_seconds, json.dumps(state_data))
    
    @staticmethod
    def get_state(video_id: str) -> dict:
        """Get processing state from Redis"""
        key = VideoProcessingState.get_key(video_id)
        data = redis_client.get(key)
        return json.loads(data) if data else {}
    
    @staticmethod
    def delete_state(video_id: str):
        """Delete processing state from Redis"""
        key = VideoProcessingState.get_key(video_id)
        redis_client.delete(key)
    
    @staticmethod
    def update_progress(video_id: str, current_step: int, total_steps: int, status: str, **extra_data):
        """Update processing progress"""
        state_data = {
            'current_step': current_step,
            'total_steps': total_steps,
            'status': status,
            'progress_percentage': round((current_step / total_steps) * 100, 1),
            'updated_at': time.time(),
            **extra_data
        }
        VideoProcessingState.set_state(video_id, state_data)
        
    @staticmethod
    def update_detailed_status(video_id: str, stage: str, status: str, step_details: dict = None, **extra_data):
        """Update detailed processing status with stage information"""
        # Get current state to preserve data
        current_state = VideoProcessingState.get_state(video_id)
        
        # Define stage mapping
        stage_mapping = {
            'initializing': {'step': 1, 'total': 10, 'name': 'Initializing'},
            'script_generation': {'step': 2, 'total': 10, 'name': 'Script Generation'},
            'voiceover_generation': {'step': 4, 'total': 10, 'name': 'Voiceover Creation'},
            'social_media_generation': {'step': 6, 'total': 10, 'name': 'Social Media Optimization'},
            'media_selection': {'step': 7, 'total': 10, 'name': 'Media Selection'},
            'video_assembly': {'step': 8, 'total': 10, 'name': 'Video Assembly'},
            'rendering': {'step': 9, 'total': 10, 'name': 'Final Rendering'},
            'completed': {'step': 10, 'total': 10, 'name': 'Completed'},
            'failed': {'step': -1, 'total': 10, 'name': 'Failed'}
        }
        
        stage_info = stage_mapping.get(stage, {'step': current_state.get('current_step', 0), 'total': 10, 'name': stage.title()})
        
        state_data = {
            'current_step': stage_info['step'],
            'total_steps': stage_info['total'],
            'progress_percentage': round((stage_info['step'] / stage_info['total']) * 100, 1) if stage_info['step'] > 0 else 0,
            'status': status,
            'stage': stage,
            'stage_name': stage_info['name'],
            'step_details': step_details or {},
            'updated_at': time.time(),
            **extra_data
        }
        
        VideoProcessingState.set_state(video_id, state_data)

# Define the Redis broker and backend URLs with defaults
# Assumes Redis is running on the default host (localhost) and port (6379).
# db=0 is the broker, where tasks are sent.
# db=1 is the backend, where results and statuses are stored.
# Using different DB numbers is a good practice to keep them separate.
broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
result_backend_url = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')

# Create a Celery instance
# The first argument 'video_tasks' is the name of the current module.
# This name is used to automatically generate task names.
celery_app = Celery(
    'video_tasks',
    broker=broker_url,
    backend=result_backend_url,
    include=['celery_app', 'video_process_tasks']  # Include modules for task discovery
)

# Configure Celery settings for better visibility and management.
celery_app.conf.update(
    task_track_started=True,
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    result_expires=3600,  # Results expire after 1 hour
    timezone='UTC',
    enable_utc=True,    
    # Windows-specific settings to fix permission issues
    worker_pool='solo',  # Use solo pool for Windows compatibility
    worker_concurrency=1,  # Single worker process
    worker_prefetch_multiplier=1,  # Process one task at a time
    task_acks_late=True,  # Acknowledge tasks after completion
    task_reject_on_worker_lost=True,  # Reject tasks if worker is lost
)

# 3. Register the 'generate_video' function as a Celery task.
#    The '@celery_app.task' decorator tells Celery that this function
#    is a task that can be executed by a worker.
#    The 'bind=True' argument makes the task instance (self) available
#    as the first argument to the function. This is useful for updating
#    the task's state.
@celery_app.task(bind=True)
def generate_video(self, user_id: str, video_settings: dict, frontend_data: dict = None):
    """
    Enhanced video generation task with detailed status tracking.
    
    Args:
        user_id: User ID requesting video generation
        video_settings: Video configuration settings
        frontend_data: Optional frontend-provided data (script, voiceover, media, etc.)
                      If provided, uses frontend data instead of generating from scratch
    """
    video_id = video_settings.get('video_id')
    
    try:
        # --- Stage 1: Initialize ---
        VideoProcessingState.update_detailed_status(
            video_id=video_id,
            stage="initializing",
            status="🚀 Initializing video generation process...",
            step_details={
                "message": "Setting up video generation environment",
                "estimated_time": "10-15 seconds",
                "current_action": "Preparing workspace"
            },
            task_id=self.request.id,
            user_id=user_id,
            video_settings=video_settings,
            start_time=time.time()
        )
        
        # Update database status to "processing" (single DB update)
        if video_id:
            session_gen = get_session()
            session = next(session_gen)
            try:
                video = session.get(Video, video_id)
                if not video:
                    print(f"Warning: Video with ID {video_id} not found in database. Continuing with task.")
                else:
                    video.status = "processing"
                    session.commit()
            finally:
                session.close()
        
        print(f"Task {self.request.id}: Started processing video {video_id} for user {user_id}")
        time.sleep(2)  # Brief pause for initialization

        # Determine processing path based on data source
        if frontend_data:
            # --- Frontend Data Path (Script/Voiceover/Social Media Already Generated) ---
            VideoProcessingState.update_detailed_status(
                video_id=video_id,
                stage="script_generation",
                status="✅ Using provided script content",
                step_details={
                    "message": "Script already generated by user",
                    "script_title": frontend_data.get('script_data', {}).get('title', 'Generated Script'),
                    "current_action": "Processing script data"
                }
            )
            time.sleep(1)
            
            VideoProcessingState.update_detailed_status(
                video_id=video_id,
                stage="voiceover_generation", 
                status="✅ Using provided voiceover audio",
                step_details={
                    "message": "Voiceover already generated by user",
                    "voice_model": frontend_data.get('voiceover_data', {}).get('voice_model', 'Selected Voice'),
                    "current_action": "Processing audio file"
                }
            )
            time.sleep(1)
            
            VideoProcessingState.update_detailed_status(
                video_id=video_id,
                stage="social_media_generation",
                status="✅ Using provided social media content",
                step_details={
                    "message": "Social media content already optimized",
                    "platforms": len(frontend_data.get('social_media_data', {}).get('platform_descriptions', [])),
                    "current_action": "Processing social media data"
                }
            )
            time.sleep(1)
            
            # Generate video from frontend data
            video_output_path = _generate_video_from_frontend_data(
                frontend_data, video_id, user_id, video_settings
            )
            
        else:
            # --- Traditional AI Generation Path ---
            VideoProcessingState.update_detailed_status(
                video_id=video_id,
                stage="script_generation",
                status="🤖 Generating AI script content...",
                step_details={
                    "message": "Creating engaging video script with AI",
                    "estimated_time": "30-45 seconds",
                    "current_action": "Analyzing prompt and generating content"
                }
            )
            time.sleep(3)
            
            VideoProcessingState.update_detailed_status(
                video_id=video_id,
                stage="voiceover_generation",
                status="🎵 Creating AI voiceover audio...",
                step_details={
                    "message": "Generating professional voiceover",
                    "estimated_time": "60-90 seconds",
                    "current_action": "Processing text-to-speech conversion"
                }
            )
            time.sleep(5)
            
            VideoProcessingState.update_detailed_status(
                video_id=video_id,
                stage="social_media_generation",
                status="📱 Optimizing for social media platforms...",
                step_details={
                    "message": "Creating platform-specific content",
                    "estimated_time": "20-30 seconds",
                    "current_action": "Generating hashtags and descriptions"
                }
            )
            time.sleep(2)
            
            # Generate using traditional AI method
            video_output_path = _generate_video_traditional(
                video_id, user_id, video_settings
            )

        # --- Final Stages (Common for both paths) ---
        VideoProcessingState.update_detailed_status(
            video_id=video_id,
            stage="video_assembly",
            status="🎬 Assembling final video...",
            step_details={
                "message": "Combining all elements into final video",
                "estimated_time": "45-60 seconds", 
                "current_action": "Rendering video with effects and transitions"
            }
        )
        
        VideoProcessingState.update_detailed_status(
            video_id=video_id,
            stage="rendering",
            status="⚡ Final rendering and optimization...",
            step_details={
                "message": "Applying final touches and optimization",
                "estimated_time": "30-45 seconds",
                "current_action": "Encoding and finalizing video file"
            }
        )
        time.sleep(3)

        # Get final video URL - Convert local path to HTTP URL
        if 'video_output_path' in locals() and video_output_path:
            # Store the local file path in database but return HTTP URL
            local_file_path = video_output_path
            # Create HTTP URL for the video file endpoint
            video_url = f"/api/videos/{video_id}/file"
        else:
            video_url = f"/api/videos/{video_id}/file"
        
        # --- Completion ---
        VideoProcessingState.update_detailed_status(
            video_id=video_id,
            stage="completed",
            status="🎉 Video generation completed successfully!",
            step_details={
                "message": "Video is ready for viewing",
                "output_url": video_url,
                "total_time": time.time() - VideoProcessingState.get_state(video_id).get('start_time', time.time()),
                "current_action": "Ready to view video"
            },
            output_url=video_url,
            completed_at=time.time()
        )
        
        # Update database with final result
        if video_id:
            session_gen = get_session()
            session = next(session_gen)
            try:
                video = session.get(Video, video_id)
                if video:
                    video.status = "completed"
                    # Store the local file path for serving, not the HTTP URL
                    if 'local_file_path' in locals() and local_file_path:
                        video.output_url = local_file_path
                    else:
                        video.output_url = video_url
                    video.updated_at = datetime.now()
                    session.commit()
                else:
                    print(f"Warning: Video {video_id} not found for completion update")
            finally:
                session.close()
        
        print(f"Task {self.request.id}: Video generation completed for {video_id}")
        
        return {
            'video_id': video_id,
            'status': 'completed',
            'output_url': video_url,
            'task_id': self.request.id
        }
            
    except Exception as e:
        error_message = str(e)
        print(f"Task {self.request.id}: Error processing video {video_id}: {error_message}")
        
        # Store error state in Redis with detailed error information
        VideoProcessingState.update_detailed_status(
            video_id=video_id,
            stage="failed",
            status=f"❌ Video generation failed: {error_message}",
            step_details={
                "message": "An error occurred during video generation",
                "error_details": error_message,
                "current_action": "Please try again or contact support",
                "failed_at": time.time()
            },
            error=error_message,
            failed_at=time.time()
        )
        
        # Update database with failure status
        try:
            session_gen = get_session()
            session = next(session_gen)
            video = session.get(Video, video_id)
            if video:
                video.status = "failed"
                video.error_message = error_message
                session.commit()
            session.close()
        except Exception as db_error:
            print(f"Failed to update database with error status: {db_error}")
        
        # Update Celery task state
        self.update_state(
            state='FAILURE',
            meta={'exc_type': type(e).__name__, 'exc_message': error_message, 'status': 'Task failed.'}
        )
        raise

def _generate_video_from_frontend_data(frontend_data: dict, video_id: str, user_id: str, video_settings: dict):
    """
    Generate video using frontend-provided data (scripts, voiceover, media, etc.)
    """
    if not VIDEO_BUILDER_AVAILABLE:
        raise ImportError("video_builder module is not available")
    
    if not generate_video_from_frontend:
        raise ImportError("generate_video_from_frontend function is not available")
    
    # Update status for media selection phase
    VideoProcessingState.update_detailed_status(
        video_id=video_id,
        stage="media_selection",
        status="🖼️ Processing and selecting media files...",
        step_details={
            "message": "Analyzing and preparing media content",
            "media_count": len(frontend_data.get('media_data', {}).get('selected_media', [])),
            "current_action": "Loading media files and checking compatibility"
        }
    )
    
    # Custom progress callback for video generation
    def detailed_progress_callback(step, message):
        # Map generic steps to detailed stages
        if "assembling" in message.lower() or "combining" in message.lower():
            VideoProcessingState.update_detailed_status(
                video_id=video_id,
                stage="video_assembly", 
                status=f"🎞️ {message}",
                step_details={
                    "message": message,
                    "current_action": "Building video timeline and adding transitions"
                }
            )
        elif "rendering" in message.lower() or "encoding" in message.lower():
            VideoProcessingState.update_detailed_status(
                video_id=video_id,
                stage="rendering",
                status=f"⚡ {message}",
                step_details={
                    "message": message,
                    "current_action": "Encoding final video file"
                }
            )
        else:
            VideoProcessingState.update_detailed_status(
                video_id=video_id,
                stage="video_assembly",
                status=f"🎬 {message}",
                step_details={
                    "message": message,
                    "current_action": "Processing video components"
                }
            )
    
    # Call the modified video builder with frontend data
    output_path = generate_video_from_frontend(
        script_data=frontend_data.get('script_data', {}),
        voiceover_data=frontend_data.get('voiceover_data', {}),
        social_media_data=frontend_data.get('social_media_data', {}),
        media_data=frontend_data.get('media_data', {}),
        video_effects_config=frontend_data.get('video_effects_config', {}),
        user_id=user_id,
        video_id=video_id,
        progress_callback=detailed_progress_callback
    )
    
    return output_path

def _generate_video_traditional(video_id: str, user_id: str, video_settings: dict):
    """
    Traditional video generation using AI (original logic with detailed status tracking)
    """
    # Media Selection Phase
    VideoProcessingState.update_detailed_status(
        video_id=video_id,
        stage="media_selection",
        status="🔍 Searching and downloading media content...",
        step_details={
            "message": "Finding relevant images and videos for your topic",
            "estimated_time": "45-60 seconds",
            "current_action": "Searching media databases"
        }
    )
    time.sleep(4)
    
    # Video Assembly Phase
    VideoProcessingState.update_detailed_status(
        video_id=video_id,
        stage="video_assembly",
        status="🎞️ Assembling video components...",
        step_details={
            "message": "Combining script, voiceover, and media into video",
            "estimated_time": "60-90 seconds", 
            "current_action": "Creating video timeline and adding transitions"
        }
    )
    time.sleep(6)
    
    # Rendering Phase
    VideoProcessingState.update_detailed_status(
        video_id=video_id,
        stage="rendering",
        status="⚡ Rendering final video...",
        step_details={
            "message": "Encoding and optimizing video file",
            "estimated_time": "30-45 seconds",
            "current_action": "Applying effects and finalizing video"
        }
    )
    time.sleep(5)
    
    # Return simulated output path (replace with actual video generation logic)
    return f"/videos/output/{video_id}_traditional.mp4"