#!/usr/bin/env python3
"""
Database Backup and Restore Manager
Provides comprehensive backup and restore functionality for ArrowTuner databases
"""

import os
import sys
import shutil
import sqlite3
import argparse
import json
import tarfile
import gzip
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class BackupManager:
    """Manages database backups and restores for ArrowTuner system"""
    
    def __init__(self, backup_dir: str = None):
        # Resolve backup directory with fallback options
        if backup_dir is None:
            backup_dir = self._resolve_backup_dir()
        
        self.backup_dir = Path(backup_dir)
        # Try to create directory, handle permission errors gracefully
        try:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            # Fall back to a local backup directory
            fallback_dir = Path.cwd() / "backups"
            print(f"⚠️  Permission denied for {self.backup_dir}, using fallback: {fallback_dir}")
            self.backup_dir = fallback_dir
            self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Database paths with proper resolution
        self.arrow_db_path = Path(self._resolve_arrow_db_path())
        self.user_db_path = Path(self._resolve_user_db_path())
        
        print(f"🗄️  Backup Manager initialized")
        print(f"   Backup directory: {self.backup_dir}")
        print(f"   Arrow database: {self.arrow_db_path}")
        print(f"   User database: {self.user_db_path}")
    
    def _resolve_backup_dir(self) -> str:
        """Resolve backup directory with fallback options"""
        # Try Docker paths first, then local development paths
        backup_paths = [
            os.environ.get('BACKUP_DIR'),  # Environment variable override
            '/app/backups',                # Docker production path
            './backups',                   # Local development path
        ]
        
        for path in backup_paths:
            if path:
                try:
                    test_path = Path(path)
                    # Test if we can create this directory
                    test_path.mkdir(parents=True, exist_ok=True)
                    return str(path)
                except (PermissionError, OSError):
                    continue
        
        # Final fallback
        return './backups'
    
    def _resolve_arrow_db_path(self) -> str:
        """Resolve arrow database path with fallback options"""
        # Try multiple locations
        arrow_db_paths = [
            os.environ.get('ARROW_DATABASE_PATH'),
            '/app/databases/arrow_database.db',     # Docker path
            '/app/arrow_data/arrow_database.db',    # Alternative Docker path  
            './databases/arrow_database.db',       # Local development path
            './arrow_database.db',                 # Fallback local path
        ]
        
        for db_path in arrow_db_paths:
            if db_path and Path(db_path).exists():
                return str(db_path)
        
        # Default to local development location
        return './databases/arrow_database.db'
    
    def _resolve_user_db_path(self) -> str:
        """Resolve user database path with fallback options"""
        # Try multiple locations
        user_db_paths = [
            os.environ.get('USER_DATABASE_PATH'),
            '/app/databases/user_data.db',         # Docker path
            '/app/user_data/user_data.db',         # Alternative Docker path
            './databases/user_data.db',           # Local development path
            './user_data.db',                     # Fallback local path
        ]
        
        for db_path in user_db_paths:
            if db_path and Path(db_path).exists():
                return str(db_path)
        
        # Default to local development location
        return './databases/user_data.db'
    
    def create_backup(self, backup_name: Optional[str] = None, include_arrow_db: bool = True, include_user_db: bool = True) -> str:
        """Create a complete backup of the database system"""
        
        if not backup_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"archerytools_backup_{timestamp}"
        
        backup_path = self.backup_dir / f"{backup_name}.tar.gz"
        temp_dir = self.backup_dir / f"temp_{backup_name}"
        
        try:
            # Create temporary directory for backup preparation
            temp_dir.mkdir(exist_ok=True)
            
            print(f"🗜️  Creating backup: {backup_name}")
            
            # Create backup metadata
            metadata = {
                "backup_name": backup_name,
                "created_at": datetime.now().isoformat(),
                "version": "1.0.0",
                "includes": {
                    "arrow_database": include_arrow_db,
                    "user_database": include_user_db
                }
            }
            
            # Backup arrow database
            if include_arrow_db and self.arrow_db_path.exists():
                print(f"📊 Backing up arrow database...")
                arrow_backup_path = temp_dir / "arrow_database.db"
                self._create_db_backup(self.arrow_db_path, arrow_backup_path)
                
                # Get database statistics for metadata
                metadata["arrow_db_stats"] = self._get_db_stats(self.arrow_db_path)
            
            # Backup user database
            if include_user_db and self.user_db_path.exists():
                print(f"👤 Backing up user database...")
                user_backup_path = temp_dir / "user_data.db"
                self._create_db_backup(self.user_db_path, user_backup_path)
                
                # Get database statistics for metadata
                metadata["user_db_stats"] = self._get_db_stats(self.user_db_path)
            
            # Save metadata
            metadata_path = temp_dir / "backup_metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Create compressed tar archive
            print(f"🗜️  Compressing backup...")
            with tarfile.open(backup_path, "w:gz") as tar:
                for file_path in temp_dir.iterdir():
                    tar.add(file_path, arcname=file_path.name)
            
            # Cleanup temporary directory
            shutil.rmtree(temp_dir)
            
            backup_size = backup_path.stat().st_size / (1024 * 1024)  # MB
            print(f"✅ Backup created successfully!")
            print(f"   File: {backup_path}")
            print(f"   Size: {backup_size:.2f} MB")
            
            return str(backup_path)
            
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            # Cleanup on failure
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            if backup_path.exists():
                backup_path.unlink()
            raise
    
    def restore_backup(self, backup_path: str, restore_arrow_db: bool = True, restore_user_db: bool = True, force: bool = False) -> bool:
        """Restore databases from a backup file"""
        
        backup_file = Path(backup_path)
        if not backup_file.exists():
            print(f"❌ Backup file not found: {backup_path}")
            return False
        
        temp_dir = self.backup_dir / f"restore_temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # Extract backup - support both .tar.gz and .gz files
            print(f"📦 Extracting backup: {backup_file.name}")
            temp_dir.mkdir(exist_ok=True)
            
            if backup_file.name.endswith('.tar.gz'):
                # Standard tar.gz format
                with tarfile.open(backup_file, "r:gz") as tar:
                    tar.extractall(temp_dir)
            elif backup_file.name.endswith('.gz'):
                # CDN .gz format - extract as gzipped tar
                import gzip
                with gzip.open(backup_file, 'rb') as gz_file:
                    with tarfile.open(fileobj=gz_file, mode='r') as tar:
                        tar.extractall(temp_dir)
            else:
                print(f"❌ Unsupported backup format: {backup_file.name}")
                return False
            
            # Load metadata
            metadata_path = temp_dir / "backup_metadata.json"
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                print(f"📋 Backup created: {metadata.get('created_at', 'Unknown')}")
                print(f"📋 Backup version: {metadata.get('version', 'Unknown')}")
            else:
                print("⚠️  No metadata found in backup")
                metadata = {}
            
            # Confirm restore if not forced
            if not force:
                print(f"\n⚠️  This will overwrite existing databases!")
                if restore_arrow_db:
                    print(f"   Arrow database: {self.arrow_db_path}")
                if restore_user_db:
                    print(f"   User database: {self.user_db_path}")
                
                response = input("Continue? (y/N): ").lower().strip()
                if response != 'y':
                    print("❌ Restore cancelled")
                    return False
            
            # Restore arrow database
            if restore_arrow_db:
                arrow_backup = temp_dir / "arrow_database.db"
                if arrow_backup.exists():
                    print(f"📊 Restoring arrow database...")
                    self._restore_db_backup(arrow_backup, self.arrow_db_path)
                else:
                    print(f"⚠️  Arrow database not found in backup")
            
            # Restore user database
            if restore_user_db:
                user_backup = temp_dir / "user_data.db"
                if user_backup.exists():
                    print(f"👤 Restoring user database...")
                    self._restore_db_backup(user_backup, self.user_db_path)
                else:
                    print(f"⚠️  User database not found in backup")
            
            # Cleanup
            shutil.rmtree(temp_dir)
            
            print(f"✅ Restore completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Restore failed: {e}")
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            return False
    
    def list_backups(self) -> List[Dict]:
        """List all available backups - supports both .tar.gz and .gz files"""
        backups = []
        
        # Look for both .tar.gz and .gz files
        backup_patterns = ["*.tar.gz", "*.gz"]
        for pattern in backup_patterns:
            for backup_file in self.backup_dir.glob(pattern):
                try:
                    # Skip .tar.gz files when processing .gz pattern to avoid duplicates
                    if pattern == "*.gz" and backup_file.name.endswith('.tar.gz'):
                        continue
                        
                    # Try to extract metadata
                    temp_dir = self.backup_dir / f"list_temp_{backup_file.stem}"
                    temp_dir.mkdir(exist_ok=True)
                    
                    # Handle both .tar.gz and .gz formats
                    if backup_file.name.endswith('.tar.gz'):
                        # Standard tar.gz format
                        with tarfile.open(backup_file, "r:gz") as tar:
                            try:
                                metadata_member = tar.getmember("backup_metadata.json")
                                metadata_file = tar.extractfile(metadata_member)
                                metadata = json.load(metadata_file)
                            except:
                                metadata = {}
                    elif backup_file.name.endswith('.gz'):
                        # CDN .gz format
                        with gzip.open(backup_file, 'rb') as gz_file:
                            with tarfile.open(fileobj=gz_file, mode='r') as tar:
                                try:
                                    metadata_member = tar.getmember("backup_metadata.json")
                                    metadata_file = tar.extractfile(metadata_member)
                                    metadata = json.load(metadata_file)
                                except:
                                    metadata = {}
                    else:
                        continue  # Skip unsupported formats
                    
                    # Extract clean backup name (remove both .tar.gz and .gz extensions)
                    clean_name = backup_file.name
                    if clean_name.endswith('.tar.gz'):
                        clean_name = clean_name[:-7]  # Remove .tar.gz
                    elif clean_name.endswith('.gz'):
                        clean_name = clean_name[:-3]  # Remove .gz
                    
                    # Generate consistent ID for local backups (hash of filename)
                    import hashlib
                    backup_id = hashlib.md5(clean_name.encode()).hexdigest()[:8]
                    
                    backup_info = {
                        "id": f"local_{backup_id}",  # Add consistent ID field
                        "file": str(backup_file),
                        "name": clean_name,
                        "backup_name": clean_name,  # Add backup_name for consistency with CDN format
                        "size_mb": backup_file.stat().st_size / (1024 * 1024),
                        "created_at": metadata.get('created_at', 'Unknown'),
                        "includes": metadata.get('includes', {}),
                        "arrow_db_stats": metadata.get('arrow_db_stats', {}),
                        "user_db_stats": metadata.get('user_db_stats', {}),
                        "is_local_file": True  # Flag to indicate this is a local file backup
                    }
                    backups.append(backup_info)
                    
                    # Cleanup
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    
                except Exception as e:
                    print(f"⚠️  Could not read backup {backup_file.name}: {e}")
        
        return sorted(backups, key=lambda x: x['created_at'], reverse=True)
    
    def verify_backup(self, backup_path: str) -> bool:
        """Verify the integrity of a backup file"""
        
        backup_file = Path(backup_path)
        if not backup_file.exists():
            print(f"❌ Backup file not found: {backup_path}")
            return False
        
        try:
            print(f"🔍 Verifying backup: {backup_file.name}")
            
            # Support both .tar.gz and .gz files
            members = []
            tar_obj = None
            
            if backup_file.name.endswith('.tar.gz'):
                # Standard tar.gz format
                tar_obj = tarfile.open(backup_file, "r:gz")
                members = tar_obj.getnames()
                print(f"📁 Archive contains {len(members)} files")
            elif backup_file.name.endswith('.gz'):
                # CDN .gz format - verify as gzipped tar
                gz_file = gzip.open(backup_file, 'rb')
                tar_obj = tarfile.open(fileobj=gz_file, mode='r')
                members = tar_obj.getnames()
                print(f"📁 Archive contains {len(members)} files")
            else:
                print(f"❌ Unsupported backup format: {backup_file.name}")
                return False
            
            # Verify expected files
            expected_files = ["backup_metadata.json"]
            missing_files = []
            
            for expected in expected_files:
                if expected not in members:
                    missing_files.append(expected)
            
            if missing_files:
                print(f"⚠️  Missing files: {', '.join(missing_files)}")
            
            # Try to extract and verify metadata
            try:
                metadata_member = tar_obj.getmember("backup_metadata.json")
                metadata_file = tar_obj.extractfile(metadata_member)
                metadata = json.load(metadata_file)
                print(f"📋 Backup created: {metadata.get('created_at', 'Unknown')}")
                print(f"📋 Includes: {metadata.get('includes', {})}")
            except Exception as e:
                print(f"⚠️  Could not read metadata: {e}")
            finally:
                if tar_obj:
                    tar_obj.close()
                if 'gz_file' in locals():
                    gz_file.close()
            
            # Verify database files if present
            for db_file in ["arrow_database.db", "user_data.db"]:
                if db_file in members:
                    print(f"✅ Found {db_file}")
                    # TODO: Could add SQLite integrity check here
                
            print(f"✅ Backup verification completed")
            return True
            
        except Exception as e:
            print(f"❌ Backup verification failed: {e}")
            return False
    
    def cleanup_old_backups(self, keep_count: int = 10) -> int:
        """Remove old backup files, keeping only the most recent ones"""
        
        backups = self.list_backups()
        
        if len(backups) <= keep_count:
            print(f"📦 {len(backups)} backups found, keeping all (limit: {keep_count})")
            return 0
        
        backups_to_remove = backups[keep_count:]
        removed_count = 0
        
        print(f"🗑️  Removing {len(backups_to_remove)} old backups (keeping {keep_count} most recent)")
        
        for backup in backups_to_remove:
            try:
                backup_file = Path(backup['file'])
                backup_file.unlink()
                print(f"   Removed: {backup_file.name}")
                removed_count += 1
            except Exception as e:
                print(f"   Failed to remove {backup['name']}: {e}")
        
        print(f"✅ Cleanup completed: removed {removed_count} backups")
        return removed_count
    
    def _create_db_backup(self, source_db: Path, backup_db: Path):
        """Create a backup of a SQLite database using SQLite's backup API"""
        
        # Ensure parent directory exists
        backup_db.parent.mkdir(parents=True, exist_ok=True)
        
        # Use SQLite's backup API for consistent backup
        source_conn = sqlite3.connect(source_db)
        backup_conn = sqlite3.connect(backup_db)
        
        try:
            source_conn.backup(backup_conn)
            print(f"   ✅ Database copied: {source_db.name}")
        finally:
            source_conn.close()
            backup_conn.close()
    
    def _restore_db_backup(self, backup_db: Path, target_db: Path):
        """Restore a SQLite database from backup"""
        
        # Ensure parent directory exists
        target_db.parent.mkdir(parents=True, exist_ok=True)
        
        # Create backup of existing database before restore
        if target_db.exists():
            backup_existing = target_db.with_suffix(f".pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
            shutil.copy2(target_db, backup_existing)
            print(f"   📋 Existing database backed up to: {backup_existing.name}")
        
        # Copy the backup to target location
        shutil.copy2(backup_db, target_db)
        print(f"   ✅ Database restored: {target_db.name}")
    
    def _get_db_stats(self, db_path: Path) -> Dict:
        """Get basic statistics from a database"""
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get table list
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables = [row[0] for row in cursor.fetchall()]
            
            stats = {
                "file_size_mb": db_path.stat().st_size / (1024 * 1024),
                "table_count": len(tables),
                "tables": {}
            }
            
            # Get row counts for each table
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM [{table}]")
                    count = cursor.fetchone()[0]
                    stats["tables"][table] = count
                except:
                    stats["tables"][table] = "unknown"
            
            conn.close()
            return stats
            
        except Exception as e:
            return {"error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="ArrowTuner Database Backup Manager")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create backup command
    backup_parser = subparsers.add_parser('backup', help='Create a new backup')
    backup_parser.add_argument('--name', help='Backup name (auto-generated if not provided)')
    backup_parser.add_argument('--arrow-db-only', action='store_true', help='Backup only arrow database')
    backup_parser.add_argument('--user-db-only', action='store_true', help='Backup only user database')
    backup_parser.add_argument('--backup-dir', default='/app/backups', help='Backup directory')
    
    # Restore backup command
    restore_parser = subparsers.add_parser('restore', help='Restore from backup')
    restore_parser.add_argument('backup_file', help='Path to backup file')
    restore_parser.add_argument('--arrow-db-only', action='store_true', help='Restore only arrow database')
    restore_parser.add_argument('--user-db-only', action='store_true', help='Restore only user database')
    restore_parser.add_argument('--force', action='store_true', help='Skip confirmation prompt')
    restore_parser.add_argument('--backup-dir', default='/app/backups', help='Backup directory')
    
    # List backups command
    list_parser = subparsers.add_parser('list', help='List available backups')
    list_parser.add_argument('--backup-dir', default='/app/backups', help='Backup directory')
    
    # Verify backup command
    verify_parser = subparsers.add_parser('verify', help='Verify backup integrity')
    verify_parser.add_argument('backup_file', help='Path to backup file')
    verify_parser.add_argument('--backup-dir', default='/app/backups', help='Backup directory')
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Remove old backups')
    cleanup_parser.add_argument('--keep', type=int, default=10, help='Number of backups to keep')
    cleanup_parser.add_argument('--backup-dir', default='/app/backups', help='Backup directory')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize backup manager
    backup_manager = BackupManager(args.backup_dir)
    
    if args.command == 'backup':
        include_arrow = not args.user_db_only
        include_user = not args.arrow_db_only
        
        backup_path = backup_manager.create_backup(
            backup_name=args.name,
            include_arrow_db=include_arrow,
            include_user_db=include_user
        )
        print(f"\n🎉 Backup created: {backup_path}")
        
    elif args.command == 'restore':
        restore_arrow = not args.user_db_only
        restore_user = not args.arrow_db_only
        
        success = backup_manager.restore_backup(
            backup_path=args.backup_file,
            restore_arrow_db=restore_arrow,
            restore_user_db=restore_user,
            force=args.force
        )
        
        if success:
            print(f"\n🎉 Restore completed successfully!")
        else:
            print(f"\n❌ Restore failed!")
            sys.exit(1)
        
    elif args.command == 'list':
        backups = backup_manager.list_backups()
        
        if not backups:
            print("📦 No backups found")
            return
        
        print(f"\n📦 Found {len(backups)} backups:")
        print("-" * 80)
        
        for backup in backups:
            print(f"Name: {backup['name']}")
            print(f"Created: {backup['created_at']}")
            print(f"Size: {backup['size_mb']:.2f} MB")
            print(f"Includes: {backup['includes']}")
            if backup.get('arrow_db_stats'):
                arrow_stats = backup['arrow_db_stats']
                print(f"Arrow DB: {arrow_stats.get('table_count', 0)} tables, {sum(v for v in arrow_stats.get('tables', {}).values() if isinstance(v, int))} records")
            if backup.get('user_db_stats'):
                user_stats = backup['user_db_stats']
                print(f"User DB: {user_stats.get('table_count', 0)} tables, {sum(v for v in user_stats.get('tables', {}).values() if isinstance(v, int))} records")
            print("-" * 80)
        
    elif args.command == 'verify':
        success = backup_manager.verify_backup(args.backup_file)
        
        if success:
            print(f"\n✅ Backup verification passed!")
        else:
            print(f"\n❌ Backup verification failed!")
            sys.exit(1)
        
    elif args.command == 'cleanup':
        removed_count = backup_manager.cleanup_old_backups(args.keep)
        print(f"\n🎉 Cleanup completed: removed {removed_count} old backups")


if __name__ == "__main__":
    main()