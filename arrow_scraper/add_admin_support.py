#!/usr/bin/env python3
"""
Script to add admin support to the user database and grant admin access to messenlien@gmail.com
"""

import sqlite3
import sys
from pathlib import Path

def add_admin_column_and_grant_access():
    """Add is_admin column to users table and grant admin access to messenlien@gmail.com"""
    
    # Use the same path resolution as UserDatabase
    db_path = "user_data.db"
    possible_paths = [
        Path("/app") / db_path,  # Docker/production path
        Path(__file__).parent / db_path, # Default development path (arrow_scraper/)
        Path(__file__).parent.parent / db_path # Root directory path
    ]

    for p in possible_paths:
        if p.exists():
            db_path = str(p)
            break
    
    print(f"Using database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check if is_admin column already exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'is_admin' not in columns:
            print("Adding is_admin column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0")
            conn.commit()
            print("✅ Added is_admin column")
        else:
            print("is_admin column already exists")
        
        # Grant admin access to messenlien@gmail.com
        cursor.execute("UPDATE users SET is_admin = 1 WHERE email = ?", ('messenlien@gmail.com',))
        if cursor.rowcount > 0:
            conn.commit()
            print("✅ Granted admin access to messenlien@gmail.com")
        else:
            print("❌ User messenlien@gmail.com not found")
        
        # Verify the update
        cursor.execute("SELECT email, is_admin FROM users WHERE email = ?", ('messenlien@gmail.com',))
        user = cursor.fetchone()
        if user:
            print(f"✅ Verification: {user['email']} is_admin = {user['is_admin']}")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = add_admin_column_and_grant_access()
    sys.exit(0 if success else 1)