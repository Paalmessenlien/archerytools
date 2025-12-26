#!/usr/bin/env python3
"""
Migration 063: Add Default Draw Length to Users Table

Adds a default_draw_length column to the users table.
This is a user preference used as a default when creating new bow setups,
NOT for calculations (which use bow_setups.draw_length).

This follows the unified draw length architecture from migration 045:
- bow_setups.draw_length = source of truth for all calculations
- users.default_draw_length = user preference for creating new setups
"""

import sqlite3
import sys
import os
from pathlib import Path

def get_migration_info():
    """Return migration metadata"""
    return {
        'version': 63,
        'description': 'Add default_draw_length column to users table for new setup defaults',
        'author': 'System',
        'created_at': '2025-11-29',
        'target_database': 'arrow',
        'dependencies': ['062'],
        'environments': ['all']
    }

def migrate_up(cursor):
    """Add default_draw_length column to users table"""
    conn = cursor.connection

    print("Adding default_draw_length column to users table...")

    # Check if column already exists
    cursor.execute("PRAGMA table_info(users)")
    columns = {col[1] for col in cursor.fetchall()}

    if 'default_draw_length' not in columns:
        cursor.execute("""
            ALTER TABLE users ADD COLUMN default_draw_length REAL DEFAULT 28.0
        """)
        conn.commit()
        print("✅ Added default_draw_length column to users table")
    else:
        print("✅ default_draw_length column already exists")

    return True

def migrate_down(cursor):
    """Remove default_draw_length column from users table"""
    conn = cursor.connection

    print("Note: SQLite does not support DROP COLUMN directly.")
    print("The default_draw_length column will remain but can be ignored.")

    return True

# Allow running directly for testing
if __name__ == '__main__':
    # Find database
    db_paths = [
        'databases/arrow_database.db',
        '../databases/arrow_database.db',
        'arrow_scraper/databases/arrow_database.db'
    ]

    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break

    if not db_path:
        print("❌ Could not find database")
        sys.exit(1)

    print(f"Using database: {db_path}")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        migrate_up(cursor)
        print("✅ Migration completed successfully")
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()
