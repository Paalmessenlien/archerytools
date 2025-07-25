#!/usr/bin/env python3
"""
Debug the material issue in compatible arrows
"""

from arrow_database import ArrowDatabase

def debug_material_issue():
    """Debug what's causing the None material issue"""
    
    print("🔧 Debugging material issue...")
    
    db = ArrowDatabase()
    
    # Search arrows like the API does
    compatible_arrows = db.search_arrows(
        manufacturer=None,
        arrow_type=None,
        model_search=None,
        limit=50
    )
    
    print(f"Found {len(compatible_arrows)} arrows from search")
    
    print("\n🔍 Checking material values:")
    none_count = 0
    for i, arrow in enumerate(compatible_arrows):
        material = arrow.get('material')
        if material is None:
            none_count += 1
            print(f"   {i:2d}. ID:{arrow.get('id')} {arrow.get('manufacturer', 'N/A')} {arrow.get('model_name', 'N/A')} | Material: {material}")
    
    print(f"\n📊 Found {none_count} arrows with None material")
    
    # Now test the filtering logic with these arrows
    print(f"\n🔧 Testing filtering logic:")
    
    bow_config = {
        'arrow_material': 'wood'
    }
    
    filtered_count = 0
    error_count = 0
    
    for arrow in compatible_arrows:
        try:
            # This is the logic from the API
            is_compatible = True
            
            if bow_config.get('arrow_material'):
                arrow_material = arrow.get('material', '').lower()  # This line causes the error
                selected_material = bow_config['arrow_material'].lower()
                
                if selected_material == 'wood':
                    if 'wood' not in arrow_material:
                        is_compatible = False
            
            if is_compatible:
                filtered_count += 1
                
        except Exception as e:
            error_count += 1
            print(f"   ❌ Error with arrow {arrow.get('id')}: {e}")
            print(f"      Material value: {repr(arrow.get('material'))}")
    
    print(f"\n📊 Results:")
    print(f"   Filtered count: {filtered_count}")
    print(f"   Error count: {error_count}")

if __name__ == "__main__":
    debug_material_issue()