#!/usr/bin/env python3
"""
User Database Migration Runner
Runs migrations specifically for the user database (user_data.db)
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add current directory to path for importing
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database_migration_manager import DatabaseMigrationManager, MigrationError
from user_database import UserDatabase

def get_user_database_path():
    """Get the user database path with environment awareness"""
    # Check for environment variable first (Docker deployment)
    env_db_path = os.environ.get('USER_DATABASE_PATH')
    if env_db_path:
        return env_db_path
    
    # Try Docker container paths
    docker_paths = [
        "/app/databases/user_data.db",
        "/app/user_data.db",
        "/app/databases/user_database.db"
    ]
    
    for docker_path in docker_paths:
        if os.path.exists(docker_path) or os.path.exists(os.path.dirname(docker_path)):
            return docker_path
    
    # Try local development paths
    local_paths = [
        "databases/user_data.db",
        "user_data.db",
        "../databases/user_data.db"
    ]
    
    for local_path in local_paths:
        if os.path.exists(local_path):
            return local_path
    
    # Default to user_data.db in current directory
    return "user_data.db"

def main():
    """Main function for user database migration runner"""
    parser = argparse.ArgumentParser(description='Run migrations for user database')
    parser.add_argument('--status-only', action='store_true', 
                       help='Only check migration status, do not run migrations')
    parser.add_argument('--database', type=str, 
                       help='Path to user database file')
    parser.add_argument('--migrations-dir', type=str, default='migrations',
                       help='Directory containing migration files')
    parser.add_argument('--target-migrations', nargs='+', 
                       help='Specific migrations to run (e.g., 019 020)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without actually running migrations')
    
    args = parser.parse_args()
    
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    # Get database path
    database_path = args.database or get_user_database_path()
    
    logger.info(f"🔧 User Database Migration Runner")
    logger.info(f"📁 Database: {database_path}")
    logger.info(f"📂 Migrations: {args.migrations_dir}")
    
    # Ensure user database exists and is initialized
    try:
        user_db = UserDatabase(database_path)
        logger.info(f"✅ User database initialized: {database_path}")
    except Exception as e:
        logger.error(f"❌ Failed to initialize user database: {e}")
        return 1
    
    try:
        # Create migration manager for user database
        manager = DatabaseMigrationManager(database_path, args.migrations_dir)
        
        if args.status_only:
            # Only check status
            status = manager.get_migration_status()
            
            if not status:
                logger.info("📋 No migrations found")
                return 0
            
            logger.info("📋 Migration Status:")
            for version, info in status.items():
                status_symbol = "✅" if info['applied'] else "⏳"
                logger.info(f"  {status_symbol} {version}: {info['description']}")
            
            # Check if there are pending migrations
            pending = [v for v, i in status.items() if not i['applied']]
            if pending:
                logger.info(f"⏳ {len(pending)} pending migrations: {', '.join(pending)}")
                return 1  # Exit with 1 to indicate pending migrations
            else:
                logger.info("✅ All migrations are up to date")
                return 0
        
        elif args.target_migrations:
            # Run specific migrations
            logger.info(f"🎯 Running target migrations: {', '.join(args.target_migrations)}")
            
            if args.dry_run:
                logger.info("🔍 DRY RUN MODE - No changes will be made")
                
            success = True
            for migration_version in args.target_migrations:
                # Pad version to 3 digits
                padded_version = str(migration_version).zfill(3)
                
                if args.dry_run:
                    logger.info(f"🔍 Would run migration {padded_version}")
                    continue
                
                try:
                    result = manager.run_specific_migration(padded_version)
                    if result:
                        logger.info(f"✅ Migration {padded_version} completed successfully")
                    else:
                        logger.error(f"❌ Migration {padded_version} failed")
                        success = False
                except Exception as e:
                    logger.error(f"❌ Migration {padded_version} failed: {e}")
                    success = False
            
            if args.dry_run:
                logger.info("🔍 DRY RUN COMPLETE - No changes were made")
                return 0
            
            return 0 if success else 1
        
        else:
            # Run all pending migrations
            logger.info("🚀 Running all pending user database migrations...")
            
            if args.dry_run:
                logger.info("🔍 DRY RUN MODE - No changes will be made")
                status = manager.get_migration_status()
                pending = [v for v, i in status.items() if not i['applied']]
                
                if pending:
                    logger.info(f"🔍 Would run {len(pending)} migrations: {', '.join(pending)}")
                else:
                    logger.info("🔍 No pending migrations to run")
                return 0
            
            success = manager.run_pending_migrations()
            
            if success:
                logger.info("✅ All user database migrations completed successfully")
                return 0
            else:
                logger.error("❌ Some user database migrations failed")
                return 1
    
    except MigrationError as e:
        logger.error(f"❌ Migration error: {e}")
        return 1
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)