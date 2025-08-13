#!/usr/bin/env python3
"""
Migration 008: Custom Equipment Management Schema
Updates bow_equipment table to support custom user-entered equipment instead of pre-chosen equipment
"""

import sqlite3
import json
from datetime import datetime
from database_migration_manager import BaseMigration

class Migration008CustomEquipmentSchema(BaseMigration):
    def __init__(self):
        super().__init__()
        self.version = "008"
        self.description = "Add custom equipment support to bow_equipment table"
        self.dependencies = ["007"]
        self.environments = ['all']
    
    def up(self, db_path: str, environment: str) -> bool:
        """Add custom equipment fields to bow_equipment table"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Add new columns to bow_equipment table for custom equipment support
            new_columns = [
                ('manufacturer_name', 'TEXT'),
                ('model_name', 'TEXT'),
                ('category_name', 'TEXT NOT NULL DEFAULT "String"'),
                ('weight_grams', 'REAL'),
                ('description', 'TEXT'),
                ('image_url', 'TEXT'),
                ('is_custom', 'BOOLEAN DEFAULT TRUE'),
            ]
            
            for column_name, column_type in new_columns:
                try:
                    cursor.execute(f'ALTER TABLE bow_equipment ADD COLUMN {column_name} {column_type}')
                    print(f"✅ Added column {column_name} to bow_equipment table")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e):
                        print(f"⚠️  Column {column_name} already exists, skipping")
                    else:
                        raise e
            
            # Make equipment_id nullable for custom equipment (update constraint)
            # Note: SQLite doesn't support modifying constraints, so we'll work with existing schema
            
            # Update existing records to have is_custom = FALSE for pre-chosen equipment
            cursor.execute('''
                UPDATE bow_equipment 
                SET is_custom = FALSE 
                WHERE equipment_id IS NOT NULL AND is_custom IS NULL
            ''')
            
            # Create equipment_field_standards table for form validation
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
            
            # Insert standard field definitions for each equipment category
            field_standards = [
                # String Equipment Fields
                {
                    'category': 'String',
                    'fields': [
                        {'name': 'material', 'type': 'dropdown', 'label': 'Material', 'required': True, 'options': ['BCY-X', 'D97', '452X', '8125G', 'Dacron', 'FastFlight'], 'order': 1},
                        {'name': 'strand_count', 'type': 'number', 'label': 'Strand Count', 'unit': 'strands', 'validation': '{"min": 12, "max": 24}', 'order': 2},
                        {'name': 'length_inches', 'type': 'number', 'label': 'Length', 'unit': 'inches', 'validation': '{"min": 40, "max": 120}', 'order': 3},
                        {'name': 'serving_material', 'type': 'text', 'label': 'Serving Material', 'order': 4},
                        {'name': 'loop_type', 'type': 'dropdown', 'label': 'Loop Type', 'options': ['flemish', 'endless', 'loop'], 'order': 5},
                        {'name': 'bow_weight_range', 'type': 'text', 'label': 'Bow Weight Range', 'help': 'e.g., 40-50 lbs', 'order': 6}
                    ]
                },
                # Sight Equipment Fields  
                {
                    'category': 'Sight',
                    'fields': [
                        {'name': 'sight_type', 'type': 'dropdown', 'label': 'Sight Type', 'required': True, 'options': ['multi-pin', 'single-pin', 'scope', 'instinctive'], 'order': 1},
                        {'name': 'pin_count', 'type': 'number', 'label': 'Pin Count', 'unit': 'pins', 'validation': '{"min": 1, "max": 7}', 'order': 2},
                        {'name': 'adjustment_type', 'type': 'dropdown', 'label': 'Adjustment Type', 'options': ['micro', 'standard', 'toolless'], 'order': 3},
                        {'name': 'mounting_type', 'type': 'dropdown', 'label': 'Mounting Type', 'options': ['dovetail', 'weaver', 'proprietary'], 'order': 4},
                        {'name': 'light_options', 'type': 'multi-select', 'label': 'Light Options', 'options': ['LED', 'Fiber Optic', 'Tritium', 'None'], 'order': 5},
                        {'name': 'max_range_yards', 'type': 'number', 'label': 'Max Range', 'unit': 'yards', 'order': 6}
                    ]
                },
                # Stabilizer Equipment Fields
                {
                    'category': 'Stabilizer', 
                    'fields': [
                        {'name': 'stabilizer_type', 'type': 'dropdown', 'label': 'Stabilizer Type', 'required': True, 'options': ['front', 'side', 'back', 'v-bar', 'offset'], 'order': 1},
                        {'name': 'length_inches', 'type': 'number', 'label': 'Length', 'unit': 'inches', 'validation': '{"min": 4, "max": 36}', 'order': 2},
                        {'name': 'weight_ounces', 'type': 'number', 'label': 'Weight', 'unit': 'ounces', 'validation': '{"min": 1, "max": 32}', 'order': 3},
                        {'name': 'thread_size', 'type': 'dropdown', 'label': 'Thread Size', 'options': ['5/16-24', '1/4-20', '8-32'], 'order': 4},
                        {'name': 'material', 'type': 'dropdown', 'label': 'Material', 'options': ['carbon', 'aluminum', 'steel'], 'order': 5},
                        {'name': 'dampening_type', 'type': 'dropdown', 'label': 'Dampening Type', 'options': ['rubber', 'foam', 'gel', 'none'], 'order': 6}
                    ]
                },
                # Arrow Rest Equipment Fields
                {
                    'category': 'Arrow Rest',
                    'fields': [
                        {'name': 'rest_type', 'type': 'dropdown', 'label': 'Rest Type', 'required': True, 'options': ['drop-away', 'blade', 'launcher', 'shelf', 'whisker-biscuit'], 'order': 1},
                        {'name': 'activation_type', 'type': 'dropdown', 'label': 'Activation Type', 'options': ['cable-driven', 'limb-driven', 'magnetic', 'manual'], 'order': 2},
                        {'name': 'adjustment_features', 'type': 'multi-select', 'label': 'Adjustment Features', 'options': ['Windage', 'Elevation', 'Center Shot', 'Timing'], 'order': 3},
                        {'name': 'arrow_containment', 'type': 'dropdown', 'label': 'Arrow Containment', 'options': ['full', 'partial', 'none'], 'order': 4},
                        {'name': 'mounting_type', 'type': 'dropdown', 'label': 'Mounting Type', 'options': ['berger-hole', 'plunger', 'adhesive'], 'order': 5},
                        {'name': 'arrow_diameter_range', 'type': 'text', 'label': 'Arrow Diameter Range', 'help': 'e.g., .204-.340 inches', 'order': 6}
                    ]
                },
                # Weight Equipment Fields
                {
                    'category': 'Weight',
                    'fields': [
                        {'name': 'weight_ounces', 'type': 'number', 'label': 'Weight', 'unit': 'ounces', 'required': True, 'validation': '{"min": 0.5, "max": 16}', 'order': 1},
                        {'name': 'mounting_location', 'type': 'dropdown', 'label': 'Mounting Location', 'options': ['stabilizer', 'riser', 'limb', 'string'], 'order': 2},
                        {'name': 'weight_type', 'type': 'dropdown', 'label': 'Weight Type', 'options': ['stainless-steel', 'tungsten', 'brass', 'lead'], 'order': 3},
                        {'name': 'thread_size', 'type': 'dropdown', 'label': 'Thread Size', 'options': ['5/16-24', '1/4-20', '8-32'], 'order': 4},
                        {'name': 'shape', 'type': 'dropdown', 'label': 'Shape', 'options': ['cylinder', 'donut', 'disc', 'custom'], 'order': 5},
                        {'name': 'purpose', 'type': 'dropdown', 'label': 'Purpose', 'options': ['balance', 'dampening', 'tuning', 'momentum'], 'order': 6}
                    ]
                }
            ]
            
            # Insert field standards for each category
            for category_data in field_standards:
                category_name = category_data['category']
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
            
            conn.commit()
            conn.close()
            
            print("✅ Successfully updated bow_equipment schema for custom equipment support")
            print("✅ Successfully created equipment_field_standards table with form definitions")
            return True
            
        except Exception as e:
            print(f"❌ Failed to update equipment schema: {e}")
            return False
    
    def down(self, db_path: str, environment: str) -> bool:
        """Remove custom equipment fields (Note: SQLite doesn't support dropping columns easily)"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Drop the equipment_field_standards table
            cursor.execute('DROP TABLE IF EXISTS equipment_field_standards')
            
            # Note: SQLite doesn't support dropping columns, so we'll leave the new columns
            # but reset is_custom flags and clear custom data
            cursor.execute('''
                UPDATE bow_equipment 
                SET is_custom = FALSE,
                    manufacturer_name = NULL,
                    model_name = NULL,
                    weight_grams = NULL,
                    description = NULL,
                    image_url = NULL
                WHERE equipment_id IS NOT NULL
            ''')
            
            conn.commit()
            conn.close()
            
            print("✅ Successfully rolled back custom equipment schema changes")
            return True
            
        except Exception as e:
            print(f"❌ Failed to rollback equipment schema: {e}")
            return False

# Create the migration instance for discovery
migration = Migration008CustomEquipmentSchema()