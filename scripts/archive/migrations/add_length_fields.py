#!/usr/bin/env python3
"""
Migration script to add riser_length and limb_length fields to bow_setups table
"""
import sys
sys.path.append('arrow_scraper')

from user_database import UserDatabase

def add_length_fields():
    print("🔧 Adding riser_length and limb_length fields to bow_setups table")
    
    db = UserDatabase()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(bow_setups)")
        columns = [col[1] for col in cursor.fetchall()]
        
        fields_to_add = []
        if 'riser_length' not in columns:
            fields_to_add.append('riser_length')
        if 'limb_length' not in columns:
            fields_to_add.append('limb_length')
            
        if not fields_to_add:
            print("✅ Fields already exist - no migration needed")
            return
            
        # Add missing columns
        for field in fields_to_add:
            print(f"  ➕ Adding {field} column...")
            cursor.execute(f"ALTER TABLE bow_setups ADD COLUMN {field} TEXT")
            
        conn.commit()
        print(f"✅ Successfully added {len(fields_to_add)} new fields")
        
        # Verify the changes
        cursor.execute("PRAGMA table_info(bow_setups)")
        columns = cursor.fetchall()
        print(f"📊 Updated table now has {len(columns)} columns:")
        for col in columns:
            if col[1] in fields_to_add:
                print(f"  ✅ {col[1]} ({col[2]}) - NEW")
            else:
                print(f"  • {col[1]} ({col[2]})")
                
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_length_fields()