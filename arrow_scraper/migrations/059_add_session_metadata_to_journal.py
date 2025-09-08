#!/usr/bin/env python3
"""
Migration 059: Add session metadata to journal_entries table
- Adds session_metadata JSON column for storing tuning session data
- Adds session_type column (paper/bareshaft/walkback/general) 
- Adds session_quality_score column for session performance tracking
- Required for enhanced journal entry viewing and session continuity features
"""

import sqlite3
import sys
import os
from datetime import datetime

def get_migration_info():
    """Return migration metadata"""
    return {
        'version': 59,
        'description': 'Add session metadata, type, and quality score to journal_entries table',
        'author': 'System',
        'created_at': '2025-09-07',
        'target_database': 'arrow',
        'dependencies': [],  # No dependencies
        'environments': ['all']
    }

def migrate_up(cursor):
    """Apply migration 059: Add session metadata columns to journal_entries table"""
    conn = cursor.connection
    
    try:
        print("🔧 Migration 059: Adding session metadata columns to journal_entries table...")
        
        # Check current columns in journal_entries table
        cursor.execute("PRAGMA table_info(journal_entries)")
        columns = [row[1] for row in cursor.fetchall()]
        
        # Add session_metadata column if it doesn't exist
        if 'session_metadata' not in columns:
            cursor.execute("ALTER TABLE journal_entries ADD COLUMN session_metadata TEXT")  # JSON as TEXT in SQLite
            print("   ✅ Added session_metadata column to journal_entries table")
        else:
            print("   ℹ️ session_metadata column already exists in journal_entries table")
        
        # Add session_type column if it doesn't exist
        if 'session_type' not in columns:
            cursor.execute("ALTER TABLE journal_entries ADD COLUMN session_type TEXT DEFAULT 'general'")
            print("   ✅ Added session_type column to journal_entries table")
            
            # Create index for efficient session type queries
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_journal_entries_session_type
                ON journal_entries(session_type)
            ''')
            print("   ✅ Added session_type index for efficient filtering")
        else:
            print("   ℹ️ session_type column already exists in journal_entries table")
        
        # Add session_quality_score column if it doesn't exist  
        if 'session_quality_score' not in columns:
            cursor.execute("ALTER TABLE journal_entries ADD COLUMN session_quality_score REAL")  # 0.0-100.0 score
            print("   ✅ Added session_quality_score column to journal_entries table")
            
            # Create index for efficient quality-based queries
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_journal_entries_quality_score
                ON journal_entries(session_quality_score)
            ''')
            print("   ✅ Added session_quality_score index for performance tracking")
        else:
            print("   ℹ️ session_quality_score column already exists in journal_entries table")
            
        # Create compound index for efficient session queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_journal_entries_session_compound
            ON journal_entries(session_type, session_quality_score, created_at DESC)
        ''')
        print("   ✅ Added compound index for efficient session-based queries")
        
        conn.commit()
        print("🎯 Migration 059 completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration 059 failed: {e}")
        conn.rollback()
        return False

def migrate_down(cursor):
    """Rollback migration 059: Remove added columns and indexes"""
    conn = cursor.connection
    
    try:
        print("🔄 Rolling back Migration 059...")
        
        # Drop the indexes we created
        cursor.execute("DROP INDEX IF EXISTS idx_journal_entries_session_type")
        cursor.execute("DROP INDEX IF EXISTS idx_journal_entries_quality_score") 
        cursor.execute("DROP INDEX IF EXISTS idx_journal_entries_session_compound")
        print("   ✅ Dropped session-related indexes")
        
        # Note: SQLite doesn't support DROP COLUMN directly
        # Would need to recreate table to remove columns
        print("   ℹ️ SQLite doesn't support DROP COLUMN - session metadata columns preserved")
        
        conn.commit()
        print("🔄 Migration 059 rollback completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration 059 rollback failed: {e}")
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