#!/usr/bin/env python3
"""
Generate blog posts from custom_topics.txt file
This is useful when Google Trends is unavailable
"""

from app import app
from services.automation_service import AutomationService
import random

def load_topics(filename='custom_topics.txt'):
    """Load topics from text file"""
    topics = []
    try:
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if line and not line.startswith('#'):
                    topics.append(line)
        return topics
    except FileNotFoundError:
        print(f"❌ File {filename} not found")
        return []

def generate_posts(count=1, random_selection=True):
    """Generate blog posts from custom topics"""
    topics = load_topics()

    if not topics:
        print("❌ No topics found in custom_topics.txt")
        return

    print(f"📚 Found {len(topics)} topics in custom_topics.txt\n")

    # Select topics
    if random_selection:
        selected_topics = random.sample(topics, min(count, len(topics)))
        print(f"🎲 Randomly selected {len(selected_topics)} topics\n")
    else:
        selected_topics = topics[:count]
        print(f"📝 Using first {len(selected_topics)} topics\n")

    # Generate blogs
    with app.app_context():
        automation = AutomationService()

        for i, topic in enumerate(selected_topics, 1):
            print(f"[{i}/{len(selected_topics)}] Generating: {topic}")

            post = automation.generate_single_blog(topic)

            if post:
                print(f"   ✅ Published: {post.title}")
                print(f"   📊 {post.word_count} words")
                print(f"   🔗 http://localhost:5001/blog/{post.slug}\n")
            else:
                print(f"   ❌ Failed to generate\n")

        print(f"✅ Completed! Generated {len(selected_topics)} blog posts")

if __name__ == '__main__':
    import sys

    count = int(sys.argv[1]) if len(sys.argv) > 1 else 1

    print("=" * 60)
    print("Blog Wire - Custom Topic Generator")
    print("=" * 60)
    print()

    generate_posts(count=count, random_selection=True)
