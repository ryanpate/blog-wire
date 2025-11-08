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
                        "content": "You are Ryan Pate, a real person who writes authentic, conversational blog posts. You write like you talk - naturally, with personality, and without corporate jargon or AI-sounding phrases. Each post you write has a distinct voice and style. You're not afraid to be opinionated, use contractions, or write short punchy sentences for emphasis. Your writing feels human because it is. Avoid repetitive headline patterns and formulaic structures - every post should feel fresh and different."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.8,
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
- Tone: Natural, conversational, and authentic - write as Ryan Pate speaking casually to readers
- Style: Long-form, informative, well-structured with genuine insights and opinions
- Use first-person perspective ("I", "my experience", "I've noticed", etc.) to make it personal
- Include relevant headers (H2, H3) for better readability
- Naturally incorporate long-tail SEO keywords throughout
- Add real value with actionable insights, examples, and personal observations
- End with a signature: "- Ryan Pate"

WRITING STYLE - CRITICAL:
- Write like a real person having a conversation, NOT like an AI or corporate blog
- Use contractions (I'm, you're, don't, can't, etc.) frequently for natural flow
- Include occasional sentence fragments for emphasis. Like this.
- Vary sentence length dramatically - mix short punchy sentences with longer explanatory ones
- Use informal language and phrases ("honestly", "look", "here's the thing", "to be fair", "pretty much")
- Include personal opinions and takes, not just facts
- Show personality - be slightly opinionated, use humor occasionally, admit uncertainties
- Avoid these AI writing tells: "delve into", "it's important to note", "landscape", "robust", "leverage", "utilize", "navigate"
- Skip formulaic transitions like "In conclusion" or "In today's digital age"
- Don't overuse power words or hyperbolic language

HEADLINE VARIATION - MUST FOLLOW:
Your headline style should vary significantly from post to post. Rotate between these approaches:
- Question format: "Why Does [Topic] Matter More Than You Think?"
- Direct/Bold: "[Number] Things Nobody Tells You About [Topic]"
- Personal angle: "I Spent [Time] Learning [Topic] - Here's What I Found"
- Controversial: "[Topic] Is Overrated (And Here's Why)"
- Simple/Clear: "Understanding [Topic]: A Real-World Guide"
- Story-driven: "How [Topic] Changed My Perspective on [Related Thing]"
- Contrarian: "Everyone's Wrong About [Topic]"
- Practical: "The Actual Way to [Accomplish Something Related to Topic]"

AVOID these repetitive headline patterns:
- Starting with "The Ultimate Guide to..."
- Using "Everything You Need to Know About..."
- "The Complete Guide to..."
- "[Topic] 101: A Beginner's Guide"
- Overusing colons in titles
- Generic superlatives like "best", "top", "essential" in every title

SEO Focus:
- Use long-form, natural search phrases (e.g., "how to invest in cryptocurrency for beginners" not just "crypto")
- Include semantic keywords and related terms people actually use
- Front-load important keywords in title and first paragraph naturally
- Use conversational search language ("how do I", "what's the best way to", etc.)
- Think about featured snippet opportunities - answer "what", "why", "how" questions clearly

Structure your response EXACTLY as follows:

TITLE: [Natural, varied title using one of the rotation styles above - avoid repetitive patterns]

META_DESCRIPTION: [150-160 character meta description with primary keyword, written conversationally]

META_KEYWORDS: [5-7 long-form search phrases people actually use, comma-separated]

EXCERPT: [2-3 sentence compelling excerpt in conversational tone that includes main keyword]

CONTENT:
[Full blog post content in Markdown format with headers, lists, and formatting]

IMPORTANT:
- End the blog post with a natural, conversational closing (not "in conclusion" or formulaic)
- Sign off with: "- Ryan Pate"
- Write as if Ryan is casually explaining something to a friend over coffee
- Make it feel authentic and human, with personality and opinions
- Use natural language patterns - how real people actually write and speak
- Ensure content is truly {min_words}-{max_words} words - no shorter!
- Each post should feel distinctly different in voice and structure from others"""

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
