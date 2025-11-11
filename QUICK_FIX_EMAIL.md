# QUICK FIX: Get Emails Working on Render (5 Minutes)

## The Problem
Your logs show SMTP connection is being blocked by Render's free tier. This is why you're not receiving emails.

## The ONLY Solution for Render Free Tier: SendGrid

SMTP will NEVER work on Render free tier. You MUST use SendGrid.

## Step-by-Step Setup

### Step 1: Sign Up for SendGrid (2 minutes)

1. Go to: https://sendgrid.com
2. Click "Start for Free"
3. Sign up with your email
4. Verify your email (check inbox)
5. Complete setup wizard

**FREE:** 100 emails/day forever - perfect for your app!

### Step 2: Get API Key (1 minute)

1. In SendGrid dashboard, click **Settings** (left sidebar)
2. Click **API Keys**
3. Click **"Create API Key"** button
4. Name: `CampusKey`
5. Select **"Full Access"**
6. Click **"Create & View"**
7. **COPY THE API KEY NOW** (starts with `SG.` - you'll only see it once!)

### Step 3: Add to Render (2 minutes)

1. Go to: https://dashboard.render.com
2. Click your **CampusKey** service
3. Click **"Environment"** tab
4. Click **"Add Environment Variable"** for each:

**Variable 1:**
- Key: `EMAIL_SERVICE`
- Value: `sendgrid`

**Variable 2:**
- Key: `SENDGRID_API_KEY`
- Value: `SG.your-actual-api-key-here` (paste the key from Step 2)

**Variable 3:**
- Key: `FROM_EMAIL`
- Value: `fortuneogulewe3@gmail.com`

5. Click **"Save Changes"**
6. Wait for Render to redeploy (check Events tab - takes 1-2 minutes)

### Step 4: Test!

1. Go to: https://campuskey.onrender.com
2. Try sending a verification code
3. Check your email inbox!

## Verify It's Working

After redeploy, check Render logs. You should see:
```
SENDING EMAIL VIA SENDGRID API
[SUCCESS] Email sent successfully via SendGrid!
```

If you see "ATTEMPTING TO SEND EMAIL" (SMTP), SendGrid isn't configured correctly.

## Troubleshooting

### Still seeing SMTP in logs?
- Check `EMAIL_SERVICE=sendgrid` is set (case-sensitive)
- Check `SENDGRID_API_KEY` is set correctly
- Make sure you saved changes in Render

### "SendGrid API error: 403"
- API key is wrong or doesn't have Mail Send permission
- Regenerate API key with "Full Access"

### "SendGrid API error: 400"
- `FROM_EMAIL` not verified in SendGrid
- Go to SendGrid → Settings → Sender Authentication → Verify Single Sender

## Important Notes

- **SMTP will NEVER work on Render free tier** - don't waste time trying
- **SendGrid is FREE** - 100 emails/day is plenty for verification codes
- **No code changes needed** - already implemented!
- **Takes 5 minutes** - sign up, get key, add to Render, done!

## What Changed?

The code now:
1. Checks for SendGrid first (works on Render!)
2. Falls back to SMTP if SendGrid not configured (blocked on Render)
3. Falls back to console if nothing configured

Once you add the 3 environment variables, emails will work immediately!

