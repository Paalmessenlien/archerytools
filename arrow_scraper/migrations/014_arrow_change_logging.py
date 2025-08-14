#!/usr/bin/env python3
"""
Migration 014: Arrow Change Logging System

Adds comprehensive change logging for arrow management including:
- Arrow setup additions and removals
- Arrow specification modifications
- User notes for change tracking
- Integration with existing change log system
"""

import sqlite3
import os
import sys
from datetime import datetime

# Add the arrow_scraper directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def get_database_path():
    """Get the correct database path for user data"""
    # Check if we're running in Docker
    if os.path.exists('/app/databases/'):
        return '/app/databases/user_data.db'
    # Check if we're in the arrow_scraper directory
    elif os.path.exists('databases/user_data.db'):
        return 'databases/user_data.db'
    # Check parent directory
    elif os.path.exists('../databases/user_data.db'):
        return '../databases/user_data.db'
    else:
        # Default fallback
        return 'user_data.db'

def run_migration():
    """Execute the arrow change logging migration"""
    db_path = get_database_path()
    print(f"🔄 Running Migration 014: Arrow Change Logging System")
    print(f"📁 Database path: {db_path}")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        print("📋 Creating arrow change logging table...")
        
        # Create arrow_change_log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS arrow_change_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bow_setup_id INTEGER NOT NULL,
                arrow_id INTEGER,
                user_id INTEGER NOT NULL,
                change_type TEXT NOT NULL CHECK (change_type IN (
                    'arrow_added', 'arrow_removed', 'arrow_modified', 
                    'quantity_changed', 'specifications_changed', 'setup_changed'
                )),
                field_name TEXT,
                old_value TEXT,
                new_value TEXT,
                change_description TEXT,
                user_note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (bow_setup_id) REFERENCES bow_setups (id) ON DELETE CASCADE,
                FOREIGN KEY (arrow_id) REFERENCES arrows (id) ON DELETE SET NULL,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        print("✅ Created arrow_change_log table")
        
        # Create indexes for performance
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_arrow_change_log_bow_setup 
            ON arrow_change_log (bow_setup_id, created_at DESC)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_arrow_change_log_arrow 
            ON arrow_change_log (arrow_id, created_at DESC)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_arrow_change_log_user 
            ON arrow_change_log (user_id, created_at DESC)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_arrow_change_log_type 
            ON arrow_change_log (change_type, created_at DESC)
        ''')
        print("✅ Created performance indexes")
        
        # Backfill existing arrow assignments as creation entries
        print("📊 Backfilling existing arrow assignments...")
        cursor.execute('''
            SELECT 
                sa.setup_id as bow_setup_id,
                bs.user_id,
                sa.arrow_id,
                bs.name as setup_name,
                sa.arrow_length,
                sa.point_weight,
                sa.notes,
                sa.created_at
            FROM setup_arrows sa
            JOIN bow_setups bs ON sa.setup_id = bs.id
        ''')
        
        existing_assignments = cursor.fetchall()
        creation_entries = 0
        
        for assignment in existing_assignments:
            details = []
            if assignment['arrow_length']:
                details.append(f"Length: {assignment['arrow_length']}\"")
            if assignment['point_weight']:
                details.append(f"Point: {assignment['point_weight']}gr")
                
            detail_str = f" ({', '.join(details)})" if details else ""
            change_description = f"Arrow assigned to setup{detail_str}"
            
            cursor.execute('''
                INSERT INTO arrow_change_log 
                (bow_setup_id, arrow_id, user_id, change_type, change_description, user_note, created_at)
                VALUES (?, ?, ?, 'arrow_added', ?, ?, ?)
            ''', (
                assignment['bow_setup_id'],
                assignment['arrow_id'], 
                assignment['user_id'],
                change_description,
                assignment['notes'] or 'Initial arrow assignment',
                assignment['created_at']
            ))
            creation_entries += 1
        
        print(f"✅ Added creation entries for {creation_entries} existing arrow assignments")
        
        # Create view for unified change history (arrows + equipment + setup)
        cursor.execute('''
            CREATE VIEW IF NOT EXISTS unified_change_history AS
            SELECT 
                'arrow' as change_source,
                acl.id,
                acl.bow_setup_id,
                acl.user_id,
                acl.change_type,
                acl.field_name,
                acl.old_value,
                acl.new_value,
                acl.change_description,
                acl.user_note as change_reason,
                acl.created_at,
                NULL as manufacturer_name,
                NULL as model_name,
                'Arrow' as category_name,
                acl.arrow_id as item_id
            FROM arrow_change_log acl
            
            UNION ALL
            
            SELECT 
                'equipment' as change_source,
                ecl.id,
                ecl.bow_setup_id,
                ecl.user_id,
                ecl.change_type,
                ecl.field_name,
                ecl.old_value,
                ecl.new_value,
                ecl.change_description,
                ecl.change_reason,
                ecl.created_at,
                be.manufacturer_name,
                be.model_name,
                be.category_name,
                ecl.equipment_id as item_id
            FROM equipment_change_log ecl
            LEFT JOIN bow_equipment be ON ecl.equipment_id = be.id
            
            UNION ALL
            
            SELECT 
                'setup' as change_source,
                scl.id,
                scl.bow_setup_id,
                scl.user_id,
                scl.change_type,
                scl.field_name,
                scl.old_value,
                scl.new_value,
                scl.change_description,
                NULL as change_reason,
                scl.created_at,
                NULL as manufacturer_name,
                NULL as model_name,
                'Setup' as category_name,
                NULL as item_id
            FROM setup_change_log scl
        ''')
        print("✅ Created unified change history view")
        
        conn.commit()
        print("🎉 Migration 014 completed successfully!")
        print("📊 Arrow change logging system is now active")
        print("   • Arrow additions, modifications, and removals will be tracked")
        print("   • User notes can be added to all arrow changes")
        print("   • Unified change history view created for comprehensive tracking")
        print("   • Historical data has been backfilled for existing arrow assignments")
        
    except sqlite3.Error as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()