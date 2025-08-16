#!/usr/bin/env python3
"""
Add Missing Columns to Production Database
Specifically addresses the missing columns shown in schema verification
"""

import sqlite3
import os
import shutil
from datetime import datetime

def add_missing_columns_production():
    """Add all missing columns identified in schema verification"""
    
    db_path = '/app/databases/arrow_database.db'
    
    if not os.path.exists(db_path):
        print("❌ Database not found")
        return False
    
    # Create backup
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"{db_path}.column_fix_backup_{timestamp}"
    shutil.copy2(db_path, backup_path)
    print(f"✅ Database backed up to: {backup_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Disable foreign keys temporarily
        cursor.execute("PRAGMA foreign_keys = OFF")
        
        print("\n🔄 Adding missing columns to tables...")
        
        # Missing columns identified from schema verification
        missing_columns = {
            'backup_metadata': {
                'backup_type': 'TEXT DEFAULT "full"',
                'includes': 'TEXT',
                'file_path': 'TEXT',
                'file_size': 'INTEGER'
            },
            'manufacturers': {
                'contact_info': 'TEXT',
                'established': 'INTEGER',
                'arrow_types': 'TEXT',
                'website': 'TEXT'
            },
            'guide_sessions': {
                'session_data': 'TEXT',
                'updated_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
                'setup_id': 'INTEGER',
                'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
            }
        }
        
        total_added = 0
        
        for table_name, columns in missing_columns.items():
            print(f"\n📋 Processing table: {table_name}")
            
            # Check if table exists
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            if not cursor.fetchone():
                print(f"  ⚠️  Table {table_name} does not exist, skipping...")
                continue
            
            # Get existing columns
            cursor.execute(f'PRAGMA table_info({table_name})')
            existing_columns = [col[1] for col in cursor.fetchall()]
            print(f"  Existing columns: {len(existing_columns)}")
            
            # Add missing columns
            for col_name, col_definition in columns.items():
                if col_name not in existing_columns:
                    try:
                        cursor.execute(f'ALTER TABLE {table_name} ADD COLUMN {col_name} {col_definition}')
                        print(f"  ✅ Added {table_name}.{col_name}")
                        total_added += 1
                    except Exception as e:
                        if "duplicate column name" in str(e).lower():
                            print(f"  ℹ️  Column {table_name}.{col_name} already exists")
                        else:
                            print(f"  ❌ Failed to add {table_name}.{col_name}: {e}")
                else:
                    print(f"  ℹ️  Column {table_name}.{col_name} already exists")
        
        # Re-enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Commit changes
        conn.commit()
        
        print(f"\n✅ Column addition completed!")
        print(f"📊 Total columns added: {total_added}")
        
        # Verification
        print(f"\n🔍 Verifying changes...")
        
        for table_name in missing_columns.keys():
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            if cursor.fetchone():
                cursor.execute(f'PRAGMA table_info({table_name})')
                columns = cursor.fetchall()
                print(f"  {table_name}: {len(columns)} columns total")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error adding columns: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

def fix_migration_status_api():
    """Fix the migration status API by ensuring proper migration table structure"""
    
    db_path = '/app/databases/arrow_database.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n🔄 Fixing migration status API...")
        
        # Check if schema_migrations table exists and has correct structure
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='schema_migrations'")
        if not cursor.fetchone():
            print("  Creating schema_migrations table...")
            cursor.execute("""
                CREATE TABLE schema_migrations (
                    version TEXT PRIMARY KEY,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    migration_name TEXT,
                    success BOOLEAN DEFAULT TRUE
                )
            """)
            print("  ✅ Created schema_migrations table")
        else:
            # Check if it has the correct columns
            cursor.execute('PRAGMA table_info(schema_migrations)')
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'version' not in columns:
                print("  ❌ schema_migrations table missing 'version' column - recreating...")
                
                # Back up existing data
                cursor.execute("SELECT * FROM schema_migrations")
                existing_data = cursor.fetchall()
                
                # Drop and recreate
                cursor.execute("DROP TABLE schema_migrations")
                cursor.execute("""
                    CREATE TABLE schema_migrations (
                        version TEXT PRIMARY KEY,
                        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        migration_name TEXT,
                        success BOOLEAN DEFAULT TRUE
                    )
                """)
                
                # Try to restore data
                if existing_data:
                    for row in existing_data:
                        try:
                            if len(row) >= 1:
                                version = str(row[0]) if row[0] else '000'
                                applied_at = row[1] if len(row) > 1 else datetime.now().isoformat()
                                migration_name = row[2] if len(row) > 2 else f"Migration {version}"
                                success = row[3] if len(row) > 3 else True
                                
                                cursor.execute("""
                                    INSERT OR REPLACE INTO schema_migrations (version, applied_at, migration_name, success)
                                    VALUES (?, ?, ?, ?)
                                """, (version, applied_at, migration_name, success))
                        except Exception as e:
                            print(f"    Warning: Could not restore migration record: {e}")
                
                print("  ✅ Fixed schema_migrations table structure")
            else:
                print("  ✅ schema_migrations table structure is correct")
        
        # Ensure migration 023 is marked as applied
        cursor.execute("SELECT version FROM schema_migrations WHERE version = '023'")
        if not cursor.fetchone():
            cursor.execute("""
                INSERT OR REPLACE INTO schema_migrations (version, migration_name, applied_at)
                VALUES ('023', 'Database Consolidation', CURRENT_TIMESTAMP)
            """)
            print("  ✅ Marked migration 023 as applied")
        
        conn.commit()
        conn.close()
        
        print("  ✅ Migration status API should now work")
        return True
        
    except Exception as e:
        print(f"  ❌ Error fixing migration API: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Adding Missing Columns to Production Database")
    print("=" * 60)
    
    # Check if running in Docker container
    if os.path.exists('/.dockerenv'):
        print("🐳 Running inside Docker container")
    
    success1 = add_missing_columns_production()
    success2 = fix_migration_status_api()
    
    if success1 and success2:
        print("\n✅ All fixes completed successfully!")
        print("🔄 Please restart the API container:")
        print("   docker restart <container-name>")
        print("\n🔍 After restart, test the admin panel migration status")
    else:
        print("\n❌ Some fixes failed. Check the logs above.")
    
    print("=" * 60)