#!/usr/bin/env python3
"""
Migration 009: Add Custom Equipment Support to User Database bow_equipment Table
Updates bow_equipment table in user database to support custom user-entered equipment instead of pre-chosen equipment
"""

import sqlite3
from database_migration_manager import BaseMigration

class Migration009UserCustomEquipmentSchema(BaseMigration):
    def __init__(self):
        super().__init__()
        self.version = "009"
        self.description = "Add custom equipment support to user database bow_equipment table"
        self.dependencies = ["007", "008"]  # Depends on bow_equipment table and custom equipment schema
        self.environments = ['all']
        self.target_database = 'user'  # This migration targets the user database
    
    def up(self, db_path: str, environment: str) -> bool:
        """Add custom equipment fields to bow_equipment table in user database"""
        try:
            # Get the user database path
            user_db_path = self._get_user_database_path(db_path)
            
            if not user_db_path:
                print(f"❌ Could not find user database for migration 009")
                return False
            
            print(f"🔧 Adding custom equipment fields to bow_equipment table: {user_db_path}")
            
            conn = sqlite3.connect(user_db_path)
            cursor = conn.cursor()
            
            # Add new columns to bow_equipment table for custom equipment support
            new_columns = [
                ('manufacturer_name', 'TEXT'),
                ('model_name', 'TEXT'),
                ('category_name', 'TEXT'),
                ('weight_grams', 'REAL'),
                ('description', 'TEXT'),
                ('image_url', 'TEXT'),
                ('is_custom', 'BOOLEAN DEFAULT FALSE'),
            ]
            
            for column_name, column_type in new_columns:
                try:
                    cursor.execute(f'ALTER TABLE bow_equipment ADD COLUMN {column_name} {column_type}')
                    print(f"✅ Added column {column_name} to bow_equipment table")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e):
                        print(f"⚠️  Column {column_name} already exists, skipping")
                    else:
                        raise e
            
            # Make equipment_id nullable for custom equipment
            # Note: SQLite doesn't support modifying constraints, so we'll work with existing schema
            
            # Update existing records to have is_custom = FALSE for pre-chosen equipment
            cursor.execute('''
                UPDATE bow_equipment 
                SET is_custom = FALSE 
                WHERE equipment_id IS NOT NULL AND (is_custom IS NULL OR is_custom = 0)
            ''')
            
            conn.commit()
            conn.close()
            
            print("✅ Successfully updated bow_equipment schema for custom equipment support in user database")
            return True
            
        except Exception as e:
            print(f"❌ Failed to update bow_equipment schema in user database: {e}")
            return False
    
    def down(self, db_path: str, environment: str) -> bool:
        """Remove custom equipment fields (Note: SQLite doesn't support dropping columns easily)"""
        try:
            user_db_path = self._get_user_database_path(db_path)
            
            if not user_db_path:
                print(f"❌ Could not find user database for migration 009 rollback")
                return False
            
            print(f"🔧 Rolling back custom equipment fields in bow_equipment table: {user_db_path}")
            
            conn = sqlite3.connect(user_db_path)
            cursor = conn.cursor()
            
            # Note: SQLite doesn't support dropping columns, so we'll clear custom data
            # and reset is_custom flags
            cursor.execute('''
                UPDATE bow_equipment 
                SET is_custom = FALSE,
                    manufacturer_name = NULL,
                    model_name = NULL,
                    category_name = NULL,
                    weight_grams = NULL,
                    description = NULL,
                    image_url = NULL
                WHERE equipment_id IS NOT NULL
            ''')
            
            conn.commit()
            conn.close()
            
            print("✅ Successfully rolled back custom equipment schema changes in user database")
            return True
            
        except Exception as e:
            print(f"❌ Failed to rollback bow_equipment schema in user database: {e}")
            return False
    
    def _get_user_database_path(self, arrow_db_path: str) -> str:
        """Get the user database path based on the arrow database path"""
        try:
            from user_database import UserDatabase
            
            # Create a UserDatabase instance to get the resolved path
            user_db = UserDatabase()
            user_db_path = user_db.db_path
            
            from pathlib import Path
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
migration = Migration009UserCustomEquipmentSchema()