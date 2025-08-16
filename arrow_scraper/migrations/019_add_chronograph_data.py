#!/usr/bin/env python3
"""
Migration 019: Add chronograph data table for storing measured arrow speeds
Created: 2025-08-15
Updated: 2025-08-16 - Converted to BaseMigration format for unified database
"""

import sqlite3
import sys
import os
from pathlib import Path

# Add parent directory to path to import BaseMigration
sys.path.append(str(Path(__file__).parent.parent))
from database_migration_manager import BaseMigration

class Migration019(BaseMigration):
    def __init__(self):
        super().__init__()
        self.version = "019"
        self.description = "Add chronograph data table for storing measured arrow speeds"
        self.dependencies = []  # No dependencies
        self.environments = ['all']  # Can run in any environment
        
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
        """Apply the migration - create chronograph_data table"""
        if not db_path:
            db_path = self.get_database_path()
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            print(f"🔄 Migration {self.version}: Creating chronograph_data table...")
            
            # Create chronograph_data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chronograph_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    setup_id INTEGER NOT NULL,
                    arrow_id INTEGER,
                    setup_arrow_id INTEGER,
                    measured_speed_fps REAL NOT NULL,
                    arrow_weight_grains REAL NOT NULL,
                    temperature_f INTEGER,
                    humidity_percent INTEGER,
                    measurement_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    chronograph_model TEXT,
                    shot_count INTEGER DEFAULT 1,
                    std_deviation REAL,
                    min_speed_fps REAL,
                    max_speed_fps REAL,
                    verified BOOLEAN DEFAULT 0,
                    notes TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (setup_id) REFERENCES bow_setups(id) ON DELETE CASCADE,
                    FOREIGN KEY (arrow_id) REFERENCES arrows(id) ON DELETE SET NULL,
                    FOREIGN KEY (setup_arrow_id) REFERENCES setup_arrows(id) ON DELETE CASCADE
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_chronograph_setup_id ON chronograph_data(setup_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_chronograph_arrow_id ON chronograph_data(arrow_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_chronograph_setup_arrow_id ON chronograph_data(setup_arrow_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_chronograph_verified ON chronograph_data(verified)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_chronograph_date ON chronograph_data(measurement_date)')
            
            # Commit changes
            conn.commit()
            
            print(f"✅ Migration {self.version} completed successfully")
            print("📊 Created chronograph_data table with indexes for performance analysis")
            
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
        """Rollback the migration - remove chronograph_data table"""
        if not db_path:
            db_path = self.get_database_path()
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            print(f"🔄 Migration {self.version}: Rolling back chronograph_data table...")
            
            # Remove chronograph_data table
            cursor.execute('DROP TABLE IF EXISTS chronograph_data')
            
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
            if not cursor.fetchone():
                print("❌ chronograph_data table does not exist")
                return False
            
            # Check table structure has expected columns
            cursor.execute('PRAGMA table_info(chronograph_data)')
            columns = [col[1] for col in cursor.fetchall()]
            
            expected_columns = [
                'id', 'setup_id', 'arrow_id', 'setup_arrow_id', 'measured_speed_fps',
                'arrow_weight_grains', 'temperature_f', 'humidity_percent', 'measurement_date',
                'chronograph_model', 'shot_count', 'std_deviation', 'min_speed_fps',
                'max_speed_fps', 'verified', 'notes', 'created_at', 'updated_at'
            ]
            
            missing_columns = [col for col in expected_columns if col not in columns]
            if missing_columns:
                print(f"❌ Missing columns in chronograph_data table: {missing_columns}")
                return False
            
            # Check indexes exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_chronograph_%'")
            indexes = [row[0] for row in cursor.fetchall()]
            
            expected_indexes = [
                'idx_chronograph_setup_id', 'idx_chronograph_arrow_id',
                'idx_chronograph_setup_arrow_id', 'idx_chronograph_verified',
                'idx_chronograph_date'
            ]
            
            missing_indexes = [idx for idx in expected_indexes if idx not in indexes]
            if missing_indexes:
                print(f"⚠️  Missing indexes: {missing_indexes}")
            
            conn.close()
            print("✅ chronograph_data table structure is correct")
            return True
            
        except Exception as e:
            print(f"❌ Validation failed: {e}")
            return False

# Migration interface for the migration manager
def get_migration():
    """Return migration instance for the migration manager"""
    return Migration019()

def main():
    """Main function for standalone execution"""
    migration = Migration019()
    print(f"Running Migration {migration.version}: {migration.description}")
    
    if len(sys.argv) < 2:
        print("Usage: python 019_add_chronograph_data.py <database_path> [--rollback]")
        sys.exit(1)
    
    db_path = sys.argv[1]
    rollback = '--rollback' in sys.argv
    
    try:
        if rollback:
            print("🔄 Rolling back migration 019...")
            success = migration.down(db_path, 'manual')
        else:
            print("🚀 Applying migration 019...")
            success = migration.up(db_path, 'manual')
        
        if success:
            print("\n🔍 Validating migration...")
            validation_success = migration.validate()
            if validation_success:
                action = "rolled back" if rollback else "applied"
                print(f"✅ Migration 019 {action} and validated successfully!")
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