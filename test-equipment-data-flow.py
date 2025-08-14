#!/usr/bin/env python3

"""
Test Equipment Data Flow - Debug Dropdown Pre-population
This script directly tests the equipment data flow to debug dropdown issues.
"""

import sqlite3
import json
from pprint import pprint

def test_equipment_data_flow():
    """Test the complete equipment data flow from database to API response"""
    
    print("🔍 Testing Equipment Data Flow for Dropdown Pre-population\n")
    
    # Step 1: Check raw database data
    print("=" * 50)
    print("STEP 1: Raw Database Data")
    print("=" * 50)
    
    conn = sqlite3.connect('databases/user_data.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get equipment with specifications
    cursor.execute("""
        SELECT id, bow_setup_id, manufacturer_name, model_name, category_name,
               custom_specifications, specifications, is_custom
        FROM bow_equipment 
        WHERE custom_specifications IS NOT NULL OR specifications IS NOT NULL
        ORDER BY id
    """)
    
    equipment_rows = cursor.fetchall()
    print(f"Found {len(equipment_rows)} equipment items with specifications:")
    
    for row in equipment_rows:
        print(f"\nEquipment ID {row['id']}:")
        print(f"  Manufacturer: {row['manufacturer_name']}")
        print(f"  Model: {row['model_name']}")
        print(f"  Category: {row['category_name']}")
        print(f"  Is Custom: {row['is_custom']}")
        
        if row['custom_specifications']:
            print(f"  Custom Specs (raw): {row['custom_specifications']}")
            try:
                custom_specs = json.loads(row['custom_specifications'])
                print(f"  Custom Specs (parsed): {json.dumps(custom_specs, indent=2)}")
            except json.JSONDecodeError as e:
                print(f"  Custom Specs parsing error: {e}")
        
        if row['specifications']:
            print(f"  Specs field (raw): {row['specifications']}")
    
    conn.close()
    
    # Step 2: Test form schema API
    print("\n" + "=" * 50)
    print("STEP 2: Form Schema API Response")
    print("=" * 50)
    
    import requests
    
    categories_to_test = ['String', 'Sight', 'Stabilizer']
    
    for category in categories_to_test:
        try:
            response = requests.get(f'http://localhost:5000/api/equipment/form-schema/{category}')
            if response.status_code == 200:
                schema = response.json()
                dropdown_fields = [f for f in schema.get('fields', []) if f.get('type') == 'dropdown']
                multi_select_fields = [f for f in schema.get('fields', []) if f.get('type') == 'multi-select']
                
                print(f"\n{category} Schema:")
                print(f"  Total fields: {len(schema.get('fields', []))}")
                print(f"  Dropdown fields: {len(dropdown_fields)}")
                print(f"  Multi-select fields: {len(multi_select_fields)}")
                
                # Show first few dropdown options
                for field in dropdown_fields[:2]:
                    print(f"    - {field['name']} ({field['label']}): {len(field.get('options', []))} options")
                    if field.get('options'):
                        print(f"      Options: {field['options'][:3]}...")
                        
                for field in multi_select_fields[:1]:
                    print(f"    - {field['name']} ({field['label']}): {len(field.get('options', []))} options")
                    if field.get('options'):
                        print(f"      Options: {field['options']}")
            else:
                print(f"  {category}: HTTP {response.status_code}")
        except Exception as e:
            print(f"  {category}: Error - {e}")
    
    # Step 3: Simulate the editing data initialization
    print("\n" + "=" * 50)
    print("STEP 3: Editing Data Initialization Simulation")
    print("=" * 50)
    
    conn = sqlite3.connect('databases/user_data.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get first equipment item
    cursor.execute("SELECT * FROM bow_equipment WHERE custom_specifications IS NOT NULL LIMIT 1")
    equipment = cursor.fetchone()
    
    if equipment:
        print(f"Simulating edit for Equipment ID {equipment['id']}:")
        print(f"  Category: {equipment['category_name']}")
        print(f"  Raw custom_specifications: {equipment['custom_specifications']}")
        
        # Simulate API processing (what happens in api.py line 3532)
        specifications = {}
        if equipment['custom_specifications']:
            try:
                specifications = json.loads(equipment['custom_specifications'])
                print(f"  API would return specifications as: {json.dumps(specifications, indent=2)}")
            except json.JSONDecodeError as e:
                print(f"  API parsing error: {e}")
                specifications = {}
        
        # Simulate frontend processing (what should happen in CustomEquipmentForm.vue)
        print(f"\n  Frontend would receive equipment object with:")
        equipment_obj = {
            'id': equipment['id'],
            'manufacturer_name': equipment['manufacturer_name'],
            'model_name': equipment['model_name'],
            'category_name': equipment['category_name'],
            'specifications': specifications  # This is what API returns
        }
        print(f"    specifications: {json.dumps(equipment_obj['specifications'], indent=4)}")
        
        # Test form field mapping
        print(f"\n  Form field mapping test:")
        for field_name, field_value in specifications.items():
            print(f"    formData.specifications['{field_name}'] = {repr(field_value)}")
            
    conn.close()
    
    # Step 4: Check if there's a mismatch in field names
    print("\n" + "=" * 50)
    print("STEP 4: Field Name Compatibility Check")
    print("=" * 50)
    
    conn = sqlite3.connect('databases/user_data.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all unique field names from equipment specifications
    cursor.execute("SELECT custom_specifications FROM bow_equipment WHERE custom_specifications IS NOT NULL")
    all_specs = cursor.fetchall()
    
    all_field_names = set()
    for spec_row in all_specs:
        try:
            specs = json.loads(spec_row['custom_specifications'])
            all_field_names.update(specs.keys())
        except:
            pass
    
    print(f"Field names found in database specifications:")
    for field_name in sorted(all_field_names):
        print(f"  - {field_name}")
    
    conn.close()

    # Step 5: Create minimal reproduction test data
    print("\n" + "=" * 50)
    print("STEP 5: Minimal Reproduction Test")
    print("=" * 50)
    
    print("Creating test data for reproduction:")
    test_equipment = {
        'id': 1,
        'manufacturer_name': 'Test Manufacturer', 
        'model_name': 'Test Model',
        'category_name': 'Sight',
        'specifications': {
            'sight_type': 'scope',
            'adjustment_type': 'micro',
            'light_options': ['LED', 'Fiber Optic']
        }
    }
    
    print(f"Test equipment object: {json.dumps(test_equipment, indent=2)}")
    print(f"\nExpected form behavior:")
    print(f"  - sight_type dropdown should show 'scope' selected")  
    print(f"  - adjustment_type dropdown should show 'micro' selected")
    print(f"  - light_options checkboxes should have 'LED' and 'Fiber Optic' checked")
    
    return equipment_rows

if __name__ == "__main__":
    test_equipment_data_flow()