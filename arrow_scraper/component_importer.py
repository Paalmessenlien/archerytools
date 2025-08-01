#!/usr/bin/env python3
"""
Component Importer for Arrow Scraper
Imports component data from JSON files into the database, similar to arrow importing
"""

import json
import sys
import sqlite3
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import threading

from component_database import ComponentDatabase

class ComponentImporter:
    """Import components from JSON files into database"""
    
    def __init__(self, db_path: str = "arrow_database.db"):
        self.db_path = Path(db_path)
        self.component_db = ComponentDatabase(db_path)
        self.processed_dir = Path("data/processed/components")
        
    def get_all_component_files(self) -> List[Path]:
        """Get all component JSON files"""
        if not self.processed_dir.exists():
            print(f"⚠️  Components directory does not exist: {self.processed_dir}")
            return []
        
        json_files = list(self.processed_dir.glob("*.json"))
        return sorted(json_files)
    
    def import_component_file(self, json_file: Path) -> int:
        """Import components from a single JSON file"""
        try:
            print(f"📦 Processing: {json_file.name}")
            
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'components' not in data:
                print(f"⚠️  No 'components' field in {json_file.name}")
                return 0
            
            components = data['components']
            if not components:
                print(f"⚠️  No components found in {json_file.name}")
                return 0
            
            manufacturer = data.get('manufacturer', 'Unknown')
            component_type = data.get('component_type', 'unknown')
            
            print(f"   📋 Manufacturer: {manufacturer}")
            print(f"   🧩 Component Type: {component_type}")
            print(f"   📊 Components: {len(components)}")
            
            imported_count = 0
            for component in components:
                try:
                    component_id = self.component_db.add_component(
                        category_name=component_type,
                        manufacturer=component.get('manufacturer', manufacturer),
                        model_name=component.get('model_name', 'Unknown Model'),
                        specifications=component.get('specifications', {}),
                        image_url=component.get('image_url'),
                        local_image_path=component.get('local_image_path'),
                        price_range=component.get('price_range'),
                        description=component.get('description'),
                        source_url=component.get('source_url'),
                        scraped_at=component.get('scraped_at', datetime.now().isoformat())
                    )
                    
                    if component_id:
                        imported_count += 1
                        
                except Exception as e:
                    print(f"⚠️  Error importing component {component.get('model_name', 'Unknown')}: {e}")
                    continue
            
            print(f"   ✅ Imported: {imported_count}/{len(components)} components")
            return imported_count
            
        except Exception as e:
            print(f"❌ Error processing {json_file.name}: {e}")
            return 0
    
    def import_all_components(self, force_rebuild: bool = False) -> bool:
        """Import all component JSON files into database"""
        
        print("📦 Starting component import from JSON files...")
        print("=" * 60)
        
        # Get component files
        json_files = self.get_all_component_files()
        
        if not json_files:
            print("ℹ️  No component JSON files found to import")
            return True
        
        print(f"📊 Found {len(json_files)} component files to process")
        
        # Check if we should skip import (similar to arrow logic)
        if not force_rebuild:
            try:
                stats = self.component_db.get_component_statistics()
                existing_components = stats.get('total_components', 0)
                if existing_components > 0:
                    print(f"ℹ️  Database already contains {existing_components} components")
                    print("   Use force_rebuild=True to reimport all components")
                    return True
            except Exception as e:
                print(f"⚠️  Could not check existing components: {e}")
        
        # Clear existing components if force rebuild
        if force_rebuild:
            print("🗑️  Force rebuild: clearing existing component data...")
            try:
                conn = self.component_db.get_connection()
                cursor = conn.cursor()
                
                # Clear in correct order due to foreign keys
                cursor.execute("DELETE FROM arrow_component_compatibility")
                cursor.execute("DELETE FROM components")
                
                conn.commit()
                print("✅ Existing component data cleared")
            except Exception as e:
                print(f"⚠️  Error clearing existing data: {e}")
        
        total_imported = 0
        successful_files = 0
        
        # Process each file
        for json_file in json_files:
            imported = self.import_component_file(json_file)
            if imported > 0:
                successful_files += 1
                total_imported += imported
            print()  # Empty line between files
        
        # Summary
        print("=" * 60)
        print("📋 COMPONENT IMPORT SUMMARY")
        print("=" * 60)
        print(f"📁 Files processed: {successful_files}/{len(json_files)}")
        print(f"🧩 Total components imported: {total_imported}")
        
        if successful_files > 0:
            # Show final statistics
            try:
                stats = self.component_db.get_component_statistics()
                print(f"💾 Database now contains:")
                print(f"   • {stats.get('total_components', 0)} components")
                print(f"   • {stats.get('total_categories', 0)} categories")
                print(f"   • {stats.get('total_manufacturers', 0)} component manufacturers")
            except Exception as e:
                print(f"💾 Database summary unavailable: {e}")
        
        print()
        
        if total_imported > 0:
            print("🎯 Component import completed successfully!")
            return True
        else:
            print("⚠️  No components were imported")
            return False

def main():
    """Main function for standalone component import"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Import components from JSON files")
    parser.add_argument("--force", action="store_true", help="Force rebuild: clear existing components")
    parser.add_argument("--db", default="arrow_database.db", help="Database file path")
    
    args = parser.parse_args()
    
    # Create importer
    importer = ComponentImporter(args.db)
    
    # Import components
    success = importer.import_all_components(force_rebuild=args.force)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()