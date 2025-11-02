"""
Scheduler for automated daily blog post generation

Run this script to start the automation:
    python scheduler.py
"""

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
from datetime import datetime

from app import app, automation_service
from config import Config
from models import db, BlogPost
import json
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def daily_blog_generation_job():
    """Job that runs daily to generate blog posts"""
    logger.info("=" * 60)
    logger.info("Starting scheduled blog generation job")
    logger.info(f"Time: {datetime.now().isoformat()}")
    logger.info("=" * 60)

    try:
        with app.app_context():
            # Run the daily blog generation
            posts = automation_service.run_daily_blog_generation(
                count=Config.POSTS_PER_DAY
            )

            logger.info(f"Job completed successfully. Generated {len(posts)} post(s).")

            # Log post details
            for post in posts:
                logger.info(f"  - {post.title} ({post.slug})")

    except Exception as e:
        logger.error(f"Error in scheduled job: {e}", exc_info=True)

    logger.info("=" * 60)


def main():
    """Main function to start the scheduler"""
    logger.info("Blog Wire Automation Scheduler Starting...")

    # Auto-import blog posts on startup if database is empty
    # This ensures posts are restored after Railway deployments
    with app.app_context():
        if BlogPost.query.count() == 0:
            logger.info("Database is empty. Auto-importing blog posts from export file...")
            try:
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

    logger.info(f"Configuration:")
    logger.info(f"  - Posts per day: {Config.POSTS_PER_DAY}")
    logger.info(f"  - Blog domain: {Config.BLOG_DOMAIN}")
    logger.info(f"  - OpenAI model: {Config.OPENAI_MODEL}")

    # Create scheduler
    scheduler = BlockingScheduler()

    # Schedule daily job at 8:00 AM
    scheduler.add_job(
        daily_blog_generation_job,
        trigger=CronTrigger(hour=8, minute=0),
        id='daily_blog_generation',
        name='Generate daily blog posts',
        replace_existing=True
    )

    logger.info("Scheduled jobs:")
    for job in scheduler.get_jobs():
        logger.info(f"  - {job.name}")

    # Optional: Run once immediately on startup
    logger.info("\nRunning initial blog generation...")
    daily_blog_generation_job()

    # Start scheduler
    logger.info("\nScheduler is running. Press Ctrl+C to exit.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped.")


if __name__ == '__main__':
    main()
