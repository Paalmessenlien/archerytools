#!/usr/bin/env python3
"""
Test Database Initialization Script
Tests the database initialization process for Docker deployment
"""

import os
import sys
import sqlite3
from pathlib import Path

def test_database_paths():
    """Test various database path configurations"""
    print("🧪 Testing Database Path Discovery...")
    
    # Test paths in order of preference
    test_paths = [
        "arrow_database.db",               # Current directory
        "../arrow_database.db",            # Parent directory
        "data/arrow_database.db",          # Local data directory  
        "/app/data/arrow_database.db",     # Docker data volume
        "/app/arrow_database.db",          # Docker app directory
    ]
    
    found_databases = []
    
    for db_path in test_paths:
        if os.path.exists(db_path):
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM arrows")
                count = cursor.fetchone()[0]
                conn.close()
                
                found_databases.append({
                    'path': db_path,
                    'count': count,
                    'valid': count > 0
                })
                
                status = "✅" if count > 0 else "⚠️ "
                print(f"  {status} {db_path}: {count} arrows")
                
            except Exception as e:
                print(f"  ❌ {db_path}: Error - {e}")
        else:
            print(f"  ✗ {db_path}: Not found")
    
    if found_databases:
        valid_dbs = [db for db in found_databases if db['valid']]
        if valid_dbs:
            best_db = valid_dbs[0]  # First valid database
            print(f"\n🎯 Best database: {best_db['path']} ({best_db['count']} arrows)")
            return best_db['path']
        else:
            print(f"\n⚠️  Found databases but none have data")
            return None
    else:
        print(f"\n❌ No databases found")
        return None

def test_processed_data():
    """Test for processed JSON data files"""
    print("\n📁 Testing Processed Data Discovery...")
    
    data_dirs = [
        "data/processed",
        "./data/processed", 
        "/app/data/processed"
    ]
    
    for data_dir in data_dirs:
        data_path = Path(data_dir)
        if data_path.exists():
            json_files = list(data_path.glob("*.json"))
            if json_files:
                print(f"  ✅ {data_dir}: {len(json_files)} JSON files")
                for json_file in json_files[:3]:  # Show first 3
                    print(f"    - {json_file.name}")
                if len(json_files) > 3:
                    print(f"    ... and {len(json_files) - 3} more")
                return str(data_path)
            else:
                print(f"  ⚠️  {data_dir}: Directory exists but no JSON files")
        else:
            print(f"  ✗ {data_dir}: Not found")
    
    print(f"  ❌ No processed data found")
    return None

def test_api_initialization():
    """Test API database initialization"""
    print("\n🌐 Testing API Database Initialization...")
    
    try:
        # Add current directory to Python path
        sys.path.insert(0, os.getcwd())
        
        # Import API functions
        from api import get_database, get_tuning_system
        
        # Test database initialization
        print("  Testing get_database()...")
        db = get_database()
        
        if db:
            print("  ✅ Database initialized successfully")
            
            # Test basic functionality
            try:
                stats = db.get_statistics()
                if stats:
                    print(f"    - Total arrows: {stats.get('total_arrows', 0)}")
                    print(f"    - Manufacturers: {len(stats.get('manufacturers', []))}")
                else:
                    print("  ⚠️  Database initialized but no statistics available")
            except Exception as e:
                print(f"  ⚠️  Database stats error: {e}")
            
            # Test tuning system
            print("  Testing get_tuning_system()...")
            ts = get_tuning_system()
            
            if ts:
                print("  ✅ Tuning system initialized successfully")
            else:
                print("  ❌ Tuning system initialization failed")
                
        else:
            print("  ❌ Database initialization failed")
            
    except Exception as e:
        print(f"  ❌ API initialization error: {e}")
        import traceback
        print(f"  Full error: {traceback.format_exc()}")

def test_init_database_script():
    """Test the init-database.py script"""
    print("\n🔧 Testing init-database.py Script...")
    
    try:
        from init_database import initialize_database, check_database_exists
        
        # Test check function
        current_db = "arrow_database.db"
        if os.path.exists(current_db):
            has_data = check_database_exists(current_db)
            print(f"  Database check: {current_db} -> {'✅ Has data' if has_data else '⚠️  Empty'}")
        
        # Test initialization
        print("  Running initialize_database()...")
        result = initialize_database()
        
        if result:
            print("  ✅ Database initialization successful")
        else:
            print("  ❌ Database initialization failed")
            
    except Exception as e:
        print(f"  ❌ Init script error: {e}")

def main():
    """Main test function"""
    print("🧪 ArrowTuner Database Initialization Test")
    print("=" * 50)
    
    # Test 1: Database path discovery
    best_db = test_database_paths()
    
    # Test 2: Processed data discovery
    processed_data = test_processed_data()
    
    # Test 3: API initialization
    test_api_initialization()
    
    # Test 4: Init script
    test_init_database_script()
    
    print("\n" + "=" * 50)
    print("🏁 Test Summary:")
    
    if best_db:
        print(f"✅ Database available: {best_db}")
    else:
        print("❌ No valid database found")
    
    if processed_data:
        print(f"✅ Processed data available: {processed_data}")
    else:
        print("❌ No processed data found")
    
    # Overall status
    if best_db or processed_data:
        print("\n🎉 System should work - database or data available for initialization")
    else:
        print("\n💥 System will fail - no database or processed data available")

if __name__ == "__main__":
    main()