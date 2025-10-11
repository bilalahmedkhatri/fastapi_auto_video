
from video_builder.video_builder import file_directory
from video_builder.core.config import base_dir
from moviepy import ImageClip
from moviepy.video.fx import Resize
import random
from celery.utils.log import get_task_logger

# Create logger using Celery's task logger
logger = get_task_logger(__name__)

def add_face_overlay(audio_duration):
    """Add animated face overlay with MoviePy 2.x syntax"""
    face_paths = file_directory.get_image_files(
        base_dir().joinpath('media', 'faces'), load_clips=False)
    if not face_paths:
        return None

    try:
        return (
            ImageClip(random.choice(face_paths))
            .with_duration(audio_duration)
            .with_effects(Resize(height=200))
            .with_position(('right', 'bottom'))
            .with_layer(2)
        )
    except Exception as e:
        logger.error(f"Face overlay error: {e}")
        return None