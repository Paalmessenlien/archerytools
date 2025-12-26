#!/usr/bin/env python3
"""
Add sample equipment data for testing the equipment management system
"""

import sqlite3
import json
from pathlib import Path

def add_sample_equipment(db_path='databases/arrow_database.db'):
    db_path = Path(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get category IDs
    cursor.execute("SELECT id, name FROM equipment_categories")
    categories = {name: id for id, name in cursor.fetchall()}
    
    # Sample equipment data
    sample_equipment = [
        # More Sights
        {
            'category': 'Sight',
            'manufacturer': 'Hoyt',
            'model_name': 'Klicker Sight',
            'specifications': {
                'sight_type': 'multi-pin',
                'pin_count': 5,
                'adjustment_type': 'micro',
                'mounting_type': 'dovetail',
                'max_range_yards': 80
            },
            'weight_grams': 320,
            'price_range': '$150-200',
            'description': 'Professional 5-pin sight with micro adjustments'
        },
        {
            'category': 'Sight',
            'manufacturer': 'Spot Hogg',
            'model_name': 'Fast Eddie XL',
            'specifications': {
                'sight_type': 'single-pin',
                'pin_count': 1,
                'adjustment_type': 'toolless',
                'mounting_type': 'dovetail',
                'light_options': ['LED'],
                'max_range_yards': 100
            },
            'weight_grams': 410,
            'price_range': '$300-400',
            'description': 'Single pin slider sight with LED light'
        },
        
        # More Stabilizers
        {
            'category': 'Stabilizer',
            'manufacturer': 'Bee Stinger',
            'model_name': 'Pro Hunter Maxx',
            'specifications': {
                'stabilizer_type': 'front',
                'length_inches': 10,
                'weight_ounces': 8.2,
                'thread_size': '5/16-24',
                'material': 'carbon',
                'dampening_type': 'rubber'
            },
            'weight_grams': 232,
            'price_range': '$80-120',
            'description': 'Carbon front stabilizer with rubber dampening'
        },
        {
            'category': 'Stabilizer',
            'manufacturer': 'Mathews',
            'model_name': 'Flatline',
            'specifications': {
                'stabilizer_type': 'front',
                'length_inches': 8,
                'weight_ounces': 6.5,
                'thread_size': '5/16-24',
                'material': 'aluminum',
                'dampening_type': 'gel'
            },
            'weight_grams': 184,
            'price_range': '$60-90',
            'description': 'Lightweight aluminum stabilizer with gel dampening'
        },
        
        # More Arrow Rests
        {
            'category': 'Arrow Rest',
            'manufacturer': 'Hamskea',
            'model_name': 'Trinity Hunter Pro',
            'specifications': {
                'rest_type': 'drop-away',
                'activation_type': 'cable-driven',
                'adjustment_features': ['windage', 'elevation', 'timing'],
                'arrow_containment': 'full',
                'mounting_type': 'berger-hole'
            },
            'weight_grams': 95,
            'price_range': '$130-160',
            'description': 'Full containment drop-away rest with micro adjustments'
        },
        {
            'category': 'Arrow Rest',
            'manufacturer': 'QAD',
            'model_name': 'Ultrarest HDX',
            'specifications': {
                'rest_type': 'drop-away',
                'activation_type': 'cable-driven',
                'adjustment_features': ['windage', 'elevation'],
                'arrow_containment': 'partial',
                'mounting_type': 'berger-hole'
            },
            'weight_grams': 78,
            'price_range': '$100-130',
            'description': 'Reliable drop-away rest for hunting applications'
        },
        
        # More Strings
        {
            'category': 'String',
            'manufacturer': 'BCY',
            'model_name': 'X99 Custom String',
            'specifications': {
                'material': 'BCY-X',
                'strand_count': 18,
                'length_inches': 92,
                'serving_material': 'BCY #4',
                'loop_type': 'flemish',
                'bow_weight_range': '50-70 lbs'
            },
            'weight_grams': 42,
            'price_range': '$25-35',
            'description': 'High-performance custom bowstring with flemish loops'
        },
        {
            'category': 'String',
            'manufacturer': 'Winner\'s Choice',
            'model_name': 'Trophy Strings',
            'specifications': {
                'material': '452X',
                'strand_count': 20,
                'length_inches': 88,
                'serving_material': 'Halo',
                'loop_type': 'endless',
                'bow_weight_range': '40-60 lbs'
            },
            'weight_grams': 38,
            'price_range': '$30-45',
            'description': 'Tournament grade string set with endless loops'
        },
        
        # More Weights
        {
            'category': 'Weight',
            'manufacturer': 'Doinker',
            'model_name': 'Supreme Weights',
            'specifications': {
                'weight_ounces': 4,
                'mounting_location': 'stabilizer',
                'weight_type': 'stainless-steel',
                'thread_size': '5/16-24',
                'shape': 'cylinder',
                'purpose': 'balance'
            },
            'weight_grams': 113,
            'price_range': '$15-25',
            'description': 'Stainless steel stabilizer weights for balance'
        },
        {
            'category': 'Weight',
            'manufacturer': 'Trophy Ridge',
            'model_name': 'Static Weights',
            'specifications': {
                'weight_ounces': 2,
                'mounting_location': 'stabilizer',
                'weight_type': 'brass',
                'thread_size': '1/4-20',
                'shape': 'donut',
                'purpose': 'dampening'
            },
            'weight_grams': 57,
            'price_range': '$10-18',
            'description': 'Brass donut weights for vibration dampening'
        }
    ]
    
    # Insert sample equipment
    added_count = 0
    for equipment in sample_equipment:
        category_id = categories.get(equipment['category'])
        if not category_id:
            print(f"⚠️  Category '{equipment['category']}' not found, skipping...")
            continue
        
        # Check if this equipment already exists
        cursor.execute("""
            SELECT COUNT(*) FROM equipment 
            WHERE manufacturer = ? AND model_name = ? AND category_id = ?
        """, (equipment['manufacturer'], equipment['model_name'], category_id))
        
        if cursor.fetchone()[0] > 0:
            print(f"⚠️  {equipment['manufacturer']} {equipment['model_name']} already exists, skipping...")
            continue
        
        # Insert the equipment
        cursor.execute("""
            INSERT INTO equipment 
            (category_id, manufacturer, model_name, specifications, weight_grams, 
             price_range, description, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """, (
            category_id,
            equipment['manufacturer'],
            equipment['model_name'],
            json.dumps(equipment['specifications']),
            equipment['weight_grams'],
            equipment['price_range'],
            equipment['description']
        ))
        
        added_count += 1
        print(f"✅ Added {equipment['manufacturer']} {equipment['model_name']}")
    
    conn.commit()
    conn.close()
    
    print(f"\n🎉 Successfully added {added_count} new equipment items!")
    
    # Show updated counts
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ec.name, COUNT(*) as count 
        FROM equipment e 
        JOIN equipment_categories ec ON e.category_id = ec.id 
        GROUP BY ec.name
        ORDER BY ec.name
    """)
    
    print("\n📊 Equipment counts by category:")
    for category, count in cursor.fetchall():
        print(f"   {category}: {count} items")
    
    conn.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1].startswith('--target-db='):
        target_db = sys.argv[1].split('=', 1)[1]
        add_sample_equipment(target_db)
    else:
        add_sample_equipment()