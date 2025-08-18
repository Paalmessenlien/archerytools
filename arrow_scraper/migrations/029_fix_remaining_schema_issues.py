#!/usr/bin/env python3
"""
Migration 029: Fix Remaining Schema Verification Issues
Addresses final schema verification warnings by adding missing columns 
and creating compatibility aliases for column name mismatches.

Date: 2025-08-18
Author: Claude Code Enhancement  
Purpose: Complete schema verification compliance
"""

import sqlite3
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database_migration_manager import BaseMigration

class Migration029FixRemainingSchemaIssues(BaseMigration):
    def __init__(self):
        super().__init__()
        self.version = "029"
        self.description = "Fix Remaining Schema Verification Issues"
        self.dependencies = ["028"]
        self.environments = ['all']
        self.target_database = 'arrow'
    
    def up(self, db_path: str, environment: str) -> bool:
        """
        Fix remaining schema verification issues
        """
        try:
            print("🔧 Fixing remaining schema verification issues...")
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check which tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = {row[0] for row in cursor.fetchall()}
            
            added_count = 0
            
            # 1. Add missing bow_equipment.updated_at
            if 'bow_equipment' in existing_tables:
                cursor.execute("PRAGMA table_info(bow_equipment)")
                existing_cols = {row[1] for row in cursor.fetchall()}
                
                if 'updated_at' not in existing_cols:
                    try:
                        cursor.execute("ALTER TABLE bow_equipment ADD COLUMN updated_at TIMESTAMP")
                        print("   ✅ Added bow_equipment.updated_at")
                        added_count += 1
                    except sqlite3.OperationalError as e:
                        print(f"   ⚠️  Could not add bow_equipment.updated_at: {e}")
            
            # 2. Add legacy bow_setups columns (for backward compatibility)
            if 'bow_setups' in existing_tables:
                cursor.execute("PRAGMA table_info(bow_setups)")
                existing_cols = {row[1] for row in cursor.fetchall()}
                
                legacy_bow_columns = [
                    ('setup_name', 'TEXT'),  # Alias for name
                    ('brace_height', 'REAL'),  # Optional specification
                    ('bow_make', 'TEXT'),  # Legacy field for compound_brand/riser_brand
                    ('bow_model', 'TEXT'),  # Legacy field for compound_model/riser_model
                    ('arrow_length', 'REAL'),  # May be needed for some workflows
                    ('point_weight', 'REAL'),  # May be needed for some workflows
                ]
                
                for col_name, col_def in legacy_bow_columns:
                    if col_name not in existing_cols:
                        try:
                            cursor.execute(f"ALTER TABLE bow_setups ADD COLUMN {col_name} {col_def}")
                            print(f"   ✅ Added bow_setups.{col_name}")
                            added_count += 1
                        except sqlite3.OperationalError as e:
                            print(f"   ⚠️  Could not add bow_setups.{col_name}: {e}")
            
            # 3. Add users.picture (legacy field)
            if 'users' in existing_tables:
                cursor.execute("PRAGMA table_info(users)")
                existing_cols = {row[1] for row in cursor.fetchall()}
                
                if 'picture' not in existing_cols:
                    try:
                        cursor.execute("ALTER TABLE users ADD COLUMN picture TEXT")
                        print("   ✅ Added users.picture")
                        added_count += 1
                    except sqlite3.OperationalError as e:
                        print(f"   ⚠️  Could not add users.picture: {e}")
            
            # 4. Fix guide_sessions table - add missing columns
            if 'guide_sessions' in existing_tables:
                cursor.execute("PRAGMA table_info(guide_sessions)")
                existing_cols = {row[1] for row in cursor.fetchall()}
                
                guide_columns = [
                    ('created_at', 'TIMESTAMP'),
                    ('updated_at', 'TIMESTAMP'),
                    ('setup_id', 'INTEGER'),  # Alias for bow_setup_id
                    ('session_data', 'TEXT'),  # JSON field for session state
                ]
                
                for col_name, col_def in guide_columns:
                    if col_name not in existing_cols:
                        try:
                            cursor.execute(f"ALTER TABLE guide_sessions ADD COLUMN {col_name} {col_def}")
                            print(f"   ✅ Added guide_sessions.{col_name}")
                            added_count += 1
                        except sqlite3.OperationalError as e:
                            print(f"   ⚠️  Could not add guide_sessions.{col_name}: {e}")
            
            # 5. Add equipment_field_standards compatibility columns
            # (These are aliases for existing columns with different names)
            if 'equipment_field_standards' in existing_tables:
                cursor.execute("PRAGMA table_info(equipment_field_standards)")
                existing_cols = {row[1] for row in cursor.fetchall()}
                
                # Add alias columns that map to existing functionality
                alias_columns = [
                    ('label', 'TEXT'),      # Alias for field_label  
                    ('unit', 'TEXT'),       # Alias for field_unit
                    ('display_order', 'INTEGER'),  # Alias for field_order
                    ('field_options', 'TEXT'),     # Alias for dropdown_options
                    ('required', 'BOOLEAN'),       # Alias for is_required
                ]
                
                for col_name, col_def in alias_columns:
                    if col_name not in existing_cols:
                        try:
                            cursor.execute(f"ALTER TABLE equipment_field_standards ADD COLUMN {col_name} {col_def}")
                            print(f"   ✅ Added equipment_field_standards.{col_name} (compatibility alias)")
                            added_count += 1
                        except sqlite3.OperationalError as e:
                            print(f"   ⚠️  Could not add equipment_field_standards.{col_name}: {e}")
            
            # 6. Populate alias columns with data from main columns
            print("   🔄 Populating compatibility alias columns...")
            try:
                # Update alias columns to match their primary counterparts
                cursor.execute("""
                    UPDATE equipment_field_standards 
                    SET 
                        label = field_label,
                        unit = field_unit, 
                        display_order = field_order,
                        field_options = dropdown_options,
                        required = is_required
                    WHERE 1=1
                """)
                
                # Update guide_sessions setup_id to match bow_setup_id
                cursor.execute("""
                    UPDATE guide_sessions 
                    SET setup_id = bow_setup_id 
                    WHERE setup_id IS NULL AND bow_setup_id IS NOT NULL
                """)
                
                print("   ✅ Updated compatibility alias columns")
                
            except sqlite3.OperationalError as e:
                print(f"   ⚠️  Could not populate alias columns: {e}")
            
            conn.commit()
            conn.close()
            
            print(f"✅ Fixed {added_count} schema verification issues")
            return True
            
        except Exception as e:
            print(f"❌ Failed to fix schema issues: {e}")
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
migration = Migration029FixRemainingSchemaIssues()

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python 029_fix_remaining_schema_issues.py <database_path>")
        sys.exit(1)
    
    db_path = sys.argv[1]
    migration = Migration029FixRemainingSchemaIssues()
    
    if '--rollback' in sys.argv:
        success = migration.down(db_path, 'manual')
    else:
        success = migration.up(db_path, 'manual')
    
    sys.exit(0 if success else 1)