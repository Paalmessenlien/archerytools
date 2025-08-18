#!/usr/bin/env python3
"""
Migration 030: Fix Draw Length Architecture
Resolves confusion between compound bow draw length module and user draw length

Changes:
1. Add draw_length_module column to bow_setups table (for compound bows)
2. Add user_draw_length column to users table (for archer's personal measurement) 
3. Migrate existing data appropriately
4. Set proper defaults and constraints

This fixes the "table bow_setups has no column named draw_length" error
while properly separating bow specifications from user measurements.
"""

import sqlite3
import sys
from pathlib import Path

# Add the parent directory to sys.path so we can import BaseMigration
sys.path.append(str(Path(__file__).parent.parent))
from database_migration_manager import BaseMigration

class Migration030FixDrawLengthArchitecture(BaseMigration):
    def __init__(self):
        super().__init__()
        self.version = "030"
        self.description = "Fix Draw Length Architecture - Separate bow specs from user measurements"
        self.dependencies = ["029"]  # Depends on previous schema fixes
        self.environments = ['all']
        self.target_database = 'arrow'
    
    def up(self, db_path: str, environment: str) -> bool:
        """Apply the migration"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            print("📏 Migration 030: Fixing draw length architecture...")
            
            # Check existing columns in bow_setups
            cursor.execute("PRAGMA table_info(bow_setups)")
            bow_columns = [row[1] for row in cursor.fetchall()]
            
            # Check existing columns in users  
            cursor.execute("PRAGMA table_info(users)")
            user_columns = [row[1] for row in cursor.fetchall()]
            
            added_count = 0
            
            # 1. Add draw_length_module column to bow_setups (for compound bows)
            if 'draw_length_module' not in bow_columns:
                try:
                    cursor.execute("ALTER TABLE bow_setups ADD COLUMN draw_length_module REAL DEFAULT NULL")
                    print("✅ Added bow_setups.draw_length_module column")
                    added_count += 1
                except sqlite3.OperationalError as e:
                    print(f"⚠️  Warning adding bow_setups.draw_length_module: {e}")
            
            # 2. Add user_draw_length column to users (for archer's personal measurement)
            if 'user_draw_length' not in user_columns:
                try:
                    cursor.execute("ALTER TABLE users ADD COLUMN user_draw_length REAL DEFAULT 28.0")
                    print("✅ Added users.user_draw_length column")
                    added_count += 1
                except sqlite3.OperationalError as e:
                    print(f"⚠️  Warning adding users.user_draw_length: {e}")
            
            # 3. Migrate existing draw_length data from users table to user_draw_length (if exists)
            migrated_users = 0
            if 'draw_length' in user_columns:
                cursor.execute("""
                    UPDATE users 
                    SET user_draw_length = COALESCE(draw_length, 28.0)
                    WHERE user_draw_length IS NULL OR user_draw_length = 28.0
                """)
                migrated_users = cursor.rowcount
                print(f"✅ Migrated {migrated_users} user draw_length values")
            else:
                print("ℹ️  No existing draw_length column in users table to migrate")
            
            # 4. For existing compound bow setups, migrate draw_length to draw_length_module (if exists)
            migrated_setups = 0
            if 'draw_length' in bow_columns:
                cursor.execute("""
                    UPDATE bow_setups 
                    SET draw_length_module = draw_length
                    WHERE bow_type = 'compound' 
                    AND draw_length IS NOT NULL 
                    AND draw_length_module IS NULL
                """)
                migrated_setups = cursor.rowcount
                print(f"✅ Migrated {migrated_setups} compound bow draw_length values to draw_length_module")
            else:
                print("ℹ️  No existing draw_length column in bow_setups table to migrate")
            
            # 5. Set reasonable defaults for bow setups missing draw_length (if column exists)
            defaulted_setups = 0
            if 'draw_length' in bow_columns:
                cursor.execute("""
                    UPDATE bow_setups 
                    SET draw_length = 28.0
                    WHERE draw_length IS NULL
                """)
                defaulted_setups = cursor.rowcount
                print(f"✅ Set default draw_length for {defaulted_setups} bow setups")
            else:
                print("ℹ️  No draw_length column in bow_setups table to set defaults")
            
            # 6. Add helpful indexes for performance
            try:
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_bow_setups_draw_length_module ON bow_setups(draw_length_module)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_user_draw_length ON users(user_draw_length)")
                print("✅ Added performance indexes")
            except sqlite3.OperationalError as e:
                print(f"⚠️  Warning creating indexes: {e}")
            
            conn.commit()
            conn.close()
            
            print(f"🎯 Migration 030 completed successfully! ({added_count + migrated_users + migrated_setups + defaulted_setups} operations)")
            print("   - Compound bows now use draw_length_module")  
            print("   - Users have personal user_draw_length")
            print("   - Performance calculations can distinguish between bow specs and user measurements")
            
            return True
            
        except Exception as e:
            conn.rollback()
            conn.close()
            print(f"❌ Error in Migration 030: {e}")
            return False
    
    def down(self, db_path: str, environment: str) -> bool:
        """Rollback the migration (limited due to SQLite constraints)"""
        print("⚠️  Rolling back Migration 030...")
        print("   Note: SQLite doesn't support DROP COLUMN, so rollback is limited")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # Clear the new columns (but keep them for schema compatibility)
            cursor.execute("UPDATE bow_setups SET draw_length_module = NULL")
            cursor.execute("UPDATE users SET user_draw_length = 28.0")
            
            # Drop indexes (these can be removed)
            cursor.execute("DROP INDEX IF EXISTS idx_bow_setups_draw_length_module")
            cursor.execute("DROP INDEX IF EXISTS idx_users_user_draw_length")
            
            conn.commit()
            conn.close()
            
            print("✅ Migration 030 rollback completed (columns preserved but data cleared)")
            return True
            
        except Exception as e:
            conn.rollback()
            conn.close()
            print(f"❌ Error rolling back Migration 030: {e}")
            return False

def main():
    """Run migration directly"""
    if len(sys.argv) < 2:
        print("Usage: python 030_fix_draw_length_architecture.py <database_path>")
        sys.exit(1)
    
    db_path = sys.argv[1]
    migration = Migration030FixDrawLengthArchitecture()
    success = migration.up(db_path, 'development')
    if success:
        print("Migration completed successfully!")
    else:
        print("Migration failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()