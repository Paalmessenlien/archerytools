#!/usr/bin/env python3
"""
Equipment Data Seeder
Seeds the equipment database with popular archery equipment
"""

import sqlite3
import json
from pathlib import Path

def get_db_path():
    """Get the correct database path"""
    possible_paths = [
        "databases/arrow_database.db",
        "../databases/arrow_database.db", 
        "arrow_database.db"
    ]
    
    for path in possible_paths:
        if Path(path).exists():
            return path
    
    return "databases/arrow_database.db"

def seed_equipment_data():
    """Seed the equipment database with popular equipment"""
    
    equipment_data = [
        # Strings
        {
            'category': 'String',
            'manufacturer': 'BCY',
            'model_name': 'X99',
            'specifications': {
                'material': 'BCY-X',
                'strand_count': 16,
                'serving_material': 'BCY Halo',
                'bow_weight_range': '30-70 lbs'
            },
            'weight_grams': 45,
            'description': 'High-performance bowstring material for target and hunting',
            'price_range': '$15-25'
        },
        {
            'category': 'String', 
            'manufacturer': 'Winner\'s Choice',
            'model_name': 'Custom String',
            'specifications': {
                'material': '452X',
                'strand_count': 18,
                'serving_material': 'BCY Halo',
                'bow_weight_range': '40-80 lbs'
            },
            'weight_grams': 50,
            'description': 'Custom bowstring with precision craftsmanship',
            'price_range': '$25-40'
        },
        
        # Sights
        {
            'category': 'Sight',
            'manufacturer': 'Trophy Ridge',
            'model_name': 'Fix Series 5-Pin',
            'specifications': {
                'sight_type': 'multi-pin',
                'pin_count': 5,
                'adjustment_type': 'micro',
                'mounting_type': 'dovetail',
                'light_options': ['rheostat'],
                'max_range_yards': 60
            },
            'weight_grams': 285,
            'description': 'Reliable 5-pin sight with micro adjustments',
            'price_range': '$60-80'
        },
        {
            'category': 'Sight',
            'manufacturer': 'Black Gold',
            'model_name': 'Ascent Verdict',
            'specifications': {
                'sight_type': 'single-pin',
                'pin_count': 1,
                'adjustment_type': 'micro',
                'mounting_type': 'dovetail',
                'light_options': ['photochromatic'],
                'max_range_yards': 100
            },
            'weight_grams': 340,
            'description': 'Single-pin slider sight with photochromatic technology',
            'price_range': '$200-300'
        },
        {
            'category': 'Sight',
            'manufacturer': 'HHA Sports',
            'model_name': 'Optimizer Lite',
            'specifications': {
                'sight_type': 'single-pin',
                'pin_count': 1,
                'adjustment_type': 'standard',
                'mounting_type': 'dovetail',
                'light_options': [],
                'max_range_yards': 80
            },
            'weight_grams': 198,
            'description': 'Lightweight single-pin sight for hunting',
            'price_range': '$80-120'
        },
        
        # Stabilizers
        {
            'category': 'Stabilizer',
            'manufacturer': 'B-Stinger',
            'model_name': 'Microhex 8"',
            'specifications': {
                'stabilizer_type': 'front',
                'length_inches': 8,
                'weight_ounces': 3.2,
                'thread_size': '5/16-24',
                'material': 'carbon',
                'dampening_type': 'rubber'
            },
            'weight_grams': 90,
            'description': 'Carbon fiber front stabilizer with micro diameter',
            'price_range': '$60-80'
        },
        {
            'category': 'Stabilizer',
            'manufacturer': 'Easton',
            'model_name': 'Contour 10"',
            'specifications': {
                'stabilizer_type': 'front',
                'length_inches': 10,
                'weight_ounces': 4.1,
                'thread_size': '5/16-24',
                'material': 'carbon',
                'dampening_type': 'gel'
            },
            'weight_grams': 116,
            'description': 'Contour series front stabilizer with gel dampening',
            'price_range': '$40-60'
        },
        {
            'category': 'Stabilizer',
            'manufacturer': 'Trophy Ridge',
            'model_name': 'Static Stabilizer 6"',
            'specifications': {
                'stabilizer_type': 'front',
                'length_inches': 6,
                'weight_ounces': 2.8,
                'thread_size': '5/16-24',
                'material': 'aluminum',
                'dampening_type': 'rubber'
            },
            'weight_grams': 79,
            'description': 'Aluminum stabilizer with rubber dampener',
            'price_range': '$25-35'
        },
        
        # Arrow Rests
        {
            'category': 'Arrow Rest',
            'manufacturer': 'QAD',
            'model_name': 'Ultrarest HDX',
            'specifications': {
                'rest_type': 'drop-away',
                'activation_type': 'cable-driven',
                'adjustment_features': ['micro-adjustable', 'windage', 'elevation'],
                'arrow_containment': 'full',
                'mounting_type': 'berger-hole',
                'arrow_diameter_range': '0.166" - 0.400"'
            },
            'weight_grams': 142,
            'description': 'Premium drop-away rest with full containment',
            'price_range': '$150-180'
        },
        {
            'category': 'Arrow Rest',
            'manufacturer': 'Hamskea',
            'model_name': 'Epsilon',
            'specifications': {
                'rest_type': 'drop-away',
                'activation_type': 'cable-driven',
                'adjustment_features': ['micro-adjustable', 'windage', 'elevation', 'timing'],
                'arrow_containment': 'full',
                'mounting_type': 'berger-hole',
                'arrow_diameter_range': '0.166" - 0.400"'
            },
            'weight_grams': 156,
            'description': 'High-end drop-away rest with precise timing control',
            'price_range': '$180-220'
        },
        {
            'category': 'Arrow Rest',
            'manufacturer': 'Trophy Ridge',
            'model_name': 'Whisker Biscuit V',
            'specifications': {
                'rest_type': 'whisker-biscuit',
                'activation_type': 'manual',
                'adjustment_features': ['windage', 'elevation'],
                'arrow_containment': 'full',
                'mounting_type': 'berger-hole',
                'arrow_diameter_range': '0.200" - 0.400"'
            },
            'weight_grams': 85,
            'description': 'Full-capture rest with whisker design',
            'price_range': '$25-35'
        },
        
        # Weights
        {
            'category': 'Weight',
            'manufacturer': 'B-Stinger',
            'model_name': 'End Weight 1oz',
            'specifications': {
                'weight_ounces': 1,
                'mounting_location': 'stabilizer',
                'weight_type': 'stainless-steel',
                'thread_size': '5/16-24',
                'shape': 'cylinder',
                'purpose': 'balance'
            },
            'weight_grams': 28,
            'description': '1oz stainless steel end weight for stabilizers',
            'price_range': '$8-12'
        },
        {
            'category': 'Weight',
            'manufacturer': 'Easton',
            'model_name': 'Weight Kit 2oz',
            'specifications': {
                'weight_ounces': 2,
                'mounting_location': 'stabilizer',
                'weight_type': 'tungsten',
                'thread_size': '5/16-24',
                'shape': 'disc',
                'purpose': 'balance'
            },
            'weight_grams': 57,
            'description': '2oz tungsten weight for fine-tuning balance',
            'price_range': '$15-25'
        }
    ]
    
    try:
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        # Get category IDs
        cursor.execute('SELECT id, name FROM equipment_categories')
        categories = {row[1]: row[0] for row in cursor.fetchall()}
        
        print(f"Available categories: {list(categories.keys())}")
        
        # Insert equipment
        for item in equipment_data:
            category_id = categories.get(item['category'])
            if not category_id:
                print(f"Warning: Category '{item['category']}' not found, skipping {item['model_name']}")
                continue
            
            cursor.execute('''
                INSERT OR IGNORE INTO equipment 
                (category_id, manufacturer, model_name, specifications, weight_grams, description, price_range)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                category_id,
                item['manufacturer'],
                item['model_name'],
                json.dumps(item['specifications']),
                item['weight_grams'],
                item['description'],
                item['price_range']
            ))
        
        conn.commit()
        print(f"✅ Successfully seeded {len(equipment_data)} equipment items")
        
        # Show summary
        cursor.execute('''
            SELECT ec.name, COUNT(e.id) as count
            FROM equipment_categories ec
            LEFT JOIN equipment e ON ec.id = e.category_id
            GROUP BY ec.id, ec.name
            ORDER BY ec.name
        ''')
        
        print("\n📊 Equipment Summary:")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]} items")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error seeding equipment data: {e}")
        return False

if __name__ == "__main__":
    print("🏹 Seeding equipment database...")
    success = seed_equipment_data()
    if success:
        print("✅ Equipment seeding completed successfully!")
    else:
        print("❌ Equipment seeding failed!")