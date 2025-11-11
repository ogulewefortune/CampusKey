# Quick Fix: OTP Codes Not Working on Render

## Problem
OTP codes work on localhost but not on Render.

## Solution: Set SMTP Environment Variables in Render

### Step 1: Go to Render Dashboard
1. Go to https://dashboard.render.com
2. Click on your CampusKey web service

### Step 2: Add Environment Variables
Click on "Environment" tab, then add these 5 variables:

```
SMTP_SERVER = smtp.gmail.com
SMTP_PORT = 465
SMTP_USERNAME = your-email@gmail.com
SMTP_PASSWORD = your-16-character-app-password
FROM_EMAIL = your-email@gmail.com
```

### Step 3: Get Gmail App Password
1. Go to https://myaccount.google.com
2. Click "Security" → "2-Step Verification" (enable if not enabled)
3. Click "App passwords"
4. Generate password for "Mail"
5. Copy the 16-character password (NO SPACES!)

### Step 4: Save and Redeploy
1. Click "Save Changes" in Render
2. Render will automatically redeploy
3. Wait for deployment to complete

### Step 5: Test
1. Go to your Render site
2. Try sending an OTP code
3. Check your email inbox (and spam folder)

## Verify Configuration

After setting variables, check Render logs:
1. Go to Render dashboard → Your service → Logs
2. Look for:
   - `✅ Email sent successfully` = Working!
   - `❌ ERROR SENDING EMAIL` = Check error message
   - `⚠️ EMAIL NOT CONFIGURED` = Variables not set correctly

## Common Issues

**"SMTP_PASSWORD: NOT SET"**
- Variable not added or has wrong name
- Make sure it's exactly `SMTP_PASSWORD` (all caps)

**"SMTP Authentication failed"**
- Wrong password
- Using regular password instead of App Password
- Password has spaces (remove them!)

**"[Errno 101] Network is unreachable"**
- Use port 465 instead of 587
- Set `SMTP_PORT=465`

## Testing Without Email

If email still doesn't work, the code will now be shown in the alert message when SMTP is not configured. This allows you to test OTP functionality even if email fails.

