import os
from dotenv import load_dotenv
import json

load_dotenv()


class Config:
    """Application configuration"""

    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Database
    # Fix for Railway's postgres:// URL (SQLAlchemy requires postgresql://)
    database_url = os.getenv('DATABASE_URL', 'sqlite:///blog_wire.db')
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # OpenAI
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview')

    # Blog settings
    BLOG_NAME = os.getenv('BLOG_NAME', 'Blog Wire')
    BLOG_DOMAIN = os.getenv('BLOG_DOMAIN', 'blog-wire.com')
    POSTS_PER_DAY = int(os.getenv('POSTS_PER_DAY', 1))
    MIN_WORD_COUNT = int(os.getenv('MIN_WORD_COUNT', 2000))
    MAX_WORD_COUNT = int(os.getenv('MAX_WORD_COUNT', 3500))

    # Google AdSense
    ADSENSE_CLIENT_ID = os.getenv('ADSENSE_CLIENT_ID', '')
    ADSENSE_ENABLED = os.getenv('ADSENSE_ENABLED', 'False').lower() == 'true'

    # Affiliate links
    AFFILIATE_KEYWORDS = os.getenv('AFFILIATE_KEYWORDS', 'amazon,product,buy,shop,review').split(',')
    AFFILIATE_LINKS = json.loads(os.getenv('AFFILIATE_LINKS', '{}'))

    # SEO & Google Search Console
    GOOGLE_SITE_VERIFICATION = os.getenv('GOOGLE_SITE_VERIFICATION', '')
    SITE_AUTHOR = os.getenv('SITE_AUTHOR', 'Ryan Pate')
    SITE_TWITTER = os.getenv('SITE_TWITTER', '')  # Twitter handle without @
