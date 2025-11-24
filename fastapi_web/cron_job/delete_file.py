"""
Cleanup script for temporary voiceover files
Deletes files older than 1 hour from media/temp/voiceovers/
Should be run hourly via cron or task scheduler
"""
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session, select
from models.database import engine
from models.db_models import FreeVoiceoverUsage, GeneratedVoiceover

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/cleanup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def delete_expired_files():
    """
    Delete voiceover files older than 1 hour from temporary directory
    Also updates database records to mark files as deleted
    """
    temp_dir = Path("media/temp/voiceovers")
    
    if not temp_dir.exists():
        logger.warning(f"Temporary directory does not exist: {temp_dir}")
        return
    
    now = datetime.now()
    expiry_threshold = now - timedelta(hours=1)
    
    deleted_count = 0
    error_count = 0
    total_size = 0
    
    logger.info(f"Starting cleanup of files older than {expiry_threshold}")
    
    # Get all files in the directory
    for file_path in temp_dir.glob("*.wav"):
        try:
            # Get file creation/modification time
            file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            
            # Check if file is older than 1 hour
            if file_mtime < expiry_threshold:
                file_size = file_path.stat().st_size
                filename = file_path.name
                
                # Delete the file
                file_path.unlink()
                deleted_count += 1
                total_size += file_size
                
                logger.info(f"Deleted expired file: {filename} ({file_size} bytes)")
                
                # Update database to mark file as deleted
                with Session(engine) as session:
                    # Find the voiceover record
                    voiceover = session.exec(
                        select(GeneratedVoiceover)
                        .where(GeneratedVoiceover.filename == filename)
                    ).first()
                    
                    if voiceover:
                        # Mark usage record as deleted
                        usage = session.exec(
                            select(FreeVoiceoverUsage)
                            .where(FreeVoiceoverUsage.voiceover_id == voiceover.id)
                        ).first()
                        
                        if usage:
                            usage.is_deleted = True
                            session.add(usage)
                            session.commit()
                            logger.info(f"Marked database record as deleted: {voiceover.id}")
        
        except Exception as e:
            error_count += 1
            logger.error(f"Error deleting file {file_path}: {str(e)}")
    
    # Log summary
    logger.info(f"Cleanup completed:")
    logger.info(f"  - Files deleted: {deleted_count}")
    logger.info(f"  - Space freed: {total_size / (1024 * 1024):.2f} MB")
    logger.info(f"  - Errors: {error_count}")
    
    return {
        "deleted_count": deleted_count,
        "total_size": total_size,
        "error_count": error_count
    }


def cleanup_old_usage_records():
    """
    Remove old usage records from database (older than 30 days)
    Keeps database size manageable
    """
    with Session(engine) as session:
        cutoff_date = datetime.now() - timedelta(days=30)
        
        # Delete old usage records
        old_records = session.exec(
            select(FreeVoiceoverUsage)
            .where(FreeVoiceoverUsage.generated_at < cutoff_date)
        ).all()
        
        deleted_count = len(old_records)
        
        for record in old_records:
            session.delete(record)
        
        session.commit()
        
        logger.info(f"Deleted {deleted_count} old usage records (older than 30 days)")
        
        return deleted_count


if __name__ == "__main__":
    try:
        logger.info("=" * 60)
        logger.info("Starting voiceover cleanup job")
        logger.info("=" * 60)
        
        # Delete expired files
        file_result = delete_expired_files()
        
        # Cleanup old database records
        db_result = cleanup_old_usage_records()
        
        logger.info("=" * 60)
        logger.info("Cleanup job completed successfully")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Cleanup job failed: {str(e)}", exc_info=True)
        sys.exit(1)
