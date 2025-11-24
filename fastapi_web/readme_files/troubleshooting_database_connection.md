# Database Connection Error - Quick Fix Guide

## Error Message
```
❌ cPanel MySQL database connection failed
❌ No database connection available!
```

## Step-by-Step Fix

### 1. Install MySQL Drivers
```bash
pip install pymysql cryptography
```

### 2. Run Diagnostic Script
```bash
python test_db_connection.py
```

This will show you the exact error and help identify the issue.

### 3. Verify Database Exists in cPanel

1. Login to **cPanel**
2. Go to **MySQL® Databases**
3. Check if database `uihxzefkgh_azeemlab_api` exists
4. If not, create it:
   - Database Name: `uihxzefkgh_azeemlab_api`
   - Click "Create Database"

### 4. Verify Database User

1. In cPanel MySQL® Databases
2. Check **Current Users** section
3. Verify user `uihxzefkgh_azeemlab_api` exists
4. If not, create it:
   - Username: `uihxzefkgh_azeemlab_api`
   - Password: `5P2bnCA43r3w`
   - Click "Create User"

### 5. Grant User Privileges

1. In cPanel MySQL® Databases
2. Go to **Add User To Database** section
3. Select:
   - User: `uihxzefkgh_azeemlab_api`
   - Database: `uihxzefkgh_azeemlab_api`
4. Click "Add"
5. Grant **ALL PRIVILEGES**
6. Click "Make Changes"

### 6. Test MySQL Connection Manually

```bash
mysql -h localhost -u uihxzefkgh_azeemlab_api -p uihxzefkgh_azeemlab_api
```

Enter password: `5P2bnCA43r3w`

If you can connect, the database is working!

### 7. Verify .env File

Make sure your `.env` file on the server contains:

```bash
cat .env | grep CPANEL
```

Should show:
```
CPANEL_MYSQL_DATABASE_URL=mysql+pymysql://uihxzefkgh_azeemlab_api:5P2bnCA43r3w@localhost:3306/uihxzefkgh_azeemlab_api
CPANEL_DB_HOST=localhost
CPANEL_DB_PORT=3306
CPANEL_DB_NAME=uihxzefkgh_azeemlab_api
CPANEL_DB_USER=uihxzefkgh_azeemlab_api
CPANEL_DB_PASSWORD=5P2bnCA43r3w
CPANEL_DB_TYPE=mysql
```

### 8. Check Installed Packages

```bash
pip list | grep -i mysql
pip list | grep -i crypto
```

Should show:
- `PyMySQL`
- `cryptography`

If missing, install:
```bash
pip install pymysql cryptography
```

## Common Issues & Solutions

### Issue 1: PyMySQL Not Installed
**Error**: `ModuleNotFoundError: No module named 'pymysql'`

**Solution**:
```bash
pip install pymysql cryptography
```

### Issue 2: Database Doesn't Exist
**Error**: `Unknown database 'uihxzefkgh_azeemlab_api'`

**Solution**: Create database in cPanel MySQL® Databases

### Issue 3: Access Denied
**Error**: `Access denied for user 'uihxzefkgh_azeemlab_api'@'localhost'`

**Solution**: 
1. Verify password is correct
2. Check user has privileges on database
3. Re-add user to database in cPanel

### Issue 4: Can't Connect to MySQL Server
**Error**: `Can't connect to MySQL server on 'localhost'`

**Solution**:
1. MySQL might be down (rare on cPanel)
2. Check with hosting provider
3. Verify MySQL is running: `systemctl status mysqld`

### Issue 5: Wrong Host
**Error**: Connection timeout

**Solution**: 
- On cPanel, use `localhost` not `127.0.0.1`
- Some servers use `127.0.0.1` - try both

## Testing After Fix

After fixing, test again:

```bash
# Run diagnostic
python test_db_connection.py

# If successful, start application
uvicorn main:app --host localhost --port 8000
```

You should see:
```
✅ Connected to CPANEL MySQL database
🗄️  Database: CPANEL - mysql+pymysql://uihxzefkgh_****@localhost:3306/uihxzefkgh_azeemlab_api
```

## Still Not Working?

Run diagnostic script and share the output:
```bash
python test_db_connection.py > db_diagnostic.log 2>&1
cat db_diagnostic.log
```

This will show the exact error for troubleshooting.

## Alternative: Use PostgreSQL on cPanel

If MySQL continues to have issues, you can create a PostgreSQL database in cPanel:

1. Go to cPanel → PostgreSQL® Databases
2. Create database: `uihxzefkgh_azeemlab_api`
3. Create user with same name
4. Update `.env`:
```bash
CPANEL_POSTGRESQL_DATABASE_URL=postgresql://uihxzefkgh_azeemlab_api:PASSWORD@localhost:5432/uihxzefkgh_azeemlab_api
CPANEL_DB_TYPE=postgresql
```

The fallback system supports both!
