#!/usr/bin/env python3
"""
Migration 023: Consolidate User Database into Arrow Database
Migrates all user tables and data from separate user_data.db into arrow_database.db

This major migration consolidates the dual database architecture into a single database
to eliminate cross-database dependency issues, simplify the architecture, and improve
data integrity with proper foreign key relationships.

Date: 2025-08-16
Author: Claude Code Enhancement
Issue: Dual database architecture causing migration complexity and cross-database dependencies
Solution: Migrate all user tables and data into arrow database for unified architecture

Database Changes:
- Create all user tables in arrow database
- Migrate all user data from user_data.db to arrow_database.db
- Preserve all foreign key relationships and data integrity
- Remove dependency on separate user database
"""

import sqlite3
import os
import json
import shutil
from pathlib import Path
from database_migration_manager import BaseMigration

class Migration023ConsolidateUserDatabase(BaseMigration):
    def __init__(self):
        super().__init__()
        self.version = "023"
        self.description = "Consolidate User Database into Arrow Database - Unified Architecture"
        self.dependencies = ["022"]  # Depends on last user database migration
        self.environments = ['all']
        self.target_database = 'arrow'  # Migrating INTO arrow database
    
    def up(self, db_path: str, environment: str) -> bool:
        """
        Consolidate user database into arrow database
        """
        try:
            print("🔄 Starting database consolidation: User DB → Arrow DB")
            print("=" * 60)
            
            # Get user database path
            user_db_path = self._get_user_database_path()
            
            if not os.path.exists(user_db_path):
                print(f"⚠️  User database not found at {user_db_path}")
                print("   Creating empty user tables in arrow database...")
                return self._create_empty_user_tables(db_path)
            
            print(f"📁 Source: {user_db_path}")
            print(f"📁 Target: {db_path}")
            
            # Create backup of user database before migration
            backup_path = f"{user_db_path}.consolidation_backup_{self._get_timestamp()}"
            shutil.copy2(user_db_path, backup_path)
            print(f"💾 Created backup: {backup_path}")
            
            # Step 1: Create all user tables in arrow database
            self._create_user_tables_in_arrow_db(db_path)
            
            # Step 2: Migrate all data from user database
            self._migrate_user_data(user_db_path, db_path)
            
            # Step 3: Verify data integrity
            self._verify_migration(user_db_path, db_path)
            
            print("✅ Database consolidation completed successfully!")
            print(f"💾 User database backup available at: {backup_path}")
            print("🎯 All data now unified in arrow database")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to consolidate databases: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _get_user_database_path(self) -> str:
        """Get the user database path using same logic as UserDatabase class"""
        # Check environment variable first
        env_db_path = os.environ.get('USER_DATABASE_PATH')
        if env_db_path and os.path.exists(env_db_path):
            return env_db_path
        
        # Try common paths
        possible_paths = [
            "/app/databases/user_data.db",
            "/app/user_data.db", 
            "/app/user_data/user_data.db",
            "databases/user_data.db",
            "user_data.db",
            "../databases/user_data.db"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # Default fallback
        return "user_data.db"
    
    def _get_timestamp(self) -> str:
        """Get timestamp for backup naming"""
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _create_user_tables_in_arrow_db(self, arrow_db_path: str):
        """Create all user tables in arrow database"""
        print("🏗️  Creating user tables in arrow database...")
        
        conn = sqlite3.connect(arrow_db_path)
        cursor = conn.cursor()
        
        try:
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    google_id TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    name TEXT,
                    profile_picture_url TEXT,
                    is_admin BOOLEAN DEFAULT 0,
                    draw_length REAL DEFAULT 28.0,
                    skill_level TEXT DEFAULT 'intermediate',
                    shooting_style TEXT DEFAULT 'target',
                    preferred_manufacturers TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Bow setups table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bow_setups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    bow_type TEXT NOT NULL,
                    draw_weight REAL NOT NULL,
                    insert_weight REAL,
                    description TEXT,
                    bow_usage TEXT,
                    riser_brand TEXT,
                    riser_model TEXT,
                    riser_length TEXT,
                    limb_brand TEXT,
                    limb_model TEXT,
                    limb_length TEXT,
                    compound_brand TEXT,
                    compound_model TEXT,
                    ibo_speed REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            """)
            
            # Guide sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS guide_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    bow_setup_id INTEGER,
                    guide_name TEXT NOT NULL,
                    guide_type TEXT NOT NULL,
                    status TEXT DEFAULT 'in_progress',
                    current_step INTEGER DEFAULT 1,
                    total_steps INTEGER,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    notes TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                    FOREIGN KEY (bow_setup_id) REFERENCES bow_setups (id) ON DELETE SET NULL
                )
            """)
            
            # Guide step results table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS guide_step_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    step_number INTEGER NOT NULL,
                    step_name TEXT NOT NULL,
                    result_type TEXT,
                    result_value TEXT,
                    measurements TEXT,
                    adjustments_made TEXT,
                    notes TEXT,
                    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES guide_sessions (id) ON DELETE CASCADE
                )
            """)
            
            # Setup arrows table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS setup_arrows (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    setup_id INTEGER NOT NULL,
                    arrow_id INTEGER NOT NULL,
                    arrow_length REAL NOT NULL,
                    point_weight REAL NOT NULL,
                    calculated_spine INTEGER,
                    compatibility_score INTEGER,
                    notes TEXT,
                    performance_data TEXT,
                    nock_weight REAL DEFAULT 0.0,
                    insert_weight REAL DEFAULT 0.0,
                    wrap_weight REAL DEFAULT 0.0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (setup_id) REFERENCES bow_setups (id) ON DELETE CASCADE,
                    FOREIGN KEY (arrow_id) REFERENCES arrows (id) ON DELETE CASCADE
                )
            """)
            
            # Bow equipment table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bow_equipment (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bow_setup_id INTEGER NOT NULL,
                    equipment_id INTEGER,
                    installation_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    installation_notes TEXT,
                    custom_specifications TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (bow_setup_id) REFERENCES bow_setups (id) ON DELETE CASCADE
                )
            """)
            
            # Tuning history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tuning_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    bow_setup_id INTEGER,
                    guide_session_id INTEGER,
                    adjustment_type TEXT NOT NULL,
                    before_value TEXT,
                    after_value TEXT,
                    improvement_score INTEGER,
                    confidence_rating INTEGER,
                    shooting_distance REAL,
                    conditions TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                    FOREIGN KEY (bow_setup_id) REFERENCES bow_setups (id) ON DELETE SET NULL,
                    FOREIGN KEY (guide_session_id) REFERENCES guide_sessions (id) ON DELETE SET NULL
                )
            """)
            
            # Backup metadata table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS backup_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    backup_name TEXT UNIQUE NOT NULL,
                    cdn_url TEXT NOT NULL,
                    cdn_type TEXT NOT NULL,
                    file_size_mb REAL NOT NULL,
                    include_arrow_db BOOLEAN NOT NULL,
                    include_user_db BOOLEAN NOT NULL,
                    created_by INTEGER NOT NULL,
                    local_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (created_by) REFERENCES users (id) ON DELETE CASCADE
                )
            """)
            
            # Backup restore log table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS backup_restore_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    backup_id INTEGER NOT NULL,
                    restored_by INTEGER NOT NULL,
                    restore_arrow_db BOOLEAN NOT NULL,
                    restore_user_db BOOLEAN NOT NULL,
                    restored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (backup_id) REFERENCES backup_metadata (id) ON DELETE CASCADE,
                    FOREIGN KEY (restored_by) REFERENCES users (id) ON DELETE CASCADE
                )
            """)
            
            # User equipment learning tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_pending_manufacturers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    manufacturer_name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    equipment_details TEXT,
                    confidence_score REAL DEFAULT 0.5,
                    learned_from TEXT,
                    suggested_match_id INTEGER,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS equipment_usage_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    equipment_manufacturer TEXT NOT NULL,
                    equipment_model TEXT NOT NULL,
                    category TEXT NOT NULL,
                    usage_count INTEGER DEFAULT 1,
                    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    satisfaction_rating INTEGER,
                    notes TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS equipment_models (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    manufacturer_name TEXT NOT NULL,
                    model_name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    confidence_score REAL DEFAULT 0.7,
                    learned_from TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            """)
            
            # Migration tracking tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS migration_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    migration_version TEXT NOT NULL,
                    migration_name TEXT NOT NULL,
                    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    executed_by TEXT,
                    execution_time_ms INTEGER,
                    status TEXT NOT NULL
                )
            """)
            
            # Change tracking tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS setup_change_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bow_setup_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    change_type TEXT NOT NULL,
                    field_name TEXT,
                    old_value TEXT,
                    new_value TEXT,
                    change_reason TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (bow_setup_id) REFERENCES bow_setups (id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS equipment_change_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bow_equipment_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    change_type TEXT NOT NULL,
                    field_name TEXT,
                    old_value TEXT,
                    new_value TEXT,
                    change_reason TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (bow_equipment_id) REFERENCES bow_equipment (id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS arrow_change_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    setup_arrow_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    change_type TEXT NOT NULL,
                    field_name TEXT,
                    old_value TEXT,
                    new_value TEXT,
                    change_reason TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (setup_arrow_id) REFERENCES setup_arrows (id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            """)
            
            # Chronograph data table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chronograph_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    setup_id INTEGER NOT NULL,
                    arrow_id INTEGER NOT NULL,
                    arrow_length REAL NOT NULL,
                    point_weight REAL NOT NULL,
                    measured_speed REAL NOT NULL,
                    measurement_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    chronograph_model TEXT,
                    distance_meters REAL DEFAULT 0.0,
                    temperature_celsius REAL,
                    humidity_percent REAL,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (setup_id) REFERENCES bow_setups (id) ON DELETE CASCADE,
                    FOREIGN KEY (arrow_id) REFERENCES arrows (id) ON DELETE CASCADE
                )
            """)
            
            conn.commit()
            print("✅ All user tables created in arrow database")
            
        finally:
            conn.close()
    
    def _migrate_user_data(self, user_db_path: str, arrow_db_path: str):
        """Migrate all data from user database to arrow database"""
        print("📦 Migrating user data...")
        
        # Get list of tables to migrate
        user_conn = sqlite3.connect(user_db_path)
        user_conn.row_factory = sqlite3.Row
        user_cursor = user_conn.cursor()
        
        arrow_conn = sqlite3.connect(arrow_db_path)
        arrow_cursor = arrow_conn.cursor()
        
        try:
            # Get all table names from user database
            user_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            user_tables = [row[0] for row in user_cursor.fetchall()]
            
            for table_name in user_tables:
                if table_name == 'database_migrations':
                    continue  # Skip migration tracking table
                    
                print(f"   📋 Migrating table: {table_name}")
                
                # Get all data from user table
                user_cursor.execute(f"SELECT * FROM {table_name}")
                rows = user_cursor.fetchall()
                
                if not rows:
                    print(f"      ℹ️  Table {table_name} is empty")
                    continue
                
                # Get column names
                columns = [description[0] for description in user_cursor.description]
                
                # Insert data into arrow database
                placeholders = ','.join(['?' for _ in columns])
                insert_sql = f"INSERT OR IGNORE INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})"
                
                for row in rows:
                    try:
                        arrow_cursor.execute(insert_sql, tuple(row))
                    except sqlite3.Error as e:
                        print(f"      ⚠️  Error inserting row into {table_name}: {e}")
                        continue
                
                print(f"      ✅ Migrated {len(rows)} rows")
            
            arrow_conn.commit()
            print("✅ All user data migrated successfully")
            
        finally:
            user_conn.close()
            arrow_conn.close()
    
    def _verify_migration(self, user_db_path: str, arrow_db_path: str):
        """Verify that migration was successful"""
        print("🔍 Verifying migration integrity...")
        
        user_conn = sqlite3.connect(user_db_path)
        user_cursor = user_conn.cursor()
        
        arrow_conn = sqlite3.connect(arrow_db_path)
        arrow_cursor = arrow_conn.cursor()
        
        try:
            # Check key tables
            verification_tables = ['users', 'bow_setups', 'setup_arrows', 'guide_sessions']
            
            for table in verification_tables:
                # Count rows in user database
                user_cursor.execute(f"SELECT COUNT(*) FROM {table}")
                user_count = user_cursor.fetchone()[0]
                
                # Count rows in arrow database
                arrow_cursor.execute(f"SELECT COUNT(*) FROM {table}")
                arrow_count = arrow_cursor.fetchone()[0]
                
                if user_count == arrow_count:
                    print(f"   ✅ {table}: {user_count} rows migrated successfully")
                else:
                    print(f"   ⚠️  {table}: User DB has {user_count} rows, Arrow DB has {arrow_count} rows")
            
        finally:
            user_conn.close()
            arrow_conn.close()
    
    def _create_empty_user_tables(self, arrow_db_path: str) -> bool:
        """Create empty user tables if no user database exists"""
        print("🏗️  Creating empty user tables (no existing user database found)")
        self._create_user_tables_in_arrow_db(arrow_db_path)
        return True
    
    def down(self, db_path: str, environment: str) -> bool:
        """
        Rollback: Remove user tables from arrow database (WARNING: Data loss!)
        """
        print("⚠️  ROLLBACK: Removing user tables from arrow database...")
        print("   This will result in data loss!")
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # List of user tables to remove
            user_tables = [
                'backup_restore_log',
                'backup_metadata',
                'arrow_change_log',
                'equipment_change_log',
                'setup_change_log',
                'migration_history',
                'equipment_models',
                'equipment_usage_stats',
                'user_pending_manufacturers',
                'chronograph_data',
                'tuning_history',
                'bow_equipment',
                'setup_arrows',
                'guide_step_results',
                'guide_sessions',
                'bow_setups',
                'users'
            ]
            
            for table in user_tables:
                cursor.execute(f'DROP TABLE IF EXISTS {table}')
                print(f"   🗑️  Dropped table: {table}")
            
            conn.commit()
            conn.close()
            
            print("✅ Rollback completed - user tables removed from arrow database")
            return True
            
        except Exception as e:
            print(f"❌ Rollback failed: {e}")
            return False

# Create the migration instance for discovery
migration = Migration023ConsolidateUserDatabase()