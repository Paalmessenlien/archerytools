#!/usr/bin/env python3
"""
Migration 054: Add shooting_style column to bow_setups table for shooting style calculations
"""
import sqlite3
import sys
import os

def get_migration_info():
    """Return migration metadata"""
    return {
        'version': 54,
        'description': 'Add shooting_style column to bow_setups table',
        'author': 'System', 
        'created_at': '2025-09-01'
    }

def migrate_up(cursor):
    """Apply the migration"""
    conn = cursor.connection
    try:
        print("🔧 Migration 054: Adding shooting_style column to bow_setups table...")
        
        # Add shooting_style column to bow_setups table
        cursor.execute("""
            ALTER TABLE bow_setups 
            ADD COLUMN shooting_style TEXT DEFAULT 'standard' CHECK (shooting_style IN ('standard', 'barebow', 'olympic', 'traditional', 'hunting', 'target'))
        """)
        
        conn.commit()
        print("🎯 Migration 054 completed successfully!")
        return True
    except Exception as e:
        print(f"❌ Migration 054 failed: {e}")
        conn.rollback()
        return False

def migrate_down(cursor):
    """Rollback the migration"""
    conn = cursor.connection
    try:
        print("🔄 Rolling back Migration 054...")
        
        # SQLite doesn't support DROP COLUMN directly, need to recreate table
        # Get current table structure
        cursor.execute("PRAGMA table_info(bow_setups)")
        columns = cursor.fetchall()
        
        # Create new table without shooting_style column
        old_columns = [col[1] for col in columns if col[1] != 'shooting_style']
        columns_str = ', '.join(old_columns)
        
        cursor.execute("BEGIN TRANSACTION")
        cursor.execute(f"CREATE TABLE bow_setups_temp AS SELECT {columns_str} FROM bow_setups")
        cursor.execute("DROP TABLE bow_setups")
        cursor.execute("ALTER TABLE bow_setups_temp RENAME TO bow_setups")
        
        conn.commit()
        print("🎯 Migration 054 rollback completed!")
        return True
    except Exception as e:
        print(f"❌ Migration 054 rollback failed: {e}")
        conn.rollback()
        return False

if __name__ == "__main__":
    # Direct execution for testing
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        db_path = os.path.join(os.path.dirname(__file__), '..', 'databases', 'arrow_database.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Testing migration 054...")
        if migrate_up(cursor):
            print("✅ Migration test successful")
        else:
            print("❌ Migration test failed")
        
        conn.close()