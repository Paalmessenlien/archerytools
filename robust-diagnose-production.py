#!/usr/bin/env python3
"""
Robust Production Database Schema Diagnostic Script
Handles different migration table schemas and database configurations
"""

import sqlite3
import os
import sys
from pathlib import Path

def analyze_migration_table(cursor):
    """Analyze the structure of the migration table"""
    try:
        # Check what migration tables exist
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name LIKE '%migration%'
        """)
        migration_tables = [row[0] for row in cursor.fetchall()]
        
        print(f"Migration tables found: {migration_tables}")
        
        for table in migration_tables:
            print(f"\n📋 Analyzing {table} table structure:")
            cursor.execute(f'PRAGMA table_info({table})')
            columns = cursor.fetchall()
            
            print(f"  Columns ({len(columns)}):")
            for col in columns:
                print(f"    - {col[1]} ({col[2]}) {'PRIMARY KEY' if col[5] else ''}")
            
            # Try to get some sample data
            try:
                cursor.execute(f'SELECT * FROM {table} LIMIT 5')
                rows = cursor.fetchall()
                print(f"  Sample data ({len(rows)} rows):")
                for i, row in enumerate(rows):
                    print(f"    Row {i+1}: {row}")
            except Exception as e:
                print(f"    Error reading data: {e}")
        
        return migration_tables
        
    except Exception as e:
        print(f"Error analyzing migration tables: {e}")
        return []

def check_applied_migrations(cursor, migration_tables):
    """Check applied migrations using whatever table structure exists"""
    applied_migrations = []
    
    for table in migration_tables:
        try:
            # Get table structure
            cursor.execute(f'PRAGMA table_info({table})')
            columns = [col[1] for col in cursor.fetchall()]
            
            print(f"\n🔍 Checking migrations in {table}:")
            print(f"  Available columns: {columns}")
            
            # Try different column name patterns
            version_col = None
            if 'version' in columns:
                version_col = 'version'
            elif 'migration_version' in columns:
                version_col = 'migration_version'
            elif 'id' in columns:
                version_col = 'id'
            elif 'name' in columns:
                version_col = 'name'
            
            if version_col:
                cursor.execute(f'SELECT {version_col} FROM {table}')
                migrations = [row[0] for row in cursor.fetchall()]
                applied_migrations.extend(migrations)
                print(f"  Applied migrations: {migrations}")
            else:
                print(f"  ⚠️  Could not determine version column in {table}")
                
        except Exception as e:
            print(f"  Error reading {table}: {e}")
    
    return applied_migrations

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
    print(f"📊 Database size: {os.path.getsize(db_path) / (1024*1024):.2f} MB")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        all_tables = [row[0] for row in cursor.fetchall()]
        
        print(f"\n📋 All tables found ({len(all_tables)}):")
        for table in all_tables:
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            count = cursor.fetchone()[0]
            print(f"  - {table}: {count} rows")
        
        # Analyze migration tables specifically
        migration_tables = analyze_migration_table(cursor)
        
        # Check applied migrations
        if migration_tables:
            applied_migrations = check_applied_migrations(cursor, migration_tables)
            print(f"\n🎯 Summary of applied migrations: {applied_migrations}")
        
        # Check for consolidation migration specifically
        print(f"\n🔍 Checking for Migration 023 (Database Consolidation):")
        
        # Try different ways to find migration 023
        found_023 = False
        for table in migration_tables:
            try:
                cursor.execute(f"""
                    SELECT * FROM {table} 
                    WHERE version = '023' OR migration_version = '023' 
                    OR id = '023' OR name LIKE '%023%'
                """)
                result = cursor.fetchone()
                if result:
                    found_023 = True
                    print(f"  ✅ Migration 023 found in {table}: {result}")
                    break
            except Exception as e:
                # Try simpler queries
                try:
                    cursor.execute(f"SELECT * FROM {table}")
                    rows = cursor.fetchall()
                    for row in rows:
                        if '023' in str(row):
                            found_023 = True
                            print(f"  ✅ Migration 023 found in {table}: {row}")
                            break
                except:
                    continue
        
        if not found_023:
            print("  ❌ Migration 023 (consolidation) has NOT been applied")
        
        # Check database architecture
        print(f"\n🏗️  Database Architecture Analysis:")
        
        # Check for user tables (indicates unified architecture)
        user_tables = ['users', 'bow_setups', 'guide_sessions', 'backup_metadata', 'bow_equipment']
        user_tables_found = 0
        missing_user_tables = []
        
        for table in user_tables:
            if table in all_tables:
                user_tables_found += 1
                print(f"  ✅ {table} table exists")
                
                # Check columns in detail
                cursor.execute(f'PRAGMA table_info({table})')
                columns = [row[1] for row in cursor.fetchall()]
                print(f"     Columns ({len(columns)}): {', '.join(columns)}")
            else:
                missing_user_tables.append(table)
                print(f"  ❌ {table} table missing")
        
        # Check for arrow tables
        arrow_tables = ['arrows', 'spine_specifications', 'manufacturers']
        arrow_tables_found = 0
        missing_arrow_tables = []
        
        for table in arrow_tables:
            if table in all_tables:
                arrow_tables_found += 1
                print(f"  ✅ {table} table exists")
                
                # Get row count
                cursor.execute(f'SELECT COUNT(*) FROM {table}')
                count = cursor.fetchone()[0]
                print(f"     Rows: {count}")
            else:
                missing_arrow_tables.append(table)
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
        
        if missing_user_tables:
            print(f"   Missing user tables: {missing_user_tables}")
        if missing_arrow_tables:
            print(f"   Missing arrow tables: {missing_arrow_tables}")
        
        # Check for old user_data.db file
        user_db_paths = ['/app/databases/user_data.db', './databases/user_data.db', './user_data.db']
        for user_db_path in user_db_paths:
            if os.path.exists(user_db_path):
                print(f"\n📁 Found separate user database: {user_db_path}")
                print(f"   Size: {os.path.getsize(user_db_path) / (1024*1024):.2f} MB")
                
                try:
                    user_conn = sqlite3.connect(user_db_path)
                    user_cursor = user_conn.cursor()
                    user_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    user_tables_in_separate = [row[0] for row in user_cursor.fetchall()]
                    print(f"   Tables in user database: {user_tables_in_separate}")
                    
                    # Check row counts
                    for table in user_tables_in_separate:
                        try:
                            user_cursor.execute(f'SELECT COUNT(*) FROM {table}')
                            count = user_cursor.fetchone()[0]
                            print(f"     - {table}: {count} rows")
                        except:
                            pass
                    
                    user_conn.close()
                except Exception as e:
                    print(f"   Error reading user database: {e}")
                break
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

def recommend_actions():
    """Provide recommendations based on findings"""
    print(f"\n🎯 RECOMMENDED ACTIONS:")
    print(f"1. Run the consolidation migration manually:")
    print(f"   docker exec arrowtuner-api python3 /app/fix-production-schema.py")
    print(f"")
    print(f"2. Check migration table structure manually:")
    print(f"   docker exec arrowtuner-api sqlite3 /app/databases/arrow_database.db '.schema schema_migrations'")
    print(f"")
    print(f"3. If migration table is corrupted, recreate it:")
    print(f"   docker exec arrowtuner-api sqlite3 /app/databases/arrow_database.db 'DROP TABLE schema_migrations;'")
    print(f"   docker exec arrowtuner-api python3 /app/fix-production-schema.py")
    print(f"")
    print(f"4. Check API container logs for more details:")
    print(f"   docker logs arrowtuner-api | tail -50")

if __name__ == "__main__":
    print("🔍 Robust Production Database Schema Diagnostic")
    print("=" * 60)
    
    success = check_database_status()
    
    if success:
        recommend_actions()
    else:
        print("\n❌ Unable to complete diagnostic. Check database paths and permissions.")
    
    print(f"\n" + "=" * 60)