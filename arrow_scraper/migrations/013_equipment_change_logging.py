#!/usr/bin/env python3
"""
Migration 013: Equipment Change Logging System
Creates comprehensive change logging tables for equipment and setup modifications

This migration adds:
1. equipment_change_log table - Track all equipment modifications
2. setup_change_log table - Track setup-level changes  
3. Indexes for performance optimization
4. Support for detailed change tracking with before/after values
"""

import sqlite3
import os
from pathlib import Path

def get_database_path():
    """Get the correct database path using the same logic as UserDatabase"""
    # Check for environment variable first (Docker deployment)
    env_db_path = os.environ.get('USER_DATABASE_PATH')
    if env_db_path:
        return env_db_path
    
    # Unified database paths - same as UserDatabase class
    possible_paths = [
        Path("/app/databases/user_data.db"),  # Docker path (highest priority)
        Path(__file__).parent.parent / "databases" / "user_data.db",  # Local development
        Path(__file__).parent.parent / "user_data.db",  # Legacy local path
    ]
    
    for p in possible_paths:
        if p.exists():
            return str(p)
    
    # Default to first option for new installations
    return str(possible_paths[0])

def run_migration():
    """Execute the migration"""
    db_path = get_database_path()
    print(f"🔄 Running Migration 013: Equipment Change Logging System")
    print(f"📁 Database path: {db_path}")
    
    # Ensure database directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if migration already applied
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='equipment_change_log'")
        if cursor.fetchone():
            print("⚠️  Migration 013 already applied - skipping")
            return
        
        print("📋 Creating equipment change logging tables...")
        
        # 1. Create equipment_change_log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS equipment_change_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bow_setup_id INTEGER NOT NULL,
                equipment_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                change_type TEXT NOT NULL CHECK (change_type IN ('add', 'remove', 'modify', 'settings_change', 'activation_change')),
                field_name TEXT,
                old_value TEXT,
                new_value TEXT,
                change_description TEXT,
                change_reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (bow_setup_id) REFERENCES bow_setups (id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        print("✅ Created equipment_change_log table")
        
        # 2. Create setup_change_log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS setup_change_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bow_setup_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                change_type TEXT NOT NULL CHECK (change_type IN ('setup_modified', 'name_changed', 'description_changed', 'bow_info_changed', 'created')),
                field_name TEXT,
                old_value TEXT,
                new_value TEXT,
                change_description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (bow_setup_id) REFERENCES bow_setups (id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        print("✅ Created setup_change_log table")
        
        # 3. Create performance indexes for efficient querying
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_equipment_change_log_setup_id ON equipment_change_log(bow_setup_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_equipment_change_log_equipment_id ON equipment_change_log(equipment_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_equipment_change_log_user_date ON equipment_change_log(user_id, created_at DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_equipment_change_log_type ON equipment_change_log(change_type)')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_setup_change_log_setup_id ON setup_change_log(bow_setup_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_setup_change_log_user_date ON setup_change_log(user_id, created_at DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_setup_change_log_type ON setup_change_log(change_type)')
        
        print("✅ Created performance indexes")
        
        # 4. Insert initial setup creation entries for existing bow setups
        cursor.execute('''
            INSERT INTO setup_change_log (bow_setup_id, user_id, change_type, change_description)
            SELECT id, user_id, 'created', 'Bow setup created: ' || name
            FROM bow_setups
        ''')
        
        existing_setups = cursor.rowcount
        if existing_setups > 0:
            print(f"✅ Added creation entries for {existing_setups} existing bow setups")
        
        # 5. Insert initial equipment addition entries for existing equipment
        cursor.execute('''
            INSERT INTO equipment_change_log (bow_setup_id, equipment_id, user_id, change_type, change_description)
            SELECT 
                be.bow_setup_id, 
                be.id,
                bs.user_id,
                'add',
                'Equipment added: ' || 
                COALESCE(be.manufacturer_name, 'Unknown') || ' ' || 
                COALESCE(be.model_name, 'Unknown') || 
                ' (' || COALESCE(be.category_name, 'Equipment') || ')'
            FROM bow_equipment be
            JOIN bow_setups bs ON be.bow_setup_id = bs.id
            WHERE be.is_active = 1
        ''')
        
        existing_equipment = cursor.rowcount
        if existing_equipment > 0:
            print(f"✅ Added addition entries for {existing_equipment} existing equipment items")
        
        # Commit all changes
        conn.commit()
        
        print("🎉 Migration 013 completed successfully!")
        print("📊 Change logging system is now active")
        print("   • Equipment modifications will be automatically logged")
        print("   • Setup changes will be tracked with detailed history")
        print("   • Historical data has been backfilled for existing setups")
        
    except sqlite3.Error as e:
        print(f"❌ Migration 013 failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()