#!/usr/bin/env python3
"""
Migration 028: Add Remaining Schema Columns
Adds the remaining missing columns identified by schema verification
to reduce validation warnings.

Date: 2025-08-18
Author: Claude Code Enhancement
Purpose: Complete schema verification requirements
"""

import sqlite3
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database_migration_manager import BaseMigration

class Migration028AddRemainingSchemaColumns(BaseMigration):
    def __init__(self):
        super().__init__()
        self.version = "028"
        self.description = "Add Remaining Schema Columns for Verification"
        self.dependencies = ["027"]
        self.environments = ['all']
        self.target_database = 'arrow'
    
    def up(self, db_path: str, environment: str) -> bool:
        """
        Add remaining missing columns needed for schema verification
        """
        try:
            print("🔧 Adding remaining schema columns...")
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check which tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = {row[0] for row in cursor.fetchall()}
            
            added_count = 0
            
            # Add missing backup_metadata columns
            if 'backup_metadata' in existing_tables:
                backup_columns = [
                    ('file_path', 'TEXT'),
                    ('backup_type', 'TEXT DEFAULT "full"'),
                    ('includes', 'TEXT'),  # JSON field
                    ('file_size', 'INTEGER'),
                ]
                
                # Check existing columns
                cursor.execute("PRAGMA table_info(backup_metadata)")
                existing_cols = {row[1] for row in cursor.fetchall()}
                
                for col_name, col_def in backup_columns:
                    if col_name not in existing_cols:
                        try:
                            cursor.execute(f"ALTER TABLE backup_metadata ADD COLUMN {col_name} {col_def}")
                            print(f"   ✅ Added backup_metadata.{col_name}")
                            added_count += 1
                        except sqlite3.OperationalError as e:
                            print(f"   ⚠️  Could not add backup_metadata.{col_name}: {e}")
            
            # Add missing bow_equipment columns (for equipment management)
            if 'bow_equipment' in existing_tables:
                equipment_columns = [
                    ('category', 'TEXT'),
                    ('manufacturer', 'TEXT'),
                    ('model', 'TEXT'),
                    ('specifications', 'TEXT'),  # JSON field
                    ('installed_at', 'TIMESTAMP'),
                    ('setup_id', 'INTEGER'),
                ]
                
                cursor.execute("PRAGMA table_info(bow_equipment)")
                existing_cols = {row[1] for row in cursor.fetchall()}
                
                for col_name, col_def in equipment_columns:
                    if col_name not in existing_cols:
                        try:
                            cursor.execute(f"ALTER TABLE bow_equipment ADD COLUMN {col_name} {col_def}")
                            print(f"   ✅ Added bow_equipment.{col_name}")
                            added_count += 1
                        except sqlite3.OperationalError as e:
                            print(f"   ⚠️  Could not add bow_equipment.{col_name}: {e}")
            
            # Add missing manufacturers columns
            if 'manufacturers' in existing_tables:
                mfg_columns = [
                    ('website', 'TEXT'),
                    ('contact_info', 'TEXT'),
                    ('established', 'INTEGER'),
                    ('arrow_types', 'TEXT'),  # JSON field
                ]
                
                cursor.execute("PRAGMA table_info(manufacturers)")
                existing_cols = {row[1] for row in cursor.fetchall()}
                
                for col_name, col_def in mfg_columns:
                    if col_name not in existing_cols:
                        try:
                            cursor.execute(f"ALTER TABLE manufacturers ADD COLUMN {col_name} {col_def}")
                            print(f"   ✅ Added manufacturers.{col_name}")
                            added_count += 1
                        except sqlite3.OperationalError as e:
                            print(f"   ⚠️  Could not add manufacturers.{col_name}: {e}")
            
            # Add missing arrows columns
            if 'arrows' in existing_tables:
                arrow_columns = [
                    ('retailer_data', 'TEXT'),  # JSON field for pricing/availability
                ]
                
                cursor.execute("PRAGMA table_info(arrows)")
                existing_cols = {row[1] for row in cursor.fetchall()}
                
                for col_name, col_def in arrow_columns:
                    if col_name not in existing_cols:
                        try:
                            cursor.execute(f"ALTER TABLE arrows ADD COLUMN {col_name} {col_def}")
                            print(f"   ✅ Added arrows.{col_name}")
                            added_count += 1
                        except sqlite3.OperationalError as e:
                            print(f"   ⚠️  Could not add arrows.{col_name}: {e}")
            
            # Create guide_sessions table if missing (may not exist)
            if 'guide_sessions' not in existing_tables:
                print("   🏗️  Creating guide_sessions table...")
                cursor.execute('''
                    CREATE TABLE guide_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        setup_id INTEGER,
                        session_data TEXT,  -- JSON field
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (setup_id) REFERENCES bow_setups (id) ON DELETE CASCADE
                    )
                ''')
                added_count += 1
                print("   ✅ Created guide_sessions table")
            
            conn.commit()
            conn.close()
            
            print(f"✅ Added {added_count} schema columns/tables")
            return True
            
        except Exception as e:
            print(f"❌ Failed to add schema columns: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def down(self, db_path: str, environment: str) -> bool:
        """
        Rollback: Remove added columns (SQLite doesn't support DROP COLUMN easily)
        """
        try:
            print("⚠️  SQLite doesn't support DROP COLUMN. Manual rollback required if needed.")
            return True
            
        except Exception as e:
            print(f"❌ Rollback failed: {e}")
            return False

# Create migration instance for discovery
migration = Migration028AddRemainingSchemaColumns()

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python 028_add_remaining_schema_columns.py <database_path>")
        sys.exit(1)
    
    db_path = sys.argv[1]
    migration = Migration028AddRemainingSchemaColumns()
    
    if '--rollback' in sys.argv:
        success = migration.down(db_path, 'manual')
    else:
        success = migration.up(db_path, 'manual')
    
    sys.exit(0 if success else 1)