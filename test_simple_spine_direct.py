#!/usr/bin/env python3
"""Test the corrected simple spine calculation directly"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'arrow_scraper'))

from arrow_scraper.spine_service import UnifiedSpineService

def test_simple_calculation_direct():
    """Test the corrected simple calculation directly"""
    
    print("🧪 Testing Corrected Simple Spine Calculation Directly")
    print("=" * 60)
    
    service = UnifiedSpineService()
    
    # Test case that should use German formula
    result = service._calculate_simple_spine(
        draw_weight=40,
        arrow_length=28,
        point_weight=125,
        bow_type='recurve',
        string_material='fastflight'
    )
    
    print("📋 Simple Calculation Result:")
    import json
    print(json.dumps(result, indent=2))
    
    # Expected calculation:
    # Base: 1100 - (40 * 10) = 700
    # Length: (28 - 28) * 25 = 0  
    # Point: (125 - 125) * 0.5 = 0
    # String: 0 (FastFlight baseline)
    # Total: 700
    
    expected_spine = 700  # German formula result
    actual_spine = result['calculated_spine']
    
    print(f"\n🎯 Expected (German formula): {expected_spine}")
    print(f"📊 Actual result: {actual_spine}")
    print(f"📏 Difference: {actual_spine - expected_spine:+d}")
    
    if actual_spine == expected_spine:
        print("✅ PASS - Calculation matches German formula!")
    else:
        print("❌ FAIL - Calculation does not match German formula")
        
    # Test with traditional bow (should be same as recurve)
    print("\n" + "-" * 40)
    result_trad = service._calculate_simple_spine(
        draw_weight=40,
        arrow_length=28,
        point_weight=125,
        bow_type='traditional',
        string_material='dacron'  # +15 adjustment
    )
    
    expected_trad = 715  # 700 + 15 for Dacron
    actual_trad = result_trad['calculated_spine']
    
    print(f"Traditional + Dacron Expected: {expected_trad}")
    print(f"Traditional + Dacron Actual: {actual_trad}")
    print(f"Difference: {actual_trad - expected_trad:+d}")

if __name__ == "__main__":
    try:
        test_simple_calculation_direct()
    except Exception as e:
        print(f"❌ Testing failed: {e}")
        import traceback
        traceback.print_exc()