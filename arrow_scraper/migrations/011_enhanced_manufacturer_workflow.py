#!/usr/bin/env python3
"""
Migration 011: Enhanced Manufacturer Workflow
Creates pending manufacturer management system for user submissions and admin approval workflow
"""

import sqlite3
import json
from datetime import datetime
from database_migration_manager import BaseMigration

class Migration011EnhancedManufacturerWorkflow(BaseMigration):
    def __init__(self):
        super().__init__()
        self.version = "011"
        self.description = "Enhanced manufacturer workflow with pending system and admin approval"
        self.dependencies = ["010"]
        self.environments = ['all']
        self.target_database = 'user'  # This migration targets the user database
    
    def up(self, db_path: str, environment: str) -> bool:
        """Create enhanced manufacturer workflow tables in user database"""
        try:
            # Get the user database path
            user_db_path = self._get_user_database_path(db_path)
            
            if not user_db_path:
                print(f"❌ Could not find user database for migration 011")
                return False
            
            print(f"🔧 Creating enhanced manufacturer workflow tables: {user_db_path}")
            
            conn = sqlite3.connect(user_db_path)
            cursor = conn.cursor()
            
            # Create pending_manufacturers table for manufacturer submission and approval workflow
            print("   Creating pending_manufacturers table...")
            try:
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS pending_manufacturers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    normalized_name TEXT,
                    category_context TEXT,
                    usage_count INTEGER DEFAULT 1,
                    user_count INTEGER DEFAULT 1,
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'pending',
                    created_by_user_id INTEGER,
                    approved_by_admin_id INTEGER,
                    admin_notes TEXT,
                    approved_at TIMESTAMP,
                    rejection_reason TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (created_by_user_id) REFERENCES users (id),
                    FOREIGN KEY (approved_by_admin_id) REFERENCES users (id)
                )
                ''')
                print("   pending_manufacturers table created successfully")
            except Exception as e:
                print(f"   Error creating pending_manufacturers table: {e}")
                raise
            
            # Create user_pending_manufacturers table to track which users have access to which pending manufacturers
            print("   Creating user_pending_manufacturers table...")
            try:
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_pending_manufacturers (
                    user_id INTEGER,
                    pending_manufacturer_id INTEGER,
                    first_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    usage_count INTEGER DEFAULT 1,
                    equipment_count INTEGER DEFAULT 1,
                    PRIMARY KEY (user_id, pending_manufacturer_id),
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (pending_manufacturer_id) REFERENCES pending_manufacturers (id) ON DELETE CASCADE
                )
                ''')
                print("   user_pending_manufacturers table created successfully")
            except Exception as e:
                print(f"   Error creating user_pending_manufacturers table: {e}")
                raise
            
            # Create indexes for performance
            print("   Creating indexes...")
            indexes = [
                ('idx_pending_manufacturers_status', 'pending_manufacturers (status)'),
                ('idx_pending_manufacturers_name', 'pending_manufacturers (normalized_name)'),
                ('idx_pending_manufacturers_created_by', 'pending_manufacturers (created_by_user_id)'),
                ('idx_user_pending_manufacturers_user', 'user_pending_manufacturers (user_id)'),
                ('idx_user_pending_manufacturers_last_used', 'user_pending_manufacturers (last_used)')
            ]
            
            for index_name, index_def in indexes:
                try:
                    cursor.execute(f'CREATE INDEX IF NOT EXISTS {index_name} ON {index_def}')
                    print(f"     ✓ Created index {index_name}")
                except Exception as e:
                    print(f"     ⚠️  Could not create index {index_name}: {e}")
                    # Continue with other indexes
            
            print("   Index creation completed")
            
            # Create manufacturer_approval_log table for audit trail
            print("   Creating manufacturer_approval_log table...")
            try:
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS manufacturer_approval_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pending_manufacturer_id INTEGER,
                    action TEXT NOT NULL,
                    admin_user_id INTEGER,
                    user_notes TEXT,
                    admin_notes TEXT,
                    old_status TEXT,
                    new_status TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (pending_manufacturer_id) REFERENCES pending_manufacturers (id) ON DELETE CASCADE,
                    FOREIGN KEY (admin_user_id) REFERENCES users (id)
                )
                ''')
                print("   manufacturer_approval_log table created successfully")
            except Exception as e:
                print(f"   Error creating manufacturer_approval_log table: {e}")
                raise
            
            # Create remaining indexes
            print("   Creating remaining indexes...")
            remaining_indexes = [
                ('idx_approval_log_manufacturer', 'manufacturer_approval_log (pending_manufacturer_id)'),
                ('idx_approval_log_action', 'manufacturer_approval_log (action)')
            ]
            
            for index_name, index_def in remaining_indexes:
                try:
                    cursor.execute(f'CREATE INDEX IF NOT EXISTS {index_name} ON {index_def}')
                    print(f"     ✓ Created index {index_name}")
                except Exception as e:
                    print(f"     ⚠️  Could not create index {index_name}: {e}")
            
            conn.commit()
            
            # Verify tables were created
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%manufacturer%' OR name LIKE '%approval%'")
            tables = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            
            print("✅ Successfully created enhanced manufacturer workflow tables:")
            for table in sorted(tables):
                print(f"   - {table}")
            
            print("✅ Features enabled:")
            print("   - User manufacturer submissions with pending status")
            print("   - User-specific manufacturer access and reuse")
            print("   - Admin approval/rejection workflow")
            print("   - Usage statistics and analytics")
            print("   - Audit trail for all manufacturer decisions")
            print("   - Fuzzy matching for duplicate prevention")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to create enhanced manufacturer workflow: {e}")
            return False
    
    def down(self, db_path: str, environment: str) -> bool:
        """Remove enhanced manufacturer workflow tables"""
        try:
            user_db_path = self._get_user_database_path(db_path)
            
            if not user_db_path:
                print(f"❌ Could not find user database for migration 011 rollback")
                return False
            
            conn = sqlite3.connect(user_db_path)
            cursor = conn.cursor()
            
            # Drop tables in reverse dependency order
            tables_to_drop = [
                'manufacturer_approval_log',
                'user_pending_manufacturers', 
                'pending_manufacturers'
            ]
            
            for table in tables_to_drop:
                cursor.execute(f'DROP TABLE IF EXISTS {table}')
                print(f"🗑️  Dropped table: {table}")
            
            # Drop indexes (will be automatically dropped with tables, but explicit for clarity)
            indexes_to_drop = [
                'idx_pending_manufacturers_status',
                'idx_pending_manufacturers_name',
                'idx_pending_manufacturers_created_by',
                'idx_user_pending_manufacturers_user',
                'idx_user_pending_manufacturers_last_used',
                'idx_approval_log_manufacturer',
                'idx_approval_log_action'
            ]
            
            for index in indexes_to_drop:
                try:
                    cursor.execute(f'DROP INDEX IF EXISTS {index}')
                except sqlite3.OperationalError:
                    pass  # Index might not exist or already dropped
            
            conn.commit()
            conn.close()
            
            print("✅ Successfully rolled back enhanced manufacturer workflow")
            return True
            
        except Exception as e:
            print(f"❌ Failed to rollback enhanced manufacturer workflow: {e}")
            return False
    
    def _get_user_database_path(self, db_path: str) -> str:
        """Get the user database path from the arrow database path"""
        import os
        
        # Handle different database path patterns
        if '/app/databases/arrow_database.db' in db_path:
            return db_path.replace('arrow_database.db', 'user_data.db')
        elif 'databases/arrow_database.db' in db_path:
            return db_path.replace('arrow_database.db', 'user_data.db')
        elif 'arrow_scraper/arrow_database.db' in db_path:
            return db_path.replace('arrow_database.db', 'user_data.db')
        elif db_path.endswith('arrow_database.db'):
            return db_path.replace('arrow_database.db', 'user_data.db')
        else:
            # Fallback: try to find user_data.db in the same directory
            db_dir = os.path.dirname(db_path)
            return os.path.join(db_dir, 'user_data.db')

# Create the migration instance for discovery
migration = Migration011EnhancedManufacturerWorkflow()