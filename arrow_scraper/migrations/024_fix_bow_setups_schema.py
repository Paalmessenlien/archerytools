#!/usr/bin/env python3
"""
Migration 024: Fix Bow Setups Schema Conflict
Fixes the bow_setups table schema conflict between arrow and user databases

This migration resolves the conflict where arrow_database.db has a different
bow_setups schema than user_data.db, preventing proper consolidation.

Date: 2025-08-17
Author: Claude Code Enhancement
Issue: Schema mismatch preventing database consolidation
Solution: Rename old bow_setups table and create proper unified schema
"""

import sqlite3
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database_migration_manager import BaseMigration

class Migration024FixBowSetupsSchema(BaseMigration):
    def __init__(self):
        super().__init__()
        self.version = "024"
        self.description = "Fix Bow Setups Schema Conflict for Database Consolidation"
        self.dependencies = ["023"]
        self.environments = ['all']
        self.target_database = 'arrow'
    
    def up(self, db_path: str, environment: str) -> bool:
        """
        Fix bow_setups schema conflict
        """
        try:
            print("🔧 Fixing bow_setups schema conflict...")
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if old bow_setups exists and handle existing bow_setups_old
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bow_setups'")
            if cursor.fetchone():
                # Check if bow_setups_old already exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bow_setups_old'")
                if cursor.fetchone():
                    print("📋 Found existing bow_setups_old table - dropping it first")
                    cursor.execute("DROP TABLE bow_setups_old")
                
                print("📋 Renaming existing bow_setups table to bow_setups_old")
                cursor.execute("ALTER TABLE bow_setups RENAME TO bow_setups_old")
            
            # Create new bow_setups with proper schema
            print("🏗️  Creating new bow_setups table with unified schema...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bow_setups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    bow_type TEXT NOT NULL,
                    draw_weight REAL NOT NULL,
                    insert_weight REAL,
                    description TEXT,
                    bow_usage TEXT,
                    riser_brand TEXT,
                    riser_model TEXT,
                    riser_length TEXT,
                    limb_brand TEXT,
                    limb_model TEXT,
                    limb_length TEXT,
                    compound_brand TEXT,
                    compound_model TEXT,
                    ibo_speed REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            """)
            
            # Migrate data from old table if it exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bow_setups_old'")
            if cursor.fetchone():
                print("📦 Migrating data from bow_setups_old...")
                # First, check what columns exist in the old table
                cursor.execute("PRAGMA table_info(bow_setups_old)")
                columns = [row[1] for row in cursor.fetchall()]
                
                # Build dynamic INSERT statement based on available columns
                old_cols = []
                new_cols = []
                for col in ['id', 'user_id', 'name', 'bow_type', 'draw_weight', 'insert_weight', 
                           'description', 'bow_usage', 'riser_brand', 'riser_model', 'riser_length',
                           'limb_brand', 'limb_model', 'limb_length', 'compound_brand', 'compound_model',
                           'ibo_speed', 'created_at']:
                    if col in columns:
                        old_cols.append(col)
                        new_cols.append(col)
                
                if old_cols:
                    cursor.execute(f"""
                        INSERT INTO bow_setups ({', '.join(new_cols)})
                        SELECT {', '.join(old_cols)}
                        FROM bow_setups_old
                    """)
                    rows_migrated = cursor.rowcount
                    print(f"   ✅ Migrated {rows_migrated} rows from old table")
                else:
                    print("   ⚠️  No compatible columns found for migration")
            
            conn.commit()
            conn.close()
            
            print("✅ Bow setups schema fixed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to fix schema: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def down(self, db_path: str, environment: str) -> bool:
        """
        Rollback: Restore old bow_setups table
        """
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Drop new table
            cursor.execute("DROP TABLE IF EXISTS bow_setups")
            
            # Restore old table if it exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bow_setups_old'")
            if cursor.fetchone():
                cursor.execute("ALTER TABLE bow_setups_old RENAME TO bow_setups")
            
            conn.commit()
            conn.close()
            
            print("✅ Rollback completed")
            return True
            
        except Exception as e:
            print(f"❌ Rollback failed: {e}")
            return False

# Create migration instance for discovery
migration = Migration024FixBowSetupsSchema()

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python 024_fix_bow_setups_schema.py <database_path>")
        sys.exit(1)
    
    db_path = sys.argv[1]
    migration = Migration024FixBowSetupsSchema()
    
    if '--rollback' in sys.argv:
        success = migration.down(db_path, 'manual')
    else:
        success = migration.up(db_path, 'manual')
    
    sys.exit(0 if success else 1)