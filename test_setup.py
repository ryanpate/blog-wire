#!/usr/bin/env python3
"""
Test script to verify Blog Wire setup
Run this after adding your OPENAI_API_KEY to .env
"""

from app import app, db
from config import Config
import sys

def test_setup():
    """Test the Blog Wire setup"""

    print("=" * 60)
    print("Blog Wire Setup Test")
    print("=" * 60)
    print()

    # Test 1: Check configuration
    print("1. Testing configuration...")
    if not Config.OPENAI_API_KEY or Config.OPENAI_API_KEY == 'your_openai_api_key_here':
        print("   ❌ OPENAI_API_KEY not set in .env file")
        print("   → Get your key from: https://platform.openai.com/api-keys")
        print("   → Edit .env and add: OPENAI_API_KEY=sk-your-key-here")
        return False
    else:
        print("   ✅ OPENAI_API_KEY configured")

    if Config.SECRET_KEY == 'your_secret_key_here' or Config.SECRET_KEY == 'dev-secret-key-change-in-production':
        print("   ⚠️  SECRET_KEY using default value (change for production)")
    else:
        print("   ✅ SECRET_KEY configured")

    print(f"   ✅ Blog Name: {Config.BLOG_NAME}")
    print(f"   ✅ Posts per day: {Config.POSTS_PER_DAY}")
    print()

    # Test 2: Check database
    print("2. Testing database connection...")
    try:
        with app.app_context():
            from models import BlogPost, TrendingTopic, AffiliateLink

            post_count = BlogPost.query.count()
            topic_count = TrendingTopic.query.count()
            link_count = AffiliateLink.query.count()

            print(f"   ✅ Database connected")
            print(f"   ℹ️  Current data: {post_count} posts, {topic_count} topics, {link_count} affiliate links")
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return False
    print()

    # Test 3: Check OpenAI API
    print("3. Testing OpenAI API connection...")
    try:
        from openai import OpenAI
        client = OpenAI(api_key=Config.OPENAI_API_KEY)

        # Simple test call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'API working' if you can read this"}],
            max_tokens=10
        )

        result = response.choices[0].message.content
        print(f"   ✅ OpenAI API connected successfully")
        print(f"   ℹ️  Test response: {result}")
    except Exception as e:
        print(f"   ❌ OpenAI API error: {e}")
        print("   → Check your API key is valid and has credits")
        return False
    print()

    # Test 4: Check services
    print("4. Testing services...")
    try:
        from services.trends_service import TrendsService
        from services.blog_generator import BlogGenerator
        from services.affiliate_service import AffiliateService
        from services.automation_service import AutomationService

        print("   ✅ TrendsService loaded")
        print("   ✅ BlogGenerator loaded")
        print("   ✅ AffiliateService loaded")
        print("   ✅ AutomationService loaded")
    except Exception as e:
        print(f"   ❌ Service error: {e}")
        return False
    print()

    # Success!
    print("=" * 60)
    print("✅ All tests passed! Your Blog Wire setup is ready!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Start the web server: python app.py")
    print("  2. Visit: http://localhost:5000")
    print("  3. Generate a test blog: curl -X POST http://localhost:5000/api/generate-blog -H 'Content-Type: application/json' -d '{\"keyword\": \"test topic\"}'")
    print("  4. Start automation: python scheduler.py")
    print()

    return True

if __name__ == '__main__':
    success = test_setup()
    sys.exit(0 if success else 1)
