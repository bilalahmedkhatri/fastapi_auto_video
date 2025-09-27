# Video Generation Process Tracking System

## Overview

The `CurrentVideoGenerate` class (aliased as `VideoGenerationProcessManager`) provides comprehensive tracking and management of video generation workflows. It enables step-by-step progress monitoring, data persistence, error recovery, and complete state management for the video builder system.

## Database Schema

### VideoGenerationProcess Table

The main table that tracks the overall video generation process:

- **Core Fields:**
  - `id`: Unique process identifier
  - `user_id`: User who initiated the process
  - `video_id`: Link to final generated video
  - `current_step`: Current workflow step
  - `overall_progress`: Completion percentage (0-100)

- **Step Data (JSON Fields):**
  - `input_data`: User prompt, preferences, categories
  - `script_data`: Generated scripts, selected script, edits
  - `voiceover_data`: Voice settings, generated audio files
  - `social_media_data`: Platform content, SEO keywords
  - `media_data`: Selected/uploaded media items
  - `video_effects_data`: Final video configuration

- **Analytics & Performance:**
  - `step_durations`: Timing for each workflow step
  - `ai_model_usage`: AI API usage tracking
  - `user_actions`: Log of user interactions
  - `quality_scores`: Quality metrics for each step

### VideoProcessStep Table

Detailed tracking for individual workflow steps:

- **Step Identification:**
  - `process_id`: Link to parent process
  - `step_name`: Name of the workflow step
  - `step_order`: Sequential order in workflow

- **Performance Metrics:**
  - `ai_requests`: Number of AI API calls
  - `ai_tokens_used`: Total tokens consumed
  - `processing_time`: Actual processing duration
  - `quality_score`: Step quality rating (0.0-1.0)

## Usage Guide

### 1. Initialize Process Manager

```python
from sqlmodel import Session
from models.video_process_manager import CurrentVideoGenerate

# Get database session
session = get_session()

# Initialize manager
manager = CurrentVideoGenerate(session)
```

### 2. Start New Video Generation Process

```python
# Create new process
process_id = manager.initialize_video_generation(
    user_id="user_123",
    initial_data={
        "prompt": "Create a video about renewable energy",
        "category": "Education",
        "language": "English",
        "script_types": ["short", "medium", "long"]
    },
    session_id="browser_session_456",
    priority="normal"  # low, normal, high
)

print(f"Process started: {process_id}")
```

### 3. Update Step Progress

```python
# Mark step as in progress
success = manager.update_step_progress(
    step_name="input",
    status="in-progress"
)

# Complete step with data and metrics
success = manager.update_step_progress(
    step_name="input",
    status="completed",
    data={
        "user_prompt": "Create a video about renewable energy",
        "selected_types": ["short", "medium"],
        "processing_time_ms": 2500
    },
    quality_score=0.95,
    ai_model_used="gpt-4-turbo",
    tokens_used=150
)
```

### 4. Handle Step Failures

```python
# Record step failure with detailed error information
success = manager.handle_step_failure(
    step_name="scripts",
    error_message="AI service temporarily unavailable",
    error_details={
        "error_code": "SERVICE_UNAVAILABLE",
        "retry_after_seconds": 30,
        "service": "openai",
        "timestamp": "2025-09-22T10:30:00Z"
    }
)

# Retry a failed step
retry_success = manager.retry_failed_step("scripts")
```

### 5. Get Process Status

```python
# Get complete process state
current_state = manager.get_current_step()

print(f"Current Step: {current_state['current_step']}")
print(f"Overall Progress: {current_state['overall_progress']}%")
print(f"Status: {current_state['status']}")
print(f"Step Progress: {current_state['step_progress']}")

# Access step-specific data
script_data = current_state.get('script_data')
voiceover_data = current_state.get('voiceover_data')
```

### 6. Complete Process

```python
# Mark process as completed
success = manager.mark_completion(
    video_id="generated_video_789",
    final_quality_score=0.88
)
```

### 7. Process Analytics

