#!/usr/bin/env python3
"""
Migration 033: Production Schema Fixes for Flight Path and Chronograph
Created: 2025-08-18
Purpose: Ensure production database has all required tables and columns for:
- Flight path calculations (setup_arrows table)
- Chronograph data functionality
- Draw length architecture fixes
"""

import sqlite3
import sys
import os
from pathlib import Path

# Add parent directory to path to import BaseMigration
sys.path.append(str(Path(__file__).parent.parent))
from database_migration_manager import BaseMigration

class Migration033(BaseMigration):
    def __init__(self):
        super().__init__()
        self.version = "033"
        self.description = "Production schema fixes for flight path and chronograph functionality"
        self.dependencies = []  # Independent migration
        self.environments = ['all']  # Can run in any environment
        
    def get_database_path(self):
        """Get the database path, prioritizing environment variables"""
        # Check environment variable first (for Docker)
        db_path = os.getenv('ARROW_DATABASE_PATH')
        if db_path and os.path.exists(db_path):
            return db_path
            
        # Try common paths
        possible_paths = [
            '/home/paal/archerytools/databases/arrow_database.db',
            '/app/databases/arrow_database.db',
            'databases/arrow_database.db',
            'arrow_database.db'
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
                
        raise FileNotFoundError("Could not find arrow database")

    def up(self):
        """Apply the migration"""
        db_path = self.get_database_path()
        
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            print("🔧 Applying Production Schema Fixes...")
            
            # 1. Ensure setup_arrows table exists with correct schema
            print("  📋 Creating setup_arrows table if missing...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS setup_arrows (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    setup_id INTEGER NOT NULL,
                    arrow_id INTEGER NOT NULL,
                    arrow_length REAL NOT NULL,
                    point_weight REAL NOT NULL,
                    calculated_spine TEXT,
                    compatibility_score REAL,
                    notes TEXT,
                    performance_data TEXT,
                    nock_weight REAL DEFAULT 0.0,
                    insert_weight REAL DEFAULT 0.0,
                    wrap_weight REAL DEFAULT 0.0,
                    fletching_weight REAL DEFAULT 0.0,
                    bushing_weight REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (setup_id) REFERENCES bow_setups (id) ON DELETE CASCADE,
                    FOREIGN KEY (arrow_id) REFERENCES arrows (id) ON DELETE CASCADE
                )
            """)
            
            # 2. Ensure bow_setups table has draw_length column
            print("  📋 Adding draw_length column to bow_setups if missing...")
            try:
                cursor.execute("ALTER TABLE bow_setups ADD COLUMN draw_length REAL DEFAULT 28.0")
                print("    ✅ Added draw_length column to bow_setups")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print("    ✅ draw_length column already exists in bow_setups")
                else:
                    raise
            
            # 3. Ensure bow_equipment table exists
            print("  📋 Creating bow_equipment table if missing...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bow_equipment (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    setup_id INTEGER NOT NULL,
                    equipment_id INTEGER,
                    category VARCHAR(50) NOT NULL,
                    manufacturer VARCHAR(100),
                    model VARCHAR(100),
                    specifications TEXT,
                    installation_notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (setup_id) REFERENCES bow_setups (id) ON DELETE CASCADE,
                    FOREIGN KEY (equipment_id) REFERENCES equipment (id) ON DELETE SET NULL
                )
            """)
            
            # 4. Ensure chronograph_data table exists with complete schema
            print("  📋 Creating chronograph_data table if missing...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chronograph_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    setup_arrow_id INTEGER NOT NULL,
                    measured_speed REAL NOT NULL,
                    arrow_weight REAL,
                    temperature REAL,
                    humidity REAL,
                    chronograph_model VARCHAR(100),
                    shot_count INTEGER DEFAULT 1,
                    standard_deviation REAL,
                    min_speed REAL,
                    max_speed REAL,
                    notes TEXT,
                    measured_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (setup_arrow_id) REFERENCES setup_arrows (id) ON DELETE CASCADE
                )
            """)
            
            # 5. Add missing columns to existing tables
            print("  📋 Adding missing columns to existing tables...")
            
            # Add missing columns to users table if needed
            missing_user_columns = [
                ("user_draw_length", "REAL DEFAULT 28.0"),
                ("skill_level", "VARCHAR(20) DEFAULT 'intermediate'"),
                ("is_admin", "BOOLEAN DEFAULT 0")
            ]
            
            for column_name, column_definition in missing_user_columns:
                try:
                    cursor.execute(f"ALTER TABLE users ADD COLUMN {column_name} {column_definition}")
                    print(f"    ✅ Added {column_name} column to users")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e):
                        print(f"    ✅ {column_name} column already exists in users")
                    else:
                        print(f"    ⚠️  Could not add {column_name} to users: {e}")
            
            # 6. Create indexes for performance
            print("  📋 Creating indexes for performance...")
            indexes = [
                ("idx_setup_arrows_setup_id", "CREATE INDEX IF NOT EXISTS idx_setup_arrows_setup_id ON setup_arrows (setup_id)"),
                ("idx_setup_arrows_arrow_id", "CREATE INDEX IF NOT EXISTS idx_setup_arrows_arrow_id ON setup_arrows (arrow_id)"),
                ("idx_chronograph_data_setup_arrow_id", "CREATE INDEX IF NOT EXISTS idx_chronograph_data_setup_arrow_id ON chronograph_data (setup_arrow_id)"),
                ("idx_bow_equipment_setup_id", "CREATE INDEX IF NOT EXISTS idx_bow_equipment_setup_id ON bow_equipment (setup_id)")
            ]
            
            for index_name, index_sql in indexes:
                try:
                    cursor.execute(index_sql)
                    print(f"    ✅ Created index {index_name}")
                except sqlite3.OperationalError:
                    print(f"    ✅ Index {index_name} already exists")
            
            conn.commit()
            print("✅ Production schema fixes completed successfully")

    def down(self):
        """Reverse the migration (optional - for testing)"""
        print("⚠️  Migration 033 down() not implemented - schema fixes should remain")
        print("   To reverse, manually drop tables: setup_arrows, chronograph_data, bow_equipment")

if __name__ == "__main__":
    migration = Migration033()
    migration.up()