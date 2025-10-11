from video_builder import logger


def close_clip_safe(clip):
    """Safely close a MoviePy clip, catching exceptions."""
    try:
        if hasattr(clip, 'close'):
            clip.close()
    except Exception as e:
        logger.error(f"Error closing clip: {e}")
