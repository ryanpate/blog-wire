import openai
from openai import OpenAI
import re
from datetime import datetime
import logging
from difflib import SequenceMatcher
from models import BlogPost, db
from config import Config
from services.image_service import ImageService

logger = logging.getLogger(__name__)


class BlogGenerator:
    """Service to generate blog posts using OpenAI API"""

    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.OPENAI_MODEL
        self.image_service = ImageService()

    def is_similar_to_existing(self, title, threshold=0.75):
        """
        Check if a title is too similar to existing posts

        Args:
            title: The title to check
            threshold: Similarity threshold (0.0-1.0, default 0.75 = 75% similar)

        Returns:
            tuple: (is_similar: bool, similar_post: BlogPost or None)
        """
        existing_posts = BlogPost.query.all()

        for post in existing_posts:
            # Calculate similarity ratio
            similarity = SequenceMatcher(None, title.lower(), post.title.lower()).ratio()

            if similarity >= threshold:
                logger.warning(f"Title too similar to existing post: '{title}' vs '{post.title}' ({similarity:.2%} similar)")
                return True, post

        return False, None

    def is_topic_covered(self, topic, threshold=0.70):
        """
        Check if a topic has already been covered in existing posts

        Args:
            topic: The topic/keyword to check
            threshold: Similarity threshold (0.0-1.0, default 0.70 = 70% similar)

        Returns:
            tuple: (is_covered: bool, similar_post: BlogPost or None)
        """
        existing_posts = BlogPost.query.all()
        topic_lower = topic.lower()

        for post in existing_posts:
            # Check title similarity
            title_similarity = SequenceMatcher(None, topic_lower, post.title.lower()).ratio()

            # Check if topic keywords appear in title
            topic_words = set(topic_lower.split())
            title_words = set(post.title.lower().split())

            # Calculate word overlap
            if topic_words and title_words:
                common_words = topic_words.intersection(title_words)
                word_overlap = len(common_words) / len(topic_words)
            else:
                word_overlap = 0

            # Consider it covered if either high title similarity or high word overlap
            if title_similarity >= threshold or word_overlap >= 0.6:
                logger.info(f"Topic '{topic}' already covered by: '{post.title}' (similarity: {title_similarity:.2%}, overlap: {word_overlap:.2%})")
                return True, post

        return False, None

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
                max_tokens=16384  # Max for gpt-4o model - supports long-form 2000-3500 word posts
            )

            content = response.choices[0].message.content

            # Parse the structured response
            blog_data = self._parse_blog_content(content, keyword)

            # Fetch featured image
            blog_data['featured_image_url'] = self.image_service.get_featured_image(
                title=blog_data['title'],
                keywords=blog_data.get('meta_keywords')
            )

            return blog_data

        except Exception as e:
            logger.error(f"Error generating blog post for '{keyword}': {e}")
            return None

    def _create_blog_prompt(self, keyword, min_words, max_words):
        """Create the prompt for blog generation"""
        return f"""Write a comprehensive, SEO-optimized blog post about: "{keyword}"

Requirements:
- Word count: {min_words}-{max_words} words (IMPORTANT: Ensure the content is substantial and meets this requirement)
- Tone: Conversational, friendly, and personable - write as Ryan Pate speaking directly to readers
- Style: Long-form, informative, well-structured with deep insights
- Use first-person perspective ("I", "my experience", etc.) to make it personal
- Include relevant headers (H2, H3) for better readability
- Naturally incorporate long-tail SEO keywords throughout
- Add real value with actionable insights, examples, and personal observations
- End with a signature: "- Ryan Pate"

SEO Focus:
- Use long-form keywords (e.g., "how to invest in cryptocurrency for beginners" not just "crypto")
- Include semantic keywords and related terms
- Front-load important keywords in title and first paragraph
- Use natural language that people actually search for

Structure your response EXACTLY as follows:

TITLE: [Compelling, SEO-friendly title with long-tail keywords]

META_DESCRIPTION: [150-160 character meta description with primary keyword]

META_KEYWORDS: [5-7 long-form keywords, comma-separated - focus on phrases people search]

EXCERPT: [2-3 sentence compelling excerpt that includes main keyword]

CONTENT:
[Full blog post content in Markdown format with headers, lists, and formatting]

IMPORTANT:
- End the blog post with a conversational closing paragraph
- Sign off with: "- Ryan Pate"
- Write as if Ryan is sharing personal insights and expertise
- Make it feel authentic and relatable, not corporate or robotic
- Ensure content is truly {min_words}-{max_words} words - no shorter!"""

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

        # Extract title - handle both "TITLE:" and "**TITLE:**" formats
        title_match = re.search(r'\*\*TITLE:\*\*\s*(.+?)(?:\n|$)', content)
        if not title_match:
            title_match = re.search(r'TITLE:\s*(.+?)(?:\n|$)', content)
        if title_match:
            data['title'] = title_match.group(1).strip()

        # Extract meta description - handle both formats
        meta_desc_match = re.search(r'\*\*META_DESCRIPTION:\*\*\s*(.+?)(?:\n|$)', content)
        if not meta_desc_match:
            meta_desc_match = re.search(r'META_DESCRIPTION:\s*(.+?)(?:\n|$)', content)
        if meta_desc_match:
            data['meta_description'] = meta_desc_match.group(1).strip()

        # Extract meta keywords - handle both formats
        meta_keywords_match = re.search(r'\*\*META_KEYWORDS:\*\*\s*(.+?)(?:\n|$)', content)
        if not meta_keywords_match:
            meta_keywords_match = re.search(r'META_KEYWORDS:\s*(.+?)(?:\n|$)', content)
        if meta_keywords_match:
            data['meta_keywords'] = meta_keywords_match.group(1).strip()

        # Extract excerpt - handle both formats
        excerpt_match = re.search(r'\*\*EXCERPT:\*\*\s*(.+?)(?:\n\n|---|\*\*CONTENT)', content, re.DOTALL)
        if not excerpt_match:
            excerpt_match = re.search(r'EXCERPT:\s*(.+?)(?:\n\n|CONTENT:|---)', content, re.DOTALL)
        if excerpt_match:
            data['excerpt'] = excerpt_match.group(1).strip()

        # Extract content - handle multiple formats
        # Try "CONTENT:" label first
        content_match = re.search(r'CONTENT:\s*(.+?)$', content, re.DOTALL)

        # If not found, try content after "---" separator
        if not content_match:
            content_match = re.search(r'---\s*\n\n(.+?)$', content, re.DOTALL)

        # If still not found, try content after EXCERPT
        if not content_match and data['excerpt']:
            # Find where excerpt ends and take everything after
            excerpt_end = content.find(data['excerpt']) + len(data['excerpt'])
            remaining = content[excerpt_end:]
            # Skip past any separators
            separator_match = re.search(r'---\s*\n\n(.+?)$', remaining, re.DOTALL)
            if separator_match:
                content_match = separator_match

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
                featured_image_url=blog_data.get('featured_image_url'),
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
