#!/usr/bin/env python3
"""
Migration Runner for ArrowTuner
Runs database migrations with environment detection and Docker support
"""

import os
import sys
import argparse
from pathlib import Path
from database_migration_manager import DatabaseMigrationManager, MigrationError

def detect_environment():
    """Detect if running in Docker or host environment"""
    if os.path.exists("/.dockerenv"):
        return "docker"
    elif os.environ.get("FLASK_ENV") == "production" or os.environ.get("NODE_ENV") == "production":
        return "production"
    else:
        return "development"

def find_database_path():
    """Find the correct database path based on environment"""
    # Check environment variables first
    env_db_path = os.environ.get('ARROW_DATABASE_PATH')
    if env_db_path and os.path.exists(env_db_path):
        return env_db_path
    
    # Check common Docker paths
    docker_paths = [
        "/app/databases/arrow_database.db",
        "/app/arrow_database.db",
        "/app/arrow_data/arrow_database.db"
    ]
    
    for path in docker_paths:
        if os.path.exists(path):
            return path
    
    # Check host paths
    host_paths = [
        "databases/arrow_database.db",
        "../databases/arrow_database.db",
        "arrow_database.db"
    ]
    
    for path in host_paths:
        if os.path.exists(path):
            return os.path.abspath(path)
    
    # Default to first Docker path for creation
    return docker_paths[0]

def run_migrations_safe(database_path=None, migrations_dir="migrations", dry_run=False, target_version=None):
    """Run migrations with comprehensive error handling"""
    try:
        # Determine database path
        if not database_path:
            database_path = find_database_path()
        
        environment = detect_environment()
        
        print(f"🗄️ Database Migration Runner")
        print(f"Environment: {environment}")
        print(f"Database: {database_path}")
        print(f"Migrations: {migrations_dir}")
        
        # Ensure database directory exists
        db_dir = os.path.dirname(database_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            print(f"📁 Created database directory: {db_dir}")
        
        # Initialize migration manager
        manager = DatabaseMigrationManager(database_path, migrations_dir)
        
        # Get migration status
        status = manager.get_migration_status()
        print(f"📊 Migration Status:")
        print(f"   Applied: {status['applied_count']}")
        print(f"   Pending: {status['pending_count']}")
        
        if status['pending_count'] == 0:
            print("✅ All migrations are up to date")
            return True
        
        # Run pending migrations
        print(f"\n🔄 Running {status['pending_count']} pending migrations...")
        success = manager.migrate(target_version, dry_run)
        
        if success:
            print("✅ All migrations completed successfully")
            return True
        else:
            print("❌ Some migrations failed")
            return False
            
    except MigrationError as e:
        print(f"❌ Migration error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """CLI interface for migration runner"""
    parser = argparse.ArgumentParser(description="ArrowTuner Database Migration Runner")
    parser.add_argument("--database", help="Database file path (auto-detected if not specified)")
    parser.add_argument("--migrations-dir", default="migrations", help="Migrations directory")
    parser.add_argument("--dry-run", action="store_true", help="Preview migrations without applying")
    parser.add_argument("--target", help="Target migration version")
    parser.add_argument("--status-only", action="store_true", help="Show status only, don't run migrations")
    
    args = parser.parse_args()
    
    if args.status_only:
        # Show status only
        try:
            database_path = args.database or find_database_path()
            manager = DatabaseMigrationManager(database_path, args.migrations_dir)
            status = manager.get_migration_status()
            
            print(f"\n🗄️ Database Migration Status")
            print("=" * 30)
            print(f"Database: {status['database_path']}")
            print(f"Environment: {status['environment']}")
            print(f"Total migrations: {status['total_migrations']}")
            print(f"Applied: {status['applied_count']}")
            print(f"Pending: {status['pending_count']}")
            
            if status['applied_versions']:
                print(f"\n✅ Applied migrations:")
                for version in status['applied_versions']:
                    print(f"  - {version}")
            
            if status['pending_versions']:
                print(f"\n⏳ Pending migrations:")
                for version in status['pending_versions']:
                    print(f"  - {version}")
            
            return
            
        except Exception as e:
            print(f"❌ Error getting migration status: {e}")
            sys.exit(1)
    
    # Run migrations
    success = run_migrations_safe(
        database_path=args.database,
        migrations_dir=args.migrations_dir,
        dry_run=args.dry_run,
        target_version=args.target
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()