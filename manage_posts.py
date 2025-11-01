#!/usr/bin/env python3
"""
Blog Post Management Script
Delete or manage blog posts in your Blog Wire database
"""

from app import app, db
from models import BlogPost
import sys

def list_all_posts():
    """List all blog posts with their IDs"""
    with app.app_context():
        posts = BlogPost.query.order_by(BlogPost.id).all()

        if not posts:
            print("No posts found in database.")
            return

        print("\n" + "=" * 80)
        print("ALL BLOG POSTS")
        print("=" * 80)

        for post in posts:
            print(f"\nID: {post.id}")
            print(f"Title: {post.title}")
            print(f"Slug: {post.slug}")
            print(f"Word Count: {post.word_count}")
            print(f"Status: {post.status}")
            print(f"Published: {post.published_at}")
            print(f"URL: /blog/{post.slug}")
            print("-" * 80)

        print(f"\nTotal posts: {len(posts)}")

def delete_post_by_id(post_id):
    """Delete a blog post by ID"""
    with app.app_context():
        post = BlogPost.query.get(post_id)

        if not post:
            print(f"❌ Post with ID {post_id} not found.")
            return False

        print(f"\nDeleting post:")
        print(f"  ID: {post.id}")
        print(f"  Title: {post.title}")
        print(f"  Word Count: {post.word_count}")

        db.session.delete(post)
        db.session.commit()

        print(f"✅ Post ID {post_id} deleted successfully!")
        return True

def delete_empty_posts():
    """Delete all posts with 0 word count"""
    with app.app_context():
        empty_posts = BlogPost.query.filter_by(word_count=0).all()

        if not empty_posts:
            print("No empty posts found.")
            return

        print(f"\nFound {len(empty_posts)} empty posts:")
        for post in empty_posts:
            print(f"  - ID {post.id}: {post.title}")

        confirm = input(f"\nDelete all {len(empty_posts)} empty posts? (yes/no): ")

        if confirm.lower() in ['yes', 'y']:
            for post in empty_posts:
                db.session.delete(post)
            db.session.commit()
            print(f"✅ Deleted {len(empty_posts)} empty posts!")
        else:
            print("❌ Deletion cancelled.")

def delete_all_posts():
    """Delete ALL blog posts"""
    with app.app_context():
        total = BlogPost.query.count()

        if total == 0:
            print("No posts to delete.")
            return

        print(f"\n⚠️  WARNING: This will delete ALL {total} blog posts!")
        confirm = input("Are you absolutely sure? Type 'DELETE ALL' to confirm: ")

        if confirm == 'DELETE ALL':
            BlogPost.query.delete()
            db.session.commit()
            print(f"✅ Deleted all {total} posts!")
        else:
            print("❌ Deletion cancelled.")

def main():
    if len(sys.argv) < 2:
        print("\nBlog Wire - Post Management")
        print("=" * 50)
        print("\nUsage:")
        print("  python manage_posts.py list")
        print("  python manage_posts.py delete <post_id>")
        print("  python manage_posts.py delete-empty")
        print("  python manage_posts.py delete-all")
        print("\nExamples:")
        print("  python manage_posts.py list")
        print("  python manage_posts.py delete 5")
        print("  python manage_posts.py delete-empty")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == 'list':
        list_all_posts()

    elif command == 'delete':
        if len(sys.argv) < 3:
            print("❌ Error: Please provide a post ID to delete")
            print("Usage: python manage_posts.py delete <post_id>")
            sys.exit(1)

        try:
            post_id = int(sys.argv[2])
            delete_post_by_id(post_id)
        except ValueError:
            print("❌ Error: Post ID must be a number")
            sys.exit(1)

    elif command == 'delete-empty':
        delete_empty_posts()

    elif command == 'delete-all':
        delete_all_posts()

    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: list, delete, delete-empty, delete-all")
        sys.exit(1)

if __name__ == '__main__':
    main()
