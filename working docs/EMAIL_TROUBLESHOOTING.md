# Email Service Troubleshooting - Quick Fix Guide

## The Problem
You're seeing "Verification code sent to [email]" but not receiving emails on Render.

## Most Likely Causes (in order)

### 1. Environment Variables Not Set (90% of issues)
**Check:** Visit `https://campuskey.onrender.com/api/check-email-config`

**If you see "NOT SET":**
- Go to Render Dashboard → Your Service → Environment
- Add these 5 variables (exact names, case-sensitive):
  ```
  SMTP_SERVER=smtp.gmail.com
  SMTP_PORT=465
  SMTP_USERNAME=your-email@gmail.com
  SMTP_PASSWORD=your-16-char-app-password
  FROM_EMAIL=your-email@gmail.com
  ```
- Click "Save Changes"
- Wait for redeploy (check Events tab)

### 2. Wrong Password Type (80% of auth failures)
**Problem:** Using regular Gmail password instead of App Password

**Fix:**
1. Go to https://myaccount.google.com
2. Security → 2-Step Verification (enable if needed)
3. App passwords → Generate
4. Select "Mail" → Generate
5. Copy the 16-character password (no spaces!)
6. Paste into Render `SMTP_PASSWORD` variable
7. Make sure `SMTP_USERNAME` matches the email that created the App Password

### 3. Wrong Port (70% of connection failures)
**Problem:** Port 587 blocked on Render free tier

**Fix:**
- Set `SMTP_PORT=465` (not 587)
- Port 465 (SSL) works better on Render

### 4. Password Has Spaces or Wrong Format
**Problem:** App Password copied with spaces or extra characters

**Fix:**
- App Password should be exactly 16 characters
- No spaces, no dashes
- Copy directly from Google (don't type it)

## Quick Diagnostic Steps

### Step 1: Check Configuration
Visit: `https://campuskey.onrender.com/api/check-email-config`

Should show:
```json
{
  "SMTP_SERVER": "smtp.gmail.com",
  "SMTP_PORT": "465",
  "SMTP_USERNAME": "your-email@gmail.com",
  "SMTP_PASSWORD": "SET",
  "FROM_EMAIL": "your-email@gmail.com",
  "configured": true
}
```

### Step 2: Test Email Sending
Open browser console (F12) and run:
```javascript
fetch('/api/test-email', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({email: 'your-email@gmail.com'})
}).then(r => r.json()).then(console.log)
```

### Step 3: Check Render Logs
1. Render Dashboard → Your Service → Logs
2. Look for:
   - ✅ `✅ Email sent successfully` = Working!
   - ❌ `❌ ERROR SENDING EMAIL` = Check error message
   - ❌ `⚠️ EMAIL NOT CONFIGURED` = Variables not set
   - ❌ `SMTP Authentication failed` = Wrong password
   - ❌ `[Errno 101] Network is unreachable` = Port issue

## What the Logs Tell You

### "SMTP_PASSWORD: NOT SET"
→ Variable not added in Render or wrong name

### "SMTP Authentication failed"
→ Wrong password or using regular password instead of App Password

### "[Errno 101] Network is unreachable"
→ Port 587 blocked, use port 465

### "Connection timeout"
→ Wrong SMTP server or network issue

### "Email sent successfully" but not received
→ Check spam folder, verify email address

## Complete Fix Checklist

- [ ] All 5 variables set in Render (check `/api/check-email-config`)
- [ ] `SMTP_PORT=465` (not 587)
- [ ] `SMTP_PASSWORD` is Gmail App Password (16 chars, no spaces)
- [ ] `SMTP_USERNAME` matches email that created App Password
- [ ] 2-Step Verification enabled on Gmail
- [ ] Render finished redeploying after changes
- [ ] `/api/test-email` returns `success: true`
- [ ] Render logs show `✅ Email sent successfully`
- [ ] Checked spam/junk folder

## Still Not Working?

1. **Check Render Logs** - Look for the exact error (it tells you what's wrong)
2. **Use `/api/test-email`** - Shows detailed error information
3. **Verify with `/api/check-email-config`** - Confirms what's configured
4. **Double-check App Password** - Regenerate if unsure
5. **Try port 465** - More reliable on Render

## Important Notes

- The code will show the verification code in the alert even if email fails
- Check Render logs for the actual error message
- Environment variable names are case-sensitive (`SMTP_PASSWORD` not `smtp_password`)
- App Password must be exactly 16 characters with no spaces
- Port 465 (SSL) is more reliable than port 587 (TLS) on Render

