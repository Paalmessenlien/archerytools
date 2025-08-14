#!/usr/bin/env python3
"""
Migration 019: Import existing manufacturers from bow setups
This migration extracts all unique manufacturers from the bow_setups table
and imports them into the manufacturers table with appropriate categories.
"""

import sqlite3
import json
from database_migration_manager import BaseMigration

class Migration019ImportBowSetupManufacturers(BaseMigration):
    def __init__(self):
        super().__init__()
        self.version = "019"
        self.description = "Import existing manufacturers from bow setups"
        self.dependencies = ["018"]
        self.environments = ['all']
        self.target_database = 'arrow'  # We're updating the arrow database
    
    def up(self, db_path: str, environment: str) -> bool:
        """Import manufacturers from bow setups"""
        try:
            # Get user database path for reading bow setups
            user_db_path = self._get_user_database_path(db_path)
            if not user_db_path:
                print("❌ Could not find user database")
                return False
            
            # Connect to both databases
            arrow_conn = sqlite3.connect(db_path)
            arrow_conn.row_factory = sqlite3.Row
            arrow_cursor = arrow_conn.cursor()
            
            user_conn = sqlite3.connect(user_db_path)
            user_conn.row_factory = sqlite3.Row
            user_cursor = user_conn.cursor()
            
            print("🔄 Importing manufacturers from bow setups...")
            
            # Extract unique manufacturers from bow setups
            manufacturers_to_import = []
            
            # Get compound bow manufacturers
            user_cursor.execute("""
                SELECT DISTINCT compound_brand 
                FROM bow_setups 
                WHERE compound_brand IS NOT NULL 
                AND compound_brand != '' 
                AND compound_brand != 'Other'
            """)
            for row in user_cursor.fetchall():
                manufacturers_to_import.append({
                    'name': row['compound_brand'],
                    'categories': ['compound_bows']
                })
            
            # Get riser manufacturers
            user_cursor.execute("""
                SELECT DISTINCT riser_brand 
                FROM bow_setups 
                WHERE riser_brand IS NOT NULL 
                AND riser_brand != '' 
                AND riser_brand != 'Other'
            """)
            for row in user_cursor.fetchall():
                manufacturers_to_import.append({
                    'name': row['riser_brand'],
                    'categories': ['recurve_risers', 'traditional_risers']
                })
            
            # Get limb manufacturers
            user_cursor.execute("""
                SELECT DISTINCT limb_brand 
                FROM bow_setups 
                WHERE limb_brand IS NOT NULL 
                AND limb_brand != '' 
                AND limb_brand != 'Other'
            """)
            for row in user_cursor.fetchall():
                manufacturers_to_import.append({
                    'name': row['limb_brand'],
                    'categories': ['recurve_limbs', 'traditional_limbs']
                })
            
            # Deduplicate manufacturers by name
            unique_manufacturers = {}
            for mfr in manufacturers_to_import:
                name = mfr['name']
                if name in unique_manufacturers:
                    # Merge categories
                    existing_cats = unique_manufacturers[name]['categories']
                    for cat in mfr['categories']:
                        if cat not in existing_cats:
                            existing_cats.append(cat)
                else:
                    unique_manufacturers[name] = mfr
            
            print(f"📊 Found {len(unique_manufacturers)} unique manufacturers to import")
            
            # Import manufacturers into arrow database
            imported_count = 0
            already_exists_count = 0
            
            for name, mfr_data in unique_manufacturers.items():
                # Check if manufacturer already exists
                arrow_cursor.execute("""
                    SELECT id FROM manufacturers 
                    WHERE LOWER(name) = LOWER(?)
                """, (name,))
                existing = arrow_cursor.fetchone()
                
                if existing:
                    print(f"⚠️ Manufacturer '{name}' already exists, skipping")
                    already_exists_count += 1
                else:
                    # Insert new manufacturer
                    arrow_cursor.execute("""
                        INSERT INTO manufacturers (
                            name, is_active, created_at, updated_at,
                            description
                        ) VALUES (?, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, ?)
                    """, (name, f"Imported from existing bow setups"))
                    
                    manufacturer_id = arrow_cursor.lastrowid
                    
                    # Add manufacturer categories
                    for category in mfr_data['categories']:
                        # Check if category exists in manufacturer_equipment_categories
                        arrow_cursor.execute("""
                            INSERT OR IGNORE INTO manufacturer_equipment_categories (
                                manufacturer_id, category_name, is_supported
                            ) VALUES (?, ?, 1)
                        """, (manufacturer_id, category))
                    
                    imported_count += 1
                    print(f"✅ Imported manufacturer: {name} with categories: {', '.join(mfr_data['categories'])}")
            
            arrow_conn.commit()
            arrow_conn.close()
            user_conn.close()
            
            print(f"\n📊 Import Summary:")
            print(f"  - Imported: {imported_count} new manufacturers")
            print(f"  - Already existed: {already_exists_count} manufacturers")
            print(f"  - Total processed: {len(unique_manufacturers)} manufacturers")
            
            return True
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            if 'arrow_conn' in locals():
                arrow_conn.rollback()
                arrow_conn.close()
            if 'user_conn' in locals():
                user_conn.close()
            return False
    
    def down(self, db_path: str, environment: str) -> bool:
        """Rollback: Remove imported manufacturers"""
        try:
            print("🔄 Rolling back manufacturer import...")
            
            # This is a data import migration, so rollback would be complex
            # We'd need to track which manufacturers were imported
            # For now, we'll just log that rollback is not implemented
            
            print("⚠️ Rollback not implemented for data import migration")
            print("   Imported manufacturers will remain in the database")
            
            return True
            
        except Exception as e:
            print(f"❌ Rollback failed: {e}")
            return False
    
    def _get_user_database_path(self, arrow_db_path: str) -> str:
        """Helper to find user database path"""
        try:
            from user_database import UserDatabase
            user_db = UserDatabase()
            return user_db.db_path
        except Exception as e:
            print(f"⚠️ Error finding user database: {e}")
            return None

# Create the migration instance for discovery
migration = Migration019ImportBowSetupManufacturers()