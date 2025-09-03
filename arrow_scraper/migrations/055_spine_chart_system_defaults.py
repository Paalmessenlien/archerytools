"""
Migration: Spine Chart System Defaults
Version: 051
Description: Add system default functionality to spine charts for unified chart management
"""

import sqlite3
import sys
from pathlib import Path

# Add parent directory to path to import migration base class
sys.path.append(str(Path(__file__).parent.parent))
from database_migration_manager import BaseMigration

class SpineChartSystemDefaultsMigration(BaseMigration):
    """Add system default functionality to spine charts"""
    
    def __init__(self):
        super().__init__()
        self.version = "055"
        self.description = "Add system default functionality to spine charts for unified chart management"
        self.dependencies = ["001"]  # Depends on spine calculator tables
        self.environments = ['all']
        self.target_database = 'arrow'
    
    def up(self, db_path: str, environment: str) -> bool:
        """Apply the migration - add system default fields"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Add system default fields to manufacturer spine charts
            try:
                cursor.execute("""
                    ALTER TABLE manufacturer_spine_charts_enhanced 
                    ADD COLUMN is_system_default BOOLEAN DEFAULT 0
                """)
                print("✅ Added is_system_default to manufacturer_spine_charts_enhanced")
            except sqlite3.OperationalError as e:
                if "duplicate column name" not in str(e).lower():
                    raise
                print("ℹ️  Column is_system_default already exists in manufacturer_spine_charts_enhanced")
            
            try:
                cursor.execute("""
                    ALTER TABLE manufacturer_spine_charts_enhanced 
                    ADD COLUMN calculation_priority INTEGER DEFAULT 100
                """)
                print("✅ Added calculation_priority to manufacturer_spine_charts_enhanced")
            except sqlite3.OperationalError as e:
                if "duplicate column name" not in str(e).lower():
                    raise
                print("ℹ️  Column calculation_priority already exists in manufacturer_spine_charts_enhanced")
            
            # Add system default fields to custom spine charts
            try:
                cursor.execute("""
                    ALTER TABLE custom_spine_charts 
                    ADD COLUMN is_system_default BOOLEAN DEFAULT 0
                """)
                print("✅ Added is_system_default to custom_spine_charts")
            except sqlite3.OperationalError as e:
                if "duplicate column name" not in str(e).lower():
                    raise
                print("ℹ️  Column is_system_default already exists in custom_spine_charts")
            
            try:
                cursor.execute("""
                    ALTER TABLE custom_spine_charts 
                    ADD COLUMN calculation_priority INTEGER DEFAULT 100
                """)
                print("✅ Added calculation_priority to custom_spine_charts")
            except sqlite3.OperationalError as e:
                if "duplicate column name" not in str(e).lower():
                    raise
                print("ℹ️  Column calculation_priority already exists in custom_spine_charts")
            
            # Create spine_system_settings table for global spine calculation settings
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS spine_system_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    setting_name TEXT NOT NULL UNIQUE,
                    setting_value TEXT NOT NULL,
                    setting_type TEXT NOT NULL DEFAULT 'string',  -- 'string', 'number', 'boolean', 'json'
                    description TEXT,
                    category TEXT DEFAULT 'general',
                    is_admin_only BOOLEAN DEFAULT 1,
                    last_modified_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("✅ Created spine_system_settings table")
            
            # Insert default system settings
            default_settings = [
                ('default_calculation_method', 'universal', 'string', 'Default calculation method for new calculations', 'calculation'),
                ('allow_chart_override', 'true', 'boolean', 'Allow users to override system default chart', 'permissions'),
                ('professional_mode_enabled', 'true', 'boolean', 'Enable professional calculation mode', 'features'),
                ('auto_select_manufacturer_chart', 'true', 'boolean', 'Automatically select manufacturer chart when available', 'calculation'),
                ('spine_tolerance_default', '25', 'number', 'Default spine tolerance range in spine units', 'calculation'),
                ('chart_validation_strict', 'false', 'boolean', 'Require strict validation for chart data entry', 'validation')
            ]
            
            for setting_name, setting_value, setting_type, description, category in default_settings:
                cursor.execute("""
                    INSERT OR IGNORE INTO spine_system_settings 
                    (setting_name, setting_value, setting_type, description, category)
                    VALUES (?, ?, ?, ?, ?)
                """, (setting_name, setting_value, setting_type, description, category))
            
            print("✅ Inserted default spine system settings")
            
            # Add indices for performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_spine_charts_system_default 
                ON manufacturer_spine_charts_enhanced(is_system_default, calculation_priority)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_custom_spine_charts_system_default 
                ON custom_spine_charts(is_system_default, calculation_priority)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_spine_system_settings_category 
                ON spine_system_settings(category, setting_name)
            """)
            
            print("✅ Created spine chart system indices")
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Failed to add spine chart system defaults: {e}")
            if 'conn' in locals():
                conn.close()
            return False
    
    def down(self, db_path: str, environment: str) -> bool:
        """Rollback the migration - remove system default functionality"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Drop the system settings table
            cursor.execute("DROP TABLE IF EXISTS spine_system_settings")
            print("✅ Dropped spine_system_settings table")
            
            # Remove added columns (Note: SQLite doesn't support DROP COLUMN directly)
            # We'll leave the columns as they're not harmful and SQLite migration complexity isn't worth it
            print("ℹ️  Leaving system default columns in place (SQLite limitation)")
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Failed to rollback spine chart system defaults: {e}")
            if 'conn' in locals():
                conn.close()
            return False