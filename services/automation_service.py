import logging
from datetime import datetime
from services.trends_service import TrendsService
from services.blog_generator import BlogGenerator
from services.affiliate_service import AffiliateService
from models import db, BlogPost

logger = logging.getLogger(__name__)


class AutomationService:
    """Main automation service that orchestrates the blog generation workflow"""

    def __init__(self):
        self.trends_service = TrendsService()
        self.blog_generator = BlogGenerator()
        self.affiliate_service = AffiliateService()

    def run_daily_blog_generation(self, count=1):
        """
        Main automated workflow to generate and publish blogs

        Args:
            count: Number of blogs to generate

        Returns:
            list: Generated blog posts
        """
        logger.info(f"Starting daily blog generation workflow (count={count})")

        generated_posts = []

        try:
            # Step 1: Fetch trending topics
            logger.info("Fetching trending topics from Google Trends...")
            trending_topics = self.trends_service.get_trending_topics(count=count * 2)

            if not trending_topics:
                logger.warning("No trending topics found. Using fallback custom topics.")
                return self._generate_from_custom_topics(count)

            # Step 2: Save trending topics to database
            saved_topics = self.trends_service.save_trending_topics(trending_topics)

            # Step 3: Generate blog posts for each topic
            for i in range(count):
                # Get next pending topic
                topic = self.trends_service.get_next_pending_topic()

                if not topic:
                    logger.warning(f"No more pending topics. Generated {i} of {count} posts.")
                    break

                logger.info(f"Processing topic: {topic.keyword}")

                # Mark topic as in progress
                topic.status = 'in_progress'
                db.session.commit()

                # Generate blog post
                blog_data = self.blog_generator.generate_blog_post(
                    topic=topic,
                    min_words=2000,
                    max_words=3500
                )

                if not blog_data:
                    logger.error(f"Failed to generate blog for '{topic.keyword}'")
                    self.trends_service.mark_topic_processed(topic.id, status='skipped')
                    continue

                # Inject affiliate links
                blog_data['content'] = self.affiliate_service.inject_affiliate_links(
                    blog_data['content'],
                    max_links=3
                )

                # Save blog post
                blog_post = self.blog_generator.save_blog_post(
                    blog_data=blog_data,
                    topic_id=topic.id,
                    status='published'
                )

                if blog_post:
                    generated_posts.append(blog_post)
                    self.trends_service.mark_topic_processed(topic.id, status='completed')
                    logger.info(f"Successfully published blog: {blog_post.title}")
                else:
                    logger.error(f"Failed to save blog for '{topic.keyword}'")
                    self.trends_service.mark_topic_processed(topic.id, status='skipped')

            logger.info(f"Daily blog generation completed. Generated {len(generated_posts)} posts.")
            return generated_posts

        except Exception as e:
            logger.error(f"Error in daily blog generation workflow: {e}")
            return generated_posts

    def generate_single_blog(self, keyword):
        """
        Generate a single blog post for a specific keyword

        Args:
            keyword: Topic keyword

        Returns:
            BlogPost: Generated blog post or None
        """
        try:
            logger.info(f"Generating single blog for keyword: {keyword}")

            # Generate blog post
            blog_data = self.blog_generator.generate_blog_post(
                topic=keyword,
                min_words=2000,
                max_words=3500
            )

            if not blog_data:
                logger.error(f"Failed to generate blog for '{keyword}'")
                return None

            # Inject affiliate links
            blog_data['content'] = self.affiliate_service.inject_affiliate_links(
                blog_data['content'],
                max_links=3
            )

            # Save blog post
            blog_post = self.blog_generator.save_blog_post(
                blog_data=blog_data,
                status='published'
            )

            if blog_post:
                logger.info(f"Successfully published blog: {blog_post.title}")
                return blog_post
            else:
                logger.error(f"Failed to save blog for '{keyword}'")
                return None

        except Exception as e:
            logger.error(f"Error generating single blog: {e}")
            return None

    def _generate_from_custom_topics(self, count=1):
        """
        Fallback method to generate blogs from custom topics file

        Args:
            count: Number of blogs to generate

        Returns:
            list: Generated blog posts
        """
        import os
        import random

        generated_posts = []

        try:
            topics_file = 'custom_topics.txt'
            if not os.path.exists(topics_file):
                logger.error("custom_topics.txt not found. Cannot generate blogs.")
                return generated_posts

            # Read topics from file
            with open(topics_file, 'r') as f:
                topics = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]

            if not topics:
                logger.error("No topics found in custom_topics.txt")
                return generated_posts

            # Randomly select topics
            selected_topics = random.sample(topics, min(count, len(topics)))
            logger.info(f"Selected {len(selected_topics)} custom topics for generation")

            # Generate blogs for selected topics
            for topic in selected_topics:
                logger.info(f"Generating blog for custom topic: {topic}")
                blog_post = self.generate_single_blog(topic)

                if blog_post:
                    generated_posts.append(blog_post)
                    logger.info(f"Successfully generated blog: {blog_post.title}")
                else:
                    logger.error(f"Failed to generate blog for custom topic: {topic}")

            return generated_posts

        except Exception as e:
            logger.error(f"Error in custom topics fallback: {e}")
            return generated_posts

    def get_blog_statistics(self):
        """
        Get statistics about blog generation

        Returns:
            dict: Statistics
        """
        from models import TrendingTopic

        total_posts = BlogPost.query.count()
        published_posts = BlogPost.query.filter_by(status='published').count()
        draft_posts = BlogPost.query.filter_by(status='draft').count()
        total_views = db.session.query(db.func.sum(BlogPost.view_count)).scalar() or 0

        total_topics = TrendingTopic.query.count()
        pending_topics = TrendingTopic.query.filter_by(status='pending').count()
        completed_topics = TrendingTopic.query.filter_by(status='completed').count()

        return {
            'total_posts': total_posts,
            'published_posts': published_posts,
            'draft_posts': draft_posts,
            'total_views': total_views,
            'total_topics': total_topics,
            'pending_topics': pending_topics,
            'completed_topics': completed_topics
        }
