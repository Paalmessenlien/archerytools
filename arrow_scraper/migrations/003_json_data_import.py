"""
Migration: JSON Data Import
Version: 003
Description: Import arrow data from JSON files in data/processed/ directory
"""

import json
import sqlite3
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import migration base class
sys.path.append(str(Path(__file__).parent.parent))
from database_migration_manager import BaseMigration

class JsonDataImportMigration(BaseMigration):
    """Import arrow data from JSON files"""
    
    def __init__(self):
        super().__init__()
        self.version = "003"
        self.description = "Import arrow data from JSON files in data/processed/ directory"
        self.dependencies = []  # Can run independently
        self.environments = ['all']
    
    def up(self, db_path: str, environment: str) -> bool:
        """Apply the migration - import JSON data"""
        try:
            # Use database import manager if available
            script_dir = Path(__file__).parent.parent
            data_dir = script_dir / "data" / "processed"
            
            if not data_dir.exists():
                print(f"ℹ️  No processed data directory found at {data_dir}")
                return True  # Not an error, just no data to import
            
            # Import using database import manager
            try:
                sys.path.insert(0, str(script_dir))
                from database_import_manager import DatabaseImportManager
                
                importer = DatabaseImportManager(db_path, str(data_dir))
                
                # Get JSON files to import
                json_files = importer.get_json_files()
                
                if not json_files:
                    print("ℹ️  No JSON files found to import")
                    return True
                
                print(f"🔄 Found {len(json_files)} JSON files to import")
                
                # Import each file
                imported_count = 0
                for file_path, mod_time, manufacturer in json_files:
                    try:
                        if importer.should_import_file(file_path, mod_time):
                            success = importer.import_manufacturer_data(file_path, manufacturer)
                            if success:
                                imported_count += 1
                                print(f"✅ Imported {manufacturer} data")
                            else:
                                print(f"⚠️  Failed to import {manufacturer} data")
                        else:
                            print(f"⏭️  Skipping {manufacturer} (already up to date)")
                    
                    except Exception as file_error:
                        print(f"⚠️  Error importing {manufacturer}: {file_error}")
                        # Continue with other files
                
                print(f"✅ JSON data import completed: {imported_count}/{len(json_files)} files imported")
                return True
                
            except ImportError as import_error:
                print(f"⚠️  Could not import DatabaseImportManager: {import_error}")
                # Try basic JSON import
                return self._basic_json_import(db_path, data_dir)
            
            finally:
                if str(script_dir) in sys.path:
                    sys.path.remove(str(script_dir))
                    
        except Exception as e:
            print(f"❌ Failed to import JSON data: {e}")
            return False
    
    def down(self, db_path: str, environment: str) -> bool:
        """Rollback the migration - remove imported JSON data"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # We don't want to delete all arrow data, just mark as imported by migration
            # Add a flag to track migration-imported data in the future
            print("⚠️  JSON data import rollback is not implemented to prevent data loss")
            print("     Arrow data imported via JSON files will remain in database")
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Failed to rollback JSON import: {e}")
            return False
    
    def _basic_json_import(self, db_path: str, data_dir: Path) -> bool:
        """Basic JSON import without full DatabaseImportManager"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Simple import of JSON files
            json_files = list(data_dir.glob("*.json"))
            imported = 0
            
            for json_file in json_files:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if isinstance(data, list) and data:
                        # Process arrow data
                        for arrow_data in data:
                            if self._insert_arrow_data(cursor, arrow_data):
                                imported += 1
                    
                    print(f"✅ Basic import from {json_file.name}")
                    
                except Exception as file_error:
                    print(f"⚠️  Error with {json_file.name}: {file_error}")
            
            conn.commit()
            conn.close()
            
            print(f"✅ Basic JSON import completed: {imported} arrows processed")
            return True
            
        except Exception as e:
            print(f"❌ Basic JSON import failed: {e}")
            if 'conn' in locals():
                conn.close()
            return False
    
    def _insert_arrow_data(self, cursor, arrow_data) -> bool:
        """Insert single arrow data record"""
        try:
            # Basic arrow insert - adapt based on your schema
            manufacturer = arrow_data.get('manufacturer', 'Unknown')
            model_name = arrow_data.get('model_name', 'Unknown')
            
            # Check if arrow already exists
            cursor.execute("""
                SELECT id FROM arrows 
                WHERE manufacturer = ? AND model_name = ?
                LIMIT 1
            """, (manufacturer, model_name))
            
            if cursor.fetchone():
                return False  # Already exists
            
            # Insert new arrow
            cursor.execute("""
                INSERT OR IGNORE INTO arrows 
                (manufacturer, model_name, material, description, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                manufacturer,
                model_name,
                arrow_data.get('material', ''),
                arrow_data.get('description', ''),
                datetime.now().isoformat()
            ))
            
            return cursor.rowcount > 0
            
        except Exception as e:
            print(f"⚠️  Error inserting arrow data: {e}")
            return False