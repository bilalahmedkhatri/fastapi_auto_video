from celery.utils.log import get_task_logger

# Create logger using Celery's task logger
logger = get_task_logger(__name__)


def close_clip_safe(clip):
    """Safely close a MoviePy clip, catching exceptions."""
    try:
        if hasattr(clip, 'close'):
            clip.close()
    except Exception as e:
        logger.error(f"Error closing clip: {e}")
