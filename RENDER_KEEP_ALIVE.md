# Keep Your Render Service Awake (Free Tier)

## Problem
Render's free tier services sleep after ~15 minutes of inactivity, causing 10-30 second delays on first request.

## Solution: Use a Free Keep-Alive Service

### Option 1: UptimeRobot (Recommended)

1. **Sign up**: Go to [https://uptimerobot.com](https://uptimerobot.com) (free account)
2. **Add Monitor**:
   - Click "Add New Monitor"
   - Monitor Type: **HTTP(s)**
   - Friendly Name: `CampusKey Keep-Alive`
   - URL: `https://campuskey.onrender.com/` (your Render URL)
   - Monitoring Interval: **5 minutes** (free tier allows this)
   - Click "Create Monitor"

3. **Done!** UptimeRobot will ping your site every 5 minutes, keeping it awake.

### Option 2: cron-job.org

1. **Sign up**: Go to [https://cron-job.org](https://cron-job.org) (free account)
2. **Create Cron Job**:
   - Title: `CampusKey Keep-Alive`
   - Address: `https://campuskey.onrender.com/`
   - Schedule: Every **10 minutes**
   - Click "Create Cronjob"

3. **Done!** Your service will be pinged every 10 minutes.

### Option 3: Python Script (Run Locally)

If you have a computer that's always on, you can run this script:

```python
import requests
import time

RENDER_URL = "https://campuskey.onrender.com/"

while True:
    try:
        requests.get(RENDER_URL, timeout=10)
        print(f"Pinged {RENDER_URL} at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    except Exception as e:
        print(f"Error: {e}")
    time.sleep(600)  # Wait 10 minutes (600 seconds)
```

Save as `keep_alive.py` and run: `python keep_alive.py`

## Why This Works

- Render free tier sleeps after 15 minutes of inactivity
- Pinging every 5-10 minutes keeps the service awake
- Your site will respond instantly (no cold starts)
- Completely free!

## Important Notes

- **Don't ping too frequently**: Every 5-10 minutes is enough
- **Ping the root URL**: `https://campuskey.onrender.com/` (not `/api/` endpoints)
- **Free services are fine**: UptimeRobot and cron-job.org free tiers work perfectly
- **No code changes needed**: This is external to your app

## Alternative: Upgrade to Paid Tier

If you want instant responses without keep-alive:
- Render Starter: $7/month
- Service stays awake 24/7
- No cold starts ever
- Better for production use

