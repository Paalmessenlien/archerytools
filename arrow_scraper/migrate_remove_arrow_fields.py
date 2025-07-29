#!/usr/bin/env python3
"""
Database migration to remove arrow_length and point_weight columns from bow_setups table.
These fields are now associated with individual arrows rather than bow setups.
"""

import sqlite3
import os
import sys
from user_database import UserDatabase

def migrate_bow_setups_table():
    """Remove arrow_length and point_weight columns from bow_setups table"""
    print("🏹 Migrating bow_setups table - removing arrow-specific fields")
    
    try:
        # Get user database connection
        user_db = UserDatabase()
        conn = user_db.get_connection()
        cursor = conn.cursor()
        
        # Check if columns exist first
        cursor.execute("PRAGMA table_info(bow_setups)")
        columns = [column[1] for column in cursor.fetchall()]
        
        print(f"Current columns: {columns}")
        
        if 'arrow_length' not in columns and 'point_weight' not in columns:
            print("✅ Migration already completed - arrow_length and point_weight columns not found")
            conn.close()
            return
        
        # SQLite doesn't support DROP COLUMN directly, so we need to recreate the table
        print("📦 Creating new table structure without arrow-specific fields...")
        
        # Create new table without arrow_length and point_weight
        cursor.execute('''
            CREATE TABLE bow_setups_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                bow_type TEXT NOT NULL,
                draw_weight REAL NOT NULL,
                draw_length REAL,
                nock_weight REAL,
                fletching_weight REAL,
                insert_weight REAL,
                description TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Copy data from old table (excluding arrow_length and point_weight columns)
        print("📋 Copying existing bow setup data...")
        cursor.execute('''
            INSERT INTO bow_setups_new (id, user_id, name, bow_type, draw_weight, draw_length, nock_weight, fletching_weight, insert_weight, description, created_at)
            SELECT id, user_id, name, bow_type, draw_weight, draw_length, 
                   COALESCE(nock_weight, NULL), COALESCE(fletching_weight, NULL), 
                   COALESCE(insert_weight, NULL), description, created_at
            FROM bow_setups
        ''')
        
        # Drop old table and rename new one
        print("🔄 Replacing old table with new structure...")
        cursor.execute('DROP TABLE bow_setups')
        cursor.execute('ALTER TABLE bow_setups_new RENAME TO bow_setups')
        
        # Commit changes
        conn.commit()
        
        # Verify migration
        cursor.execute("PRAGMA table_info(bow_setups)")
        new_columns = [column[1] for column in cursor.fetchall()]
        
        print(f"✅ Migration completed successfully!")
        print(f"New columns: {new_columns}")
        print(f"Removed: arrow_length, point_weight")
        
        # Count bow setups
        cursor.execute("SELECT COUNT(*) FROM bow_setups")
        count = cursor.fetchone()[0]
        print(f"📊 {count} bow setups migrated")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 Starting bow_setups table migration...")
    migrate_bow_setups_table()
    print("🎯 Migration complete - arrow-specific fields removed from bow setups")
    print("💡 Point weight and arrow length are now managed per arrow when adding arrows to setups")