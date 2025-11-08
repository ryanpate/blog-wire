import re
from bs4 import BeautifulSoup
import markdown
import logging

logger = logging.getLogger(__name__)


class SEOService:
    """Service for SEO optimization of blog posts"""

    def __init__(self):
        pass

    def optimize_content(self, content, keyword, title):
        """
        Optimize blog content for SEO

        Args:
            content: Blog post content (markdown)
            keyword: Target keyword
            title: Post title

        Returns:
            str: SEO-optimized content
        """
        # Convert markdown to HTML for processing
        html_content = markdown.markdown(content)
        soup = BeautifulSoup(html_content, 'html.parser')

        # Ensure keyword appears in first paragraph
        first_p = soup.find('p')
        if first_p and keyword.lower() not in first_p.text.lower():
            # Keyword not in first paragraph, add it naturally
            logger.info(f"Adding keyword '{keyword}' to first paragraph for SEO")

        # Ensure proper heading structure
        self._optimize_headings(soup)

        # Add internal linking opportunities (placeholder for future)
        # self._add_internal_links(soup)

        # Convert back to markdown-friendly format
        return content

    def _optimize_headings(self, soup):
        """Ensure proper heading hierarchy"""
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])

        # Ensure only one H1 (should be the title)
        h1_count = len([h for h in headings if h.name == 'h1'])
        if h1_count > 1:
            logger.warning(f"Multiple H1 tags found ({h1_count}). SEO best practice is one H1 per page.")

    def generate_schema_markup(self, blog_post):
        """
        Generate JSON-LD schema markup for article

        Args:
            blog_post: BlogPost model instance

        Returns:
            dict: Schema.org Article markup
        """
        from config import Config

        # Enhanced author schema with more detail
        author_schema = {
            "@type": "Person",
            "name": Config.SITE_AUTHOR,
            "url": f"https://{Config.BLOG_DOMAIN}",
            "description": "Writer and content creator focused on trending topics and insights"
        }

        schema = {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": blog_post.title,
            "description": blog_post.meta_description or blog_post.excerpt,
            "datePublished": blog_post.published_at.isoformat() if blog_post.published_at else None,
            "dateModified": blog_post.updated_at.isoformat() if blog_post.updated_at else blog_post.published_at.isoformat() if blog_post.published_at else None,
            "author": author_schema,
            "publisher": {
                "@type": "Organization",
                "name": Config.BLOG_NAME,
                "url": f"https://{Config.BLOG_DOMAIN}",
                "logo": {
                    "@type": "ImageObject",
                    "url": f"https://{Config.BLOG_DOMAIN}/static/logo.png"
                }
            },
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": f"https://{Config.BLOG_DOMAIN}/blog/{blog_post.slug}"
            },
            "wordCount": blog_post.word_count,
            "inLanguage": "en-US",
            "isAccessibleForFree": True
        }

        # Add image if available with enhanced properties
        if blog_post.featured_image_url:
            schema["image"] = {
                "@type": "ImageObject",
                "url": blog_post.featured_image_url,
                "width": 1200,
                "height": 630,
                "caption": blog_post.title
            }

        # Add keywords/tags if available
        if blog_post.meta_keywords:
            keywords = [k.strip() for k in blog_post.meta_keywords.split(',')]
            schema["keywords"] = keywords

        return schema

    def generate_breadcrumb_schema(self, blog_post):
        """
        Generate breadcrumb schema for article pages

        Args:
            blog_post: BlogPost model instance

        Returns:
            dict: Schema.org BreadcrumbList markup
        """
        from config import Config

        return {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": 1,
                    "name": "Home",
                    "item": f"https://{Config.BLOG_DOMAIN}/"
                },
                {
                    "@type": "ListItem",
                    "position": 2,
                    "name": blog_post.title,
                    "item": f"https://{Config.BLOG_DOMAIN}/blog/{blog_post.slug}"
                }
            ]
        }

    def generate_website_schema(self):
        """
        Generate website schema for homepage

        Returns:
            dict: Schema.org WebSite markup
        """
        from config import Config

        return {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": Config.BLOG_NAME,
            "url": f"https://{Config.BLOG_DOMAIN}",
            "description": "Trending topics and insights from around the web",
            "publisher": {
                "@type": "Organization",
                "name": Config.BLOG_NAME,
                "logo": {
                    "@type": "ImageObject",
                    "url": f"https://{Config.BLOG_DOMAIN}/static/logo.png"
                }
            },
            "potentialAction": {
                "@type": "SearchAction",
                "target": f"https://{Config.BLOG_DOMAIN}/?s={{search_term_string}}",
                "query-input": "required name=search_term_string"
            }
        }

    def extract_faq_from_content(self, content):
        """
        Extract FAQ questions and answers from blog content
        Looks for patterns like "What is...", "How to...", "Why does..." followed by answers

        Args:
            content: Blog post content in markdown

        Returns:
            list: List of dicts with 'question' and 'answer' keys, or empty list
        """
        faqs = []

        # Pattern to match questions in headers (H2/H3) and their following content
        # Looks for headers that start with question words
        question_patterns = [
            r'##\s+(What|Why|How|When|Where|Who|Can|Should|Is|Are|Do|Does)\s+.+?\?',
            r'###\s+(What|Why|How|When|Where|Who|Can|Should|Is|Are|Do|Does)\s+.+?\?'
        ]

        for pattern in question_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                question = match.group(0).strip('#').strip()

                # Get the position after the question
                start_pos = match.end()

                # Find the next header or end of content
                next_header = re.search(r'\n##', content[start_pos:])
                if next_header:
                    end_pos = start_pos + next_header.start()
                else:
                    end_pos = len(content)

                # Extract answer (next paragraph after the question)
                answer_text = content[start_pos:end_pos].strip()

                # Take first 2-3 paragraphs as answer (up to 500 chars)
                paragraphs = [p.strip() for p in answer_text.split('\n\n') if p.strip()]
                answer = ' '.join(paragraphs[:2])[:500]

                if answer and len(answer) > 50:  # Only include substantial answers
                    faqs.append({
                        'question': question,
                        'answer': answer
                    })

        return faqs[:5]  # Limit to 5 FAQs for schema

    def generate_faq_schema(self, blog_post):
        """
        Generate FAQ schema markup if the content contains Q&A patterns

        Args:
            blog_post: BlogPost model instance

        Returns:
            dict: Schema.org FAQPage markup, or None if no FAQs found
        """
        faqs = self.extract_faq_from_content(blog_post.content)

        if not faqs:
            return None

        faq_entities = []
        for faq in faqs:
            faq_entities.append({
                "@type": "Question",
                "name": faq['question'],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": faq['answer']
                }
            })

        return {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": faq_entities
        }

    def calculate_seo_score(self, blog_post):
        """
        Calculate basic SEO score for a blog post

        Args:
            blog_post: BlogPost model instance

        Returns:
            dict: SEO score and recommendations
        """
        score = 0
        max_score = 100
        issues = []
        good_points = []

        # Title length (50-60 characters is ideal)
        title_len = len(blog_post.title)
        if 50 <= title_len <= 60:
            score += 15
            good_points.append("Title length is optimal")
        elif title_len < 50:
            score += 8
            issues.append(f"Title is too short ({title_len} chars). Aim for 50-60 characters.")
        else:
            score += 8
            issues.append(f"Title is too long ({title_len} chars). Aim for 50-60 characters.")

        # Meta description (150-160 characters)
        if blog_post.meta_description:
            meta_len = len(blog_post.meta_description)
            if 150 <= meta_len <= 160:
                score += 15
                good_points.append("Meta description length is perfect")
            elif meta_len < 150:
                score += 8
                issues.append(f"Meta description is short ({meta_len} chars). Aim for 150-160.")
            else:
                score += 8
                issues.append(f"Meta description is long ({meta_len} chars). May be truncated.")
        else:
            issues.append("Missing meta description")

        # Content length (2000+ words for long-form)
        if blog_post.word_count >= 2000:
            score += 20
            good_points.append(f"Excellent word count ({blog_post.word_count} words)")
        elif blog_post.word_count >= 1000:
            score += 15
            issues.append(f"Good word count ({blog_post.word_count}), but longer is better for SEO")
        else:
            score += 5
            issues.append(f"Content too short ({blog_post.word_count} words). Aim for 2000+")

        # URL structure (slug)
        slug_words = len(blog_post.slug.split('-'))
        if 3 <= slug_words <= 5:
            score += 10
            good_points.append("URL structure is clean and descriptive")
        else:
            score += 5
            issues.append("URL could be more concise (3-5 words ideal)")

        # Keywords
        if blog_post.meta_keywords:
            score += 10
            good_points.append("Meta keywords defined")
        else:
            issues.append("Missing meta keywords")

        # Heading structure (check for H2/H3 in content)
        if re.search(r'##\s+', blog_post.content):
            score += 15
            good_points.append("Content uses proper heading structure")
        else:
            score += 5
            issues.append("Content lacks proper headings (H2/H3)")

        # Images (check for markdown images)
        image_count = len(re.findall(r'!\[.*?\]\(.*?\)', blog_post.content))
        if image_count > 0:
            score += 15
            good_points.append(f"Content includes {image_count} image(s)")
        else:
            issues.append("Content has no images. Add relevant images for better engagement.")

        return {
            'score': score,
            'max_score': max_score,
            'percentage': round((score / max_score) * 100, 1),
            'grade': self._get_grade(score, max_score),
            'issues': issues,
            'good_points': good_points
        }

    def _get_grade(self, score, max_score):
        """Convert score to letter grade"""
        percentage = (score / max_score) * 100
        if percentage >= 90:
            return 'A'
        elif percentage >= 80:
            return 'B'
        elif percentage >= 70:
            return 'C'
        elif percentage >= 60:
            return 'D'
        else:
            return 'F'
