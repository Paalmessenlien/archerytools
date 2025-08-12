#!/usr/bin/env python3
"""
Migration 006: Bow and Limb Manufacturer Integration
Adds bow and limb manufacturers from hardcoded frontend lists to the unified manufacturer system
"""

import sqlite3
import json
from datetime import datetime
from database_migration_manager import BaseMigration

class Migration006BowLimbManufacturers(BaseMigration):
    def __init__(self):
        super().__init__()
        self.version = "006"
        self.description = "Integrate bow and limb manufacturers into unified manufacturer system"
        self.dependencies = ["005"]
        self.environments = ['all']
    
    def up(self, db_path: str, environment: str) -> bool:
        """Add bow and limb manufacturers to unified manufacturer system"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            print("🏹 Adding bow and limb manufacturers to unified system...")
            
            # Define bow/limb manufacturers extracted from AddBowSetupModal.vue
            bow_manufacturers = {
                'compound_bows': [
                    'Hoyt', 'Mathews', 'PSE', 'Bowtech', 'Prime', 'Elite', 
                    'Bear', 'Diamond', 'Mission'
                ],
                'recurve_risers': [
                    'Hoyt', 'Win&Win', 'Uukha', 'Samick', 'Bernardini', 
                    'Border', 'Mybo'
                ],
                'recurve_limbs': [
                    'Hoyt', 'Win&Win', 'Uukha', 'Border', 'Samick', 
                    'SF Archery', 'Core', 'Fivics'
                ],
                'traditional_risers': [
                    'Samick', 'Bear', 'PSE', 'Martin', 'Black Widow'
                ],
                'traditional_limbs': [
                    'Samick', 'Bear', 'PSE', 'Martin', 'Black Widow'
                ],
                'longbows': [
                    'Howard Hill', 'Bear', 'Bodnik', 'Black Widow', 
                    'Great Plains', 'Three Rivers Archery', 'Martin', 'Samick'
                ]
            }
            
            # Get all unique manufacturer names
            all_bow_manufacturers = set()
            for category_list in bow_manufacturers.values():
                all_bow_manufacturers.update(category_list)
            
            print(f"📊 Found {len(all_bow_manufacturers)} unique bow/limb manufacturers")
            
            # Insert manufacturers into unified table
            manufacturer_map = {}
            inserted_count = 0
            updated_count = 0
            
            for manufacturer_name in sorted(all_bow_manufacturers):
                # Check if manufacturer already exists
                cursor.execute('SELECT id FROM manufacturers WHERE name = ?', (manufacturer_name,))
                existing = cursor.fetchone()
                
                if existing:
                    manufacturer_id = existing[0]
                    manufacturer_map[manufacturer_name] = manufacturer_id
                    updated_count += 1
                    print(f"   ✓ Found existing: {manufacturer_name}")
                else:
                    # Insert new manufacturer
                    cursor.execute('''
                        INSERT INTO manufacturers (name, is_active, description)
                        VALUES (?, ?, ?)
                    ''', (manufacturer_name, True, f"Bow/Limb manufacturer - added from bow setup system"))
                    
                    manufacturer_id = cursor.lastrowid
                    manufacturer_map[manufacturer_name] = manufacturer_id
                    inserted_count += 1
                    print(f"   + Added new: {manufacturer_name}")
            
            print(f"📈 Manufacturer summary: {inserted_count} new, {updated_count} existing")
            
            # Set up equipment category mappings
            print("🏷️ Setting up bow equipment category mappings...")
            
            category_mapping_count = 0
            for category, manufacturer_list in bow_manufacturers.items():
                print(f"   📂 Processing {category} ({len(manufacturer_list)} manufacturers)")
                
                for manufacturer_name in manufacturer_list:
                    manufacturer_id = manufacturer_map[manufacturer_name]
                    
                    # Insert or update equipment category mapping
                    cursor.execute('''
                        INSERT OR REPLACE INTO manufacturer_equipment_categories 
                        (manufacturer_id, category_name, is_supported, notes)
                        VALUES (?, ?, ?, ?)
                    ''', (manufacturer_id, category, True, f"Supports {category.replace('_', ' ')} - migrated from bow setup system"))
                    
                    category_mapping_count += 1
            
            print(f"🔗 Created {category_mapping_count} equipment category mappings")
            
            # Get final statistics
            cursor.execute('SELECT COUNT(*) FROM manufacturers')
            total_manufacturers = cursor.fetchone()[0]
            
            cursor.execute('''
                SELECT COUNT(*) FROM manufacturer_equipment_categories 
                WHERE category_name IN ('compound_bows', 'recurve_risers', 'recurve_limbs', 'traditional_risers', 'traditional_limbs', 'longbows')
            ''')
            bow_category_mappings = cursor.fetchone()[0]
            
            # Verify data integrity
            cursor.execute('''
                SELECT category_name, COUNT(*) 
                FROM manufacturer_equipment_categories 
                WHERE category_name IN ('compound_bows', 'recurve_risers', 'recurve_limbs', 'traditional_risers', 'traditional_limbs', 'longbows')
                GROUP BY category_name
            ''')
            category_stats = cursor.fetchall()
            
            conn.commit()
            conn.close()
            
            print(f"✅ Successfully integrated bow/limb manufacturers:")
            print(f"   📊 Total manufacturers in system: {total_manufacturers}")
            print(f"   🏹 Bow equipment category mappings: {bow_category_mappings}")
            print(f"   📈 Category breakdown:")
            for category, count in category_stats:
                print(f"      • {category.replace('_', ' ').title()}: {count} manufacturers")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to integrate bow/limb manufacturers: {e}")
            if conn:
                conn.rollback()
            return False
    
    def down(self, db_path: str, environment: str) -> bool:
        """Remove bow/limb manufacturer integrations"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            print("⚠️ Removing bow/limb manufacturer integrations...")
            
            # Remove bow equipment category mappings
            bow_categories = ['compound_bows', 'recurve_risers', 'recurve_limbs', 'traditional_risers', 'traditional_limbs', 'longbows']
            
            for category in bow_categories:
                cursor.execute('''
                    DELETE FROM manufacturer_equipment_categories 
                    WHERE category_name = ?
                ''', (category,))
                
            deleted_mappings = cursor.rowcount
            
            # Note: We don't remove the manufacturers themselves as they might be used by other systems
            # or have been manually added. Only remove the bow-specific category mappings.
            
            conn.commit()
            conn.close()
            
            print(f"✅ Successfully removed bow/limb manufacturer integrations:")
            print(f"   🗑️ Removed {deleted_mappings} bow equipment category mappings")
            print(f"   ℹ️ Note: Manufacturers remain in system for other equipment types")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to remove bow/limb manufacturer integrations: {e}")
            if conn:
                conn.rollback()
            return False

# Create the migration instance for discovery
migration = Migration006BowLimbManufacturers()