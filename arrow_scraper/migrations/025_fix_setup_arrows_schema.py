#!/usr/bin/env python3
"""
Migration 025: Fix setup_arrows Schema - Add Missing Columns
Add missing columns from old user database schema to unified database

This migration fixes the setup_arrows table schema by adding missing columns
that exist in the old user database but are missing in the unified database.

Date: 2025-08-16
Author: Claude Code Enhancement  
Issue: Missing fletching_weight and bushing_weight columns in setup_arrows table
Solution: Add missing columns to match original user database schema

Missing Columns:
- fletching_weight REAL (for fletching component weight)
- bushing_weight REAL (for bushing component weight, used by API)

Schema Comparison:
Old: id, setup_id, arrow_id, arrow_length, point_weight, calculated_spine, 
     compatibility_score, notes, created_at, nock_weight, fletching_weight,
     insert_weight, wrap_weight, bushing_weight, performance_data

New: id, setup_id, arrow_id, arrow_length, point_weight, calculated_spine,
     compatibility_score, notes, performance_data, nock_weight, insert_weight,
     wrap_weight, created_at

Missing: fletching_weight, bushing_weight
"""

import sqlite3
import os
import sys
from pathlib import Path

# Add parent directory to path to import migration base class
sys.path.append(str(Path(__file__).parent.parent))

class Migration:
    def __init__(self):
        self.version = "025"
        self.description = "Fix setup_arrows Schema - Add Missing Columns (fletching_weight, bushing_weight)"
        self.dependencies = ["024"]  # Depends on unified database migration
        self.environments = ['all']
        self.target_database = 'arrow'  # Unified database

    def up(self, db_path: str, environment: str) -> bool:
        """Add missing columns to setup_arrows table"""
        try:
            print("🔄 Adding missing columns to setup_arrows table...")
            print("=" * 60)
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if columns already exist
            cursor.execute("PRAGMA table_info(setup_arrows)")
            existing_columns = [row[1] for row in cursor.fetchall()]
            
            columns_to_add = []
            
            if 'fletching_weight' not in existing_columns:
                columns_to_add.append(('fletching_weight', 'REAL', '0.0'))
                
            if 'bushing_weight' not in existing_columns:
                columns_to_add.append(('bushing_weight', 'REAL', '0.0'))
                
            if not columns_to_add:
                print("✅ All columns already exist in setup_arrows table")
                return True
                
            print(f"📝 Adding {len(columns_to_add)} missing columns:")
            
            for column_name, column_type, default_value in columns_to_add:
                print(f"   • {column_name} {column_type} DEFAULT {default_value}")
                cursor.execute(f'''
                    ALTER TABLE setup_arrows 
                    ADD COLUMN {column_name} {column_type} DEFAULT {default_value}
                ''')
                
            conn.commit()
            
            # Verify the additions
            cursor.execute("PRAGMA table_info(setup_arrows)")
            final_columns = [row[1] for row in cursor.fetchall()]
            
            print("\n🔍 Final setup_arrows schema:")
            for i, col in enumerate(final_columns):
                print(f"   {i}: {col}")
                
            print("\n✅ Successfully added missing columns to setup_arrows table")
            print("🎯 API can now use both bushing_weight and fletching_weight columns")
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Failed to add missing columns: {e}")
            import traceback
            traceback.print_exc()
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            return False

    def down(self, db_path: str, environment: str) -> bool:
        """Remove the added columns (rollback)"""
        print("⚠️  ROLLBACK: Cannot remove columns with SQLite ALTER TABLE")
        print("   SQLite does not support DROP COLUMN")
        print("   Manual intervention required if rollback needed")
        return True

# Create the migration instance for discovery
migration = Migration()

def main():
    """Main function for standalone execution"""
    import sys
    if len(sys.argv) < 2:
        print("Usage: python 025_fix_setup_arrows_schema.py <arrow_database_path> [--rollback]")
        sys.exit(1)
    
    arrow_db_path = sys.argv[1]
    rollback = '--rollback' in sys.argv
    
    migration = Migration()
    
    try:
        if rollback:
            print("🔄 Rolling back setup_arrows schema changes...")
            success = migration.down(arrow_db_path, 'manual')
        else:
            print("🚀 Applying setup_arrows schema fixes...")
            success = migration.up(arrow_db_path, 'manual')
        
        if success:
            action = "rolled back" if rollback else "applied"
            print(f"✅ Migration 025 {action} successfully!")
        else:
            print("❌ Migration 025 failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()