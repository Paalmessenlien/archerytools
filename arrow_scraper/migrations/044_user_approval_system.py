#!/usr/bin/env python3
"""
Migration 044: User Approval System
Adds user approval workflow - new users require admin activation before accessing the platform
"""
import sqlite3
import sys
import os

def get_migration_info():
    """Return migration metadata"""
    return {
        'version': 44,
        'description': 'User approval system - add status column to users table',
        'author': 'System', 
        'created_at': '2025-08-28',
        'target_database': 'arrow',  # Unified database - all data in arrow_database.db
        'dependencies': ['023'],  # Depends on unified database architecture
        'environments': ['all']
    }

def migrate_up(cursor):
    """Apply the migration"""
    conn = cursor.connection
    try:
        print("🔧 Migration 044: Adding user approval system...")
        
        # Check if status column already exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'status' not in columns:
            # Add status column with default 'pending' for new users
            cursor.execute("ALTER TABLE users ADD COLUMN status TEXT DEFAULT 'pending'")
            print("✅ Added status column to users table")
        else:
            print("ℹ️ Status column already exists in users table")
        
        # Update existing users to 'active' status (grandfather existing users)
        cursor.execute("UPDATE users SET status = 'active' WHERE status IS NULL OR status = ''")
        affected_rows = cursor.rowcount
        print(f"✅ Updated {affected_rows} existing users to 'active' status")
        
        # Ensure admin user (messenlien@gmail.com) is always active
        cursor.execute("UPDATE users SET status = 'active' WHERE email = 'messenlien@gmail.com'")
        
        conn.commit()
        print("🎯 Migration 044 completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration 044 failed: {e}")
        conn.rollback()
        return False

def migrate_down(cursor):
    """Rollback the migration"""
    conn = cursor.connection
    try:
        print("🔄 Rolling back Migration 044...")
        
        # Note: SQLite doesn't support DROP COLUMN directly
        # This rollback would require recreating the table without the status column
        # For simplicity, we'll just reset all users to active status
        cursor.execute("UPDATE users SET status = 'active'")
        
        conn.commit()
        print("✅ Migration 044 rollback completed")
        return True
        
    except Exception as e:
        print(f"❌ Migration 044 rollback failed: {e}")
        conn.rollback()
        return False

if __name__ == "__main__":
    # Test standalone - matches recommended format from documentation
    db_path = os.path.join(os.path.dirname(__file__), '..', 'databases', 'arrow_database.db')
    
    # For testing, use a temporary database
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        db_path = "test_migration_044.db"
        if os.path.exists(db_path):
            os.remove(db_path)
            
        # Create test database with users table
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                name TEXT,
                is_admin BOOLEAN DEFAULT 0
            )
        """)
        cursor.execute("INSERT INTO users (email, name) VALUES ('test@example.com', 'Test User')")
        cursor.execute("INSERT INTO users (email, name) VALUES ('messenlien@gmail.com', 'Admin User')")
        conn.commit()
    else:
        # Use actual database for standalone execution
        conn = sqlite3.connect(db_path)
    
    try:
        success = migrate_up(conn.cursor())
        print("✅ Migration test completed successfully" if success else "❌ Migration test failed")
        
        if success and len(sys.argv) > 1 and sys.argv[1] == "test":
            # Verify test results
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(users)")
            columns = [column[1] for column in cursor.fetchall()]
            if 'status' in columns:
                cursor.execute("SELECT email, status FROM users")
                for row in cursor.fetchall():
                    print(f"  User: {row[0]} -> Status: {row[1]}")
                    
    finally:
        conn.close()
        if len(sys.argv) > 1 and sys.argv[1] == "test" and os.path.exists("test_migration_044.db"):
            os.remove("test_migration_044.db")