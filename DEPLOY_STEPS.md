# 🚂 Railway Deployment - Quick Steps

Follow these steps in order to deploy Blog Wire to Railway.

## Prerequisites

✅ Railway CLI installed (you have this)
✅ GitHub repo pushed (done)
✅ OpenAI API key ready

## Step-by-Step Deployment

### 1️⃣ Login to Railway (In Your Terminal)

Open a new terminal window and run:

```bash
cd ~/blog-wire
railway login
```

This will:
- Open your browser
- Ask you to authenticate with Railway
- Return you to the terminal

### 2️⃣ Run the Deployment Script

After logging in, run the automated deployment script:

```bash
./deploy_railway.sh
```

This script will:
- ✅ Check if you're logged in
- ✅ Initialize Railway project
- ✅ Set environment variables
- ✅ Deploy your application
- ✅ Give you the live URL

**Important:** When prompted, paste your OpenAI API key

### 3️⃣ Alternative: Manual Deployment

If you prefer manual control:

```bash
# 1. Login
railway login

# 2. Initialize project
railway init
# Choose: Create new project
# Name it: blog-wire

# 3. Set environment variables
railway variables set OPENAI_API_KEY=sk-your-actual-key-here
railway variables set SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
railway variables set FLASK_ENV=production
railway variables set BLOG_NAME="Blog Wire"

# 4. Deploy
railway up

# 5. Get your URL
railway status
```

### 4️⃣ Verify Deployment

After deployment completes:

```bash
# Check deployment status
railway status

# View logs
railway logs

# Open in browser
railway open
```

### 5️⃣ Test Your Live Blog

Once deployed, test these endpoints:

```bash
# Replace YOUR-URL with your Railway URL

# Homepage
curl https://YOUR-URL.railway.app/

# API Stats
curl https://YOUR-URL.railway.app/api/stats

# Generate a blog post
curl -X POST https://YOUR-URL.railway.app/api/generate-blog \
  -H "Content-Type: application/json" \
  -d '{"keyword": "test topic"}'
```

### 6️⃣ Add Daily Automation (Optional)

To enable automatic daily blog generation:

**Option A: Railway Cron Jobs**
1. Go to Railway Dashboard: https://railway.app
2. Select your project
3. Click "New" → "Cron Job"
4. Set schedule: `0 8 * * *` (8 AM daily)
5. Set command: `python scheduler.py`

**Option B: External Cron Service**
- Use your Railway URL with an external cron service
- Call: `POST https://your-url.railway.app/api/generate-blog`

### 7️⃣ Get Your Custom Domain (Optional)

In Railway Dashboard:
1. Go to Settings
2. Click "Generate Domain" (free .railway.app subdomain)
3. Or add your custom domain

Then update your environment:
```bash
railway variables set BLOG_DOMAIN=your-domain.railway.app
```

## 🎉 You're Live!

Your blog is now:
- ✅ Deployed to Railway
- ✅ Accessible at your Railway URL
- ✅ Generating AI-powered blog posts
- ✅ SEO optimized and ready to monetize

## Common Issues

**Issue: "Not logged in"**
```bash
railway login
```

**Issue: "OPENAI_API_KEY not set"**
```bash
railway variables set OPENAI_API_KEY=sk-your-key
```

**Issue: App won't start**
```bash
railway logs  # Check the logs
```

**Issue: Can't find project**
```bash
railway link  # Link to existing project
```

## Next Steps

1. **Test blog generation** on your live URL
2. **Add Google AdSense** (update .env variables)
3. **Add affiliate links** via API
4. **Submit sitemap** to Google Search Console
5. **Monitor costs** in Railway dashboard

## Useful Commands

```bash
# View all environment variables
railway variables

# Update a variable
railway variables set KEY=value

# View deployment logs
railway logs

# SSH into your container
railway shell

# Redeploy
railway up

# Check resource usage
railway status
```

## Cost Estimate

**Railway Costs:**
- Free tier: $5 credit/month
- Hobby: $5/month (recommended)
- Pro: $20/month

**OpenAI Costs:**
- ~$0.01-0.05 per blog post
- 1 post/day = ~$1.50/month
- Adjust POSTS_PER_DAY based on budget

---

**Questions?** Check `RAILWAY_DEPLOYMENT.md` for detailed docs.

**Your automated blog is live!** 🚀
