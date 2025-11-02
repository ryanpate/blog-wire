#!/usr/bin/env python3
"""
Generate initial diverse blog posts for fresh start
Selects topics from different categories to ensure variety
"""

from app import app
from services.automation_service import AutomationService

# Curated list of diverse topics (one from each category)
DIVERSE_TOPICS = [
    # Technology
    "quantum computing explained for beginners",

    # Health & Wellness
    "intermittent fasting benefits and how to start",

    # Finance
    "passive income strategies for 2025",

    # Lifestyle
    "minimalist living tips for reducing stress",

    # Business
    "digital marketing strategies for small businesses",

    # Travel
    "budget travel destinations in Europe",

    # Food
    "healthy meal prep ideas for busy professionals",

    # Personal Development
    "productivity apps and tools for remote workers",

    # Sustainability
    "sustainable fashion trends and eco-friendly brands"
]

def generate_diverse_posts(count=9):
    """Generate diverse blog posts from different categories"""
    with app.app_context():
        automation = AutomationService()

        # Select topics (up to count)
        selected_topics = DIVERSE_TOPICS[:count]

        print(f"📝 Generating {len(selected_topics)} diverse blog posts...\n")

        successful = 0
        failed = 0

        for i, topic in enumerate(selected_topics, 1):
            print(f"[{i}/{len(selected_topics)}] Generating: {topic}...")

            try:
                post = automation.generate_single_blog(topic)

                if post:
                    print(f"   ✅ Published: {post.title}")
                    print(f"   📊 {post.word_count} words")
                    print(f"   🔗 /blog/{post.slug}\n")
                    successful += 1
                else:
                    print(f"   ❌ Failed to generate\n")
                    failed += 1
            except Exception as e:
                print(f"   ❌ Error: {e}\n")
                failed += 1

        print("=" * 60)
        print(f"✅ Successfully generated: {successful} posts")
        if failed > 0:
            print(f"❌ Failed: {failed} posts")
        print("=" * 60)

if __name__ == '__main__':
    import sys

    count = int(sys.argv[1]) if len(sys.argv) > 1 else 9
    generate_diverse_posts(count)
