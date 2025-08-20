#!/usr/bin/env python3
"""
Migration 036: Make equipment_id nullable in bow_equipment table
Fix: NOT NULL constraint failed: bow_equipment.equipment_id

This migration allows custom equipment entries where equipment_id can be NULL
since they don't exist in the main equipment database.
"""

import sqlite3
import sys
import os

def get_migration_info():
    """Return migration metadata"""
    return {
        'version': 36,
        'description': 'Make equipment_id nullable in bow_equipment table',
        'author': 'System',
        'created_at': '2025-08-20'
    }

def migrate_up(cursor):
    """Apply the migration"""
    conn = cursor.connection
    
    try:
        print("🔧 Migration 036: Making equipment_id nullable in bow_equipment table...")
        
        # Step 1: Check if the constraint needs to be fixed
        cursor.execute("PRAGMA table_info(bow_equipment);")
        columns = cursor.fetchall()
        
        equipment_id_column = None
        for col in columns:
            if col[1] == 'equipment_id':
                equipment_id_column = col
                break
        
        if equipment_id_column and equipment_id_column[3] == 1:  # NOT NULL = 1
            print("   ⚠️  equipment_id column is currently NOT NULL, fixing...")
            
            # Step 2: Create new table with nullable equipment_id
            cursor.execute('''
                CREATE TABLE bow_equipment_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bow_setup_id INTEGER NOT NULL,
                    equipment_id INTEGER,  -- Made nullable (removed NOT NULL)
                    installation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    installation_notes TEXT,
                    custom_specifications TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    manufacturer_name TEXT,
                    model_name TEXT,
                    category_name TEXT NOT NULL DEFAULT 'String',
                    weight_grams REAL,
                    description TEXT,
                    image_url TEXT,
                    is_custom BOOLEAN DEFAULT TRUE,
                    deleted_at TIMESTAMP,
                    deleted_by INTEGER,
                    setup_id INTEGER,
                    installed_at TIMESTAMP,
                    manufacturer TEXT,
                    category TEXT,
                    model TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    specifications TEXT,
                    FOREIGN KEY (bow_setup_id) REFERENCES bow_setups(id)
                )
            ''')
            
            # Step 3: Copy data from old table to new table
            print("   📋 Copying existing equipment data...")
            cursor.execute('''
                INSERT INTO bow_equipment_new (
                    id, bow_setup_id, equipment_id, installation_date, installation_notes,
                    custom_specifications, is_active, created_at, manufacturer_name,
                    model_name, category_name, weight_grams, description, image_url,
                    is_custom, deleted_at, deleted_by, setup_id, installed_at,
                    manufacturer, category, model, updated_at, specifications
                )
                SELECT 
                    id, bow_setup_id, equipment_id, installation_date, installation_notes,
                    custom_specifications, is_active, created_at, manufacturer_name,
                    model_name, category_name, weight_grams, description, image_url,
                    is_custom, deleted_at, deleted_by, setup_id, installed_at,
                    manufacturer, category, model, updated_at, specifications
                FROM bow_equipment
            ''')
            
            # Step 4: Drop old table and rename new table
            cursor.execute('DROP TABLE bow_equipment')
            cursor.execute('ALTER TABLE bow_equipment_new RENAME TO bow_equipment')
            
            print("   ✅ equipment_id is now nullable, custom equipment can be added")
            
        else:
            print("   ✅ equipment_id is already nullable, no changes needed")
        
        # Step 5: Verify the change
        cursor.execute("PRAGMA table_info(bow_equipment);")
        columns = cursor.fetchall()
        equipment_id_col = next((col for col in columns if col[1] == 'equipment_id'), None)
        
        if equipment_id_col and equipment_id_col[3] == 0:  # NOT NULL = 0 (nullable)
            print("   ✅ Verification: equipment_id is now nullable")
        else:
            raise Exception("   ❌ Verification failed: equipment_id is still NOT NULL")
        
        conn.commit()
        print("🎯 Migration 036 completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration 036 failed: {e}")
        conn.rollback()
        return False

def migrate_down(cursor):
    """Rollback the migration"""
    conn = cursor.connection
    
    try:
        print("🔄 Rolling back Migration 036...")
        
        # Step 1: Create table with NOT NULL constraint restored
        cursor.execute('''
            CREATE TABLE bow_equipment_rollback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bow_setup_id INTEGER NOT NULL,
                equipment_id INTEGER NOT NULL,  -- Restored NOT NULL constraint
                installation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                installation_notes TEXT,
                custom_specifications TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                manufacturer_name TEXT,
                model_name TEXT,
                category_name TEXT NOT NULL DEFAULT 'String',
                weight_grams REAL,
                description TEXT,
                image_url TEXT,
                is_custom BOOLEAN DEFAULT TRUE,
                deleted_at TIMESTAMP,
                deleted_by INTEGER,
                setup_id INTEGER,
                installed_at TIMESTAMP,
                manufacturer TEXT,
                category TEXT,
                model TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                specifications TEXT,
                FOREIGN KEY (bow_setup_id) REFERENCES bow_setups(id)
            )
        ''')
        
        # Step 2: Copy only records with non-NULL equipment_id
        print("   ⚠️  Copying only equipment with valid equipment_id (custom equipment will be lost)")
        cursor.execute('''
            INSERT INTO bow_equipment_rollback (
                id, bow_setup_id, equipment_id, installation_date, installation_notes,
                custom_specifications, is_active, created_at, manufacturer_name,
                model_name, category_name, weight_grams, description, image_url,
                is_custom, deleted_at, deleted_by, setup_id, installed_at,
                manufacturer, category, model, updated_at, specifications
            )
            SELECT 
                id, bow_setup_id, equipment_id, installation_date, installation_notes,
                custom_specifications, is_active, created_at, manufacturer_name,
                model_name, category_name, weight_grams, description, image_url,
                is_custom, deleted_at, deleted_by, setup_id, installed_at,
                manufacturer, category, model, updated_at, specifications
            FROM bow_equipment
            WHERE equipment_id IS NOT NULL
        ''')
        
        # Step 3: Replace the table
        cursor.execute('DROP TABLE bow_equipment')
        cursor.execute('ALTER TABLE bow_equipment_rollback RENAME TO bow_equipment')
        
        conn.commit()
        print("🔄 Migration 036 rollback completed")
        return True
        
    except Exception as e:
        print(f"❌ Migration 036 rollback failed: {e}")
        conn.rollback()
        return False

if __name__ == "__main__":
    # Test the migration
    db_path = os.path.join(os.path.dirname(__file__), '..', 'databases', 'arrow_database.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        sys.exit(1)
    
    conn = sqlite3.connect(db_path)
    
    try:
        if len(sys.argv) > 1 and sys.argv[1] == 'down':
            success = migrate_down(conn)
        else:
            success = migrate_up(conn)
        
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