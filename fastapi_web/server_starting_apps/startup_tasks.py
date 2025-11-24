"""
Server Startup Tasks

Handles background tasks that run when the server starts.
"""
import asyncio
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
from sqlmodel import Session, select, func
from models.db_models import SelectAIVoices, engine

logger = logging.getLogger(__name__)

# Configuration
SAMPLES_DIR = Path("media/voice-samples")
LAST_RUN_FILE = Path("server_starting_apps/.last_voice_sample_check")
MIN_SAMPLE_THRESHOLD = 40  # Trigger generation if less than this
CHECK_INTERVAL_HOURS = 24  # Don't run if checked within last 24 hours


def get_last_run_time() -> Optional[datetime]:
    """Get the last time voice sample check was run"""
    try:
        if LAST_RUN_FILE.exists():
            timestamp = float(LAST_RUN_FILE.read_text().strip())
            return datetime.fromtimestamp(timestamp)
    except Exception as e:
        logger.warning(f"Could not read last run time: {e}")
    return None


def set_last_run_time():
    """Record the current time as last run time"""
    try:
        LAST_RUN_FILE.parent.mkdir(parents=True, exist_ok=True)
        LAST_RUN_FILE.write_text(str(datetime.now().timestamp()))
    except Exception as e:
        logger.error(f"Could not save last run time: {e}")


def should_run_voice_sample_check() -> tuple[bool, str]:
    """
    Determine if voice sample generation should run
    Returns: (should_run, reason)
    """
    try:
        # Check if run recently
        last_run = get_last_run_time()
        if last_run:
            time_since_last_run = datetime.now() - last_run
            if time_since_last_run < timedelta(hours=CHECK_INTERVAL_HOURS):
                hours_remaining = CHECK_INTERVAL_HOURS - (time_since_last_run.total_seconds() / 3600)
                return False, f"Last run {time_since_last_run.total_seconds()/3600:.1f}h ago (skip until {hours_remaining:.1f}h)"
        
        # Count voices with local samples
        session = Session(engine)
        total_voices = session.exec(
            select(func.count(SelectAIVoices.id))
            .where(SelectAIVoices.is_active == True)
        ).one()
        
        # Count voices with local sample URLs
        voices_with_samples = session.exec(
            select(func.count(SelectAIVoices.id))
            .where(SelectAIVoices.is_active == True)
            .where(SelectAIVoices.voice_sample_url.like("/api/voice-samples/%"))
        ).one()
        
        session.close()
        
        if voices_with_samples >= MIN_SAMPLE_THRESHOLD:
            return False, f"Sufficient samples: {voices_with_samples}/{total_voices}"
        
        return True, f"Need samples: {voices_with_samples}/{total_voices} (threshold: {MIN_SAMPLE_THRESHOLD})"
        
    except Exception as e:
        logger.error(f"Error checking voice sample status: {e}")
        return False, f"Error: {str(e)}"


async def run_voice_sample_generation():
    """Run voice sample generation in background"""
    try:
        logger.info("🎙️  Starting voice sample generation...")
        
        # Import here to avoid circular dependencies
        from server_starting_apps.auto_generate_missing_samples import check_missing_samples
        
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, check_missing_samples, False)
        
        # Record successful run
        set_last_run_time()
        logger.info("✅ Voice sample generation completed")
        
    except Exception as e:
        logger.error(f"❌ Voice sample generation failed: {e}")


async def startup_voice_sample_check():
    """
    Smart voice sample check on server startup
    Only generates samples if needed
    """
    try:
        should_run, reason = should_run_voice_sample_check()
        
        logger.info(f"🔍 Voice sample check: {reason}")
        
        if should_run:
            # Run in background - don't block server startup
            asyncio.create_task(run_voice_sample_generation())
        else:
            logger.info("⏭️  Skipping voice sample generation")
            
    except Exception as e:
        logger.error(f"Error in voice sample startup check: {e}")
