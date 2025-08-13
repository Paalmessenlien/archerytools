#!/usr/bin/env python3
"""
Migration 009: Complete Equipment Categories
Adds missing Scope, Plunger, and Other equipment categories to equipment_field_standards table
This completes the 8-category equipment management system
"""

import sqlite3
import json
from datetime import datetime
from database_migration_manager import BaseMigration

class Migration010CompleteEquipmentCategories(BaseMigration):
    def __init__(self):
        super().__init__()
        self.version = "010"
        self.description = "Add missing Scope, Plunger, and Other equipment categories"
        self.dependencies = ["008", "009"]
        self.environments = ['all']
    
    def up(self, db_path: str, environment: str) -> bool:
        """Add missing equipment categories to equipment_field_standards table"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if equipment_field_standards table exists (should exist from migration 008)
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='equipment_field_standards'
            """)
            if not cursor.fetchone():
                print("⚠️  equipment_field_standards table doesn't exist. Migration 008 may not have run.")
                # Create the table if it doesn't exist (fallback)
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS equipment_field_standards (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_name TEXT NOT NULL,
                    field_name TEXT NOT NULL,
                    field_type TEXT NOT NULL CHECK (field_type IN ('text', 'number', 'dropdown', 'multi-select')),
                    label TEXT NOT NULL,
                    required BOOLEAN DEFAULT FALSE,
                    help_text TEXT,
                    unit TEXT,
                    default_value TEXT,
                    validation_rules TEXT,
                    field_options TEXT,
                    display_order INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE (category_name, field_name)
                )
                ''')
            
            # Add missing equipment categories (Scope, Plunger, Other)
            missing_categories = [
                # Scope Equipment Fields
                {
                    'category': 'Scope',
                    'fields': [
                        {'name': 'magnification', 'type': 'dropdown', 'label': 'Magnification', 'required': True, 'options': ['1x', '2x', '3x', '4x', '6x', '8x', 'variable'], 'order': 1},
                        {'name': 'objective_lens_size', 'type': 'number', 'label': 'Objective Lens Size', 'unit': 'mm', 'validation': '{"min": 20, "max": 50}', 'order': 2},
                        {'name': 'reticle_type', 'type': 'dropdown', 'label': 'Reticle Type', 'options': ['crosshair', 'dot', 'circle', 'duplex'], 'order': 3},
                        {'name': 'turret_type', 'type': 'dropdown', 'label': 'Turret Type', 'options': ['target', 'hunting', 'tactical'], 'order': 4},
                        {'name': 'eye_relief', 'type': 'number', 'label': 'Eye Relief', 'unit': 'inches', 'validation': '{"min": 2, "max": 6}', 'order': 5},
                        {'name': 'tube_diameter', 'type': 'dropdown', 'label': 'Tube Diameter', 'options': ['1 inch', '30mm', '34mm'], 'order': 6}
                    ]
                },
                # Plunger Equipment Fields
                {
                    'category': 'Plunger',
                    'fields': [
                        {'name': 'plunger_type', 'type': 'dropdown', 'label': 'Plunger Type', 'required': True, 'options': ['magnetic', 'spring', 'hydraulic'], 'order': 1},
                        {'name': 'tension_range', 'type': 'text', 'label': 'Tension Range', 'help': 'e.g., 1-10 lbs', 'order': 2},
                        {'name': 'material', 'type': 'dropdown', 'label': 'Material', 'options': ['aluminum', 'steel', 'composite'], 'order': 3},
                        {'name': 'thread_size', 'type': 'dropdown', 'label': 'Thread Size', 'options': ['5/16-24', '1/4-20', '8-32'], 'order': 4},
                        {'name': 'adjustment_method', 'type': 'dropdown', 'label': 'Adjustment Method', 'options': ['micro', 'standard', 'tool-free'], 'order': 5}
                    ]
                },
                # Other Equipment Fields
                {
                    'category': 'Other',
                    'fields': [
                        {'name': 'equipment_type', 'type': 'text', 'label': 'Equipment Type', 'required': True, 'order': 1},
                        {'name': 'primary_function', 'type': 'text', 'label': 'Primary Function', 'order': 2},
                        {'name': 'specifications', 'type': 'text', 'label': 'Specifications', 'order': 3},
                        {'name': 'installation_method', 'type': 'text', 'label': 'Installation Method', 'order': 4},
                        {'name': 'compatibility_notes', 'type': 'text', 'label': 'Compatibility Notes', 'order': 5}
                    ]
                }
            ]
            
            # Insert field standards for missing categories
            fields_added = 0
            for category_data in missing_categories:
                category_name = category_data['category']
                
                # Check if category already exists
                cursor.execute("""
                    SELECT COUNT(*) FROM equipment_field_standards 
                    WHERE category_name = ?
                """, (category_name,))
                existing_count = cursor.fetchone()[0]
                
                if existing_count > 0:
                    print(f"⚠️  Category '{category_name}' already exists with {existing_count} fields, skipping")
                    continue
                
                print(f"➕ Adding category '{category_name}' with {len(category_data['fields'])} fields")
                
                for field in category_data['fields']:
                    cursor.execute('''
                        INSERT OR IGNORE INTO equipment_field_standards 
                        (category_name, field_name, field_type, label, required, 
                         help_text, unit, default_value, validation_rules, field_options, display_order)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        category_name,
                        field['name'],
                        field['type'],
                        field['label'],
                        field.get('required', False),
                        field.get('help'),
                        field.get('unit'),
                        None,  # default_value
                        field.get('validation'),
                        json.dumps(field.get('options', [])) if field.get('options') else None,
                        field.get('order', 0)
                    ))
                    fields_added += 1
            
            conn.commit()
            
            # Verify all 8 categories are now present
            cursor.execute("""
                SELECT category_name, COUNT(*) as field_count 
                FROM equipment_field_standards 
                GROUP BY category_name 
                ORDER BY category_name
            """)
            categories = cursor.fetchall()
            
            conn.close()
            
            print("✅ Successfully added missing equipment categories")
            print(f"✅ Total fields added: {fields_added}")
            print("✅ Complete equipment categories now available:")
            for category, count in categories:
                print(f"   - {category}: {count} fields")
            
            # Verify we have all 8 expected categories
            expected_categories = {'String', 'Sight', 'Scope', 'Stabilizer', 'Arrow Rest', 'Plunger', 'Weight', 'Other'}
            actual_categories = {category for category, _ in categories}
            
            if expected_categories == actual_categories:
                print("🎯 All 8 equipment categories are now complete!")
            else:
                missing = expected_categories - actual_categories
                if missing:
                    print(f"⚠️  Still missing categories: {missing}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to add missing equipment categories: {e}")
            return False
    
    def down(self, db_path: str, environment: str) -> bool:
        """Remove the added equipment categories"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Remove the categories added in this migration
            categories_to_remove = ['Scope', 'Plunger', 'Other']
            
            for category in categories_to_remove:
                cursor.execute("""
                    DELETE FROM equipment_field_standards 
                    WHERE category_name = ?
                """, (category,))
                print(f"🗑️  Removed category '{category}'")
            
            conn.commit()
            conn.close()
            
            print("✅ Successfully removed added equipment categories")
            return True
            
        except Exception as e:
            print(f"❌ Failed to remove equipment categories: {e}")
            return False

# Create the migration instance for discovery
migration = Migration010CompleteEquipmentCategories()