```python
# Get comprehensive analytics
analytics = manager.get_process_analytics()

print(f"Success Rate: {analytics['step_statistics']['success_rate']}%")
print(f"Total AI Tokens: {analytics['ai_usage']['total_tokens']}")
print(f"Average Step Duration: {analytics['timing_statistics']['average_step_duration']}s")
```

## Workflow Steps

The system tracks these standard workflow steps:

1. **input** - User enters prompt and preferences
2. **loading** - AI script generation in progress
3. **scripts** - Script selection and editing
4. **editing** - Advanced script modifications
5. **voiceover** - Voice generation and audio settings
6. **social-media** - Platform-specific content generation
7. **media** - Media selection and management
8. **video-effects** - Final video configuration

## Step Status Values

Each step can have these status values:

- `not-started` - Step hasn't begun
- `in-progress` - Step is currently being processed
- `completed` - Step finished successfully
- `failed` - Step encountered an error
- `skipped` - Step was bypassed by user

## Process Status Values

Overall process status:

- `active` - Process is ongoing
- `paused` - Process temporarily stopped
- `completed` - All steps finished successfully
- `failed` - Process failed and cannot continue
- `cancelled` - User cancelled the process

## Utility Functions

### Get User's Active Processes

```python
from models.video_process_manager import get_active_processes_for_user

active_processes = get_active_processes_for_user(session, "user_123", limit=10)

for process in active_processes:
    print(f"Process {process['process_id']}: {process['current_step']} ({process['overall_progress']}%)")
```

### Cleanup Old Processes

```python
from models.video_process_manager import cleanup_old_processes

# Clean up processes older than 30 days
cleaned_count = cleanup_old_processes(session, days_old=30)
print(f"Cleaned up {cleaned_count} old processes")
```

### Resume Existing Process

```python
# Load existing process
success = manager.load_process("existing_process_id_123")

if success:
    current_state = manager.get_current_step()
    print(f"Resumed process at step: {current_state['current_step']}")
```

## Error Handling Best Practices

1. **Always check return values** from manager methods
2. **Use try/catch blocks** around database operations
3. **Log detailed error information** when failures occur
4. **Implement retry logic** for transient failures
5. **Provide user feedback** about process status

```python
try:
    success = manager.update_step_progress("scripts", "completed", script_data)
    if not success:
        print("Failed to update step progress")
        # Handle failure appropriately
except Exception as e:
    print(f"Database error: {e}")
    # Implement error recovery
```

## Performance Considerations

1. **Use database sessions efficiently** - close when done
2. **Batch updates** when possible to reduce database calls
3. **Monitor JSON field sizes** - large data may impact performance
4. **Regular cleanup** of old processes to maintain performance
5. **Index optimization** for frequently queried fields

## Integration with FastAPI

Example FastAPI endpoint using the video process manager:

```python
from fastapi import APIRouter, Depends
from sqlmodel import Session

router = APIRouter()

@router.post("/video-generation/start")
async def start_video_generation(
    request: VideoGenerationRequest,
    session: Session = Depends(get_session)
):
    manager = CurrentVideoGenerate(session)
    
    try:
        process_id = manager.initialize_video_generation(
            user_id=request.user_id,
            initial_data=request.dict(),
            priority=request.priority or "normal"
        )
        
        return {
            "success": True,
            "process_id": process_id,
            "message": "Video generation process started"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/video-generation/{process_id}/status")
async def get_process_status(
    process_id: str,
    session: Session = Depends(get_session)
):
    manager = CurrentVideoGenerate(session)
    
    if manager.load_process(process_id):
        return manager.get_current_step()
    else:
        return {"error": "Process not found"}
```

## Next Steps for Integration

1. **Create FastAPI endpoints** for process management
2. **Integrate with existing video builder components**
3. **Add WebSocket support** for real-time progress updates
4. **Implement frontend state synchronization**
5. **Add process monitoring dashboard**
6. **Set up automated cleanup jobs**

This system provides the foundation for robust video generation workflow tracking and can be extended to meet specific business requirements.