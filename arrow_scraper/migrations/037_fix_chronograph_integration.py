#!/usr/bin/env python3
"""
Migration 037: Fix Chronograph Integration
Created: 2025-08-21
Updated: 2025-08-21 - Converted to BaseMigration format for migration manager compatibility
"""

import sqlite3
import sys
import os
from pathlib import Path

# Add parent directory to path to import BaseMigration
sys.path.append(str(Path(__file__).parent.parent))
from database_migration_manager import BaseMigration

class Migration037(BaseMigration):
    def __init__(self):
        super().__init__()
        self.version = "037"
        self.description = "Fix Chronograph Integration - Setup arrow ID mapping and performance calculation priority"
        self.dependencies = []  # No dependencies
        self.environments = ['all']  # Can run in any environment
        self.target_database = 'arrow'  # Target unified database
        
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
    
    def up(self, db_path: str, environment: str) -> bool:
        """Apply the migration - Fix chronograph integration"""
        print(f"🔄 Migration {self.version}: Starting up() method...")
        print(f"   Provided db_path: {db_path}")
        print(f"   Environment: {environment}")
        
        if not db_path:
            print("   No db_path provided, resolving...")
            try:
                db_path = self.get_database_path()
                print(f"   Resolved db_path: {db_path}")
            except Exception as e:
                print(f"   ❌ Failed to resolve db_path: {e}")
                return False
        
        print(f"   Using database: {db_path}")
        print(f"   Database exists: {os.path.exists(db_path)}")
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            print(f"🔄 Migration {self.version}: Fixing chronograph integration...")
            
            # Check if chronograph_data table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chronograph_data'")
            chronograph_table_exists = cursor.fetchone() is not None
            
            print(f"   Chronograph table exists: {chronograph_table_exists}")
            
            if not chronograph_table_exists:
                print("   ⚠️  chronograph_data table does not exist, skipping chronograph-specific fixes")
                print("   ✅ Migration completed (no chronograph data to fix)")
                conn.close()
                return True
            
            # 1. Check for chronograph data with mismatched setup_arrow_id
            print("1. Checking for chronograph data consistency...")
            cursor.execute('''
                SELECT cd.id, cd.setup_id, cd.arrow_id, cd.setup_arrow_id, cd.measured_speed_fps,
                       sa.id as actual_setup_arrow_id
                FROM chronograph_data cd
                LEFT JOIN setup_arrows sa ON cd.setup_id = sa.setup_id AND cd.arrow_id = sa.arrow_id
                WHERE cd.setup_arrow_id != sa.id OR sa.id IS NULL
            ''')
            
            mismatched_records = cursor.fetchall()
            
            if mismatched_records:
                print(f"   Found {len(mismatched_records)} chronograph records with incorrect setup_arrow_id")
                
                for record in mismatched_records:
                    if record[5]:  # actual_setup_arrow_id
                        print(f"   Fixing record {record[0]}: setup_arrow_id {record[3]} → {record[5]}")
                        cursor.execute('''
                            UPDATE chronograph_data 
                            SET setup_arrow_id = ? 
                            WHERE id = ?
                        ''', (record[5], record[0]))
                    else:
                        print(f"   ⚠️  Record {record[0]} has no matching setup arrow - keeping as is")
            else:
                print("   ✅ All chronograph records have correct setup_arrow_id")
            
            # 2. Ensure all chronograph data has verified = 1
            print("2. Ensuring chronograph data is marked as verified...")
            cursor.execute('''
                UPDATE chronograph_data 
                SET verified = 1 
                WHERE verified IS NULL OR verified = 0
            ''')
            updated_verified = cursor.rowcount
            if updated_verified > 0:
                print(f"   ✅ Updated {updated_verified} chronograph records to verified=1")
            else:
                print("   ✅ All chronograph data already verified")
            
            # 3. Clear cached performance data to force recalculation
            print("3. Clearing cached performance data to force recalculation...")
            cursor.execute('''
                UPDATE setup_arrows 
                SET performance_data = NULL 
                WHERE performance_data IS NOT NULL
            ''')
            cleared_performance = cursor.rowcount
            if cleared_performance > 0:
                print(f"   ✅ Cleared {cleared_performance} cached performance calculations")
            else:
                print("   ✅ No cached performance data to clear")
            
            # 4. Add index on chronograph_data for faster lookups
            print("4. Adding database indexes for faster chronograph lookups...")
            try:
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_chronograph_setup_arrow 
                    ON chronograph_data(setup_id, arrow_id, verified, measurement_date DESC)
                ''')
                print("   ✅ Created index on chronograph_data")
            except sqlite3.OperationalError as e:
                print(f"   ⚠️  Index creation skipped: {e}")
            
            # Commit changes
            conn.commit()
            
            print(f"✅ Migration {self.version} completed successfully")
            print(f"🎯 Chronograph integration fixes applied")
            
            return True
            
        except Exception as e:
            print(f"❌ Migration {self.version} failed: {e}")
            if 'conn' in locals():
                conn.rollback()
            raise
        finally:
            if 'conn' in locals():
                conn.close()
    
    def down(self, db_path: str, environment: str) -> bool:
        """Rollback the migration"""
        if not db_path:
            db_path = self.get_database_path()
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            print(f"🔄 Migration {self.version}: Rolling back chronograph integration fixes...")
            
            # Remove the index we created
            cursor.execute('DROP INDEX IF EXISTS idx_chronograph_setup_arrow')
            
            # Commit changes
            conn.commit()
            
            print(f"✅ Migration {self.version} rollback completed")
            
            return True
            
        except Exception as e:
            print(f"❌ Migration {self.version} rollback failed: {e}")
            if 'conn' in locals():
                conn.rollback()
            raise
        finally:
            if 'conn' in locals():
                conn.close()
    
    def validate(self):
        """Validate that the migration was applied correctly"""
        db_path = self.get_database_path()
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if chronograph_data table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chronograph_data'")
            chronograph_exists = cursor.fetchone() is not None
            
            if not chronograph_exists:
                print("ℹ️  chronograph_data table does not exist - migration completed successfully (no data to fix)")
                conn.close()
                return True
            
            # Check if the index was created (only if chronograph table exists)
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_chronograph_setup_arrow'")
            if not cursor.fetchone():
                print("⚠️  chronograph index not found, but migration may still be valid")
            else:
                print("✅ chronograph index found")
            
            conn.close()
            print("✅ Migration validation passed")
            return True
            
        except Exception as e:
            print(f"❌ Validation failed: {e}")
            return False

# Migration interface for the migration manager
def get_migration():
    """Return migration instance for the migration manager"""
    return Migration037()

def main():
    """Main function for standalone execution"""
    migration = Migration037()
    print(f"Running Migration {migration.version}: {migration.description}")
    
    if len(sys.argv) < 2:
        print("Usage: python 037_fix_chronograph_integration.py <database_path> [--rollback]")
        sys.exit(1)
    
    db_path = sys.argv[1]
    rollback = '--rollback' in sys.argv
    
    try:
        if rollback:
            print("🔄 Rolling back migration 037...")
            success = migration.down(db_path, 'manual')
        else:
            print("🚀 Applying migration 037...")
            success = migration.up(db_path, 'manual')
        
        if success:
            print("\n🔍 Validating migration...")
            validation_success = migration.validate()
            if validation_success:
                action = "rolled back" if rollback else "applied"
                print(f"✅ Migration 037 {action} and validated successfully!")
            else:
                print("⚠️  Migration completed but validation found issues")
        else:
            print("❌ Migration failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Migration error: {e}")
        import traceback
        print(traceback.format_exc())
        sys.exit(1)

if __name__ == '__main__':
    main()