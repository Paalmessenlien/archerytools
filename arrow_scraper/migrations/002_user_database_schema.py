"""
Migration: User Database Schema
Version: 002
Description: Ensure user database tables exist with proper schema
"""

import sqlite3
import sys
from pathlib import Path

# Add parent directory to path to import migration base class
sys.path.append(str(Path(__file__).parent.parent))
from database_migration_manager import BaseMigration

class UserDatabaseSchemaMigration(BaseMigration):
    """Ensure user database tables exist with proper schema"""
    
    def __init__(self):
        super().__init__()
        self.version = "002"
        self.description = "Ensure user database tables exist with proper schema"
        self.dependencies = []
        self.environments = ['all']
        self.target_database = 'user'  # This migration creates user database schema
    
    def up(self, db_path: str, environment: str) -> bool:
        """Apply the migration - ensure user database schema"""
        try:
            # This migration works on the user database, not arrow database
            # We need to find the user database path
            user_db_path = self._get_user_database_path(db_path)
            
            conn = sqlite3.connect(user_db_path)
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    name TEXT,
                    google_id TEXT UNIQUE,
                    draw_length REAL,
                    is_admin BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create bow_setups table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bow_setups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    setup_name TEXT NOT NULL,
                    bow_type TEXT NOT NULL,
                    draw_weight REAL NOT NULL,
                    arrow_length REAL NOT NULL,
                    point_weight REAL NOT NULL,
                    bow_brand TEXT,
                    bow_model TEXT,
                    ibo_speed REAL,
                    axle_to_axle REAL,
                    brace_height REAL,
                    let_off REAL,
                    cam_type TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Create setup_arrows table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS setup_arrows (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    setup_id INTEGER NOT NULL,
                    arrow_id INTEGER NOT NULL,
                    spine_selected TEXT,
                    custom_length REAL,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (setup_id) REFERENCES bow_setups (id)
                )
            """)
            
            # Create guide_sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS guide_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    session_name TEXT NOT NULL,
                    guide_type TEXT NOT NULL,
                    bow_setup_id INTEGER,
                    current_step INTEGER DEFAULT 0,
                    total_steps INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'active',
                    session_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (bow_setup_id) REFERENCES bow_setups (id)
                )
            """)
            
            # Create backup_metadata table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS backup_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    backup_name TEXT NOT NULL,
                    backup_type TEXT DEFAULT 'manual',
                    file_path TEXT,
                    cdn_url TEXT,
                    backup_size INTEGER,
                    includes TEXT,
                    arrow_db_stats TEXT,
                    user_db_stats TEXT,
                    created_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
            
            print(f"✅ User database schema updated at: {user_db_path}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to update user database schema: {e}")
            if 'conn' in locals():
                conn.close()
            return False
    
    def down(self, db_path: str, environment: str) -> bool:
        """Rollback the migration - this is a no-op for user schema"""
        # We don't want to drop user tables as this would lose user data
        print("⚠️  User database schema rollback is not implemented to prevent data loss")
        return True
    
    def _get_user_database_path(self, arrow_db_path: str) -> str:
        """Determine user database path from arrow database path"""
        import os
        
        # Check for environment variable first
        user_db_path = os.environ.get('USER_DATABASE_PATH')
        if user_db_path:
            return user_db_path
        
        # Derive from arrow database path
        if '/app/databases/' in arrow_db_path:
            return arrow_db_path.replace('arrow_database.db', 'user_data.db')
        elif 'databases/' in arrow_db_path:
            return arrow_db_path.replace('arrow_database.db', 'user_data.db')
        else:
            # Default fallback
            return arrow_db_path.replace('arrow_database.db', 'user_data.db')