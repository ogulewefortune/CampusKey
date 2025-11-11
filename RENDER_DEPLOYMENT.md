# Render Deployment Guide for CAMPUSKEY

## Prerequisites
- GitHub repository connected to Render
- Render account

## Steps to Deploy

### 1. Environment Variables
Set these in your Render dashboard under your web service settings:

**Required:**
- `SECRET_KEY`: A secure random string (e.g., generate with: `python -c "import secrets; print(secrets.token_hex(32))"`)
- `DATABASE_URL`: Automatically provided by Render if you add a PostgreSQL database

**Email Configuration (REQUIRED for Email OTP to work):**
To enable email OTP verification codes, you MUST set these environment variables:

1. **`SMTP_SERVER`**: Your SMTP server
   - For Gmail: `smtp.gmail.com`
   - For Outlook: `smtp-mail.outlook.com`
   - For other providers: Check your email provider's SMTP settings

2. **`SMTP_PORT`**: SMTP port number
   - For Gmail with TLS: `587`
   - For Gmail with SSL: `465`
   - For Outlook: `587`

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

**Example for Gmail:**
```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=abcdefghijklmnop
FROM_EMAIL=your-email@gmail.com
```

**⚠️ Important Notes:**
- Without these variables set, emails will NOT be sent (codes will only print to console/logs)
- Never commit your email password to GitHub
- Use App Passwords for Gmail (not your regular password)
- Make sure there are NO spaces in the SMTP_PASSWORD when copying from Gmail

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

### Email Not Sending
- Verify SMTP environment variables are set
- Check email service logs in Render dashboard
- For Gmail, ensure you're using an App Password, not regular password

### Build Failures
- Check that all dependencies in `requirements.txt` are valid
- Ensure Python version in `runtime.txt` matches Render's supported versions

## Security Checklist
- [ ] Set a strong `SECRET_KEY` (don't use default)
- [ ] Use environment variables for all sensitive data
- [ ] Enable HTTPS (automatic on Render)
- [ ] Don't commit `.env` files or secrets to GitHub

