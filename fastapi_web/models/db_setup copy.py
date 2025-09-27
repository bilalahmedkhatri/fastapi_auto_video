#!/usr/bin/env python3
"""
Database setup script for auto_video FastAPI application
Creates database tables and verifies the setup
"""

import os
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from db_models import create_db_and_tables, engine, get_session, Video
from sqlmodel import Session, select
import logging

# Configure logging
logger = logging.getLogger(__name__)
def setup_database():
    """Initialize the database and create tables"""
    try:
        logger.info("Setting up database...")
        
        # Create tables
        create_db_and_tables()
        logger.info("✅ Database tables created successfully")
        
        # Test database connection
        with Session(engine) as session:
            # Try to query videos table
            statement = select(Video).limit(1)
            result = session.exec(statement).first()
            logger.info("✅ Database connection test successful")
        
        logger.info("🎉 Database setup completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database setup failed: {e}")
        return False

def verify_database():
    """Verify database is working correctly"""
    try:
        with Session(engine) as session:
            # Count videos
            statement = select(Video)
            videos = session.exec(statement).all()
            logger.info(f"📊 Found {len(videos)} videos in database")
            
            # Show database file location if SQLite
            if str(engine.url).startswith("sqlite"):
                db_path = str(engine.url).replace("sqlite:///", "")
                full_path = Path(db_path).resolve()
                logger.info(f"📁 SQLite database location: {full_path}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Database verification failed: {e}")
        return False

if __name__ == "__main__":
    print("🗄️  Auto Video Database Setup")
    print("=" * 40)
    
    # Setup database
    if setup_database():
        # Verify setup
        if verify_database():
            print("\n✅ Database is ready for use!")
            print("\nNext steps:")
            print("1. Run: python main.py")
            print("2. Visit: http://localhost:8000/docs")
        else:
            print("\n⚠️  Database verification failed")
            sys.exit(1)
    else:
        print("\n❌ Database setup failed")
        sys.exit(1)
