# 🎉 Blog Wire Setup Complete!

Your automated blog platform is ready. Follow these final steps to get started.

## 📋 Configuration Checklist

### 1. Add Your OpenAI API Key

Edit `.env` file:
```bash
nano .env
# or
code .env
```

**Required changes:**
```env
# Replace this line:
OPENAI_API_KEY=your_openai_api_key_here

# With your actual key:
OPENAI_API_KEY=sk-your-actual-key-here

# Replace this line:
SECRET_KEY=your_secret_key_here

# With this generated key:
SECRET_KEY=48806db2fded5a90bc3a2f0a0ed41a4144bac94aa77762213e480f20eee9b0fa
```

**Get your OpenAI API key:** https://platform.openai.com/api-keys

### 2. Test Your Setup

```bash
source venv/bin/activate
python test_setup.py
```

This will verify:
- ✅ API keys are configured
- ✅ Database is working
- ✅ OpenAI connection works
- ✅ All services load correctly

### 3. Start the Blog

**Option A: Run web server only**
```bash
source venv/bin/activate
python app.py
```
Visit: http://localhost:5000

**Option B: Run with automation (recommended)**

Terminal 1 - Web Server:
```bash
source venv/bin/activate
python app.py
```

Terminal 2 - Automation:
```bash
source venv/bin/activate
python scheduler.py
```

## 🚀 Quick Commands

### Generate Your First Blog Post

```bash
# Generate from a specific keyword
curl -X POST http://localhost:5000/api/generate-blog \
  -H "Content-Type: application/json" \
  -d '{"keyword": "artificial intelligence trends 2024"}'

# Generate from trending topics
curl -X POST http://localhost:5000/api/generate-blog
```

### View Statistics

```bash
curl http://localhost:5000/api/stats | python3 -m json.tool
```

### Add Affiliate Link

```bash
curl -X POST http://localhost:5000/api/affiliate-links \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "laptop",
    "url": "https://amazon.com/dp/PRODUCT?tag=your-tag",
    "platform": "amazon"
  }'
```

### List All Posts

```bash
curl http://localhost:5000/api/posts | python3 -m json.tool
```

## 📁 Important Files

| File | Purpose |
|------|---------|
| `.env` | Configuration (API keys, settings) |
| `app.py` | Main web application |
| `scheduler.py` | Automated daily blog generation |
| `test_setup.py` | Setup verification script |
| `blog_wire.db` | SQLite database (auto-created) |
| `scheduler.log` | Automation logs |

## ⚙️ Configuration Options

Edit `.env` to customize:

```env
# How many posts per day?
POSTS_PER_DAY=1

# Word count range
MIN_WORD_COUNT=2000
MAX_WORD_COUNT=3500

# Blog branding
BLOG_NAME=Blog Wire
BLOG_DOMAIN=blog-wire.com

# OpenAI model
OPENAI_MODEL=gpt-4-turbo-preview
```

## 🎯 Next Steps

1. **Test the system**: Run `python test_setup.py`
2. **Generate first blog**: Use the curl command above
3. **Enable monetization**:
   - Sign up for Google AdSense
   - Add affiliate links via API
4. **Deploy to production**:
   - Railway: `railway up`
   - Render: Connect GitHub repo
   - Heroku: `git push heroku main`

## 📚 Documentation

- **Full Guide**: README.md
- **API Reference**: API_DOCUMENTATION.md
- **Quick Start**: QUICKSTART.md

## 🐛 Troubleshooting

**No blogs generating?**
- Check OpenAI API key in `.env`
- Verify API credits: https://platform.openai.com/usage

**Database errors?**
- Delete `blog_wire.db` and restart

**Google Trends issues?**
- Rate limiting - wait 5 minutes
- Use manual keywords instead

## 💡 Tips

1. Start with manual generation to test
2. Monitor `scheduler.log` for automation status
3. Use `gpt-3.5-turbo` for lower costs during testing
4. Add affiliate links before generating blogs
5. Check `/api/stats` to track performance

---

**Ready to launch your automated content empire!** 🚀

Run: `python test_setup.py` to verify everything works.
