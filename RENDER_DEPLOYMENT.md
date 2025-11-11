# Render Deployment Guide for CAMPUSKEY

## Prerequisites
- GitHub repository connected to Render
- Render account

## Steps to Deploy

### 1. Environment Variables
Set these in your Render dashboard under your web service settings:

**How to Access Environment Variables in Render:**

1. **Log in to Render Dashboard**
   - Go to [https://dashboard.render.com](https://dashboard.render.com)
   - Sign in with your account

2. **Navigate to Your Web Service**
   - Click on "Services" in the left sidebar (or go to your dashboard)
   - Find and click on your CAMPUSKEY web service

3. **Open Environment Variables Section**
   - In your service page, look for the "Environment" tab in the top menu
   - OR scroll down to find the "Environment Variables" section
   - Click on "Environment" or "Environment Variables"

4. **Add/Edit Variables**
   - You'll see a list of existing environment variables (if any)
   - To add a new variable:
     - Click "Add Environment Variable" or the "+" button
     - Enter the variable name (e.g., `SMTP_PORT`)
     - Enter the value (e.g., `465`)
     - Click "Save Changes"
   - To edit an existing variable:
     - Click on the variable name or the edit icon
     - Update the value
     - Click "Save Changes"

5. **After Making Changes**
   - Render will automatically redeploy your service
   - Wait for the deployment to complete (check the "Events" or "Logs" tab)

**Required:**
- `SECRET_KEY`: A secure random string (e.g., generate with: `python -c "import secrets; print(secrets.token_hex(32))"`)
- `DATABASE_URL`: Automatically provided by Render if you add a PostgreSQL database

**Email Configuration (REQUIRED for Email OTP to work):**
To enable email OTP verification codes, you MUST set these environment variables in Render:

**Quick Checklist - Add these 5 environment variables:**
- [ ] `SMTP_SERVER` = `smtp.gmail.com` (or your email provider's SMTP server)
- [ ] `SMTP_PORT` = `465` (recommended for Render)
- [ ] `SMTP_USERNAME` = `your-email@gmail.com` (your email address)
- [ ] `SMTP_PASSWORD` = `your-app-password` (Gmail App Password, not regular password)
- [ ] `FROM_EMAIL` = `your-email@gmail.com` (usually same as SMTP_USERNAME)

**Detailed Configuration:**

1. **`SMTP_SERVER`**: Your SMTP server
   - For Gmail: `smtp.gmail.com`
   - For Outlook: `smtp-mail.outlook.com`
   - For other providers: Check your email provider's SMTP settings

2. **`SMTP_PORT`**: SMTP port number
   - **Recommended for Render**: `465` (SSL) - more reliable on cloud platforms
   - For Gmail with TLS: `587` (may have network issues on Render)
   - For Gmail with SSL: `465` (recommended)
   - For Outlook: `587` or `465`

3. **`SMTP_USERNAME`**: Your email address
   - Example: `your-email@gmail.com`

4. **`SMTP_PASSWORD`**: Your email app password
   - **IMPORTANT**: For Gmail, you MUST use an App Password, NOT your regular password
   - To create a Gmail App Password:
     1. Go to your Google Account settings
     2. Enable 2-Step Verification (if not already enabled)
     3. Go to App Passwords
     4. Generate a new app password for "Mail"
     5. Copy the 16-character password (no spaces)
   - For other providers, use your email password or app-specific password

5. **`FROM_EMAIL`**: Sender email address (usually same as SMTP_USERNAME)
   - Example: `your-email@gmail.com`

**Example for Gmail (Recommended for Render):**
```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=465
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=abcdefghijklmnop
FROM_EMAIL=your-email@gmail.com
```

**Note:** 
- Port 465 (SSL) is recommended for Render deployments as it's more reliable than port 587 (TLS) on cloud platforms. The code will automatically try port 465 as a fallback if port 587 fails.
- **Email sending is asynchronous**: Emails are sent in the background to prevent request timeouts. The API returns immediately while the email is being sent.
- **Timeout reduced**: Connection timeout is set to 10 seconds (reduced from 30) to fail faster if SMTP is unreachable.

**⚠️ Important Notes:**
- Without these variables set, emails will NOT be sent (codes will only print to console/logs)
- Never commit your email password to GitHub
- Use App Passwords for Gmail (not your regular password)
- Make sure there are NO spaces in the SMTP_PASSWORD when copying from Gmail

**WebAuthn/Biometric Authentication Configuration:**
- ✅ **Automatically configured**: The app automatically uses `RENDER_EXTERNAL_URL` (provided by Render) for WebAuthn
- ✅ **Biometrics WILL work on Render** - no additional configuration needed!
- **How it works**: 
  - Render automatically sets `RENDER_EXTERNAL_URL` (e.g., `https://campuskey.onrender.com`)
  - Your app extracts the domain for WebAuthn RP_ID automatically
  - Just register your biometric on the Render site (credentials from localhost won't work on Render)
- **Optional customization**: If you need a custom domain for WebAuthn:
  - `WEBAUTHN_RP_ID`: Custom Relying Party ID (domain name, e.g., `yourdomain.com`)
  - `WEBAUTHN_ORIGIN`: Custom origin URL (e.g., `https://yourdomain.com`)
- **Note**: For most deployments, you don't need to set these - Render's `RENDER_EXTERNAL_URL` is automatically used
- See `RENDER_WEBAUTHN_CHECK.md` for detailed WebAuthn configuration information

**Optional:**
- `FLASK_DEBUG`: Set to `False` for production (default is False)
- `PORT`: Automatically set by Render (don't override)

### 2. Database Setup
1. In Render dashboard, add a PostgreSQL database
2. Render will automatically set `DATABASE_URL` environment variable
3. The app will automatically create tables on first run

### 3. Build & Deploy Settings
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: (Leave empty - Procfile handles this)
- **Python Version**: 3.11.4 (specified in runtime.txt)

### 4. Files Already Configured
✅ `Procfile` - Tells Render how to run the app  
✅ `requirements.txt` - All dependencies including pytz  
✅ `runtime.txt` - Python version  
✅ `config.py` - Handles DATABASE_URL automatically  

### 5. Post-Deployment
After deployment:
1. Visit your Render URL
2. The app will automatically create database tables
3. Sample users will be created if database is empty
4. Test login with demo users

## Troubleshooting

### Database Issues
- Ensure PostgreSQL database is added and connected
- Check `DATABASE_URL` is set correctly
- Database tables are created automatically on first run

### Email Not Sending / Not Receiving Emails

**Symptom**: App says "code sent" but you don't receive the email

**How to Debug**:

1. **Check Render Logs**:
   - Go to your Render dashboard
   - Click on your web service
   - Click "Logs" tab
   - Look for email-related errors (search for "ERROR SENDING EMAIL" or "SMTP")
   - Check if SMTP environment variables are set correctly

2. **Verify SMTP Environment Variables**:
   - Go to Render dashboard → Your service → Environment tab
   - Verify these are set:
     - `SMTP_SERVER` = `smtp.gmail.com`
     - `SMTP_PORT` = `465` (recommended)
     - `SMTP_USERNAME` = your email
     - `SMTP_PASSWORD` = your app password (no spaces!)
     - `FROM_EMAIL` = your email
   - **Important**: Make sure `SMTP_PASSWORD` has NO spaces when copying from Gmail

3. **Check Spam Folder**:
   - Emails might be going to spam
   - Check spam/junk folder in your email

4. **Check Email Address**:
   - Make sure the email address you entered is correct
   - Try a different email address to test

5. **Common Error: "[Errno 101] Network is unreachable"**

This error occurs when Render cannot connect to external SMTP servers. Solutions:

1. **Use SSL Port (465) instead of TLS Port (587)**
   - Change `SMTP_PORT` from `587` to `465` in Render environment variables
   - SSL connections are more reliable on cloud platforms
   - Example: `SMTP_PORT=465`

2. **Verify SMTP Configuration**
   - Ensure all SMTP environment variables are set correctly
   - For Gmail, use an App Password (not regular password)
   - Check email service logs in Render dashboard for detailed errors

3. **Alternative: Use Cloud Email Services**
   - Consider using SendGrid, Mailgun, or AWS SES for better cloud compatibility
   - These services are designed for cloud platforms and have better reliability

4. **Network Restrictions**
   - Some Render regions may have network restrictions
   - Try deploying to a different region if issues persist
   - Contact Render support if SMTP ports are blocked in your region

### Build Failures
- Check that all dependencies in `requirements.txt` are valid
- Ensure Python version in `runtime.txt` matches Render's supported versions

### Slow Loading / Cold Starts (Free Tier)

**Issue**: Service takes 10-30 seconds to respond on first request after inactivity

**What's happening**: Render's free tier services automatically sleep after ~15 minutes of inactivity to save resources. When you visit the site, it needs to "wake up" which takes time.

**Solutions**:

1. **Use a Keep-Alive Service** (Free):
   - Use a free service like [UptimeRobot](https://uptimerobot.com/) or [cron-job.org](https://cron-job.org/)
   - Set it to ping your Render URL every 10-14 minutes
   - This keeps your service awake and prevents cold starts
   - Example: `https://campuskey.onrender.com/` (ping the root URL)

2. **Upgrade to Paid Tier** ($7/month):
   - Paid services stay awake 24/7
   - No cold starts, instant response
   - Better for production use

3. **Optimize Startup Time** (Already done):
   - Database initialization is now lazy (only runs on first request)
   - This reduces cold start time from ~30s to ~10-15s

4. **Accept the Delay**:
   - Free tier is free for a reason
   - First request after sleep takes 10-30 seconds
   - Subsequent requests are fast until service sleeps again

## Security Checklist
- [ ] Set a strong `SECRET_KEY` (don't use default)
- [ ] Use environment variables for all sensitive data
- [ ] Enable HTTPS (automatic on Render)
- [ ] Don't commit `.env` files or secrets to GitHub

