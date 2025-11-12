# Diagnose Email Service Issue on Render

## Quick Diagnosis Steps

### Step 1: Check Email Configuration Status

Visit this URL in your browser:
```
https://campuskey.onrender.com/api/check-email-config
```

**What to look for:**
- ✅ All variables show values (not "NOT SET")
- ✅ `SMTP_PORT` is `465` (not 587)
- ✅ `configured: true`

**If you see "NOT SET":**
- Go to Render Dashboard → Your Service → Environment tab
- Add the missing variables

### Step 2: Test Email Sending

Open browser console (F12) and run:
```javascript
fetch('/api/test-email', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({email: 'your-email@gmail.com'})
}).then(r => r.json()).then(console.log)
```

**What to look for:**
- ✅ `success: true` = Email sent successfully
- ❌ `success: false` = Check the `error` field for details

### Step 3: Check Render Logs

1. Go to https://dashboard.render.com
2. Click your CampusKey service
3. Click "Logs" tab
4. Look for these messages:

**✅ Good Signs:**
- `✅ Email sent successfully to [email]`
- `✅ SSL connection successful on port 465`
- `Attempting SSL connection on port 465...`
- `Authenticating with SMTP server...`

**❌ Error Signs:**
- `❌ ERROR SENDING EMAIL TO [email]`
- `❌ SMTP Authentication failed`
- `⚠️ EMAIL NOT CONFIGURED`
- `Connection failed`
- `[Errno 101] Network is unreachable`

## Common Issues and Fixes

### Issue 1: "SMTP_PASSWORD: NOT SET"

**Problem:** Environment variable not set in Render

**Fix:**
1. Go to Render Dashboard → Your Service → Environment tab
2. Add `SMTP_PASSWORD` variable
3. Value should be your Gmail App Password (16 characters, no spaces)
4. Click "Save Changes"
5. Wait for redeploy

### Issue 2: "SMTP Authentication failed"

**Problem:** Wrong password or using regular password instead of App Password

**Fix:**
1. Go to https://myaccount.google.com
2. Security → 2-Step Verification (must be enabled)
3. App passwords → Generate
4. Select "Mail" and your device
5. Copy the 16-character password (no spaces!)
6. Update `SMTP_PASSWORD` in Render
7. Make sure `SMTP_USERNAME` matches the email that created the App Password

### Issue 3: "[Errno 101] Network is unreachable"

**Problem:** Port 587 is blocked on Render free tier

**Fix:**
1. Set `SMTP_PORT=465` in Render environment variables
2. Port 465 (SSL) works better on Render than port 587 (TLS)
3. Save and wait for redeploy

### Issue 4: "Connection timeout"

**Problem:** SMTP server unreachable or wrong server address

**Fix:**
1. Verify `SMTP_SERVER=smtp.gmail.com` (for Gmail)
2. Check Render logs for network errors
3. Try port 465 instead of 587

### Issue 5: Email shows "sent" but not received

**Problem:** Email is failing silently or going to spam

**Fix:**
1. Check Render logs for actual error messages
2. Check spam/junk folder
3. Verify email address is correct
4. Use `/api/test-email` endpoint to test
5. Check if `email_sent: false` in the response

## Required Environment Variables

Make sure ALL of these are set in Render (case-sensitive):

```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=465
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
FROM_EMAIL=your-email@gmail.com
```

## Verification Checklist

- [ ] All 5 SMTP variables are set in Render
- [ ] `SMTP_PORT=465` (not 587)
- [ ] `SMTP_PASSWORD` is Gmail App Password (16 chars, no spaces)
- [ ] `SMTP_USERNAME` matches email that created App Password
- [ ] 2-Step Verification is enabled on Gmail account
- [ ] `/api/check-email-config` shows `configured: true`
- [ ] `/api/test-email` returns `success: true`
- [ ] Render logs show `✅ Email sent successfully`
- [ ] Checked spam folder

## Still Not Working?

1. **Check Render Logs** - Look for the exact error message
2. **Use Test Endpoint** - `/api/test-email` shows detailed error info
3. **Verify Configuration** - `/api/check-email-config` shows what's set
4. **Check Gmail Settings** - Make sure App Password is correct
5. **Try Different Port** - Use 465 instead of 587

## Debugging Commands

### Check Configuration:
```bash
curl https://campuskey.onrender.com/api/check-email-config
```

### Test Email:
```bash
curl -X POST https://campuskey.onrender.com/api/test-email \
  -H "Content-Type: application/json" \
  -d '{"email":"your-email@gmail.com"}'
```

## What the Code Does

1. **Checks Configuration** - Verifies all SMTP variables are set
2. **Tries SSL First** - Attempts port 465 (SSL) connection
3. **Falls Back to TLS** - If SSL fails, tries port 587 (TLS)
4. **Logs Everything** - All errors are logged to Render logs
5. **Returns Code** - Even if email fails, code is returned so login still works

## Next Steps

1. Run `/api/check-email-config` to see what's configured
2. Run `/api/test-email` to see what error occurs
3. Check Render logs for detailed error messages
4. Fix the issue based on the error message
5. Test again

