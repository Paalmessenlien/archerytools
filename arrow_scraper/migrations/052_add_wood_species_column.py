#!/usr/bin/env python3
"""
Migration 052: Add wood_species column to bow_setups table for wood arrow spine calculations
"""
import sqlite3
import sys
import os

def get_migration_info():
    """Return migration metadata"""
    return {
        'version': 52,
        'description': 'Add wood_species column to bow_setups table',
        'author': 'System', 
        'created_at': '2025-08-31'
    }

def migrate_up(cursor):
    """Apply the migration"""
    conn = cursor.connection
    try:
        print("🔧 Migration 052: Adding wood_species column to bow_setups table...")
        
        # Add wood_species column to bow_setups table
        cursor.execute("""
            ALTER TABLE bow_setups 
            ADD COLUMN wood_species TEXT
        """)
        
        conn.commit()
        print("🎯 Migration 052 completed successfully!")
        return True
    except Exception as e:
        print(f"❌ Migration 052 failed: {e}")
        conn.rollback()
        return False

def migrate_down(cursor):
    """Rollback the migration"""
    conn = cursor.connection
    try:
        print("🔄 Rolling back Migration 052...")
        
        # SQLite doesn't support DROP COLUMN directly, need to recreate table
        # Get current table structure
        cursor.execute("PRAGMA table_info(bow_setups)")
        columns = cursor.fetchall()
        
        # Create new table without wood_species column
        old_columns = [col[1] for col in columns if col[1] != 'wood_species']
        columns_str = ', '.join(old_columns)
        
        cursor.execute("BEGIN TRANSACTION")
        cursor.execute(f"CREATE TABLE bow_setups_temp AS SELECT {columns_str} FROM bow_setups")
        cursor.execute("DROP TABLE bow_setups")
        cursor.execute("ALTER TABLE bow_setups_temp RENAME TO bow_setups")
        
        conn.commit()
        print("🎯 Migration 052 rollback completed!")
        return True
    except Exception as e:
        print(f"❌ Migration 052 rollback failed: {e}")
        conn.rollback()
        return False

if __name__ == "__main__":
    # Direct execution for testing
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        db_path = os.path.join(os.path.dirname(__file__), '..', 'databases', 'arrow_database.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Testing migration 052...")
        if migrate_up(cursor):
            print("✅ Migration test successful")
        else:
            print("❌ Migration test failed")
        
        conn.close()