# 🚀 Brushy Creek MUD Voice Service - Free Deployment Guide

Deploy your AI voice assistant for **FREE** without running your Mac Mini 24/7!

## 🎯 **Recommended: Deploy to Railway**

### **Step 1: Prepare for Deployment**

1. **Create a Railway account**: Go to [railway.app](https://railway.app) and sign up with GitHub
2. **Install Railway CLI** (optional):
   ```bash
   npm install -g @railway/cli
   ```

### **Step 2: Set Up Your Repository**

1. **Push your code to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial Brushy Creek voice service"
   git remote add origin https://github.com/yourusername/brushy-creek-voice
   git push -u origin main
   ```

### **Step 3: Deploy to Railway**

1. **Go to Railway Dashboard**: [railway.app/new](https://railway.app/new)
2. **Deploy from GitHub**: Connect your repository
3. **Railway will auto-detect** your Python app and use the `Procfile`

### **Step 4: Configure Environment Variables**

In Railway dashboard, add these environment variables:

```bash
# Required API Keys
OPENAI_API_KEY=sk-your-openai-api-key
ELEVENLABS_API_KEY=sk_your-elevenlabs-api-key
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=+18776652873

# Webhook URL (will be: https://yourapp.railway.app)
WEBHOOK_BASE_URL=https://yourapp.railway.app

# Production Settings
DEBUG=false
```

### **Step 5: Update Twilio Webhook**

1. **Get your Railway URL**: `https://yourapp.railway.app`
2. **Update Twilio phone number webhook**:
   - Webhook URL: `https://yourapp.railway.app/voice/incoming`
   - HTTP Method: POST

### **Step 6: Test Your Deployment**

1. **Check health**: `https://yourapp.railway.app/health`
2. **Call your number**: +1 (877) 665-2873
3. **Monitor logs** in Railway dashboard

---

## 🏗️ **Alternative: Google Cloud Run (Pay-per-Use)**

### **Ultra-cheap option** (~$0.001 per call):

1. **Create Dockerfile**:
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   EXPOSE 8080
   CMD ["python3", "start.py"]
   ```

2. **Deploy**:
   ```bash
   gcloud run deploy brushy-creek-voice --source .
   ```

---

## 🛠️ **Alternative: Fly.io (Always-On Free)**

1. **Install flyctl**: [fly.io/docs/hands-on/install-flyctl/](https://fly.io/docs/hands-on/install-flyctl/)

2. **Initialize app**:
   ```bash
   fly launch
   ```

3. **Set environment variables**:
   ```bash
   fly secrets set OPENAI_API_KEY=your-key
   fly secrets set ELEVENLABS_API_KEY=your-key
   # ... etc
   ```

4. **Deploy**:
   ```bash
   fly deploy
   ```

---

## 🔧 **Environment Variables Required**

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `ELEVENLABS_API_KEY` | ElevenLabs API key | `sk_...` |
| `TWILIO_ACCOUNT_SID` | Twilio Account SID | `ACxxxxxxxxx` |
| `TWILIO_AUTH_TOKEN` | Twilio Auth Token | `xxxxx` |
| `TWILIO_PHONE_NUMBER` | Your Twilio number | `+18776652873` |
| `WEBHOOK_BASE_URL` | Your app's public URL | `https://yourapp.railway.app` |
| `DEBUG` | Production mode | `false` |

---

## ✅ **Production Checklist**

- [ ] All environment variables set
- [ ] Twilio webhook updated to new URL
- [ ] Health check working: `/health`
- [ ] Test phone call successful
- [ ] Casey responding with knowledge base
- [ ] ElevenLabs voice working
- [ ] No errors in logs

---

## 💰 **Cost Comparison**

| Platform | Free Tier | Best For |
|----------|-----------|----------|
| **Railway** | $5/month credits | ⭐ **Recommended - Easy setup** |
| **Fly.io** | 3 VMs free | Always-on services |
| **Google Cloud Run** | Pay-per-use | Very low traffic |
| **Render** | Free (sleeps) | ❌ Not suitable (delays) |

---

## 🚨 **Important Notes**

1. **No Sleeping**: Voice services need to be always-on (Railway/Fly.io best)
2. **Webhook Security**: Use HTTPS only for Twilio webhooks
3. **Monitoring**: Set up alerts for service downtime
4. **Logs**: Monitor logs for errors and performance

---

## 📞 **Final Result**

Your Brushy Creek voice service will be running 24/7 at:
- **Phone**: +1 (877) 665-2873  
- **Health Check**: `https://yourapp.railway.app/health`
- **Always Available**: No more Mac Mini required!

**Casey will answer calls with her enhanced knowledge base, providing helpful answers to residents about water rates, facilities, trash schedules, and more!** 🌟 