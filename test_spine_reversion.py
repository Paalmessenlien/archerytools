#!/usr/bin/env python3
"""
Test script to verify that spine calculation reversion worked correctly
"""
import sys
import os

# Add the arrow_scraper directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'arrow_scraper'))

from spine_service import calculate_unified_spine

def test_spine_calculations():
    """Test spine calculations to ensure reversion worked correctly"""
    
    print("🏹 Testing spine calculation reversion")
    print("=" * 50)
    
    # Test parameters
    test_cases = [
        {
            'name': 'Standard Compound Bow',
            'draw_weight': 50,
            'arrow_length': 28,
            'point_weight': 125,
            'bow_type': 'compound',
            'shooting_style': 'standard'
        },
        {
            'name': 'Recurve with Barebow style',
            'draw_weight': 40,
            'arrow_length': 28,
            'point_weight': 125,
            'bow_type': 'recurve',
            'shooting_style': 'barebow'
        },
        {
            'name': 'Recurve with Olympic style',
            'draw_weight': 40,
            'arrow_length': 28,
            'point_weight': 125,
            'bow_type': 'recurve',
            'shooting_style': 'olympic'
        },
        {
            'name': 'Traditional with Standard style',
            'draw_weight': 30,
            'arrow_length': 28,
            'point_weight': 125,
            'bow_type': 'traditional',
            'shooting_style': 'standard'
        },
        {
            'name': 'Traditional with Traditional style',
            'draw_weight': 30,
            'arrow_length': 28,
            'point_weight': 125,
            'bow_type': 'traditional',
            'shooting_style': 'traditional'
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📊 Testing: {test_case['name']}")
        print(f"   Bow: {test_case['bow_type']}, {test_case['draw_weight']}lbs")
        print(f"   Arrow: {test_case['arrow_length']}\", {test_case['point_weight']}gr point")
        print(f"   Style: {test_case['shooting_style']}")
        
        try:
            result = calculate_unified_spine(
                draw_weight=test_case['draw_weight'],
                arrow_length=test_case['arrow_length'],
                point_weight=test_case['point_weight'],
                bow_type=test_case['bow_type'],
                shooting_style=test_case['shooting_style']
            )
            
            print(f"   ✅ Result: {result['calculated_spine']} spine")
            print(f"   📏 Range: {result['spine_range']['minimum']} - {result['spine_range']['maximum']}")
            print(f"   🔧 Source: {result['source']}")
            
            # Print shooting style adjustment if any
            if 'adjustments' in result['calculations']:
                adjustments = result['calculations']['adjustments']
                if 'shooting_style_adjustment' in adjustments and adjustments['shooting_style_adjustment'] != 0:
                    print(f"   🎯 Shooting style adjustment: {adjustments['shooting_style_adjustment']:+.1f} spine")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Test completed!")

def test_original_formula():
    """Test that original simple formula is working"""
    print("\n🧮 Testing original formula logic")
    print("=" * 30)
    
    # Test case: 50lb compound, 28" arrow, 125gr point
    # Original formula should be: 50 * 12.5 = 625 base spine
    draw_weight = 50
    arrow_length = 28
    point_weight = 125
    
    expected_base = draw_weight * 12.5  # Should be 625
    length_adj = (arrow_length - 28) * 25  # Should be 0
    point_adj = (point_weight - 125) * 0.5  # Should be 0
    bow_type_adj = 0  # Compound = 0
    
    expected_result = expected_base + length_adj + point_adj + bow_type_adj
    
    print(f"Expected calculation for 50lb compound:")
    print(f"  Base spine: {expected_base}")
    print(f"  Length adj: {length_adj}")
    print(f"  Point adj: {point_adj}")
    print(f"  Bow type adj: {bow_type_adj}")
    print(f"  Expected result: {expected_result}")
    
    # Test actual calculation
    result = calculate_unified_spine(
        draw_weight=50,
        arrow_length=28,
        point_weight=125,
        bow_type='compound',
        shooting_style='standard'
    )
    
    actual_result = result['calculated_spine']
    print(f"  Actual result: {actual_result}")
    
    if actual_result == expected_result:
        print("  ✅ Original formula working correctly!")
    else:
        print(f"  ❌ Formula mismatch! Expected {expected_result}, got {actual_result}")

if __name__ == '__main__':
    test_spine_calculations()
    test_original_formula()