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
