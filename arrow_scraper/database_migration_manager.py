#!/usr/bin/env python3
"""
Database Migration Manager for ArrowTuner
Provides robust, versioned database migration system with environment awareness
"""

import os
import sqlite3
import json
import logging
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from abc import ABC, abstractmethod
import importlib.util
import sys

class MigrationError(Exception):
    """Exception raised for migration-related errors"""
    pass

class BaseMigration(ABC):
    """Base class for all database migrations"""
    
    def __init__(self):
        self.version = None
        self.description = None
        self.dependencies = []  # List of migration versions this depends on
        self.environments = ['all']  # ['all', 'development', 'production', 'docker']
        
    @abstractmethod
    def up(self, db_path: str, environment: str) -> bool:
        """Apply the migration"""
        pass
    
    @abstractmethod
    def down(self, db_path: str, environment: str) -> bool:
        """Rollback the migration"""
        pass
    
    def can_run_in_environment(self, environment: str) -> bool:
        """Check if migration can run in the given environment"""
        return 'all' in self.environments or environment in self.environments
    
    def get_checksum(self) -> str:
        """Generate checksum for migration integrity verification"""
        migration_content = f"{self.version}:{self.description}:{str(self.dependencies)}"
        return hashlib.md5(migration_content.encode()).hexdigest()

