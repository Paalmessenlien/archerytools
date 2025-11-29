#!/usr/bin/env python3
"""
Migration 062: Create Bow Types Table

Creates the bow_types table to store bow type metadata including display names,
descriptions, and configuration templates. This allows admins to customize
bow type display names and add new custom bow types.
"""

import sqlite3
import sys
import os
from pathlib import Path
from datetime import datetime

def get_migration_info():
    """Return migration metadata"""
    return {
        'version': 62,
        'description': 'Create bow_types table for customizable bow type metadata',
        'author': 'System',
        'created_at': '2025-11-29',
        'target_database': 'arrow',
        'dependencies': ['061'],
        'environments': ['all']
    }

def migrate_up(cursor):
    """Create bow_types table with default bow types"""
    conn = cursor.connection

    print("Creating bow_types table...")

    # Create bow_types table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bow_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            display_name TEXT NOT NULL,
            description TEXT,
            icon TEXT DEFAULT 'fas fa-bullseye',
            is_default BOOLEAN DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            sort_order INTEGER DEFAULT 100,
            config_template TEXT,
            created_by INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
    """)

    # Create indexes
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_bow_types_name ON bow_types(name)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_bow_types_active ON bow_types(is_active)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_bow_types_sort ON bow_types(sort_order)
    """)

    print("✅ Created bow_types table with indexes")

    # Insert default bow types with metadata
    default_bow_types = [
        ('compound', 'Compound', 'Modern mechanical bow with cams and cables for let-off', 'fas fa-cogs', True, True, 1, 'compound'),
        ('recurve', 'Recurve', 'Traditional Olympic-style bow with curved limbs', 'fas fa-archway', True, True, 2, 'recurve'),
        ('barebow', 'Barebow', 'Recurve bow without sights or stabilizers - instinctive shooting', 'fas fa-hand-paper', True, True, 3, 'barebow'),
        ('longbow', 'Longbow', 'Traditional straight-limbed bow - minimal equipment', 'fas fa-ruler-vertical', True, True, 4, 'longbow'),
        ('traditional', 'Traditional', 'Traditional recurve or hybrid bow - classic archery', 'fas fa-feather-alt', True, True, 5, 'traditional'),
    ]

    for name, display_name, description, icon, is_default, is_active, sort_order, config_template in default_bow_types:
        cursor.execute("""
            INSERT OR IGNORE INTO bow_types
            (name, display_name, description, icon, is_default, is_active, sort_order, config_template)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, display_name, description, icon, is_default, is_active, sort_order, config_template))

    conn.commit()
    print(f"✅ Inserted {len(default_bow_types)} default bow types")

    # Migrate any existing custom bow types from bow_type_equipment_rules
    cursor.execute("""
        SELECT DISTINCT bow_type FROM bow_type_equipment_rules
        WHERE bow_type NOT IN ('compound', 'recurve', 'barebow', 'longbow', 'traditional')
    """)
    custom_types = cursor.fetchall()

    if custom_types:
        for row in custom_types:
            bow_type = row[0]
            display_name = bow_type.replace('_', ' ').replace('-', ' ').title()
            cursor.execute("""
                INSERT OR IGNORE INTO bow_types
                (name, display_name, description, icon, is_default, is_active, sort_order, config_template)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (bow_type, display_name, f'Custom bow type: {display_name}', 'fas fa-bullseye', False, True, 100, 'traditional'))

        conn.commit()
        print(f"✅ Migrated {len(custom_types)} custom bow types from equipment rules")

    return True

def migrate_down(cursor):
    """Remove bow_types table"""
    conn = cursor.connection

    print("Dropping bow_types table...")

    cursor.execute("DROP TABLE IF EXISTS bow_types")
    cursor.execute("DROP INDEX IF EXISTS idx_bow_types_name")
    cursor.execute("DROP INDEX IF EXISTS idx_bow_types_active")
    cursor.execute("DROP INDEX IF EXISTS idx_bow_types_sort")

    conn.commit()
    print("✅ Dropped bow_types table")

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
