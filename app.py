from flask import Flask, render_template, jsonify, request, abort, redirect
from flask_migrate import Migrate
import logging
import markdown
import json
from datetime import datetime

from config import Config
from models import db, BlogPost, TrendingTopic, AffiliateLink
from services.automation_service import AutomationService
from services.seo_service import SEOService
from services.image_service import ImageService

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

# Add basic cache headers for static files
@app.after_request
def add_header(response):
    # Cache static assets for 1 year
    if request.path.startswith('/static/'):
        response.cache_control.max_age = 31536000
        response.cache_control.public = True
    return response

# Initialize services
automation_service = AutomationService()
seo_service = SEOService()


# Create database tables and auto-import posts if database is empty
with app.app_context():
    db.create_all()

    # Auto-import blog posts on startup if database is empty
    # This ensures posts are restored after Railway deployments
    if BlogPost.query.count() == 0:
        logger.info("Database is empty. Auto-importing blog posts from export file...")
        try:
            import os
            export_file = 'blog_posts_export.json'

            if os.path.exists(export_file):
                with open(export_file, 'r') as f:
                    posts_data = json.load(f)

                imported_count = 0
                for post_data in posts_data:
                    post = BlogPost(
                        title=post_data['title'],
                        slug=post_data['slug'],
                        content=post_data['content'],
                        excerpt=post_data['excerpt'],
                        meta_description=post_data['meta_description'],
                        meta_keywords=post_data['meta_keywords'],
                        featured_image_url=post_data.get('featured_image_url'),
                        word_count=post_data['word_count'],
                        status=post_data['status'],
                        published_at=datetime.fromisoformat(post_data['published_at']) if post_data['published_at'] else None
                    )
                    db.session.add(post)
                    imported_count += 1

                db.session.commit()
                logger.info(f"✅ Auto-imported {imported_count} blog posts successfully")
            else:
                logger.warning(f"Export file {export_file} not found. Skipping auto-import.")
        except Exception as e:
            logger.error(f"Error during auto-import: {e}")
            db.session.rollback()


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

    # Generate website schema for homepage
    website_schema = seo_service.generate_website_schema()

    return render_template(
        'index.html',
        posts=posts,
        website_schema=json.dumps(website_schema)
    )


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

    # Get related posts based on shared keywords
    related_posts = []
    if post.meta_keywords:
        keywords = [k.strip().lower() for k in post.meta_keywords.split(',')[:3]]
        # Find posts with similar keywords
        for keyword in keywords:
            related = BlogPost.query.filter(
                BlogPost.id != post.id,
                BlogPost.status == 'published',
                BlogPost.meta_keywords.ilike(f'%{keyword}%')
            ).order_by(BlogPost.published_at.desc()).limit(3).all()
            related_posts.extend(related)

        # Remove duplicates and limit to 3
        seen_ids = set()
        unique_related = []
        for p in related_posts:
            if p.id not in seen_ids:
                seen_ids.add(p.id)
                unique_related.append(p)
                if len(unique_related) >= 3:
                    break
        related_posts = unique_related

    # If no related posts found, get recent posts
    if not related_posts:
        related_posts = BlogPost.query.filter(
            BlogPost.id != post.id,
            BlogPost.status == 'published'
        ).order_by(BlogPost.published_at.desc()).limit(3).all()

    # Generate schema markup for SEO
    article_schema = seo_service.generate_schema_markup(post)
    breadcrumb_schema = seo_service.generate_breadcrumb_schema(post)
    faq_schema = seo_service.generate_faq_schema(post)

    # Combine schemas into a graph
    schema_graph = [article_schema, breadcrumb_schema]
    if faq_schema:
        schema_graph.append(faq_schema)

    schema_markup = {
        "@context": "https://schema.org",
        "@graph": schema_graph
    }

    return render_template(
        'blog_post.html',
        post=post,
        html_content=html_content,
        schema_markup=json.dumps(schema_markup),
        related_posts=related_posts
    )


