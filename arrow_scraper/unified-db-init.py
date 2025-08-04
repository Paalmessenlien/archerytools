#!/usr/bin/env python3
"""
Unified Database Initialization Script
Ensures both arrow_database.db and user_data.db exist in the unified location
Handles migration from old locations to new unified structure
"""

import os
import shutil
import sqlite3
from pathlib import Path
import sys
import time

# Color codes for output
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color

def print_message(color, message):
    """Print colored message"""
    print(f"{color}{message}{NC}")

def ensure_directories():
    """Ensure all required directories exist"""
    print_message(BLUE, "📁 Ensuring directory structure...")
    
    directories = [
        Path("/app/databases"),
        Path("/app/logs"),
        Path("/app/backups"),
        Path("/app/data/processed")
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print_message(GREEN, f"  ✅ {directory}")

def find_existing_database(db_name, search_paths):
    """Find an existing database file in various locations"""
    for path in search_paths:
        db_path = Path(path)
        if db_path.exists() and db_path.stat().st_size > 0:
            # Verify it's a valid SQLite database
            try:
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1")
                cursor.fetchone()
                conn.close()
                return db_path
            except Exception:
                continue
    return None

def migrate_arrow_database():
    """Migrate arrow database to unified location"""
    print_message(BLUE, "🗄️  Checking arrow database...")
    
    target_path = Path("/app/databases/arrow_database.db")
    
    if target_path.exists():
        print_message(GREEN, "  ✅ Arrow database already exists in unified location")
        return
    
    # Search paths for existing arrow database
    search_paths = [
        "/app/arrow_data/arrow_database.db",
        "/app/arrow_database.db",
        "/app/arrow_database_backup.db",
        "arrow_database.db",
        "arrow_scraper/arrow_database.db"
    ]
    
    existing_db = find_existing_database("arrow_database.db", search_paths)
    
    if existing_db:
        print_message(YELLOW, f"  📋 Found existing database at: {existing_db}")
        print_message(BLUE, f"  🔄 Migrating to: {target_path}")
        shutil.copy2(existing_db, target_path)
        print_message(GREEN, "  ✅ Arrow database migrated successfully")
    else:
        print_message(YELLOW, "  ⚠️  No existing arrow database found")
        # Import from JSON files if available
        import_from_json()

def migrate_user_database():
    """Migrate user database to unified location"""
    print_message(BLUE, "🗄️  Checking user database...")
    
    target_path = Path("/app/databases/user_data.db")
    
    if target_path.exists():
        print_message(GREEN, "  ✅ User database already exists in unified location")
        return
    
    # Search paths for existing user database
    search_paths = [
        "/app/user_data/user_data.db",
        "/app/user_data.db",
        "user_data.db",
        "arrow_scraper/user_data.db"
    ]
    
    existing_db = find_existing_database("user_data.db", search_paths)
    
    if existing_db:
        print_message(YELLOW, f"  📋 Found existing database at: {existing_db}")
        print_message(BLUE, f"  🔄 Migrating to: {target_path}")
        shutil.copy2(existing_db, target_path)
        print_message(GREEN, "  ✅ User database migrated successfully")
    else:
        print_message(YELLOW, "  ⚠️  No existing user database found")
        # Create new user database
        create_user_database()

def import_from_json():
    """Import arrow data from JSON files"""
    print_message(BLUE, "  📥 Attempting to import from JSON files...")
    
    # Set environment variable for unified database path
    os.environ['ARROW_DATABASE_PATH'] = '/app/databases/arrow_database.db'
    
    try:
        # Import the database manager
        sys.path.append('/app')
        from database_import_manager import import_all_json_to_database
        
        data_dir = Path("/app/data/processed")
        if data_dir.exists() and any(data_dir.glob("*.json")):
            import_all_json_to_database(str(data_dir), force=True)
            print_message(GREEN, "  ✅ Successfully imported arrow data from JSON files")
        else:
            print_message(YELLOW, "  ⚠️  No JSON files found for import")
            create_arrow_database()
    except Exception as e:
        print_message(RED, f"  ❌ Failed to import from JSON: {e}")
        create_arrow_database()

def create_arrow_database():
    """Create a new arrow database with schema"""
    print_message(BLUE, "  🔨 Creating new arrow database...")
    
    # Set environment variable
    os.environ['ARROW_DATABASE_PATH'] = '/app/databases/arrow_database.db'
    
    try:
        from arrow_database import ArrowDatabase
        db = ArrowDatabase('/app/databases/arrow_database.db')
        db.close()
        print_message(GREEN, "  ✅ Arrow database created successfully")
    except Exception as e:
        print_message(RED, f"  ❌ Failed to create arrow database: {e}")
        # Create minimal database
        create_minimal_arrow_database()

def create_minimal_arrow_database():
    """Create a minimal arrow database if imports fail"""
    print_message(YELLOW, "  🔧 Creating minimal arrow database...")
    
    db_path = Path("/app/databases/arrow_database.db")
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Create minimal schema
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS arrows (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            manufacturer TEXT NOT NULL,
            model_name TEXT NOT NULL,
            material TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS spine_specs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            arrow_id INTEGER NOT NULL,
            spine REAL NOT NULL,
            gpi_weight REAL,
            outer_diameter REAL,
            inner_diameter REAL,
            FOREIGN KEY (arrow_id) REFERENCES arrows (id)
        )
    """)
    
    conn.commit()
    conn.close()
    print_message(GREEN, "  ✅ Minimal arrow database created")

def create_user_database():
    """Create a new user database"""
    print_message(BLUE, "  🔨 Creating new user database...")
    
    # Set environment variable
    os.environ['USER_DATABASE_PATH'] = '/app/databases/user_data.db'
    
    try:
        from user_database import UserDatabase
        db = UserDatabase('/app/databases/user_data.db')
        print_message(GREEN, "  ✅ User database created successfully")
    except Exception as e:
        print_message(RED, f"  ❌ Failed to create user database: {e}")

def verify_databases():
    """Verify both databases are accessible and valid"""
    print_message(BLUE, "🔍 Verifying databases...")
    
    databases = {
        "Arrow Database": "/app/databases/arrow_database.db",
        "User Database": "/app/databases/user_data.db"
    }
    
    all_valid = True
    
    for name, path in databases.items():
        db_path = Path(path)
        if not db_path.exists():
            print_message(RED, f"  ❌ {name} not found at {path}")
            all_valid = False
            continue
        
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Check for tables
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            table_count = cursor.fetchone()[0]
            
            if table_count > 0:
                print_message(GREEN, f"  ✅ {name}: Valid ({table_count} tables)")
            else:
                print_message(YELLOW, f"  ⚠️  {name}: Empty database")
            
            conn.close()
        except Exception as e:
            print_message(RED, f"  ❌ {name}: Invalid - {e}")
            all_valid = False
    
    return all_valid

def set_permissions():
    """Set appropriate permissions on database files"""
    print_message(BLUE, "🔐 Setting file permissions...")
    
    paths = [
        Path("/app/databases"),
        Path("/app/databases/arrow_database.db"),
        Path("/app/databases/user_data.db"),
        Path("/app/logs"),
        Path("/app/backups")
    ]
    
    for path in paths:
        if path.exists():
            try:
                if path.is_file():
                    os.chmod(path, 0o664)  # rw-rw-r--
                else:
                    os.chmod(path, 0o775)  # rwxrwxr-x
                print_message(GREEN, f"  ✅ {path}")
            except Exception as e:
                print_message(YELLOW, f"  ⚠️  {path}: {e}")

def main():
    """Main initialization process"""
    print_message(GREEN, "🏹 ArrowTuner Unified Database Initialization")
    print_message(GREEN, "=" * 50)
    
    # Wait a moment for volumes to be fully mounted
    time.sleep(2)
    
    # Ensure directory structure
    ensure_directories()
    
    # Migrate databases
    migrate_arrow_database()
    migrate_user_database()
    
    # Verify databases
    if verify_databases():
        print_message(GREEN, "\n✅ Database initialization completed successfully!")
    else:
        print_message(RED, "\n❌ Database initialization completed with errors")
        sys.exit(1)
    
    # Set permissions
    set_permissions()
    
    print_message(GREEN, "\n🚀 System ready for startup!")

if __name__ == "__main__":
    main()