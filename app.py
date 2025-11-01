from flask import Flask, render_template, jsonify, request, abort
from flask_migrate import Migrate
import logging
import markdown
import json
from datetime import datetime

from config import Config
from models import db, BlogPost, TrendingTopic, AffiliateLink
from services.automation_service import AutomationService
from services.seo_service import SEOService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)

# Initialize services
automation_service = AutomationService()
seo_service = SEOService()


# Create database tables
with app.app_context():
    db.create_all()


# ============================================================
# PUBLIC ROUTES - Blog Display
# ============================================================

@app.route('/')
def index():
    """Homepage - show recent blog posts"""
    page = request.args.get('page', 1, type=int)
    per_page = 10

    posts = BlogPost.query.filter_by(
        status='published'
    ).order_by(
        BlogPost.published_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    return render_template('index.html', posts=posts)


@app.route('/blog/<slug>')
def blog_post(slug):
    """Individual blog post page"""
    post = BlogPost.query.filter_by(slug=slug, status='published').first_or_404()

    # Increment view count
    post.view_count += 1
    db.session.commit()

    # Convert markdown to HTML
    html_content = markdown.markdown(
        post.content,
        extensions=['fenced_code', 'tables', 'nl2br']
    )

    # Generate schema markup for SEO
    schema_markup = seo_service.generate_schema_markup(post)

    return render_template(
        'blog_post.html',
        post=post,
        html_content=html_content,
        schema_markup=json.dumps(schema_markup)
    )


@app.route('/sitemap.xml')
def sitemap():
    """Generate XML sitemap for SEO"""
    posts = BlogPost.query.filter_by(status='published').all()

    sitemap_xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    sitemap_xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

    # Homepage
    sitemap_xml.append('<url>')
    sitemap_xml.append(f'  <loc>https://{Config.BLOG_DOMAIN}/</loc>')
    sitemap_xml.append('  <changefreq>daily</changefreq>')
    sitemap_xml.append('  <priority>1.0</priority>')
    sitemap_xml.append('</url>')

    # Blog posts
    for post in posts:
        sitemap_xml.append('<url>')
        sitemap_xml.append(f'  <loc>https://{Config.BLOG_DOMAIN}/blog/{post.slug}</loc>')
        if post.updated_at:
            sitemap_xml.append(f'  <lastmod>{post.updated_at.strftime("%Y-%m-%d")}</lastmod>')
        sitemap_xml.append('  <changefreq>monthly</changefreq>')
        sitemap_xml.append('  <priority>0.8</priority>')
        sitemap_xml.append('</url>')

    sitemap_xml.append('</urlset>')

    return '\n'.join(sitemap_xml), 200, {'Content-Type': 'application/xml'}


@app.route('/robots.txt')
def robots():
    """Robots.txt for SEO"""
    robots_txt = f"""User-agent: *
Allow: /
Sitemap: https://{Config.BLOG_DOMAIN}/sitemap.xml
"""
    return robots_txt, 200, {'Content-Type': 'text/plain'}


# ============================================================
# API ROUTES - Automation & Management
# ============================================================

@app.route('/api/generate-blog', methods=['POST'])
def api_generate_blog():
    """API endpoint to trigger blog generation"""
    data = request.get_json() or {}
    keyword = data.get('keyword')

    if keyword:
        # Generate single blog for specific keyword
        blog_post = automation_service.generate_single_blog(keyword)
        if blog_post:
            return jsonify({
                'success': True,
                'message': 'Blog post generated successfully',
                'post': blog_post.to_dict()
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to generate blog post'
            }), 500
    else:
        # Run daily automation workflow
        posts = automation_service.run_daily_blog_generation(
            count=Config.POSTS_PER_DAY
        )

        return jsonify({
            'success': True,
            'message': f'Generated {len(posts)} blog post(s)',
            'posts': [p.to_dict() for p in posts]
        })


@app.route('/api/stats')
def api_stats():
    """Get blog statistics"""
    stats = automation_service.get_blog_statistics()
    return jsonify(stats)


@app.route('/api/posts')
def api_posts():
    """Get all posts (for admin/management)"""
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return jsonify([p.to_dict() for p in posts])


@app.route('/api/trending-topics')
def api_trending_topics():
    """Get all trending topics"""
    topics = TrendingTopic.query.order_by(TrendingTopic.discovered_at.desc()).limit(50).all()
    return jsonify([{
        'id': t.id,
        'keyword': t.keyword,
        'trend_score': t.trend_score,
        'status': t.status,
        'discovered_at': t.discovered_at.isoformat() if t.discovered_at else None
    } for t in topics])


@app.route('/api/affiliate-links', methods=['GET', 'POST'])
def api_affiliate_links():
    """Manage affiliate links"""
    if request.method == 'POST':
        data = request.get_json()
        keyword = data.get('keyword')
        url = data.get('url')
        platform = data.get('platform')

        if not keyword or not url:
            return jsonify({'success': False, 'message': 'Keyword and URL required'}), 400

        aff_link = automation_service.affiliate_service.add_affiliate_link(
            keyword=keyword,
            url=url,
            platform=platform
        )

        if aff_link:
            return jsonify({'success': True, 'message': 'Affiliate link added'})
        else:
            return jsonify({'success': False, 'message': 'Failed to add affiliate link'}), 500

    else:
        # GET - return all affiliate links
        links = AffiliateLink.query.all()
        return jsonify([{
            'id': l.id,
            'keyword': l.keyword,
            'url': l.url,
            'platform': l.platform,
            'active': l.active,
            'click_count': l.click_count
        } for l in links])


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def api_delete_post(post_id):
    """Delete a blog post by ID"""
    post = BlogPost.query.get(post_id)

    if not post:
        return jsonify({'success': False, 'message': f'Post {post_id} not found'}), 404

    title = post.title
    db.session.delete(post)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Post "{title}" deleted successfully'
    })


@app.route('/api/posts/delete-empty', methods=['POST'])
def api_delete_empty_posts():
    """Delete all posts with 0 word count"""
    empty_posts = BlogPost.query.filter_by(word_count=0).all()

    if not empty_posts:
        return jsonify({'success': True, 'message': 'No empty posts found', 'deleted': 0})

    count = len(empty_posts)
    for post in empty_posts:
        db.session.delete(post)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Deleted {count} empty post(s)',
        'deleted': count
    })


# ============================================================
# TEMPLATE FILTERS
# ============================================================

@app.template_filter('format_date')
def format_date(date):
    """Format date for display"""
    if not date:
        return ''
    return date.strftime('%B %d, %Y')


@app.template_filter('reading_time')
def reading_time(word_count):
    """Calculate reading time based on word count"""
    # Average reading speed: 200 words per minute
    minutes = max(1, round(word_count / 200))
    return f"{minutes} min read"


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
