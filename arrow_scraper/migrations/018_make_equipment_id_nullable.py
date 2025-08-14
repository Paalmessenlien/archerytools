#!/usr/bin/env python3
"""
Migration 018: Make equipment_id nullable in bow_equipment table
This fixes the issue where custom equipment cannot be added because equipment_id
is required but custom equipment doesn't have an equipment_id from the arrow database.
"""

import sqlite3
from database_migration_manager import BaseMigration

class Migration018MakeEquipmentIdNullable(BaseMigration):
    def __init__(self):
        super().__init__()
        self.version = "018"
        self.description = "Make equipment_id nullable for custom equipment"
        self.dependencies = ["017"]
        self.environments = ['all']
        self.target_database = 'user'
    
    def up(self, db_path: str, environment: str) -> bool:
        """Make equipment_id nullable in bow_equipment table"""
        try:
            # Get user database path
            user_db_path = self._get_user_database_path(db_path)
            if not user_db_path:
                print("❌ Could not find user database")
                return False
            
            conn = sqlite3.connect(user_db_path)
            cursor = conn.cursor()
            
            # Check current schema
            cursor.execute("PRAGMA table_info(bow_equipment)")
            columns = cursor.fetchall()
            
            # Check if equipment_id is currently NOT NULL
            equipment_id_nullable = False
            for col in columns:
                if col[1] == 'equipment_id':  # column name
                    equipment_id_nullable = (col[3] == 0)  # notnull = 0 means nullable
                    break
            
            if equipment_id_nullable:
                print("✅ equipment_id is already nullable, migration not needed")
                conn.close()
                return True
            
            print("🔄 Making equipment_id nullable in bow_equipment table...")
            
            # Drop the view that depends on bow_equipment
            cursor.execute("DROP VIEW IF EXISTS unified_change_history")
            
            # Get existing data
            cursor.execute("SELECT * FROM bow_equipment")
            existing_data = cursor.fetchall()
            
            # Get column names
            cursor.execute("PRAGMA table_info(bow_equipment)")
            column_info = cursor.fetchall()
            columns_with_types = [(col[1], col[2], col[4]) for col in column_info]  # name, type, default
            
            # Create new table with nullable equipment_id
            create_sql = """
                CREATE TABLE bow_equipment_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bow_setup_id INTEGER NOT NULL,
                    equipment_id INTEGER,  -- Made nullable (removed NOT NULL)
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
            """
            cursor.execute(create_sql)
            
            # Copy existing data
            if existing_data:
                # Build column list for INSERT
                column_names = [col[0] for col in columns_with_types]
                placeholders = ','.join(['?' for _ in column_names])
                column_list = ','.join(column_names)
                
                cursor.executemany(f'''
                    INSERT INTO bow_equipment_new ({column_list})
                    VALUES ({placeholders})
                ''', existing_data)
            
            # Replace old table with new table
            cursor.execute("DROP TABLE bow_equipment")
            cursor.execute("ALTER TABLE bow_equipment_new RENAME TO bow_equipment")
            
            # Recreate the unified_change_history view
            cursor.execute("""
                CREATE VIEW unified_change_history AS
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
            """)
            
            conn.commit()
            conn.close()
            
            print("✅ Successfully made equipment_id nullable in bow_equipment table")
            return True
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            return False
    
    def down(self, db_path: str, environment: str) -> bool:
        """Rollback: Make equipment_id NOT NULL again"""
        try:
            # Get user database path
            user_db_path = self._get_user_database_path(db_path)
            if not user_db_path:
                print("❌ Could not find user database")
                return False
            
            conn = sqlite3.connect(user_db_path)
            cursor = conn.cursor()
            
            # Check if any records have NULL equipment_id
            cursor.execute("SELECT COUNT(*) FROM bow_equipment WHERE equipment_id IS NULL")
            null_count = cursor.fetchone()[0]
            
            if null_count > 0:
                print(f"⚠️ Warning: Cannot rollback - {null_count} records have NULL equipment_id")
                conn.close()
                return False
            
            print("🔄 Rolling back: Making equipment_id NOT NULL again...")
            
            # Get existing data
            cursor.execute("SELECT * FROM bow_equipment")
            existing_data = cursor.fetchall()
            
            # Create table with NOT NULL equipment_id
            create_sql = """
                CREATE TABLE bow_equipment_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bow_setup_id INTEGER NOT NULL,
                    equipment_id INTEGER NOT NULL,  -- Made NOT NULL again
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
            """
            cursor.execute(create_sql)
            
            # Copy existing data (this will fail if any NULL equipment_id exists)
            if existing_data:
                cursor.executemany('''
                    INSERT INTO bow_equipment_new 
                    (id, bow_setup_id, equipment_id, installation_date, installation_notes,
                     custom_specifications, is_active, created_at, manufacturer_name, model_name,
                     category_name, weight_grams, description, image_url, is_custom)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', existing_data)
            
            # Replace tables
            cursor.execute("DROP TABLE bow_equipment")
            cursor.execute("ALTER TABLE bow_equipment_new RENAME TO bow_equipment")
            
            conn.commit()
            conn.close()
            
            print("✅ Successfully rolled back equipment_id to NOT NULL")
            return True
            
        except Exception as e:
            print(f"❌ Rollback failed: {e}")
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            return False
    
    def _get_user_database_path(self, arrow_db_path: str) -> str:
        """Helper to find user database path"""
        try:
            from user_database import UserDatabase
            user_db = UserDatabase()
            return user_db.db_path
        except Exception as e:
            print(f"⚠️ Error finding user database: {e}")
            return None

# Create the migration instance for discovery
migration = Migration018MakeEquipmentIdNullable()