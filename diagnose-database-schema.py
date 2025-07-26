#!/usr/bin/env python3
"""
Diagnose Database Schema
Checks the actual database schema that was built vs what the code expects
"""

import sqlite3
import os

def diagnose_database_schema():
    """Check the actual database schema"""
    print("🔍 Diagnosing Database Schema")
    print("=" * 40)
    
    # Check for database files
    db_files = [
        "arrow_scraper/arrow_database.db",
        "arrow_database.db"
    ]
    
    database_path = None
    for db_file in db_files:
        if os.path.exists(db_file):
            database_path = db_file
            print(f"✅ Found database: {database_path}")
            break
    
    if not database_path:
        print("❌ No database found")
        return
    
    try:
        conn = sqlite3.connect(database_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        cursor = conn.cursor()
        
        # Check tables
        print("\n📋 Tables in database:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table['name']
            print(f"  📄 {table_name}")
            
            # Check columns in each table
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            print(f"    Columns:")
            for col in columns:
                print(f"      - {col['name']} ({col['type']})")
            
            # Check row count
            cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            count = cursor.fetchone()['count']
            print(f"    Rows: {count}")
            
            if count > 0 and count <= 3:
                # Show sample data for small tables
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                rows = cursor.fetchall()
                print(f"    Sample data:")
                for row in rows:
                    row_dict = dict(row)
                    print(f"      {row_dict}")
            
            print()
        
        # Test get_statistics method compatibility
        print("🧪 Testing get_statistics compatibility:")
        
        try:
            # Test the exact query from get_statistics
            cursor.execute('SELECT COUNT(*) as count FROM arrows')
            arrow_count = cursor.fetchone()['count']
            print(f"  ✅ Arrow count query works: {arrow_count}")
            
            cursor.execute('SELECT COUNT(*) as count FROM spine_specifications')
            spec_count = cursor.fetchone()['count']
            print(f"  ✅ Spine spec count query works: {spec_count}")
            
            # Test manufacturer query
            cursor.execute('''
            SELECT manufacturer, COUNT(*) as arrow_count
            FROM arrows 
            GROUP BY manufacturer 
            ORDER BY arrow_count DESC
            LIMIT 3
            ''')
            
            manufacturers = cursor.fetchall()
            print(f"  ✅ Manufacturer query works: {len(manufacturers)} manufacturers")
            for mfg in manufacturers:
                print(f"    - {mfg['manufacturer']}: {mfg['arrow_count']} arrows")
            
        except Exception as e:
            print(f"  ❌ Statistics query error: {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    diagnose_database_schema()