# Render PostgreSQL Database Setup Guide

This guide will help you connect your CampusKey application to a PostgreSQL database on Render, ensuring all data changes are persisted.

## ✅ What's Already Configured

Your application is already set up to automatically use PostgreSQL when deployed on Render:
- ✅ Database configuration in `config.py` detects PostgreSQL automatically
- ✅ Connection pooling configured for optimal performance
- ✅ Automatic table creation on first run
- ✅ `psycopg2-binary` added to requirements.txt

## 📋 Step-by-Step Setup

### 1. Create PostgreSQL Database on Render

1. **Log in to Render Dashboard**
   - Go to [render.com](https://render.com)
   - Sign in to your account

2. **Create New PostgreSQL Database**
   - Click **"New +"** button in the top right
   - Select **"PostgreSQL"**
   - Fill in the details:
     - **Name**: `campuskey-db` (or any name you prefer)
     - **Database**: `campuskey` (or leave default)
     - **User**: Leave default (auto-generated)
     - **Region**: Choose closest to your users (e.g., `Oregon (US West)` for North America)
     - **PostgreSQL Version**: `16` (recommended) or latest available
     - **Plan**: 
       - **Free**: For testing/development (limited connections, may spin down)
       - **Starter ($7/month)**: Recommended for production (always on, better performance)

3. **Click "Create Database"**
   - Render will automatically create the database
   - **Important**: Save the connection details shown (you'll need them)

### 2. Connect Database to Your Web Service

#### Option A: Automatic Connection (Recommended)

1. **In Render Dashboard**, go to your **Web Service** (CampusKey app)
2. Click on **"Environment"** tab
3. Scroll down to **"Add Environment Variable"**
4. **You don't need to add DATABASE_URL manually** - Render does this automatically!

#### Option B: Manual Connection

If automatic connection doesn't work:

1. **Get Database Connection String**
   - Go to your PostgreSQL database in Render
   - Click on **"Connections"** tab
   - Copy the **"Internal Database URL"** (for services in same region)
   - Or copy **"External Database URL"** (if needed)

2. **Add to Web Service Environment**
   - Go to your Web Service → **Environment** tab
   - Click **"Add Environment Variable"**
   - **Key**: `DATABASE_URL`
   - **Value**: Paste the connection string (starts with `postgres://`)
   - Click **"Save Changes"**

### 3. Verify Database Connection

After deploying:

1. **Check Logs**
   - Go to your Web Service → **Logs** tab
   - Look for: `Database initialization note:` or similar messages
   - Should see successful table creation messages

2. **Test the Application**
   - Visit your Render URL
   - Try logging in (tables will be created automatically)
   - Create a test user or make changes
   - Restart the service - data should persist!

### 4. Database Tables Created Automatically

Your app will automatically create these tables on first run:
- ✅ `user` - User accounts (admin, professors, students)
- ✅ `login_attempt` - Login history and security logs
- ✅ `active_session` - Active user sessions
- ✅ `email_verification_code` - Email verification codes
- ✅ `course` - Course information
- ✅ `grade` - Student grades
- ✅ `device_fingerprint` - Device security fingerprints
- ✅ `webauthn_credential` - Biometric authentication credentials

## 🔧 Configuration Details

### Connection Pooling (Already Configured)

Your `config.py` includes optimized settings for Render:
- **Pool Size**: 5 connections
- **Max Overflow**: 10 additional connections
- **Pool Pre-ping**: Tests connections before use (handles dropped connections)
- **Pool Recycle**: Recycles connections after 1 hour
- **Connection Timeout**: 10 seconds

### Environment Variables

The app automatically detects:
- ✅ `DATABASE_URL` - Set automatically by Render when database is connected
- ✅ Falls back to SQLite for local development (when DATABASE_URL not set)

## 🚨 Troubleshooting

### Issue: "Database connection failed"

**Solutions:**
1. Verify database is running (check Render dashboard)
2. Ensure `DATABASE_URL` is set in Web Service environment
3. Check database region matches Web Service region (for internal connections)
4. Verify `psycopg2-binary` is in requirements.txt (✅ already added)

### Issue: "Tables not created"

**Solutions:**
1. Check logs for error messages
2. Ensure database has proper permissions
3. Try manual initialization (see below)

### Issue: "Connection pool exhausted"

**Solutions:**
1. This is rare, but if it happens:
   - Upgrade to Starter plan ($7/month) for more connections
   - Or reduce `pool_size` in config.py (not recommended)

## 🔄 Manual Database Initialization (If Needed)

If tables don't create automatically, you can manually initialize:

1. **SSH into Render** (if available) or use Render Shell
2. Run Python shell:
   ```python
   from app import app, db
   with app.app_context():
       db.create_all()
   ```

## 📊 Database Management

### Viewing Your Data

**Option 1: Render Dashboard**
- Go to your PostgreSQL database
- Click **"Connect"** → **"psql"** (opens web-based SQL editor)

**Option 2: External Tool**
- Use pgAdmin, DBeaver, or any PostgreSQL client
- Connect using External Database URL from Render

**Option 3: Command Line**
```bash
# Install psql locally
# Then connect using External Database URL
psql "postgres://user:password@host:port/database"
```

### Backup Your Database

Render automatically backs up databases on paid plans. For free tier:
- Export data manually using `pg_dump`
- Or upgrade to Starter plan for automatic backups

## ✅ Verification Checklist

After setup, verify:
- [ ] PostgreSQL database created on Render
- [ ] Database connected to Web Service (DATABASE_URL set automatically)
- [ ] Application deployed successfully
- [ ] Tables created automatically (check logs)
- [ ] Can login and create users
- [ ] Data persists after service restart
- [ ] No connection errors in logs

## 🎉 Success!

Once configured, your CampusKey application will:
- ✅ Store all data in PostgreSQL on Render
- ✅ Persist data across deployments
- ✅ Handle multiple users simultaneously
- ✅ Maintain login sessions and security logs
- ✅ Scale with connection pooling

## 📝 Notes

- **Free Tier Limitations**: 
  - Database may spin down after inactivity
  - Limited to 90 days of backups
  - Limited connections (usually sufficient for small apps)
  
- **Production Recommendations**:
  - Use Starter plan ($7/month) for always-on database
  - Regular backups enabled
  - Better performance and reliability

- **Local Development**:
  - App automatically uses SQLite locally (when DATABASE_URL not set)
  - No changes needed for local development
  - Data stored in `instance/campuskey.db`

## 🔗 Related Documentation

- [Render PostgreSQL Docs](https://render.com/docs/databases)
- [Flask-SQLAlchemy Docs](https://flask-sqlalchemy.palletsprojects.com/)
- [RENDER_DEPLOYMENT.md](./RENDER_DEPLOYMENT.md) - Full deployment guide

