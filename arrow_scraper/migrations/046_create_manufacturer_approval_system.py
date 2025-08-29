#!/usr/bin/env python3
"""
Migration 046: Create Manufacturer Approval System for Unified Database

Creates the complete manufacturer approval workflow system in the unified database:
- pending_manufacturers table for new manufacturer submissions
- user_pending_manufacturers table for user-manufacturer relationships
- manufacturer_approval_log table for audit trail
- Required indexes for performance

This migration ensures the manufacturer approval system works in the unified database architecture.
"""

import sqlite3
import json
from datetime import datetime

def get_migration_info():
    """Return migration metadata"""
    return {
        'version': '046',
        'description': 'Create manufacturer approval system for unified database',
        'dependencies': ['045'],
        'target_database': 'unified'
    }

def run_migration():
    """Execute the migration"""
    print("🔧 Migration 046: Creating manufacturer approval system for unified database...")
    
    # Use the unified database path
    import os
    from pathlib import Path
    
    # Determine database path
    if os.path.exists('./databases/arrow_database.db'):
        db_path = './databases/arrow_database.db'
    elif os.path.exists('../databases/arrow_database.db'):
        db_path = '../databases/arrow_database.db'
    else:
        db_path = 'databases/arrow_database.db'
    
    print(f"   Using database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if tables already exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pending_manufacturers'")
        pending_exists = cursor.fetchone()
        
        if pending_exists:
            print("   ✅ pending_manufacturers table already exists")
        else:
            # Create pending_manufacturers table
            print("   Creating pending_manufacturers table...")
            cursor.execute('''
            CREATE TABLE pending_manufacturers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                normalized_name TEXT,
                category_context TEXT,
                usage_count INTEGER DEFAULT 1,
                user_count INTEGER DEFAULT 1,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending',
                created_by_user_id INTEGER,
                approved_by_admin_id INTEGER,
                admin_notes TEXT,
                approved_at TIMESTAMP,
                rejection_reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by_user_id) REFERENCES users (id),
                FOREIGN KEY (approved_by_admin_id) REFERENCES users (id)
            )
            ''')
            print("   ✅ pending_manufacturers table created")
        
        # Check user_pending_manufacturers table structure
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_pending_manufacturers'")
        user_pending_exists = cursor.fetchone()
        
        if user_pending_exists:
            # Check if it has the correct structure
            cursor.execute("PRAGMA table_info(user_pending_manufacturers)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'pending_manufacturer_id' not in columns:
                print("   Dropping incorrectly structured user_pending_manufacturers table...")
                cursor.execute("DROP TABLE user_pending_manufacturers")
                user_pending_exists = False
        
        if not user_pending_exists:
            # Create user_pending_manufacturers table with correct structure
            print("   Creating user_pending_manufacturers table...")
            cursor.execute('''
            CREATE TABLE user_pending_manufacturers (
                user_id INTEGER,
                pending_manufacturer_id INTEGER,
                first_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                usage_count INTEGER DEFAULT 1,
                equipment_count INTEGER DEFAULT 1,
                PRIMARY KEY (user_id, pending_manufacturer_id),
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (pending_manufacturer_id) REFERENCES pending_manufacturers (id) ON DELETE CASCADE
            )
            ''')
            print("   ✅ user_pending_manufacturers table created")
        else:
            print("   ✅ user_pending_manufacturers table already exists with correct structure")
        
        # Check manufacturer_approval_log table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='manufacturer_approval_log'")
        log_exists = cursor.fetchone()
        
        if not log_exists:
            # Create manufacturer_approval_log table
            print("   Creating manufacturer_approval_log table...")
            cursor.execute('''
            CREATE TABLE manufacturer_approval_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pending_manufacturer_id INTEGER,
                action TEXT NOT NULL,
                admin_user_id INTEGER,
                user_notes TEXT,
                admin_notes TEXT,
                old_status TEXT,
                new_status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (pending_manufacturer_id) REFERENCES pending_manufacturers (id) ON DELETE CASCADE,
                FOREIGN KEY (admin_user_id) REFERENCES users (id)
            )
            ''')
            print("   ✅ manufacturer_approval_log table created")
        else:
            print("   ✅ manufacturer_approval_log table already exists")
        
        # Create indexes for performance
        print("   Creating indexes...")
        indexes = [
            ('idx_pending_manufacturers_status', 'pending_manufacturers', 'status'),
            ('idx_pending_manufacturers_name', 'pending_manufacturers', 'normalized_name'),
            ('idx_pending_manufacturers_created_by', 'pending_manufacturers', 'created_by_user_id'),
            ('idx_user_pending_manufacturers_user', 'user_pending_manufacturers', 'user_id'),
            ('idx_approval_log_manufacturer', 'manufacturer_approval_log', 'pending_manufacturer_id'),
            ('idx_approval_log_action', 'manufacturer_approval_log', 'action')
        ]
        
        for index_name, table_name, column_name in indexes:
            try:
                cursor.execute(f'CREATE INDEX IF NOT EXISTS {index_name} ON {table_name} ({column_name})')
                print(f"     ✓ Created index {index_name}")
            except Exception as e:
                print(f"     ⚠️  Could not create index {index_name}: {e}")
        
        # Verify all tables exist
        cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name IN ('pending_manufacturers', 'user_pending_manufacturers', 'manufacturer_approval_log')
        ORDER BY name
        """)
        created_tables = [row[0] for row in cursor.fetchall()]
        
        conn.commit()
        conn.close()
        
        print("✅ Migration 046 completed successfully!")
        print(f"   Created/verified tables: {', '.join(created_tables)}")
        print("   ✨ Manufacturer approval workflow is now available")
        print("   ✨ New manufacturers will be queued for admin approval")
        print("   ✨ Full audit trail enabled for approval decisions")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration 046 failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def rollback_migration():
    """Rollback the migration"""
    print("🔄 Rolling back migration 046...")
    
    # Use the unified database path
    import os
    
    # Determine database path
    if os.path.exists('./databases/arrow_database.db'):
        db_path = './databases/arrow_database.db'
    elif os.path.exists('../databases/arrow_database.db'):
        db_path = '../databases/arrow_database.db'
    else:
        db_path = 'databases/arrow_database.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Drop tables in reverse dependency order
        tables_to_drop = [
            'manufacturer_approval_log',
            'user_pending_manufacturers', 
            'pending_manufacturers'
        ]
        
        for table in tables_to_drop:
            cursor.execute(f"DROP TABLE IF EXISTS {table}")
            print(f"   ✓ Dropped table {table}")
        
        conn.commit()
        conn.close()
        
        print("✅ Migration 046 rollback completed")
        return True
        
    except Exception as e:
        print(f"❌ Migration 046 rollback failed: {e}")
        return False

if __name__ == "__main__":
    run_migration()