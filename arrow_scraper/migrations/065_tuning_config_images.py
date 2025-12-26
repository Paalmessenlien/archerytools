#!/usr/bin/env python3
"""
Migration 065: Add image support to bow tuning configs

Adds an image_url column to bow_tuning_configs table to store
a photo of the setup configuration.
"""

import sqlite3
import sys
import os

def get_migration_info():
    """Return migration metadata"""
    return {
        'version': 65,
        'description': 'Add image support to bow tuning configs',
        'author': 'System',
        'created_at': '2025-11-29',
        'target_database': 'arrow',
        'dependencies': ['064'],
        'environments': ['all']
    }

def migrate_up(cursor):
    """Add image_url column to bow_tuning_configs"""
    conn = cursor.connection

    print("Adding image_url column to bow_tuning_configs...")

    # Check if column already exists
    cursor.execute("PRAGMA table_info(bow_tuning_configs)")
    columns = [col[1] for col in cursor.fetchall()]

    if 'image_url' not in columns:
        cursor.execute("""
            ALTER TABLE bow_tuning_configs
            ADD COLUMN image_url TEXT
        """)
        print("✅ Added image_url column to bow_tuning_configs")
    else:
        print("ℹ️ image_url column already exists")

    conn.commit()
    print("✅ Migration 065 completed successfully")

    return True

def migrate_down(cursor):
    """Remove image_url column from bow_tuning_configs"""
    conn = cursor.connection

    print("Removing image_url column from bow_tuning_configs...")

    # SQLite doesn't support DROP COLUMN directly in older versions
    # Need to recreate the table without the column
    cursor.execute("""
        CREATE TABLE bow_tuning_configs_backup AS
        SELECT id, bow_setup_id, user_id, name, description, is_active, created_at, updated_at
        FROM bow_tuning_configs
    """)

    cursor.execute("DROP TABLE bow_tuning_configs")

    cursor.execute("""
        CREATE TABLE bow_tuning_configs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bow_setup_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            is_active BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (bow_setup_id) REFERENCES bow_setups(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    cursor.execute("""
        INSERT INTO bow_tuning_configs (id, bow_setup_id, user_id, name, description, is_active, created_at, updated_at)
        SELECT id, bow_setup_id, user_id, name, description, is_active, created_at, updated_at
        FROM bow_tuning_configs_backup
    """)

    cursor.execute("DROP TABLE bow_tuning_configs_backup")

    conn.commit()
    print("✅ image_url column removed from bow_tuning_configs")

    return True

# Allow running directly for testing
if __name__ == '__main__':
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
    cursor.execute("PRAGMA foreign_keys = ON")

    try:
        migrate_up(cursor)
        print("✅ Migration completed successfully")
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()
