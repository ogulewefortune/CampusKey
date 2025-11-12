# Fix "[Errno 101] Network is unreachable" on Render

## The Problem
Render's free tier often blocks port 587 (TLS), causing "[Errno 101] Network is unreachable" errors.

## The Solution

### Step 1: Set SMTP_PORT to 465 in Render

1. Go to Render Dashboard → Your Service → Environment tab
2. Find `SMTP_PORT` variable
3. Change it to: `465`
4. If it doesn't exist, add it: `SMTP_PORT = 465`
5. Click "Save Changes"
6. Render will redeploy automatically

### Step 2: Verify All Variables Are Set

Make sure these are all set in Render:
```
SMTP_SERVER = smtp.gmail.com
SMTP_PORT = 465
SMTP_USERNAME = your-email@gmail.com
SMTP_PASSWORD = your-16-char-app-password
FROM_EMAIL = your-email@gmail.com
```

### Step 3: Wait for Redeploy

After saving, wait for Render to finish redeploying (check the "Events" tab).

### Step 4: Test Again

Try sending an OTP code again. The code now:
- Tries port 465 (SSL) first (more reliable on Render)
- Falls back to port 587 (TLS) if needed
- Shows clear error messages

## Why Port 465 Works Better

- **Port 465 (SSL)**: Direct encrypted connection - works on Render
- **Port 587 (TLS)**: Starts unencrypted then upgrades - often blocked on Render free tier

## What Changed in the Code

The email service now:
1. Defaults to port 465 (instead of 587)
2. Tries SSL first, then TLS as fallback
3. Has better error messages
4. Uses 15-second timeout (instead of 10)

## Still Getting Errors?

1. **Check Render Logs** for the exact error message
2. **Verify SMTP_PASSWORD** is a Gmail App Password (16 characters, no spaces)
3. **Check SMTP_USERNAME** matches the email that created the App Password
4. **Try the test endpoint**: `/api/test-email` to see configuration status

## Quick Checklist

- [ ] `SMTP_PORT` is set to `465` in Render
- [ ] All 5 SMTP variables are set correctly
- [ ] Using Gmail App Password (not regular password)
- [ ] No spaces in `SMTP_PASSWORD`
- [ ] Render has finished redeploying

After setting `SMTP_PORT=465`, emails should work!

