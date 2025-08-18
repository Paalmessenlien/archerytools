#!/usr/bin/env python3
"""
Migration 026: Add Peep Sight Equipment Category
Adds "Peep Sight" as a new equipment category with appropriate field definitions

Date: 2025-08-17
Author: Claude Code Enhancement
Request: User wants to add peep sight as equipment option
Solution: Add Peep Sight category with specialized field schema
"""

import sqlite3
import json
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database_migration_manager import BaseMigration

class Migration026AddPeepSightCategory(BaseMigration):
    def __init__(self):
        super().__init__()
        self.version = "026"
        self.description = "Add Peep Sight equipment category with specialized fields"
        self.dependencies = ["025"]
        self.environments = ['all']
        self.target_database = 'arrow'  # Target unified database
    
    def up(self, db_path: str, environment: str) -> bool:
        """
        Add Peep Sight category to equipment_field_standards table
        """
        try:
            print("🔧 Adding Peep Sight equipment category...")
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if equipment_field_standards table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='equipment_field_standards'")
            if not cursor.fetchone():
                print("⚠️  equipment_field_standards table not found - skipping migration")
                conn.close()
                return True
            
            # Check if Peep Sight category already exists
            cursor.execute("SELECT COUNT(*) FROM equipment_field_standards WHERE category_name = 'Peep Sight'")
            existing_count = cursor.fetchone()[0]
            
            if existing_count > 0:
                print(f"✅ Peep Sight category already exists with {existing_count} fields - no changes needed")
                conn.close()
                return True
            
            print("🏗️  Adding Peep Sight category with specialized field definitions...")
            
            # Define Peep Sight specific fields
            peep_sight_fields = [
                {
                    'name': 'aperture_diameter',
                    'type': 'dropdown',
                    'label': 'Aperture Diameter',
                    'required': True,
                    'options': ['1/16"', '3/32"', '1/8"', '5/32"', '3/16"', '1/4"', '5/16"'],
                    'help': 'Diameter of the peep sight opening',
                    'order': 1
                },
                {
                    'name': 'mounting_style',
                    'type': 'dropdown',
                    'label': 'Mounting Style',
                    'required': True,
                    'options': ['served in', 'twist in', 'tie in', 'split yoke'],
                    'help': 'How the peep sight attaches to the string',
                    'order': 2
                },
                {
                    'name': 'material',
                    'type': 'dropdown',
                    'label': 'Material',
                    'options': ['aluminum', 'brass', 'steel', 'plastic', 'composite'],
                    'order': 3
                },
                {
                    'name': 'clarifying_lens',
                    'type': 'dropdown',
                    'label': 'Clarifying Lens',
                    'options': ['none', 'included', 'optional', 'interchangeable'],
                    'help': 'Type of clarifying lens support',
                    'order': 4
                },
                {
                    'name': 'tube_length',
                    'type': 'number',
                    'label': 'Tube Length',
                    'unit': 'inches',
                    'validation': '{"min": 0.1, "max": 2.0, "step": 0.1}',
                    'help': 'Length of the peep sight tube',
                    'order': 5
                },
                {
                    'name': 'weight',
                    'type': 'number',
                    'label': 'Weight',
                    'unit': 'grains',
                    'validation': '{"min": 1, "max": 50}',
                    'help': 'Weight of the peep sight in grains',
                    'order': 6
                },
                {
                    'name': 'string_alignment',
                    'type': 'dropdown',
                    'label': 'String Alignment',
                    'options': ['self-aligning', 'manual', 'fixed'],
                    'help': 'How the peep sight aligns on the string',
                    'order': 7
                },
                {
                    'name': 'light_gathering',
                    'type': 'dropdown',
                    'label': 'Light Gathering',
                    'options': ['standard', 'enhanced', 'none'],
                    'help': 'Light gathering capability',
                    'order': 8
                },
                {
                    'name': 'interchangeable_apertures',
                    'type': 'dropdown',
                    'label': 'Interchangeable Apertures',
                    'options': ['yes', 'no'],
                    'help': 'Whether aperture size can be changed',
                    'order': 9
                },
                {
                    'name': 'draw_length_compatibility',
                    'type': 'text',
                    'label': 'Draw Length Compatibility',
                    'help': 'Compatible draw length range (e.g., 28-32 inches)',
                    'order': 10
                }
            ]
            
            # Insert field standards for Peep Sight category
            fields_added = 0
            for field in peep_sight_fields:
                cursor.execute('''
                    INSERT INTO equipment_field_standards 
                    (category_name, field_name, field_type, field_label, is_required, 
                     help_text, field_unit, validation_rules, dropdown_options, field_order)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    'Peep Sight',
                    field['name'],
                    field['type'],
                    field['label'],
                    field.get('required', False),
                    field.get('help'),
                    field.get('unit'),
                    field.get('validation'),
                    json.dumps(field.get('options', [])) if field.get('options') else None,
                    field.get('order', 0)
                ))
                fields_added += 1
            
            # Verify the addition
            cursor.execute("SELECT COUNT(*) FROM equipment_field_standards WHERE category_name = 'Peep Sight'")
            added_count = cursor.fetchone()[0]
            
            conn.commit()
            conn.close()
            
            if added_count == len(peep_sight_fields):
                print("✅ Peep Sight category added successfully!")
                print(f"   - Added {fields_added} specialized fields")
                print("   - Supports various aperture sizes and mounting styles")
                print("   - Includes clarifying lens and alignment options")
                return True
            else:
                print(f"❌ Field count mismatch: expected {len(peep_sight_fields)}, got {added_count}")
                return False
            
        except Exception as e:
            print(f"❌ Failed to add Peep Sight category: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def down(self, db_path: str, environment: str) -> bool:
        """
        Remove Peep Sight category
        """
        try:
            print("⚠️  Removing Peep Sight equipment category...")
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Remove all Peep Sight fields
            cursor.execute("DELETE FROM equipment_field_standards WHERE category_name = 'Peep Sight'")
            removed_count = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            print(f"✅ Removed Peep Sight category ({removed_count} fields)")
            return True
            
        except Exception as e:
            print(f"❌ Failed to remove Peep Sight category: {e}")
            return False

# Create migration instance for discovery
migration = Migration026AddPeepSightCategory()

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python 026_add_peep_sight_category.py <database_path>")
        sys.exit(1)
    
    db_path = sys.argv[1]
    migration = Migration026AddPeepSightCategory()
    
    if '--rollback' in sys.argv:
        success = migration.down(db_path, 'manual')
    else:
        success = migration.up(db_path, 'manual')
    
    sys.exit(0 if success else 1)