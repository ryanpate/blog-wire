#!/usr/bin/env python3
"""
Script to remove featured_image_url from older blog posts (before today)
so they show a gradient instead of broken image links.
"""

import os
import sys
from datetime import datetime, date

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from config import Config
from models import db, BlogPost
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app for database access
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def remove_old_images():
    """
    Remove featured_image_url from posts before today
    """
    with app.app_context():
        # Get today's date
        today = date.today()

        logger.info(f"Today's date: {today}")

        # Get all published posts
        all_posts = BlogPost.query.filter_by(status='published').all()
        logger.info(f"Found {len(all_posts)} published posts total")

        # Find posts from before today that have images
        posts_to_update = []
        for post in all_posts:
            if post.published_at:
                post_date = post.published_at.date()
                if post_date < today and post.featured_image_url:
                    posts_to_update.append(post)

        logger.info(f"Found {len(posts_to_update)} posts from before today with images")

        if not posts_to_update:
            logger.info("✅ No old posts with images to update!")
            return

        # Remove images from old posts
        updated_count = 0
        for post in posts_to_update:
            logger.info(f"Removing image from: {post.title} (published: {post.published_at.date()})")
            post.featured_image_url = None
            updated_count += 1

        db.session.commit()

        logger.info(f"✅ Completed! Removed images from {updated_count} posts")

if __name__ == '__main__':
    logger.info("=" * 80)
    logger.info("Starting removal of old post images...")
    logger.info("=" * 80)

    remove_old_images()

    logger.info("=" * 80)
    logger.info("Image removal complete!")
    logger.info("=" * 80)
