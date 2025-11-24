# Database Fallback System

## Overview

The FastAPI application now includes an intelligent database connection system with automatic fallback. It will:

1. **Try to connect to LOCAL PostgreSQL database first**
2. **Automatically fall back to cPanel PostgreSQL database** if local is unavailable

This ensures the application can run both in development (local) and production (cPanel) environments seamlessly.

## How It Works

### Connection Priority

```
1. Local PostgreSQL (localhost:5432/auto_video_db)
   ↓ (if connection fails)
2. cPanel PostgreSQL (localhost:5432/uihxzefkgh_azeemlab_api)
   ↓ (if both fail)
3. Throw ConnectionError
```

### Connection Manager

The `DatabaseConnectionManager` class in `models/database_connection.py` handles:

- **Connection testing** - Verifies database availability before using
- **Automatic fallback** - Switches to backup database if primary fails
- **Health monitoring** - Provides health check endpoint
- **Secure logging** - Masks passwords in logs

## Configuration

### Environment Variables

Update your `.env` file with both database configurations:

```env
# Local PostgreSQL (Primary)
POSTGRESQL_DATABASE_URL=postgresql://admin:admin_password@localhost:5432/auto_video_db

# cPanel PostgreSQL (Fallback)
CPANEL_POSTGRESQL_DATABASE_URL=postgresql://uihxzefkgh_azeemlab_api:5P2bnCA43r3w@localhost:5432/uihxzefkgh_azeemlab_api

# Alternative: Individual components (optional)
CPANEL_DB_HOST=localhost
CPANEL_DB_PORT=5432
CPANEL_DB_NAME=uihxzefkgh_azeemlab_api
CPANEL_DB_USER=uihxzefkgh_azeemlab_api
CPANEL_DB_PASSWORD=5P2bnCA43r3w
```

### cPanel Database Setup

Based on your cPanel setup:

- **Database Name**: `uihxzefkgh_azeemlab_api`
- **Username**: `uihxzefkgh_azeemlab_api`
- **Password**: `5P2bnCA43r3w`
- **Host**: `localhost` (on cPanel server)
- **Port**: `5432` (PostgreSQL default)

## Usage

### Starting the Application

The application will automatically:

1. Test local PostgreSQL connection
2. Fall back to cPanel PostgreSQL if needed
3. Log which database is being used

```bash
# Start the application
uvicorn main:app --host localhost --port 8000

# You'll see logs like:
# 🔍 Attempting to connect to local PostgreSQL database...
# ✅ Connected to LOCAL PostgreSQL database
# 🗄️  Database: LOCAL - postgresql://admin:****@localhost:5432/auto_video_db
```

Or if local fails:

```bash
# ⚠️  Local PostgreSQL database not available, trying fallback...
# 🔍 Attempting to connect to cPanel PostgreSQL database...
# ✅ Connected to CPANEL PostgreSQL database
# 🗄️  Database: CPANEL - postgresql://uihxzefkgh_****@localhost:5432/uihxzefkgh_azeemlab_api
```

### Health Check Endpoint

Check database connection status:

```bash
# GET request to health endpoint
curl http://localhost:8000/api/health
```

Response:

```json
{
  "status": "healthy",
  "timestamp": "2025-11-24T10:30:00",
  "database": {
    "status": "healthy",
    "connection_type": "local",
    "message": "Connected to local database"
  },
  "application": {
    "name": "Auto Video Generation API",
    "version": "1.0.0"
  }
}
```

## Force cPanel Database

To force using cPanel database (skip local):

```python
from models.database_connection import db_manager

# Force cPanel connection
engine, conn_type = db_manager.connect(force_cpanel=True)
```

## Database Migration

Both databases should have the same schema. To sync:

### 1. Export Local Schema

```bash
# On your development machine
pg_dump -h localhost -U admin -d auto_video_db --schema-only > schema.sql
```

### 2. Import to cPanel

```bash
# On cPanel server (or via phpPgAdmin)
psql -h localhost -U uihxzefkgh_azeemlab_api -d uihxzefkgh_azeemlab_api < schema.sql
```

### 3. Or Let Application Auto-Create

The application will automatically create tables on startup:

```python
# In main.py startup event
create_db_and_tables()  # Creates tables if they don't exist
```

## Troubleshooting

### Connection Timeout

If connection is slow, adjust timeout in `database_connection.py`:

```python
def _test_connection(self, connection_url: str, timeout: int = 3):
    # Increase timeout to 10 seconds
    timeout = 10
```

### Both Databases Fail

Check logs for error details:

```bash
# View application logs
tail -f logs/auto_video.log
```

Common issues:

1. **Wrong credentials** - Verify username/password in `.env`
2. **Database doesn't exist** - Create database in cPanel
3. **Firewall blocking** - Check PostgreSQL port (5432) is open
4. **PostgreSQL not running** - Start PostgreSQL service

### Force Reconnection

Restart the application to retry connection:

```bash
# Stop application (Ctrl+C)
# Start again
uvicorn main:app --host localhost --port 8000 --reload
```

## Development vs Production

### Development (Local)

- Uses `POSTGRESQL_DATABASE_URL` (local PostgreSQL)
- Fast development with local data
- Full control over database

### Production (cPanel)

- Falls back to `CPANEL_POSTGRESQL_DATABASE_URL`
- Shared hosting environment
- Managed by cPanel

### Hybrid Setup

Keep both databases in sync:

1. Develop locally with local PostgreSQL
2. Deploy to cPanel with automatic fallback
3. Application adapts to environment automatically

## Security Notes

1. **Never commit `.env` file** to version control
2. **Use different passwords** for local and production
3. **Passwords are masked** in application logs
4. **Use strong passwords** for production database

## API Integration

The fallback system is transparent to your API code:

```python
# Your code works the same regardless of which database is used
from models.db_models import get_session

@app.get("/api/example")
async def example(session: Session = Depends(get_session)):
    # Works with both local and cPanel database
    result = session.execute(select(Video))
    return result
```

## Monitoring

Monitor database connection in logs:

```bash
# Filter for database logs
tail -f logs/auto_video.log | grep -i database
```

Look for:

- `✅ Connected to LOCAL PostgreSQL database`
- `✅ Connected to CPANEL PostgreSQL database`
- `❌ No database connection available!`

## Benefits

✅ **Seamless deployment** - Works in any environment  
✅ **Automatic failover** - No manual intervention needed  
✅ **Health monitoring** - Check status via API  
✅ **Secure logging** - Passwords masked in logs  
✅ **Fast testing** - 3-second timeout per database  
✅ **Backward compatible** - Existing code works unchanged  

---

**Last Updated**: November 24, 2025  
**Module**: `models/database_connection.py`
