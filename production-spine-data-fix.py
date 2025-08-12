#!/usr/bin/env python3
"""
Production Spine Data Fix Script
Manually imports spine calculator data to production database
"""

import os
import sys
import sqlite3
from pathlib import Path
import json

def main():
    print("🎯 Production Spine Data Fix Script")
    print("=" * 40)
    
    # Find the correct production database path
    possible_db_paths = [
        "/app/databases/arrow_database.db",  # Docker container path
        "/app/arrow_data/arrow_database.db",  # Alternative container path
        "./databases/arrow_database.db",     # Local relative path
        "./arrow_database.db",               # Project root
        "./arrow_scraper/databases/arrow_database.db"  # Legacy path
    ]
    
    production_db_path = None
    for db_path in possible_db_paths:
        if os.path.exists(db_path):
            production_db_path = db_path
            print(f"✅ Found production database at: {db_path}")
            break
    
    if not production_db_path:
        print("❌ Could not find production database file!")
        print("Checked paths:")
        for path in possible_db_paths:
            print(f"  - {path}")
        sys.exit(1)
    
    # Check if spine tables exist
    try:
        conn = sqlite3.connect(production_db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) FROM sqlite_master 
            WHERE type='table' AND name='manufacturer_spine_charts_enhanced'
        """)
        table_exists = cursor.fetchone()[0] > 0
        
        if table_exists:
            cursor.execute("SELECT COUNT(*) FROM manufacturer_spine_charts_enhanced")
            chart_count = cursor.fetchone()[0]
            print(f"ℹ️  Spine table exists with {chart_count} charts")
            
            if chart_count > 0:
                print("✅ Spine data already exists in production database!")
                print("The issue might be with API database path resolution.")
                conn.close()
                return
        else:
            print("⚠️  manufacturer_spine_charts_enhanced table does not exist")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        sys.exit(1)
    
    # Import spine calculator data
    print("\n🔧 Running spine calculator data import...")
    
    # Set environment variable for database path
    os.environ["ARROW_DATABASE_PATH"] = production_db_path
    
    # Change to arrow_scraper directory
    script_dir = Path(__file__).parent
    arrow_scraper_dir = script_dir / "arrow_scraper"
    
    if not arrow_scraper_dir.exists():
        print("❌ arrow_scraper directory not found!")
        sys.exit(1)
    
    os.chdir(arrow_scraper_dir)
    
    # Import the spine calculator data importer
    try:
        sys.path.insert(0, str(arrow_scraper_dir))
        from spine_calculator_data_importer import SpineCalculatorDataImporter
        
        importer = SpineCalculatorDataImporter(production_db_path)
        importer.run_import()
        
        print("✅ Spine calculator data import completed!")
        
        # Verify import
        conn = sqlite3.connect(production_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM manufacturer_spine_charts_enhanced")
        chart_count = cursor.fetchone()[0]
        print(f"📊 Verified: {chart_count} spine charts imported successfully")
        conn.close()
        
    except Exception as e:
        print(f"❌ Error during import: {e}")
        print("\n🔄 Trying alternative import method...")
        
        # Fallback: run the script directly
        import subprocess
        result = subprocess.run([
            sys.executable, "spine_calculator_data_importer.py"
        ], capture_output=True, text=True, env=os.environ.copy())
        
        if result.returncode == 0:
            print("✅ Alternative import method succeeded!")
            print(result.stdout)
        else:
            print("❌ Alternative import method failed!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            sys.exit(1)
    
    print("\n🎯 Production spine data fix completed!")
    print("You can now restart your production services.")

if __name__ == "__main__":
    main()