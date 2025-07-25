#!/usr/bin/env python3
"""
Test wood arrow functionality
"""

from arrow_database import ArrowDatabase

def test_wood_arrows():
    """Test wood arrow spine formatting and retrieval"""
    
    print("🌲 Testing wood arrow functionality...")
    
    # Initialize database
    db = ArrowDatabase()
    
    # Test wood arrow search
    print("\n🔍 Searching for wood arrows...")
    wood_arrows = db.search_arrows(manufacturer="Traditional Wood", limit=20)
    
    print(f"Found {len(wood_arrows)} arrows from Traditional Wood manufacturer:")
    
    # Also search for the newer comprehensive wood arrows
    comprehensive_wood_arrows = db.search_arrows(manufacturer="Traditional Wood Arrows", limit=20)
    
    print(f"Found {len(comprehensive_wood_arrows)} arrows from Traditional Wood Arrows manufacturer:")
    
    # Combine both results
    all_wood_arrows = wood_arrows + comprehensive_wood_arrows
    wood_arrows = all_wood_arrows
    
    print(f"Found {len(wood_arrows)} wood arrows:")
    
    for arrow in wood_arrows[:5]:
        print(f"\n🎯 {arrow['manufacturer']} - {arrow['model_name']}")
        print(f"   Material: {arrow['material']}")
        print(f"   Spine range: {arrow['min_spine']}-{arrow['max_spine']}")
        print(f"   Spine display: {arrow['spine_display']}")
        print(f"   Diameter: {arrow.get('min_diameter', 'N/A')}-{arrow.get('max_diameter', 'N/A')}")
        print(f"   GPI: {arrow.get('min_gpi', 'N/A')}-{arrow.get('max_gpi', 'N/A')}")
    
    # Test material filtering
    print(f"\n🔍 Testing material filtering...")
    search_results = db.search_arrows(limit=50)
    
    # Simulate frontend filtering logic
    for arrow in search_results[:3]:
        arrow_material = arrow.get('material', '').lower()
        
        # Test wood filter
        is_wood_match = 'wood' in arrow_material
        print(f"   {arrow['model_name'][:30]:30} | Material: {arrow['material']:20} | Wood match: {is_wood_match}")

if __name__ == "__main__":
    test_wood_arrows()