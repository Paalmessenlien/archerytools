#!/usr/bin/env python3
"""
Migration 020: Enhance string equipment fields for speed calculation
Created: 2025-08-15
"""

import sqlite3
import sys
import os
import json

def migrate_up(cursor):
    """Apply the migration - enhance string equipment fields"""
    
    # Enhanced string equipment fields for speed calculation
    string_fields = [
        {
            'category_name': 'String',
            'field_name': 'material',
            'field_type': 'dropdown',
            'label': 'String Material',
            'unit': '',
            'required': True,
            'validation_rules': json.dumps({'required': True}),
            'field_options': json.dumps([
                'Dacron',
                'FastFlight',
                'Dyneema', 
                'Vectran',
                'SK75 Dyneema',
                'Custom Blend'
            ]),
            'default_value': 'Dacron',
            'help_text': 'String material affects bow speed - Dacron is slowest but most forgiving',
            'display_order': 20
        },
        {
            'category_name': 'String',
            'field_name': 'strand_count',
            'field_type': 'number',
            'label': 'Strand Count',
            'unit': 'strands',
            'required': False,
            'validation_rules': json.dumps({'min': 8, 'max': 24}),
            'field_options': json.dumps([]),
            'default_value': '12',
            'help_text': 'Number of strands in the string (typically 8-24)',
            'display_order': 30
        },
        {
            'category_name': 'String',
            'field_name': 'serving_material',
            'field_type': 'dropdown',
            'label': 'Serving Material',
            'unit': '',
            'required': False,
            'validation_rules': json.dumps({}),
            'field_options': json.dumps([
                'Monofilament',
                'Braided',
                'Halo',
                'BCY 3D',
                'Angel Majesty'
            ]),
            'default_value': 'Monofilament',
            'help_text': 'Material used for center and end servings',
            'display_order': 40
        },
        {
            'category_name': 'String',
            'field_name': 'string_length',
            'field_type': 'text',
            'label': 'String Length',
            'unit': 'inches',
            'required': False,
            'validation_rules': json.dumps({}),
            'field_options': json.dumps([]),
            'default_value': '',
            'help_text': 'Actual measurement or AMO length',
            'display_order': 50
        },
        {
            'category_name': 'String',
            'field_name': 'brace_height',
            'field_type': 'text',
            'label': 'Brace Height',
            'unit': 'inches',
            'required': False,
            'validation_rules': json.dumps({}),
            'field_options': json.dumps([]),
            'default_value': '',
            'help_text': 'Distance from grip to string at rest',
            'display_order': 60
        },
        {
            'category_name': 'String',
            'field_name': 'estimated_shots',
            'field_type': 'number',
            'label': 'Estimated Shot Count',
            'unit': 'shots',
            'required': False,
            'validation_rules': json.dumps({'min': 0}),
            'field_options': json.dumps([]),
            'default_value': '0',
            'help_text': 'Approximate number of shots on this string',
            'display_order': 70
        },
        {
            'category_name': 'String',
            'field_name': 'speed_rating',
            'field_type': 'dropdown',
            'label': 'Speed Rating',
            'unit': '',
            'required': False,
            'validation_rules': json.dumps({}),
            'field_options': json.dumps([
                'Slow (Dacron)',
                'Standard (FastFlight)',
                'Fast (Dyneema)',
                'Very Fast (Vectran)',
                'Ultra Fast (SK75)',
                'Unknown'
            ]),
            'default_value': 'Standard (FastFlight)',
            'help_text': 'Relative speed category of string material',
            'display_order': 25
        }
    ]
    
    # Insert or update string equipment fields
    for field in string_fields:
        # Check if field already exists
        cursor.execute('''
            SELECT COUNT(*) FROM equipment_field_standards 
            WHERE category_name = ? AND field_name = ?
        ''', (field['category_name'], field['field_name']))
        
        exists = cursor.fetchone()[0] > 0
        
        if exists:
            # Update existing field
            cursor.execute('''
                UPDATE equipment_field_standards 
                SET field_type = ?, label = ?, unit = ?, required = ?, 
                    validation_rules = ?, field_options = ?, default_value = ?, 
                    help_text = ?, display_order = ?
                WHERE category_name = ? AND field_name = ?
            ''', (
                field['field_type'], field['label'], field['unit'], field['required'],
                field['validation_rules'], field['field_options'], field['default_value'],
                field['help_text'], field['display_order'],
                field['category_name'], field['field_name']
            ))
            print(f"✅ Updated string field: {field['field_name']}")
        else:
            # Insert new field
            cursor.execute('''
                INSERT INTO equipment_field_standards 
                (category_name, field_name, field_type, label, unit, required, 
                 validation_rules, field_options, default_value, help_text, display_order)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                field['category_name'], field['field_name'], field['field_type'],
                field['label'], field['unit'], field['required'], field['validation_rules'],
                field['field_options'], field['default_value'], field['help_text'],
                field['display_order']
            ))
            print(f"✅ Added string field: {field['field_name']}")

def migrate_down(cursor):
    """Rollback the migration - remove enhanced string fields"""
    enhanced_fields = ['material', 'strand_count', 'serving_material', 'string_length', 
                      'brace_height', 'estimated_shots', 'speed_rating']
    
    for field_name in enhanced_fields:
        cursor.execute('''
            DELETE FROM equipment_field_standards 
            WHERE category_name = 'String' AND field_name = ?
        ''', (field_name,))
        print(f"✅ Removed string field: {field_name}")

def get_migration_info():
    """Return migration metadata"""
    return {
        'version': 20,
        'description': 'Enhance string equipment fields for speed calculation',
        'dependencies': ["008"]  # Depends on equipment_field_standards table
    }

def main():
    """Main function for standalone execution"""
    if len(sys.argv) < 2:
        print("Usage: python 020_enhance_string_equipment_fields.py <database_path> [--rollback]")
        sys.exit(1)
    
    db_path = sys.argv[1]
    rollback = '--rollback' in sys.argv
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        sys.exit(1)
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        if rollback:
            print("🔄 Rolling back migration 020...")
            migrate_down(cursor)
        else:
            print("🚀 Applying migration 020...")
            migrate_up(cursor)
        
        # Commit changes
        conn.commit()
        conn.close()
        
        action = "rolled back" if rollback else "applied"
        print(f"✅ Migration 020 {action} successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()