@app.route('/sitemap.xml')
def sitemap():
    """Generate XML sitemap for SEO"""
    posts = BlogPost.query.filter_by(status='published').all()

    sitemap_xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    sitemap_xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

    # Homepage - use the most recent post date as lastmod
    sitemap_xml.append('<url>')
    sitemap_xml.append(f'  <loc>https://{Config.BLOG_DOMAIN}/</loc>')
    if posts:
        latest_post = max(posts, key=lambda p: p.updated_at or p.published_at or datetime.min)
        latest_date = latest_post.updated_at or latest_post.published_at
        if latest_date:
            sitemap_xml.append(f'  <lastmod>{latest_date.strftime("%Y-%m-%d")}</lastmod>')
    sitemap_xml.append('  <changefreq>daily</changefreq>')
    sitemap_xml.append('  <priority>1.0</priority>')
    sitemap_xml.append('</url>')

    # Privacy Policy
    sitemap_xml.append('<url>')
    sitemap_xml.append(f'  <loc>https://{Config.BLOG_DOMAIN}/privacy-policy</loc>')
    sitemap_xml.append('  <changefreq>monthly</changefreq>')
    sitemap_xml.append('  <priority>0.3</priority>')
    sitemap_xml.append('</url>')

    # Terms of Service
    sitemap_xml.append('<url>')
    sitemap_xml.append(f'  <loc>https://{Config.BLOG_DOMAIN}/terms</loc>')
    sitemap_xml.append('  <changefreq>monthly</changefreq>')
    sitemap_xml.append('  <priority>0.3</priority>')
    sitemap_xml.append('</url>')

    # About Us
    sitemap_xml.append('<url>')
    sitemap_xml.append(f'  <loc>https://{Config.BLOG_DOMAIN}/about</loc>')
    sitemap_xml.append('  <changefreq>monthly</changefreq>')
    sitemap_xml.append('  <priority>0.5</priority>')
    sitemap_xml.append('</url>')

    # Contact
    sitemap_xml.append('<url>')
    sitemap_xml.append(f'  <loc>https://{Config.BLOG_DOMAIN}/contact</loc>')
    sitemap_xml.append('  <changefreq>monthly</changefreq>')
    sitemap_xml.append('  <priority>0.5</priority>')
    sitemap_xml.append('</url>')

    # Blog posts
    for post in posts:
        sitemap_xml.append('<url>')
        sitemap_xml.append(f'  <loc>https://{Config.BLOG_DOMAIN}/blog/{post.slug}</loc>')
        # Use updated_at if available, otherwise published_at
        lastmod = post.updated_at or post.published_at
        if lastmod:
            sitemap_xml.append(f'  <lastmod>{lastmod.strftime("%Y-%m-%d")}</lastmod>')
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


@app.route('/ads.txt')
def ads_txt():
    """Ads.txt - redirect to Ezoic ads.txt manager for automatic updates"""
    return redirect(f'https://srv.adstxtmanager.com/19390/{Config.BLOG_DOMAIN}', code=301)


@app.route('/privacy-policy')
def privacy_policy():
    """Privacy Policy page for ad compliance"""
    return render_template('privacy_policy.html')


@app.route('/terms')
def terms():
    """Terms of Service page"""
    return render_template('terms.html')


@app.route('/about')
def about():
    """About Us page"""
    return render_template('about.html')


@app.route('/contact')
def contact():
    """Contact page"""
    return render_template('contact.html')


@app.route('/google<verification_code>.html')
def google_verification(verification_code):
    """Google Search Console HTML file verification"""
    return f'google-site-verification: google{verification_code}.html', 200, {'Content-Type': 'text/html'}


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


@app.route('/api/posts/delete-all', methods=['POST'])
def api_delete_all_posts():
    """Delete all blog posts (use with caution!)"""
    all_posts = BlogPost.query.all()

    if not all_posts:
        return jsonify({'success': True, 'message': 'No posts found', 'deleted': 0})

    count = len(all_posts)
    for post in all_posts:
        db.session.delete(post)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Deleted all {count} post(s)',
        'deleted': count
    })


@app.route('/api/migrate-schema', methods=['POST'])
def api_migrate_schema():
    """Run database schema migration for PostgreSQL"""
    from sqlalchemy import text

    try:
        # Alter the columns to increase length
        db.session.execute(text('ALTER TABLE blog_posts ALTER COLUMN meta_description TYPE VARCHAR(500)'))
        db.session.execute(text('ALTER TABLE blog_posts ALTER COLUMN meta_keywords TYPE VARCHAR(500)'))
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Database schema updated successfully'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Schema migration failed: {str(e)}'
        }), 500


