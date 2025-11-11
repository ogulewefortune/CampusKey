# SendGrid Setup - Fix Render SMTP Blocking

## The Problem
Render's free tier blocks SMTP connections (`[Errno 101] Network is unreachable`). SendGrid uses HTTP API instead, which works perfectly on Render.

## Quick Setup (5 minutes)

### Step 1: Sign Up for SendGrid (FREE)

1. Go to https://sendgrid.com
2. Click "Start for Free"
3. Sign up with your email
4. Verify your email address
5. Complete the setup wizard

**Free Tier:** 100 emails/day forever (perfect for your app!)

### Step 2: Create API Key

1. In SendGrid dashboard, go to **Settings** → **API Keys**
2. Click **"Create API Key"**
3. Name it: `CampusKey Production`
4. Select **"Full Access"** (or "Restricted Access" → Mail Send)
5. Click **"Create & View"**
6. **COPY THE API KEY** (you'll only see it once!)
   - It looks like: `SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### Step 3: Add to Render

1. Go to https://dashboard.render.com
2. Click your **CampusKey** service
3. Click **"Environment"** tab
4. Add these 3 variables:

```
EMAIL_SERVICE=sendgrid
SENDGRID_API_KEY=SG.your-actual-api-key-here
FROM_EMAIL=fortuneogulewe3@gmail.com
```

**Important:**
- Replace `SG.your-actual-api-key-here` with your actual API key from Step 2
- Keep `FROM_EMAIL` as your Gmail address (or any verified email)

5. Click **"Save Changes"**
6. Wait for Render to redeploy (check Events tab)

### Step 4: Verify Sender Email (Optional but Recommended)

1. In SendGrid dashboard, go to **Settings** → **Sender Authentication**
2. Click **"Verify a Single Sender"**
3. Enter your email: `fortuneogulewe3@gmail.com`
4. Fill in the form and verify via email
5. This prevents emails from going to spam

### Step 5: Test!

1. Go to your Render site: `https://campuskey.onrender.com`
2. Try sending a verification code
3. Check your email inbox!

## Verify It's Working

Check Render logs - you should see:
```
📧 SENDING EMAIL VIA SENDGRID API
✅ Email sent successfully via SendGrid!
```

## Troubleshooting

### "SendGrid API error: 403"
- API key is wrong or doesn't have Mail Send permission
- Regenerate API key with "Full Access"

### "SendGrid API error: 400"
- `FROM_EMAIL` is not verified in SendGrid
- Go to Settings → Sender Authentication → Verify your email

### Emails going to spam
- Verify sender email in SendGrid (Step 4 above)
- Add SPF/DKIM records (advanced, optional)

## Cost

**FREE:** 100 emails/day forever
- Perfect for your verification codes
- No credit card required
- Upgrade later if needed (starts at $15/month for 40,000 emails)

## Why SendGrid?

✅ Works on Render free tier (HTTP API, not SMTP)
✅ Free 100 emails/day
✅ Reliable delivery
✅ Easy setup (5 minutes)
✅ Professional emails
✅ No code changes needed (already added!)

## What Changed?

The code now:
1. Checks for `EMAIL_SERVICE=sendgrid` and `SENDGRID_API_KEY`
2. Uses SendGrid API if configured (works on Render!)
3. Falls back to SMTP if SendGrid not configured
4. Falls back to console if nothing configured

## Done!

Once you add the 3 environment variables to Render, emails will work immediately! 🎉

