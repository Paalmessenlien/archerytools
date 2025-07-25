#!/usr/bin/env python3
"""
Add comprehensive wood arrow data to the arrow database
"""

import json
from arrow_database import ArrowDatabase

def add_comprehensive_wood_arrows_to_database():
    print("🌲 Adding comprehensive wood arrows to database...")
    
    # Load comprehensive wood arrow data
    try:
        with open('comprehensive_wood_arrows.json', 'r') as f:
            wood_data = json.load(f)
    except FileNotFoundError:
        print("❌ comprehensive_wood_arrows.json not found. Run parse_wood_arrows.py first.")
        return
    
    # Initialize database
    db = ArrowDatabase()
    
    print(f"📊 Current database stats before adding comprehensive wood arrows:")
    stats = db.get_statistics()
    print(f"   Total arrows: {stats['total_arrows']}")
    print(f"   Total manufacturers: {len(stats['manufacturers'])}")
    
    # Add comprehensive wood arrows
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
            print(f"   🌳 Wood type: {arrow_data['wood_type']}")
            print(f"   📐 Diameter: {arrow_data['diameter_inches']} ({arrow_data['diameter']}mm)")
            print(f"   ⚖️ GPI: {arrow_data['gpi_weight']}")
            print(f"   🎯 Recommended use: {arrow_data['recommended_use']}")
        else:
            print(f"   ❌ Failed to add arrow (may already exist)")
    
    print(f"\n✅ Comprehensive wood arrows added successfully!")
    print(f"   Arrows added: {total_arrows_added}")
    print(f"   Spine specifications added: {total_specs_added}")
    
    # Show updated stats
    print(f"\n📊 Updated database stats:")
    updated_stats = db.get_statistics()
    print(f"   Total arrows: {updated_stats['total_arrows']} (+{updated_stats['total_arrows'] - stats['total_arrows']})\"")
    print(f"   Total manufacturers: {len(updated_stats['manufacturers'])}")
    
    # Show manufacturers
    print(f"\n🏭 Manufacturers:")
    for mfr in updated_stats['manufacturers']:
        print(f"   {mfr['manufacturer']}: {mfr['arrow_count']} arrows")
    
    # Show wood arrow summary
    wood_arrows = [arrow for arrow in wood_data['arrows']]
    wood_types = list(set(arrow['wood_type'] for arrow in wood_arrows))
    spine_ranges = list(set(arrow['spine_options'] for arrow in wood_arrows))
    
    print(f"\n🌲 Wood Arrow Summary:")
    print(f"   Wood types: {', '.join(sorted(wood_types))}")
    print(f"   Spine ranges: {', '.join(sorted(spine_ranges))}")
    print(f"   Total spine specifications: {sum(len(arrow['spine_specifications']) for arrow in wood_arrows)}")
    
    print(f"\n📝 Notes from source document:")
    for note in wood_data['notes']:
        print(f"   • {note}")

if __name__ == "__main__":
    add_comprehensive_wood_arrows_to_database()