"""
Database initialization script for video builder application.
Creates all necessary tables for storing generated scripts and social media content.
"""

import logging
from sqlmodel import create_engine, SQLModel
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import models to register them
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from models.db_models import ScriptGeneration, SocialMediaContent

# Configure logging
logger = logging.getLogger(__name__)
def get_database_url():
    """Get database URL from environment variables."""
    db_user = os.getenv("POSTGRES_USER", "postgres")
    db_password = os.getenv("POSTGRES_PASSWORD", "password")
    db_host = os.getenv("POSTGRES_HOST", "localhost")
    db_port = os.getenv("POSTGRES_PORT", "5432")
    db_name = os.getenv("POSTGRES_DB", "fastapi_web")
    
    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

def init_database():
    """Initialize database tables."""
    try:
        database_url = get_database_url()
        logger.info(f"Connecting to database: {database_url.replace(':password', ':****')}")
        
        engine = create_engine(database_url)
        
        # Create all tables
        SQLModel.metadata.create_all(engine)
        
        logger.info("Database tables created successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return False

if __name__ == "__main__":
    init_database()