class DatabaseMigrationManager:
    """Manages database migrations with versioning and environment awareness"""
    
    def __init__(self, database_path: str = "arrow_database.db", migrations_dir: str = "migrations"):
        """
        Initialize the migration manager
        
        Args:
            database_path: Path to the SQLite database
            migrations_dir: Directory containing migration files
        """
        # Set up logging first
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        
        # Now initialize other attributes
        self.database_path = self._resolve_database_path(database_path)
        self.migrations_dir = Path(migrations_dir)
        self.environment = self._detect_environment()
        
        # Ensure migrations table exists
        self._ensure_migrations_table()
    
    def _resolve_database_path(self, db_path: str) -> str:
        """Resolve database path with environment awareness"""
        # Check for environment variable first (Docker deployment)
        env_db_path = os.environ.get('ARROW_DATABASE_PATH')
        if env_db_path:
            self.logger.info(f"🔧 Using ARROW_DATABASE_PATH: {env_db_path}")
            return env_db_path
        
        # Try Docker container paths
        docker_paths = [
            "/app/databases/arrow_database.db",
            "/app/arrow_database.db",
            "/app/arrow_data/arrow_database.db"
        ]
        
        for docker_path in docker_paths:
            if os.path.exists(docker_path) or os.path.exists(os.path.dirname(docker_path)):
                self.logger.info(f"🐳 Using Docker database path: {docker_path}")
                return docker_path
        
        # Fall back to provided path
        if Path(db_path).is_absolute():
            return db_path
        
        # Try relative paths
        possible_paths = [
            f"databases/{db_path}",
            f"../databases/{db_path}",
            db_path
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                resolved_path = os.path.abspath(path)
                self.logger.info(f"🔧 Resolved database path: {resolved_path}")
                return resolved_path
        
        # Default to first possible path for creation
        default_path = os.path.abspath(possible_paths[0])
        self.logger.info(f"📁 Using default database path: {default_path}")
        os.makedirs(os.path.dirname(default_path), exist_ok=True)
        return default_path
    
    def _detect_environment(self) -> str:
        """Detect the current environment"""
        if os.path.exists("/.dockerenv"):
            return "docker"
        elif os.environ.get("FLASK_ENV") == "production" or os.environ.get("NODE_ENV") == "production":
            return "production"
        else:
            return "development"
    
    def _ensure_migrations_table(self):
        """Ensure the migrations tracking table exists"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS database_migrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    checksum TEXT NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    applied_by TEXT DEFAULT 'migration_manager',
                    environment TEXT NOT NULL,
                    success BOOLEAN DEFAULT 1,
                    error_message TEXT,
                    rollback_info TEXT
                )
            """)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create migrations table: {e}")
            raise MigrationError(f"Cannot create migrations table: {e}")
    
    def discover_migrations(self) -> Dict[str, BaseMigration]:
        """Discover all migration files in the migrations directory"""
        migrations = {}
        
        if not self.migrations_dir.exists():
            self.logger.warning(f"Migrations directory does not exist: {self.migrations_dir}")
            return migrations
        
        # Look for Python migration files
        for migration_file in self.migrations_dir.glob("*.py"):
            if migration_file.name.startswith("__"):
                continue
                
            try:
                # Load migration module
                spec = importlib.util.spec_from_file_location(migration_file.stem, migration_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                migration_found = False
                
                # Method 1: Look for BaseMigration subclass (class-based migrations 001-011)
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, BaseMigration) and 
                        attr != BaseMigration):
                        
                        migration = attr()
                        if migration.version:
                            migrations[migration.version] = migration
                            migration_found = True
                            break
                
                # Method 2: Look for plain Migration class (standalone migrations 012+)
                if not migration_found and hasattr(module, 'Migration'):
                    migration_class = getattr(module, 'Migration')
                    if isinstance(migration_class, type):
                        migration_instance = migration_class()
                        if hasattr(migration_instance, 'version') and migration_instance.version:
                            # Create wrapper to make it compatible with BaseMigration interface
                            wrapper = self._create_migration_wrapper(migration_instance, module, migration_file)
                            migrations[str(migration_instance.version).zfill(3)] = wrapper
                            migration_found = True
                
                # Method 3: Look for standalone up/down functions (function-based migrations)
                if not migration_found and hasattr(module, 'up') and hasattr(module, 'down'):
                    # Extract version from filename (e.g., "013_equipment_change_logging.py" -> "013")
                    version_match = migration_file.stem.split('_')[0]
                    if version_match.isdigit():
                        # Create wrapper to make it compatible with BaseMigration interface
                        wrapper = self._create_function_wrapper(module, migration_file, version_match)
                        migrations[version_match] = wrapper
                        migration_found = True
                
                # Method 4: Look for run_migration function (legacy function-based migrations)
                if not migration_found and hasattr(module, 'run_migration'):
                    # Extract version from filename (e.g., "013_equipment_change_logging.py" -> "013")
                    version_match = migration_file.stem.split('_')[0]
                    if version_match.isdigit():
                        # Create wrapper to make it compatible with BaseMigration interface
                        wrapper = self._create_run_migration_wrapper(module, migration_file, version_match)
                        migrations[version_match] = wrapper
                        migration_found = True
                
                if not migration_found:
                    self.logger.warning(f"⚠️  No migration class or functions found in {migration_file}")
                            
            except Exception as e:
                self.logger.error(f"❌ Failed to load migration {migration_file}: {e}")
        
        return migrations
    
    def _create_migration_wrapper(self, migration_instance, module, migration_file):
        """Create a BaseMigration wrapper for plain Migration class instances"""
        class MigrationWrapper(BaseMigration):
            def __init__(self, wrapped_migration):
                super().__init__()
                self.wrapped = wrapped_migration
                self.version = str(wrapped_migration.version).zfill(3)
                self.description = getattr(wrapped_migration, 'description', f'Migration {self.version}')
                self.dependencies = getattr(wrapped_migration, 'dependencies', [])
                self.environments = getattr(wrapped_migration, 'environments', ['all'])
            
            def up(self, db_path: str, environment: str = None) -> bool:
                if hasattr(self.wrapped, 'up'):
                    try:
                        # Try to call with db_path parameter first
                        import inspect
                        up_signature = inspect.signature(self.wrapped.up)
                        if len(up_signature.parameters) > 0:
                            # Method accepts parameters, pass db_path
                            result = self.wrapped.up(db_path)
                        else:
                            # Method takes no parameters, call without arguments
                            result = self.wrapped.up()
                        return result if result is not None else True
                    except Exception as e:
                        self.logger.error(f"Migration {self.version} up() failed: {e}")
                        return False
                return True
            
            def down(self, db_path: str, environment: str = None) -> bool:
                if hasattr(self.wrapped, 'down'):
                    try:
                        # Try to call with db_path parameter first
                        import inspect
                        down_signature = inspect.signature(self.wrapped.down)
                        if len(down_signature.parameters) > 0:
                            # Method accepts parameters, pass db_path
                            result = self.wrapped.down(db_path)
                        else:
                            # Method takes no parameters, call without arguments
                            result = self.wrapped.down()
                        return result if result is not None else True
                    except Exception as e:
                        self.logger.error(f"Migration {self.version} down() failed: {e}")
                        return False
                return True
        
        return MigrationWrapper(migration_instance)
    
    def _create_function_wrapper(self, module, migration_file, version):
        """Create a BaseMigration wrapper for function-based migrations"""
        class FunctionWrapper(BaseMigration):
            def __init__(self, module, version, file_path):
                super().__init__()
                self.module = module
                self.version = str(version).zfill(3)
                self.description = getattr(module, '__doc__', f'Migration {self.version}').strip() if hasattr(module, '__doc__') and module.__doc__ else f'Migration {self.version}'
                # Extract description from docstring if available
                if hasattr(module, '__doc__') and module.__doc__:
                    lines = [line.strip() for line in module.__doc__.strip().split('\n') if line.strip()]
                    if len(lines) > 1:
                        self.description = lines[1]  # Second line usually contains the description
                    elif len(lines) == 1:
                        self.description = lines[0]
                self.dependencies = []
                self.environments = ['all']
                self.file_path = file_path
            
            def up(self, db_path: str, environment: str = None) -> bool:
                if hasattr(self.module, 'up'):
                    try:
                        result = self.module.up(db_path)
                        return result if result is not None else True
                    except Exception as e:
                        self.logger.error(f"Migration {self.version} up() failed: {e}")
                        return False
                return True
            
            def down(self, db_path: str, environment: str = None) -> bool:
                if hasattr(self.module, 'down'):
                    try:
                        result = self.module.down(db_path)
                        return result if result is not None else True
                    except Exception as e:
                        self.logger.error(f"Migration {self.version} down() failed: {e}")
                        return False
                return True
        
        return FunctionWrapper(module, version, migration_file)
    
    def _create_run_migration_wrapper(self, module, migration_file, version):
        """Create a BaseMigration wrapper for run_migration() function-based migrations"""
        class RunMigrationWrapper(BaseMigration):
            def __init__(self, module, version, file_path):
                super().__init__()
                self.module = module
                self.version = str(version).zfill(3)
                self.description = getattr(module, '__doc__', f'Migration {self.version}').strip() if hasattr(module, '__doc__') and module.__doc__ else f'Migration {self.version}'
                # Extract description from docstring if available
                if hasattr(module, '__doc__') and module.__doc__:
                    lines = [line.strip() for line in module.__doc__.strip().split('\n') if line.strip()]
                    # Look for the description line (usually starts with "Migration XXX:")
                    for line in lines:
                        if line.startswith(f'Migration {version}:'):
                            self.description = line.split(':', 1)[1].strip() if ':' in line else line
                            break
                    else:
                        # Fallback to second line
                        if len(lines) > 1:
                            self.description = lines[1]
                        elif len(lines) == 1:
                            self.description = lines[0]
                self.dependencies = []
                self.environments = ['all']
                self.file_path = file_path
            
            def up(self, db_path: str, environment: str = None) -> bool:
                if hasattr(self.module, 'run_migration'):
                    try:
                        # run_migration() functions typically don't return a value
                        self.module.run_migration()
                        return True
                    except Exception as e:
                        self.logger.error(f"Migration {self.version} run_migration() failed: {e}")
                        return False
                return True
            
            def down(self, db_path: str, environment: str = None) -> bool:
                # run_migration() style migrations typically don't support rollback
                self.logger.warning(f"Migration {self.version} does not support rollback (run_migration style)")
                return True
        
        return RunMigrationWrapper(module, version, migration_file)
    
    def get_applied_migrations(self) -> List[str]:
        """Get list of already applied migration versions"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT version FROM database_migrations 
                WHERE success = 1 
                ORDER BY applied_at
            """)
            
            versions = [row[0] for row in cursor.fetchall()]
            conn.close()
            return versions
            
        except sqlite3.OperationalError:
            # Migrations table doesn't exist yet
            return []
        except Exception as e:
            self.logger.error(f"❌ Failed to get applied migrations: {e}")
            return []
    
    def get_pending_migrations(self) -> List[BaseMigration]:
        """Get list of pending migrations in dependency order"""
        all_migrations = self.discover_migrations()
        applied_versions = set(self.get_applied_migrations())
        
        # Filter out already applied migrations and check environment compatibility
        pending = []
        for version, migration in all_migrations.items():
            if version not in applied_versions and migration.can_run_in_environment(self.environment):
                pending.append(migration)
        
        # Sort by dependencies and version
        return self._sort_migrations_by_dependencies(pending)
    
    def _sort_migrations_by_dependencies(self, migrations: List[BaseMigration]) -> List[BaseMigration]:
        """Sort migrations by their dependencies"""
        sorted_migrations = []
        remaining = migrations.copy()
        applied_versions = set(self.get_applied_migrations())
        
        while remaining:
            progress_made = False
            
            for migration in remaining[:]:
                # Check if all dependencies are satisfied
                deps_satisfied = all(
                    dep in applied_versions or 
                    any(m.version == dep for m in sorted_migrations)
                    for dep in migration.dependencies
                )
                
                if deps_satisfied:
                    sorted_migrations.append(migration)
                    remaining.remove(migration)
                    progress_made = True
            
            if not progress_made and remaining:
                # Circular dependency or missing dependency
                missing_deps = []
                for migration in remaining:
                    for dep in migration.dependencies:
                        if dep not in applied_versions and not any(m.version == dep for m in sorted_migrations):
                            missing_deps.append(f"{migration.version} -> {dep}")
                
                raise MigrationError(f"Circular dependency or missing migrations: {missing_deps}")
        
        return sorted_migrations
    
    def apply_migration(self, migration: BaseMigration, dry_run: bool = False) -> bool:
        """Apply a single migration"""
        self.logger.info(f"🔄 {'[DRY RUN] ' if dry_run else ''}Applying migration {migration.version}: {migration.description}")
        
        if dry_run:
            self.logger.info(f"✅ [DRY RUN] Would apply migration {migration.version}")
            return True
        
        try:
            # Check if already applied
            if migration.version in self.get_applied_migrations():
                self.logger.info(f"⏭️  Migration {migration.version} already applied")
                return True
            
            # Apply the migration
            success = migration.up(self.database_path, self.environment)
            
            if success:
                # Record successful application
                self._record_migration(migration, success=True)
                self.logger.info(f"✅ Successfully applied migration {migration.version}")
                return True
            else:
                # Record failed application
                self._record_migration(migration, success=False, error="Migration returned False")
                self.logger.error(f"❌ Migration {migration.version} returned False")
                return False
                
        except Exception as e:
            # Record failed application
            self._record_migration(migration, success=False, error=str(e))
            self.logger.error(f"❌ Failed to apply migration {migration.version}: {e}")
            return False
    
    def rollback_migration(self, migration: BaseMigration, dry_run: bool = False) -> bool:
        """Rollback a single migration"""
        self.logger.info(f"🔙 {'[DRY RUN] ' if dry_run else ''}Rolling back migration {migration.version}: {migration.description}")
        
        if dry_run:
            self.logger.info(f"✅ [DRY RUN] Would rollback migration {migration.version}")
            return True
        
        try:
            # Apply the rollback
            success = migration.down(self.database_path, self.environment)
            
            if success:
                # Remove from migrations table
                self._remove_migration_record(migration.version)
                self.logger.info(f"✅ Successfully rolled back migration {migration.version}")
                return True
            else:
                self.logger.error(f"❌ Migration {migration.version} rollback returned False")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Failed to rollback migration {migration.version}: {e}")
            return False
    
    def migrate(self, target_version: Optional[str] = None, dry_run: bool = False) -> bool:
        """Run all pending migrations up to target version"""
        pending = self.get_pending_migrations()
        
        if target_version:
            # Filter to only migrations up to target version
            pending = [m for m in pending if m.version <= target_version]
        
        if not pending:
            self.logger.info("✅ No pending migrations")
            return True
        
        self.logger.info(f"📊 Found {len(pending)} pending migrations")
        
        # Create backup before migrating
        if not dry_run:
            backup_path = self._create_backup()
            self.logger.info(f"💾 Created backup: {backup_path}")
        
        success_count = 0
        for migration in pending:
            if self.apply_migration(migration, dry_run):
                success_count += 1
            else:
                self.logger.error(f"❌ Migration failed, stopping at {migration.version}")
                if not dry_run:
                    self.logger.info(f"💾 Restore from backup if needed: {backup_path}")
                return False
        
        self.logger.info(f"✅ Successfully applied {success_count} migrations")
        return True
    
    def get_migration_status(self) -> Dict[str, Any]:
        """Get comprehensive migration status"""
        all_migrations = self.discover_migrations()
        applied_migrations = self.get_applied_migrations()
        pending_migrations = self.get_pending_migrations()
        
        # Get detailed migration info
        applied_details = []
        pending_details = []
        
        # Get applied migration details from database
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT version, name, applied_at, environment, success, error_message
                FROM database_migrations
                WHERE success = 1
                ORDER BY applied_at DESC
            """)
            
            for row in cursor.fetchall():
                applied_details.append({
                    'version': row[0],
                    'name': row[1],
                    'applied_at': row[2],
                    'environment': row[3],
                    'success': bool(row[4]),
                    'error_message': row[5]
                })
            
            conn.close()
        except Exception:
            # If migrations table doesn't exist or other error
            pass
        
        # Get pending migration details
        for migration in pending_migrations:
            pending_details.append({
                'version': migration.version,
                'description': migration.description or migration.__class__.__name__,
                'dependencies': migration.dependencies,
                'environments': migration.environments,
                'can_run': migration.can_run_in_environment(self.environment)
            })
        
        return {
            "database_path": self.database_path,
            "environment": self.environment,
            "total_migrations": len(all_migrations),
            "applied_count": len(applied_migrations),
            "pending_count": len(pending_migrations),
            "applied_versions": applied_migrations,
            "pending_versions": [m.version for m in pending_migrations],
            "last_migration": applied_migrations[-1] if applied_migrations else None,
            "applied_details": applied_details,
            "pending_details": pending_details,
            "database_exists": os.path.exists(self.database_path),
            "migrations_table_exists": self._migrations_table_exists()
        }
    
    def _migrations_table_exists(self) -> bool:
        """Check if migrations tracking table exists"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='database_migrations'
            """)
            exists = cursor.fetchone() is not None
            conn.close()
            return exists
        except Exception:
            return False
    
    def get_migration_details(self, version: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific migration"""
        try:
            # First check available migrations
            all_migrations = self.discover_migrations()
            if version in all_migrations:
                migration = all_migrations[version]
                
                # Get execution history from database
                execution_history = []
                try:
                    conn = sqlite3.connect(self.database_path)
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT applied_at, applied_by, environment, success, error_message
                        FROM database_migrations
                        WHERE version = ?
                        ORDER BY applied_at DESC
                    """, (version,))
                    
                    for row in cursor.fetchall():
                        execution_history.append({
                            'applied_at': row[0],
                            'applied_by': row[1],
                            'environment': row[2],
                            'success': bool(row[3]),
                            'error_message': row[4]
                        })
                    
                    conn.close()
                except Exception:
                    pass
                
                return {
                    'version': migration.version,
                    'description': migration.description or migration.__class__.__name__,
                    'dependencies': migration.dependencies,
                    'environments': migration.environments,
                    'can_run_in_environment': migration.can_run_in_environment(self.environment),
                    'checksum': migration.get_checksum(),
                    'is_applied': version in self.get_applied_migrations(),
                    'execution_history': execution_history
                }
            
            return None
        except Exception as e:
            self.logger.error(f"❌ Failed to get migration details for {version}: {e}")
            return None
    
    def validate_migration_sequence(self) -> Dict[str, Any]:
        """Validate that all migrations can be applied in correct order"""
        try:
            all_migrations = self.discover_migrations()
            applied_migrations = set(self.get_applied_migrations())
            
            validation_results = {
                'valid': True,
                'issues': [],
                'warnings': []
            }
            
            # Check for missing dependencies
            for version, migration in all_migrations.items():
                if version not in applied_migrations:
                    for dep in migration.dependencies:
                        if dep not in applied_migrations and dep not in all_migrations:
                            validation_results['valid'] = False
                            validation_results['issues'].append(
                                f"Migration {version} depends on {dep} which is not available"
                            )
                        elif dep not in applied_migrations:
                            validation_results['warnings'].append(
                                f"Migration {version} depends on {dep} which is not yet applied"
                            )
            
            # Check for environment compatibility
            incompatible = []
            for version, migration in all_migrations.items():
                if not migration.can_run_in_environment(self.environment):
                    incompatible.append(version)
            
            if incompatible:
                validation_results['warnings'].append(
                    f"Migrations not compatible with environment '{self.environment}': {', '.join(incompatible)}"
                )
            
            return validation_results
        except Exception as e:
            return {
                'valid': False,
                'issues': [f"Validation failed: {str(e)}"],
                'warnings': []
            }
    
    def _record_migration(self, migration: BaseMigration, success: bool, error: str = None):
        """Record migration application in the database"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO database_migrations 
                (version, name, checksum, applied_at, applied_by, environment, success, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                migration.version,
                migration.description or migration.__class__.__name__,
                migration.get_checksum(),
                datetime.now().isoformat(),
                "migration_manager",
                self.environment,
                success,
                error
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"❌ Failed to record migration: {e}")
    
    def _remove_migration_record(self, version: str):
        """Remove migration record from database"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM database_migrations WHERE version = ?", (version,))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"❌ Failed to remove migration record: {e}")
    
    def _create_backup(self) -> str:
        """Create database backup before migrations"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{self.database_path}.backup_{timestamp}"
        
        try:
            # Create backup using sqlite3 backup API
            source = sqlite3.connect(self.database_path)
            backup = sqlite3.connect(backup_path)
            source.backup(backup)
            source.close()
            backup.close()
            
            return backup_path
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create backup: {e}")
            return None

def main():
    """CLI interface for migration management"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Database Migration Manager")
    parser.add_argument("--database", default="arrow_database.db", help="Database file path")
    parser.add_argument("--migrations-dir", default="migrations", help="Migrations directory")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show migration status")
    
    # Migrate command
    migrate_parser = subparsers.add_parser("migrate", help="Run pending migrations")
    migrate_parser.add_argument("--target", help="Target migration version")
    migrate_parser.add_argument("--dry-run", action="store_true", help="Preview migrations without applying")
    
    # Rollback command
    rollback_parser = subparsers.add_parser("rollback", help="Rollback migrations")
    rollback_parser.add_argument("version", help="Version to rollback to")
    rollback_parser.add_argument("--dry-run", action="store_true", help="Preview rollback without applying")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize migration manager
    manager = DatabaseMigrationManager(args.database, args.migrations_dir)
    
    if args.command == "status":
        status = manager.get_migration_status()
        print("\n🗄️ Database Migration Status")
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
    
    elif args.command == "migrate":
        success = manager.migrate(args.target, args.dry_run)
        sys.exit(0 if success else 1)
    
    elif args.command == "rollback":
        print(f"❌ Rollback not yet implemented")
        sys.exit(1)

if __name__ == "__main__":
    main()