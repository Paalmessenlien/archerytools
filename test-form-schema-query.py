#!/usr/bin/env python3
"""
Test script to debug form schema database query
"""

import sqlite3
import json
import os

def test_form_schema_query():
    """Test the form schema database query directly"""
    
    # Connect to the database
    db_path = 'databases/arrow_database.db' if os.path.exists('databases/arrow_database.db') else 'arrow_database.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    cursor = conn.cursor()
    
    print("🧪 Testing Form Schema Database Queries")
    print("=" * 50)
    
    # Test categories with new ones
    test_categories = ['Scope', 'Plunger', 'Other', 'Sight', 'String']
    
    for category in test_categories:
        print(f"\n📝 Testing category: {category}")
        try:
            # Execute the same query as the API
            cursor.execute('''
                SELECT field_name, field_type, field_label, field_unit, is_required,
                       validation_rules, dropdown_options, default_value, help_text, field_order
                FROM equipment_field_standards 
                WHERE category_name = ?
                ORDER BY field_order, field_name
            ''', (category,))
            
            rows = cursor.fetchall()
            print(f"   Found {len(rows)} fields")
            
            if rows:
                # Test building the response like the API does
                fields = []
                for row in rows:
                    field_data = {
                        'name': row[0],      # field_name
                        'type': row[1],      # field_type
                        'label': row[2],     # field_label
                        'unit': row[3],      # field_unit
                        'required': bool(row[4]),  # is_required
                        'order': row[9]      # field_order
                    }
                    
                    # Parse JSON fields
                    if row[5]:  # validation_rules
                        try:
                            field_data['validation'] = json.loads(row[5])
                        except json.JSONDecodeError as e:
                            print(f"   ⚠️  JSON decode error in validation_rules: {e}")
                            field_data['validation'] = {}
                    
                    if row[6]:  # dropdown_options
                        try:
                            field_data['options'] = json.loads(row[6])
                        except json.JSONDecodeError as e:
                            print(f"   ⚠️  JSON decode error in dropdown_options: {e}")
                            field_data['options'] = []
                    
                    if row[7]:  # default_value
                        field_data['default'] = row[7]
                    
                    if row[8]:  # help_text
                        field_data['help'] = row[8]
                    
                    fields.append(field_data)
                
                print(f"   ✅ Successfully processed {len(fields)} fields")
                print(f"   📋 Field names: {[f['name'] for f in fields]}")
            else:
                print("   ❌ No fields found for this category")
                
        except Exception as e:
            print(f"   ❌ Query error: {e}")
            import traceback
            traceback.print_exc()
    
    conn.close()
    print(f"\n{'='*50}")
    print("✅ Form schema query test completed!")

if __name__ == '__main__':
    os.chdir('/home/paal/archerytools/arrow_scraper')
    test_form_schema_query()