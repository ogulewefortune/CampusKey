# Quick Check: Is Email Configured on Render?

## Step 1: Check Configuration Status

Visit this URL in your browser (replace with your Render URL):
```
https://campuskey.onrender.com/api/check-email-config
```

This will show you which SMTP variables are set or missing.

## Step 2: What You Should See

### ✅ If Configured Correctly:
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

### ❌ If NOT Configured:
```json
{
  "SMTP_SERVER": "NOT SET",
  "SMTP_PORT": "NOT SET",
  "SMTP_USERNAME": "NOT SET",
  "SMTP_PASSWORD": "NOT SET",
  "FROM_EMAIL": "NOT SET",
  "configured": false
}
```

## Step 3: If Variables Are Missing

1. Go to Render Dashboard: https://dashboard.render.com
2. Click your CampusKey service
3. Click "Environment" tab
4. Add these 5 variables:

```
SMTP_SERVER = smtp.gmail.com
SMTP_PORT = 465
SMTP_USERNAME = your-email@gmail.com
SMTP_PASSWORD = your-16-character-app-password
FROM_EMAIL = your-email@gmail.com
```

5. Click "Save Changes"
6. Wait for Render to redeploy
7. Check the config URL again

## Step 4: Test Email Sending

After setting variables, test email:

1. Open browser console (F12)
2. Run this:
```javascript
fetch('/api/test-email', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({email: 'your-email@gmail.com'})
}).then(r => r.json()).then(console.log)
```

This will:
- Show configuration status
- Try to send a test email
- Show any errors

## Step 5: Check Render Logs

After trying to send an email, check Render logs:

1. Render Dashboard → Your Service → Logs
2. Look for:
   - `✅ Email sent successfully` = Working!
   - `❌ ERROR SENDING EMAIL` = Check error message
   - `⚠️ EMAIL NOT CONFIGURED` = Variables not set

## Common Issues

### "SMTP_PASSWORD: NOT SET"
- Variable not added in Render
- Variable name is wrong (must be exactly `SMTP_PASSWORD`)
- Variable has spaces or special characters

### "SMTP Authentication failed"
- Wrong password
- Using regular password instead of App Password
- Password has spaces (remove them!)

### "[Errno 101] Network is unreachable"
- Port 587 blocked on Render
- Use port 465 instead
- Set `SMTP_PORT=465`

## Quick Fix Checklist

- [ ] Check `/api/check-email-config` shows all variables SET
- [ ] Verify `SMTP_PORT=465` (not 587)
- [ ] Verify `SMTP_PASSWORD` is Gmail App Password (16 chars, no spaces)
- [ ] Verify `SMTP_USERNAME` matches email that created App Password
- [ ] Check Render logs for errors
- [ ] Test with `/api/test-email` endpoint

