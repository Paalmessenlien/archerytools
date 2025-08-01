#!/usr/bin/env python3
"""
Simple integration to show how components relate to arrows
Works with current database schema
"""

from component_database import ComponentDatabase
from arrow_database import ArrowDatabase

def show_component_arrow_integration():
    """Demonstrate how components can be matched with arrows"""
    
    print("🔗 Component-Arrow Integration Demonstration")
    print("=" * 60)
    
    # Initialize databases
    arrow_db = ArrowDatabase()
    component_db = ComponentDatabase()
    
    # Get sample data
    components = component_db.get_components('inserts', limit=5)
    arrows = arrow_db.search_arrows(limit=10)
    
    print(f"📊 Database Summary:")
    arrow_stats = arrow_db.get_statistics()
    component_stats = component_db.get_component_statistics()
    print(f"   Arrows: {arrow_stats['total_arrows']} total")
    print(f"   Components: {component_stats['total_components']} total")
    print()
    
    print("🔧 Sample Inserts with Specifications:")
    for component in components:
        if component['manufacturer'] == 'Tophat Archery':
            specs = component['specifications']
            print(f"   • {component['model_name']}")
            print(f"     Inner Diameter: {specs.get('inner_diameter_inch', 'N/A')}\"")
            print(f"     Outer Diameter: {specs.get('outer_diameter_inch', 'N/A')}\"")
            print(f"     Weight: {specs.get('weight_grain', 'N/A')}gr")
            print(f"     Compatibility: {specs.get('compatibility', ['N/A'])[0]}")
            print()
    
    print("🏹 Sample Arrows with Inner Diameters:")
    for arrow in arrows[:5]:
        details = arrow_db.get_arrow_details(arrow['id'])
        if details and details.get('spine_specifications'):
            spine_specs = details['spine_specifications']
            print(f"   • {arrow['manufacturer']} {arrow['model_name']}")
            for spec in spine_specs[:2]:  # Show first 2 spine options
                inner_d = spec.get('inner_diameter', 'N/A')
                outer_d = spec.get('outer_diameter', 'N/A')
                print(f"     Spine {spec['spine']}: ID {inner_d}\", OD {outer_d}\"")
            print()
    
    print("💡 Integration Possibilities:")
    print("   1. Match insert outer diameter to arrow inner diameter")
    print("   2. Match point inner diameter to arrow outer diameter")
    print("   3. Use compatibility strings to find specific arrow models")
    print("   4. Create compatibility scoring based on dimensional fit")
    print()
    
    # Example matching
    print("🎯 Example Compatibility Analysis:")
    tophat_insert = None
    for comp in components:
        if comp['manufacturer'] == 'Tophat Archery' and 'Insert' in comp['model_name']:
            tophat_insert = comp
            break
    
    if tophat_insert:
        specs = tophat_insert['specifications']
        insert_od = specs.get('outer_diameter_inch')
        print(f"Insert: {tophat_insert['model_name']}")
        print(f"   Outer Diameter: {insert_od}\"")
        print()
        
        if insert_od:
            print("Compatible arrows (where insert OD fits arrow ID):")
            matches = 0
            for arrow in arrows:
                details = arrow_db.get_arrow_details(arrow['id'])
                if details and details.get('spine_specifications'):
                    for spec in details['spine_specifications']:
                        arrow_id = spec.get('inner_diameter')
                        if arrow_id and insert_od <= arrow_id:
                            fit_tolerance = arrow_id - insert_od
                            print(f"   ✅ {arrow['manufacturer']} {arrow['model_name']} (spine {spec['spine']})")
                            print(f"      Arrow ID: {arrow_id}\", Fit tolerance: {fit_tolerance:.3f}\"")
                            matches += 1
                            break
                        
            print(f"\nFound {matches} potentially compatible arrows!")
    
    print("\n📋 Next Steps for Full Integration:")
    print("   1. Create compatibility relationships in arrow_component_compatibility table")
    print("   2. Implement compatibility scoring algorithm")
    print("   3. Add API endpoints to find components for specific arrows")
    print("   4. Include component recommendations in arrow tuning system")

if __name__ == "__main__":
    show_component_arrow_integration()