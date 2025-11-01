# Blog Wire API Documentation

Complete API reference for the Blog Wire automated blogging platform.

## Base URL

```
http://localhost:5000
```

For production: `https://blog-wire.com`

---

## Public Routes

### GET /

**Description**: Homepage with paginated list of published blog posts

**Query Parameters**:
- `page` (integer, optional): Page number (default: 1)

**Response**: HTML page

---

### GET /blog/:slug

**Description**: Individual blog post page

**Parameters**:
- `slug` (string, required): URL slug of the blog post

**Response**: HTML page with full blog post content

**Example**:
```
GET /blog/introduction-to-artificial-intelligence
```

---

### GET /sitemap.xml

**Description**: XML sitemap for SEO (all published posts)

**Response**: XML sitemap

---

### GET /robots.txt

**Description**: Robots.txt file for search engine crawlers

**Response**: Plain text robots.txt

---

## API Routes

### POST /api/generate-blog

**Description**: Trigger blog post generation (manual or automated)

**Request Body** (optional):
```json
{
  "keyword": "artificial intelligence"
}
```

**Response** (with keyword):
```json
{
  "success": true,
  "message": "Blog post generated successfully",
  "post": {
    "id": 1,
    "title": "Understanding Artificial Intelligence in 2024",
    "slug": "understanding-artificial-intelligence-in-2024",
    "excerpt": "Artificial intelligence is transforming...",
    "content": "Full markdown content...",
    "meta_description": "A comprehensive guide to AI...",
    "meta_keywords": "AI, machine learning, technology",
    "status": "published",
    "published_at": "2024-01-15T10:30:00",
    "view_count": 0,
    "word_count": 2547,
    "created_at": "2024-01-15T10:30:00"
  }
}
```

**Response** (without keyword - uses trending topics):
```json
{
  "success": true,
  "message": "Generated 1 blog post(s)",
  "posts": [
    {
      "id": 1,
      "title": "...",
      ...
    }
  ]
}
```

**Error Response**:
```json
{
  "success": false,
  "message": "Failed to generate blog post"
}
```

**Example**:
```bash
# Generate from trending topics
curl -X POST http://localhost:5000/api/generate-blog

# Generate for specific keyword
curl -X POST http://localhost:5000/api/generate-blog \
  -H "Content-Type: application/json" \
  -d '{"keyword": "blockchain technology"}'
```

---

### GET /api/stats

**Description**: Get blog platform statistics

**Response**:
```json
{
  "total_posts": 45,
  "published_posts": 42,
  "draft_posts": 3,
  "total_views": 12450,
  "total_topics": 58,
  "pending_topics": 12,
  "completed_topics": 46
}
```

**Example**:
```bash
curl http://localhost:5000/api/stats
```

---

### GET /api/posts

**Description**: Get all blog posts (for admin/management)

**Response**:
```json
[
  {
    "id": 1,
    "title": "Understanding AI",
    "slug": "understanding-ai",
    "excerpt": "AI is transforming...",
    "content": "Full markdown content...",
    "meta_description": "A guide to AI...",
    "meta_keywords": "AI, technology",
    "status": "published",
    "published_at": "2024-01-15T10:30:00",
    "view_count": 234,
    "word_count": 2547,
    "created_at": "2024-01-15T10:30:00"
  },
  ...
]
```

**Example**:
```bash
curl http://localhost:5000/api/posts
```

---

### GET /api/trending-topics

**Description**: Get all discovered trending topics

**Response**:
```json
[
  {
    "id": 1,
    "keyword": "artificial intelligence",
    "trend_score": 85.5,
    "status": "completed",
    "discovered_at": "2024-01-15T08:00:00"
  },
  {
    "id": 2,
    "keyword": "climate change",
    "trend_score": 72.3,
    "status": "pending",
    "discovered_at": "2024-01-15T08:00:00"
  },
  ...
]
```

**Status values**:
- `pending`: Topic discovered but not processed
- `in_progress`: Blog generation in progress
- `completed`: Blog successfully generated
- `skipped`: Topic skipped due to error

