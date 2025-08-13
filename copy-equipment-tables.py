#!/usr/bin/env python3
"""
Copy missing equipment tables from databases/ to arrow_scraper/ database
"""

import sqlite3
import os

def copy_equipment_tables():
    """Copy equipment tables from source to destination database"""
    
    source_db = '/home/paal/archerytools/arrow_scraper/databases/arrow_database.db'
    dest_db = '/home/paal/archerytools/databases/arrow_database.db'
    
    if not os.path.exists(source_db):
        print(f"❌ Source database not found: {source_db}")
        return False
        
    if not os.path.exists(dest_db):
        print(f"❌ Destination database not found: {dest_db}")
        return False
    
    print("🔄 Copying Equipment Tables")
    print("=" * 50)
    
    # Tables to copy
    tables_to_copy = [
        'manufacturer_equipment_categories',
        'equipment_field_standards'
    ]
    
    try:
        # Connect to both databases
        source_conn = sqlite3.connect(source_db)
        dest_conn = sqlite3.connect(dest_db)
        
        source_cursor = source_conn.cursor()
        dest_cursor = dest_conn.cursor()
        
        for table_name in tables_to_copy:
            print(f"\n📋 Copying table: {table_name}")
            
            # Check if table exists in source
            source_cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name=?
            """, (table_name,))
            
            if not source_cursor.fetchone():
                print(f"   ❌ Table {table_name} not found in source database")
                continue
            
            # Get table schema from source
            source_cursor.execute(f"SELECT sql FROM sqlite_master WHERE name='{table_name}'")
            schema_row = source_cursor.fetchone()
            if not schema_row:
                print(f"   ❌ Could not get schema for {table_name}")
                continue
                
            create_sql = schema_row[0]
            print(f"   📐 Got table schema")
            
            # Drop table if exists in destination
            dest_cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            print(f"   🗑️  Dropped existing table (if any)")
            
            # Create table in destination
            dest_cursor.execute(create_sql)
            print(f"   🏗️  Created table structure")
            
            # Copy data
            source_cursor.execute(f"SELECT * FROM {table_name}")
            rows = source_cursor.fetchall()
            
            if rows:
                # Get column info to build INSERT statement
                source_cursor.execute(f"PRAGMA table_info({table_name})")
                columns = [col[1] for col in source_cursor.fetchall()]
                placeholders = ','.join(['?' for _ in columns])
                
                insert_sql = f"INSERT INTO {table_name} VALUES ({placeholders})"
                dest_cursor.executemany(insert_sql, rows)
                print(f"   📊 Copied {len(rows)} rows")
            else:
                print(f"   📊 No data to copy (empty table)")
        
        # Commit changes
        dest_conn.commit()
        print(f"\n✅ Successfully copied all equipment tables!")
        
        # Verify the copy worked
        print(f"\n🔍 Verification:")
        for table_name in tables_to_copy:
            dest_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = dest_cursor.fetchone()[0]
            print(f"   {table_name}: {count} rows")
        
        source_conn.close()
        dest_conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error copying tables: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = copy_equipment_tables()
    if success:
        print(f"\n🎉 Equipment tables successfully copied!")
        print("   The API should now be able to access form schemas for new categories.")
    else:
        print(f"\n💥 Failed to copy equipment tables.")