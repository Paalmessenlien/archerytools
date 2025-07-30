#!/usr/bin/env python3
"""
Production Migration Script for bow_setups Table
Ensures all required columns exist for the bow setup functionality
"""
import sys
import sqlite3
import os
from pathlib import Path

# Add arrow_scraper to Python path
sys.path.append(str(Path(__file__).parent / 'arrow_scraper'))

from user_database import UserDatabase

def migrate_bow_setups_table():
    """Add all missing columns to bow_setups table for production compatibility"""
    print("🔧 Migrating bow_setups table - adding all missing columns")
    
    # Connect to the user database
    db = UserDatabase()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        # Get current table schema
        cursor.execute("PRAGMA table_info(bow_setups)")
        existing_columns = {col[1]: col[2] for col in cursor.fetchall()}
        
        print(f"📊 Found {len(existing_columns)} existing columns:")
        for col_name, col_type in existing_columns.items():
            print(f"  • {col_name} ({col_type})")
        
        # Define all required columns that should exist
        required_columns = {
            'riser_brand': 'TEXT',
            'riser_model': 'TEXT', 
            'riser_length': 'TEXT',
            'limb_brand': 'TEXT',
            'limb_model': 'TEXT',
            'limb_length': 'TEXT',
            'compound_brand': 'TEXT',
            'compound_model': 'TEXT',
            'bow_usage': 'TEXT',
            'arrow_length': 'REAL',
            'point_weight': 'REAL',
            'nock_weight': 'REAL',
            'fletching_weight': 'REAL',
            'insert_weight': 'REAL'
        }
        
        # Find missing columns
        missing_columns = []
        for col_name, col_type in required_columns.items():
            if col_name not in existing_columns:
                missing_columns.append((col_name, col_type))
        
        if not missing_columns:
            print("✅ All required columns already exist - no migration needed")
            return True
        
        print(f"\n➕ Adding {len(missing_columns)} missing columns:")
        
        # Add missing columns
        for col_name, col_type in missing_columns:
            print(f"  • Adding {col_name} ({col_type})...")
            cursor.execute(f"ALTER TABLE bow_setups ADD COLUMN {col_name} {col_type}")
        
        # Commit changes
        conn.commit()
        print(f"\n✅ Successfully added {len(missing_columns)} columns to bow_setups table")
        
        # Verify final schema
        cursor.execute("PRAGMA table_info(bow_setups)")
        final_columns = cursor.fetchall()
        print(f"\n📊 Final table schema ({len(final_columns)} columns):")
        for col in final_columns:
            status = "NEW" if col[1] in [mc[0] for mc in missing_columns] else ""
            print(f"  • {col[1]} ({col[2]}) {status}")
        
        # Test basic functionality
        cursor.execute("SELECT COUNT(*) FROM bow_setups")
        count = cursor.fetchone()[0]
        print(f"\n📈 Table contains {count} existing bow setups")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def verify_migration():
    """Verify that the migration was successful"""
    print("\n🔍 Verifying migration...")
    
    db = UserDatabase()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        # Test that we can select from all expected columns
        test_query = """
        SELECT id, user_id, name, bow_type, draw_weight, draw_length,
               riser_brand, riser_model, riser_length,
               limb_brand, limb_model, limb_length,
               compound_brand, compound_model,
               bow_usage, description
        FROM bow_setups LIMIT 1
        """
        
        cursor.execute(test_query)
        print("✅ All columns accessible - migration verified successfully")
        return True
        
    except sqlite3.OperationalError as e:
        print(f"❌ Migration verification failed: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("🚀 Starting bow_setups table migration for production...")
    
    # Run the migration
    if migrate_bow_setups_table():
        # Verify the migration worked
        if verify_migration():
            print("\n🎉 Migration completed successfully!")
            print("✅ Production database is now compatible with bow setup functionality")
        else:
            print("\n⚠️ Migration completed but verification failed")
            sys.exit(1)
    else:
        print("\n❌ Migration failed")
        sys.exit(1)