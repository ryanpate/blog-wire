from trendspy import Trends
import time
from datetime import datetime
from models import TrendingTopic, db
import logging

logger = logging.getLogger(__name__)


class TrendsService:
    """Service to fetch trending topics from Google Trends using trendspy"""

    def __init__(self):
        self.trends = Trends()

    def get_trending_topics(self, count=10, region='US'):
        """
        Fetch trending topics from Google Trends using trendspy

        Args:
            count: Number of trending topics to retrieve
            region: Geographic region for trends (e.g., 'US', 'GB', 'CA')

        Returns:
            list: List of trending topic dictionaries
        """
        try:
            # Get trending searches using trendspy
            logger.info(f"Fetching trending topics from Google Trends (region={region})...")
            trending = self.trends.trending_now(geo=region)

            if not trending:
                logger.warning("No trending topics found")
                return []

            topics = []
            # Limit to requested count
            for trend in trending[:count]:
                # trendspy provides volume directly
                keyword = trend.keyword
                volume = trend.volume if hasattr(trend, 'volume') else 0

                # Calculate trend score (normalized 0-100)
                trend_score = min(100, (volume / 10000)) if volume else 0

                topics.append({
                    'keyword': keyword,
                    'trend_score': trend_score,
                    'search_volume': volume
                })

                logger.debug(f"Found trending topic: {keyword} (volume: {volume:,})")

            logger.info(f"Successfully fetched {len(topics)} trending topics")
            return topics

        except Exception as e:
            logger.error(f"Error fetching trending topics with trendspy: {e}")
            return []

    def save_trending_topics(self, topics):
        """
        Save trending topics to database

        Args:
            topics: List of topic dictionaries

        Returns:
            list: List of TrendingTopic model instances
        """
        saved_topics = []

        for topic_data in topics:
            # Check if topic already exists and is pending/in_progress
            existing = TrendingTopic.query.filter_by(
                keyword=topic_data['keyword']
            ).first()

            if existing and existing.status in ['pending', 'in_progress']:
                # Skip if already being processed
                continue

            # Create new trending topic
            topic = TrendingTopic(
                keyword=topic_data['keyword'],
                search_volume=topic_data.get('search_volume', 0),
                trend_score=topic_data.get('trend_score', 0),
                status='pending'
            )

            db.session.add(topic)
            saved_topics.append(topic)

        try:
            db.session.commit()
            logger.info(f"Saved {len(saved_topics)} new trending topics")
            return saved_topics
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error saving trending topics: {e}")
            return []

    def get_next_pending_topic(self):
        """
        Get the next pending topic to process

        Returns:
            TrendingTopic: Next pending topic or None
        """
        return TrendingTopic.query.filter_by(
            status='pending'
        ).order_by(
            TrendingTopic.trend_score.desc()
        ).first()

    def mark_topic_processed(self, topic_id, status='completed'):
        """
        Mark a topic as processed

        Args:
            topic_id: Topic ID
            status: New status (completed or skipped)
        """
        topic = TrendingTopic.query.get(topic_id)
        if topic:
            topic.status = status
            topic.processed_at = datetime.utcnow()
            db.session.commit()
