#!/usr/bin/env python3
"""
Migration 024: Add Missing Schema Columns
Adds all missing columns identified in schema verification to ensure complete unified database schema
"""

import sqlite3
import os
from pathlib import Path

class Migration024:
    def __init__(self):
        self.version = "024"
        self.description = "Add Missing Schema Columns for Complete Unified Database"
        
    def get_database_path(self):
        """Get the database path, prioritizing environment variables"""
        # Check environment variable first (for Docker)
        db_path = os.getenv('ARROW_DATABASE_PATH')
        if db_path and os.path.exists(db_path):
            return db_path
            
        # Try common paths
        possible_paths = [
            '/app/databases/arrow_database.db',  # Docker production
            './databases/arrow_database.db',     # Local development
            '../databases/arrow_database.db',    # From migrations directory
            './arrow_database.db'               # Legacy location
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        raise FileNotFoundError("Database file not found in any expected location")
    
    def up(self):
        """Apply the migration - add missing columns"""
        db_path = self.get_database_path()
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Disable foreign keys temporarily
            cursor.execute("PRAGMA foreign_keys = OFF")
            
            print(f"🔄 Migration {self.version}: Adding missing schema columns...")
            
            # Define all missing columns with their table and definition
            missing_columns = [
                # backup_metadata table columns
                ('backup_metadata', 'backup_type', 'TEXT DEFAULT "full"'),
                ('backup_metadata', 'includes', 'TEXT'),
                ('backup_metadata', 'file_path', 'TEXT'),
                ('backup_metadata', 'file_size', 'INTEGER'),
                
                # manufacturers table columns
                ('manufacturers', 'contact_info', 'TEXT'),
                ('manufacturers', 'established', 'INTEGER'),
                ('manufacturers', 'arrow_types', 'TEXT'),
                ('manufacturers', 'website', 'TEXT'),
                
                # guide_sessions table columns  
                ('guide_sessions', 'session_data', 'TEXT'),
                ('guide_sessions', 'updated_at', 'TIMESTAMP'),
                ('guide_sessions', 'setup_id', 'INTEGER'),
                ('guide_sessions', 'created_at', 'TIMESTAMP'),
                
                # bow_equipment table columns (in case they're missing)
                ('bow_equipment', 'setup_id', 'INTEGER'),
                ('bow_equipment', 'installed_at', 'TIMESTAMP'),
                ('bow_equipment', 'manufacturer', 'TEXT'),
                ('bow_equipment', 'category', 'TEXT'),
                ('bow_equipment', 'model', 'TEXT'),
                ('bow_equipment', 'updated_at', 'TIMESTAMP'),
                ('bow_equipment', 'specifications', 'TEXT'),
                
                # bow_setups table columns (in case they're missing)
                ('bow_setups', 'bow_make', 'TEXT'),
                ('bow_setups', 'setup_name', 'TEXT'),
                ('bow_setups', 'updated_at', 'TIMESTAMP'),
                ('bow_setups', 'brace_height', 'REAL'),
                ('bow_setups', 'bow_model', 'TEXT'),
                
                # users table columns (in case they're missing)
                ('users', 'updated_at', 'TIMESTAMP'),
                ('users', 'last_login', 'TIMESTAMP'),
                ('users', 'picture', 'TEXT'),
                ('users', 'is_admin', 'BOOLEAN DEFAULT FALSE'),
            ]
            
            total_added = 0
            
            for table_name, column_name, column_definition in missing_columns:
                try:
                    # Check if table exists
                    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
                    if not cursor.fetchone():
                        print(f"  ⚠️  Table {table_name} does not exist, skipping column {column_name}")
                        continue
                    
                    # Check if column already exists
                    cursor.execute(f'PRAGMA table_info({table_name})')
                    existing_columns = [col[1] for col in cursor.fetchall()]
                    
                    if column_name not in existing_columns:
                        # Add the column
                        cursor.execute(f'ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}')
                        print(f"  ✅ Added {table_name}.{column_name}")
                        total_added += 1
                    else:
                        print(f"  ℹ️  Column {table_name}.{column_name} already exists")
                        
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e).lower():
                        print(f"  ℹ️  Column {table_name}.{column_name} already exists")
                    else:
                        print(f"  ❌ Failed to add {table_name}.{column_name}: {e}")
                        raise
            
            # Ensure schema_migrations table has correct structure
            self._fix_schema_migrations_table(cursor)
            
            # Re-enable foreign keys
            cursor.execute("PRAGMA foreign_keys = ON")
            
            # Commit all changes
            conn.commit()
            
            print(f"✅ Migration {self.version} completed successfully")
            print(f"📊 Total columns added: {total_added}")
            
            return True
            
        except Exception as e:
            print(f"❌ Migration {self.version} failed: {e}")
            if 'conn' in locals():
                conn.rollback()
            raise
        finally:
            if 'conn' in locals():
                conn.close()
    
    def _fix_schema_migrations_table(self, cursor):
        """Ensure schema_migrations table has correct structure for API compatibility"""
        try:
            # Check if schema_migrations table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='schema_migrations'")
            if not cursor.fetchone():
                # Create the table if it doesn't exist
                cursor.execute("""
                    CREATE TABLE schema_migrations (
                        version TEXT PRIMARY KEY,
                        applied_at TIMESTAMP,
                        migration_name TEXT,
                        success BOOLEAN DEFAULT TRUE
                    )
                """)
                print("  ✅ Created schema_migrations table")
                return
            
            # Check table structure
            cursor.execute('PRAGMA table_info(schema_migrations)')
            columns = [col[1] for col in cursor.fetchall()]
            
            required_columns = ['version', 'applied_at', 'migration_name', 'success']
            missing_columns = [col for col in required_columns if col not in columns]
            
            if missing_columns:
                print(f"  🔄 schema_migrations table missing columns: {missing_columns}")
                
                # Back up existing data
                cursor.execute("SELECT * FROM schema_migrations")
                existing_data = cursor.fetchall()
                existing_columns = columns.copy()
                
                # Drop and recreate table with correct structure
                cursor.execute("DROP TABLE schema_migrations")
                cursor.execute("""
                    CREATE TABLE schema_migrations (
                        version TEXT PRIMARY KEY,
                        applied_at TIMESTAMP,
                        migration_name TEXT,
                        success BOOLEAN DEFAULT TRUE
                    )
                """)
                
                # Restore data with column mapping
                for row in existing_data:
                    try:
                        row_dict = dict(zip(existing_columns, row))
                        
                        version = str(row_dict.get('version', row_dict.get('id', '000')))
                        applied_at = row_dict.get('applied_at', row_dict.get('timestamp'))
                        migration_name = row_dict.get('migration_name', row_dict.get('name', f'Migration {version}'))
                        success = row_dict.get('success', True)
                        
                        cursor.execute("""
                            INSERT OR REPLACE INTO schema_migrations (version, applied_at, migration_name, success)
                            VALUES (?, ?, ?, ?)
                        """, (version, applied_at, migration_name, success))
                    except Exception as e:
                        print(f"    Warning: Could not restore migration record {row}: {e}")
                
                print("  ✅ Fixed schema_migrations table structure")
            else:
                print("  ✅ schema_migrations table structure is correct")
                
        except Exception as e:
            print(f"  ❌ Error fixing schema_migrations table: {e}")
            raise
    
    def down(self):
        """Rollback the migration - remove added columns"""
        # Note: SQLite doesn't support DROP COLUMN, so rollback is not implemented
        # In practice, these columns are safe to keep
        print(f"⚠️  Migration {self.version} rollback not implemented (SQLite limitation)")
        print("   Added columns are safe to keep and don't affect functionality")
        return True
    
    def validate(self):
        """Validate that the migration was applied correctly"""
        db_path = self.get_database_path()
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check key tables have expected columns
            tables_to_check = {
                'backup_metadata': ['backup_type', 'includes', 'file_path', 'file_size'],
                'manufacturers': ['contact_info', 'established', 'arrow_types', 'website'],
                'guide_sessions': ['session_data', 'updated_at', 'setup_id', 'created_at'],
                'schema_migrations': ['version', 'applied_at', 'migration_name', 'success']
            }
            
            all_valid = True
            
            for table_name, expected_columns in tables_to_check.items():
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
                if cursor.fetchone():
                    cursor.execute(f'PRAGMA table_info({table_name})')
                    actual_columns = [col[1] for col in cursor.fetchall()]
                    
                    missing = [col for col in expected_columns if col not in actual_columns]
                    if missing:
                        print(f"❌ Table {table_name} missing columns: {missing}")
                        all_valid = False
                    else:
                        print(f"✅ Table {table_name} has all expected columns")
                else:
                    print(f"⚠️  Table {table_name} does not exist")
            
            conn.close()
            return all_valid
            
        except Exception as e:
            print(f"❌ Validation failed: {e}")
            return False

# Migration interface for the migration manager
def get_migration():
    """Return migration instance for the migration manager"""
    return Migration024()

if __name__ == "__main__":
    # Allow running migration directly
    migration = Migration024()
    print(f"Running Migration {migration.version}: {migration.description}")
    
    try:
        success = migration.up()
        if success:
            print("\n🔍 Validating migration...")
            validation_success = migration.validate()
            if validation_success:
                print("✅ Migration completed and validated successfully!")
            else:
                print("⚠️  Migration completed but validation found issues")
        else:
            print("❌ Migration failed")
    except Exception as e:
        print(f"❌ Migration error: {e}")
        import traceback
        print(traceback.format_exc())