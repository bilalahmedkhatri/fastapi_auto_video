#!/usr/bin/env python3
"""
Video Process Celery Tasks

This module implements Celery tasks for video generation workflow, integrating with 
the VideoGenerationProcessManager to provide comprehensive tracking and status updates.

Each task corresponds to a step in the video-builder workflow:
- Input processing
- Script generation  
- Voiceover generation
- Social media content
- Media processing
- Video effects and rendering

Tasks are designed to be chained together for complete workflow automation.
"""

import time
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from celery import Celery, chain, group
from celery.exceptions import Retry, WorkerLostError, MaxRetriesExceededError

from celery_app import celery_app, VideoProcessingState
from models.db_models import get_session, Video
from models.video_process_manager import VideoGenerationProcessManager


class VideoProcessTaskBase:
    """Base class for video process tasks with common functionality."""
    
    @staticmethod
    def get_manager(process_id: int) -> VideoGenerationProcessManager:
        """Get VideoGenerationProcessManager instance for a process."""
        session = next(get_session())
        manager = VideoGenerationProcessManager(session)
        if not manager.load_process(process_id):
            raise Exception(f"Video process {process_id} not found")
        return manager
    
    @staticmethod
    def update_step_status(manager: VideoGenerationProcessManager, step_name: str, 
                          status: str, data: Dict = None, **kwargs):
        """Update step status using the manager."""
        try:
            return manager.update_step_progress(
                step_name=step_name,
                status=status,
                data=data or {},
                **kwargs
            )
        except Exception as e:
            print(f"Failed to update step {step_name}: {e}")
            return False


