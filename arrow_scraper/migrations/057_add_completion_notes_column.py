#!/usr/bin/env python3
"""
Migration 057: Add completion_notes column to guide_sessions table
- Adds completion_notes column for storing session completion summary
- Required for paper tuning session completion functionality
"""

import sqlite3
import sys
import os
from datetime import datetime

def get_migration_info():
    """Return migration metadata"""
    return {
        'version': 57,
        'description': 'Add completion_notes column to guide_sessions table',
        'author': 'System',
        'created_at': '2025-09-06',
        'target_database': 'arrow',
        'dependencies': [],
        'environments': ['all']
    }

def migrate_up(cursor):
    """Apply migration 057: Add completion_notes column"""
    conn = cursor.connection
    
    try:
        print("🔧 Migration 057: Adding completion_notes column to guide_sessions table...")
        
        # Check if completion_notes column exists
        cursor.execute("PRAGMA table_info(guide_sessions)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'completion_notes' not in columns:
            cursor.execute("ALTER TABLE guide_sessions ADD COLUMN completion_notes TEXT")
            print("   ✅ Added completion_notes column to guide_sessions table")
        else:
            print("   ℹ️ completion_notes column already exists in guide_sessions table")
        
        conn.commit()
        print("🎯 Migration 057 completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration 057 failed: {e}")
        conn.rollback()
        return False

def migrate_down(cursor):
    """Rollback migration 057: Remove completion_notes column"""
    conn = cursor.connection
    
    try:
        print("🔄 Rolling back Migration 057...")
        
        # Note: SQLite doesn't support DROP COLUMN directly
        # Would need to recreate table to remove column
        print("   ℹ️ SQLite doesn't support DROP COLUMN - completion_notes column preserved")
        
        conn.commit()
        print("🔄 Migration 057 rollback completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration 057 rollback failed: {e}")
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