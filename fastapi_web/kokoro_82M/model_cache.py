"""
Kokoro Model Cache - Singleton Pattern for Model Reuse
Reduces generation time from 16s to 2s by keeping model in memory
"""
import threading
import logging
from typing import Optional

# Import will be available when called from FastAPI context
from kokoro_82M.generators import KokoroVoiceGenerator

logger = logging.getLogger(__name__)

# Global cache for the model instance
_cached_generator: Optional[KokoroVoiceGenerator] = None
_generator_lock = threading.Lock()


def get_cached_generator() -> KokoroVoiceGenerator:
    """
    Get or create a cached KokoroVoiceGenerator instance.
    
    Uses singleton pattern with thread-safe initialization:
    - First call: Loads model (takes ~8 seconds)
    - Subsequent calls: Returns cached instance (instant)
    
    Thread Safety:
    - Uses threading.Lock to prevent race conditions
    - Multiple concurrent requests wait for single initialization
    - After init, all requests share the same model instance
    
    Returns:
        KokoroVoiceGenerator: Cached generator instance
    
    Performance:
    - Cold start: 8 seconds (one-time cost)
    - Warm requests: <100ms (just returns cached instance)
    - Memory usage: ~500MB-1GB (model stays in RAM)
    """
    global _cached_generator
    
    # Fast path - if already initialized, return immediately
    if _cached_generator is not None:
        return _cached_generator
    
    # Slow path - need to initialize
    with _generator_lock:
        # Double-check pattern: another thread might have initialized while we waited
        if _cached_generator is None:
            logger.info("🔄 Initializing Kokoro model (one-time load, ~8 seconds)...")
            try:
                _cached_generator = KokoroVoiceGenerator()
                logger.info("✅ Kokoro model loaded and cached successfully")
                logger.info(f"📊 Model memory footprint: ~500MB-1GB")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Kokoro model: {e}")
                raise RuntimeError(f"Model initialization failed: {e}") from e
        else:
            logger.debug("Model was initialized by another thread, using cached instance")
    
    return _cached_generator


def get_model_status() -> dict:
    """
    Get current model cache status.
    
    Returns:
        dict: Status information with keys:
            - is_loaded (bool): Whether model is cached
            - instance_id (str): Memory address of cached instance
            - ready (bool): Whether model is ready for use
    """
    global _cached_generator
    
    return {
        "is_loaded": _cached_generator is not None,
        "instance_id": str(id(_cached_generator)) if _cached_generator else None,
        "ready": _cached_generator is not None
    }


def clear_cache():
    """
    Clear the cached model instance (for testing/debugging).
    
    WARNING: This will force the next request to reload the model (8s delay).
    Only use this if you need to free memory or reload model with different settings.
    """
    global _cached_generator
    
    with _generator_lock:
        if _cached_generator is not None:
            logger.warning("🗑️ Clearing cached Kokoro model (next request will reload)")
            _cached_generator = None
        else:
            logger.info("Model cache is already empty")


# Optional: Preload model when this module is imported
# Uncomment if you want model to load when server starts (not on first request)
# def _preload_model():
#     """Preload model when module is imported"""
#     try:
#         get_cached_generator()
#     except Exception as e:
#         logger.error(f"Failed to preload model: {e}")
# 
# _preload_model()
