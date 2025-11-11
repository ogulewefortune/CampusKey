# Quick Guide: Setting Up Email on Render

## Step-by-Step Instructions

### 1. Get Your Gmail App Password

1. Go to https://myaccount.google.com/
2. Click **Security** in the left sidebar
3. Under "How you sign in to Google", click **2-Step Verification**
   - If not enabled, enable it first
4. Scroll down and click **App passwords**
5. Select **Mail** as the app and **Other (Custom name)** as device
6. Enter "CAMPUSKEY" as the name
7. Click **Generate**
8. **Copy the 16-character password** (it will look like: `abcd efgh ijkl mnop`)
   - Remove spaces when copying: `abcdefghijklmnop`

### 2. Set Environment Variables in Render

1. Go to your Render dashboard
2. Click on your **CampusKey** web service
3. Go to **Environment** tab
4. Click **Add Environment Variable** for each of these:

#### Required Email Variables:

**Variable Name:** `SMTP_SERVER`  
**Value:** `smtp.gmail.com`

**Variable Name:** `SMTP_PORT`  
**Value:** `587`

**Variable Name:** `SMTP_USERNAME`  
**Value:** `your-email@gmail.com` (replace with your actual Gmail)

**Variable Name:** `SMTP_PASSWORD`  
**Value:** `abcdefghijklmnop` (paste your 16-character App Password, NO spaces)

**Variable Name:** `FROM_EMAIL`  
**Value:** `your-email@gmail.com` (usually same as SMTP_USERNAME)

### 3. Save and Redeploy

1. After adding all variables, click **Save Changes**
2. Render will automatically redeploy your service
3. Wait for deployment to complete

### 4. Test Email

1. Visit your Render URL (e.g., `https://campuskey.onrender.com`)
2. Go to login page
3. Enter a username and email address
4. Click "Send Code"
5. Check your email inbox for the verification code

## Troubleshooting

### Email Not Received?

1. **Check Render Logs:**
   - Go to Render dashboard → Your service → Logs
   - Look for email-related errors

2. **Verify Environment Variables:**
   - Make sure all 5 variables are set correctly
   - Check for typos in variable names (case-sensitive)
   - Ensure SMTP_PASSWORD has no spaces

3. **Gmail-Specific Issues:**
   - Make sure you're using an App Password, not your regular password
   - Verify 2-Step Verification is enabled
   - Check that "Less secure app access" is NOT needed (App Passwords replace this)

4. **Check Spam Folder:**
   - Sometimes emails go to spam initially

### Common Errors:

**"SMTP Authentication failed"**
- Wrong password or using regular password instead of App Password
- Check SMTP_USERNAME matches the email that created the App Password

**"Connection timeout"**
- Check SMTP_SERVER and SMTP_PORT are correct
- Try port 465 with SSL instead of 587 with TLS

**"Email service returned False"**
- Check Render logs for detailed error messages
- Verify all environment variables are set

## Alternative Email Providers

### Outlook/Hotmail:
```
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USERNAME=your-email@outlook.com
SMTP_PASSWORD=your-password
FROM_EMAIL=your-email@outlook.com
```

### Yahoo Mail:
```
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_USERNAME=your-email@yahoo.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@yahoo.com
```

### Custom SMTP:
Check your email provider's documentation for SMTP settings.

