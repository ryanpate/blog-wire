#!/usr/bin/env python3
"""
Import blog posts from JSON file into database
"""

from app import app, db
from models import BlogPost
from datetime import datetime
import json

def import_posts():
    with app.app_context():
        try:
            with open('blog_posts_export.json', 'r') as f:
                posts_data = json.load(f)

            print(f"Found {len(posts_data)} posts to import")

            imported_count = 0
            skipped_count = 0

            for post_data in posts_data:
                # Check if post with this slug already exists
                existing = BlogPost.query.filter_by(slug=post_data['slug']).first()

                if existing:
                    print(f"  ⏭️  Skipping: {post_data['title']} (already exists)")
                    skipped_count += 1
                    continue

                # Create new post
                post = BlogPost(
                    title=post_data['title'],
                    slug=post_data['slug'],
                    content=post_data['content'],
                    excerpt=post_data['excerpt'],
                    meta_description=post_data['meta_description'],
                    meta_keywords=post_data['meta_keywords'],
                    word_count=post_data['word_count'],
                    status=post_data['status'],
                    published_at=datetime.fromisoformat(post_data['published_at']) if post_data['published_at'] else None
                )

                db.session.add(post)
                print(f"  ✅ Importing: {post_data['title']}")
                imported_count += 1

            db.session.commit()

            print(f"\n{'=' * 60}")
            print(f"✅ Successfully imported {imported_count} posts")
            print(f"⏭️  Skipped {skipped_count} existing posts")
            print(f"{'=' * 60}")

        except FileNotFoundError:
            print("❌ Error: blog_posts_export.json not found")
            print("Run export_posts.py first to create the export file")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error importing posts: {e}")

if __name__ == '__main__':
    import_posts()
