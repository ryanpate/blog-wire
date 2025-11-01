from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Text

db = SQLAlchemy()


class BlogPost(db.Model):
    """Blog post model"""
    __tablename__ = 'blog_posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False, index=True)
    content = db.Column(Text, nullable=False)
    excerpt = db.Column(Text)

    # SEO fields
    meta_description = db.Column(db.String(160))
    meta_keywords = db.Column(db.String(255))
    featured_image_url = db.Column(db.String(500))

    # Status
    status = db.Column(db.String(20), default='draft')  # draft, published, archived
    published_at = db.Column(db.DateTime)

    # Metrics
    view_count = db.Column(db.Integer, default=0)
    word_count = db.Column(db.Integer)

    # Relationships
    topic_id = db.Column(db.Integer, db.ForeignKey('trending_topics.id'))
    topic = db.relationship('TrendingTopic', back_populates='posts')

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<BlogPost {self.title}>'

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'excerpt': self.excerpt,
            'content': self.content,
            'meta_description': self.meta_description,
            'meta_keywords': self.meta_keywords,
            'status': self.status,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'view_count': self.view_count,
            'word_count': self.word_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class TrendingTopic(db.Model):
    """Trending topics from Google Trends"""
    __tablename__ = 'trending_topics'

    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(255), nullable=False)
    search_volume = db.Column(db.Integer)
    trend_score = db.Column(db.Float)
    category = db.Column(db.String(100))

    # Status
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed, skipped

    # Relationships
    posts = db.relationship('BlogPost', back_populates='topic', lazy='dynamic')

    # Timestamps
    discovered_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)

    def __repr__(self):
        return f'<TrendingTopic {self.keyword}>'


class AffiliateLink(db.Model):
    """Affiliate links to be injected into blog posts"""
    __tablename__ = 'affiliate_links'

    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    platform = db.Column(db.String(100))  # amazon, ebay, etc.
    active = db.Column(db.Boolean, default=True)

    # Metrics
    click_count = db.Column(db.Integer, default=0)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<AffiliateLink {self.keyword}>'
