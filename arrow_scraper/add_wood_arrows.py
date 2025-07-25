#!/usr/bin/env python3
"""
Add wood arrow data to the arrow database
"""

import json
from arrow_database import ArrowDatabase

def add_wood_arrows_to_database():
    print("🌲 Adding wood arrows to database...")
    
    # Load wood arrow data
    try:
        with open('wood_arrows_data.json', 'r') as f:
            wood_data = json.load(f)
    except FileNotFoundError:
        print("❌ wood_arrows_data.json not found. Run extract_excel_data.py first.")
        return
    
    # Initialize database
    db = ArrowDatabase()
    
    print(f"📊 Current database stats before adding wood arrows:")
    stats = db.get_statistics()
    print(f"   Total arrows: {stats['total_arrows']}")
    print(f"   Total manufacturers: {len(stats['manufacturers'])}")
    
    # Add wood arrows
    total_arrows_added = 0
    total_specs_added = 0
    
    for arrow_data in wood_data['arrows']:
        print(f"\n🎯 Adding {arrow_data['model_name']}...")
        
        # Add the arrow
        arrow_id = db._add_arrow(arrow_data, wood_data['manufacturer'])
        
        if arrow_id:
            total_arrows_added += 1
            print(f"   ✅ Arrow added with ID: {arrow_id}")
            
            # Add spine specifications
            for spec in arrow_data['spine_specifications']:
                if db._add_spine_specification(arrow_id, spec):
                    total_specs_added += 1
            
            print(f"   📏 Added {len(arrow_data['spine_specifications'])} spine specifications")
        else:
            print(f"   ❌ Failed to add arrow (may already exist)")
    
    print(f"\n✅ Wood arrows added successfully!")
    print(f"   Arrows added: {total_arrows_added}")
    print(f"   Spine specifications added: {total_specs_added}")
    
    # Show updated stats
    print(f"\n📊 Updated database stats:")
    updated_stats = db.get_statistics()
    print(f"   Total arrows: {updated_stats['total_arrows']} (+{updated_stats['total_arrows'] - stats['total_arrows']})")
    print(f"   Total manufacturers: {len(updated_stats['manufacturers'])}")
    
    # Show manufacturers
    print(f"\n🏭 Manufacturers:")
    for mfr in updated_stats['manufacturers']:
        print(f"   {mfr['manufacturer']}: {mfr['arrow_count']} arrows")

if __name__ == "__main__":
    add_wood_arrows_to_database()