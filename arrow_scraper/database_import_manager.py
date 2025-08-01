#!/usr/bin/env python3
"""
Database Import Manager for Arrow Scraper
Handles importing arrow data from JSON files to database during server startup
"""

import json
import sqlite3
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import hashlib
import logging

class DatabaseImportManager:
    """Manages importing arrow data from JSON files to SQLite database"""
    
    def __init__(self, database_path: str = "arrow_database.db", processed_data_dir: str = "data/processed"):
        """
        Initialize the database import manager
        
        Args:
            database_path: Path to the SQLite database
            processed_data_dir: Directory containing processed JSON files
        """
        self.database_path = database_path
        self.processed_data_dir = Path(processed_data_dir)
        self.logger = logging.getLogger(__name__)
        
        # Set up logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        
    def get_json_files(self) -> List[Tuple[Path, datetime, str]]:
        """
        Get all JSON files from processed directory with metadata
        
        Returns:
            List of tuples (file_path, modification_time, manufacturer_name)
        """
        json_files = []
        
        if not self.processed_data_dir.exists():
            self.logger.warning(f"Processed data directory does not exist: {self.processed_data_dir}")
            return json_files
        
        # Find all JSON files (both learn and update patterns)
        for json_file in self.processed_data_dir.glob("*.json"):
            if json_file.is_file():
                try:
                    # Get modification time
                    mod_time = datetime.fromtimestamp(json_file.stat().st_mtime)
                    
                    # Extract manufacturer name from filename
                    # Pattern: Manufacturer_Name_type_YYYYMMDD_HHMMSS.json
                    filename = json_file.stem
                    
                    # Handle different naming patterns
                    if "_learn_" in filename:
                        manufacturer = filename.split("_learn_")[0].replace("_", " ")
                    elif "_update_" in filename:
                        manufacturer = filename.split("_update_")[0].replace("_", " ")
                    elif "_test_" in filename:
                        manufacturer = filename.split("_test_")[0].replace("_", " ")
                    else:
                        # Fallback: use first part before underscore
                        manufacturer = filename.split("_")[0].replace("_", " ")
                    
                    json_files.append((json_file, mod_time, manufacturer))
                    
                except Exception as e:
                    self.logger.warning(f"Error processing file {json_file}: {e}")
        
        # Sort by modification time (newest first)
        json_files.sort(key=lambda x: x[1], reverse=True)
        
        return json_files
    
    def get_database_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about current database contents
        
        Returns:
            Dictionary with database statistics and last modified info
        """
        if not os.path.exists(self.database_path):
            return {
                "exists": False,
                "arrow_count": 0,
                "manufacturer_count": 0,
                "last_modified": None,
                "manufacturers": []
            }
        
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Get arrow count
            cursor.execute("SELECT COUNT(*) FROM arrows")
            arrow_count = cursor.fetchone()[0]
            
            # Get manufacturer count and list
            cursor.execute("SELECT DISTINCT manufacturer FROM arrows ORDER BY manufacturer")
            manufacturers = [row[0] for row in cursor.fetchall()]
            manufacturer_count = len(manufacturers)
            
            # Get database file modification time
            db_stat = os.stat(self.database_path)
            last_modified = datetime.fromtimestamp(db_stat.st_mtime)
            
            conn.close()
            
            return {
                "exists": True,
                "arrow_count": arrow_count,
                "manufacturer_count": manufacturer_count,
                "last_modified": last_modified,
                "manufacturers": manufacturers
            }
            
        except Exception as e:
            self.logger.error(f"Error reading database metadata: {e}")
            return {
                "exists": False,
                "arrow_count": 0,
                "manufacturer_count": 0,
                "last_modified": None,
                "manufacturers": []
            }
    
    def load_json_data(self, json_file: Path) -> Optional[Dict[str, Any]]:
        """
        Load and validate JSON data from file
        
        Args:
            json_file: Path to JSON file
            
        Returns:
            Loaded JSON data or None if invalid
        """
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate required fields
            if not isinstance(data, dict):
                self.logger.warning(f"Invalid JSON structure in {json_file}")
                return None
            
            if "manufacturer" not in data or "arrows" not in data:
                self.logger.warning(f"Missing required fields in {json_file}")
                return None
            
            if not isinstance(data["arrows"], list):
                self.logger.warning(f"Invalid arrows data in {json_file}")
                return None
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error loading JSON file {json_file}: {e}")
            return None
    
    def get_data_hash(self, data: Dict[str, Any]) -> str:
        """
        Generate hash of arrow data for comparison
        
        Args:
            data: Arrow data dictionary
            
        Returns:
            SHA256 hash of the data
        """
        # Create a consistent string representation for hashing
        # Focus on arrow specifications, ignoring metadata like scraped_at
        hash_data = {
            "manufacturer": data.get("manufacturer"),
            "arrows": []
        }
        
        for arrow in data.get("arrows", []):
            arrow_hash_data = {
                "model_name": arrow.get("model_name"),
                "spine_specifications": arrow.get("spine_specifications", []),
                "material": arrow.get("material"),
                "arrow_type": arrow.get("arrow_type"),
                "description": arrow.get("description")
            }
            hash_data["arrows"].append(arrow_hash_data)
        
        # Sort arrows by model name for consistent hashing
        hash_data["arrows"].sort(key=lambda x: x.get("model_name", ""))
        
        # Generate hash
        data_str = json.dumps(hash_data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(data_str.encode('utf-8')).hexdigest()
    
    def clear_manufacturer_data(self, manufacturer: str):
        """
        Clear existing data for a manufacturer from database
        
        Args:
            manufacturer: Manufacturer name to clear
        """
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Get arrow IDs for the manufacturer first
            cursor.execute("SELECT id FROM arrows WHERE manufacturer = ?", (manufacturer,))
            arrow_ids = [row[0] for row in cursor.fetchall()]
            
            if arrow_ids:
                # Delete spine specifications first (foreign key constraint)
                placeholders = ','.join('?' * len(arrow_ids))
                cursor.execute(f"""
                    DELETE FROM spine_specifications 
                    WHERE arrow_id IN ({placeholders})
                """, arrow_ids)
                
                # Delete arrows
                cursor.execute("DELETE FROM arrows WHERE manufacturer = ?", (manufacturer,))
                
                deleted_arrows = cursor.rowcount
                conn.commit()
                
                if deleted_arrows > 0:
                    self.logger.info(f"Cleared {deleted_arrows} existing arrows for {manufacturer}")
            
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error clearing manufacturer data for {manufacturer}: {e}")
    
    def import_arrow_data(self, data: Dict[str, Any]) -> int:
        """
        Import arrow data into database
        
        Args:
            data: Arrow data from JSON file
            
        Returns:
            Number of arrows imported
        """
        if not data or "arrows" not in data:
            return 0
        
        manufacturer = data.get("manufacturer", "Unknown")
        arrows_imported = 0
        
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            for arrow in data["arrows"]:
                try:
                    # Insert arrow
                    cursor.execute("""
                        INSERT INTO arrows (
                            manufacturer, model_name, material, arrow_type, 
                            description, source_url, image_url,
                            created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        manufacturer,
                        arrow.get("model_name", ""),
                        self._normalize_material(arrow.get("material")),
                        arrow.get("arrow_type", "target"),
                        arrow.get("description", ""),
                        arrow.get("source_url", ""),
                        arrow.get("primary_image_url", ""),
                        datetime.now().isoformat()
                    ))
                    
                    arrow_id = cursor.lastrowid
                    
                    # Insert spine specifications
                    spine_specs = arrow.get("spine_specifications", [])
                    for spec in spine_specs:
                        if isinstance(spec, dict) and "spine" in spec:
                            cursor.execute("""
                                INSERT INTO spine_specifications (
                                    arrow_id, spine, outer_diameter, inner_diameter,
                                    gpi_weight
                                ) VALUES (?, ?, ?, ?, ?)
                            """, (
                                arrow_id,
                                spec.get("spine"),
                                spec.get("outer_diameter"),
                                spec.get("inner_diameter"),
                                spec.get("gpi_weight")
                            ))
                    
                    arrows_imported += 1
                    
                except Exception as e:
                    self.logger.warning(f"Error importing arrow {arrow.get('model_name', 'Unknown')}: {e}")
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Database error during import: {e}")
        
        return arrows_imported
    
    def _normalize_material(self, material: Optional[str]) -> str:
        """Normalize material string to standard format"""
        if not material:
            return "Carbon"
        
        material_lower = material.lower()
        
        if "wood" in material_lower or "cedar" in material_lower:
            return "Wood"
        elif "aluminum" in material_lower and "carbon" in material_lower:
            return "Carbon / Aluminum"
        elif "aluminum" in material_lower or "alloy" in material_lower:
            return "Aluminum"
        else:
            return "Carbon"
    
    def _classify_diameter(self, inner_diameter: Optional[float], outer_diameter: Optional[float]) -> str:
        """Classify arrow diameter into category"""
        diameter = inner_diameter or outer_diameter
        
        if not diameter:
            return "Standard target"
        
        if diameter < 0.200:
            return "Ultra-thin"
        elif diameter < 0.220:
            return "Thin"
        elif diameter < 0.250:
            return "Small hunting"
        elif diameter < 0.270:
            return "Standard target"
        elif diameter < 0.320:
            return "Standard hunting"
        elif diameter < 0.360:
            return "Large hunting"
        else:
            return "Heavy hunting"
    
    def check_for_updates(self) -> Dict[str, Any]:
        """
        Check if database needs updates based on JSON files
        
        Returns:
            Dictionary with update status and recommendations
        """
        self.logger.info("🔍 Checking for database updates...")
        
        json_files = self.get_json_files()
        db_metadata = self.get_database_metadata()
        
        update_info = {
            "needs_update": False,
            "reason": "",
            "json_files_found": len(json_files),
            "database_exists": db_metadata["exists"],
            "database_arrow_count": db_metadata["arrow_count"],
            "recommendations": []
        }
        
        if not db_metadata["exists"]:
            update_info["needs_update"] = True
            update_info["reason"] = "Database does not exist"
            update_info["recommendations"].append("Create new database from JSON files")
            
        elif len(json_files) == 0:
            update_info["reason"] = "No JSON files found in processed directory"
            update_info["recommendations"].append("No updates needed - no source data available")
            
        elif db_metadata["arrow_count"] == 0:
            update_info["needs_update"] = True
            update_info["reason"] = "Database exists but is empty"
            update_info["recommendations"].append("Import all JSON files to populate database")
            
        else:
            # Check if any JSON files are newer than database
            newest_json = max(json_files, key=lambda x: x[1])[1] if json_files else None
            
            if newest_json and db_metadata["last_modified"] and newest_json > db_metadata["last_modified"]:
                update_info["needs_update"] = True
                update_info["reason"] = f"JSON files newer than database (newest: {newest_json}, db: {db_metadata['last_modified']})"
                update_info["recommendations"].append("Update database with newer JSON data")
            else:
                update_info["reason"] = "Database appears up to date"
                update_info["recommendations"].append("No updates needed")
        
        return update_info
    
    def import_all_json_files(self, force_update: bool = False) -> Dict[str, Any]:
        """
        Import all JSON files to database
        
        Args:
            force_update: If True, clear existing data before import
            
        Returns:
            Import results summary
        """
        self.logger.info("📦 Starting database import from JSON files...")
        
        json_files = self.get_json_files()
        
        if not json_files:
            self.logger.warning("No JSON files found to import")
            return {
                "success": True,
                "files_processed": 0,
                "arrows_imported": 0,
                "manufacturers_updated": 0,
                "errors": []
            }
        
        results = {
            "success": True,
            "files_processed": 0,
            "arrows_imported": 0,
            "manufacturers_updated": set(),
            "errors": []
        }
        
        # Process each manufacturer (use latest file for each)
        manufacturer_files = {}
        for json_file, mod_time, manufacturer in json_files:
            if manufacturer not in manufacturer_files or mod_time > manufacturer_files[manufacturer][1]:
                manufacturer_files[manufacturer] = (json_file, mod_time)
        
        self.logger.info(f"Found {len(manufacturer_files)} manufacturers to import: {list(manufacturer_files.keys())}")
        
        for manufacturer, (json_file, mod_time) in manufacturer_files.items():
            try:
                self.logger.info(f"📋 Processing {manufacturer} from {json_file.name}")
                
                # Load JSON data
                data = self.load_json_data(json_file)
                if not data:
                    results["errors"].append(f"Failed to load {json_file}")
                    continue
                
                # Clear existing data for this manufacturer if force_update or new data
                if force_update:
                    self.clear_manufacturer_data(manufacturer)
                
                # Import arrow data
                imported_count = self.import_arrow_data(data)
                
                if imported_count > 0:
                    results["arrows_imported"] += imported_count
                    results["manufacturers_updated"].add(manufacturer)
                    self.logger.info(f"✅ Imported {imported_count} arrows for {manufacturer}")
                else:
                    self.logger.warning(f"⚠️  No arrows imported for {manufacturer}")
                
                results["files_processed"] += 1
                
            except Exception as e:
                error_msg = f"Error processing {manufacturer}: {e}"
                self.logger.error(error_msg)
                results["errors"].append(error_msg)
                results["success"] = False
        
        # Convert set to count for final results
        results["manufacturers_updated"] = len(results["manufacturers_updated"])
        
        self.logger.info(f"🎯 Import complete: {results['files_processed']} files, "
                        f"{results['arrows_imported']} arrows, "
                        f"{results['manufacturers_updated']} manufacturers")
        
        if results["errors"]:
            self.logger.warning(f"⚠️  {len(results['errors'])} errors occurred during import")
        
        return results
    
    def run_startup_import(self) -> bool:
        """
        Run database import process during server startup
        
        Returns:
            True if import successful or not needed, False if critical error
        """
        try:
            self.logger.info("🚀 Running startup database import check...")
            
            # Check if updates are needed
            update_info = self.check_for_updates()
            
            if update_info["needs_update"]:
                self.logger.info(f"📥 Database update needed: {update_info['reason']}")
                
                # Run import
                results = self.import_all_json_files(force_update=True)
                
                if results["success"]:
                    self.logger.info("✅ Database import completed successfully")
                    return True
                else:
                    self.logger.error("❌ Database import failed")
                    return False
            else:
                self.logger.info(f"✅ Database is up to date: {update_info['reason']}")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Critical error during startup import: {e}")
            return False


