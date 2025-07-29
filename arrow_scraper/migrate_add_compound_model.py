#!/usr/bin/env python3
"""
Database migration to add compound_model field for compound bows.
This allows users to specify the exact model name when selecting a compound bow brand.
"""

import sqlite3
import os
import sys
from user_database import UserDatabase

def migrate_add_compound_model():
    """Add compound_model field to bow_setups table"""
    print("🏹 Migrating bow_setups table - adding compound model field")
    
    try:
        # Get user database connection
        user_db = UserDatabase()
        conn = user_db.get_connection()
        cursor = conn.cursor()
        
        # Check current table structure
        cursor.execute("PRAGMA table_info(bow_setups)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"Current columns: {columns}")
        
        # Check if compound_model already exists
        if 'compound_model' in columns:
            print("✅ Migration already completed - compound_model column already exists")
            conn.close()
            return
        
        # Add compound_model column
        print("📦 Adding compound_model column...")
        cursor.execute("ALTER TABLE bow_setups ADD COLUMN compound_model TEXT")
        
        # Commit changes
        conn.commit()
        
        # Verify migration
        cursor.execute("PRAGMA table_info(bow_setups)")
        final_columns = [column[1] for column in cursor.fetchall()]
        
        print(f"✅ Migration completed successfully!")
        print(f"Final columns: {final_columns}")
        print(f"Added: compound_model")
        
        # Count bow setups
        cursor.execute("SELECT COUNT(*) FROM bow_setups")
        count = cursor.fetchone()[0]
        print(f"📊 {count} bow setups will have the new field available")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 Starting bow_setups table migration for compound model field...")
    migrate_add_compound_model()
    print("🎯 Migration complete - compound_model field added")
    print("💡 Users can now specify model names for compound bows (e.g., RX-7 Ultra, Halon X, V3X)")