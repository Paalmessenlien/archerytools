#!/usr/bin/env python3
"""
Migration 027: Add Essential Missing Columns
Adds only the essential missing columns identified by schema verification.
Excludes legacy columns that are no longer needed.

Date: 2025-08-18
Author: Claude Code Enhancement
Purpose: Fix schema verification issues by adding essential missing columns
"""

import sqlite3
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database_migration_manager import BaseMigration

class Migration027AddEssentialMissingColumns(BaseMigration):
    def __init__(self):
        super().__init__()
        self.version = "027"
        self.description = "Add Essential Missing Columns"
        self.dependencies = ["026"]
        self.environments = ['all']
        self.target_database = 'arrow'
    
    def up(self, db_path: str, environment: str) -> bool:
        """
        Add essential missing columns to tables
        """
        try:
            print("🔧 Adding essential missing columns...")
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Essential missing columns to add (SQLite compatible)
            essential_columns = [
                # bow_setups table
                ('bow_setups', 'updated_at', 'TIMESTAMP'),
                
                # users table  
                ('users', 'last_login', 'TIMESTAMP'),
                ('users', 'updated_at', 'TIMESTAMP'),
                
                # spine_specifications table
                ('spine_specifications', 'created_at', 'TIMESTAMP'),
                
                # equipment_field_standards table - add missing but important columns
                ('equipment_field_standards', 'updated_at', 'TIMESTAMP'),
            ]
            
            # Check which tables exist and add columns
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = {row[0] for row in cursor.fetchall()}
            
            added_count = 0
            for table_name, column_name, column_def in essential_columns:
                if table_name not in existing_tables:
                    print(f"   ⚠️  Table {table_name} doesn't exist, skipping {column_name}")
                    continue
                
                # Check if column already exists
                cursor.execute(f"PRAGMA table_info({table_name})")
                existing_columns = {row[1] for row in cursor.fetchall()}
                
                if column_name not in existing_columns:
                    try:
                        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_def}")
                        print(f"   ✅ Added {table_name}.{column_name}")
                        added_count += 1
                    except sqlite3.OperationalError as e:
                        print(f"   ⚠️  Could not add {table_name}.{column_name}: {e}")
                else:
                    print(f"   ✅ Column {table_name}.{column_name} already exists")
            
            # Create backup_metadata table if it doesn't exist (for backup system)
            if 'backup_metadata' not in existing_tables:
                print("   🏗️  Creating backup_metadata table...")
                cursor.execute('''
                    CREATE TABLE backup_metadata (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        backup_name TEXT NOT NULL UNIQUE,
                        file_path TEXT,
                        file_size INTEGER,
                        backup_type TEXT DEFAULT 'full',
                        includes TEXT,  -- JSON field
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        notes TEXT
                    )
                ''')
                added_count += 1
                print("   ✅ Created backup_metadata table")
            
            conn.commit()
            conn.close()
            
            print(f"✅ Added {added_count} essential database columns/tables")
            return True
            
        except Exception as e:
            print(f"❌ Failed to add essential columns: {e}")
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
migration = Migration027AddEssentialMissingColumns()

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python 027_add_essential_missing_columns.py <database_path>")
        sys.exit(1)
    
    db_path = sys.argv[1]
    migration = Migration027AddEssentialMissingColumns()
    
    if '--rollback' in sys.argv:
        success = migration.down(db_path, 'manual')
    else:
        success = migration.up(db_path, 'manual')
    
    sys.exit(0 if success else 1)