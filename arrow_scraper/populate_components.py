#!/usr/bin/env python3
"""
Component Database Population Script
Populates the component database with common archery components
"""

import json
from pathlib import Path
from component_database import ComponentDatabase

def populate_component_database():
    """Populate the component database with extensive component data"""
    print("🏹 Populating Component Database")
    print("=" * 50)
    
    db = ComponentDatabase()
    
    # Points (Arrow Tips)
    print("\n🎯 Adding arrow points...")
    points_data = [
        # Easton Points
        {
            'manufacturer': 'Easton Archery',
            'model_name': 'Field Point 75gr',
            'specifications': {
                'weight': '75gr',
                'thread_type': '8-32',
                'diameter': 0.25,
                'material': 'stainless_steel',
                'point_type': 'field'
            },
            'price_range': '$8-12',
            'description': 'Standard field point for target practice'
        },
        {
            'manufacturer': 'Easton Archery',
            'model_name': 'Field Point 125gr',
            'specifications': {
                'weight': '125gr',
                'thread_type': '8-32',
                'diameter': 0.25,
                'material': 'stainless_steel',
                'point_type': 'field'
            },
            'price_range': '$8-12',
            'description': 'Heavier field point for hunting practice'
        },
        {
            'manufacturer': 'Easton Archery',
            'model_name': 'Bullet Point 100gr',
            'specifications': {
                'weight': '100gr',
                'thread_type': '8-32',
                'diameter': 0.25,
                'material': 'stainless_steel',
                'point_type': 'bullet'
            },
            'price_range': '$10-15',
            'description': 'Streamlined bullet point for reduced deflection'
        },
        # Gold Tip Points
        {
            'manufacturer': 'Gold Tip',
            'model_name': 'Accu Point 100gr',
            'specifications': {
                'weight': '100gr',
                'thread_type': '8-32',
                'diameter': 0.246,
                'material': 'steel',
                'point_type': 'field'
            },
            'price_range': '$6-10',
            'description': 'Precision machined field point'
        },
        # Victory Points
        {
            'manufacturer': 'Victory Archery',
            'model_name': 'VForce Point 100gr',
            'specifications': {
                'weight': '100gr',
                'thread_type': '8-32',
                'diameter': 0.245,
                'material': 'stainless_steel',
                'point_type': 'field'
            },
            'price_range': '$10-14',
            'description': 'High-precision field point'
        }
    ]
    
    for point in points_data:
        db.add_component('points', **point)
    
    # Nocks
    print("\n🔹 Adding nocks...")
    nocks_data = [
        {
            'manufacturer': 'Easton Archery',
            'model_name': 'Super Nock',
            'specifications': {
                'nock_size': '0.244',
                'fit_type': 'push_in',
                'material': 'plastic',
                'colors': ['red', 'yellow', 'green', 'orange'],
                'weight': '6gr',
                'throat_size': 0.088
            },
            'price_range': '$8-12 per dozen',
            'description': 'Precision molded super nock'
        },
        {
            'manufacturer': 'Gold Tip',
            'model_name': 'Accu Nock',
            'specifications': {
                'nock_size': '0.246',
                'fit_type': 'push_in',
                'material': 'plastic',
                'colors': ['red', 'yellow', 'white'],
                'weight': '7gr',
                'throat_size': 0.098
            },
            'price_range': '$10-15 per dozen',
            'description': 'Consistent accuracy nock'
        },
        {
            'manufacturer': 'Victory Archery',
            'model_name': 'VForce Nock',
            'specifications': {
                'nock_size': '0.245',
                'fit_type': 'push_in',
                'material': 'plastic',
                'colors': ['red', 'orange', 'yellow'],
                'weight': '6gr',
                'throat_size': 0.088
            },
            'price_range': '$12-16 per dozen',
            'description': 'High-performance nock system'
        }
    ]
    
    for nock in nocks_data:
        db.add_component('nocks', **nock)
    
    # Fletchings
    print("\n🪶 Adding fletchings...")
    fletchings_data = [
        {
            'manufacturer': 'Bohning',
            'model_name': 'Blazer Vane',
            'specifications': {
                'length': 2.0,
                'height': 0.5,
                'material': 'plastic',
                'profile': 'low',
                'attachment': 'adhesive',
                'colors': ['white', 'orange', 'yellow', 'red', 'blue'],
                'weight': '5gr'
            },
            'price_range': '$8-12 per dozen',
            'description': 'Popular low-profile hunting vane'
        },
        {
            'manufacturer': 'AAE',
            'model_name': 'Elite Plastinock',
            'specifications': {
                'length': 2.3,
                'height': 0.4,
                'material': 'plastic',
                'profile': 'low',
                'attachment': 'adhesive',
                'colors': ['white', 'orange', 'yellow'],
                'weight': '4gr'
            },
            'price_range': '$10-15 per dozen',
            'description': 'Professional grade fletching'
        },
        {
            'manufacturer': 'NAP',
            'model_name': 'QuikFletch',
            'specifications': {
                'length': 3.0,
                'height': 1.0,
                'material': 'plastic',
                'profile': 'high',
                'attachment': 'wrap',
                'colors': ['white', 'orange'],
                'weight': '12gr'
            },
            'price_range': '$15-20 per dozen',
            'description': 'Easy installation fletching system'
        }
    ]
    
    for fletching in fletchings_data:
        db.add_component('fletchings', **fletching)
    
    # Inserts
    print("\n🔩 Adding inserts...")
    inserts_data = [
        {
            'manufacturer': 'Easton Archery',
            'model_name': 'HIT Insert',
            'specifications': {
                'outer_diameter': 0.244,
                'inner_diameter': 0.204,
                'thread': '8-32',
                'length': 0.6,
                'weight': '12gr',
                'material': 'aluminum',
                'type': 'insert'
            },
            'price_range': '$15-20 per dozen',
            'description': 'Hidden Insert Technology (HIT) system'
        },
        {
            'manufacturer': 'Gold Tip',
            'model_name': 'Accu Insert',
            'specifications': {
                'outer_diameter': 0.246,
                'inner_diameter': 0.204,
                'thread': '8-32',
                'length': 0.5,
                'weight': '10gr',
                'material': 'aluminum',
                'type': 'insert'
            },
            'price_range': '$12-18 per dozen',
            'description': 'Precision machined aluminum insert'
        },
        {
            'manufacturer': 'Victory Archery',
            'model_name': 'VForce Insert',
            'specifications': {
                'outer_diameter': 0.245,
                'inner_diameter': 0.204,
                'thread': '8-32',
                'length': 0.55,
                'weight': '11gr',
                'material': 'stainless',
                'type': 'insert'
            },
            'price_range': '$18-25 per dozen',
            'description': 'Stainless steel precision insert'
        }
    ]
    
    for insert in inserts_data:
        db.add_component('inserts', **insert)
    
    # Bow Strings
    print("\n🎻 Adding bow strings...")
    strings_data = [
        {
            'manufacturer': 'BCY',
            'model_name': 'X99 String Material',
            'specifications': {
                'bow_type': 'compound',
                'length': 'custom',
                'strand_count': 24,
                'material': 'dyneema',
                'serving': 'not_included'
            },
            'price_range': '$40-60',
            'description': 'High-performance string material'
        },
        {
            'manufacturer': 'Winner\'s Choice',
            'model_name': 'Custom Compound String',
            'specifications': {
                'bow_type': 'compound',
                'length': 'custom',
                'strand_count': 26,
                'material': 'fastflight',
                'serving': 'included'
            },
            'price_range': '$80-120',
            'description': 'Professional custom bow string set'
        }
    ]
    
    for string in strings_data:
        db.add_component('strings', **string)
    
    # Arrow Rests
    print("\n🏹 Adding arrow rests...")
    rests_data = [
        {
            'manufacturer': 'QAD',
            'model_name': 'Ultra-Rest HDX',
            'specifications': {
                'bow_type': 'compound',
                'rest_type': 'drop_away',
                'adjustment': 'micro_adjust',
                'mounting': 'berger_hole'
            },
            'price_range': '$120-160',
            'description': 'Premium drop-away arrow rest'
        },
        {
            'manufacturer': 'Trophy Taker',
            'model_name': 'Smackdown Pro',
            'specifications': {
                'bow_type': 'compound',
                'rest_type': 'drop_away',
                'adjustment': 'micro_adjust',
                'mounting': 'berger_hole'
            },
            'price_range': '$140-180',
            'description': 'Competition-grade drop-away rest'
        },
        {
            'manufacturer': 'NAP',
            'model_name': 'Apache',
            'specifications': {
                'bow_type': 'recurve',
                'rest_type': 'magnetic',
                'adjustment': 'standard',
                'mounting': 'side_mount'
            },
            'price_range': '$30-50',
            'description': 'Traditional magnetic arrow rest'
        }
    ]
    
    for rest in rests_data:
        db.add_component('rests', **rest)
    
    # Accessories
    print("\n🎛️ Adding accessories...")
    accessories_data = [
        {
            'manufacturer': 'Spot Hogg',
            'model_name': 'Fast Eddie XL',
            'specifications': {
                'accessory_type': 'sight',
                'mounting': 'dovetail',
                'adjustment_range': 'micro'
            },
            'price_range': '$300-400',
            'description': 'Professional bow sight system'
        },
        {
            'manufacturer': 'Bee Stinger',
            'model_name': 'Microhex Stabilizer',
            'specifications': {
                'accessory_type': 'stabilizer',
                'mounting': 'screw_on',
                'adjustment_range': 'both'
            },
            'price_range': '$80-120',
            'description': 'Carbon fiber stabilizer system'
        },
        {
            'manufacturer': 'TruGlo',
            'model_name': 'Speed Shot XS',
            'specifications': {
                'accessory_type': 'release',
                'mounting': 'clamp',
                'adjustment_range': 'micro'
            },
            'price_range': '$60-90',
            'description': 'Adjustable wrist release'
        }
    ]
    
    for accessory in accessories_data:
        db.add_component('accessories', **accessory)
    
    # Get final statistics
    stats = db.get_component_statistics()
    print(f"\n📊 Final Component Database Statistics:")
    print(f"   Total components: {stats['total_components']}")
    
    for category in stats['categories']:
        print(f"   {category['name']}: {category['count']} components")
    
    print(f"\n✅ Component database population completed!")
    print(f"📝 Added components across {len(stats['categories'])} categories")
    
    return stats

if __name__ == "__main__":
    populate_component_database()