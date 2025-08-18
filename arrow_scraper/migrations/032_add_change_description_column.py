#!/usr/bin/env python3
"""
Migration 032: Add change_description column to change log tables

The change_log_service.py code expects a change_description column, but the database 
tables only have change_reason. This migration adds the missing change_description
column to all relevant change log tables.

Author: Claude
Date: 2025-08-18
"""

import sqlite3
import sys
from pathlib import Path

# Add the parent directory to sys.path so we can import BaseMigration
sys.path.append(str(Path(__file__).parent.parent))
from database_migration_manager import BaseMigration

class Migration032AddChangeDescriptionColumn(BaseMigration):
    def __init__(self):
        super().__init__()
        self.version = "032"
        self.description = "Add change_description column to change log tables"
        self.dependencies = ["031"]  # Depends on user profile columns
        self.environments = ['all']

    def up(self, db_path, environment='development'):
        """Add change_description column to change log tables"""
        print(f"🔄 Adding change_description column to change log tables in: {db_path}")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        added_count = 0
        
        try:
            # Get list of tables that might need change_description column
            tables_to_check = [
                'setup_change_log',
                'equipment_change_log', 
                'arrow_change_log'
            ]
            
            for table in tables_to_check:
                # Check if table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
                if not cursor.fetchone():
                    print(f"⚠️  Table {table} does not exist, skipping")
                    continue
                
                # Get current columns
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [row[1] for row in cursor.fetchall()]
                print(f"📋 Current {table} columns: {columns}")
                
                # Add change_description column if it doesn't exist
                if 'change_description' not in columns:
                    try:
                        cursor.execute(f"ALTER TABLE {table} ADD COLUMN change_description TEXT DEFAULT NULL")
                        print(f"✅ Added change_description column to {table}")
                        added_count += 1
                    except sqlite3.OperationalError as e:
                        print(f"⚠️  Warning adding change_description to {table}: {e}")
                else:
                    print(f"✅ change_description column already exists in {table}")
            
            conn.commit()
            print(f"✅ Migration 032 completed successfully. Added {added_count} columns.")
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Migration 032 failed: {e}")
            return False
        finally:
            conn.close()

    def down(self, db_path, environment='development'):
        """Remove change_description column from change log tables"""
        print(f"🔄 Removing change_description column from change log tables in: {db_path}")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # SQLite doesn't support DROP COLUMN directly, so we'd need to recreate tables
            # For now, just print a warning
            print("⚠️  SQLite doesn't support DROP COLUMN. Manual cleanup required if rolling back.")
            
        except Exception as e:
            print(f"❌ Migration 032 rollback failed: {e}")
            raise
        finally:
            conn.close()

if __name__ == "__main__":
    migration = Migration032AddChangeDescriptionColumn()
    
    # Use environment variable or default path
    import os
    db_path = os.getenv('ARROW_DATABASE_PATH', '/home/paal/archerytools/arrow_scraper/databases/arrow_database.db')
    
    print(f"Running migration {migration.version}: {migration.description}")
    migration.up(db_path)
    print("Migration completed!")