def main():
    """Test the database import manager"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Database Import Manager")
    parser.add_argument("--check", action="store_true", help="Check for updates only")
    parser.add_argument("--import-all", action="store_true", help="Import all JSON files")
    parser.add_argument("--force", action="store_true", help="Force update (clear existing data)")
    parser.add_argument("--database", default="arrow_database.db", help="Database path")
    parser.add_argument("--data-dir", default="data/processed", help="Processed data directory")
    
    args = parser.parse_args()
    
    manager = DatabaseImportManager(args.database, args.data_dir)
    
    if args.check:
        update_info = manager.check_for_updates()
        print(f"Database exists: {update_info['database_exists']}")
        print(f"Arrow count: {update_info['database_arrow_count']}")
        print(f"JSON files found: {update_info['json_files_found']}")
        print(f"Needs update: {update_info['needs_update']}")
        print(f"Reason: {update_info['reason']}")
        print("Recommendations:")
        for rec in update_info['recommendations']:
            print(f"  - {rec}")
    
    elif args.import_all or args.force:
        results = manager.import_all_json_files(force_update=args.force)
        print(f"Success: {results['success']}")
        print(f"Files processed: {results['files_processed']}")
        print(f"Arrows imported: {results['arrows_imported']}")
        print(f"Manufacturers updated: {results['manufacturers_updated']}")
        if results['errors']:
            print("Errors:")
            for error in results['errors']:
                print(f"  - {error}")
    
    else:
        # Run startup import
        success = manager.run_startup_import()
        exit(0 if success else 1)


if __name__ == "__main__":
    main()