import openai
from openai import OpenAI
import re
from datetime import datetime
import logging
from models import BlogPost, db
from config import Config

logger = logging.getLogger(__name__)


class BlogGenerator:
    """Service to generate blog posts using OpenAI API"""

    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.OPENAI_MODEL

    def generate_blog_post(self, topic, min_words=2000, max_words=3500):
        """
        Generate a complete blog post for a given topic

        Args:
            topic: Topic keyword or TrendingTopic instance
            min_words: Minimum word count
            max_words: Maximum word count

        Returns:
            dict: Blog post data including title, content, meta info
        """
        keyword = topic if isinstance(topic, str) else topic.keyword

        try:
            # Generate blog post using GPT
            prompt = self._create_blog_prompt(keyword, min_words, max_words)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert blog writer who creates engaging, SEO-optimized, long-form content in a conversational and friendly tone. Your blogs are well-researched, informative, and easy to read."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=4096
            )

            content = response.choices[0].message.content

            # Parse the structured response
            blog_data = self._parse_blog_content(content, keyword)

            return blog_data

        except Exception as e:
            logger.error(f"Error generating blog post for '{keyword}': {e}")
            return None

    def _create_blog_prompt(self, keyword, min_words, max_words):
        """Create the prompt for blog generation"""
        return f"""Write a comprehensive, SEO-optimized blog post about: "{keyword}"

Requirements:
- Word count: {min_words}-{max_words} words
- Tone: Conversational, friendly, and engaging
- Style: Long-form, informative, well-structured
- Include relevant headers (H2, H3) for better readability
- Naturally incorporate the keyword throughout
- Add value with actionable insights and examples
- Write in a way that keeps readers engaged

Structure your response EXACTLY as follows:

TITLE: [Compelling, SEO-friendly title]

META_DESCRIPTION: [150-160 character meta description]

META_KEYWORDS: [5-7 relevant keywords, comma-separated]

EXCERPT: [2-3 sentence excerpt/summary]

CONTENT:
[Full blog post content in Markdown format with headers, lists, and formatting]

Remember: Write naturally and conversationally as if explaining to a friend. Make it engaging and valuable!"""

    def _parse_blog_content(self, content, keyword):
        """Parse the structured blog content from GPT response"""
        data = {
            'keyword': keyword,
            'title': '',
            'content': '',
            'meta_description': '',
            'meta_keywords': '',
            'excerpt': '',
            'word_count': 0
        }

        # Extract title
        title_match = re.search(r'TITLE:\s*(.+?)(?:\n|$)', content)
        if title_match:
            data['title'] = title_match.group(1).strip()

        # Extract meta description
        meta_desc_match = re.search(r'META_DESCRIPTION:\s*(.+?)(?:\n|$)', content)
        if meta_desc_match:
            data['meta_description'] = meta_desc_match.group(1).strip()

        # Extract meta keywords
        meta_keywords_match = re.search(r'META_KEYWORDS:\s*(.+?)(?:\n|$)', content)
        if meta_keywords_match:
            data['meta_keywords'] = meta_keywords_match.group(1).strip()

        # Extract excerpt
        excerpt_match = re.search(r'EXCERPT:\s*(.+?)(?:\n\n|CONTENT:)', content, re.DOTALL)
        if excerpt_match:
            data['excerpt'] = excerpt_match.group(1).strip()

        # Extract content
        content_match = re.search(r'CONTENT:\s*(.+?)$', content, re.DOTALL)
        if content_match:
            data['content'] = content_match.group(1).strip()

        # Calculate word count
        data['word_count'] = len(data['content'].split())

        # Fallbacks
        if not data['title']:
            data['title'] = f"Everything You Need to Know About {keyword.title()}"
        if not data['excerpt']:
            data['excerpt'] = data['content'][:200] + '...'
        if not data['meta_description']:
            data['meta_description'] = data['excerpt'][:160]

        return data

    def create_slug(self, title):
        """Create URL-friendly slug from title"""
        slug = title.lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'[\s_]+', '-', slug)
        slug = slug.strip('-')
        return slug

    def save_blog_post(self, blog_data, topic_id=None, status='published'):
        """
        Save generated blog post to database

        Args:
            blog_data: Dictionary with blog post data
            topic_id: Associated trending topic ID
            status: Post status (draft or published)

        Returns:
            BlogPost: Saved blog post instance
        """
        try:
            slug = self.create_slug(blog_data['title'])

            # Check for duplicate slug
            existing = BlogPost.query.filter_by(slug=slug).first()
            if existing:
                slug = f"{slug}-{int(datetime.utcnow().timestamp())}"

            blog_post = BlogPost(
                title=blog_data['title'],
                slug=slug,
                content=blog_data['content'],
                excerpt=blog_data['excerpt'],
                meta_description=blog_data['meta_description'],
                meta_keywords=blog_data['meta_keywords'],
                word_count=blog_data['word_count'],
                topic_id=topic_id,
                status=status,
                published_at=datetime.utcnow() if status == 'published' else None
            )

            db.session.add(blog_post)
            db.session.commit()

            logger.info(f"Blog post saved: {blog_post.title} (ID: {blog_post.id})")
            return blog_post

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error saving blog post: {e}")
            return None
