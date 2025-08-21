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

def get_migration_info():
    """Return migration metadata"""
    return {
        'version': 33,
        'description': 'Production schema fixes for flight path and chronograph functionality',
        'author': 'System',
        'created_at': '2025-08-18',
        'target_database': 'arrow',
        'dependencies': [],
        'environments': ['all']
    }

def migrate_up(cursor):
    """Apply the migration"""
    conn = cursor.connection
    
    try:
        print("🔧 Migration 033: Applying Production Schema Fixes...")
        
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
        print("🎯 Migration 033 completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration 033 failed: {e}")
        conn.rollback()
        return False

def migrate_down(cursor):
    """Rollback the migration"""
    conn = cursor.connection
    
    try:
        print("🔄 Rolling back Migration 033...")
        print("⚠️  Schema fixes rollback not implemented - tables should remain for data preservation")
        print("   To reverse, manually drop tables: setup_arrows, chronograph_data, bow_equipment")
        
        conn.commit()
        print("🔄 Migration 033 rollback completed")
        return True
        
    except Exception as e:
        print(f"❌ Migration 033 rollback failed: {e}")
        conn.rollback()
        return False

if __name__ == "__main__":
    # Test the migration - try multiple database paths
    possible_paths = [
        '/app/databases/arrow_database.db',  # Docker production
        '/root/archerytools/databases/arrow_database.db',  # Production host
        os.path.join(os.path.dirname(__file__), '..', 'databases', 'arrow_database.db'),  # Development
        'databases/arrow_database.db',  # Relative path
        'arrow_database.db'  # Current directory
    ]
    
    db_path = None
    for path in possible_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print(f"❌ Database not found in any location: {possible_paths}")
        sys.exit(1)
    
    print(f"📁 Using database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    
    try:
        if len(sys.argv) > 1 and sys.argv[1] == 'down':
            success = migrate_down(conn.cursor())
        else:
            success = migrate_up(conn.cursor())
        
        if success:
            print("✅ Migration test completed successfully")
        else:
            print("❌ Migration test failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Migration test error: {e}")
        sys.exit(1)
    finally:
        conn.close()