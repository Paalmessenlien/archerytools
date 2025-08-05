#!/usr/bin/env python3
"""
Database migration script to add missing columns to spine_specifications table.
This fixes the admin arrow editing functionality by adding columns expected by the frontend.
"""

import sqlite3
import os
import sys

def get_db_path():
    """Get the correct database path based on environment."""
    # Check for Docker environment path first
    docker_path = '/app/arrow_data/arrow_database.db'
    if os.path.exists(docker_path):
        return docker_path
    
    # Fallback to local development path
    local_path = 'arrow_database.db'
    if os.path.exists(local_path):
        return local_path
    
    raise FileNotFoundError("Could not find arrow_database.db in any expected location")

def check_column_exists(cursor, table_name, column_name):
    """Check if a column exists in the table."""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns

def migrate_spine_specifications():
    """Add missing columns to spine_specifications table."""
    db_path = get_db_path()
    print(f"Using database: {db_path}")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # List of columns to add with their definitions
        new_columns = [
            ('length_options', 'TEXT'),
            ('wall_thickness', 'REAL'),
            ('insert_weight_range', 'TEXT'),
            ('nock_size', 'TEXT'),
            ('notes', 'TEXT'),
            ('straightness_tolerance', 'TEXT'),
            ('weight_tolerance', 'TEXT')
        ]
        
        print("Checking spine_specifications table schema...")
        
        # Check current columns
        cursor.execute("PRAGMA table_info(spine_specifications)")
        existing_columns = [row[1] for row in cursor.fetchall()]
        print(f"Existing columns: {existing_columns}")
        
        columns_added = 0
        
        # Add missing columns
        for column_name, column_type in new_columns:
            if not check_column_exists(cursor, 'spine_specifications', column_name):
                print(f"Adding column: {column_name} ({column_type})")
                cursor.execute(f"ALTER TABLE spine_specifications ADD COLUMN {column_name} {column_type}")
                columns_added += 1
            else:
                print(f"Column {column_name} already exists")
        
        # Commit the changes
        conn.commit()
        
        print(f"\nMigration completed successfully!")
        print(f"Added {columns_added} new columns to spine_specifications table")
        
        # Verify the new schema
        print("\nUpdated schema:")
        cursor.execute("PRAGMA table_info(spine_specifications)")
        for row in cursor.fetchall():
            print(f"  {row[1]} ({row[2]})")
            
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    print("Spine Specifications Table Migration")
    print("=" * 40)
    migrate_spine_specifications()