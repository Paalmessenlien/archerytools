#!/usr/bin/env python3
"""
Debug form schema API issue by replicating the API logic exactly
"""

import sqlite3
import json
import os
import sys

# Add arrow_scraper to path
sys.path.insert(0, '/home/paal/archerytools/arrow_scraper')

def debug_form_schema():
    """Debug form schema using same logic as API"""
    print("🔍 Debugging Form Schema API Logic")
    print("=" * 50)
    
    # Import the API modules to use same database connection logic
    try:
        from arrow_database import ArrowDatabase
        
        # Try to get database using same logic as get_database()
        print("\n1. Testing database connection logic:")
        
        # Test database paths in order of priority
        db_paths = [
            '/app/arrow_database.db',          # Primary location
            '/app/arrow_database_backup.db',   # Backup location  
            'arrow_database.db',               # Development location
            'databases/arrow_database.db',     # Alternative location
        ]
        
        database_path = None
        for db_path in db_paths:
            abs_path = os.path.abspath(db_path)
            if os.path.exists(abs_path):
                print(f"   ✅ Found database at: {abs_path}")
                # Test if it has arrows
                try:
                    conn = sqlite3.connect(abs_path)
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM arrows")
                    count = cursor.fetchone()[0]
                    if count > 0:
                        database_path = abs_path
                        print(f"   📊 Database has {count} arrows - using this one")
                        conn.close()
                        break
                    else:
                        print(f"   ⚠️  Database empty ({count} arrows) - skipping")
                    conn.close()
                except Exception as e:
                    print(f"   ❌ Database error: {e}")
            else:
                print(f"   ❌ Not found: {abs_path}")
        
        if not database_path:
            print("❌ No suitable database found!")
            return
            
        print(f"\n2. Using database: {database_path}")
        
        # Test form schema query for new categories
        conn = sqlite3.connect(database_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        test_categories = ['Scope', 'Plunger', 'Other']
        
        for category in test_categories:
            print(f"\n3. Testing form schema for: {category}")
            
            try:
                # Execute exact same query as API
                cursor.execute('''
                    SELECT field_name, field_type, field_label, field_unit, is_required,
                           validation_rules, dropdown_options, default_value, help_text, field_order
                    FROM equipment_field_standards 
                    WHERE category_name = ?
                    ORDER BY field_order, field_name
                ''', (category,))
                
                fields = []
                rows = cursor.fetchall()
                print(f"   📊 Found {len(rows)} field rows")
                
                for row in rows:
                    field_data = {
                        'name': row[0],      # field_name
                        'type': row[1],      # field_type
                        'label': row[2],     # field_label
                        'unit': row[3],      # field_unit
                        'required': bool(row[4]),  # is_required
                        'order': row[9]      # field_order
                    }
                    
                    # Parse JSON fields like the API does
                    if row[5]:  # validation_rules
                        try:
                            field_data['validation'] = json.loads(row[5])
                        except json.JSONDecodeError:
                            pass
                            
                    if row[6]:  # dropdown_options
                        try:
                            field_data['options'] = json.loads(row[6])
                        except json.JSONDecodeError:
                            field_data['options'] = []
                            
                    if row[7]:  # default_value
                        field_data['default'] = row[7]
                        
                    if row[8]:  # help_text
                        field_data['help'] = row[8]
                        
                    fields.append(field_data)
                
                # Build response like API does
                response = {
                    'category': category,
                    'fields': fields
                }
                
                print(f"   ✅ Successfully built response with {len(fields)} fields")
                print(f"   📝 Field names: {[f['name'] for f in fields]}")
                
                # Try to serialize as JSON like Flask does
                try:
                    json_response = json.dumps(response, indent=2)
                    print(f"   ✅ JSON serialization successful ({len(json_response)} characters)")
                except Exception as e:
                    print(f"   ❌ JSON serialization error: {e}")
                    
            except Exception as e:
                print(f"   ❌ Query error for {category}: {e}")
                import traceback
                traceback.print_exc()
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    os.chdir('/home/paal/archerytools/arrow_scraper')
    debug_form_schema()