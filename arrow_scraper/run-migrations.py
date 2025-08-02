#!/usr/bin/env python3
"""
Centralized migration runner for ArrowTuner database schemas.
Runs all necessary migrations in the correct order during startup.
"""

import os
import sys
import sqlite3
import json
from pathlib import Path
from datetime import datetime

# Migration tracking table
MIGRATION_TABLE = """
CREATE TABLE IF NOT EXISTS schema_migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    migration_name TEXT UNIQUE NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN DEFAULT 1,
    error_message TEXT
)
"""

class MigrationRunner:
    def __init__(self):
        self.migrations_run = []
        self.errors = []
        
    def get_db_paths(self):
        """Get database paths for both arrow and user databases"""
        # Check for Docker environment
        if os.path.exists("/app/api.py"):
            arrow_db = "/app/arrow_database.db"
            user_db = "/app/user_data/user_data.db" if os.path.exists("/app/user_data") else "/app/user_data.db"
        else:
            arrow_db = "arrow_database.db"
            user_db = "user_data.db"
            
        return arrow_db, user_db
    
    def ensure_migration_table(self, db_path):
        """Create migration tracking table if it doesn't exist"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(MIGRATION_TABLE)
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"❌ Error creating migration table in {db_path}: {e}")
            
    def has_migration_run(self, db_path, migration_name):
        """Check if a migration has already been applied"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM schema_migrations WHERE migration_name = ? AND success = 1", (migration_name,))
            result = cursor.fetchone()
            conn.close()
            return result is not None
        except:
            return False
            
    def record_migration(self, db_path, migration_name, success=True, error_message=None):
        """Record that a migration has been run"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO schema_migrations (migration_name, success, error_message) VALUES (?, ?, ?)",
                (migration_name, success, error_message)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠️  Failed to record migration {migration_name}: {e}")
    
    def run_user_db_migration(self, user_db_path):
        """Run migrations specific to user database"""
        print("\n📦 Running User Database Migrations...")
        print("=" * 50)
        
        self.ensure_migration_table(user_db_path)
        
        # Migration 1: Fix bow_setups schema
        migration_name = "fix_bow_setups_schema_2025"
        if not self.has_migration_run(user_db_path, migration_name):
            print(f"🔄 Running migration: {migration_name}")
            try:
                conn = sqlite3.connect(user_db_path)
                cursor = conn.cursor()
                
                # Check current schema
                cursor.execute("PRAGMA table_info(bow_setups)")
                current_columns = {col[1] for col in cursor.fetchall()}
                
                # Check if we need to migrate (if riser_brand is missing)
                if 'riser_brand' not in current_columns:
                    print("  📋 Detected old schema, migrating bow_setups table...")
                    
                    # Create new table with correct schema
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS bow_setups_new (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER NOT NULL,
                            name TEXT NOT NULL,
                            bow_type TEXT NOT NULL,
                            draw_weight REAL NOT NULL,
                            draw_length REAL NOT NULL,
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
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                        )
                    """)
                    
                    # Copy existing data
                    common_columns = ['id', 'user_id', 'name', 'bow_type', 'draw_weight', 'draw_length', 'created_at']
                    existing_columns = [col for col in common_columns if col in current_columns]
                    
                    if existing_columns:
                        cursor.execute(f"""
                            INSERT INTO bow_setups_new ({', '.join(existing_columns)})
                            SELECT {', '.join(existing_columns)}
                            FROM bow_setups
                        """)
                        
                    # Replace old table
                    cursor.execute("DROP TABLE bow_setups")
                    cursor.execute("ALTER TABLE bow_setups_new RENAME TO bow_setups")
                    
                    conn.commit()
                    print("  ✅ Successfully migrated bow_setups schema")
                else:
                    print("  ✅ Schema already up to date")
                    
                conn.close()
                self.record_migration(user_db_path, migration_name, True)
                self.migrations_run.append(migration_name)
                
            except Exception as e:
                print(f"  ❌ Migration failed: {e}")
                self.record_migration(user_db_path, migration_name, False, str(e))
                self.errors.append((migration_name, str(e)))
        else:
            print(f"⏭️  Migration {migration_name} already applied")
            
        # Migration 2: Ensure all user profile fields exist
        migration_name = "add_user_profile_fields_2025"
        if not self.has_migration_run(user_db_path, migration_name):
            print(f"🔄 Running migration: {migration_name}")
            try:
                from user_database import UserDatabase
                user_db = UserDatabase(user_db_path)
                # The UserDatabase class has its own migration methods that run on init
                print("  ✅ User profile fields verified")
                self.record_migration(user_db_path, migration_name, True)
                self.migrations_run.append(migration_name)
            except Exception as e:
                print(f"  ❌ Migration failed: {e}")
                self.record_migration(user_db_path, migration_name, False, str(e))
                self.errors.append((migration_name, str(e)))
        else:
            print(f"⏭️  Migration {migration_name} already applied")
                
    def run_arrow_db_migration(self, arrow_db_path):
        """Run migrations specific to arrow database"""
        print("\n📦 Running Arrow Database Migrations...")
        print("=" * 50)
        
        self.ensure_migration_table(arrow_db_path)
        
        # Migration 1: Add diameter categories
        migration_name = "add_diameter_categories_2025"
        if not self.has_migration_run(arrow_db_path, migration_name):
            print(f"🔄 Running migration: {migration_name}")
            try:
                # Check if migration script exists
                if os.path.exists("migrate_diameter_categories.py"):
                    import subprocess
                    result = subprocess.run([sys.executable, "migrate_diameter_categories.py"], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        print("  ✅ Diameter categories migration completed")
                        self.record_migration(arrow_db_path, migration_name, True)
                        self.migrations_run.append(migration_name)
                    else:
                        # Check if it's just a missing dependency
                        if "ModuleNotFoundError" in result.stderr:
                            print("  ⚠️  Migration skipped due to missing dependencies")
                            print("     (This is OK if you're not using the arrow scraper)")
                        else:
                            raise Exception(result.stderr or "Migration script failed")
                else:
                    print("  ⚠️  Migration script not found, skipping")
            except Exception as e:
                print(f"  ❌ Migration failed: {e}")
                self.record_migration(arrow_db_path, migration_name, False, str(e))
                self.errors.append((migration_name, str(e)))
        else:
            print(f"⏭️  Migration {migration_name} already applied")
    
    def run_all_migrations(self):
        """Run all migrations for both databases"""
        print("🚀 Starting ArrowTuner Database Migrations")
        print("=" * 50)
        
        arrow_db, user_db = self.get_db_paths()
        print(f"📁 Arrow Database: {arrow_db}")
        print(f"📁 User Database: {user_db}")
        
        # Run user database migrations
        if os.path.exists(user_db):
            self.run_user_db_migration(user_db)
        else:
            print(f"⚠️  User database not found at {user_db}, will be created on first run")
            
        # Run arrow database migrations
        if os.path.exists(arrow_db):
            self.run_arrow_db_migration(arrow_db)
        else:
            print(f"⚠️  Arrow database not found at {arrow_db}")
            
        # Summary
        print("\n📊 Migration Summary")
        print("=" * 50)
        if self.migrations_run:
            print(f"✅ Successfully ran {len(self.migrations_run)} migrations:")
            for migration in self.migrations_run:
                print(f"   - {migration}")
        else:
            print("ℹ️  No new migrations were needed")
            
        if self.errors:
            print(f"\n❌ {len(self.errors)} migrations failed:")
            for migration, error in self.errors:
                print(f"   - {migration}: {error}")
            return 1
            
        return 0

def main():
    """Main entry point"""
    runner = MigrationRunner()
    return runner.run_all_migrations()

if __name__ == "__main__":
    sys.exit(main())