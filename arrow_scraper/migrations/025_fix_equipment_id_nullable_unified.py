#!/usr/bin/env python3
"""
Migration 025: Fix Equipment ID Nullable for Unified Database
Fixes the bow_equipment table in the unified database to allow NULL equipment_id for custom equipment entries

This migration corrects the issue where Migration 018 was designed for the old dual-database
architecture but we now have a unified database. The equipment_id column needs to be nullable
to allow custom equipment that doesn't link to the equipment table.

Date: 2025-08-17
Author: Claude Code Enhancement
Issue: Equipment addition 500 error - NOT NULL constraint failed: bow_equipment.equipment_id
Solution: Make equipment_id nullable in unified arrow_database.db
"""

import sqlite3
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database_migration_manager import BaseMigration

class Migration025FixEquipmentIdNullableUnified(BaseMigration):
    def __init__(self):
        super().__init__()
        self.version = "025"
        self.description = "Fix Equipment ID Nullable for Unified Database Architecture"
        self.dependencies = ["024"]
        self.environments = ['all']
        self.target_database = 'arrow'  # Target unified database
    
    def up(self, db_path: str, environment: str) -> bool:
        """
        Make equipment_id nullable in bow_equipment table in unified database
        """
        try:
            print("🔧 Fixing bow_equipment.equipment_id constraint in unified database...")
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if bow_equipment table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bow_equipment'")
            if not cursor.fetchone():
                print("⚠️  bow_equipment table not found - skipping migration")
                conn.close()
                return True
            
            # Check current schema
            cursor.execute("PRAGMA table_info(bow_equipment)")
            columns = cursor.fetchall()
            print(f"📋 Current bow_equipment table has {len(columns)} columns")
            
            # Check if equipment_id is already nullable
            equipment_id_col = None
            for col in columns:
                if col[1] == 'equipment_id':
                    equipment_id_col = col
                    break
            
            if not equipment_id_col:
                print("⚠️  equipment_id column not found - skipping migration")
                conn.close()
                return True
                
            # Check if it's already nullable (notnull = 0 means nullable)
            if equipment_id_col[3] == 0:  # notnull field
                print("✅ equipment_id is already nullable - no changes needed")
                conn.close()
                return True
            
            print(f"🏗️  Recreating bow_equipment table - equipment_id currently NOT NULL: {equipment_id_col[3]}")
            
            # Get all existing data first
            cursor.execute("SELECT * FROM bow_equipment")
            existing_data = cursor.fetchall()
            data_count = len(existing_data)
            print(f"📦 Found {data_count} existing equipment records to preserve")
            
            # Rename old table
            cursor.execute("ALTER TABLE bow_equipment RENAME TO bow_equipment_old")
            
            # Create new table with equipment_id nullable and all existing columns
            cursor.execute("""
                CREATE TABLE bow_equipment (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bow_setup_id INTEGER NOT NULL,
                    equipment_id INTEGER,  -- Made nullable for custom equipment
                    installation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    installation_notes TEXT,
                    custom_specifications TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    manufacturer_name TEXT,
                    model_name TEXT,
                    category_name TEXT NOT NULL DEFAULT "String",
                    weight_grams REAL,
                    description TEXT,
                    image_url TEXT,
                    is_custom BOOLEAN DEFAULT TRUE,
                    deleted_at TIMESTAMP,
                    deleted_by INTEGER,
                    FOREIGN KEY (bow_setup_id) REFERENCES bow_setups (id) ON DELETE CASCADE,
                    FOREIGN KEY (equipment_id) REFERENCES equipment (id)
                )
            """)
            
            # Copy data from old table if any exists
            if data_count > 0:
                print("📦 Migrating existing equipment data...")
                cursor.execute("""
                    INSERT INTO bow_equipment 
                    SELECT * FROM bow_equipment_old
                """)
                rows_migrated = cursor.rowcount
                print(f"   ✅ Migrated {rows_migrated} equipment records")
            
            # Recreate indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_bow_equipment_deleted 
                ON bow_equipment (is_active, deleted_at DESC)
            """)
            
            # Drop old table
            cursor.execute("DROP TABLE bow_equipment_old")
            
            # Verify the fix
            cursor.execute("PRAGMA table_info(bow_equipment)")
            new_columns = cursor.fetchall()
            equipment_id_new = None
            for col in new_columns:
                if col[1] == 'equipment_id':
                    equipment_id_new = col
                    break
            
            conn.commit()
            conn.close()
            
            if equipment_id_new and equipment_id_new[3] == 0:
                print("✅ bow_equipment schema fixed successfully!")
                print("   - equipment_id is now nullable for custom equipment")
                print("   - Custom equipment can be added without database constraints")
                return True
            else:
                print("❌ Schema fix verification failed")
                return False
            
        except Exception as e:
            print(f"❌ Failed to fix schema: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def down(self, db_path: str, environment: str) -> bool:
        """
        Rollback: Restore NOT NULL constraint on equipment_id (WARNING: may fail if NULL values exist)
        """
        try:
            print("⚠️  Rolling back equipment_id nullable change...")
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check for NULL equipment_id values
            cursor.execute("SELECT COUNT(*) FROM bow_equipment WHERE equipment_id IS NULL")
            null_count = cursor.fetchone()[0]
            
            if null_count > 0:
                print(f"❌ Cannot rollback: {null_count} records have NULL equipment_id")
                print("   Remove custom equipment entries before rolling back")
                conn.close()
                return False
            
            # Rename current table
            cursor.execute("ALTER TABLE bow_equipment RENAME TO bow_equipment_nullable")
            
            # Recreate with NOT NULL constraint
            cursor.execute("""
                CREATE TABLE bow_equipment (
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
                    category_name TEXT NOT NULL DEFAULT "String",
                    weight_grams REAL,
                    description TEXT,
                    image_url TEXT,
                    is_custom BOOLEAN DEFAULT TRUE,
                    deleted_at TIMESTAMP,
                    deleted_by INTEGER,
                    FOREIGN KEY (bow_setup_id) REFERENCES bow_setups (id) ON DELETE CASCADE,
                    FOREIGN KEY (equipment_id) REFERENCES equipment (id)
                )
            """)
            
            # Copy data back (this will only work if no NULL values exist)
            cursor.execute("INSERT INTO bow_equipment SELECT * FROM bow_equipment_nullable")
            
            # Recreate indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_bow_equipment_deleted 
                ON bow_equipment (is_active, deleted_at DESC)
            """)
            
            # Drop temporary table
            cursor.execute("DROP TABLE bow_equipment_nullable")
            
            conn.commit()
            conn.close()
            
            print("✅ Rollback completed - equipment_id is NOT NULL again")
            return True
            
        except Exception as e:
            print(f"❌ Rollback failed: {e}")
            return False

# Create migration instance for discovery
migration = Migration025FixEquipmentIdNullableUnified()

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python 025_fix_equipment_id_nullable_unified.py <database_path>")
        sys.exit(1)
    
    db_path = sys.argv[1]
    migration = Migration025FixEquipmentIdNullableUnified()
    
    if '--rollback' in sys.argv:
        success = migration.down(db_path, 'manual')
    else:
        success = migration.up(db_path, 'manual')
    
    sys.exit(0 if success else 1)