#!/usr/bin/env python3
"""
Generate 5 trending blog posts with long-tail SEO keywords
These are curated trending topics for high search volume
"""

from app import app
from services.automation_service import AutomationService

# Curated trending topics with long-tail SEO keywords
# These are selected for high search volume and relevance
TRENDING_TOPICS = [
    "how to use artificial intelligence for business growth in 2025",
    "best ways to invest in cryptocurrency for beginners step by step",
    "complete guide to starting a successful online business from home",
    "how to improve mental health and reduce stress naturally",
    "sustainable living tips for reducing carbon footprint at home"
]

def generate_trending_posts():
    """Generate 5 trending blog posts"""

    print("=" * 80)
    print("GENERATING 5 TRENDING BLOG POSTS")
    print("=" * 80)
    print("\nThese posts are optimized for:")
    print("✅ Long-tail SEO keywords")
    print("✅ Conversational voice (Ryan Pate)")
    print("✅ 2000-3500 words each")
    print("✅ Personal signature")
    print("\n" + "=" * 80)

    with app.app_context():
        automation = AutomationService()

        generated_posts = []

        for i, topic in enumerate(TRENDING_TOPICS, 1):
            print(f"\n[{i}/5] Generating: {topic}")
            print("-" * 80)

            try:
                post = automation.generate_single_blog(topic)

                if post:
                    print(f"✅ SUCCESS!")
                    print(f"   Title: {post.title}")
                    print(f"   Words: {post.word_count}")
                    print(f"   Slug: {post.slug}")
                    print(f"   URL: /blog/{post.slug}")
                    generated_posts.append(post)
                else:
                    print(f"❌ FAILED to generate post for: {topic}")

            except Exception as e:
                print(f"❌ ERROR: {e}")
                continue

        print("\n" + "=" * 80)
        print(f"✅ COMPLETE! Generated {len(generated_posts)} of 5 posts")
        print("=" * 80)
        print("\nGenerated posts:")
        for i, post in enumerate(generated_posts, 1):
            print(f"{i}. {post.title} ({post.word_count} words)")

        return generated_posts

if __name__ == '__main__':
    print("\n🚀 Starting Blog Generation...\n")
    print("This will take about 2-3 minutes...")
    print("Each post is being carefully crafted by AI...\n")

    posts = generate_trending_posts()

    print("\n🎉 All done! Check your blog to see the new posts!")
    print("\nView them at: http://localhost:5001")
    print("Or on Railway: https://web-production-98510.up.railway.app/\n")
