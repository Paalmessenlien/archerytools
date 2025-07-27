#!/usr/bin/env python3
"""
Test the fixed spine calculation for low draw weight recurve bows
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'arrow_scraper'))

from spine_calculator import SpineCalculator, BowConfiguration, BowType

def test_low_weight_recurve():
    print("🎯 Testing Fixed Recurve Spine Calculation")
    print("=" * 50)
    
    calculator = SpineCalculator()
    
    # Test the problematic case: 26 lbs recurve with 25" arrow length
    recurve_bow = BowConfiguration(
        draw_weight=26,
        draw_length=28,  # Draw length doesn't affect spine calculation
        bow_type=BowType.RECURVE
    )
    
    print("\n🏹 Problem Case: 26 lb recurve, 25\" arrow length")
    result = calculator.calculate_required_spine(
        recurve_bow,
        arrow_length=25,
        point_weight=100
    )
    
    print(f"   Calculated spine: {result['calculated_spine']}")
    print(f"   Spine range: {result['spine_range']['minimum']}-{result['spine_range']['maximum']}")
    print(f"   Base spine: {result['base_spine']}")
    print(f"   Adjustments: {result['adjustments']}")
    
    # Test a few more low draw weight cases
    test_cases = [
        {"weight": 20, "length": 26, "expected_range": "1800-2000"},
        {"weight": 25, "length": 25, "expected_range": "1700-1900"},
        {"weight": 30, "length": 26, "expected_range": "1200-1400"},
        {"weight": 35, "length": 28, "expected_range": "700-900"},
    ]
    
    print("\n📊 Additional Test Cases:")
    for case in test_cases:
        test_bow = BowConfiguration(
            draw_weight=case["weight"],
            draw_length=28,
            bow_type=BowType.RECURVE
        )
        
        result = calculator.calculate_required_spine(
            test_bow,
            arrow_length=case["length"],
            point_weight=100
        )
        
        print(f"   {case['weight']}# @ {case['length']}\": {result['calculated_spine']} (expected ~{case['expected_range']})")

if __name__ == "__main__":
    test_low_weight_recurve()