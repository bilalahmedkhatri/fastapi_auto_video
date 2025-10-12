"""
Cleanup helper to prevent MoviePy Windows handle errors.
This module provides utilities to properly clean up MoviePy resources on Windows.

Known issue: https://github.com/Zulko/moviepy/issues/1925
Windows + Python 3.12 + MoviePy causes invalid handle errors during cleanup.
"""

import gc
import warnings
import os

def setup_moviepy_environment():
    """
    Configure environment to minimize MoviePy cleanup warnings on Windows.
    Call this at the start of your script.
    """
    # Suppress warnings
    warnings.filterwarnings('ignore', category=UserWarning, module='moviepy')
    warnings.filterwarnings('ignore', category=ResourceWarning)
    os.environ['PYTHONWARNINGS'] = 'ignore'


def close_clip_safely(clip):
    """
    Safely close a MoviePy clip, ignoring any errors.
    
    Args:
        clip: MoviePy clip object to close
    """
    try:
        if clip and hasattr(clip, 'close'):
            clip.close()
    except Exception:
        pass  # Ignore any cleanup errors


def cleanup_clips(clips_list):
    """
    Clean up a list of MoviePy clips.
    
    Args:
        clips_list: List of MoviePy clip objects
    """
    for clip in clips_list:
        close_clip_safely(clip)
    
    clips_list.clear()
    gc.collect()


def cleanup_transition_objects(transition_objects):
    """
    Clean up transition objects and their internal clips.
    
    Args:
        transition_objects: List of transition objects that may contain clips
    """
    for trans_obj in transition_objects:
        try:
            if hasattr(trans_obj, 'clips'):
                cleanup_clips(trans_obj.clips)
        except Exception:
            pass
    
    transition_objects.clear()
    gc.collect()


def final_cleanup(delay=0.5):
    """
    Perform final cleanup before script exit.
    Includes garbage collection and optional delay for Windows handle release.
    
    Args:
        delay: Seconds to wait after cleanup (default 0.5)
    """
    gc.collect()
    if delay > 0:
        import time
        time.sleep(delay)
