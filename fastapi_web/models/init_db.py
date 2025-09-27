#!/usr/bin/env python3
"""
Simple database initialization script
Creates SQLite database and tables
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path to import db_models
import sys
sys.path.insert(0, str(Path(__file__).parent))

from fastapi_web.models.db_models import create_db_and_tables, engine

logger = logging.getLogger(__name__)
def init_database():
    """Initialize database and create tables"""
    try:
        database_url = os.getenv("DATABASE_URL", "sqlite:///./auto_video.db")
        logger.info(f"🗄️  Initializing database...")
        logger.info(f"Database URL: {database_url}")
        
        # Create all tables
        create_db_and_tables()
        
        logger.info("✅ Database initialized successfully!")
        logger.info("Tables created: VideoCreationRequest, Video")
        
        if database_url.startswith("sqlite://"):
            db_file = database_url.replace("sqlite:///", "")
            db_path = Path(db_file).resolve()
            logger.info(f"SQLite database file: {db_path}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return False

if __name__ == "__main__":
    try:
        if init_database():
            print("\n🎉 Database setup complete!")
            print("You can now run: python main.py")
        else:
            print("\n❌ Database setup failed!")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        sys.exit(1)
