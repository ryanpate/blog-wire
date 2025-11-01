import re
import logging
from models import AffiliateLink, db

logger = logging.getLogger(__name__)


class AffiliateService:
    """Service to manage and inject affiliate links"""

    def __init__(self):
        pass

    def inject_affiliate_links(self, content, max_links=3):
        """
        Inject affiliate links into blog content

        Args:
            content: Blog post content (markdown)
            max_links: Maximum number of affiliate links to inject

        Returns:
            str: Content with affiliate links injected
        """
        # Get active affiliate links
        affiliate_links = AffiliateLink.query.filter_by(active=True).all()

        if not affiliate_links:
            logger.info("No active affiliate links to inject")
            return content

        modified_content = content
        links_injected = 0

        for aff_link in affiliate_links:
            if links_injected >= max_links:
                break

            # Find keyword in content (case-insensitive)
            pattern = re.compile(r'\b' + re.escape(aff_link.keyword) + r'\b', re.IGNORECASE)
            matches = list(pattern.finditer(modified_content))

            if matches and links_injected < max_links:
                # Replace first occurrence with affiliate link
                match = matches[0]
                keyword_text = match.group(0)

                # Create markdown link
                affiliate_markdown = f"[{keyword_text}]({aff_link.url})"

                # Replace in content
                modified_content = (
                    modified_content[:match.start()] +
                    affiliate_markdown +
                    modified_content[match.end():]
                )

                links_injected += 1
                logger.info(f"Injected affiliate link for '{aff_link.keyword}'")

        return modified_content

    def add_affiliate_link(self, keyword, url, platform=None):
        """
        Add a new affiliate link to the database

        Args:
            keyword: Keyword to match in content
            url: Affiliate URL
            platform: Platform name (e.g., 'amazon', 'ebay')

        Returns:
            AffiliateLink: Created affiliate link instance
        """
        try:
            aff_link = AffiliateLink(
                keyword=keyword,
                url=url,
                platform=platform,
                active=True
            )

            db.session.add(aff_link)
            db.session.commit()

            logger.info(f"Added affiliate link: {keyword} -> {url}")
            return aff_link

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding affiliate link: {e}")
            return None

    def get_all_affiliate_links(self):
        """Get all affiliate links"""
        return AffiliateLink.query.all()

    def toggle_affiliate_link(self, link_id, active):
        """
        Enable or disable an affiliate link

        Args:
            link_id: Affiliate link ID
            active: True to enable, False to disable
        """
        try:
            aff_link = AffiliateLink.query.get(link_id)
            if aff_link:
                aff_link.active = active
                db.session.commit()
                logger.info(f"Affiliate link {link_id} set to {'active' if active else 'inactive'}")
                return True
            return False

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error toggling affiliate link: {e}")
            return False

    def track_click(self, link_id):
        """
        Track a click on an affiliate link

        Args:
            link_id: Affiliate link ID
        """
        try:
            aff_link = AffiliateLink.query.get(link_id)
            if aff_link:
                aff_link.click_count += 1
                db.session.commit()

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error tracking affiliate click: {e}")
