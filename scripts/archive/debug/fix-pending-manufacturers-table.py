#!/usr/bin/env python3
"""
Fix pending_manufacturers table by adding missing columns
"""

import sys
import os
sys.path.append('/home/paal/archerytools/arrow_scraper')

from user_database import UserDatabase

def fix_pending_manufacturers_table():
    print("🔧 Fixing pending_manufacturers Table")
    print("=" * 40)
    
    try:
        user_db = UserDatabase()
        conn = user_db.get_connection()
        cursor = conn.cursor()
        
        # List of columns to add with their definitions
        columns_to_add = [
            ('normalized_name', 'TEXT'),
            ('user_count', 'INTEGER DEFAULT 1'),
            ('approved_by_admin_id', 'INTEGER'),
            ('approved_at', 'TIMESTAMP'),
            ('rejection_reason', 'TEXT'),
            ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
            ('updated_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
        ]
        
        # Check current table structure
        cursor.execute("PRAGMA table_info(pending_manufacturers)")
        existing_columns = [col[1] for col in cursor.fetchall()]
        print(f"📋 Current columns: {', '.join(existing_columns)}")
        
        # Add missing columns
        for column_name, column_def in columns_to_add:
            if column_name not in existing_columns:
                try:
                    cursor.execute(f'ALTER TABLE pending_manufacturers ADD COLUMN {column_name} {column_def}')
                    print(f"✅ Added column: {column_name}")
                except Exception as e:
                    print(f"❌ Failed to add {column_name}: {e}")
            else:
                print(f"✅ Column {column_name} already exists")
        
        # Add foreign key constraint if it doesn't exist (can't be added via ALTER TABLE)
        # We'll need to check if the constraint exists another way
        
        # Commit changes
        conn.commit()
        
        # Verify final structure
        cursor.execute("PRAGMA table_info(pending_manufacturers)")
        final_columns = [col[1] for col in cursor.fetchall()]
        print(f"\n📋 Final columns ({len(final_columns)}): {', '.join(final_columns)}")
        
        conn.close()
        print("\n✅ pending_manufacturers table fixed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_pending_manufacturers_table()