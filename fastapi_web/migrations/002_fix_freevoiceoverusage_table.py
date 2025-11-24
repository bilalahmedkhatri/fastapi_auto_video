"""
Fix FreeVoiceoverUsage table structure
Drop and recreate with correct columns
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import Session, text
from models.db_models import engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fix_table():
    """Drop and recreate FreeVoiceoverUsage table with correct structure"""
    
    with Session(engine) as session:
        try:
            # Drop existing table
            logger.info("Dropping existing freevoiceoverusage table...")
            session.exec(text("DROP TABLE IF EXISTS freevoiceoverusage CASCADE;"))
            session.commit()
            logger.info("✅ Table dropped")
            
            # Create table with correct structure
            logger.info("Creating freevoiceoverusage table with correct structure...")
            session.exec(text("""
                CREATE TABLE freevoiceoverusage (
                    id VARCHAR PRIMARY KEY,
                    identifier VARCHAR NOT NULL,
                    voiceover_id VARCHAR NOT NULL,
                    generated_at TIMESTAMP NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    is_deleted BOOLEAN NOT NULL DEFAULT FALSE
                );
            """))
            session.commit()
            logger.info("✅ Table created")
            
            # Create index
            logger.info("Creating index on identifier...")
            session.exec(text("""
                CREATE INDEX idx_freevoiceoverusage_identifier 
                ON freevoiceoverusage(identifier);
            """))
            session.commit()
            logger.info("✅ Index created")
            
            logger.info("\n🎉 Table fix completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Fix failed: {e}")
            session.rollback()
            return False


if __name__ == "__main__":
    success = fix_table()
    sys.exit(0 if success else 1)
