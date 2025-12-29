# 🚀 Deploying Product Metrics Copilot API

## Option 1: Railway (Recommended - Easiest)

### Step 1: Push to GitHub
```bash
# Already done! Your repo is at:
# https://github.com/AsafHuga/Product-Co-pilot
```

### Step 2: Deploy to Railway

1. Go to **https://railway.app/**
2. Click **"Start a New Project"**
3. Choose **"Deploy from GitHub repo"**
4. Select **`AsafHuga/Product-Co-pilot`**
5. Railway will auto-detect Python and deploy!

### Step 3: Get Your API URL

After deployment (2-3 minutes):
- Railway will show your URL: `https://your-app.railway.app`
- Copy this URL

### Step 4: Update Lovable Component

In Lovable, update `MetricsAnalyzer.tsx` line 56:
```typescript
const API_URL = 'https://your-app.railway.app';
```

**Done!** ✅

---

## Option 2: Render.com (Also Free)

### Step 1: Create Render Account
Go to **https://render.com** and sign up

### Step 2: Create New Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub: `AsafHuga/Product-Co-pilot`
3. Settings:
   - **Name:** `metrics-copilot-api`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn metrics_copilot.api:app --host 0.0.0.0 --port $PORT`
4. Click **"Create Web Service"**

### Step 3: Get Your URL
- Render URL: `https://metrics-copilot-api.onrender.com`
- Copy this URL

### Step 4: Update Lovable
```typescript
const API_URL = 'https://metrics-copilot-api.onrender.com';
```

---

## Option 3: Vercel (Serverless)

### Step 1: Install Vercel CLI
```bash
npm install -g vercel
```

### Step 2: Deploy
```bash
cd /Users/asafhuga
vercel deploy
```

Follow the prompts, and you'll get a URL.

---

## After Deployment

### Test Your Deployed API

```bash
# Replace with your actual URL
curl https://your-app.railway.app/

# Should return:
# {"name":"Product Metrics Copilot API","version":"0.1.0","status":"healthy"}
```

### Update CORS for Production

In `metrics_copilot/api.py`, update line 15:
```python
allow_origins=[
    "https://lovable.app",
    "https://*.lovable.app",
    "http://localhost:*"
],
```

Then commit and push:
```bash
git add metrics_copilot/api.py
git commit -m "Update CORS for production"
git push
```

Railway/Render will auto-redeploy.

---

## 🎯 Final Lovable Setup

### In your Lovable `MetricsAnalyzer.tsx`:

```typescript
// Line 56
const API_URL = 'https://your-actual-deployed-url.railway.app';
```

### Test It!
1. Upload a CSV in Lovable
2. Should connect to deployed API
3. Get results! 🎉

---

## Troubleshooting

### API not responding
- Check Railway/Render logs
- Make sure requirements.txt has all dependencies
- Verify start command is correct

### CORS errors
- Update `allow_origins` in api.py
- Add your Lovable domain
- Redeploy

### Timeout errors
- Large files may take longer
- Railway free tier has limits
- Consider upgrading if needed

---

## Cost

- **Railway:** Free tier (500 hours/month)
- **Render:** Free tier (750 hours/month)
- **Vercel:** Free for hobby projects

All options are **FREE** for development! 🎉

---

## 🔒 Security for Production

Before going live:
1. Add API authentication
2. Rate limiting
3. File size limits (already in code)
4. Environment variables for secrets
5. HTTPS only (automatic on Railway/Render)

---

**Ready to deploy?** Choose Railway for the easiest experience!
