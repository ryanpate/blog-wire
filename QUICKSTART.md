# Blog Wire - Quick Start Guide

Get your automated blog running in 5 minutes!

## Step 1: Setup Environment

```bash
# Run the automated setup script
./setup.sh

# Or manually:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Step 2: Configure API Keys

Edit `.env` file and add your OpenAI API key:

```env
OPENAI_API_KEY=sk-your-key-here
SECRET_KEY=your-random-secret-key-here
```

**Get your OpenAI API key**: https://platform.openai.com/api-keys

## Step 3: Run the Application

```bash
# Start the web server
python app.py
```

Visit: http://localhost:5000

## Step 4: Generate Your First Blog

**Option A: Via Web API**

```bash
curl -X POST http://localhost:5000/api/generate-blog \
  -H "Content-Type: application/json" \
  -d '{"keyword": "artificial intelligence"}'
```

**Option B: Via Python**

```python
from app import app, automation_service

with app.app_context():
    post = automation_service.generate_single_blog("artificial intelligence")
    print(f"Created: {post.title}")
```

**Option C: Automated Daily Posts**

```bash
# Run the scheduler (generates posts daily at 8 AM)
python scheduler.py
```

## Step 5: Enable Monetization (Optional)

### Google AdSense

1. Sign up at https://www.google.com/adsense
2. Add to `.env`:
```env
ADSENSE_CLIENT_ID=ca-pub-XXXXXXXXXXXXXXXX
ADSENSE_ENABLED=True
```

### Affiliate Links

```bash
curl -X POST http://localhost:5000/api/affiliate-links \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "laptop",
    "url": "https://amazon.com/dp/PRODUCT?tag=your-tag",
    "platform": "amazon"
  }'
```

## Common Tasks

### View Statistics

```bash
curl http://localhost:5000/api/stats
```

### List All Posts

```bash
curl http://localhost:5000/api/posts | python -m json.tool
```

### Generate Multiple Posts

Edit `.env`:
```env
POSTS_PER_DAY=3
```

Then run:
```bash
curl -X POST http://localhost:5000/api/generate-blog
```

## Deployment

### Deploy to Railway

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### Deploy to Render

1. Connect your GitHub repo to Render
2. Add environment variables in Render dashboard
3. Deploy both `web` and `worker` services

## Troubleshooting

**Issue**: No blogs generated
- **Fix**: Check OpenAI API key in `.env`
- **Fix**: Ensure sufficient API credits

**Issue**: No trending topics
- **Fix**: Google Trends may be rate limiting, wait 5 minutes

**Issue**: Database errors
- **Fix**: Delete `blog_wire.db` and restart

## Next Steps

1. Customize blog prompts in `services/blog_generator.py`
2. Modify templates in `templates/` for your design
3. Add custom CSS in `static/css/style.css`
4. Set up your domain and SSL certificate
5. Configure Google Search Console for SEO

## Resources

- Full docs: `README.md`
- API reference: `API_DOCUMENTATION.md`
- OpenAI docs: https://platform.openai.com/docs
- Flask docs: https://flask.palletsprojects.com/

---

**Happy blogging!** Your automated content empire starts now.
