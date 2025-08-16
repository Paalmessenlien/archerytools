#!/usr/bin/env python3
"""
Robust Production Database Schema Fix Script
Handles different migration table schemas and applies consolidation migration
"""

import sqlite3
import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

def backup_database(db_path):
    """Create a backup before making changes"""
    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    try:
        shutil.copy2(db_path, backup_path)
        print(f"✅ Database backed up to: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"❌ Failed to backup database: {e}")
        return None

def fix_migration_table(cursor):
    """Fix or recreate the schema_migrations table with proper structure"""
    try:
        # Check if table exists and its structure
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='schema_migrations'")
        if cursor.fetchone():
            print("🔍 Checking existing schema_migrations table structure...")
            
            # Get current structure
            cursor.execute('PRAGMA table_info(schema_migrations)')
            columns = [col[1] for col in cursor.fetchall()]
            print(f"   Current columns: {columns}")
            
            # Check if we have the required columns
            required_columns = ['version', 'applied_at', 'migration_name', 'success']
            missing_columns = [col for col in required_columns if col not in columns]
            
            if missing_columns:
                print(f"   Missing columns: {missing_columns}")
                print("🔄 Recreating schema_migrations table with proper structure...")
                
                # Backup existing data
                cursor.execute("SELECT * FROM schema_migrations")
                existing_data = cursor.fetchall()
                print(f"   Backing up {len(existing_data)} existing migration records...")
                
                # Drop and recreate table
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
                for row in existing_data:
                    try:
                        # Try to map old data to new structure
                        if len(row) >= 1:
                            version = str(row[0])
                            applied_at = row[1] if len(row) > 1 else datetime.now().isoformat()
                            migration_name = row[2] if len(row) > 2 else f"Migration {version}"
                            success = row[3] if len(row) > 3 else True
                            
                            cursor.execute("""
                                INSERT INTO schema_migrations (version, applied_at, migration_name, success)
                                VALUES (?, ?, ?, ?)
                            """, (version, applied_at, migration_name, success))
                    except Exception as e:
                        print(f"   Warning: Could not restore migration record {row}: {e}")
                
                print("✅ Schema_migrations table recreated")
            else:
                print("✅ Schema_migrations table structure is correct")
        else:
            print("🔄 Creating schema_migrations table...")
            cursor.execute("""
                CREATE TABLE schema_migrations (
                    version TEXT PRIMARY KEY,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    migration_name TEXT,
                    success BOOLEAN DEFAULT TRUE
                )
            """)
            print("✅ Schema_migrations table created")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing migration table: {e}")
        return False

def check_migration_applied(cursor, version):
    """Check if a migration has been applied"""
    try:
        cursor.execute("SELECT version FROM schema_migrations WHERE version = ?", (version,))
        return cursor.fetchone() is not None
    except Exception as e:
        print(f"Warning: Could not check migration {version}: {e}")
        return False

def apply_consolidation_migration(cursor):
    """Apply the database consolidation migration manually"""
    
    print("🔄 Applying database consolidation migration...")
    
    # Check if user tables already exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    if cursor.fetchone():
        print("✅ User tables already exist - consolidation may be partially complete")
        
        # Still need to check if all required columns exist
        print("🔍 Checking for missing columns in existing tables...")
        
        # Check users table
        cursor.execute('PRAGMA table_info(users)')
        user_columns = [col[1] for col in cursor.fetchall()]
        required_user_columns = ['id', 'google_id', 'email', 'name', 'picture', 'is_admin', 'created_at', 'updated_at', 'last_login']
        missing_user_columns = [col for col in required_user_columns if col not in user_columns]
        
        for col in missing_user_columns:
            try:
                if col == 'updated_at':
                    cursor.execute('ALTER TABLE users ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
                elif col == 'last_login':
                    cursor.execute('ALTER TABLE users ADD COLUMN last_login TIMESTAMP')
                elif col == 'picture':
                    cursor.execute('ALTER TABLE users ADD COLUMN picture TEXT')
                elif col == 'is_admin':
                    cursor.execute('ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE')
                print(f"  ✅ Added missing column users.{col}")
            except Exception as e:
                print(f"  ⚠️  Could not add users.{col}: {e}")
        
        return True
    
    try:
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                google_id TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                name TEXT,
                picture TEXT,
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        """)
        print("✅ Created users table")
        
        # Create bow_setups table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bow_setups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                setup_name TEXT NOT NULL,
                bow_type TEXT NOT NULL,
                bow_make TEXT,
                bow_model TEXT,
                brace_height REAL,
                draw_weight REAL NOT NULL,
                arrow_length REAL NOT NULL,
                point_weight REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)
        print("✅ Created bow_setups table")
        
        # Create guide_sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS guide_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                setup_id INTEGER,
                guide_type TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                current_step INTEGER DEFAULT 1,
                session_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (setup_id) REFERENCES bow_setups (id) ON DELETE SET NULL
            )
        """)
        print("✅ Created guide_sessions table")
        
        # Create setup_arrows table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS setup_arrows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                setup_id INTEGER NOT NULL,
                arrow_id INTEGER NOT NULL,
                arrow_length REAL NOT NULL,
                point_weight REAL NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (setup_id) REFERENCES bow_setups (id) ON DELETE CASCADE,
                FOREIGN KEY (arrow_id) REFERENCES arrows (id) ON DELETE CASCADE
            )
        """)
        print("✅ Created setup_arrows table")
        
        # Create bow_equipment table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bow_equipment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                setup_id INTEGER NOT NULL,
                equipment_id INTEGER,
                category TEXT NOT NULL,
                manufacturer TEXT NOT NULL,
                model TEXT NOT NULL,
                specifications TEXT,
                installation_notes TEXT,
                installed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (setup_id) REFERENCES bow_setups (id) ON DELETE CASCADE,
                FOREIGN KEY (equipment_id) REFERENCES equipment (id)
            )
        """)
        print("✅ Created bow_equipment table")
        
        # Create backup_metadata table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS backup_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                backup_name TEXT NOT NULL,
                backup_type TEXT NOT NULL,
                file_path TEXT,
                cdn_url TEXT,
                file_size INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER,
                includes TEXT,
                FOREIGN KEY (created_by) REFERENCES users (id)
            )
        """)
        print("✅ Created backup_metadata table")
        
        # Update manufacturers table with missing columns
        print("🔄 Updating manufacturers table...")
        
        # Check current structure
        cursor.execute('PRAGMA table_info(manufacturers)')
        manufacturer_columns = [col[1] for col in cursor.fetchall()]
        
        missing_manufacturer_columns = []
        for col, sql_type in [('website', 'TEXT'), ('established', 'INTEGER'), ('arrow_types', 'TEXT'), ('contact_info', 'TEXT')]:
            if col not in manufacturer_columns:
                missing_manufacturer_columns.append(col)
                try:
                    cursor.execute(f"ALTER TABLE manufacturers ADD COLUMN {col} {sql_type}")
                    print(f"  ✅ Added manufacturers.{col}")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" not in str(e):
                        print(f"  ⚠️  Could not add manufacturers.{col}: {e}")
        
        if not missing_manufacturer_columns:
            print("  ✅ Manufacturers table already has all required columns")
        
        print("✅ Database consolidation migration applied successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error applying consolidation migration: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

def mark_migration_complete(cursor, version, name):
    """Mark a migration as completed"""
    try:
        cursor.execute("""
            INSERT OR REPLACE INTO schema_migrations (version, migration_name, applied_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (version, name))
        print(f"✅ Marked migration {version} as complete")
    except Exception as e:
        print(f"⚠️  Could not mark migration {version} as complete: {e}")

