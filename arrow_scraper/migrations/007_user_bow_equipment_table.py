#!/usr/bin/env python3
"""
Migration 007: Add bow_equipment table to user database
Adds the bow_equipment table to the user database for linking bow setups to equipment.
This table stores the junction relationship between bow setups and equipment items.
"""

import sqlite3
import os
from pathlib import Path
from database_migration_manager import BaseMigration

class Migration007UserBowEquipmentTable(BaseMigration):
    def __init__(self):
        super().__init__()
        self.version = "007"
        self.description = "Add bow_equipment table to user database"
        self.dependencies = ["002"]  # Depends on user database schema
        self.environments = ['all']
        self.target_database = 'user'  # This migration targets the user database
    
    def up(self, db_path: str, environment: str) -> bool:
        """Add bow_equipment table to user database"""
        try:
            # Get the user database path
            user_db_path = self._get_user_database_path(db_path)
            
            if not user_db_path:
                print(f"❌ Could not find user database for migration 007")
                return False
            
            print(f"🔧 Adding bow_equipment table to user database: {user_db_path}")
            
            conn = sqlite3.connect(user_db_path)
            cursor = conn.cursor()
            
            # Check if bow_equipment table already exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='bow_equipment'
            """)
            
            if cursor.fetchone():
                print("✅ bow_equipment table already exists in user database")
                conn.close()
                return True
            
            # Create bow_equipment table
            cursor.execute("""
                CREATE TABLE bow_equipment (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bow_setup_id INTEGER NOT NULL,
                    equipment_id INTEGER NOT NULL,
                    installation_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    installation_notes TEXT,
                    custom_specifications TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (bow_setup_id) REFERENCES bow_setups (id) ON DELETE CASCADE
                )
            """)
            
            # Create index for better performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_bow_equipment_setup_id 
                ON bow_equipment (bow_setup_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_bow_equipment_equipment_id 
                ON bow_equipment (equipment_id)
            """)
            
            conn.commit()
            conn.close()
            
            print("✅ Successfully added bow_equipment table to user database")
            return True
            
        except Exception as e:
            print(f"❌ Failed to add bow_equipment table: {e}")
            return False
    
    def down(self, db_path: str, environment: str) -> bool:
        """Remove bow_equipment table from user database"""
        try:
            user_db_path = self._get_user_database_path(db_path)
            
            if not user_db_path:
                print(f"❌ Could not find user database for migration 007 rollback")
                return False
            
            print(f"🔧 Removing bow_equipment table from user database: {user_db_path}")
            
            conn = sqlite3.connect(user_db_path)
            cursor = conn.cursor()
            
            # Drop indexes first
            cursor.execute('DROP INDEX IF EXISTS idx_bow_equipment_setup_id')
            cursor.execute('DROP INDEX IF EXISTS idx_bow_equipment_equipment_id')
            
            # Drop table
            cursor.execute('DROP TABLE IF EXISTS bow_equipment')
            
            conn.commit()
            conn.close()
            
            print("✅ Successfully removed bow_equipment table from user database")
            return True
            
        except Exception as e:
            print(f"❌ Failed to remove bow_equipment table: {e}")
            return False
    
    def _get_user_database_path(self, arrow_db_path: str) -> str:
        """Get the user database path based on the arrow database path"""
        try:
            from user_database import UserDatabase
            
            # Create a UserDatabase instance to get the resolved path
            user_db = UserDatabase()
            user_db_path = user_db.db_path
            
            if Path(user_db_path).exists() or Path(user_db_path).parent.exists():
                return user_db_path
            
            # Fallback: try to infer user db path from arrow db path
            arrow_path = Path(arrow_db_path)
            possible_user_paths = [
                arrow_path.parent / "user_data.db",
                Path(str(arrow_path).replace("arrow_database.db", "user_data.db")),
                Path("/app/user_data/user_data.db"),
                Path("user_data.db")
            ]
            
            for path in possible_user_paths:
                if path.exists() or path.parent.exists():
                    return str(path)
            
            print(f"⚠️  Could not find user database, tried: {possible_user_paths}")
            return None
            
        except Exception as e:
            print(f"⚠️  Error finding user database: {e}")
            return None

# Create the migration instance for discovery
migration = Migration007UserBowEquipmentTable()