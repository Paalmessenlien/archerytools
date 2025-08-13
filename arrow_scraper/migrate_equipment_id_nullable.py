#!/usr/bin/env python3
"""
Database Migration: Allow NULL equipment_id for custom equipment

This migration removes the NOT NULL constraint from the equipment_id column 
in the bow_equipment table to support custom equipment that doesn't link to 
pre-defined equipment records.

This fixes the error: NOT NULL constraint failed: bow_equipment.equipment_id
"""

import sqlite3
import sys
import os
from pathlib import Path

def migrate_equipment_id_nullable():
    """Remove NOT NULL constraint from bow_equipment.equipment_id column"""
    
    # Determine database path using environment variable or default
    db_path = os.getenv('USER_DATABASE_PATH', 'databases/user_data.db')
    
    # Ensure database file exists
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return False
    
    print(f"🔄 Migrating database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check if the migration is needed
        cursor.execute("PRAGMA table_info(bow_equipment)")
        columns = cursor.fetchall()
        
        equipment_id_column = None
        for col in columns:
            if col['name'] == 'equipment_id':
                equipment_id_column = col
                break
        
        if not equipment_id_column:
            print("❌ equipment_id column not found in bow_equipment table")
            return False
        
        if equipment_id_column['notnull'] == 0:
            print("✅ equipment_id column already allows NULL values - no migration needed")
            return True
        
        print("🔧 Removing NOT NULL constraint from equipment_id column...")
        
        # Step 1: Get current table schema
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='bow_equipment'")
        create_table_sql = cursor.fetchone()['sql']
        print(f"📋 Current table schema: {create_table_sql}")
        
        # Step 2: Begin transaction
        cursor.execute("BEGIN TRANSACTION")
        
        # Step 3: Create temporary table without NOT NULL constraint on equipment_id
        cursor.execute('''
            CREATE TABLE bow_equipment_temp (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bow_setup_id INTEGER NOT NULL,
                equipment_id INTEGER,  -- Removed NOT NULL constraint
                installation_date TEXT DEFAULT CURRENT_TIMESTAMP,
                installation_notes TEXT,
                custom_specifications TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                manufacturer_name TEXT,
                model_name TEXT,
                category_name TEXT,
                weight_grams REAL,
                description TEXT,
                image_url TEXT,
                is_custom BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (bow_setup_id) REFERENCES bow_setups (id) ON DELETE CASCADE
            )
        ''')
        
        # Step 4: Copy data from original table to temporary table
        cursor.execute('''
            INSERT INTO bow_equipment_temp 
            SELECT * FROM bow_equipment
        ''')
        
        # Step 5: Drop original table
        cursor.execute('DROP TABLE bow_equipment')
        
        # Step 6: Rename temporary table to original name
        cursor.execute('ALTER TABLE bow_equipment_temp RENAME TO bow_equipment')
        
        # Step 7: Commit transaction
        cursor.execute("COMMIT")
        
        # Verify the migration
        cursor.execute("PRAGMA table_info(bow_equipment)")
        columns = cursor.fetchall()
        
        equipment_id_column = None
        for col in columns:
            if col['name'] == 'equipment_id':
                equipment_id_column = col
                break
        
        if equipment_id_column and equipment_id_column['notnull'] == 0:
            print("✅ Migration successful - equipment_id column now allows NULL values")
            
            # Count existing records
            cursor.execute("SELECT COUNT(*) as count FROM bow_equipment")
            count = cursor.fetchone()['count']
            print(f"📊 Preserved {count} existing equipment records")
            
            return True
        else:
            print("❌ Migration verification failed")
            return False
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        try:
            cursor.execute("ROLLBACK")
        except:
            pass
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    print("🗄️  Equipment ID Nullable Migration")
    print("=" * 50)
    
    success = migrate_equipment_id_nullable()
    
    if success:
        print("✅ Migration completed successfully")
        sys.exit(0)
    else:
        print("❌ Migration failed")
        sys.exit(1)