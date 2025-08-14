#!/usr/bin/env python3
"""
Migration 020: Add missing equipment learning tables
Creates equipment_models and equipment_usage_stats tables needed by EquipmentLearningManager
"""

import sqlite3
from database_migration_manager import BaseMigration

class Migration020AddEquipmentLearningTables(BaseMigration):
    def __init__(self):
        super().__init__()
        self.version = "020"
        self.description = "Add missing equipment learning tables"
        self.dependencies = ["019"]
        self.environments = ['all']
        self.target_database = 'user'  # These tables belong in user_data.db
    
    def up(self, db_path: str, environment: str) -> bool:
        """Create equipment learning tables"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            print("🔄 Creating equipment learning tables...")
            
            # Create equipment_models table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS equipment_models (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    manufacturer_name TEXT NOT NULL,
                    model_name TEXT NOT NULL,
                    category_name TEXT NOT NULL,
                    usage_count INTEGER DEFAULT 1,
                    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by_user_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(manufacturer_name, model_name, category_name),
                    FOREIGN KEY (created_by_user_id) REFERENCES users (id) ON DELETE SET NULL
                )
            ''')
            
            # Create equipment_usage_stats table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS equipment_usage_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    manufacturer_name TEXT NOT NULL,
                    model_name TEXT NOT NULL,
                    category_name TEXT NOT NULL,
                    monthly_usage INTEGER DEFAULT 0,
                    total_usage INTEGER DEFAULT 0,
                    period_start DATE NOT NULL,
                    period_end DATE NOT NULL,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(manufacturer_name, model_name, category_name, period_start)
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_equipment_models_manufacturer 
                ON equipment_models (manufacturer_name)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_equipment_models_category 
                ON equipment_models (category_name)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_equipment_models_usage 
                ON equipment_models (usage_count DESC)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_equipment_models_last_used 
                ON equipment_models (last_used DESC)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_equipment_usage_stats_period 
                ON equipment_usage_stats (period_start, period_end)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_equipment_usage_stats_category 
                ON equipment_usage_stats (category_name)
            ''')
            
            conn.commit()
            conn.close()
            
            print("✅ Equipment learning tables created successfully")
            print("   - equipment_models: Track model usage and statistics")
            print("   - equipment_usage_stats: Monthly usage statistics")
            print("   - Created 6 performance indexes")
            
            return True
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            return False
    
    def down(self, db_path: str, environment: str) -> bool:
        """Rollback: Remove equipment learning tables"""
        try:
            print("🔄 Rolling back equipment learning tables...")
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Drop indexes first
            cursor.execute('DROP INDEX IF EXISTS idx_equipment_models_manufacturer')
            cursor.execute('DROP INDEX IF EXISTS idx_equipment_models_category')
            cursor.execute('DROP INDEX IF EXISTS idx_equipment_models_usage')
            cursor.execute('DROP INDEX IF EXISTS idx_equipment_models_last_used')
            cursor.execute('DROP INDEX IF EXISTS idx_equipment_usage_stats_period')
            cursor.execute('DROP INDEX IF EXISTS idx_equipment_usage_stats_category')
            
            # Drop tables
            cursor.execute('DROP TABLE IF EXISTS equipment_usage_stats')
            cursor.execute('DROP TABLE IF EXISTS equipment_models')
            
            conn.commit()
            conn.close()
            
            print("✅ Equipment learning tables removed")
            
            return True
            
        except Exception as e:
            print(f"❌ Rollback failed: {e}")
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            return False

# Create the migration instance for discovery
migration = Migration020AddEquipmentLearningTables()