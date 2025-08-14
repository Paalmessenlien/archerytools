"""
Migration: Remove Setup Arrows Duplicate Constraint
Version: 017
Description: Remove unique constraint on setup_arrows to allow arrow duplication
"""

import sqlite3
import sys
from pathlib import Path

# Add parent directory to path to import migration base class
sys.path.append(str(Path(__file__).parent.parent))

class Migration:
    """Remove unique constraint on setup_arrows to allow duplicate arrows"""
    
    def __init__(self):
        self.version = "017"
        self.description = "Remove unique constraint on setup_arrows to allow arrow duplication"
        self.dependencies = []
        self.environments = ['all']
    
    def up(self, db_path: str, environment: str) -> bool:
        """Apply the migration - remove unique constraint from setup_arrows"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            print("🔄 Removing unique constraint from setup_arrows table...")
            
            # Check if the table exists and has the constraint
            cursor.execute("PRAGMA table_info(setup_arrows)")
            columns = cursor.fetchall()
            
            if not columns:
                print("⚠️  setup_arrows table not found, skipping migration")
                return True
            
            # Get current indexes to see if the unique constraint exists
            cursor.execute("PRAGMA index_list(setup_arrows)")
            indexes = cursor.fetchall()
            
            has_unique_constraint = False
            for index in indexes:
                if index[2] == 1:  # index[2] is the 'unique' flag
                    cursor.execute(f"PRAGMA index_info({index[1]})")
                    index_columns = [col[2] for col in cursor.fetchall()]
                    if set(index_columns) == {'setup_id', 'arrow_id', 'arrow_length', 'point_weight'}:
                        has_unique_constraint = True
                        break
            
            if not has_unique_constraint:
                print("✅ No unique constraint found on setup_arrows, migration not needed")
                return True
            
            # SQLite doesn't support dropping constraints directly, so we need to recreate the table
            print("🔄 Recreating setup_arrows table without unique constraint...")
            
            # Get all data from the current table
            cursor.execute("SELECT * FROM setup_arrows")
            existing_data = cursor.fetchall()
            
            # Create new table without the unique constraint
            cursor.execute('''
                CREATE TABLE setup_arrows_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    setup_id INTEGER NOT NULL,
                    arrow_id INTEGER NOT NULL,
                    arrow_length REAL NOT NULL,
                    point_weight REAL NOT NULL,
                    calculated_spine INTEGER,
                    compatibility_score INTEGER,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    nock_weight REAL,
                    fletching_weight REAL,
                    insert_weight REAL,
                    wrap_weight REAL,
                    bushing_weight REAL,
                    FOREIGN KEY (setup_id) REFERENCES bow_setups (id)
                )
            ''')
            
            # Copy all data to new table
            if existing_data:
                print(f"📋 Copying {len(existing_data)} existing records...")
                cursor.executemany('''
                    INSERT INTO setup_arrows_new 
                    (id, setup_id, arrow_id, arrow_length, point_weight, calculated_spine, 
                     compatibility_score, notes, created_at, nock_weight, fletching_weight,
                     insert_weight, wrap_weight, bushing_weight)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', existing_data)
                print(f"✅ Copied {len(existing_data)} records successfully")
            
            # Drop old table and rename new one
            cursor.execute("DROP TABLE setup_arrows")
            cursor.execute("ALTER TABLE setup_arrows_new RENAME TO setup_arrows")
            
            conn.commit()
            print("✅ Successfully removed unique constraint from setup_arrows table")
            print("📝 Users can now duplicate arrows with identical specifications")
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Failed to remove unique constraint: {e}")
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            return False
    
    def down(self, db_path: str, environment: str) -> bool:
        """Rollback the migration - add unique constraint back to setup_arrows"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            print("🔄 Adding unique constraint back to setup_arrows table...")
            
            # Get all data from the current table
            cursor.execute("SELECT * FROM setup_arrows")
            existing_data = cursor.fetchall()
            
            # Create table with unique constraint
            cursor.execute('''
                CREATE TABLE setup_arrows_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    setup_id INTEGER NOT NULL,
                    arrow_id INTEGER NOT NULL,
                    arrow_length REAL NOT NULL,
                    point_weight REAL NOT NULL,
                    calculated_spine INTEGER,
                    compatibility_score INTEGER,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    nock_weight REAL,
                    fletching_weight REAL,
                    insert_weight REAL,
                    wrap_weight REAL,
                    bushing_weight REAL,
                    UNIQUE(setup_id, arrow_id, arrow_length, point_weight),
                    FOREIGN KEY (setup_id) REFERENCES bow_setups (id)
                )
            ''')
            
            # Copy data back, removing duplicates if any exist
            if existing_data:
                print(f"📋 Copying {len(existing_data)} records with duplicate removal...")
                seen_combinations = set()
                unique_data = []
                
                for row in existing_data:
                    # Create key from setup_id, arrow_id, arrow_length, point_weight
                    key = (row[1], row[2], row[3], row[4])  # Assuming columns are in this order
                    if key not in seen_combinations:
                        seen_combinations.add(key)
                        unique_data.append(row)
                
                cursor.executemany('''
                    INSERT INTO setup_arrows_new 
                    (id, setup_id, arrow_id, arrow_length, point_weight, calculated_spine, 
                     compatibility_score, notes, created_at, nock_weight, fletching_weight,
                     insert_weight, wrap_weight, bushing_weight)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', unique_data)
                
                removed_count = len(existing_data) - len(unique_data)
                if removed_count > 0:
                    print(f"⚠️  Removed {removed_count} duplicate records during rollback")
                print(f"✅ Copied {len(unique_data)} unique records successfully")
            
            # Drop old table and rename new one
            cursor.execute("DROP TABLE setup_arrows")
            cursor.execute("ALTER TABLE setup_arrows_new RENAME TO setup_arrows")
            
            conn.commit()
            print("✅ Successfully added unique constraint back to setup_arrows table")
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Failed to add unique constraint back: {e}")
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            return False