@celery_app.task(bind=True, name="process_video_input", autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 60})
def process_video_input_task(self, process_id: int, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process and validate user input for video generation.
    
    Args:
        process_id: Video generation process ID
        input_data: User input data (prompt, categories, etc.)
        
    Returns:
        Dict with processed input data and validation results
    """
    try:
        manager = VideoProcessTaskBase.get_manager(process_id)
        
        # Start the input step
        VideoProcessTaskBase.update_step_status(
            manager, "input", "in-progress", 
            {"message": "Processing user input", "started_at": datetime.utcnow().isoformat()}
        )
        
        # Simulate input processing
        time.sleep(2)
        
        # Validate input data
        validation_results = {
            "prompt_valid": bool(input_data.get("prompt", "").strip()),
            "category_valid": bool(input_data.get("category")),
            "language_valid": bool(input_data.get("language", "English")),
            "duration_valid": input_data.get("duration") in ["short", "medium", "long"]
        }
        
        processed_data = {
            "original_prompt": input_data.get("prompt", ""),
            "processed_prompt": input_data.get("prompt", "").strip(),
            "category": input_data.get("category", "General"),
            "language": input_data.get("language", "English"),
            "duration": input_data.get("duration", "medium"),
            "validation_results": validation_results,
            "processing_time": 2.0
        }
        
        # Mark step as completed
        success = VideoProcessTaskBase.update_step_status(
            manager, "input", "completed",
            processed_data,
            quality_score=0.9 if all(validation_results.values()) else 0.7
        )
        
        if not success:
            raise Exception("Failed to update input step status")
            
        return {
            "status": "completed",
            "data": processed_data,
            "next_step": "loading"
        }
        
    except Exception as e:
        # Handle failure
        try:
            manager = VideoProcessTaskBase.get_manager(process_id)
            manager.handle_step_failure(
                step_name="input",
                error_message=str(e),
                error_details={"task_id": self.request.id, "input_data": input_data}
            )
        except:
            pass
        
        self.update_state(
            state='FAILURE',
            meta={'step': 'input', 'error': str(e), 'process_id': process_id}
        )
        raise


@celery_app.task(bind=True, name="generate_video_scripts", autoretry_for=(Exception,), retry_kwargs={'max_retries': 2, 'countdown': 120})
def generate_video_scripts_task(self, process_id: int, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate video scripts using AI based on processed input.
    
    Args:
        process_id: Video generation process ID
        input_data: Processed input data from previous step
        
    Returns:
        Dict with generated scripts and metadata
    """
    try:
        manager = VideoProcessTaskBase.get_manager(process_id)
        
        # Update loading step to in-progress
        VideoProcessTaskBase.update_step_status(
            manager, "loading", "in-progress",
            {"message": "AI script generation in progress", "started_at": datetime.utcnow().isoformat()}
        )
        
        # Simulate AI script generation
        time.sleep(8)
        
        # Generate multiple script variations
        scripts = []
        for i in range(3):
            script = {
                "id": f"script_{i+1}",
                "title": f"Generated Title {i+1} - {input_data.get('category', 'Video')}",
                "content": f"This is script variation {i+1} based on: {input_data.get('processed_prompt', '')}",
                "duration_estimate": 30 + (i * 15),  # 30, 45, 60 seconds
                "word_count": 100 + (i * 25),
                "tone": ["professional", "casual", "educational"][i],
                "ai_confidence": 0.85 + (i * 0.05)
            }
            scripts.append(script)
        
        script_data = {
            "scripts": scripts,
            "total_generated": len(scripts),
            "generation_time": 8.0,
            "ai_model_used": "gpt-4",
            "tokens_used": 500,
            "quality_metrics": {
                "coherence": 0.92,
                "relevance": 0.88,
                "creativity": 0.85
            }
        }
        
        # Complete loading step
        VideoProcessTaskBase.update_step_status(
            manager, "loading", "completed",
            {"message": "Script generation completed"},
            quality_score=0.88,
            ai_model_used="gpt-4",
            tokens_used=500
        )
        
        # Start scripts step
        VideoProcessTaskBase.update_step_status(
            manager, "scripts", "completed",
            script_data,
            quality_score=0.88
        )
        
        return {
            "status": "completed",
            "data": script_data,
            "next_step": "editing"
        }
        
    except Exception as e:
        # Handle failure for both loading and scripts steps
        try:
            manager = VideoProcessTaskBase.get_manager(process_id)
            manager.handle_step_failure(
                step_name="loading",
                error_message=f"Script generation failed: {str(e)}",
                error_details={"task_id": self.request.id, "input_data": input_data}
            )
        except:
            pass
        
        self.update_state(
            state='FAILURE',
            meta={'step': 'scripts', 'error': str(e), 'process_id': process_id}
        )
        raise


@celery_app.task(bind=True, name="generate_voiceover")
def generate_voiceover_task(self, process_id: int, script_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate voiceover audio for selected script.
    
    Args:
        process_id: Video generation process ID
        script_data: Script data with selected script
        
    Returns:
        Dict with voiceover file paths and metadata
    """
    try:
        manager = VideoProcessTaskBase.get_manager(process_id)
        
        # Start voiceover step
        VideoProcessTaskBase.update_step_status(
            manager, "voiceover", "in-progress",
            {"message": "Generating voiceover audio", "started_at": datetime.utcnow().isoformat()}
        )
        
        # Simulate voiceover generation
        time.sleep(6)
        
        # Select first script for voiceover (in real implementation, user would select)
        selected_script = script_data.get("scripts", [{}])[0]
        
        voiceover_data = {
            "audio_file": f"/media/voiceovers/process_{process_id}_voiceover.wav",
            "script_id": selected_script.get("id", "script_1"),
            "voice_model": "elevenlabs_professional",
            "duration": selected_script.get("duration_estimate", 45),
            "voice_settings": {
                "stability": 0.75,
                "similarity_boost": 0.85,
                "style": 0.2
            },
            "generation_time": 6.0,
            "file_size_mb": 2.3,
            "quality_metrics": {
                "clarity": 0.91,
                "naturalness": 0.87,
                "emotion": 0.83
            }
        }
        
        # Complete voiceover step
        VideoProcessTaskBase.update_step_status(
            manager, "voiceover", "completed",
            voiceover_data,
            quality_score=0.87,
            ai_model_used="elevenlabs_professional"
        )
        
        return {
            "status": "completed",
            "data": voiceover_data,
            "next_step": "social-media"
        }
        
    except Exception as e:
        try:
            manager = VideoProcessTaskBase.get_manager(process_id)
            manager.handle_step_failure(
                step_name="voiceover",
                error_message=str(e),
                error_details={"task_id": self.request.id, "script_data": script_data}
            )
        except:
            pass
        
        self.update_state(
            state='FAILURE', 
            meta={'step': 'voiceover', 'error': str(e), 'process_id': process_id}
        )
        raise


@celery_app.task(bind=True, name="generate_social_media")
def generate_social_media_task(self, process_id: int, content_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate social media content based on video script and settings.
    
    Args:
        process_id: Video generation process ID
        content_data: Combined script and voiceover data
        
    Returns:
        Dict with social media content for various platforms
    """
    try:
        manager = VideoProcessTaskBase.get_manager(process_id)
        
        # Start social media step
        VideoProcessTaskBase.update_step_status(
            manager, "social-media", "in-progress",
            {"message": "Generating social media content", "started_at": datetime.utcnow().isoformat()}
        )
        
        # Simulate social media content generation
        time.sleep(4)
        
        social_media_data = {
            "youtube": {
                "title": "Amazing AI-Generated Video Content | Auto Video Creator",
                "description": "Discover how AI can create engaging videos automatically. This video was generated using advanced AI technology.",
                "tags": ["ai", "video", "automation", "content creation", "technology"],
                "thumbnail_suggestions": [
                    "/media/thumbnails/process_{}_thumb_1.jpg".format(process_id),
                    "/media/thumbnails/process_{}_thumb_2.jpg".format(process_id)
                ]
            },
            "tiktok": {
                "caption": "Mind-blowing AI video creation! 🤖✨ #AI #VideoCreation #Tech",
                "hashtags": ["#AI", "#VideoCreation", "#Tech", "#Innovation", "#Viral"],
                "hook": "You won't believe this was made by AI!"
            },
            "instagram": {
                "caption": "The future of video creation is here! 🚀 This entire video was generated by AI.",
                "hashtags": ["#ArtificialIntelligence", "#VideoContent", "#Innovation", "#TechTrends"],
                "story_text": "Swipe to see how AI made this!"
            },
            "twitter": {
                "tweet": "Just created this video using AI! The technology is incredible. #AI #VideoGeneration",
                "thread": [
                    "1/ Here's how AI generated this entire video:",
                    "2/ Started with a simple prompt",
                    "3/ AI generated the script automatically", 
                    "4/ Created professional voiceover",
                    "5/ Added visuals and effects"
                ]
            },
            "generation_metrics": {
                "total_platforms": 4,
                "generation_time": 4.0,
                "ai_model_used": "gpt-4",
                "tokens_used": 350,
                "sentiment_score": 0.82
            }
        }
        
        # Complete social media step
        VideoProcessTaskBase.update_step_status(
            manager, "social-media", "completed",
            social_media_data,
            quality_score=0.85,
            ai_model_used="gpt-4",
            tokens_used=350
        )
        
        return {
            "status": "completed",
            "data": social_media_data,
            "next_step": "media"
        }
        
    except Exception as e:
        try:
            manager = VideoProcessTaskBase.get_manager(process_id)
            manager.handle_step_failure(
                step_name="social-media",
                error_message=str(e),
                error_details={"task_id": self.request.id, "content_data": content_data}
            )
        except:
            pass
        
        self.update_state(
            state='FAILURE',
            meta={'step': 'social-media', 'error': str(e), 'process_id': process_id}
        )
        raise


@celery_app.task(bind=True, name="process_video_media")
def process_video_media_task(self, process_id: int, content_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Download and process media assets (images, videos, music) for the video.
    
    Args:
        process_id: Video generation process ID
        content_data: All previous step data
        
    Returns:
        Dict with processed media files and metadata
    """
    try:
        manager = VideoProcessTaskBase.get_manager(process_id)
        
        # Start media step
        VideoProcessTaskBase.update_step_status(
            manager, "media", "in-progress",
            {"message": "Processing video media assets", "started_at": datetime.utcnow().isoformat()}
        )
        
        # Simulate media processing
        time.sleep(10)
        
        media_data = {
            "background_music": {
                "file": f"/media/music/process_{process_id}_bgm.mp3",
                "duration": 45,
                "genre": "ambient",
                "bpm": 80,
                "license": "royalty_free"
            },
            "images": [
                {
                    "file": f"/media/images/process_{process_id}_img_1.jpg",
                    "type": "background",
                    "resolution": "1920x1080",
                    "source": "pixabay",
                    "license": "free"
                },
                {
                    "file": f"/media/images/process_{process_id}_img_2.jpg", 
                    "type": "overlay",
                    "resolution": "1920x1080",
                    "source": "unsplash",
                    "license": "free"
                }
            ],
            "video_clips": [
                {
                    "file": f"/media/videos/process_{process_id}_clip_1.mp4",
                    "duration": 15,
                    "resolution": "1920x1080",
                    "fps": 30,
                    "source": "pixabay"
                }
            ],
            "processing_stats": {
                "total_files": 4,
                "total_size_mb": 125.7,
                "download_time": 7.2,
                "processing_time": 2.8,
                "compression_ratio": 0.85
            }
        }
        
        # Complete media step
        VideoProcessTaskBase.update_step_status(
            manager, "media", "completed",
            media_data,
            quality_score=0.89
        )
        
        return {
            "status": "completed",
            "data": media_data,
            "next_step": "video-effects"
        }
        
    except Exception as e:
        try:
            manager = VideoProcessTaskBase.get_manager(process_id)
            manager.handle_step_failure(
                step_name="media",
                error_message=str(e),
                error_details={"task_id": self.request.id, "content_data": content_data}
            )
        except:
            pass
        
        self.update_state(
            state='FAILURE',
            meta={'step': 'media', 'error': str(e), 'process_id': process_id}
        )
        raise


@celery_app.task(bind=True, name="render_final_video")
def render_final_video_task(self, process_id: int, all_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply video effects and render the final video.
    
    Args:
        process_id: Video generation process ID
        all_data: Combined data from all previous steps
        
    Returns:
        Dict with final video file and rendering metadata
    """
    try:
        manager = VideoProcessTaskBase.get_manager(process_id)
        
        # Start video effects step
        VideoProcessTaskBase.update_step_status(
            manager, "video-effects", "in-progress",
            {"message": "Applying effects and rendering video", "started_at": datetime.utcnow().isoformat()}
        )
        
        # Simulate video rendering
        for i in range(5):
            time.sleep(3)
            progress = (i + 1) / 5 * 100
            VideoProcessTaskBase.update_step_status(
                manager, "video-effects", "in-progress",
                {"message": f"Rendering video: {progress:.0f}%", "render_progress": progress}
            )
        
        final_video_data = {
            "output_file": f"/media/output/process_{process_id}_final_video.mp4",
            "duration": 45.3,
            "resolution": "1920x1080",
            "fps": 30,
            "bitrate": "2500kbps",
            "file_size_mb": 87.5,
            "effects_applied": [
                "fade_in",
                "fade_out", 
                "text_overlay",
                "background_music",
                "color_correction"
            ],
            "rendering_stats": {
                "total_render_time": 15.0,
                "compression_time": 3.2,
                "quality_score": 0.92,
                "cpu_usage_avg": 78.5,
                "memory_usage_mb": 1024
            },
            "quality_metrics": {
                "video_quality": 0.91,
                "audio_quality": 0.89,
                "sync_accuracy": 0.95,
                "overall_score": 0.92
            }
        }
        
        # Complete video effects step and mark process as completed
        VideoProcessTaskBase.update_step_status(
            manager, "video-effects", "completed",
            final_video_data,
            quality_score=0.92
        )
        

        # Mark entire process as completed
        manager.mark_completion(
            video_id=final_video_data["output_file"],
            final_quality_score=0.92
        )

        # Immediately clean up this process
        from models.video_process_manager import cleanup_old_processes
        session = next(get_session())
        cleanup_old_processes(session, days_old=0)

        return {
            "status": "completed",
            "data": final_video_data,
            "process_complete": True
        }
        
    except Exception as e:
        try:
            manager = VideoProcessTaskBase.get_manager(process_id)
            manager.handle_step_failure(
                step_name="video-effects",
                error_message=str(e),
                error_details={"task_id": self.request.id, "all_data": all_data}
            )
        except:
            pass
        
        self.update_state(
            state='FAILURE',
            meta={'step': 'video-effects', 'error': str(e), 'process_id': process_id}
        )
        raise


# Workflow orchestration task
@celery_app.task(bind=True, name="start_video_generation_workflow")
def start_video_generation_workflow(self, user_id: str, input_data: Dict[str, Any], 
                                  session_id: str = None, priority: str = "normal") -> Dict[str, Any]:
    """
    Start the complete video generation workflow by chaining all steps.
    
    Args:
        user_id: User ID starting the video generation
        input_data: Initial user input data
        session_id: Browser session ID
        priority: Task priority
        
    Returns:
        Dict with process ID and workflow task chain ID
    """
    try:
        # Create new process in database
        session = next(get_session())
        manager = VideoGenerationProcessManager(session)
        
        process_id = manager.initialize_video_generation(
            user_id=user_id,
            initial_data=input_data,
            session_id=session_id,
            priority=priority
        )
        
        # Create the workflow chain
        workflow = chain(
            process_video_input_task.s(process_id, input_data),
            generate_video_scripts_task.s(process_id),
            generate_voiceover_task.s(process_id),
            generate_social_media_task.s(process_id),
            process_video_media_task.s(process_id),
            render_final_video_task.s(process_id)
        )
        
        # Start the workflow
        workflow_result = workflow.apply_async()
        
        return {
            "process_id": process_id,
            "workflow_task_id": workflow_result.id,
            "status": "started",
            "estimated_completion_minutes": 5
        }
        
    except Exception as e:
        self.update_state(
            state='FAILURE',
            meta={'error': str(e), 'user_id': user_id}
        )
        raise


# Utility tasks for monitoring and management
@celery_app.task(name="get_process_status")
def get_process_status_task(process_id: int) -> Dict[str, Any]:
    """Get detailed status of a video generation process."""
    try:
        manager = VideoProcessTaskBase.get_manager(process_id)
        current_step = manager.get_current_step()
        analytics = manager.get_process_analytics()
        
        return {
            "process_id": process_id,
            "current_step_info": current_step,
            "analytics": analytics,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "process_id": process_id,
            "error": str(e),
            "status": "error"
        }


@celery_app.task(name="cleanup_completed_processes")
def cleanup_completed_processes_task(days_old: int = 7) -> Dict[str, Any]:
    """Clean up old completed video generation processes."""
    try:
        session = next(get_session())
        from .models.video_process_manager import cleanup_old_processes
        
        cleaned_count = cleanup_old_processes(session, days_old)
        
        return {
            "cleaned_processes": cleaned_count,
            "days_old_threshold": days_old,
            "cleanup_time": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": "cleanup_failed"
        }