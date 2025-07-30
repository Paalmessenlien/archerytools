#!/usr/bin/env python3
"""
Migration script to add brand fields to bow_setups table.
This adds riser_brand, limb_brand, and compound_brand columns.
"""
import sqlite3
import sys
from pathlib import Path

# Add the arrow_scraper directory to Python path
sys.path.append(str(Path(__file__).parent / 'arrow_scraper'))

from user_database import UserDatabase

def main():
    print("🚀 Starting bow_setups table migration for brand fields...")
    print("🏹 Migrating bow_setups table - adding brand fields")
    
    try:
        # Initialize user database
        user_db = UserDatabase()
        conn = user_db.get_connection()
        cursor = conn.cursor()
        
        # Get current column information
        cursor.execute("PRAGMA table_info(bow_setups)")
        columns_info = cursor.fetchall()
        current_columns = [col[1] for col in columns_info]
        print(f"Current columns: {current_columns}")
        
        # Add brand columns if they don't exist
        brand_columns = [
            ('riser_brand', 'TEXT'),
            ('limb_brand', 'TEXT'),
            ('compound_brand', 'TEXT')
        ]
        
        added_columns = []
        for column_name, column_type in brand_columns:
            if column_name not in current_columns:
                print(f"📦 Adding {column_name} column...")
                cursor.execute(f"ALTER TABLE bow_setups ADD COLUMN {column_name} {column_type}")
                added_columns.append(column_name)
            else:
                print(f"✅ {column_name} column already exists")
        
        # Commit changes
        conn.commit()
        
        # Verify final state
        cursor.execute("PRAGMA table_info(bow_setups)")
        columns_info = cursor.fetchall()
        final_columns = [col[1] for col in columns_info]
        print(f"Final columns: {final_columns}")
        
        if added_columns:
            print(f"Added: {added_columns}")
        
        # Count existing setups
        cursor.execute("SELECT COUNT(*) FROM bow_setups")
        setup_count = cursor.fetchone()[0]
        print(f"📊 {setup_count} bow setups will have new brand fields available")
        
        conn.close()
        print("✅ Migration completed successfully!")
        print("🎯 Migration complete - brand fields added")  
        print("💡 New fields: riser_brand, limb_brand, compound_brand for better bow organization")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()