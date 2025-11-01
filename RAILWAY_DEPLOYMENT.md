# Railway Deployment Guide for Blog Wire

## Quick Deploy Steps

### 1. Login to Railway

```bash
railway login
```

This will open a browser window to authenticate.

### 2. Initialize Railway Project

```bash
railway init
```

Select:
- Create a new project: **blog-wire**
- Or link to existing project if you already created one

### 3. Set Environment Variables

```bash
# Set your OpenAI API key
railway variables set OPENAI_API_KEY=sk-your-key-here

# Set Flask secret key
railway variables set SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

# Set other required variables
railway variables set FLASK_ENV=production
railway variables set BLOG_NAME="Blog Wire"
railway variables set BLOG_DOMAIN=your-domain.railway.app
railway variables set POSTS_PER_DAY=1
```

### 4. Add Database (Optional - SQLite works for starter)

For production, you may want PostgreSQL:

```bash
# Add PostgreSQL (optional)
railway add
# Select PostgreSQL from the list
```

If using PostgreSQL, update your DATABASE_URL:
```bash
railway variables set DATABASE_URL=postgresql://...
```

For SQLite (simpler, works fine for this use case):
- No additional setup needed
- Railway will persist the database file

### 5. Deploy!

```bash
railway up
```

This will:
- Build your application
- Deploy to Railway
- Provide you with a URL

### 6. Add Scheduler Service (For Daily Automation)

To run the scheduler that generates daily posts:

**Option A: Using Railway's Cron Jobs (Recommended)**

1. Go to Railway dashboard
2. Click on your project
3. Add a new service: "Cron Job"
4. Set schedule: `0 8 * * *` (8 AM daily)
5. Set command: `python scheduler.py`

**Option B: Add Worker Service**

Create a new service in Railway:
- Name: blog-wire-scheduler
- Start command: `python scheduler.py`

### 7. Get Your Live URL

```bash
railway status
```

Or check the Railway dashboard.

### 8. Set Custom Domain (Optional)

In Railway dashboard:
1. Go to Settings
2. Click "Generate Domain" or add your custom domain
3. Update BLOG_DOMAIN environment variable

## Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `OPENAI_API_KEY` | ✅ Yes | Your OpenAI API key | `sk-...` |
| `SECRET_KEY` | ✅ Yes | Flask session secret | Random hex string |
| `FLASK_ENV` | No | Environment | `production` |
| `BLOG_NAME` | No | Blog name | `Blog Wire` |
| `BLOG_DOMAIN` | No | Your domain | `blog-wire.railway.app` |
| `POSTS_PER_DAY` | No | Daily posts | `1` |
| `ADSENSE_CLIENT_ID` | No | AdSense ID | `ca-pub-...` |
| `ADSENSE_ENABLED` | No | Enable ads | `True` |

## Useful Railway Commands

```bash
# View logs
railway logs

# Open in browser
railway open

# Check status
railway status

# Set environment variable
railway variables set KEY=value

# View all variables
railway variables

# SSH into container
railway shell

# Link to different project
railway link

# Unlink project
railway unlink
```

## Troubleshooting

### Issue: App won't start

**Check logs:**
```bash
railway logs
```

**Common fixes:**
- Ensure OPENAI_API_KEY is set
- Check that gunicorn is in requirements.txt
- Verify PORT environment variable is used

### Issue: Database not persisting

**Solution:** Railway should auto-persist SQLite. If not:
- Add volume in Railway dashboard
- Or switch to PostgreSQL (recommended for production)

### Issue: Scheduler not running

**Solution:**
- Add separate Cron service in Railway
- Or use external cron service like Render Cron Jobs

## Monitoring

**View application:**
```bash
railway open
```

**Check resource usage:**
- Go to Railway Dashboard
- View Metrics tab
- Monitor CPU, Memory, Network

## Scaling

Railway automatically scales based on your plan:
- **Hobby Plan**: $5/month - Good for starting
- **Pro Plan**: $20/month - More resources
- Automatic scaling with traffic

## Cost Estimate

**Typical Monthly Cost:**
- Railway Hosting: $5-20/month
- OpenAI API: $10-50/month (depends on posts generated)
- **Total**: ~$15-70/month

## Production Checklist

- [ ] Set FLASK_ENV=production
- [ ] Use strong SECRET_KEY
- [ ] Enable HTTPS (automatic on Railway)
- [ ] Set up custom domain
- [ ] Configure Google AdSense
- [ ] Add affiliate links
- [ ] Set up monitoring/alerts
- [ ] Enable automatic backups (if using PostgreSQL)
- [ ] Test blog generation
- [ ] Configure cron job for automation

## Next Steps

After deployment:
1. Visit your Railway URL
2. Test blog generation: `curl -X POST https://your-url.railway.app/api/generate-blog -d '{"keyword":"test"}'`
3. Check `/api/stats` endpoint
4. Set up Google Search Console
5. Submit sitemap: `https://your-url.railway.app/sitemap.xml`

---

**Your blog is now live and generating content automatically!** 🚀
