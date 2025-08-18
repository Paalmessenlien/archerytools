#!/usr/bin/env python3
"""
Migration 031: Add User Profile Columns

Adds missing user profile columns that are expected by the API:
- skill_level: User's archery experience level (beginner, intermediate, advanced)
- shooting_style: JSON array of shooting styles (target, hunting, traditional, 3d)
- preferred_manufacturers: JSON array of preferred arrow manufacturers
- notes: User's personal notes

Author: Claude
Date: 2025-08-18
"""

import sqlite3
import json
import sys
import os

# Add parent directory to path so we can import from arrow_scraper
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from database_migration_manager import BaseMigration

class Migration(BaseMigration):
    def __init__(self):
        super().__init__()
        self.version = "031"
        self.description = "Add user profile columns (skill_level, shooting_style, preferred_manufacturers, notes)"
        self.dependencies = ["030"]  # Depends on draw length architecture fix
    
    def up(self, db_path, environment='development'):
        """Add missing user profile columns"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            print(f"🔄 Adding user profile columns to database: {db_path}")
            
            # Get current users table schema
            cursor.execute("PRAGMA table_info(users)")
            columns = {row[1]: row[2] for row in cursor.fetchall()}
            print(f"📋 Current users table columns: {list(columns.keys())}")
            
            added_count = 0
            
            # Add skill_level column
            if 'skill_level' not in columns:
                try:
                    cursor.execute("ALTER TABLE users ADD COLUMN skill_level TEXT DEFAULT NULL")
                    print("✅ Added users.skill_level column")
                    added_count += 1
                except sqlite3.OperationalError as e:
                    print(f"⚠️  Warning adding skill_level: {e}")
            else:
                print("✅ skill_level column already exists")
            
            # Add shooting_style column (JSON array)
            if 'shooting_style' not in columns:
                try:
                    cursor.execute("ALTER TABLE users ADD COLUMN shooting_style TEXT DEFAULT NULL")
                    print("✅ Added users.shooting_style column")
                    added_count += 1
                except sqlite3.OperationalError as e:
                    print(f"⚠️  Warning adding shooting_style: {e}")
            else:
                print("✅ shooting_style column already exists")
            
            # Add preferred_manufacturers column (JSON array)
            if 'preferred_manufacturers' not in columns:
                try:
                    cursor.execute("ALTER TABLE users ADD COLUMN preferred_manufacturers TEXT DEFAULT NULL")
                    print("✅ Added users.preferred_manufacturers column")
                    added_count += 1
                except sqlite3.OperationalError as e:
                    print(f"⚠️  Warning adding preferred_manufacturers: {e}")
            else:
                print("✅ preferred_manufacturers column already exists")
            
            # Add notes column
            if 'notes' not in columns:
                try:
                    cursor.execute("ALTER TABLE users ADD COLUMN notes TEXT DEFAULT NULL")
                    print("✅ Added users.notes column")
                    added_count += 1
                except sqlite3.OperationalError as e:
                    print(f"⚠️  Warning adding notes: {e}")
            else:
                print("✅ notes column already exists")
            
            conn.commit()
            
            print(f"✅ Migration 031 completed successfully. Added {added_count} new columns.")
            return True
            
        except Exception as e:
            print(f"❌ Migration 031 failed: {str(e)}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def down(self, db_path, environment='development'):
        """Remove user profile columns (SQLite doesn't support DROP COLUMN for older versions)"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            print(f"🔄 Rolling back user profile columns from database: {db_path}")
            
            # SQLite doesn't support DROP COLUMN in older versions
            # So we'll recreate the table without these columns
            
            # Get current data
            cursor.execute("""
                SELECT id, google_id, email, name, profile_picture_url, created_at, 
                       is_admin, last_login, updated_at, picture, user_draw_length
                FROM users
            """)
            existing_data = cursor.fetchall()
            
            # Drop existing table
            cursor.execute("DROP TABLE users")
            
            # Recreate table without profile columns
            cursor.execute("""
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    google_id TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    name TEXT,
                    profile_picture_url TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    is_admin BOOLEAN DEFAULT 0,
                    last_login TIMESTAMP,
                    updated_at TIMESTAMP,
                    picture TEXT,
                    user_draw_length REAL DEFAULT 28.0
                )
            """)
            
            # Restore existing data
            if existing_data:
                cursor.executemany("""
                    INSERT INTO users (id, google_id, email, name, profile_picture_url, created_at,
                                     is_admin, last_login, updated_at, picture, user_draw_length)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, existing_data)
            
            # Recreate index
            cursor.execute("CREATE INDEX idx_users_user_draw_length ON users(user_draw_length)")
            
            conn.commit()
            print("✅ Migration 031 rollback completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Migration 031 rollback failed: {str(e)}")
            conn.rollback()
            return False
        finally:
            conn.close()

if __name__ == "__main__":
    migration = Migration()
    
    # Test database path
    import os
    db_path = os.path.join(os.path.dirname(__file__), '..', 'databases', 'arrow_database.db')
    
    print(f"Running Migration 031 on: {db_path}")
    success = migration.up(db_path)
    
    if success:
        print("✅ Migration 031 applied successfully!")
    else:
        print("❌ Migration 031 failed!")