#!/usr/bin/env python3
"""
Test Migration System
Quick test script to verify migration system works on production server
"""

import os
import sys
from pathlib import Path

def main():
    print("🔧 Testing Migration System")
    print("=" * 30)
    
    # Check if we're in the right directory
    if not os.path.exists("arrow_scraper"):
        print("❌ Error: Run this script from the project root directory")
        print("   Expected: /root/archerytools/")
        print(f"   Current:  {os.getcwd()}")
        return False
    
    # Change to arrow_scraper directory
    os.chdir("arrow_scraper")
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Check if migration files exist
    required_files = [
        "database_migration_manager.py",
        "run_migrations.py",
        "migrations/001_spine_calculator_tables.py",
        "migrations/002_user_database_schema.py",
        "migrations/003_json_data_import.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"✅ Found: {file_path}")
    
    if missing_files:
        print(f"\n❌ Missing files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    
    # Test import of migration manager
    try:
        sys.path.insert(0, os.getcwd())
        from database_migration_manager import DatabaseMigrationManager
        print("✅ Successfully imported DatabaseMigrationManager")
    except Exception as e:
        print(f"❌ Failed to import DatabaseMigrationManager: {e}")
        return False
    
    # Test migration manager initialization
    try:
        manager = DatabaseMigrationManager()
        print(f"✅ Migration manager initialized")
        print(f"   Database: {manager.database_path}")
        print(f"   Environment: {manager.environment}")
        print(f"   Migrations dir: {manager.migrations_dir}")
    except Exception as e:
        print(f"❌ Failed to initialize migration manager: {e}")
        return False
    
    # Test migration discovery
    try:
        migrations = manager.discover_migrations()
        print(f"✅ Discovered {len(migrations)} migrations:")
        for version, migration in migrations.items():
            print(f"   - {version}: {migration.description}")
    except Exception as e:
        print(f"❌ Failed to discover migrations: {e}")
        return False
    
    # Test migration status
    try:
        status = manager.get_migration_status()
        print(f"✅ Migration status retrieved:")
        print(f"   Total: {status['total_migrations']}")
        print(f"   Applied: {status['applied_count']}")
        print(f"   Pending: {status['pending_count']}")
        
        if status['pending_versions']:
            print(f"   Pending versions: {', '.join(status['pending_versions'])}")
    except Exception as e:
        print(f"❌ Failed to get migration status: {e}")
        return False
    
    print("\n✅ Migration system test completed successfully!")
    print("\n🚀 Ready to run migrations:")
    print("   python3 run_migrations.py --status-only  # Show status")
    print("   python3 run_migrations.py --dry-run      # Preview migrations")
    print("   python3 run_migrations.py                # Run migrations")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)