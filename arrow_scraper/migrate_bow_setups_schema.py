#!/usr/bin/env python3
"""
Migration script to update bow_setups table schema to match frontend requirements.
Removes arrow-specific fields and adds bow configuration fields.
"""

import sqlite3
import os
from pathlib import Path

def get_db_path():
    """Find the user database path"""
    possible_paths = [
        Path("user_data.db"),
        Path("/app/user_data/user_data.db"),
        Path("/app/user_data.db"),
    ]
    
    for path in possible_paths:
        if path.exists():
            return str(path)
    
    # Default to local path
    return "user_data.db"

def backup_database(db_path):
    """Create a backup of the database"""
    backup_path = f"{db_path}.backup"
    print(f"Creating backup at {backup_path}")
    import shutil
    shutil.copy2(db_path, backup_path)
    return backup_path

def migrate_bow_setups_table(db_path):
    """Migrate bow_setups table to new schema"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Begin transaction
        cursor.execute("BEGIN TRANSACTION")
        
        # Get current schema
        cursor.execute("PRAGMA table_info(bow_setups)")
        current_columns = {col[1] for col in cursor.fetchall()}
        print(f"Current columns: {current_columns}")
        
        # Create temporary table with new schema
        print("Creating new table with updated schema...")
        cursor.execute("""
            CREATE TABLE bow_setups_new (
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
        
        # Copy data from old table to new table
        print("Copying existing data...")
        # Only copy columns that exist in both tables
        common_columns = ['id', 'user_id', 'name', 'bow_type', 'draw_weight', 'draw_length', 'created_at']
        columns_to_copy = [col for col in common_columns if col in current_columns]
        
        cursor.execute(f"""
            INSERT INTO bow_setups_new ({', '.join(columns_to_copy)})
            SELECT {', '.join(columns_to_copy)}
            FROM bow_setups
        """)
        
        rows_copied = cursor.rowcount
        print(f"Copied {rows_copied} bow setups")
        
        # Drop old table and rename new table
        print("Replacing old table...")
        cursor.execute("DROP TABLE bow_setups")
        cursor.execute("ALTER TABLE bow_setups_new RENAME TO bow_setups")
        
        # Commit transaction
        cursor.execute("COMMIT")
        print("✅ Migration completed successfully!")
        
        # Verify new schema
        cursor.execute("PRAGMA table_info(bow_setups)")
        new_columns = cursor.fetchall()
        print("\nNew table schema:")
        for col in new_columns:
            print(f"  {col[1]} - {col[2]}")
            
    except Exception as e:
        cursor.execute("ROLLBACK")
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        conn.close()

def main():
    """Main migration function"""
    db_path = get_db_path()
    print(f"Database path: {db_path}")
    
    if not Path(db_path).exists():
        print("❌ Database not found!")
        return
    
    # Create backup
    backup_path = backup_database(db_path)
    print(f"✅ Backup created at {backup_path}")
    
    try:
        # Run migration
        migrate_bow_setups_table(db_path)
        
        # Test connection
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM bow_setups")
        count = cursor.fetchone()[0]
        conn.close()
        print(f"\n✅ Database is working correctly. Found {count} bow setups.")
        
    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        print(f"You can restore from backup: {backup_path}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())