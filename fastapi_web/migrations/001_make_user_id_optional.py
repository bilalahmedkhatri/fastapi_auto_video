"""
Migration: Make user_id optional in GeneratedVoiceover and add FreeVoiceoverUsage table
Run with: python migrations/001_make_user_id_optional.py
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import Session, text
from models.db_models import engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_migration():
    """Run the migration to make user_id optional and add new table"""
    
    with Session(engine) as session:
        try:
            # Step 1: Make user_id nullable in generatedvoiceover table
            logger.info("Making user_id column nullable in generatedvoiceover table...")
            session.exec(text("""
                ALTER TABLE generatedvoiceover 
                ALTER COLUMN user_id DROP NOT NULL;
            """))
            session.commit()
            logger.info("✅ user_id is now nullable")
            
            # Step 2: Create FreeVoiceoverUsage table
            logger.info("Creating freevoiceoverusage table...")
            session.exec(text("""
                CREATE TABLE IF NOT EXISTS freevoiceoverusage (
                    id VARCHAR PRIMARY KEY,
                    identifier VARCHAR NOT NULL,
                    voiceover_id VARCHAR NOT NULL,
                    generated_at TIMESTAMP NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    is_deleted BOOLEAN NOT NULL DEFAULT FALSE
                );
            """))
            session.commit()
            logger.info("✅ freevoiceoverusage table created")
            
            # Step 3: Create index on identifier for faster lookups
            logger.info("Creating index on identifier column...")
            session.exec(text("""
                CREATE INDEX IF NOT EXISTS idx_freevoiceoverusage_identifier 
                ON freevoiceoverusage(identifier);
            """))
            session.commit()
            logger.info("✅ Index created")
            
            logger.info("\n🎉 Migration completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            session.rollback()
            return False


if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
