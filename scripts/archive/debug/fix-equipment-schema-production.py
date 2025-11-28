#!/usr/bin/env python3
"""
Production fix for equipment form schema errors
This script will check and apply migration 008 if needed on production
"""
import sqlite3
import json
import os
import sys
from pathlib import Path

def check_equipment_field_standards_table(db_path):
    """Check if equipment_field_standards table exists and has data"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='equipment_field_standards'
        """)
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("❌ equipment_field_standards table does not exist")
            return False, 0
        
        # Check if table has data
        cursor.execute("SELECT COUNT(*) FROM equipment_field_standards")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("⚠️  equipment_field_standards table exists but is empty")
            return True, 0
        
        # Check categories
        cursor.execute("SELECT DISTINCT category_name FROM equipment_field_standards")
        categories = [row[0] for row in cursor.fetchall()]
        
        expected_categories = ["String", "Sight", "Stabilizer", "Arrow Rest", "Weight"]
        missing_categories = [cat for cat in expected_categories if cat not in categories]
        
        if missing_categories:
            print(f"⚠️  Missing categories: {missing_categories}")
            print(f"   Existing categories: {categories}")
            return True, count
        
        print(f"✅ equipment_field_standards table exists with {count} fields")
        print(f"   Categories: {categories}")
        return True, count
        
    except Exception as e:
        print(f"❌ Error checking table: {e}")
        return False, 0
    finally:
        conn.close()

def create_equipment_field_standards_table(db_path):
    """Create equipment_field_standards table with all required data"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔧 Creating equipment_field_standards table...")
        
        # Create the table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS equipment_field_standards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT NOT NULL,
            field_name TEXT NOT NULL,
            field_type TEXT NOT NULL CHECK (field_type IN ('text', 'number', 'dropdown', 'multi-select')),
            field_label TEXT NOT NULL,
            field_unit TEXT,
            is_required BOOLEAN DEFAULT FALSE,
            validation_rules TEXT,
            dropdown_options TEXT,
            default_value TEXT,
            help_text TEXT,
            field_order INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (category_name, field_name)
        )
        ''')
        
        # Insert all field standards
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
                    {'name': 'sight_type', 'type': 'dropdown', 'label': 'Sight Type', 'required': True, 'options': ['multi-pin', 'single-pin', 'instinctive'], 'order': 1},
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
        
        # Insert field standards for each category
        for category_data in field_standards:
            category_name = category_data['category']
            for field in category_data['fields']:
                cursor.execute('''
                    INSERT OR IGNORE INTO equipment_field_standards 
                    (category_name, field_name, field_type, field_label, is_required, 
                     help_text, field_unit, default_value, validation_rules, dropdown_options, field_order)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    category_name,
                    field['name'],
                    field['type'],
                    field['label'],
                    field.get('required', False),
                    field.get('help', None),
                    field.get('unit', None),
                    field.get('default', None),
                    field.get('validation', None),
                    json.dumps(field.get('options', [])) if field.get('options') else None,
                    field.get('order', 0)
                ))
        
        conn.commit()
        print("✅ Successfully created equipment_field_standards table with all field definitions")
        
        # Verify the data was inserted
        cursor.execute("SELECT COUNT(*) FROM equipment_field_standards")
        count = cursor.fetchone()[0]
        print(f"✅ Total fields inserted: {count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        return False
    finally:
        conn.close()

def find_database_paths():
    """Find potential database paths"""
    paths = []
    
    # Production paths (Docker)
    if os.path.exists("/app/databases/arrow_database.db"):
        paths.append("/app/databases/arrow_database.db")
    
    # Development paths
    if os.path.exists("databases/arrow_database.db"):
        paths.append("databases/arrow_database.db")
    
    if os.path.exists("arrow_scraper/databases/arrow_database.db"):
        paths.append("arrow_scraper/databases/arrow_database.db")
    
    # Legacy paths
    if os.path.exists("arrow_database.db"):
        paths.append("arrow_database.db")
    
    if os.path.exists("arrow_scraper/arrow_database.db"):
        paths.append("arrow_scraper/arrow_database.db")
    
    return paths

def main():
    print("🔧 Equipment Form Schema Production Fix")
    print("=" * 50)
    
    # Find database paths
    db_paths = find_database_paths()
    
    if not db_paths:
        print("❌ No arrow database found!")
        print("Expected locations:")
        print("  - /app/databases/arrow_database.db (Docker)")
        print("  - databases/arrow_database.db")
        print("  - arrow_scraper/databases/arrow_database.db")
        return False
    
    print(f"📋 Found {len(db_paths)} database(s):")
    for path in db_paths:
        print(f"  - {path}")
    
    # Check each database
    fixed_any = False
    for db_path in db_paths:
        print(f"\n🔍 Checking database: {db_path}")
        
        exists, count = check_equipment_field_standards_table(db_path)
        
        if not exists or count == 0:
            print(f"🔧 Applying fix to {db_path}...")
            if create_equipment_field_standards_table(db_path):
                fixed_any = True
                print(f"✅ Fixed database: {db_path}")
            else:
                print(f"❌ Failed to fix: {db_path}")
        else:
            print(f"✅ Database OK: {db_path}")
    
    print("\n" + "=" * 50)
    if fixed_any:
        print("🎉 Equipment form schema has been fixed!")
        print("The following endpoints should now work:")
        print("  - /api/equipment/form-schema/String")
        print("  - /api/equipment/form-schema/Sight")  
        print("  - /api/equipment/form-schema/Stabilizer")
        print("  - /api/equipment/form-schema/Arrow Rest")
        print("  - /api/equipment/form-schema/Weight")
        print("\nRestart your application to ensure changes take effect.")
    else:
        print("ℹ️  All databases already have the required equipment field standards.")
    
    return True

if __name__ == "__main__":
    main()