"""
Database Connection Module with Fallback Logic

Connects to local PostgreSQL first, falls back to cPanel MySQL if unavailable.
"""

import os
import logging
import re
from typing import Optional, Tuple
from sqlmodel import create_engine
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class DatabaseConnectionManager:
    """Manages database connections with automatic fallback"""
    
    def __init__(self):
        self.engine = None
        self.connection_type: Optional[str] = None
    
    def _test_connection(self, connection_url: str) -> bool:
        """Test if a database connection works"""
        try:
            test_engine = create_engine(
                connection_url,
                echo=False,
                pool_pre_ping=True,
                connect_args={"connect_timeout": 3}
            )
            
            with test_engine.connect() as conn:
                conn.execute(text("SELECT 1")).fetchone()
            
            test_engine.dispose()
            return True
            
        except Exception as e:
            logger.debug(f"Connection test failed: {str(e)}")
            return False
    
    def _get_local_url(self) -> Optional[str]:
        """Get local PostgreSQL URL"""
        return os.getenv('POSTGRESQL_DATABASE_URL')
    
    def _get_cpanel_url(self) -> Optional[str]:
        """Get cPanel MySQL URL"""
        return os.getenv('CPANEL_MYSQL_DATABASE_URL') or os.getenv('CPANEL_POSTGRESQL_DATABASE_URL')
    
    def connect(self) -> Tuple[object, str]:
        """Establish database connection with fallback logic"""
        
        # Try local PostgreSQL first
        local_url = self._get_local_url()
        if local_url:
            logger.info("🔍 Connecting to local PostgreSQL...")
            if self._test_connection(local_url):
                logger.info("✅ Connected to LOCAL PostgreSQL")
                self.engine = create_engine(local_url, echo=False)
                self.connection_type = 'local'
                return self.engine, 'local'
            else:
                logger.warning("⚠️  Local PostgreSQL unavailable, trying fallback...")
        
        # Fallback to cPanel database
        cpanel_url = self._get_cpanel_url()
        if cpanel_url:
            db_type = "MySQL" if "mysql" in cpanel_url else "PostgreSQL"
            logger.info(f"🔍 Connecting to cPanel {db_type}...")
            if self._test_connection(cpanel_url):
                logger.info(f"✅ Connected to CPANEL {db_type}")
                self.engine = create_engine(cpanel_url, echo=False)
                self.connection_type = 'cpanel'
                return self.engine, 'cpanel'
            else:
                logger.error(f"❌ cPanel {db_type} connection failed")
        
        raise ConnectionError("Failed to connect to any database. Check .env configuration.")
    
    def get_engine(self):
        """Get the current database engine"""
        if not self.engine:
            self.connect()
        return self.engine
    
    def get_connection_info(self) -> dict:
        """Get current connection information"""
        return {
            "connected": self.engine is not None,
            "connection_type": self.connection_type,
            "connection_url_masked": self._mask_password() if self.engine else None
        }
    
    def _mask_password(self) -> str:
        """Mask password in database URL for logging"""
        url = str(self.engine.url) if self.engine else None
        if not url:
            return None
        
        # Replace password with asterisks
        pattern = r'((?:postgresql|mysql\+pymysql)://[^:]+:)([^@]+)(@.+)'
        return re.sub(pattern, r'\1****\3', url)
    
    def health_check(self) -> dict:
        """Perform database health check"""
        if not self.engine:
            return {"status": "disconnected", "message": "No active connection"}
        
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1")).fetchone()
            
            return {
                "status": "healthy",
                "connection_type": self.connection_type,
                "message": f"Connected to {self.connection_type} database"
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


# Global instance
db_manager = DatabaseConnectionManager()

# Initialize on import
if os.getenv('SKIP_DB_INIT', 'false').lower() != 'true':
    try:
        engine, connection_type = db_manager.connect()
        logger.info(f"🗄️  Database initialized: {connection_type.upper()}")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
else:
    logger.warning("⚠️  Database initialization skipped")
    engine = None


def get_engine():
    """Get database engine"""
    return db_manager.get_engine()


def get_connection_info() -> dict:
    """Get database connection information"""
    return db_manager.get_connection_info()


def health_check() -> dict:
    """Perform database health check"""
    return db_manager.health_check()
