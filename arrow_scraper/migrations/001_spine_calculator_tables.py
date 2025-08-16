"""
Migration: Spine Calculator Tables
Version: 001
Description: Create enhanced spine calculation tables and import spine data
"""

import os
import sqlite3
import sys
from pathlib import Path

# Add parent directory to path to import migration base class
sys.path.append(str(Path(__file__).parent.parent))
from database_migration_manager import BaseMigration

class SpineCalculatorTablesMigration(BaseMigration):
    """Create spine calculator tables and import data"""
    
    def __init__(self):
        super().__init__()
        self.version = "001"
        self.description = "Create enhanced spine calculation tables and import spine data"
        self.dependencies = []
        self.environments = ['all']
        self.target_database = 'arrow'  # Spine calculation tables belong with arrow data
    
    def up(self, db_path: str, environment: str) -> bool:
        """Apply the migration - create spine tables and import data"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create manufacturer_spine_charts_enhanced table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS manufacturer_spine_charts_enhanced (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    manufacturer TEXT NOT NULL,
                    model TEXT NOT NULL,
                    bow_type TEXT NOT NULL,
                    grid_definition TEXT,  -- JSON
                    spine_grid TEXT,       -- JSON array
                    provenance TEXT,
                    spine_system TEXT,
                    chart_notes TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(manufacturer, model, bow_type)
                )
            """)
            
            # Create custom_spine_charts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS custom_spine_charts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chart_name TEXT NOT NULL,
                    manufacturer TEXT,
                    model TEXT,
                    bow_type TEXT NOT NULL,
                    grid_definition TEXT,  -- JSON
                    spine_grid TEXT,       -- JSON array  
                    spine_system TEXT,
                    chart_notes TEXT,
                    created_by TEXT,
                    overrides_manufacturer_chart BOOLEAN DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create spine_conversion_tables table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS spine_conversion_tables (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversion_type TEXT NOT NULL,  -- 'carbon_to_aluminum', 'weight_calculation', etc.
                    source_system TEXT NOT NULL,
                    target_system TEXT NOT NULL,
                    conversion_data TEXT NOT NULL,  -- JSON
                    formula TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(conversion_type, source_system, target_system)
                )
            """)
            
            # Create spine_calculation_adjustments table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS spine_calculation_adjustments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    adjustment_type TEXT NOT NULL,  -- 'bow_speed', 'release_type', etc.
                    adjustment_factor REAL NOT NULL,
                    conditions TEXT,  -- JSON conditions
                    description TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            print("✅ Created spine calculator tables")
            
            # Import spine data if available
            self._import_spine_data(conn, cursor, environment)
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Failed to create spine calculator tables: {e}")
            if 'conn' in locals():
                conn.close()
            return False
    
    def down(self, db_path: str, environment: str) -> bool:
        """Rollback the migration - remove spine tables"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Drop tables in reverse order
            tables_to_drop = [
                "spine_calculation_adjustments",
                "spine_conversion_tables", 
                "custom_spine_charts",
                "manufacturer_spine_charts_enhanced"
            ]
            
            for table in tables_to_drop:
                cursor.execute(f"DROP TABLE IF EXISTS {table}")
                print(f"✅ Dropped table {table}")
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Failed to drop spine calculator tables: {e}")
            if 'conn' in locals():
                conn.close()
            return False
    
    def _import_spine_data(self, conn, cursor, environment):
        """Import spine calculator data if available"""
        try:
            # Try to import using spine calculator data importer
            script_dir = Path(__file__).parent.parent
            spine_importer_path = script_dir / "spine_calculator_data_importer.py"
            
            if spine_importer_path.exists():
                print("🔄 Importing spine calculator data...")
                
                # Set database path for importer
                original_db_path = os.environ.get('ARROW_DATABASE_PATH')
                os.environ['ARROW_DATABASE_PATH'] = str(conn.execute("PRAGMA database_list").fetchone()[2])
                
                try:
                    # Import and run the importer
                    sys.path.insert(0, str(script_dir))
                    from spine_calculator_data_importer import SpineCalculatorDataImporter
                    
                    # Close current connection temporarily
                    db_path = conn.execute("PRAGMA database_list").fetchone()[2]
                    conn.close()
                    
                    # Run importer
                    importer = SpineCalculatorDataImporter(db_path)
                    importer.import_all_data()
                    
                    # Reconnect
                    conn = sqlite3.connect(db_path)
                    
                    print("✅ Spine calculator data imported successfully")
                    
                except Exception as import_error:
                    print(f"⚠️  Could not import spine data: {import_error}")
                    # Not a critical error for migration
                
                finally:
                    # Restore original environment
                    if original_db_path:
                        os.environ['ARROW_DATABASE_PATH'] = original_db_path
                    elif 'ARROW_DATABASE_PATH' in os.environ:
                        del os.environ['ARROW_DATABASE_PATH']
                    
                    if str(script_dir) in sys.path:
                        sys.path.remove(str(script_dir))
            else:
                print("ℹ️  Spine calculator data importer not found, skipping data import")
                
        except Exception as e:
            print(f"⚠️  Error during spine data import: {e}")
            # Not a critical error for migration