import requests
import logging
import boto3
import uuid
from datetime import datetime
from io import BytesIO
from openai import OpenAI
from config import Config
from PIL import Image

logger = logging.getLogger(__name__)


class ImageService:
    """Service to fetch or generate featured images for blog posts"""

    def __init__(self):
        self.unsplash_access_key = Config.UNSPLASH_ACCESS_KEY
        self.dalle_enabled = Config.DALLE_ENABLED
        self.dalle_quality = Config.DALLE_QUALITY
        self.placeholder_url = Config.IMAGE_PLACEHOLDER_URL

        logger.info(f"ImageService init: DALLE_ENABLED={self.dalle_enabled}, has_api_key={bool(Config.OPENAI_API_KEY)}")

        # Initialize OpenAI client only if DALL-E is enabled
        if self.dalle_enabled and Config.OPENAI_API_KEY:
            try:
                self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
                logger.info("✅ OpenAI client initialized successfully for DALL-E")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.openai_client = None
        else:
            self.openai_client = None
            logger.warning(f"OpenAI client NOT initialized (dalle_enabled={self.dalle_enabled}, has_key={bool(Config.OPENAI_API_KEY)})")

        # Initialize R2 client for permanent image storage
        # Log R2 configuration for debugging
        logger.info(f"R2 Config check:")
        logger.info(f"  - R2_ACCOUNT_ID: {'SET' if Config.R2_ACCOUNT_ID else 'NOT SET'}")
        logger.info(f"  - R2_ACCESS_KEY_ID: {'SET' if Config.R2_ACCESS_KEY_ID else 'NOT SET'}")
        logger.info(f"  - R2_SECRET_ACCESS_KEY: {'SET' if Config.R2_SECRET_ACCESS_KEY else 'NOT SET'}")
        logger.info(f"  - R2_BUCKET_NAME: {Config.R2_BUCKET_NAME if Config.R2_BUCKET_NAME else 'NOT SET'}")
        logger.info(f"  - R2_PUBLIC_URL: {Config.R2_PUBLIC_URL if Config.R2_PUBLIC_URL else 'NOT SET'}")

        self.r2_enabled = all([
            Config.R2_ACCOUNT_ID,
            Config.R2_ACCESS_KEY_ID,
            Config.R2_SECRET_ACCESS_KEY,
            Config.R2_BUCKET_NAME,
            Config.R2_PUBLIC_URL
        ])

        if self.r2_enabled:
            try:
                self.r2_client = boto3.client(
                    's3',
                    endpoint_url=f'https://{Config.R2_ACCOUNT_ID}.r2.cloudflarestorage.com',
                    aws_access_key_id=Config.R2_ACCESS_KEY_ID,
                    aws_secret_access_key=Config.R2_SECRET_ACCESS_KEY,
                    region_name='auto'
                )
                self.r2_bucket = Config.R2_BUCKET_NAME
                self.r2_public_url = Config.R2_PUBLIC_URL.rstrip('/')
                logger.info("✅ R2 client initialized successfully for permanent image storage")
            except Exception as e:
                logger.error(f"Failed to initialize R2 client: {e}")
                self.r2_enabled = False
                self.r2_client = None
        else:
            self.r2_client = None
            logger.warning("R2 storage not configured - DALL-E images will use temporary URLs")

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
        logger.info(f"Checking DALL-E fallback: dalle_enabled={self.dalle_enabled}, has_client={bool(self.openai_client)}")
        if self.dalle_enabled and self.openai_client:
            logger.info("Unsplash search failed. Trying DALL-E...")
            image_url = self._generate_dalle_image(title)

            if image_url:
                logger.info(f"✅ Generated DALL-E image: {image_url}")
                return image_url
        else:
            logger.warning(f"Skipping DALL-E: dalle_enabled={self.dalle_enabled}, has_client={bool(self.openai_client)}")

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
        Generate image using DALL-E 3 and upload to R2 for permanent storage

        Args:
            title: Blog post title to generate image for

        Returns:
            str: Permanent image URL or None if generation failed
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
                size="1024x1024",  # Optimized size for web delivery (was 1792x1024)
                quality=self.dalle_quality,  # 'standard' or 'hd'
                n=1
            )

            temp_image_url = response.data[0].url

            logger.info(f"DALL-E image generated successfully")

            # If R2 is enabled, download and upload to R2 for permanent storage
            if self.r2_enabled and self.r2_client:
                logger.info("Uploading DALL-E image to R2 for permanent storage...")
                permanent_url = self._upload_to_r2(temp_image_url, title)
                if permanent_url:
                    logger.info(f"✅ Image permanently stored at: {permanent_url}")
                    return permanent_url
                else:
                    logger.warning("R2 upload failed, using temporary DALL-E URL")
                    return temp_image_url
            else:
                logger.warning("R2 not configured, using temporary DALL-E URL (expires in 2 hours)")
                return temp_image_url

        except Exception as e:
            logger.error(f"DALL-E generation error: {e}")
            return None

    def _optimize_image(self, image_bytes, max_width=1200):
        """
        Optimize image: resize, convert to JPEG, and compress

        Args:
            image_bytes: Original image bytes
            max_width: Maximum width in pixels (default 1200px for web)

        Returns:
            BytesIO: Optimized image bytes
        """
        try:
            # Open image
            img = Image.open(BytesIO(image_bytes))

            # Convert RGBA to RGB if needed (for JPEG compatibility)
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background

            # Resize if image is too large
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
                logger.info(f"Resized image from {img.width}x{img.height} to {max_width}x{new_height}")

            # Save as optimized JPEG
            output = BytesIO()
            img.save(output, format='JPEG', quality=85, optimize=True)
            output.seek(0)

            original_size = len(image_bytes) / 1024  # KB
            optimized_size = len(output.getvalue()) / 1024  # KB
            savings = ((original_size - optimized_size) / original_size) * 100

            logger.info(f"Image optimized: {original_size:.1f}KB → {optimized_size:.1f}KB (saved {savings:.1f}%)")

            return output

        except Exception as e:
            logger.error(f"Error optimizing image: {e}")
            # Return original if optimization fails
            return BytesIO(image_bytes)

    def _upload_to_r2(self, image_url, title):
        """
        Download image from URL, optimize it, and upload to R2 storage

        Args:
            image_url: URL of the image to download
            title: Blog post title (used for filename)

        Returns:
            str: Public R2 URL or None if upload failed
        """
        try:
            # Download the image
            logger.info(f"Downloading image from: {image_url}")
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()

            # Optimize the image
            logger.info("Optimizing image...")
            optimized_image = self._optimize_image(response.content, max_width=1200)

            # Generate unique filename
            # Use YYYYMM folder structure (e.g., 202511/)
            now = datetime.utcnow()
            folder = now.strftime('%Y%m')
            unique_id = str(uuid.uuid4())[:8]
            filename = f"{folder}/{unique_id}.jpg"  # Changed to .jpg

            # Upload to R2
            logger.info(f"Uploading to R2 bucket '{self.r2_bucket}' as: {filename}")
            self.r2_client.put_object(
                Bucket=self.r2_bucket,
                Key=filename,
                Body=optimized_image,
                ContentType='image/jpeg',  # Changed to JPEG
                CacheControl='public, max-age=31536000'  # Cache for 1 year
            )

            # Construct public URL
            public_url = f"{self.r2_public_url}/{filename}"
            logger.info(f"✅ Image uploaded successfully to R2: {public_url}")

            return public_url

        except requests.exceptions.RequestException as e:
            logger.error(f"Error downloading image: {e}")
            return None
        except Exception as e:
            logger.error(f"Error uploading to R2: {e}")
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
