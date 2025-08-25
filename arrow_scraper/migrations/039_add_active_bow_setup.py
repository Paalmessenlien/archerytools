"""
Migration 039: Add Active Bow Setup Support
Adds active_bow_setup_id to users table for tracking user's currently active setup
"""

import sqlite3
import sys
import os

def get_migration_info():
    """Return migration metadata"""
    return {
        'version': 39,
        'description': 'Add Active Bow Setup Support',
        'author': 'System',
        'created_at': '2025-08-25',
        'target_database': 'user',  # This targets the user database
        'dependencies': [],
        'environments': ['all']
    }

def migrate_up(cursor):
    """Add active_bow_setup_id to users table"""
    conn = cursor.connection
    
    try:
        print("🔧 Migration 039: Adding active bow setup support...")
        
        # Add active_bow_setup_id column to users table
        try:
            cursor.execute("""
                ALTER TABLE users ADD COLUMN active_bow_setup_id INTEGER
                REFERENCES bow_setups(id) ON DELETE SET NULL
            """)
            print("✅ Added active_bow_setup_id column to users table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("✅ active_bow_setup_id column already exists")
            else:
                raise e
        
        # Create index for better performance
        try:
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_users_active_bow_setup
                ON users(active_bow_setup_id)
            """)
            print("✅ Created index for active_bow_setup_id")
        except Exception as e:
            print(f"⚠️ Failed to create index: {e}")
        
        conn.commit()
        print("✅ Migration 039 completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Migration 039 failed: {e}")
        conn.rollback()
        return False

def migrate_down(cursor):
    """Remove active_bow_setup_id from users table"""
    conn = cursor.connection
    
    try:
        print("🔄 Migration 039: Downgrading active bow setup support...")
        
        # SQLite doesn't support DROP COLUMN directly, so we need to recreate the table
        # For now, just log that downgrade is not supported
        print("⚠️ Downgrade not supported for this migration - column will remain")
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"❌ Migration 039 downgrade failed: {e}")
        conn.rollback()
        return False

if __name__ == "__main__":
    # Test the migration
    db_path = os.path.join(os.path.dirname(__file__), '..', 'databases', 'user_data.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        sys.exit(1)
    
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