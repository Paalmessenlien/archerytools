#!/usr/bin/env python3
"""
Debug script to check pending manufacturers in the database
"""

import sys
import os
sys.path.append('/home/paal/archerytools/arrow_scraper')

from user_database import UserDatabase
from equipment_learning_manager import EquipmentLearningManager

def debug_pending_manufacturers():
    print("🔍 Debugging Pending Manufacturers")
    print("=" * 50)
    
    try:
        # Check if migration 011 was applied
        user_db = UserDatabase()
        conn = user_db.get_connection()
        cursor = conn.cursor()
        
        # Check if pending_manufacturers table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pending_manufacturers'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("❌ pending_manufacturers table does not exist!")
            print("   Migration 011 may not have been applied.")
            return
        
        print("✅ pending_manufacturers table exists")
        
        # Check table schema
        cursor.execute("PRAGMA table_info(pending_manufacturers)")
        columns = cursor.fetchall()
        print(f"📋 Table has {len(columns)} columns:")
        for col in columns:
            print(f"   - {col[1]} ({col[2]})")
        
        # Check for any pending manufacturers
        cursor.execute("SELECT COUNT(*) as count FROM pending_manufacturers")
        total_count = cursor.fetchone()['count']
        print(f"\n📊 Total manufacturers in pending table: {total_count}")
        
        if total_count > 0:
            # Show all pending manufacturers
            cursor.execute('''
                SELECT pm.*, u.name as created_by_name
                FROM pending_manufacturers pm
                LEFT JOIN users u ON pm.created_by_user_id = u.id
                ORDER BY pm.created_at DESC
            ''')
            
            manufacturers = cursor.fetchall()
            print(f"\n📋 All manufacturers in pending_manufacturers table:")
            for m in manufacturers:
                print(f"   ID: {m['id']}, Name: '{m['name']}', Status: {m['status']}")
                print(f"       Created: {m['created_at']}, Usage: {m['usage_count']}, User: {m['created_by_name']}")
                print(f"       Category Context: {m['category_context']}")
                print()
        
        # Check user_pending_manufacturers table
        cursor.execute("SELECT COUNT(*) as count FROM user_pending_manufacturers")
        user_pending_count = cursor.fetchone()['count']
        print(f"📊 Total user-manufacturer relationships: {user_pending_count}")
        
        # Test the equipment learning manager
        print("\n🧠 Testing EquipmentLearningManager:")
        learning = EquipmentLearningManager()
        pending_list = learning.get_pending_manufacturers('pending', 50)
        print(f"   get_pending_manufacturers() returned {len(pending_list)} items:")
        for p in pending_list:
            print(f"     - {p.get('name')} (status: {p.get('status')})")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error during debugging: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_pending_manufacturers()