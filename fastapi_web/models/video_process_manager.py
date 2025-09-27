"""
Current Video Generate Class - Video Generation Process Manager

This module provides the CurrentVideoGenerate class for comprehensive tracking
and management of video generation workflows. It handles step-by-step progress,
data persistence, error recovery, and state management.

Author: AI Assistant
Date: September 22, 2025
"""

from sqlmodel import Session, select
from datetime import datetime
from typing import Optional, Dict, Any, List
import json

from .db_models import VideoGenerationProcess, VideoProcessStep


class VideoGenerationProcessManager:
    """
    Enhanced manager class for video generation processes with advanced features.
    Provides comprehensive workflow orchestration with database persistence.
    """
    
    def __init__(self, session: Session):
        """
        Initialize the video generation process manager.
        
        Args:
            session: SQLModel database session
        """
        self.session = session
        self.process_id = None
        self.current_process = None
    
    def initialize_video_generation(self, user_id: str, initial_data: Dict = None, 
                                  session_id: str = None, priority: str = "normal") -> int:
        """
        Start a new video generation process and return the process ID.
        
        Args:
            user_id: User initiating the video generation
            initial_data: Initial form data (prompt, categories, etc.)
            session_id: Browser session identifier
            priority: Process priority (low, normal, high)
            
        Returns:
            str: Process ID for tracking
            
        Raises:
            Exception: If process creation fails
        """
        try:
            process = VideoGenerationProcess(
                user_id=user_id,
                session_id=session_id,
                current_step="input",
                step_progress=json.dumps({
                    "input": "not-started",
                    "loading": "not-started", 
                    "scripts": "not-started",
                    "editing": "not-started",
                    "voiceover": "not-started",
                    "social-media": "not-started",
                    "media": "not-started",
                    "video-effects": "not-started"
                }),
                input_data=json.dumps(initial_data) if initial_data else None,
                priority=priority,
                started_at=datetime.utcnow(),
                step_durations=json.dumps({}),
                ai_model_usage=json.dumps({}),
                user_actions=json.dumps([])
            )
            
            self.session.add(process)
            self.session.commit()
            self.session.refresh(process)
            
            self.process_id = process.id
            self.current_process = process
            
            # Create initial step records
            self._initialize_step_records()
            
            # Log initial action
            self._log_user_action("process_initialized", {
                "user_id": user_id,
                "initial_data": initial_data,
                "priority": priority
            })
            
            return process.id
            
        except Exception as e:
            self.session.rollback()
            raise Exception(f"Failed to initialize video generation: {str(e)}")
    
    def _initialize_step_records(self):
        """Create individual step tracking records for the process."""
        steps = [
            ("input", 1, "User input and preferences"),
            ("loading", 2, "AI script generation in progress"),
            ("scripts", 3, "Script selection and editing"),
            ("editing", 4, "Advanced script editing"),
            ("voiceover", 5, "Voice generation and audio settings"),
            ("social-media", 6, "Social media content generation"),
            ("media", 7, "Media selection and management"),
            ("video-effects", 8, "Final video configuration and effects")
        ]
        
        for step_name, step_order, description in steps:
            step = VideoProcessStep(
                process_id=self.process_id,
                step_name=step_name,
                step_order=step_order,
                status="not-started",
                input_data=json.dumps({"description": description}),
                processing_logs=json.dumps([]),
                user_modifications=json.dumps([])
            )
            self.session.add(step)
        
        self.session.commit()
    
    def load_process(self, process_id: int) -> bool:
        """
        Load an existing video generation process.
        
        Args:
            process_id: ID of the process to load
            
        Returns:
            bool: Success status
        """
        try:
            process = self.session.get(VideoGenerationProcess, process_id)
            if process:
                self.process_id = process_id
                self.current_process = process
                return True
            return False
        except Exception as e:
            print(f"Error loading process: {e}")
            return False
    
    def update_step_progress(self, step_name: str, status: str, data: Dict = None, 
                           quality_score: float = None, ai_model_used: str = None,
                           tokens_used: int = 0) -> bool:
        """
        Update the progress of a specific workflow step with comprehensive tracking.
        
        Args:
            step_name: Name of the step being updated
            status: New status (not-started, in-progress, completed, failed, skipped)
            data: Step-specific data to store
            quality_score: Quality rating (0.0 to 1.0)
            ai_model_used: Name of AI model used in this step
            tokens_used: Number of AI tokens consumed
            
        Returns:
            bool: Success status
        """
        if not self.current_process:
            print("No current process loaded")
            return False
        
        try:
            # Get step record
            step = self.session.exec(
                select(VideoProcessStep).where(
                    VideoProcessStep.process_id == self.process_id,
                    VideoProcessStep.step_name == step_name
                )
            ).first()
            
            if not step:
                print(f"Step {step_name} not found")
                return False
            
            # Record timing
            now = datetime.utcnow()
            
            if status == "in-progress" and step.status == "not-started":
                step.started_at = now
                self._log_processing_event(step_name, "step_started", {"timestamp": now.isoformat()})
            elif status == "completed" and step.status == "in-progress":
                step.completed_at = now
                if step.started_at:
                    duration = (now - step.started_at).total_seconds()
                    step.duration_seconds = int(duration)
                    self._update_step_duration_tracking(step_name, int(duration))
                self._log_processing_event(step_name, "step_completed", {
                    "duration_seconds": step.duration_seconds,
                    "quality_score": quality_score
                })
            
            # Update step properties
            step.status = status
            step.quality_score = quality_score
            
            if data:
                step.output_data = json.dumps(data)
            
            if ai_model_used:
                step.ai_requests += 1
                self._track_ai_model_usage(ai_model_used, tokens_used)
            
            step.ai_tokens_used += tokens_used
            
            # Update main process
            step_progress = json.loads(self.current_process.step_progress)
            step_progress[step_name] = status
            
            self.current_process.step_progress = json.dumps(step_progress)
            self.current_process.current_step = step_name
            self.current_process.last_updated = now
            
            # Calculate overall progress
            completed_steps = sum(1 for s in step_progress.values() if s == "completed")
            total_steps = len(step_progress)
            self.current_process.overall_progress = int((completed_steps / total_steps) * 100)
            
            # Store step-specific data in main process record
            if data:
                self._store_step_data(step_name, data)
            
            # Update estimated completion time
            if self.current_process.overall_progress > 0:
                self._update_estimated_completion()
            
            self.session.commit()
            
            # Log user action
            self._log_user_action(f"step_{status}", {
                "step_name": step_name,
                "progress": self.current_process.overall_progress,
                "data_size": len(json.dumps(data)) if data else 0
            })
            
            return True
            
        except Exception as e:
            self.session.rollback()
            print(f"Error updating step progress: {e}")
            return False
    
    def _store_step_data(self, step_name: str, data: Dict):
        """Store step-specific data in the appropriate process field."""
        data_json = json.dumps(data)
        
        if step_name == "input":
            self.current_process.input_data = data_json
        elif step_name in ["scripts", "editing"]:
            self.current_process.script_data = data_json
        elif step_name == "voiceover":
            self.current_process.voiceover_data = data_json
        elif step_name == "social-media":
            self.current_process.social_media_data = data_json
        elif step_name == "media":
            self.current_process.media_data = data_json
        elif step_name == "video-effects":
            self.current_process.video_effects_data = data_json
    
    def _update_step_duration_tracking(self, step_name: str, duration_seconds: int):
        """Update the step duration tracking in the main process."""
        try:
            durations = json.loads(self.current_process.step_durations) if self.current_process.step_durations else {}
            durations[step_name] = duration_seconds
            self.current_process.step_durations = json.dumps(durations)
        except Exception as e:
            print(f"Error updating step durations: {e}")
    
    def _track_ai_model_usage(self, model_name: str, tokens_used: int):
        """Track AI model usage across the process."""
        try:
            usage = json.loads(self.current_process.ai_model_usage) if self.current_process.ai_model_usage else {}
            if model_name not in usage:
                usage[model_name] = {"requests": 0, "total_tokens": 0}
            
            usage[model_name]["requests"] += 1
            usage[model_name]["total_tokens"] += tokens_used
            
            self.current_process.ai_model_usage = json.dumps(usage)
        except Exception as e:
            print(f"Error tracking AI model usage: {e}")
    
    def _update_estimated_completion(self):
        """Update estimated completion time based on current progress."""
        try:
            if self.current_process.started_at and self.current_process.overall_progress > 0:
                elapsed = (datetime.utcnow() - self.current_process.started_at).total_seconds()
                estimated_total = elapsed / (self.current_process.overall_progress / 100)
                estimated_remaining = estimated_total - elapsed
                
                self.current_process.estimated_completion = datetime.utcnow().replace(
                    second=int(estimated_remaining) % 60,
                    microsecond=0
                )
        except Exception as e:
            print(f"Error updating estimated completion: {e}")
    
    def _log_processing_event(self, step_name: str, event_type: str, data: Dict):
        """Log a processing event for a specific step."""
        try:
            step = self.session.exec(
                select(VideoProcessStep).where(
                    VideoProcessStep.process_id == self.process_id,
                    VideoProcessStep.step_name == step_name
                )
            ).first()
            
            if step:
                logs = json.loads(step.processing_logs) if step.processing_logs else []
                logs.append({
                    "timestamp": datetime.utcnow().isoformat(),
                    "event_type": event_type,
                    "data": data
                })
                step.processing_logs = json.dumps(logs)
        except Exception as e:
            print(f"Error logging processing event: {e}")
    
    def _log_user_action(self, action_type: str, data: Dict):
        """Log user actions during the video generation process."""
        try:
            actions = json.loads(self.current_process.user_actions) if self.current_process.user_actions else []
            actions.append({
                "timestamp": datetime.utcnow().isoformat(),
                "action_type": action_type,
                "data": data
            })
            self.current_process.user_actions = json.dumps(actions)
        except Exception as e:
            print(f"Error logging user action: {e}")
    
    def handle_step_failure(self, step_name: str, error_message: str, 
                           error_details: Dict = None, retry_immediately: bool = False) -> bool:
        """
        Handle and record step failures with detailed error information and recovery options.
        
        Args:
            step_name: Name of the failed step
            error_message: Human-readable error message
            error_details: Detailed error context
            retry_immediately: Whether to attempt immediate retry
            
        Returns:
            bool: Success status
        """
        if not self.current_process:
            return False
        
        try:
            # Update step record
            step = self.session.exec(
                select(VideoProcessStep).where(
                    VideoProcessStep.process_id == self.process_id,
                    VideoProcessStep.step_name == step_name
                )
            ).first()
            
            if step:
                step.status = "failed"
                step.error_message = error_message
                step.error_details = json.dumps(error_details) if error_details else None
                step.retry_count += 1
            
            # Update main process error tracking
            failed_steps = json.loads(self.current_process.failed_steps) if self.current_process.failed_steps else []
            if step_name not in failed_steps:
                failed_steps.append(step_name)
            
            error_messages = json.loads(self.current_process.error_messages) if self.current_process.error_messages else []
            error_messages.append({
                "step": step_name,
                "message": error_message,
                "timestamp": datetime.utcnow().isoformat(),
                "details": error_details,
                "retry_count": step.retry_count if step else 0
            })
            
            self.current_process.failed_steps = json.dumps(failed_steps)
            self.current_process.error_messages = json.dumps(error_messages)
            self.current_process.last_error_at = datetime.utcnow()
            self.current_process.retry_count += 1
            
            # Determine if process should be marked as failed
            max_retries = 3
            if self.current_process.retry_count >= max_retries and not retry_immediately:
                self.current_process.status = "failed"
            
            # Log the failure
            self._log_user_action("step_failed", {
                "step_name": step_name,
                "error_message": error_message,
                "retry_count": step.retry_count if step else 0,
                "will_retry": retry_immediately or self.current_process.retry_count < max_retries
            })
            
            self.session.commit()
            return True
            
        except Exception as e:
            self.session.rollback()
            print(f"Error handling step failure: {e}")
            return False
    
    def retry_failed_step(self, step_name: str) -> bool:
        """
        Retry a failed step by resetting its status.
        
        Args:
            step_name: Name of the step to retry
            
        Returns:
            bool: Success status
        """
        try:
            step = self.session.exec(
                select(VideoProcessStep).where(
                    VideoProcessStep.process_id == self.process_id,
                    VideoProcessStep.step_name == step_name
                )
            ).first()
            
            if step and step.status == "failed":
                step.status = "not-started"
                step.error_message = None
                step.error_details = None
                step.started_at = None
                step.completed_at = None
                
                # Update process step progress
                step_progress = json.loads(self.current_process.step_progress)
                step_progress[step_name] = "not-started"
                self.current_process.step_progress = json.dumps(step_progress)
                
                self._log_user_action("step_retried", {"step_name": step_name})
                
                self.session.commit()
                return True
            
            return False
        except Exception as e:
            self.session.rollback()
            print(f"Error retrying step: {e}")
            return False
    
    def get_current_step(self) -> Dict[str, Any]:
        """
        Get the current state of the video generation process.
        
        Returns:
            dict: Complete process state information
        """
        if not self.current_process:
            return {}
        
        try:
            # Get detailed step information
            steps = self.session.exec(
                select(VideoProcessStep).where(
                    VideoProcessStep.process_id == self.process_id
                ).order_by(VideoProcessStep.step_order)
            ).all()
            
            step_details = {}
            for step in steps:
                step_details[step.step_name] = {
                    "status": step.status,
                    "started_at": step.started_at.isoformat() if step.started_at else None,
                    "completed_at": step.completed_at.isoformat() if step.completed_at else None,
                    "duration_seconds": step.duration_seconds,
                    "quality_score": step.quality_score,
                    "error_message": step.error_message,
                    "retry_count": step.retry_count,
                    "ai_requests": step.ai_requests,
                    "ai_tokens_used": step.ai_tokens_used
                }
            
            return {
                "process_id": self.current_process.id,
                "user_id": self.current_process.user_id,
                "current_step": self.current_process.current_step,
                "overall_progress": self.current_process.overall_progress,
                "step_progress": json.loads(self.current_process.step_progress),
                "step_details": step_details,
                "status": self.current_process.status,
                "priority": self.current_process.priority,
                "started_at": self.current_process.started_at.isoformat(),
                "last_updated": self.current_process.last_updated.isoformat(),
                "completed_at": self.current_process.completed_at.isoformat() if self.current_process.completed_at else None,
                "estimated_completion": self.current_process.estimated_completion.isoformat() if self.current_process.estimated_completion else None,
                "total_processing_time": self.current_process.total_processing_time,
                "step_durations": json.loads(self.current_process.step_durations) if self.current_process.step_durations else {},
                "ai_model_usage": json.loads(self.current_process.ai_model_usage) if self.current_process.ai_model_usage else {},
                "failed_steps": json.loads(self.current_process.failed_steps) if self.current_process.failed_steps else [],
                "error_messages": json.loads(self.current_process.error_messages) if self.current_process.error_messages else [],
                "retry_count": self.current_process.retry_count,
                
                # Step data
                "input_data": json.loads(self.current_process.input_data) if self.current_process.input_data else None,
                "script_data": json.loads(self.current_process.script_data) if self.current_process.script_data else None,
                "voiceover_data": json.loads(self.current_process.voiceover_data) if self.current_process.voiceover_data else None,
                "social_media_data": json.loads(self.current_process.social_media_data) if self.current_process.social_media_data else None,
                "media_data": json.loads(self.current_process.media_data) if self.current_process.media_data else None,
                "video_effects_data": json.loads(self.current_process.video_effects_data) if self.current_process.video_effects_data else None
            }
        except Exception as e:
            print(f"Error getting current step: {e}")
            return {}
    
    def mark_completion(self, video_id: str = None, final_quality_score: float = None) -> bool:
        """
        Mark the video generation process as completed with comprehensive finalization.
        
        Args:
            video_id: ID of the generated video record
            final_quality_score: Overall quality score for the generated video
            
        Returns:
            bool: Success status
        """
        if not self.current_process:
            return False
        
        try:
            now = datetime.utcnow()
            
            # Update main process
            self.current_process.status = "completed"
            self.current_process.completed_at = now
            self.current_process.overall_progress = 100
            self.current_process.video_id = video_id
            
            # Calculate total processing time
            if self.current_process.started_at:
                total_time = (now - self.current_process.started_at).total_seconds()
                self.current_process.total_processing_time = int(total_time)
            
            # Store final quality score
            if final_quality_score is not None:
                quality_scores = json.loads(self.current_process.quality_scores) if self.current_process.quality_scores else {}
                quality_scores["final_video"] = final_quality_score
                self.current_process.quality_scores = json.dumps(quality_scores)
            
            # Log completion
            self._log_user_action("process_completed", {
                "video_id": video_id,
                "total_processing_time": self.current_process.total_processing_time,
                "final_quality_score": final_quality_score,
                "completed_steps": len([s for s in json.loads(self.current_process.step_progress).values() if s == "completed"])
            })
            
            self.session.commit()
            return True
            
        except Exception as e:
            self.session.rollback()
            print(f"Error marking completion: {e}")
            return False
    
    def pause_process(self, reason: str = None) -> bool:
        """
        Pause the video generation process.
        
        Args:
            reason: Optional reason for pausing
            
        Returns:
            bool: Success status
        """
        if not self.current_process:
            return False
        
        try:
            self.current_process.status = "paused"
            self.current_process.last_updated = datetime.utcnow()
            
            self._log_user_action("process_paused", {"reason": reason})
            
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            print(f"Error pausing process: {e}")
            return False
    
    def resume_process(self) -> bool:
        """
        Resume a paused video generation process.
        
        Returns:
            bool: Success status
        """
        if not self.current_process or self.current_process.status != "paused":
            return False
        
        try:
            self.current_process.status = "active"
            self.current_process.last_updated = datetime.utcnow()
            
            self._log_user_action("process_resumed", {})
            
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            print(f"Error resuming process: {e}")
            return False
    
    def get_process_analytics(self) -> Dict[str, Any]:
        """
        Get comprehensive analytics for the video generation process.
        
        Returns:
            dict: Process analytics and performance metrics
        """
        if not self.current_process:
            return {}
        
        try:
            steps = self.session.exec(
                select(VideoProcessStep).where(
                    VideoProcessStep.process_id == self.process_id
                ).order_by(VideoProcessStep.step_order)
            ).all()
            
            # Calculate step statistics
            total_steps = len(steps)
            completed_steps = sum(1 for step in steps if step.status == "completed")
            failed_steps = sum(1 for step in steps if step.status == "failed")
            
            # Calculate timing statistics
            step_durations = []
            total_ai_tokens = 0
            total_ai_requests = 0
            
            for step in steps:
                if step.duration_seconds:
                    step_durations.append(step.duration_seconds)
                total_ai_tokens += step.ai_tokens_used or 0
                total_ai_requests += step.ai_requests or 0
            
            avg_step_duration = sum(step_durations) / len(step_durations) if step_durations else 0
            
            return {
                "process_id": self.current_process.id,
                "status": self.current_process.status,
                "overall_progress": self.current_process.overall_progress,
                "total_processing_time": self.current_process.total_processing_time,
                "step_statistics": {
                    "total_steps": total_steps,
                    "completed_steps": completed_steps,
                    "failed_steps": failed_steps,
                    "success_rate": (completed_steps / total_steps * 100) if total_steps > 0 else 0
                },
                "timing_statistics": {
                    "average_step_duration": avg_step_duration,
                    "longest_step_duration": max(step_durations) if step_durations else 0,
                    "shortest_step_duration": min(step_durations) if step_durations else 0
                },
                "ai_usage": {
                    "total_tokens": total_ai_tokens,
                    "total_requests": total_ai_requests,
                    "models_used": json.loads(self.current_process.ai_model_usage) if self.current_process.ai_model_usage else {}
                },
                "error_statistics": {
                    "total_retries": self.current_process.retry_count,
                    "failed_steps": json.loads(self.current_process.failed_steps) if self.current_process.failed_steps else [],
                    "last_error": self.current_process.last_error_at.isoformat() if self.current_process.last_error_at else None
                },
                "user_engagement": {
                    "total_actions": len(json.loads(self.current_process.user_actions)) if self.current_process.user_actions else 0,
                    "session_duration": (datetime.utcnow() - self.current_process.started_at).total_seconds() if self.current_process.started_at else 0
                }
            }
        except Exception as e:
            print(f"Error getting process analytics: {e}")
            return {}


