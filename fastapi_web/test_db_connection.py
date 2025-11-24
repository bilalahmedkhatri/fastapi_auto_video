#!/usr/bin/env python3
"""
Database Connection Diagnostic Tool

This script tests database connectivity and helps diagnose connection issues.
Run this before starting the FastAPI application to verify database setup.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_mysql_connection():
    """Test MySQL connection"""
    print("=" * 70)
    print("🔍 Testing MySQL Connection")
    print("=" * 70)
    
    # First try to get connection URL directly from .env
    cpanel_url = os.getenv('CPANEL_MYSQL_DATABASE_URL')
    if cpanel_url:
        print(f"\n📋 Using CPANEL_MYSQL_DATABASE_URL from .env")
        print(f"   URL: {cpanel_url[:30]}...{cpanel_url[-15:]}")
        
        # Parse URL to show details
        import re
        match = re.search(r'mysql\+pymysql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', cpanel_url)
        if match:
            username, password, host, port, database = match.groups()
            print(f"\n📋 Parsed Connection Details:")
            print(f"   Host:     {host}")
            print(f"   Port:     {port}")
            print(f"   Database: {database}")
            print(f"   Username: {username}")
            print(f"   Password: {'*' * len(password)}")
        else:
            # Fallback to individual components
            host = os.getenv('CPANEL_DB_HOST', 'localhost')
            port = os.getenv('CPANEL_DB_PORT', '3306')
            database = os.getenv('CPANEL_DB_NAME', 'uihxzefkgh_azeemlab_api')
            username = os.getenv('CPANEL_DB_USER', 'uihxzefkgh_azeemlab_api')
            password = os.getenv('CPANEL_DB_PASSWORD', '5P2bnCA43r3w')
            
            print(f"\n📋 Connection Details (from components):")
            print(f"   Host:     {host}")
            print(f"   Port:     {port}")
            print(f"   Database: {database}")
            print(f"   Username: {username}")
            print(f"   Password: {'*' * len(password) if password else 'NOT SET'}")
    else:
        print(f"\n⚠️  CPANEL_MYSQL_DATABASE_URL not found in .env")
        print(f"   Falling back to individual components...")
        
        # Get credentials from environment
        host = os.getenv('CPANEL_DB_HOST', 'localhost')
        port = os.getenv('CPANEL_DB_PORT', '3306')
        database = os.getenv('CPANEL_DB_NAME', 'uihxzefkgh_azeemlab_api')
        username = os.getenv('CPANEL_DB_USER', 'uihxzefkgh_azeemlab_api')
        password = os.getenv('CPANEL_DB_PASSWORD', '5P2bnCA43r3w')
        
        print(f"\n📋 Connection Details:")
        print(f"   Host:     {host}")
        print(f"   Port:     {port}")
        print(f"   Database: {database}")
        print(f"   Username: {username}")
        print(f"   Password: {'*' * len(password) if password else 'NOT SET'}")
    
    # Test 1: Check if pymysql is installed
    print(f"\n1️⃣  Checking PyMySQL installation...")
    try:
        import pymysql
        print(f"   ✅ PyMySQL version {pymysql.__version__} installed")
    except ImportError as e:
        print(f"   ❌ PyMySQL not installed: {e}")
        print(f"   💡 Install with: pip install pymysql cryptography")
        return False
    
    # Test 2: Test direct PyMySQL connection
    print(f"\n2️⃣  Testing direct PyMySQL connection...")
    try:
        # Use parsed values from URL if available, otherwise use components
        if cpanel_url and match:
            username, password, host, port, database = match.groups()
        
        connection = pymysql.connect(
            host=host,
            port=int(port),
            user=username,
            password=password,
            database=database,
            connect_timeout=5
        )
        print(f"   ✅ Direct connection successful!")
        
        # Test query
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"   📊 MySQL Version: {version[0]}")
        
        connection.close()
        
    except pymysql.Error as e:
        print(f"   ❌ Connection failed: {e}")
        print(f"\n💡 Troubleshooting tips:")
        print(f"   - Check if MySQL is running")
        print(f"   - Verify database exists in cPanel MySQL")
        print(f"   - Verify username/password are correct")
        print(f"   - Check if user has access to database")
        print(f"   - Try: mysql -h {host} -u {username} -p {database}")
        return False
    
    # Test 3: Test SQLAlchemy connection
    print(f"\n3️⃣  Testing SQLAlchemy connection...")
    try:
        from sqlalchemy import create_engine, text
        
        # Use URL from .env if available
        if cpanel_url:
            url = cpanel_url
        else:
            url = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
        
        engine = create_engine(url, echo=False)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        
        print(f"   ✅ SQLAlchemy connection successful!")
        engine.dispose()
        
    except Exception as e:
        print(f"   ❌ SQLAlchemy connection failed: {e}")
        return False
    
    # Test 4: Test from .env file URL
    print(f"\n4️⃣  Testing .env CPANEL_MYSQL_DATABASE_URL...")
    cpanel_url = os.getenv('CPANEL_MYSQL_DATABASE_URL')
    if cpanel_url:
        print(f"   Found: {cpanel_url[:20]}...{cpanel_url[-20:]}")
        try:
            from sqlalchemy import create_engine, text
            engine = create_engine(cpanel_url, echo=False)
            
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            
            print(f"   ✅ Connection using .env URL successful!")
            engine.dispose()
            
        except Exception as e:
            print(f"   ❌ Connection failed: {e}")
            return False
    else:
        print(f"   ⚠️  CPANEL_MYSQL_DATABASE_URL not found in .env")
    
    print(f"\n{'=' * 70}")
    print(f"✅ ALL TESTS PASSED - Database connection is working!")
    print(f"{'=' * 70}\n")
    return True


def test_postgresql_connection():
    """Test PostgreSQL connection"""
    print("=" * 70)
    print("🔍 Testing PostgreSQL Connection (Local)")
    print("=" * 70)
    
    pg_url = os.getenv('POSTGRESQL_DATABASE_URL')
    if not pg_url:
        print("   ⚠️  POSTGRESQL_DATABASE_URL not found in .env")
        return False
    
    print(f"\n📋 Connection URL: {pg_url[:30]}...{pg_url[-20:]}")
    
    # Test psycopg2
    print(f"\n1️⃣  Checking psycopg2 installation...")
    try:
        import psycopg2
        print(f"   ✅ psycopg2 installed")
    except ImportError as e:
        print(f"   ❌ psycopg2 not installed: {e}")
        print(f"   💡 Install with: pip install psycopg2-binary")
        return False
    
    # Test connection
    print(f"\n2️⃣  Testing PostgreSQL connection...")
    try:
        from sqlalchemy import create_engine, text
        engine = create_engine(pg_url, echo=False)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()
            print(f"   ✅ Connection successful!")
            print(f"   📊 PostgreSQL Version: {version[0][:50]}...")
        
        engine.dispose()
        print(f"\n{'=' * 70}")
        print(f"✅ PostgreSQL connection working!")
        print(f"{'=' * 70}\n")
        return True
        
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        print(f"   💡 This is normal if PostgreSQL is not running locally")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🔬 DATABASE CONNECTION DIAGNOSTIC TOOL")
    print("=" * 70 + "\n")
    
    # Test PostgreSQL (local)
    pg_ok = test_postgresql_connection()
    
    print("\n")
    
    # Test MySQL (cPanel)
    mysql_ok = test_mysql_connection()
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    print(f"PostgreSQL (Local):  {'✅ Working' if pg_ok else '❌ Failed'}")
    print(f"MySQL (cPanel):      {'✅ Working' if mysql_ok else '❌ Failed'}")
    
    if mysql_ok or pg_ok:
        print(f"\n✅ At least one database is working!")
        print(f"   Your application should start successfully.")
    else:
        print(f"\n❌ No database connections working!")
        print(f"   Please fix database configuration before starting the app.")
        sys.exit(1)
    
    print("=" * 70 + "\n")
