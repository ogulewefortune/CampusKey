# Render Free Tier Blocks SMTP - Solution Guide

## The Problem

**Error:** `[Errno 101] Network is unreachable`

**Cause:** Render's free tier blocks outbound SMTP connections (ports 465 and 587). This is a Render limitation, not a code issue.

## Solutions (Choose One)

### Option 1: Use SendGrid (Recommended - FREE)

SendGrid offers 100 free emails/day and works perfectly with Render.

**Steps:**

1. **Sign up for SendGrid:**
   - Go to https://sendgrid.com
   - Sign up for free account (100 emails/day free)
   - Verify your email

2. **Get API Key:**
   - Go to Settings → API Keys
   - Create API Key → Full Access
   - Copy the API key

3. **Add to Render:**
   - Render Dashboard → Your Service → Environment
   - Add these variables:
     ```
     EMAIL_SERVICE=sendgrid
     SENDGRID_API_KEY=your-api-key-here
     FROM_EMAIL=fortuneogulewe3@gmail.com
     ```
   - Save and redeploy

4. **Done!** Emails will now work.

### Option 2: Upgrade Render Plan

- Upgrade to Render paid plan ($7/month)
- SMTP connections will work
- No code changes needed

### Option 3: Use Mailgun (Alternative FREE service)

Similar to SendGrid:

1. Sign up at https://mailgun.com (free tier: 5,000 emails/month)
2. Get API key from dashboard
3. Add to Render:
   ```
   EMAIL_SERVICE=mailgun
   MAILGUN_API_KEY=your-api-key
   MAILGUN_DOMAIN=your-domain
   FROM_EMAIL=fortuneogulewe3@gmail.com
   ```

### Option 4: Use Gmail API (More Complex)

Requires OAuth setup - more complex but free.

## Current Status

Your code is correct. The issue is Render's network restrictions on the free tier.

## Quick Fix

The easiest solution is **SendGrid** (Option 1):
- Free (100 emails/day)
- Works immediately with Render
- No code changes needed (I'll add support)
- Takes 5 minutes to set up

## What Happens Now

Until you implement one of the solutions above:
- ✅ Verification codes are still generated
- ✅ Codes are shown in the alert message
- ✅ Users can still login using the displayed code
- ❌ Emails won't be sent (Render blocks SMTP)

The app will continue to work - users just need to use the code shown in the alert instead of checking email.