def fix_production_schema():
    """Main function to fix production schema"""
    
    # Find database
    possible_paths = [
        '/app/databases/arrow_database.db',
        '/app/arrow_database.db',
        './databases/arrow_database.db',
        './arrow_database.db'
    ]
    
    db_path = None
    for path in possible_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("❌ Database file not found")
        return False
    
    print(f"🔍 Working with database: {db_path}")
    print(f"📊 Database size: {os.path.getsize(db_path) / (1024*1024):.2f} MB")
    
    # Backup database
    backup_path = backup_database(db_path)
    if not backup_path:
        print("❌ Cannot proceed without backup")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Fix or ensure proper migration table structure
        if not fix_migration_table(cursor):
            print("❌ Failed to fix migration table")
            return False
        
        # Check if consolidation migration was applied
        if not check_migration_applied(cursor, '023'):
            print("🔄 Migration 023 not found - applying consolidation migration...")
            
            if apply_consolidation_migration(cursor):
                mark_migration_complete(cursor, '023', 'Database Consolidation')
                print("✅ Migration 023 applied and marked complete")
            else:
                print("❌ Failed to apply migration 023")
                conn.rollback()
                return False
        else:
            print("✅ Migration 023 already applied")
            
            # Still check for missing columns in case migration was incomplete
            print("🔍 Verifying all required columns exist...")
            apply_consolidation_migration(cursor)
        
        # Commit changes
        conn.commit()
        print("✅ All changes committed successfully")
        
        # Verify the fix
        print("\n🔍 Verifying schema fix...")
        
        # Check table counts
        user_tables = ['users', 'bow_setups', 'guide_sessions', 'backup_metadata', 'bow_equipment']
        arrow_tables = ['arrows', 'spine_specifications', 'manufacturers']
        
        user_tables_found = 0
        for table in user_tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if cursor.fetchone():
                user_tables_found += 1
        
        arrow_tables_found = 0
        for table in arrow_tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if cursor.fetchone():
                arrow_tables_found += 1
        
        architecture = "UNIFIED" if user_tables_found >= 3 and arrow_tables_found >= 2 else "INCOMPLETE"
        
        print(f"📊 Database Architecture: {architecture}")
        print(f"   User tables found: {user_tables_found}/{len(user_tables)}")
        print(f"   Arrow tables found: {arrow_tables_found}/{len(arrow_tables)}")
        
        if architecture == "UNIFIED":
            print("✅ Database successfully consolidated to unified architecture")
        else:
            print("⚠️  Database consolidation may be incomplete")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error fixing schema: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("🔧 Robust Production Database Schema Fix")
    print("=" * 50)
    
    # Check if running in Docker container
    if os.path.exists('/.dockerenv'):
        print("🐳 Running inside Docker container")
    
    success = fix_production_schema()
    
    if success:
        print("\n✅ Schema fix completed successfully!")
        print("🔄 Please restart the API container:")
        print("   docker restart arrowtuner-api")
        print("\n🔍 After restart, check the admin panel schema verification")
    else:
        print("\n❌ Schema fix failed. Check the backup file and logs.")
    
    print("=" * 50)