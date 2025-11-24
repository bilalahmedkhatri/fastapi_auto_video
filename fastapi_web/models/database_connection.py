"""
Database Connection Module with Fallback Logic

This module provides intelligent database connection management:
1. Try to connect to local PostgreSQL database
2. If local database is unavailable, fall back to cPanel PostgreSQL database
3. Log connection status and provide health check functionality
"""

import os
import logging
from typing import Optional, Tuple
from sqlmodel import create_engine, Session
from sqlalchemy import text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class DatabaseConnectionManager:
    """Manages database connections with automatic fallback"""
    
    def __init__(self):
        self.engine = None
        self.connection_type: Optional[str] = None
        self.connection_url: Optional[str] = None
        
    def _test_connection(self, connection_url: str, timeout: int = 3) -> bool:
        """
        Test if a database connection is working
        
        Args:
            connection_url: Database URL to test
            timeout: Connection timeout in seconds
            
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Create test engine with timeout
            test_engine = create_engine(
                connection_url,
                echo=False,
                pool_pre_ping=True,
                connect_args={"connect_timeout": timeout}
            )
            
            # Try to execute a simple query
            with test_engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            
            # Clean up test engine
            test_engine.dispose()
            return True
            
        except Exception as e:
            logger.debug(f"Connection test failed: {e}")
            return False
    
    def _get_local_postgresql_url(self) -> Optional[str]:
        """Get local PostgreSQL connection URL from environment"""
        return os.getenv('POSTGRESQL_DATABASE_URL')
    
    def _get_cpanel_postgresql_url(self) -> Optional[str]:
        """
        Get cPanel PostgreSQL connection URL from environment
        
        Format: postgresql://username:password@host:port/database
        """
        # Try to get from environment variable first
        cpanel_url = os.getenv('CPANEL_POSTGRESQL_DATABASE_URL')
        if cpanel_url:
            return cpanel_url
        
        # Build from individual components if available
        host = os.getenv('CPANEL_DB_HOST', 'localhost')
        port = os.getenv('CPANEL_DB_PORT', '5432')
        database = os.getenv('CPANEL_DB_NAME', 'uihxzefkgh_azeemlab_api')
        username = os.getenv('CPANEL_DB_USER', 'uihxzefkgh_azeemlab_api')
        password = os.getenv('CPANEL_DB_PASSWORD', '5P2bnCA43r3w')
        
        if all([host, port, database, username, password]):
            return f"postgresql://{username}:{password}@{host}:{port}/{database}"
        
        return None
    
    def connect(self, force_cpanel: bool = False) -> Tuple[object, str]:
        """
        Establish database connection with fallback logic
        
        Args:
            force_cpanel: If True, skip local database and use cPanel directly
            
        Returns:
            Tuple of (engine, connection_type)
            connection_type can be: 'local', 'cpanel', or None
        """
        
        # Try local PostgreSQL first (unless forced to use cPanel)
        if not force_cpanel:
            local_url = self._get_local_postgresql_url()
            if local_url:
                logger.info("🔍 Attempting to connect to local PostgreSQL database...")
                if self._test_connection(local_url):
                    logger.info("✅ Connected to LOCAL PostgreSQL database")
                    self.engine = create_engine(local_url, echo=False)
                    self.connection_type = 'local'
                    self.connection_url = local_url
                    return self.engine, 'local'
                else:
                    logger.warning("⚠️  Local PostgreSQL database not available, trying fallback...")
        
        # Fallback to cPanel PostgreSQL
        cpanel_url = self._get_cpanel_postgresql_url()
        if cpanel_url:
            logger.info("🔍 Attempting to connect to cPanel PostgreSQL database...")
            if self._test_connection(cpanel_url):
                logger.info("✅ Connected to CPANEL PostgreSQL database")
                self.engine = create_engine(cpanel_url, echo=False)
                self.connection_type = 'cpanel'
                self.connection_url = cpanel_url
                return self.engine, 'cpanel'
            else:
                logger.error("❌ cPanel PostgreSQL database connection failed")
        
        # No database connection available
        logger.error("❌ No database connection available!")
        raise ConnectionError(
            "Failed to connect to any database. "
            "Please check your database configuration in .env file."
        )
    
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
            "connection_url_masked": self._mask_password(self.connection_url) if self.connection_url else None
        }
    
    def _mask_password(self, url: str) -> str:
        """Mask password in database URL for logging"""
        if not url:
            return None
        
        try:
            # Replace password with asterisks
            import re
            pattern = r'(postgresql://[^:]+:)([^@]+)(@.+)'
            return re.sub(pattern, r'\1****\3', url)
        except:
            return "***masked***"
    
    def health_check(self) -> dict:
        """
        Perform database health check
        
        Returns:
            Dictionary with health status information
        """
        if not self.engine:
            return {
                "status": "disconnected",
                "message": "No active database connection"
            }
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            
            return {
                "status": "healthy",
                "connection_type": self.connection_type,
                "message": f"Connected to {self.connection_type} database"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "connection_type": self.connection_type,
                "error": str(e)
            }


# Global database connection manager instance
db_manager = DatabaseConnectionManager()

# Establish connection on module import
try:
    engine, connection_type = db_manager.connect()
    logger.info(f"🗄️  Database initialized: {connection_type.upper()} database")
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")
    raise


def get_engine():
    """Get database engine (for backward compatibility)"""
    return db_manager.get_engine()


def get_connection_info() -> dict:
    """Get database connection information"""
    return db_manager.get_connection_info()


def health_check() -> dict:
    """Perform database health check"""
    return db_manager.health_check()
