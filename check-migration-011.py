#!/usr/bin/env python3
"""
Check if migration 011 was fully applied
"""

import sys
import os
sys.path.append('/home/paal/archerytools/arrow_scraper')

from user_database import UserDatabase

def check_migration_011():
    print("🔍 Checking Migration 011 Status")
    print("=" * 40)
    
    try:
        user_db = UserDatabase()
        conn = user_db.get_connection()
        cursor = conn.cursor()
        
        # Check schema_version table
        try:
            cursor.execute("SELECT version, applied_at FROM schema_version ORDER BY version DESC LIMIT 5")
            versions = cursor.fetchall()
            print("📋 Recent migrations:")
            for v in versions:
                print(f"   Version {v['version']} applied at {v['applied_at']}")
        except:
            print("❌ schema_version table doesn't exist")
        
        # Check pending_manufacturers table structure
        cursor.execute("PRAGMA table_info(pending_manufacturers)")
        columns = cursor.fetchall()
        expected_columns = [
            'id', 'name', 'normalized_name', 'category_context', 'usage_count',
            'user_count', 'first_seen', 'last_seen', 'status', 'created_by_user_id',
            'approved_by_admin_id', 'admin_notes', 'approved_at', 'rejection_reason',
            'created_at', 'updated_at'
        ]
        
        actual_columns = [col[1] for col in columns]
        print(f"\n📋 pending_manufacturers table columns ({len(actual_columns)} found):")
        for col in actual_columns:
            status = "✅" if col in expected_columns else "❓"
            print(f"   {status} {col}")
        
        print(f"\n📋 Expected columns ({len(expected_columns)}):")
        for col in expected_columns:
            status = "✅" if col in actual_columns else "❌"
            print(f"   {status} {col}")
        
        missing_columns = set(expected_columns) - set(actual_columns)
        if missing_columns:
            print(f"\n❌ Missing columns: {', '.join(missing_columns)}")
        else:
            print(f"\n✅ All expected columns present!")
        
        # Check other tables from migration 011
        tables_to_check = ['user_pending_manufacturers', 'manufacturer_approval_log']
        for table_name in tables_to_check:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            exists = cursor.fetchone()
            print(f"{'✅' if exists else '❌'} {table_name} table exists")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_migration_011()