**Example**:
```bash
curl http://localhost:5000/api/trending-topics
```

---

### GET /api/affiliate-links

**Description**: Get all affiliate links

**Response**:
```json
[
  {
    "id": 1,
    "keyword": "laptop",
    "url": "https://amazon.com/dp/PRODUCT?tag=your-tag",
    "platform": "amazon",
    "active": true,
    "click_count": 45
  },
  ...
]
```

**Example**:
```bash
curl http://localhost:5000/api/affiliate-links
```

---

### POST /api/affiliate-links

**Description**: Add a new affiliate link

**Request Body**:
```json
{
  "keyword": "smartphone",
  "url": "https://amazon.com/dp/PRODUCT?tag=your-tag",
  "platform": "amazon"
}
```

**Parameters**:
- `keyword` (string, required): Keyword to match in blog content
- `url` (string, required): Affiliate URL
- `platform` (string, optional): Platform name (e.g., "amazon", "ebay")

**Response**:
```json
{
  "success": true,
  "message": "Affiliate link added"
}
```

**Error Response**:
```json
{
  "success": false,
  "message": "Keyword and URL required"
}
```

**Example**:
```bash
curl -X POST http://localhost:5000/api/affiliate-links \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "headphones",
    "url": "https://amazon.com/dp/PRODUCT?tag=your-tag",
    "platform": "amazon"
  }'
```

---

## Data Models

### BlogPost

```json
{
  "id": 1,
  "title": "Blog Post Title",
  "slug": "blog-post-title",
  "content": "Full markdown content...",
  "excerpt": "Short excerpt...",
  "meta_description": "SEO meta description",
  "meta_keywords": "keyword1, keyword2, keyword3",
  "featured_image_url": "https://...",
  "status": "published",
  "published_at": "2024-01-15T10:30:00",
  "view_count": 0,
  "word_count": 2547,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

### TrendingTopic

```json
{
  "id": 1,
  "keyword": "artificial intelligence",
  "search_volume": 8500,
  "trend_score": 85.5,
  "category": "technology",
  "status": "completed",
  "discovered_at": "2024-01-15T08:00:00",
  "processed_at": "2024-01-15T10:30:00"
}
```

### AffiliateLink

```json
{
  "id": 1,
  "keyword": "laptop",
  "url": "https://amazon.com/dp/PRODUCT?tag=your-tag",
  "platform": "amazon",
  "active": true,
  "click_count": 45,
  "created_at": "2024-01-10T12:00:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

---

## Automation Workflow

The automated daily blog generation follows this workflow:

1. **Fetch Trending Topics**
   - Connects to Google Trends API
   - Retrieves trending searches
   - Saves to database with status "pending"

2. **Generate Blog Content**
   - Gets next pending topic
   - Calls OpenAI API with optimized prompt
   - Generates 2000-3500 word blog post
   - Includes SEO metadata

3. **Inject Affiliate Links**
   - Scans content for matching keywords
   - Injects affiliate links (max 3 per post)
   - Tracks link usage

4. **Publish Post**
   - Saves to database with status "published"
   - Marks topic as "completed"
   - Updates sitemap

5. **Repeat**
   - Runs daily at scheduled time (default: 8:00 AM)
   - Generates configured number of posts

---

## Rate Limits

- **Google Trends**: ~1 request per second (built-in delays)
- **OpenAI API**: Based on your API tier
  - Free tier: 3 requests/min
  - Pay-as-you-go: 3,500 requests/min (GPT-4)

---

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request (missing parameters) |
| 404 | Not Found (blog post or resource not found) |
| 500 | Internal Server Error |

---

## Best Practices

1. **API Key Security**: Never commit API keys to version control
2. **Rate Limiting**: Respect API rate limits (built-in delays included)
3. **Monitoring**: Check `scheduler.log` for automation status
4. **Backups**: Regularly backup `blog_wire.db` database
5. **Testing**: Test affiliate links before adding to production

---

## Support

For issues or questions, please refer to the main README.md or create an issue in the repository.
