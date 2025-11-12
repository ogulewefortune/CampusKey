# Debug Email Not Working on Render

## Step 1: Check Render Logs

1. Go to https://dashboard.render.com
2. Click your CampusKey service
3. Click "Logs" tab
4. Look for these messages:

###  Good Signs:
- ` Email sent successfully to [email]`
- ` SSL connection successful on port 465`

###  Error Signs:
- ` ERROR SENDING EMAIL TO [email]`
- ` SMTP Authentication failed`
- ` Connection failed`
- ` EMAIL NOT CONFIGURED`

## Step 2: Test Email Configuration

I've added a test endpoint. To use it:

1. Go to your Render site: `https://campuskey.onrender.com`
2. Open browser console (F12)
3. Run this command:
```javascript
fetch('/api/test-email', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({email: 'your-email@gmail.com'})
}).then(r => r.json()).then(console.log)
```

This will show you:
- Which SMTP variables are set/not set
- Any errors when trying to send
- Configuration status

## Step 3: Verify Environment Variables

Go to Render Dashboard → Your Service → Environment tab

**Check these exact variable names (case-sensitive):**
- `SMTP_SERVER` (not `smtp_server`)
- `SMTP_PORT` (not `smtp_port`)
- `SMTP_USERNAME` (not `smtp_username`)
- `SMTP_PASSWORD` (not `smtp_password`)
- `FROM_EMAIL` (not `from_email`)

**Common Mistakes:**
-  Wrong case: `smtp_server` instead of `SMTP_SERVER`
-  Spaces in password: `abcd efgh` instead of `abcdefgh`
-  Using regular password instead of App Password
-  Missing variables

## Step 4: Gmail App Password Setup

1. Go to https://myaccount.google.com
2. Security → 2-Step Verification (must be enabled)
3. App passwords → Generate
4. Select "Mail" and your device
5. Copy the 16-character password (no spaces!)
6. Paste into Render `SMTP_PASSWORD` variable

## Step 5: Check Port

Make sure `SMTP_PORT=465` (not 587)

Port 465 (SSL) is more reliable on Render than port 587 (TLS).

## Step 6: Check Email Address

- Make sure the email you're testing with matches your Gmail account
- Check spam/junk folder
- Try a different email address

## Common Errors and Fixes

### "SMTP Authentication failed"
- **Fix**: Use App Password, not regular password
- **Fix**: Make sure 2-Step Verification is enabled
- **Fix**: Check SMTP_USERNAME matches the email that created the App Password

### "[Errno 101] Network is unreachable"
- **Fix**: Use port 465 instead of 587
- **Fix**: Check Render region (some regions may block SMTP)

### "SMTP_PASSWORD: NOT SET"
- **Fix**: Variable name must be exactly `SMTP_PASSWORD` (all caps)
- **Fix**: Make sure you saved the variable in Render

### "Connection timeout"
- **Fix**: Check SMTP_SERVER is correct (`smtp.gmail.com`)
- **Fix**: Try port 465
- **Fix**: Check Render logs for network errors

## Still Not Working?

1. Check Render logs for the exact error message
2. Use the test endpoint to see configuration status
3. Verify all 5 environment variables are set correctly
4. Make sure you're using Gmail App Password (16 characters, no spaces)
5. Try port 465 instead of 587

## Quick Test

After setting variables, check logs for:
```
 Email sent successfully to [your-email]
```

If you see errors, they'll tell you exactly what's wrong!

