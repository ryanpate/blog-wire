#!/usr/bin/env python3
"""
Generate blog posts from custom topic lists
Use this when Google Trends is unavailable or you want specific topics
"""

from app import app
from services.automation_service import AutomationService

# Define your topic categories and keywords
TOPIC_LISTS = {
    "technology": [
        "artificial intelligence trends",
        "cloud computing benefits",
        "cybersecurity best practices",
        "smartphone comparison guide",
        "software development trends"
    ],
    "health": [
        "healthy eating habits",
        "mental health awareness",
        "fitness workout routines",
        "stress management techniques",
        "sleep quality improvement"
    ],
    "finance": [
        "personal finance tips",
        "investing for beginners",
        "cryptocurrency explained",
        "retirement planning strategies",
        "budgeting methods"
    ],
    "lifestyle": [
        "productivity hacks",
        "work from home tips",
        "sustainable living ideas",
        "travel destination guides",
        "home organization tips"
    ],
    "business": [
        "entrepreneurship guide",
        "marketing strategies",
        "remote team management",
        "startup funding options",
        "business growth tactics"
    ]
}

def generate_from_category(category, count=1):
    """Generate blog posts from a specific category"""
    with app.app_context():
        automation = AutomationService()
        
        if category not in TOPIC_LISTS:
            print(f"❌ Category '{category}' not found")
            print(f"Available: {', '.join(TOPIC_LISTS.keys())}")
            return
        
        topics = TOPIC_LISTS[category][:count]
        
        print(f"📝 Generating {len(topics)} blog(s) from {category.upper()} category\n")
        
        for i, topic in enumerate(topics, 1):
            print(f"[{i}/{len(topics)}] Generating: {topic}...")
            post = automation.generate_single_blog(topic)
            
            if post:
                print(f"   ✅ Published: {post.title}")
                print(f"   📊 {post.word_count} words")
                print(f"   🔗 /blog/{post.slug}\n")
            else:
                print(f"   ❌ Failed to generate\n")

def generate_mixed_topics(count=5):
    """Generate blogs from mixed categories"""
    import random
    
    with app.app_context():
        automation = AutomationService()
        
        # Get random topics from different categories
        all_topics = []
        for category, topics in TOPIC_LISTS.items():
            all_topics.extend([(topic, category) for topic in topics])
        
        selected = random.sample(all_topics, min(count, len(all_topics)))
        
        print(f"📝 Generating {len(selected)} diverse blog posts\n")
        
        for i, (topic, category) in enumerate(selected, 1):
            print(f"[{i}/{len(selected)}] {category.upper()}: {topic}...")
            post = automation.generate_single_blog(topic)
            
            if post:
                print(f"   ✅ Published: {post.title}")
                print(f"   📊 {post.word_count} words\n")
            else:
                print(f"   ❌ Failed\n")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python generate_custom_topics.py <category> [count]")
        print("  python generate_custom_topics.py mixed [count]")
        print("\nAvailable categories:")
        for cat in TOPIC_LISTS.keys():
            print(f"  - {cat}")
        print("\nExample:")
        print("  python generate_custom_topics.py technology 3")
        print("  python generate_custom_topics.py mixed 5")
        sys.exit(1)
    
    category = sys.argv[1].lower()
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    
    if category == 'mixed':
        generate_mixed_topics(count)
    else:
        generate_from_category(category, count)
