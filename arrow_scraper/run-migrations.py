#!/usr/bin/env python3
"""
Run all database migrations in the correct order.
This script should be run before starting the API to ensure the database schema is up to date.
"""

import os
import sys
import subprocess

def run_migration(script_name):
    """Run a single migration script"""
    print(f"🔄 Running migration: {script_name}")
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, 
                              text=True, 
                              check=True)
        print(result.stdout)
        if result.stderr:
            print(f"⚠️  Warnings: {result.stderr}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Migration failed: {script_name}")
        print(f"Error: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"⚠️  Migration script not found: {script_name} - skipping")
        return True

def main():
    """Run all migrations in order"""
    print("🚀 Starting database migrations...")
    
    # List of migrations to run in order
    migrations = [
        "migrate_remove_arrow_fields.py",
        "migrate_add_bow_info_fields.py", 
        "migrate_add_compound_model.py"
    ]
    
    # Run each migration
    for migration in migrations:
        if os.path.exists(migration):
            if not run_migration(migration):
                print("❌ Migration process failed!")
                sys.exit(1)
        else:
            print(f"⚠️  Migration {migration} not found, skipping...")
    
    print("✅ All migrations completed successfully!")

if __name__ == "__main__":
    main()