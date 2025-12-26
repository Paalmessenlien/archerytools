#!/usr/bin/env python3
"""
Production Database Diagnostic Script
Helps identify which database path the production API is actually using
"""

import os
import sqlite3
from pathlib import Path

def check_database_path(db_path):
    """Check a database path and return information about it"""
    if not os.path.exists(db_path):
        return {"exists": False, "error": "File does not exist"}
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get basic info
        cursor.execute("SELECT COUNT(*) FROM arrows")
        arrow_count = cursor.fetchone()[0]
        
        # Check for spine tables
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name LIKE '%spine%'
            ORDER BY name
        """)
        spine_tables = [row[0] for row in cursor.fetchall()]
        
        # Check manufacturer_spine_charts_enhanced specifically
        has_enhanced_table = 'manufacturer_spine_charts_enhanced' in spine_tables
        enhanced_count = 0
        
        if has_enhanced_table:
            cursor.execute("SELECT COUNT(*) FROM manufacturer_spine_charts_enhanced")
            enhanced_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "exists": True,
            "arrow_count": arrow_count,
            "spine_tables": spine_tables,
            "has_enhanced_spine_table": has_enhanced_table,
            "enhanced_spine_count": enhanced_count,
            "file_size": os.path.getsize(db_path),
            "modified_time": os.path.getmtime(db_path)
        }
        
    except Exception as e:
        return {"exists": True, "error": str(e)}

def main():
    print("🔍 Production Database Diagnostic")
    print("=" * 40)
    
    # Check all possible database paths
    possible_paths = [
        "/app/databases/arrow_database.db",
        "/app/arrow_data/arrow_database.db", 
        "/app/arrow_database.db",
        "./databases/arrow_database.db",
        "./arrow_scraper/databases/arrow_database.db",
        "./arrow_database.db",
        "/var/lib/docker/volumes/arrowtuner-arrowdata/_data/arrow_database.db"
    ]
    
    print("Checking possible database paths:")
    print()
    
    for db_path in possible_paths:
        print(f"📍 {db_path}")
        info = check_database_path(db_path)
        
        if not info["exists"]:
            print(f"   ❌ {info['error']}")
        elif "error" in info:
            print(f"   ⚠️  Error: {info['error']}")
        else:
            print(f"   ✅ Exists")
            print(f"   📊 Arrows: {info['arrow_count']}")
            print(f"   📏 Size: {info['file_size']:,} bytes")
            print(f"   🏷️  Spine tables: {len(info['spine_tables'])}")
            
            if info['spine_tables']:
                print(f"      Tables: {', '.join(info['spine_tables'])}")
            
            if info['has_enhanced_spine_table']:
                print(f"   ✅ Enhanced spine table: {info['enhanced_spine_count']} charts")
            else:
                print(f"   ❌ Missing enhanced spine table")
        
        print()
    
    print("🔧 Environment Variables:")
    relevant_env_vars = [
        "ARROW_DATABASE_PATH",
        "DATABASE_PATH", 
        "DB_PATH",
        "FLASK_ENV",
        "NODE_ENV"
    ]
    
    for env_var in relevant_env_vars:
        value = os.environ.get(env_var)
        if value:
            print(f"   {env_var}={value}")
        else:
            print(f"   {env_var}=<not set>")
    
    print()
    print("💡 Recommendations:")
    print("1. The database with the most arrows is likely your main production database")
    print("2. Look for the database that is missing the enhanced spine table")
    print("3. Run the production-spine-data-fix.py script on the correct database")

if __name__ == "__main__":
    main()