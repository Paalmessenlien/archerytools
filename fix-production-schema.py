#!/usr/bin/env python3
"""
Production Database Schema Fix Script
Applies missing migrations and fixes schema issues
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

def ensure_schema_migrations_table(cursor):
    """Ensure the schema_migrations table exists"""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            migration_name TEXT,
            success BOOLEAN DEFAULT TRUE
        )
    """)
    print("✅ Schema migrations table ready")

def check_migration_applied(cursor, version):
    """Check if a migration has been applied"""
    cursor.execute("SELECT version FROM schema_migrations WHERE version = ?", (version,))
    return cursor.fetchone() is not None

def apply_consolidation_migration(cursor):
    """Apply the database consolidation migration manually"""
    
    print("🔄 Applying database consolidation migration...")
    
    # Check if user tables already exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    if cursor.fetchone():
        print("✅ User tables already exist - consolidation may be partially complete")
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
        
        # Update manufacturers table with missing columns
        print("🔄 Updating manufacturers table...")
        try:
            cursor.execute("ALTER TABLE manufacturers ADD COLUMN website TEXT")
        except sqlite3.OperationalError:
            pass  # Column might already exist
        
        try:
            cursor.execute("ALTER TABLE manufacturers ADD COLUMN established INTEGER")
        except sqlite3.OperationalError:
            pass
        
        try:
            cursor.execute("ALTER TABLE manufacturers ADD COLUMN arrow_types TEXT")
        except sqlite3.OperationalError:
            pass
        
        try:
            cursor.execute("ALTER TABLE manufacturers ADD COLUMN contact_info TEXT")
        except sqlite3.OperationalError:
            pass
        
        print("✅ Database consolidation migration applied successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error applying consolidation migration: {e}")
        return False

def mark_migration_complete(cursor, version, name):
    """Mark a migration as completed"""
    cursor.execute("""
        INSERT OR REPLACE INTO schema_migrations (version, migration_name, applied_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
    """, (version, name))

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
        
        # Ensure schema migrations table
        ensure_schema_migrations_table(cursor)
        
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
        
        # Commit changes
        conn.commit()
        print("✅ All changes committed successfully")
        
        # Verify the fix
        print("\n🔍 Verifying schema fix...")
        from database_health_checker import DatabaseHealthChecker
        
        checker = DatabaseHealthChecker(db_path)
        health_report = checker.run_comprehensive_health_check()
        
        print(f"Database Architecture: {health_report.database_architecture}")
        print(f"Performance Score: {health_report.performance_score}/100")
        print(f"Integrity Status: {health_report.integrity_status}")
        
        if health_report.database_architecture == 'unified':
            print("✅ Database successfully consolidated to unified architecture")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error fixing schema: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Production Database Schema Fix")
    print("=" * 50)
    
    # Check if running in Docker container
    if os.path.exists('/.dockerenv'):
        print("🐳 Running inside Docker container")
    
    success = fix_production_schema()
    
    if success:
        print("\n✅ Schema fix completed successfully!")
        print("🔄 Please restart the API container:")
        print("   docker restart arrowtuner-api")
    else:
        print("\n❌ Schema fix failed. Check the backup file and logs.")
    
    print("=" * 50)