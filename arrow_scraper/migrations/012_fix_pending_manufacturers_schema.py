#!/usr/bin/env python3
"""
Migration 012: Fix Pending Manufacturers Schema
Adds missing columns to pending_manufacturers table that were missing from Migration 011
"""

import sqlite3
from pathlib import Path
import os

class Migration:
    def __init__(self):
        self.version = 12
        self.description = "Fix pending manufacturers schema - add missing columns"
        
    def get_user_db_path(self):
        """Get the user database path with proper fallback logic"""
        # Try production path first
        production_path = Path("/app/user_data/user_data.db")
        if production_path.parent.exists():
            return str(production_path)
        
        # Try container path
        container_path = Path("/app/databases/user_data.db") 
        if container_path.parent.exists():
            return str(container_path)
            
        # Fallback to local development
        local_path = Path(__file__).parent.parent / "databases" / "user_data.db"
        return str(local_path)
    
    def up(self):
        """Apply the migration - add missing columns to pending_manufacturers table"""
        user_db_path = self.get_user_db_path()
        print(f"🔧 Applying Migration 012 to user database: {user_db_path}")
        
        try:
            conn = sqlite3.connect(user_db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Check if pending_manufacturers table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pending_manufacturers'")
            if not cursor.fetchone():
                print("❌ pending_manufacturers table does not exist! Run Migration 011 first.")
                return False
            
            # Get current table structure
            cursor.execute("PRAGMA table_info(pending_manufacturers)")
            existing_columns = [col[1] for col in cursor.fetchall()]
            print(f"   Current columns: {', '.join(existing_columns)}")
            
            # List of columns to add with their definitions
            columns_to_add = [
                ('normalized_name', 'TEXT'),
                ('user_count', 'INTEGER DEFAULT 1'),
                ('approved_by_admin_id', 'INTEGER'),
                ('approved_at', 'TIMESTAMP'),
                ('rejection_reason', 'TEXT'),
                ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
                ('updated_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
            ]
            
            added_count = 0
            
            # Add missing columns
            for column_name, column_def in columns_to_add:
                if column_name not in existing_columns:
                    try:
                        cursor.execute(f'ALTER TABLE pending_manufacturers ADD COLUMN {column_name} {column_def}')
                        print(f"   ✅ Added column: {column_name}")
                        added_count += 1
                    except Exception as e:
                        print(f"   ❌ Failed to add {column_name}: {e}")
                        conn.rollback()
                        return False
                else:
                    print(f"   ✅ Column {column_name} already exists")
            
            # Update existing records to have proper created_at and updated_at if they're NULL
            if 'created_at' in [col[0] for col in columns_to_add]:
                cursor.execute('''
                    UPDATE pending_manufacturers 
                    SET created_at = CURRENT_TIMESTAMP 
                    WHERE created_at IS NULL
                ''')
                print("   ✅ Updated NULL created_at values")
            
            if 'updated_at' in [col[0] for col in columns_to_add]:
                cursor.execute('''
                    UPDATE pending_manufacturers 
                    SET updated_at = CURRENT_TIMESTAMP 
                    WHERE updated_at IS NULL
                ''')
                print("   ✅ Updated NULL updated_at values")
            
            # Update normalized_name for existing records
            cursor.execute("SELECT id, name FROM pending_manufacturers WHERE normalized_name IS NULL")
            records_to_update = cursor.fetchall()
            for record in records_to_update:
                normalized_name = record['name'].lower().strip()
                cursor.execute("UPDATE pending_manufacturers SET normalized_name = ? WHERE id = ?", 
                             (normalized_name, record['id']))
            
            if records_to_update:
                print(f"   ✅ Updated normalized_name for {len(records_to_update)} records")
            
            conn.commit()
            
            # Verify final structure
            cursor.execute("PRAGMA table_info(pending_manufacturers)")
            final_columns = [col[1] for col in cursor.fetchall()]
            print(f"   📋 Final table has {len(final_columns)} columns")
            
            print(f"✅ Migration 012 applied successfully - added {added_count} new columns")
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Migration 012 failed: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return False
    
    def down(self):
        """Reverse the migration - remove the added columns"""
        print("⚠️  Migration 012 rollback not supported")
        print("   SQLite doesn't support dropping columns easily")
        print("   Manual intervention required if rollback needed")
        return True

def run_migration():
    """Run this migration directly"""
    migration = Migration()
    print(f"🔄 Running Migration {migration.version}: {migration.description}")
    return migration.up()

if __name__ == "__main__":
    success = run_migration()
    exit(0 if success else 1)