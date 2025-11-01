#!/usr/bin/env python3
"""
Export blog posts to JSON file
"""

from app import app
from models import BlogPost
import json

def export_posts():
    with app.app_context():
        posts = BlogPost.query.order_by(BlogPost.id).all()

        posts_data = []
        for post in posts:
            posts_data.append({
                'title': post.title,
                'slug': post.slug,
                'content': post.content,
                'excerpt': post.excerpt,
                'meta_description': post.meta_description,
                'meta_keywords': post.meta_keywords,
                'word_count': post.word_count,
                'status': post.status,
                'published_at': post.published_at.isoformat() if post.published_at else None
            })

        with open('blog_posts_export.json', 'w') as f:
            json.dump(posts_data, f, indent=2)

        print(f"✅ Exported {len(posts_data)} posts to blog_posts_export.json")

if __name__ == '__main__':
    export_posts()
