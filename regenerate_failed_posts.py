#!/usr/bin/env python3
"""
Regenerate the 4 failed posts with fixed parser
"""

from app import app
from services.automation_service import AutomationService

# The 4 topics that failed (cryptocurrency worked, so skip it)
FAILED_TOPICS = [
    "how to use artificial intelligence for business growth in 2025",
    "complete guide to starting a successful online business from home",
    "how to improve mental health and reduce stress naturally",
    "sustainable living tips for reducing carbon footprint at home"
]

def regenerate_failed_posts():
    """Regenerate the 4 failed blog posts"""

    print("=" * 80)
    print("REGENERATING 4 FAILED BLOG POSTS")
    print("=" * 80)
    print("\nUsing FIXED parser that handles OpenAI's response format")
    print("")

    with app.app_context():
        automation = AutomationService()

        generated_posts = []

        for i, topic in enumerate(FAILED_TOPICS, 1):
            print(f"\n[{i}/4] Generating: {topic}")
            print("-" * 80)

            try:
                post = automation.generate_single_blog(topic)

                if post and post.word_count > 0:
                    print(f"✅ SUCCESS!")
                    print(f"   Title: {post.title}")
                    print(f"   Words: {post.word_count}")
                    print(f"   Slug: {post.slug}")
                    print(f"   URL: /blog/{post.slug}")
                    generated_posts.append(post)
                else:
                    print(f"❌ FAILED - Post has 0 word count")

            except Exception as e:
                print(f"❌ ERROR: {e}")
                continue

        print("\n" + "=" * 80)
        print(f"✅ COMPLETE! Generated {len(generated_posts)} of 4 posts")
        print("=" * 80)
        print("\nGenerated posts:")
        for i, post in enumerate(generated_posts, 1):
            print(f"{i}. {post.title} ({post.word_count} words)")

        return generated_posts

if __name__ == '__main__':
    print("\n🚀 Regenerating Failed Posts...\n")
    posts = regenerate_failed_posts()
    print("\n🎉 Done! Check your blog at: http://localhost:5001\n")
