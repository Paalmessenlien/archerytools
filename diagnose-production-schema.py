#!/usr/bin/env python3
"""
Production Database Schema Diagnostic Script
Checks current database state and identifies missing migrations
"""

import sqlite3
import os
import sys
from pathlib import Path

def check_database_status():
    """Check the current state of the production database"""
    
    # Try different possible database paths
    possible_paths = [
        '/app/databases/arrow_database.db',
        '/app/arrow_database.db',
        './databases/arrow_database.db',
        './arrow_database.db'
    ]
    
    db_path = None
    for path in possible_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("❌ Database file not found in any expected location")
        print("Expected locations:", possible_paths)
        return False
    
    print(f"✅ Found database at: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if schema_migrations table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='schema_migrations'")
        has_migrations_table = cursor.fetchone() is not None
        
        print(f"\n📋 Schema Migrations Table: {'✅ Present' if has_migrations_table else '❌ Missing'}")
        
        if has_migrations_table:
            cursor.execute('SELECT version, applied_at FROM schema_migrations ORDER BY version')
            migrations = cursor.fetchall()
            print(f"Applied migrations: {len(migrations)}")
            for version, applied_at in migrations:
                print(f"  - Migration {version}: {applied_at}")
        
        # Check for consolidation migration specifically
        print(f"\n🔍 Checking for Migration 023 (Database Consolidation):")
        if has_migrations_table:
            cursor.execute("SELECT * FROM schema_migrations WHERE version = '023'")
            migration_023 = cursor.fetchone()
            if migration_023:
                print("  ✅ Migration 023 has been applied")
            else:
                print("  ❌ Migration 023 (consolidation) has NOT been applied")
        
        # Check table structure
        print(f"\n🏗️  Database Architecture Analysis:")
        
        # Check for user tables (indicates unified architecture)
        user_tables = ['users', 'bow_setups', 'guide_sessions', 'backup_metadata', 'bow_equipment']
        user_tables_found = 0
        
        for table in user_tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if cursor.fetchone():
                user_tables_found += 1
                print(f"  ✅ {table} table exists")
                
                # Check columns
                cursor.execute(f'PRAGMA table_info({table})')
                columns = [row[1] for row in cursor.fetchall()]
                print(f"     Columns ({len(columns)}): {', '.join(columns)}")
            else:
                print(f"  ❌ {table} table missing")
        
        # Check for arrow tables
        arrow_tables = ['arrows', 'spine_specifications', 'manufacturers']
        arrow_tables_found = 0
        
        for table in arrow_tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if cursor.fetchone():
                arrow_tables_found += 1
                print(f"  ✅ {table} table exists")
            else:
                print(f"  ❌ {table} table missing")
        
        # Determine architecture
        if user_tables_found >= 3 and arrow_tables_found >= 2:
            architecture = "UNIFIED"
        elif arrow_tables_found >= 2 and user_tables_found == 0:
            architecture = "SEPARATE"
        else:
            architecture = "INCOMPLETE"
        
        print(f"\n🏛️  Database Architecture: {architecture}")
        print(f"   User tables found: {user_tables_found}/{len(user_tables)}")
        print(f"   Arrow tables found: {arrow_tables_found}/{len(arrow_tables)}")
        
        # Check for old user_data.db file
        user_db_paths = ['/app/databases/user_data.db', './databases/user_data.db', './user_data.db']
        for user_db_path in user_db_paths:
            if os.path.exists(user_db_path):
                print(f"\n📁 Found separate user database: {user_db_path}")
                user_conn = sqlite3.connect(user_db_path)
                user_cursor = user_conn.cursor()
                user_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                user_tables_in_separate = [row[0] for row in user_cursor.fetchall()]
                print(f"   Tables in user database: {user_tables_in_separate}")
                user_conn.close()
                break
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return False

def recommend_actions():
    """Provide recommendations based on findings"""
    print(f"\n🎯 RECOMMENDED ACTIONS:")
    print(f"1. Run the consolidation migration:")
    print(f"   docker exec arrowtuner-api python3 /app/migrations/023_consolidate_user_database.py")
    print(f"")
    print(f"2. Check if migration ran successfully:")
    print(f"   docker exec arrowtuner-api python3 /app/diagnose-production-schema.py")
    print(f"")
    print(f"3. If issues persist, check migration logs:")
    print(f"   docker logs arrowtuner-api | grep -i migration")
    print(f"")
    print(f"4. Restart the API container after migrations:")
    print(f"   docker restart arrowtuner-api")

if __name__ == "__main__":
    print("🔍 Production Database Schema Diagnostic")
    print("=" * 50)
    
    success = check_database_status()
    
    if success:
        recommend_actions()
    else:
        print("\n❌ Unable to complete diagnostic. Check database paths and permissions.")
    
    print(f"\n" + "=" * 50)