@app.route('/api/posts/regenerate-images', methods=['POST'])
def api_regenerate_images():
    """Regenerate images for existing blog posts"""
    try:
        # Initialize ImageService
        image_service = ImageService()

        if not image_service.r2_enabled:
            return jsonify({
                'success': False,
                'message': 'R2 storage is not enabled! Please configure R2 environment variables.'
            }), 500

        # Get all published posts
        posts = BlogPost.query.filter_by(status='published').order_by(BlogPost.published_at.desc()).all()

        logger.info(f"Found {len(posts)} published posts")

        # Find posts that need new images
        def needs_new_image(post):
            if not post.featured_image_url:
                return True
            if 'placeholder' in post.featured_image_url.lower():
                return True
            if 'oaidalleapiprodscus.blob.core.windows.net' in post.featured_image_url:
                return True
            return False

        posts_to_update = [post for post in posts if needs_new_image(post)]

        logger.info(f"Found {len(posts_to_update)} posts that need new images")

        if not posts_to_update:
            return jsonify({
                'success': True,
                'message': 'All posts already have valid images!',
                'updated': 0
            })

        updated_count = 0
        failed_count = 0

        # Process each post
        for i, post in enumerate(posts_to_update, 1):
            logger.info(f"[{i}/{len(posts_to_update)}] Processing: {post.title}")

            try:
                # Generate new image
                new_image_url = image_service.get_featured_image(
                    title=post.title,
                    keywords=post.meta_keywords
                )

                if new_image_url:
                    # Update the post
                    post.featured_image_url = new_image_url
                    db.session.commit()
                    updated_count += 1
                    logger.info(f"✅ Updated with new image: {new_image_url}")
                else:
                    failed_count += 1
                    logger.warning(f"⚠️ Failed to generate image for: {post.title}")

            except Exception as e:
                failed_count += 1
                logger.error(f"❌ Error processing post {post.id}: {e}")
                db.session.rollback()
                continue

        return jsonify({
            'success': True,
            'message': f'Image regeneration completed',
            'updated': updated_count,
            'failed': failed_count,
            'total_checked': len(posts_to_update)
        })

    except Exception as e:
        logger.error(f"Error in image regeneration: {e}")
        return jsonify({
            'success': False,
            'message': f'Image regeneration failed: {str(e)}'
        }), 500


@app.route('/api/posts/remove-old-images', methods=['POST'])
def api_remove_old_images():
    """Remove images from posts older than today"""
    from datetime import date

    try:
        # Get today's date
        today = date.today()

        logger.info(f"Removing images from posts before: {today}")

        # Get all published posts
        all_posts = BlogPost.query.filter_by(status='published').all()

        # Find posts from before today that have images
        posts_to_update = []
        for post in all_posts:
            if post.published_at:
                post_date = post.published_at.date()
                if post_date < today and post.featured_image_url:
                    posts_to_update.append(post)

        logger.info(f"Found {len(posts_to_update)} posts to update")

        if not posts_to_update:
            return jsonify({
                'success': True,
                'message': 'No old posts with images to update',
                'updated': 0
            })

        # Remove images from old posts
        updated_count = 0
        for post in posts_to_update:
            logger.info(f"Removing image from: {post.title}")
            post.featured_image_url = None
            updated_count += 1

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Removed images from {updated_count} old posts',
            'updated': updated_count
        })

    except Exception as e:
        logger.error(f"Error removing old images: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


@app.route('/api/posts/import', methods=['POST'])
def api_import_posts():
    """Import blog posts from JSON file"""
    try:
        with open('blog_posts_export.json', 'r') as f:
            posts_data = json.load(f)

        imported_count = 0
        skipped_count = 0

        for post_data in posts_data:
            # Check if post with this slug already exists
            existing = BlogPost.query.filter_by(slug=post_data['slug']).first()

            if existing:
                skipped_count += 1
                continue

            # Create new post
            post = BlogPost(
                title=post_data['title'],
                slug=post_data['slug'],
                content=post_data['content'],
                excerpt=post_data['excerpt'],
                meta_description=post_data['meta_description'],
                meta_keywords=post_data['meta_keywords'],
                featured_image_url=post_data.get('featured_image_url'),
                word_count=post_data['word_count'],
                status=post_data['status'],
                published_at=datetime.fromisoformat(post_data['published_at']) if post_data['published_at'] else None
            )

            db.session.add(post)
            imported_count += 1

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Imported {imported_count} posts, skipped {skipped_count} existing',
            'imported': imported_count,
            'skipped': skipped_count
        })

    except FileNotFoundError:
        return jsonify({
            'success': False,
            'message': 'blog_posts_export.json not found'
        }), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error importing posts: {str(e)}'
        }), 500


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
