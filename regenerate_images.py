#!/usr/bin/env python3
"""
Script to regenerate images for existing blog posts that have expired or missing images.
This will use the new R2 storage system to create permanent image URLs.
"""

import os
import sys
import logging
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from config import Config
from models import db, BlogPost
from services.image_service import ImageService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app for database access
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def needs_new_image(post):
    """
    Check if a post needs a new image

    Returns True if:
    - No featured_image_url
    - Has placeholder URL
    - Has expired DALL-E URL (oaidalleapiprodscus.blob.core.windows.net)
    """
    if not post.featured_image_url:
        return True

    if 'placeholder' in post.featured_image_url.lower():
        return True

    if 'oaidalleapiprodscus.blob.core.windows.net' in post.featured_image_url:
        return True

    return False

def regenerate_images():
    """
    Regenerate images for all posts that need them
    """
    with app.app_context():
        # Initialize ImageService
        image_service = ImageService()

        if not image_service.r2_enabled:
            logger.error("❌ R2 storage is not enabled! Please configure R2 environment variables.")
            return

        logger.info("✅ R2 storage is enabled and ready")

        # Get all published posts
        posts = BlogPost.query.filter_by(status='published').order_by(BlogPost.published_at.desc()).all()

        logger.info(f"Found {len(posts)} published posts")

        # Find posts that need new images
        posts_to_update = [post for post in posts if needs_new_image(post)]

        logger.info(f"Found {len(posts_to_update)} posts that need new images")

        if not posts_to_update:
            logger.info("✅ All posts already have valid images!")
            return

        # Process each post
        for i, post in enumerate(posts_to_update, 1):
            logger.info(f"\n[{i}/{len(posts_to_update)}] Processing: {post.title}")
            logger.info(f"Current image URL: {post.featured_image_url or 'None'}")

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

                    logger.info(f"✅ Updated with new image: {new_image_url}")
                else:
                    logger.warning(f"⚠️ Failed to generate image for: {post.title}")

            except Exception as e:
                logger.error(f"❌ Error processing post {post.id}: {e}")
                db.session.rollback()
                continue

        logger.info(f"\n✅ Completed! Updated {len(posts_to_update)} posts with new images")

if __name__ == '__main__':
    logger.info("=" * 80)
    logger.info("Starting image regeneration process...")
    logger.info("=" * 80)

    regenerate_images()

    logger.info("=" * 80)
    logger.info("Image regeneration complete!")
    logger.info("=" * 80)
