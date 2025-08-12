#!/usr/bin/env python3
"""
Migration 005: Unified Manufacturer Management System
Creates centralized manufacturer management with equipment category support
"""

import sqlite3
import json
from datetime import datetime
from database_migration_manager import BaseMigration

class Migration005UnifiedManufacturers(BaseMigration):
    def __init__(self):
        super().__init__()
        self.version = "005"
        self.description = "Create unified manufacturer management system"
        self.dependencies = ["004"]
        self.environments = ['all']
    
    def up(self, db_path: str, environment: str) -> bool:
        """Create unified manufacturer tables and migrate existing data"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            print("🏭 Creating unified manufacturer management tables...")
            
            # Create manufacturers table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS manufacturers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                website_url TEXT,
                logo_url TEXT,
                description TEXT,
                country TEXT,
                established_year INTEGER,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Create manufacturer equipment categories mapping
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS manufacturer_equipment_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                manufacturer_id INTEGER NOT NULL,
                category_name TEXT NOT NULL,
                is_supported BOOLEAN DEFAULT TRUE,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (manufacturer_id) REFERENCES manufacturers (id) ON DELETE CASCADE,
                UNIQUE(manufacturer_id, category_name)
            )
            ''')
            
            print("📊 Extracting and consolidating manufacturer data...")
            
            # Extract unique manufacturers from arrows table
            cursor.execute('SELECT DISTINCT manufacturer FROM arrows WHERE manufacturer IS NOT NULL AND manufacturer != ""')
            arrow_manufacturers = [row[0] for row in cursor.fetchall()]
            
            # Extract unique manufacturers from equipment table  
            cursor.execute('SELECT DISTINCT manufacturer FROM equipment WHERE manufacturer IS NOT NULL AND manufacturer != ""')
            equipment_manufacturers = [row[0] for row in cursor.fetchall()]
            
            # Combine and deduplicate manufacturers
            all_manufacturers = list(set(arrow_manufacturers + equipment_manufacturers))
            
            print(f"📋 Found {len(arrow_manufacturers)} arrow manufacturers, {len(equipment_manufacturers)} equipment manufacturers")
            print(f"🔄 Consolidating into {len(all_manufacturers)} unique manufacturers")
            
            # Insert consolidated manufacturers
            manufacturer_map = {}
            for manufacturer_name in sorted(all_manufacturers):
                # Clean up manufacturer name
                cleaned_name = manufacturer_name.strip()
                if not cleaned_name:
                    continue
                    
                cursor.execute('''
                    INSERT OR IGNORE INTO manufacturers (name, is_active)
                    VALUES (?, ?)
                ''', (cleaned_name, True))
                
                # Get the manufacturer ID
                cursor.execute('SELECT id FROM manufacturers WHERE name = ?', (cleaned_name,))
                manufacturer_id = cursor.fetchone()[0]
                manufacturer_map[manufacturer_name] = manufacturer_id
            
            print("🏷️ Setting up equipment category mappings...")
            
            # Set up equipment category mappings based on existing data
            equipment_categories = ['arrows', 'strings', 'sights', 'stabilizers', 'arrow_rests', 'weights']
            
            for manufacturer_name, manufacturer_id in manufacturer_map.items():
                # Check if manufacturer makes arrows
                cursor.execute('SELECT COUNT(*) FROM arrows WHERE manufacturer = ?', (manufacturer_name,))
                has_arrows = cursor.fetchone()[0] > 0
                
                # Check if manufacturer makes equipment and what types
                cursor.execute('''
                    SELECT DISTINCT ec.name 
                    FROM equipment e 
                    JOIN equipment_categories ec ON e.category_id = ec.id 
                    WHERE e.manufacturer = ?
                ''', (manufacturer_name,))
                equipment_types = [row[0].lower().replace(' ', '_') for row in cursor.fetchall()]
                
                # Insert category mappings
                for category in equipment_categories:
                    is_supported = False
                    notes = ""
                    
                    if category == 'arrows' and has_arrows:
                        is_supported = True
                        notes = "Auto-detected from arrow database"
                    elif category in equipment_types:
                        is_supported = True
                        notes = "Auto-detected from equipment database"
                    
                    cursor.execute('''
                        INSERT OR IGNORE INTO manufacturer_equipment_categories 
                        (manufacturer_id, category_name, is_supported, notes)
                        VALUES (?, ?, ?, ?)
                    ''', (manufacturer_id, category, is_supported, notes))
            
            print("🔗 Adding manufacturer_id columns to existing tables...")
            
            # Add manufacturer_id column to arrows table
            try:
                cursor.execute('ALTER TABLE arrows ADD COLUMN manufacturer_id INTEGER REFERENCES manufacturers(id)')
                print("   ✅ Added manufacturer_id to arrows table")
            except sqlite3.OperationalError as e:
                if "duplicate column name" not in str(e).lower():
                    raise
                print("   ⚠️ manufacturer_id column already exists in arrows table")
            
            # Add manufacturer_id column to equipment table
            try:
                cursor.execute('ALTER TABLE equipment ADD COLUMN manufacturer_id INTEGER REFERENCES manufacturers(id)')
                print("   ✅ Added manufacturer_id to equipment table")
            except sqlite3.OperationalError as e:
                if "duplicate column name" not in str(e).lower():
                    raise
                print("   ⚠️ manufacturer_id column already exists in equipment table")
            
            print("🔄 Updating foreign key references...")
            
            # Update arrows table with manufacturer_id references
            for manufacturer_name, manufacturer_id in manufacturer_map.items():
                cursor.execute('''
                    UPDATE arrows 
                    SET manufacturer_id = ? 
                    WHERE manufacturer = ? AND manufacturer_id IS NULL
                ''', (manufacturer_id, manufacturer_name))
            
            # Update equipment table with manufacturer_id references
            for manufacturer_name, manufacturer_id in manufacturer_map.items():
                cursor.execute('''
                    UPDATE equipment 
                    SET manufacturer_id = ? 
                    WHERE manufacturer = ? AND manufacturer_id IS NULL
                ''', (manufacturer_id, manufacturer_name))
            
            # Get statistics
            cursor.execute('SELECT COUNT(*) FROM manufacturers')
            total_manufacturers = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM manufacturer_equipment_categories WHERE is_supported = 1')
            total_supported_categories = cursor.fetchone()[0]
            
            conn.commit()
            conn.close()
            
            print(f"✅ Successfully created unified manufacturer management system:")
            print(f"   📊 {total_manufacturers} manufacturers")
            print(f"   🏷️ {total_supported_categories} supported equipment categories")
            print(f"   🔗 Updated foreign key references in arrows and equipment tables")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to create unified manufacturer system: {e}")
            if conn:
                conn.rollback()
            return False
    
    def down(self, db_path: str, environment: str) -> bool:
        """Remove unified manufacturer tables (WARNING: This will lose manufacturer data)"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            print("⚠️ Removing unified manufacturer management system...")
            
            # Remove manufacturer_id columns from existing tables
            print("🔗 Removing manufacturer_id foreign key columns...")
            
            # For arrows table - create new table without manufacturer_id
            cursor.execute('''
                CREATE TABLE arrows_backup AS 
                SELECT id, manufacturer, model_name, material, carbon_content, arrow_type, 
                       recommended_use, price_range, straightness_tolerance, description,
                       image_url, local_image_path, scraped_at, created_at
                FROM arrows
            ''')
            
            cursor.execute('DROP TABLE arrows')
            cursor.execute('ALTER TABLE arrows_backup RENAME TO arrows')
            
            # For equipment table - create new table without manufacturer_id  
            cursor.execute('''
                CREATE TABLE equipment_backup AS
                SELECT id, category_id, manufacturer, model_name, specifications,
                       compatibility_rules, weight_grams, price_range, image_url,
                       local_image_path, description, source_url, scraped_at, created_at
                FROM equipment
            ''')
            
            cursor.execute('DROP TABLE equipment')
            cursor.execute('ALTER TABLE equipment_backup RENAME TO equipment')
            
            # Drop unified manufacturer tables
            cursor.execute('DROP TABLE IF EXISTS manufacturer_equipment_categories')
            cursor.execute('DROP TABLE IF EXISTS manufacturers')
            
            conn.commit()
            conn.close()
            
            print("✅ Successfully removed unified manufacturer management system")
            print("⚠️ Note: Manufacturer data has been restored to original string format")
            return True
            
        except Exception as e:
            print(f"❌ Failed to remove unified manufacturer system: {e}")
            return False

# Create the migration instance for discovery
migration = Migration005UnifiedManufacturers()