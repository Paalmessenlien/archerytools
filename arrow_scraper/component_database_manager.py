#!/usr/bin/env python3
"""
Component Database Management

This module handles the storage, retrieval, and management of arrow component
data in a SQLite database. It complements the arrow database with detailed
component specifications for inserts, points, nocks, etc.

Usage:
    python component_database_manager.py --import data/processed/components/tophat_archery_components_*.json
    python component_database_manager.py --stats
    python component_database_manager.py --search-components --category inserts --weight 30
"""

import sqlite3
import json
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
import glob

class ComponentDatabase:
    """Database management for arrow components"""
    
    def __init__(self, db_path: str = "component_database.db"):
        self.db_path = db_path
        self.logger = self._setup_logging()
        self.init_database()
        
    def _setup_logging(self) -> logging.Logger:
        """Set up logging"""
        logger = logging.getLogger("component_db")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
        
    def init_database(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Components table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS components (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                component_id TEXT UNIQUE NOT NULL,
                supplier TEXT NOT NULL,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                type TEXT,
                subcategory TEXT,
                material TEXT,
                weight_grain REAL,
                inner_diameter_inch REAL,
                inner_diameter_mm REAL,
                outer_diameter_inch REAL,
                outer_diameter_mm REAL,
                length_mm REAL,
                length_inch REAL,
                thread_specification TEXT,
                color TEXT,
                finish TEXT,
                usage_type TEXT,
                price TEXT,
                availability TEXT,
                description TEXT,
                image_url TEXT,
                source_url TEXT,
                extracted_at TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Component weight options (for components with multiple weight choices)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS component_weight_options (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                component_id TEXT,
                weight_grain REAL,
                FOREIGN KEY (component_id) REFERENCES components (component_id)
            )
        ''')
        
        # Component compatibility (arrow models/shafts this component fits)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS component_compatibility (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                component_id TEXT,
                compatibility_info TEXT,
                FOREIGN KEY (component_id) REFERENCES components (component_id)
            )
        ''')
        
        # Create indexes for better query performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_components_category ON components (category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_components_type ON components (type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_components_weight ON components (weight_grain)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_components_inner_dia ON components (inner_diameter_inch)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_components_supplier ON components (supplier)')
        
        conn.commit()
        conn.close()
        
    def import_components_from_json(self, json_file: str) -> int:
        """Import components from JSON file"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            components = data.get('components', [])
            supplier = data.get('supplier', 'Unknown')
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            imported_count = 0
            
            for comp_data in components:
                try:
                    # Insert component
                    cursor.execute('''
                        INSERT OR REPLACE INTO components (
                            component_id, supplier, name, category, type, subcategory,
                            material, weight_grain, inner_diameter_inch, inner_diameter_mm,
                            outer_diameter_inch, outer_diameter_mm, length_mm, length_inch,
                            thread_specification, color, finish, usage_type, price,
                            availability, description, image_url, source_url, extracted_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        comp_data.get('component_id'),
                        comp_data.get('supplier'),
                        comp_data.get('name'),
                        comp_data.get('category'),
                        comp_data.get('type'),
                        comp_data.get('subcategory'),
                        comp_data.get('material'),
                        comp_data.get('weight_grain'),
                        comp_data.get('inner_diameter_inch'),
                        comp_data.get('inner_diameter_mm'),
                        comp_data.get('outer_diameter_inch'),
                        comp_data.get('outer_diameter_mm'),
                        comp_data.get('length_mm'),
                        comp_data.get('length_inch'),
                        comp_data.get('thread_specification'),
                        comp_data.get('color'),
                        comp_data.get('finish'),
                        comp_data.get('usage_type'),
                        comp_data.get('price'),
                        comp_data.get('availability'),
                        comp_data.get('description'),
                        comp_data.get('image_url'),
                        comp_data.get('source_url'),
                        comp_data.get('extracted_at')
                    ))
                    
                    component_id = comp_data.get('component_id')
                    
                    # Clear existing related data
                    cursor.execute('DELETE FROM component_weight_options WHERE component_id = ?', (component_id,))
                    cursor.execute('DELETE FROM component_compatibility WHERE component_id = ?', (component_id,))
                    
                    # Insert weight options if multiple weights available
                    weight_options = comp_data.get('weight_options')
                    if weight_options and isinstance(weight_options, list):
                        for weight in weight_options:
                            cursor.execute('''
                                INSERT INTO component_weight_options (component_id, weight_grain)
                                VALUES (?, ?)
                            ''', (component_id, weight))
                    
                    # Insert compatibility information
                    compatibility = comp_data.get('compatibility')
                    if compatibility and isinstance(compatibility, list):
                        for comp_info in compatibility:
                            cursor.execute('''
                                INSERT INTO component_compatibility (component_id, compatibility_info)
                                VALUES (?, ?)
                            ''', (component_id, comp_info))
                    
                    imported_count += 1
                    
                except Exception as e:
                    self.logger.warning(f"Error importing component {comp_data.get('name', 'unknown')}: {e}")
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"✅ Imported {imported_count} components from {json_file}")
            return imported_count
            
        except Exception as e:
            self.logger.error(f"Error importing components from {json_file}: {e}")
            return 0
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Total components
        cursor.execute('SELECT COUNT(*) FROM components')
        stats['total_components'] = cursor.fetchone()[0]
        
        # Components by category
        cursor.execute('''
            SELECT category, COUNT(*) 
            FROM components 
            GROUP BY category 
            ORDER BY COUNT(*) DESC
        ''')
        stats['by_category'] = dict(cursor.fetchall())
        
        # Components by supplier
        cursor.execute('''
            SELECT supplier, COUNT(*) 
            FROM components 
            GROUP BY supplier 
            ORDER BY COUNT(*) DESC
        ''')
        stats['by_supplier'] = dict(cursor.fetchall())
        
        # Weight range
        cursor.execute('SELECT MIN(weight_grain), MAX(weight_grain) FROM components WHERE weight_grain IS NOT NULL')
        weight_range = cursor.fetchone()
        stats['weight_range'] = {
            'min': weight_range[0],
            'max': weight_range[1]
        } if weight_range[0] is not None else None
        
        # Diameter ranges
        cursor.execute('SELECT MIN(inner_diameter_inch), MAX(inner_diameter_inch) FROM components WHERE inner_diameter_inch IS NOT NULL')
        inner_dia_range = cursor.fetchone()
        stats['inner_diameter_range'] = {
            'min': inner_dia_range[0],
            'max': inner_dia_range[1]
        } if inner_dia_range[0] is not None else None
        
        conn.close()
        return stats

def main():
    """CLI interface for component database"""
    parser = argparse.ArgumentParser(description="Component database management")
    parser.add_argument("--import", dest="import_file", help="Import components from JSON file")
    parser.add_argument("--import-all", help="Import all JSON files from directory")
    parser.add_argument("--stats", action="store_true", help="Show database statistics")
    
    args = parser.parse_args()
    
    db = ComponentDatabase()
    
    if args.import_file:
        db.import_components_from_json(args.import_file)
        
    elif args.import_all:
        json_files = glob.glob(f"{args.import_all}/*.json")
        total_imported = 0
        for json_file in json_files:
            imported = db.import_components_from_json(json_file)
            total_imported += imported
        print(f"Total imported: {total_imported} components from {len(json_files)} files")
        
    elif args.stats:
        stats = db.get_database_stats()
        print("📊 Component Database Statistics")
        print("=" * 40)
        print(f"Total Components: {stats['total_components']}")
        
        if stats['by_category']:
            print("\nBy Category:")
            for category, count in stats['by_category'].items():
                print(f"  {category}: {count}")
                
        if stats['by_supplier']:
            print("\nBy Supplier:")
            for supplier, count in stats['by_supplier'].items():
                print(f"  {supplier}: {count}")
                
        if stats['weight_range']:
            print(f"\nWeight Range: {stats['weight_range']['min']}-{stats['weight_range']['max']} grain")
            
        if stats['inner_diameter_range']:
            print(f"Inner Diameter Range: {stats['inner_diameter_range']['min']}-{stats['inner_diameter_range']['max']}\"")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()