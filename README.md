# Blog Wire - Automated AI Blog Platform

An automated blog platform that generates SEO-optimized, long-form content on trending topics using OpenAI's GPT API and Google Trends.

## Features

- **Automated Content Generation**: Daily automated blog post creation using OpenAI GPT
- **Trending Topic Discovery**: Fetches trending topics from Google Trends API
- **SEO Optimized**: Auto-generated meta tags, schema markup, and sitemap
- **Monetization Ready**: Google AdSense integration and affiliate link management
- **Minimal Human Intervention**: Fully automated workflow with scheduling
- **Modern Tech Stack**: Flask, SQLAlchemy, APScheduler

## Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key
- pip package manager

### Installation

1. **Clone the repository**
```bash
cd blog-wire
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
```

Edit `.env` file and add your configuration:
```env
OPENAI_API_KEY=your_openai_api_key_here
ADSENSE_CLIENT_ID=ca-pub-XXXXXXXXXXXXXXXX
SECRET_KEY=your_secret_key_here
```

5. **Initialize database**
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

Or simply run the app (it will auto-create tables):
```bash
python app.py
```

## Usage

### Running the Web Application

```bash
python app.py
```

Access the blog at: `http://localhost:5000`

### Running the Automated Scheduler

The scheduler automatically generates blog posts daily at 8:00 AM:

```bash
python scheduler.py
```

This will:
1. Fetch trending topics from Google Trends
2. Generate blog posts using OpenAI
3. Inject affiliate links
4. Publish automatically

### Manual Blog Generation

You can manually trigger blog generation via API:

```bash
# Generate blog from trending topics
curl -X POST http://localhost:5000/api/generate-blog

# Generate blog for specific keyword
curl -X POST http://localhost:5000/api/generate-blog \
  -H "Content-Type: application/json" \
  -d '{"keyword": "artificial intelligence"}'
```

## API Endpoints

### Public Routes

- `GET /` - Homepage with blog list
- `GET /blog/<slug>` - Individual blog post
- `GET /sitemap.xml` - SEO sitemap
- `GET /robots.txt` - Robots.txt file

### API Routes

- `POST /api/generate-blog` - Trigger blog generation
- `GET /api/stats` - Get blog statistics
- `GET /api/posts` - Get all posts (JSON)
- `GET /api/trending-topics` - Get trending topics
- `GET /api/affiliate-links` - Get affiliate links
- `POST /api/affiliate-links` - Add new affiliate link

## Project Structure

```
blog-wire/
├── app.py                  # Main Flask application
├── config.py              # Configuration
├── models.py              # Database models
├── scheduler.py           # Automated scheduling
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
├── services/
│   ├── trends_service.py      # Google Trends integration
│   ├── blog_generator.py      # OpenAI blog generation
│   ├── seo_service.py         # SEO optimization
│   ├── affiliate_service.py   # Affiliate link management
│   └── automation_service.py  # Main automation workflow
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── blog_post.html
│   ├── 404.html
│   └── 500.html
└── static/
    └── css/
        └── style.css
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (required) | - |
| `OPENAI_MODEL` | GPT model to use | gpt-4-turbo-preview |
| `ADSENSE_CLIENT_ID` | Google AdSense client ID | - |
| `ADSENSE_ENABLED` | Enable AdSense | False |
| `POSTS_PER_DAY` | Number of posts to generate daily | 1 |
| `MIN_WORD_COUNT` | Minimum words per post | 2000 |
| `MAX_WORD_COUNT` | Maximum words per post | 3500 |

### Scheduling

Edit `scheduler.py` to change the schedule:

```python
# Default: Daily at 8:00 AM
scheduler.add_job(
    daily_blog_generation_job,
    trigger=CronTrigger(hour=8, minute=0),
    ...
)
```

## Monetization

### Google AdSense

1. Set up AdSense account at https://www.google.com/adsense
2. Add your client ID to `.env`:
```env
ADSENSE_CLIENT_ID=ca-pub-XXXXXXXXXXXXXXXX
ADSENSE_ENABLED=True
```
3. Update ad slot IDs in templates:
   - `templates/index.html` - Homepage ad
   - `templates/blog_post.html` - In-article and bottom ads

### Affiliate Links

Add affiliate links via API:

```bash
curl -X POST http://localhost:5000/api/affiliate-links \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "laptop",
    "url": "https://amazon.com/dp/PRODUCT?tag=your-tag",
    "platform": "amazon"
  }'
```

The system will automatically inject affiliate links into blog content when keywords match.

## Deployment

### Railway / Render / Heroku

1. Create a `Procfile`:
```
web: gunicorn app:app
worker: python scheduler.py
```

2. Set environment variables in your hosting platform
3. Deploy the application
4. Ensure both `web` and `worker` dynos are running

### Custom Server

```bash
# Production server with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Run scheduler in background
nohup python scheduler.py &
```

## Development

### Adding Custom Affiliate Links

Edit `.env`:
```env
AFFILIATE_KEYWORDS=laptop,smartphone,headphones
AFFILIATE_LINKS={"amazon": "https://amazon.com/?tag=your-tag"}
```

### Customizing Blog Generation

Edit `services/blog_generator.py` to modify:
- Blog prompt templates
- Content structure
- Writing style
- Word count targets

### SEO Customization

Edit `services/seo_service.py` to customize:
- Meta tag generation
- Schema markup
- SEO scoring

## Troubleshooting

### Issue: No trending topics found

**Solution**: Google Trends may be rate-limiting. Wait a few minutes and try again, or use manual keywords.

### Issue: OpenAI API errors

**Solution**: Check your API key and account credits. Ensure you have access to the specified model.

### Issue: Database errors

**Solution**: Delete `blog_wire.db` and restart the app to recreate tables.

## License

MIT License - feel free to use for personal or commercial projects.

## Support

For issues and questions, please check the documentation or create an issue in the repository.

---

**Built with** Flask, OpenAI GPT, Google Trends, and modern web technologies.
