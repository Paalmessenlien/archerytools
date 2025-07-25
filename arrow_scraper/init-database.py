#!/usr/bin/env python3
"""
Initialize Arrow Database for Docker Deployment
This script ensures the database is properly created with data
"""

import os
import sys
import sqlite3
from pathlib import Path

def check_database_exists(db_path):
    """Check if database exists and has data"""
    if not os.path.exists(db_path):
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM arrows")
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
    except:
        return False

def initialize_database():
    """Initialize database with arrow data"""
    print("🔧 Initializing Arrow Database...")
    
    # Ensure data directory exists
    data_dir = Path("/app/data")
    data_dir.mkdir(exist_ok=True)
    
    # Database paths to check (in order of preference)
    db_paths = [
        "/app/data/arrow_database.db",        # Target location
        "/app/arrow_database.db",             # Current directory 
        "arrow_database.db"                   # Relative path
    ]
    
    # Check if any database exists with data
    for db_path in db_paths:
        if check_database_exists(db_path):
            print(f"✅ Found existing database: {db_path}")
            
            # Copy to standard location if needed
            if db_path != "/app/data/arrow_database.db":
                import shutil
                try:
                    shutil.copy2(db_path, "/app/data/arrow_database.db")
                    print(f"📋 Copied database to /app/data/arrow_database.db")
                except Exception as e:
                    print(f"⚠️  Could not copy database: {e}")
                    # Still return True if we found a working database
            
            return True
    
    # No existing database found, create new one
    print("📦 Creating new database from processed data...")
    
    try:
        # Change to app directory
        os.chdir("/app")
        
        # Check if processed data exists
        processed_dir = Path("/app/data/processed")
        if not processed_dir.exists() or not any(processed_dir.glob("*.json")):
            # Try alternative locations
            alt_processed_dirs = [
                Path("data/processed"),
                Path("./data/processed")
            ]
            
            processed_dir = None
            for alt_dir in alt_processed_dirs:
                if alt_dir.exists() and any(alt_dir.glob("*.json")):
                    processed_dir = alt_dir
                    print(f"📁 Found processed data in: {processed_dir}")
                    break
            
            if not processed_dir:
                print("❌ No processed data found in any location")
                return False
        
        # Import and run database creation
        from arrow_database import ArrowDatabase
        
        # Create database in data directory
        print("🏗️  Creating database from processed JSON files...")
        db = ArrowDatabase("/app/data/arrow_database.db")
        
        # Check if data was loaded
        conn = sqlite3.connect("/app/data/arrow_database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM arrows")
        count = cursor.fetchone()[0]
        conn.close()
        
        if count > 0:
            print(f"✅ Database created successfully with {count} arrows")
            
            # Also try to copy any existing data files to /app/data for consistency
            try:
                if Path("data").exists():
                    import shutil
                    shutil.copytree("data", "/app/data", dirs_exist_ok=True)
                    print("📋 Copied data directory to /app/data")
            except Exception as e:
                print(f"⚠️  Could not copy data directory: {e}")
            
            return True
        else:
            print("⚠️  Database created but no arrow data found")
            print("💡 This might be due to missing processed JSON files")
            return False
            
    except Exception as e:
        print(f"❌ Failed to create database: {e}")
        import traceback
        print(f"🔍 Full error: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    if initialize_database():
        print("🚀 Database initialization complete!")
        sys.exit(0)
    else:
        print("💥 Database initialization failed!")
        sys.exit(1)