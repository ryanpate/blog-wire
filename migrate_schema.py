#!/usr/bin/env python3
"""
Migration script to update PostgreSQL schema for longer meta fields
Run this once after deploying the updated models.py
"""

from app import app, db
from sqlalchemy import text

def migrate_schema():
    """Update blog_posts table to support longer meta fields"""
    with app.app_context():
        try:
            print("🔄 Updating database schema...")

            # Alter the columns to increase length
            db.session.execute(text('ALTER TABLE blog_posts ALTER COLUMN meta_description TYPE VARCHAR(500)'))
            print("✅ Updated meta_description to VARCHAR(500)")

            db.session.execute(text('ALTER TABLE blog_posts ALTER COLUMN meta_keywords TYPE VARCHAR(500)'))
            print("✅ Updated meta_keywords to VARCHAR(500)")

            db.session.commit()
            print("\n✅ Database schema migration completed successfully!")

        except Exception as e:
            db.session.rollback()
            print(f"❌ Migration failed: {e}")
            raise

if __name__ == '__main__':
    migrate_schema()
