# cPanel Deployment Guide for FastAPI Voiceover App

## Prerequisites
- cPanel hosting with Python 3.9+ support
- SSH access (optional but recommended)
- At least 2GB RAM available
- PostgreSQL database access

## Step-by-Step Deployment

### 1. Check Python Version in cPanel
1. Log into cPanel
2. Go to "Setup Python App" or "Python Selector"
3. **CRITICAL**: Check available Python versions
   - ✅ Need: Python 3.9 or higher
   - ❌ If only Python 2.7.x: Contact hosting provider

### 2. Prepare Files for Upload

**Files to Upload:**
```
fastapi_web/
├── passenger_wsgi.py         ← Created automatically
├── main.py
├── requirements.txt
├── .env                       ← Create this (see below)
├── api/
├── kokoro_82M/
├── models/
├── migrations/
├── media/
├── server_starting_apps/
└── All other project files
```

**Create .env file:**
```env
# Database
DATABASE_URL=postgresql://username:password@localhost/database_name

# API Settings
API_BASE_URL=https://yourdomain.com

# Redis (if using Celery - optional)
REDIS_HOST=localhost
REDIS_PORT=6379

# Celery (optional)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

### 3. Upload Files to cPanel

**Option A: File Manager (Easier)**
1. cPanel → File Manager
2. Navigate to `/home/yourusername/`
3. Create folder: `fastapi_web`
4. Upload all files (use ZIP for faster upload)
5. Extract in place

**Option B: FTP/SFTP**
1. Use FileZilla or similar FTP client
2. Connect to your hosting
3. Upload entire `fastapi_web` folder
4. Preserve folder structure

### 4. Create Python Application in cPanel

1. Go to cPanel → "Setup Python App"
2. Click "Create Application"
3. Fill in the form:
   ```
   Python version: 3.9 or higher ⚠️ IMPORTANT
   Application root: /home/yourusername/fastapi_web
   Application URL: Select your domain or subdomain
   Application startup file: passenger_wsgi.py
   Application Entry point: application
   ```
4. Click "Create"

### 5. Install Dependencies

**After app creation, cPanel shows command to enter virtual environment:**
```bash
source /home/yourusername/virtualenv/fastapi_web/3.9/bin/activate && cd /home/yourusername/fastapi_web
```

**Install packages:**
```bash
# Activate virtual environment (command from cPanel)
source /home/yourusername/virtualenv/fastapi_web/3.9/bin/activate

# Navigate to app directory
cd /home/yourusername/fastapi_web

# Install dependencies
pip install -r requirements.txt

# May need to install separately if requirements.txt fails
pip install fastapi uvicorn sqlmodel psycopg2-binary python-dotenv kokoro-onnx torch scipy numpy
```

### 6. Setup Database

**Create PostgreSQL Database in cPanel:**
1. cPanel → PostgreSQL Databases
2. Create new database: `yourusername_fastapi`
3. Create user with password
4. Grant all privileges to user on database
5. Note: hostname is usually `localhost`

**Update .env file** with database credentials

**Run migrations:**
```bash
# SSH into server (if available)
source /home/yourusername/virtualenv/fastapi_web/3.9/bin/activate
cd /home/yourusername/fastapi_web

# Run migrations (if you have alembic)
# OR migrations will auto-run on startup via create_db_and_tables()
```

### 7. Configure Media Directories

```bash
# Create required directories
mkdir -p media/temp/voiceovers
mkdir -p media/voice-samples
chmod 755 media
chmod 755 media/temp
chmod 755 media/temp/voiceovers
```

### 8. Restart Application

In cPanel Python App Manager:
1. Find your application
2. Click "Restart" button
3. Wait 10-15 seconds for model to load

### 9. Test Deployment

**Visit your application URL:**
```
https://yourdomain.com/api/docs
```

**Test free tool endpoint:**
```
POST https://yourdomain.com/api/voiceover/free_tool
{
    "text": "Hello, this is a test",
    "voice_id": "af_sarah",
    "speed": 1.0
}
```

## Important Notes for cPanel

### Model Caching
- ✅ Model loads once at startup (~8 seconds)
- ✅ Uses ~500MB-1GB RAM (constant)
- ⚠️ First request after deployment takes longer

### File Cleanup
- Set up cron job for old file deletion:
  ```bash
  # cPanel → Cron Jobs
  # Run hourly:
  0 * * * * cd /home/yourusername/fastapi_web && source /home/yourusername/virtualenv/fastapi_web/3.9/bin/activate && python cron_job/delete_file.py
  ```

### Limitations on Shared Hosting

**Will NOT work:**
- ❌ Celery (requires Redis + background workers)
- ❌ Multiple workers (shared hosting limits)
- ❌ WebSocket real-time updates

**Will work:**
- ✅ FastAPI application
- ✅ Model caching (singleton pattern)
- ✅ Synchronous endpoints
- ✅ Rate limiting
- ✅ File cleanup via cron
- ✅ Database operations
- ✅ Good for <10 concurrent users

### Troubleshooting

**500 Internal Server Error:**
1. Check error logs: cPanel → Error Log
2. Verify Python version is 3.9+
3. Check passenger_wsgi.py exists
4. Verify all dependencies installed

**Model fails to load:**
1. Check RAM limits (need 1GB+ free)
2. Verify kokoro-onnx installed
3. Check Hugging Face cache directory permissions

**Database connection failed:**
1. Verify DATABASE_URL in .env
2. Check database exists and user has permissions
3. Ensure psycopg2-binary is installed

**Static files not loading:**
1. Check media directory permissions (755)
2. Verify static file paths in main.py
3. Ensure files were uploaded correctly

### Performance Tips

1. **Enable gzip compression** in .htaccess:
   ```apache
   <IfModule mod_deflate.c>
       AddOutputFilterByType DEFLATE text/plain
       AddOutputFilterByType DEFLATE text/html
       AddOutputFilterByType DEFLATE text/xml
       AddOutputFilterByType DEFLATE application/json
   </IfModule>
   ```

2. **Set cache headers** for static files:
   ```apache
   <FilesMatch "\.(wav|mp3|jpg|jpeg|png|gif)$">
       Header set Cache-Control "max-age=3600, public"
   </FilesMatch>
   ```

3. **Monitor resource usage**:
   - cPanel → CPU and Concurrent Connection Usage
   - If hitting limits, consider VPS upgrade

## Expected Behavior After Deployment

✅ **Startup:** 10-15 seconds (model loading)
✅ **First request:** 2-3 seconds (cached model)
✅ **Subsequent requests:** 2-3 seconds each
✅ **Concurrent users:** Up to 5-10 smooth, 10-20 slower
✅ **RAM usage:** Constant ~1GB
✅ **Long text:** Automatic chunking and merging

## Support

If deployment fails:
1. Check Python version (MUST be 3.9+)
2. Review error logs in cPanel
3. Verify all files uploaded correctly
4. Check database connection
5. Ensure sufficient RAM available

**Common hosting providers with Python 3.9+ support:**
- A2 Hosting (Managed VPS)
- SiteGround (Cloud Hosting)
- HostGator (VPS plans)
- InMotion (VPS plans)

**Most shared hosting only has Python 2.7** - you may need VPS/Cloud hosting for this application.
