#!/usr/bin/env python3
"""Test low draw weight spine calculation issue"""

from arrow_scraper.spine_calculator import SpineCalculator, BowConfiguration, BowType
from arrow_scraper.arrow_database import ArrowDatabase

def test_low_draw_weight_issue():
    print("🎯 Testing Low Draw Weight Issue")
    print("=" * 50)
    
    # Test the exact scenario: 24 lbs recurve with 26" arrow
    calculator = SpineCalculator()
    
    bow_config = BowConfiguration(
        draw_weight=24,
        draw_length=28,  # This doesn't affect spine calculation
        bow_type=BowType.RECURVE
    )
    
    # Calculate spine for 26" arrow
    result = calculator.calculate_required_spine(
        bow_config, 
        arrow_length=26, 
        point_weight=100
    )
    
    print(f"📊 Calculation Results:")
    print(f"   Calculated spine: {result['calculated_spine']}")
    print(f"   Spine range: {result['spine_range']['minimum']}-{result['spine_range']['maximum']}")
    
    # Check what spine values are actually available in the database
    db = ArrowDatabase()
    
    print(f"\n🔍 Checking database for spine range {result['spine_range']['minimum']}-{result['spine_range']['maximum']}:")
    
    # Test current search method
    search_results = db.search_arrows(
        spine_min=result['spine_range']['minimum'],
        spine_max=result['spine_range']['maximum'],
        limit=10
    )
    
    print(f"   Found {len(search_results)} arrows with exact spine range")
    
    if search_results:
        for arrow in search_results[:3]:
            print(f"   - {arrow['manufacturer']} {arrow['model_name']} (spine: {arrow['min_spine']}-{arrow['max_spine']})")
    
    # Now check all available spine values to see what's closest
    print(f"\n🎯 Finding closest available spine values:")
    
    # Get all unique spine values from database using the database methods
    # Let's search for a very wide range to see all available spines
    all_arrows_search = db.search_arrows(spine_min=1, spine_max=10000, limit=1000)
    all_spines = set()
    
    for arrow in all_arrows_search:
        if arrow.get('min_spine'):
            all_spines.add(arrow['min_spine'])
        if arrow.get('max_spine'):
            all_spines.add(arrow['max_spine'])
    
    all_spines = sorted([s for s in all_spines if s is not None])
    
    target_spine = result['calculated_spine']
    closest_spines = []
    
    # Find the 5 closest spine values
    for spine in all_spines:
        if spine is not None:
            deviation = abs(spine - target_spine)
            closest_spines.append((spine, deviation))
    
    closest_spines.sort(key=lambda x: x[1])
    
    print(f"   Target spine: {target_spine}")
    print(f"   5 closest available spines:")
    for spine, deviation in closest_spines[:5]:
        print(f"   - {spine} (deviation: ±{deviation:.0f})")
    
    # Test search with expanded range
    print(f"\n🔄 Testing expanded spine search:")
    expanded_search = db.search_arrows(
        spine_min=closest_spines[0][0] - 100,  # Much wider range
        spine_max=closest_spines[4][0] + 100,
        limit=10
    )
    
    print(f"   Found {len(expanded_search)} arrows with expanded range")
    if expanded_search:
        for arrow in expanded_search[:3]:
            print(f"   - {arrow['manufacturer']} {arrow['model_name']} (spine: {arrow['min_spine']}-{arrow['max_spine']})")

if __name__ == "__main__":
    test_low_draw_weight_issue()