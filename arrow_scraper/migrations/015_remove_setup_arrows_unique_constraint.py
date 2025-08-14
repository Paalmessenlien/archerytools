#!/usr/bin/env python3
"""
Migration 015: Remove UNIQUE constraint from setup_arrows table to allow arrow duplication
Date: 2025-08-14
Purpose: Fix duplicate arrow functionality by removing the UNIQUE constraint that prevented
         creating duplicate arrows with the same specifications.
"""

import sqlite3
from pathlib import Path

def get_migration_info():
    """Return migration metadata"""
    return {
        'version': '015',
        'name': 'remove_setup_arrows_unique_constraint',
        'description': 'Remove UNIQUE constraint from setup_arrows table to allow arrow duplication',
        'date': '2025-08-14',
        'dependencies': ['002_user_database_schema.py']  # Depends on setup_arrows table creation
    }

def up(db_path: str) -> bool:
    """
    Remove the UNIQUE constraint from setup_arrows table
    """
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check if setup_arrows table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='setup_arrows'
        """)
        
        if not cursor.fetchone():
            print("⚠️  setup_arrows table not found - skipping migration")
            conn.close()
            return True
        
        # Check current schema for UNIQUE constraint
        cursor.execute("""
            SELECT sql FROM sqlite_master 
            WHERE type='table' AND name='setup_arrows'
        """)
        
        current_schema = cursor.fetchone()
        if not current_schema:
            print("❌ Could not retrieve setup_arrows schema")
            conn.close()
            return False
            
        schema_sql = current_schema['sql']
        
        # Check if UNIQUE constraint exists
        if 'UNIQUE(setup_id, arrow_id, arrow_length, point_weight)' not in schema_sql:
            print("✅ UNIQUE constraint not found - migration already applied or not needed")
            conn.close()
            return True
        
        print("🔧 Removing UNIQUE constraint from setup_arrows table...")
        
        # Get all existing data
        cursor.execute("SELECT * FROM setup_arrows ORDER BY id")
        existing_data = cursor.fetchall()
        print(f"📊 Backing up {len(existing_data)} existing records")
        
        # Create new table without UNIQUE constraint
        cursor.execute("DROP TABLE IF EXISTS setup_arrows_new")
        cursor.execute("""
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
                FOREIGN KEY (setup_id) REFERENCES bow_setups (id) ON DELETE CASCADE
            )
        """)
        
        # Copy all data to new table
        for row in existing_data:
            cursor.execute("""
                INSERT INTO setup_arrows_new 
                (id, setup_id, arrow_id, arrow_length, point_weight, calculated_spine, 
                 compatibility_score, notes, created_at, nock_weight, fletching_weight, 
                 insert_weight, wrap_weight, bushing_weight)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row['id'], row['setup_id'], row['arrow_id'], row['arrow_length'],
                row['point_weight'], row['calculated_spine'], row['compatibility_score'],
                row['notes'], row['created_at'],
                row['nock_weight'] if 'nock_weight' in row.keys() else None,
                row['fletching_weight'] if 'fletching_weight' in row.keys() else None,
                row['insert_weight'] if 'insert_weight' in row.keys() else None,
                row['wrap_weight'] if 'wrap_weight' in row.keys() else None,
                row['bushing_weight'] if 'bushing_weight' in row.keys() else None
            ))
        
        # Replace old table with new one
        cursor.execute("DROP TABLE setup_arrows")
        cursor.execute("ALTER TABLE setup_arrows_new RENAME TO setup_arrows")
        
        conn.commit()
        
        # Verify the constraint was removed
        cursor.execute("""
            SELECT sql FROM sqlite_master 
            WHERE type='table' AND name='setup_arrows'
        """)
        new_schema = cursor.fetchone()
        new_sql = new_schema['sql']
        
        if 'UNIQUE(setup_id, arrow_id, arrow_length, point_weight)' in new_sql:
            print("❌ UNIQUE constraint still exists after migration!")
            conn.close()
            return False
        
        # Verify data count
        cursor.execute("SELECT COUNT(*) as count FROM setup_arrows")
        count = cursor.fetchone()['count']
        
        if count != len(existing_data):
            print(f"❌ Data count mismatch! Expected {len(existing_data)}, got {count}")
            conn.close()
            return False
        
        conn.close()
        print(f"✅ Successfully removed UNIQUE constraint and preserved {count} records")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def down(db_path: str) -> bool:
    """
    Add back the UNIQUE constraint (rollback)
    Note: This is potentially destructive if duplicate arrows exist
    """
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check if setup_arrows table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='setup_arrows'
        """)
        
        if not cursor.fetchone():
            print("⚠️  setup_arrows table not found - skipping rollback")
            conn.close()
            return True
        
        print("🔄 Rolling back: Adding UNIQUE constraint to setup_arrows table")
        print("⚠️  Warning: This may fail if duplicate arrows exist!")
        
        # Get all existing data
        cursor.execute("SELECT * FROM setup_arrows ORDER BY id")
        existing_data = cursor.fetchall()
        
        # Check for potential duplicates that would violate the constraint
        cursor.execute("""
            SELECT setup_id, arrow_id, arrow_length, point_weight, COUNT(*) as count
            FROM setup_arrows 
            GROUP BY setup_id, arrow_id, arrow_length, point_weight
            HAVING COUNT(*) > 1
        """)
        duplicates = cursor.fetchall()
        
        if duplicates:
            print(f"❌ Cannot rollback: {len(duplicates)} duplicate arrow combinations found")
            for dup in duplicates:
                print(f"   - Setup {dup['setup_id']}, Arrow {dup['arrow_id']}, "
                      f"Length {dup['arrow_length']}\", Weight {dup['point_weight']}gr "
                      f"({dup['count']} duplicates)")
            conn.close()
            return False
        
        # Create new table with UNIQUE constraint
        cursor.execute("DROP TABLE IF EXISTS setup_arrows_with_unique")
        cursor.execute("""
            CREATE TABLE setup_arrows_with_unique (
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
                FOREIGN KEY (setup_id) REFERENCES bow_setups (id) ON DELETE CASCADE,
                UNIQUE(setup_id, arrow_id, arrow_length, point_weight)
            )
        """)
        
        # Copy data to new table
        for row in existing_data:
            cursor.execute("""
                INSERT INTO setup_arrows_with_unique 
                (id, setup_id, arrow_id, arrow_length, point_weight, calculated_spine, 
                 compatibility_score, notes, created_at, nock_weight, fletching_weight, 
                 insert_weight, wrap_weight, bushing_weight)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row['id'], row['setup_id'], row['arrow_id'], row['arrow_length'],
                row['point_weight'], row['calculated_spine'], row['compatibility_score'],
                row['notes'], row['created_at'],
                row['nock_weight'] if 'nock_weight' in row.keys() else None,
                row['fletching_weight'] if 'fletching_weight' in row.keys() else None,
                row['insert_weight'] if 'insert_weight' in row.keys() else None,
                row['wrap_weight'] if 'wrap_weight' in row.keys() else None,
                row['bushing_weight'] if 'bushing_weight' in row.keys() else None
            ))
        
        # Replace old table
        cursor.execute("DROP TABLE setup_arrows")
        cursor.execute("ALTER TABLE setup_arrows_with_unique RENAME TO setup_arrows")
        
        conn.commit()
        conn.close()
        
        print("✅ Successfully rolled back UNIQUE constraint")
        return True
        
    except Exception as e:
        print(f"❌ Rollback failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# For standalone testing
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
        print(f"Testing migration on {db_path}")
        success = up(db_path)
        print(f"Migration {'succeeded' if success else 'failed'}")
    else:
        print("Usage: python 015_remove_setup_arrows_unique_constraint.py <db_path>")