# Alias for backward compatibility
CurrentVideoGenerate = VideoGenerationProcessManager


# Utility functions for process management

def get_active_processes_for_user(session: Session, user_id: str, limit: int = 10) -> List[Dict]:
    """
    Get all active video generation processes for a user.
    
    Args:
        session: Database session
        user_id: User ID to filter by
        limit: Maximum number of processes to return
        
    Returns:
        List of process summaries
    """
    try:
        processes = session.exec(
            select(VideoGenerationProcess)
            .where(VideoGenerationProcess.user_id == user_id)
            .where(VideoGenerationProcess.status.in_(["active", "paused"]))
            .order_by(VideoGenerationProcess.last_updated.desc())
            .limit(limit)
        ).all()
        
        return [
            {
                "process_id": p.id,
                "current_step": p.current_step,
                "overall_progress": p.overall_progress,
                "status": p.status,
                "started_at": p.started_at.isoformat(),
                "last_updated": p.last_updated.isoformat()
            }
            for p in processes
        ]
    except Exception as e:
        print(f"Error getting active processes: {e}")
        return []


def cleanup_old_processes(session: Session, days_old: int = 30) -> int:
    """
    Clean up old completed or failed processes.
    
    Args:
        session: Database session
        days_old: Number of days after which to clean up processes
        
    Returns:
        Number of processes cleaned up
    """
    try:
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        old_processes = session.exec(
            select(VideoGenerationProcess)
            .where(VideoGenerationProcess.status.in_(["completed", "failed"]))
            .where(VideoGenerationProcess.last_updated < cutoff_date)
        ).all()
        
        count = len(old_processes)
        
        for process in old_processes:
            # Delete associated step records first
            steps = session.exec(
                select(VideoProcessStep)
                .where(VideoProcessStep.process_id == process.id)
            ).all()
            
            for step in steps:
                session.delete(step)
            
            # Delete the process
            session.delete(process)
        
        session.commit()
        return count
        
    except Exception as e:
        session.rollback()
        print(f"Error cleaning up old processes: {e}")
        return 0