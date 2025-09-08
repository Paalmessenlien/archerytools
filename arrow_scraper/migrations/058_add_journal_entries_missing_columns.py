#!/usr/bin/env python3
"""
Migration 058: Add missing columns to journal_entries table
- Adds arrow_id column for tuning session journal entries
- Adds is_favorite column for favoriting journal entries
- Required for paper tuning session completion functionality
"""

import sqlite3
import sys
import os
from datetime import datetime

def get_migration_info():
    """Return migration metadata"""
    return {
        'version': 58,
        'description': 'Add arrow_id and is_favorite columns to journal_entries table',
        'author': 'System',
        'created_at': '2025-09-06',
        'target_database': 'arrow',
        'dependencies': [],
        'environments': ['all']
    }

def migrate_up(cursor):
    """Apply migration 058: Add missing columns to journal_entries table"""
    conn = cursor.connection
    
    try:
        print("🔧 Migration 058: Adding missing columns to journal_entries table...")
        
        # Check current columns in journal_entries table
        cursor.execute("PRAGMA table_info(journal_entries)")
        columns = [row[1] for row in cursor.fetchall()]
        
        # Add arrow_id column if it doesn't exist
        if 'arrow_id' not in columns:
            cursor.execute("ALTER TABLE journal_entries ADD COLUMN arrow_id INTEGER")
            print("   ✅ Added arrow_id column to journal_entries table")
            
            # Add foreign key constraint through index (SQLite doesn't support adding FK constraints to existing tables)
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_journal_entries_arrow_id
                ON journal_entries(arrow_id)
            ''')
            print("   ✅ Added arrow_id index for referential integrity")
        else:
            print("   ℹ️ arrow_id column already exists in journal_entries table")
        
        # Add is_favorite column if it doesn't exist
        if 'is_favorite' not in columns:
            cursor.execute("ALTER TABLE journal_entries ADD COLUMN is_favorite BOOLEAN DEFAULT 0")
            print("   ✅ Added is_favorite column to journal_entries table")
        else:
            print("   ℹ️ is_favorite column already exists in journal_entries table")
        
        conn.commit()
        print("🎯 Migration 058 completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration 058 failed: {e}")
        conn.rollback()
        return False

def migrate_down(cursor):
    """Rollback migration 058: Remove added columns"""
    conn = cursor.connection
    
    try:
        print("🔄 Rolling back Migration 058...")
        
        # Note: SQLite doesn't support DROP COLUMN directly
        # Would need to recreate table to remove columns
        print("   ℹ️ SQLite doesn't support DROP COLUMN - arrow_id and is_favorite columns preserved")
        
        # Drop the index we created
        cursor.execute("DROP INDEX IF EXISTS idx_journal_entries_arrow_id")
        print("   ✅ Dropped arrow_id index")
        
        conn.commit()
        print("🔄 Migration 058 rollback completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration 058 rollback failed: {e}")
        conn.rollback()
        return False

if __name__ == "__main__":
    # Test the migration - try multiple database paths
    possible_paths = [
        '/app/databases/arrow_database.db',  # Docker production
        '/root/archerytools/databases/arrow_database.db',  # Production host
        os.path.join(os.path.dirname(__file__), '..', 'databases', 'arrow_database.db'),  # Development
        'databases/arrow_database.db',  # Relative path
        'arrow_database.db'  # Current directory
    ]
    
    db_path = None
    for path in possible_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print(f"❌ Database not found in any location: {possible_paths}")
        sys.exit(1)
    
    print(f"📁 Using database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    
    try:
        if len(sys.argv) > 1 and sys.argv[1] == 'down':
            success = migrate_down(conn.cursor())
        else:
            success = migrate_up(conn.cursor())
        
        if success:
            print("✅ Migration test completed successfully")
        else:
            print("❌ Migration test failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Migration test error: {e}")
        sys.exit(1)
    finally:
        conn.close()