import requests
import logging
from openai import OpenAI
from config import Config

logger = logging.getLogger(__name__)


class ImageService:
    """Service to fetch or generate featured images for blog posts"""

    def __init__(self):
        self.unsplash_access_key = Config.UNSPLASH_ACCESS_KEY
        self.dalle_enabled = Config.DALLE_ENABLED
        self.dalle_quality = Config.DALLE_QUALITY
        self.placeholder_url = Config.IMAGE_PLACEHOLDER_URL

        # Initialize OpenAI client only if DALL-E is enabled
        if self.dalle_enabled and Config.OPENAI_API_KEY:
            self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
        else:
            self.openai_client = None

    def get_featured_image(self, title, keywords=None):
        """
        Get featured image URL for a blog post
        Priority: Unsplash -> DALL-E -> Placeholder

        Args:
            title: Blog post title
            keywords: Optional comma-separated keywords for better search

        Returns:
            str: Image URL
        """
        logger.info(f"Fetching featured image for: {title}")

        # Try Unsplash first (free and fast)
        image_url = self._search_unsplash(title, keywords)

        if image_url:
            logger.info(f"✅ Found Unsplash image: {image_url}")
            return image_url

        # Fallback to DALL-E if enabled
        if self.dalle_enabled and self.openai_client:
            logger.info("Unsplash search failed. Trying DALL-E...")
            image_url = self._generate_dalle_image(title)

            if image_url:
                logger.info(f"✅ Generated DALL-E image: {image_url}")
                return image_url

        # Final fallback to placeholder
        logger.warning(f"No image found for '{title}'. Using placeholder.")
        return self.placeholder_url

    def _search_unsplash(self, title, keywords=None):
        """
        Search Unsplash for relevant image

        Args:
            title: Blog post title to search for
            keywords: Optional additional keywords

        Returns:
            str: Image URL or None if not found
        """
        if not self.unsplash_access_key:
            logger.warning("Unsplash API key not configured. Skipping Unsplash search.")
            return None

        try:
            # Build search query from title and keywords
            search_query = self._build_search_query(title, keywords)

            # Unsplash API endpoint
            url = "https://api.unsplash.com/search/photos"
            headers = {
                "Authorization": f"Client-ID {self.unsplash_access_key}"
            }
            params = {
                "query": search_query,
                "per_page": 1,
                "orientation": "landscape",  # Better for blog headers
                "content_filter": "high"  # Family-friendly content
            }

            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Check if we found any results
            if data.get('results') and len(data['results']) > 0:
                photo = data['results'][0]

                # Get the regular size URL (good quality, not too large)
                image_url = photo['urls']['regular']

                # Log photographer credit (Unsplash requirement)
                photographer = photo['user']['name']
                photographer_url = photo['user']['links']['html']
                logger.info(f"Image by {photographer} on Unsplash: {photographer_url}")

                return image_url
            else:
                logger.info(f"No Unsplash results for query: {search_query}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Unsplash API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error searching Unsplash: {e}")
            return None

    def _generate_dalle_image(self, title):
        """
        Generate image using DALL-E 3

        Args:
            title: Blog post title to generate image for

        Returns:
            str: Image URL or None if generation failed
        """
        if not self.openai_client:
            logger.warning("OpenAI client not initialized. Skipping DALL-E generation.")
            return None

        try:
            # Create a descriptive prompt for DALL-E
            prompt = self._create_dalle_prompt(title)

            logger.info(f"Generating DALL-E image with prompt: {prompt}")

            response = self.openai_client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1792x1024",  # Landscape format for blog headers
                quality=self.dalle_quality,  # 'standard' or 'hd'
                n=1
            )

            image_url = response.data[0].url

            logger.info(f"DALL-E image generated successfully")
            return image_url

        except Exception as e:
            logger.error(f"DALL-E generation error: {e}")
            return None

    def _build_search_query(self, title, keywords=None):
        """
        Build optimal search query from title and keywords

        Args:
            title: Blog post title
            keywords: Optional keywords

        Returns:
            str: Search query
        """
        # Extract key terms from title (remove common words)
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                     'of', 'with', 'by', 'from', 'about', 'how', 'what', 'why', 'when',
                     'where', 'which', 'who', 'best', 'guide', 'tips', 'everything',
                     'complete', 'ultimate', 'your', 'you', 'need', 'know'}

        # Clean and filter title words
        title_words = [w.lower() for w in title.split() if w.lower() not in stop_words and len(w) > 3]

        # Take first 3-5 significant words
        query_words = title_words[:5]

        # Add keywords if provided
        if keywords:
            keyword_list = [k.strip() for k in keywords.split(',')[:2]]  # Take first 2 keywords
            query_words.extend(keyword_list)

        # Join into search query
        search_query = ' '.join(query_words)

        # Limit length (Unsplash has query length limits)
        if len(search_query) > 100:
            search_query = search_query[:100]

        return search_query

    def _create_dalle_prompt(self, title):
        """
        Create DALL-E prompt from blog title

        Args:
            title: Blog post title

        Returns:
            str: DALL-E prompt
        """
        # Create a descriptive, professional prompt
        prompt = f"A professional, modern, and visually appealing illustration for a blog post titled '{title}'. "
        prompt += "The image should be clean, colorful, and suitable for a professional blog header. "
        prompt += "Style: contemporary digital illustration with a professional aesthetic."

        return prompt

    def get_placeholder_image(self):
        """
        Get placeholder image URL

        Returns:
            str: Placeholder image URL
        """
        return self.placeholder_url
