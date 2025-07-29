#!/usr/bin/env python3
"""
Database migration to add bow usage and model name fields for Issue #13.
- Add bow_usage field for recurve bows (Olympic, Barebow, other)
- Add riser_model field for riser model names
- Add limb_model field for limb model names
"""

import sqlite3
import os
import sys
from user_database import UserDatabase

def migrate_add_bow_info_fields():
    """Add bow_usage, riser_model, and limb_model fields to bow_setups table"""
    print("🏹 Migrating bow_setups table - adding bow usage and model name fields")
    
    try:
        # Get user database connection
        user_db = UserDatabase()
        conn = user_db.get_connection()
        cursor = conn.cursor()
        
        # Check current table structure
        cursor.execute("PRAGMA table_info(bow_setups)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"Current columns: {columns}")
        
        # Check if new columns already exist
        new_columns = ['bow_usage', 'riser_model', 'limb_model']
        existing_new_columns = [col for col in new_columns if col in columns]
        
        if len(existing_new_columns) == len(new_columns):
            print("✅ Migration already completed - all new columns found")
            conn.close()
            return
        
        # Add missing columns one by one
        for column in new_columns:
            if column not in columns:
                print(f"📦 Adding {column} column...")
                if column == 'bow_usage':
                    cursor.execute("ALTER TABLE bow_setups ADD COLUMN bow_usage TEXT")
                elif column == 'riser_model':
                    cursor.execute("ALTER TABLE bow_setups ADD COLUMN riser_model TEXT")
                elif column == 'limb_model':
                    cursor.execute("ALTER TABLE bow_setups ADD COLUMN limb_model TEXT")
        
        # Commit changes
        conn.commit()
        
        # Verify migration
        cursor.execute("PRAGMA table_info(bow_setups)")
        final_columns = [column[1] for column in cursor.fetchall()]
        
        print(f"✅ Migration completed successfully!")
        print(f"Final columns: {final_columns}")
        print(f"Added: {[col for col in new_columns if col not in columns]}")
        
        # Count bow setups
        cursor.execute("SELECT COUNT(*) FROM bow_setups")
        count = cursor.fetchone()[0]
        print(f"📊 {count} bow setups will have new fields available")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 Starting bow_setups table migration for Issue #13...")
    migrate_add_bow_info_fields()
    print("🎯 Migration complete - bow usage and model name fields added")
    print("💡 New fields: bow_usage (Olympic/Barebow/other), riser_model, limb_model")