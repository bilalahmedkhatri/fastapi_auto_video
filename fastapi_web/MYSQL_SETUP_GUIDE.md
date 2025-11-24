# MySQL Database Setup Guide for cPanel

## Current Error
```
Access denied for user 'uihxzefkgh_azeemlab_api'@'localhost' (using password: YES)
```

This means either:
1. Password is incorrect
2. User doesn't have privileges on the database

## Solution: Fix in cPanel (RECOMMENDED)

### Step 1: Add User to Database

1. Login to **cPanel**
2. Go to **MySQL® Databases**
3. Scroll to **"Add User To Database"** section
4. Select:
   - **User**: `uihxzefkgh_azeemlab_api`
   - **Database**: `uihxzefkgh_azeemlab_api`
5. Click **"Add"**
6. On the privileges page:
   - Check **"ALL PRIVILEGES"** (at the top)
   - Click **"Make Changes"**

### Step 2: Verify Password

If adding user doesn't work, reset the password:

1. In cPanel → **MySQL® Database Users** section
2. Find user `uihxzefkgh_azeemlab_api`
3. Click **"Change Password"**
4. Set password to: `5P2bnCA43r3w`
5. Click **"Change Password"**

### Step 3: Test Connection

After fixing, run:
```bash
python test_db_connection.py
```

Should show:
```
✅ Direct connection successful!
```

## Alternative: Command Line Fix (Advanced)

If you have SSH access and root privileges, you can fix this via command line:

```bash
# Login to MySQL as root
mysql -u root -p

# Grant privileges
GRANT ALL PRIVILEGES ON uihxzefkgh_azeemlab_api.* TO 'uihxzefkgh_azeemlab_api'@'localhost' IDENTIFIED BY '5P2bnCA43r3w';
FLUSH PRIVILEGES;
EXIT;
```

Then test:
```bash
mysql -h localhost -u uihxzefkgh_azeemlab_api -p5P2bnCA43r3w uihxzefkgh_azeemlab_api
```

## Verify Database Exists

Make sure the database actually exists:

```bash
mysql -u root -p -e "SHOW DATABASES LIKE 'uihxzefkgh_azeemlab_api';"
```

Should return:
```
+--------------------------------+
| Database (uihxzefkgh_azeemlab_api) |
+--------------------------------+
| uihxzefkgh_azeemlab_api        |
+--------------------------------+
```

## Common cPanel Issues

### Issue 1: Database name has prefix
Some cPanel setups add a prefix to database names.

Check if your actual database name is:
- `uihxzefkgh_azeemlab_api` (current)
- `cpaneluser_azeemlab_api` (with prefix)

To check, look at the database list in cPanel screenshot. Use the **exact name** shown.

### Issue 2: localhost vs 127.0.0.1

Try changing host in `.env`:
```bash
CPANEL_DB_HOST=127.0.0.1
```

Some MySQL setups use different authentication for `localhost` vs `127.0.0.1`.

### Issue 3: Password has special characters

If your password has special characters, it might need URL encoding in the connection string.

Current password: `5P2bnCA43r3w` (no special chars, should be fine)

## After Fixing

Once you've added the user to the database in cPanel:

1. Run test: `python test_db_connection.py`
2. Start app: `uvicorn main:app --host localhost --port 8000`

You should see:
```
✅ Connected to CPANEL MySQL database
```

## Still Not Working?

Take a screenshot of:
1. cPanel → MySQL® Databases → **Current Databases** section (shows privileged users)
2. cPanel → MySQL® Databases → **Current Users** section

And check if user is listed under "Privileged Users" for that database.
