from pytrends.request import TrendReq
import time
from datetime import datetime
from models import TrendingTopic, db
import logging

logger = logging.getLogger(__name__)


class TrendsService:
    """Service to fetch trending topics from Google Trends"""

    def __init__(self):
        self.pytrends = TrendReq(hl='en-US', tz=360)

    def get_trending_topics(self, count=10, region='united_states'):
        """
        Fetch trending topics from Google Trends

        Args:
            count: Number of trending topics to retrieve
            region: Geographic region for trends

        Returns:
            list: List of trending topic dictionaries
        """
        try:
            # Get trending searches
            trending_df = self.pytrends.trending_searches(pn=region)

            if trending_df.empty:
                logger.warning("No trending topics found")
                return []

            topics = []
            trending_searches = trending_df[0].head(count).tolist()

            for keyword in trending_searches:
                # Get interest over time for relative popularity score
                try:
                    self.pytrends.build_payload([keyword], timeframe='now 7-d')
                    interest_df = self.pytrends.interest_over_time()

                    trend_score = 0
                    if not interest_df.empty and keyword in interest_df.columns:
                        trend_score = float(interest_df[keyword].mean())

                    topics.append({
                        'keyword': keyword,
                        'trend_score': trend_score,
                        'search_volume': int(trend_score * 100)  # Approximation
                    })

                    # Rate limiting
                    time.sleep(1)

                except Exception as e:
                    logger.error(f"Error fetching details for '{keyword}': {e}")
                    topics.append({
                        'keyword': keyword,
                        'trend_score': 0,
                        'search_volume': 0
                    })

            return topics

        except Exception as e:
            logger.error(f"Error fetching trending topics: {e}")
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
