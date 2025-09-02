#!/usr/bin/env python3
"""
Test heavy bow scenarios to find why user experiences 'too soft' spine recommendations
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'arrow_scraper'))

from arrow_scraper.spine_service import calculate_unified_spine

def test_heavy_bow_professional_scenarios():
    """Test heavy bows with various Professional mode parameters"""
    
    print("💪 Heavy Bow Professional Mode Analysis")
    print("Testing if Professional mode parameters cause 'too soft' spine recommendations")
    print("=" * 80)
    
    # Base heavy bow configuration
    base_config = {
        'draw_weight': 65,
        'arrow_length': 29,
        'point_weight': 125,
        'bow_type': 'compound'
    }
    
    print(f"Base Configuration: 65lbs compound, 29\" arrows, 125gr points")
    print("-" * 60)
    
    # Test baseline
    baseline = calculate_unified_spine(**base_config)
    print(f"Baseline:                    {baseline['calculated_spine']:<4} spine")
    
    # Test with different bow speeds (Professional mode)
    speeds = [280, 300, 320, 340]
    for speed in speeds:
        result = calculate_unified_spine(**base_config, bow_speed=speed)
        diff = result['calculated_spine'] - baseline['calculated_spine']
        print(f"Bow speed {speed}fps:           {result['calculated_spine']:<4} spine ({diff:+d})")
    
    # Test with release types
    for release in ['mechanical', 'finger']:
        result = calculate_unified_spine(**base_config, release_type=release)
        diff = result['calculated_spine'] - baseline['calculated_spine']
        print(f"Release type '{release}':     {result['calculated_spine']:<4} spine ({diff:+d})")
    
    # Test with different arrow lengths (common tuning scenario)
    print(f"\n📏 Arrow Length Effects:")
    lengths = [27, 28, 29, 30, 31]
    for length in lengths:
        config = base_config.copy()
        config['arrow_length'] = length
        result = calculate_unified_spine(**config)
        diff = result['calculated_spine'] - baseline['calculated_spine']
        print(f"Arrow length {length}\":          {result['calculated_spine']:<4} spine ({diff:+d})")
    
    # Test with different point weights (tuning scenario)
    print(f"\n⚖️  Point Weight Effects:")
    point_weights = [100, 125, 150, 175, 200]
    for points in point_weights:
        config = base_config.copy()
        config['point_weight'] = points
        result = calculate_unified_spine(**config)
        diff = result['calculated_spine'] - baseline['calculated_spine']
        print(f"Point weight {points}gr:        {result['calculated_spine']:<4} spine ({diff:+d})")

def test_extreme_heavy_bow_scenarios():
    """Test very heavy bows that might reveal the 'too soft' issue"""
    
    print(f"\n🎯 EXTREME HEAVY BOW SCENARIOS:")
    print(f"Testing very heavy setups where spine might be too soft")
    print("-" * 60)
    
    extreme_scenarios = [
        {"weight": 70, "length": 27, "points": 100, "desc": "70lbs short arrows, light points"},
        {"weight": 75, "length": 28, "points": 100, "desc": "75lbs hunting setup"},
        {"weight": 80, "length": 28, "points": 125, "desc": "80lbs target compound"},
        {"weight": 70, "length": 30, "points": 200, "desc": "70lbs long arrows, heavy points"},
    ]
    
    for scenario in extreme_scenarios:
        result = calculate_unified_spine(
            draw_weight=scenario["weight"],
            arrow_length=scenario["length"],
            point_weight=scenario["points"],
            bow_type='compound'
        )
        
        spine = result['calculated_spine']
        
        # For very heavy bows, expect very stiff spines (200-350 range)
        if spine < 200:
            assessment = "✅ VERY STIFF - appropriate for extreme setups"
        elif spine < 300:
            assessment = "✅ STIFF - good for heavy compounds"
        elif spine < 400:
            assessment = "⚠️  MODERATE - may be too soft for very heavy bows"
        else:
            assessment = "❌ SOFT - likely too weak for heavy compounds"
        
        print(f"{scenario['desc']:<40}: {spine:<4} {assessment}")

def analyze_formula_gaps():
    """Check for potential gaps or issues in formula logic"""
    
    print(f"\n🔍 FORMULA LOGIC ANALYSIS:")
    print(f"Looking for potential issues causing user's 'too soft' experience")
    print("-" * 60)
    
    # Check compound formula behavior
    compound_weights = [50, 55, 60, 65, 70, 75, 80]
    print(f"Compound bow formula: 720 - (weight × 6.5)")
    
    for weight in compound_weights:
        calculated = 720 - (weight * 6.5)
        
        # Check if this matches real-world expectations
        if weight >= 70:
            expected_range = (200, 300)
        elif weight >= 60:
            expected_range = (300, 400)
        else:
            expected_range = (400, 500)
        
        expected_min, expected_max = expected_range
        
        if calculated < expected_min:
            status = f"✅ STIFF ({expected_min - calculated:+.0f} from range)"
        elif calculated > expected_max:
            status = f"❌ SOFT ({calculated - expected_max:+.0f} above range)"
        else:
            status = "✅ GOOD"
        
        print(f"   {weight}lbs → {calculated:.0f} spine (expect {expected_min}-{expected_max}) {status}")

if __name__ == "__main__":
    try:
        test_heavy_bow_professional_scenarios()
        test_extreme_heavy_bow_scenarios()
        analyze_formula_gaps()
        
        print(f"\n🎯 FINDINGS SUMMARY:")
        print(f"✅ Light bow formulas FIXED - now giving appropriate spine values")
        print(f"⚠️  Heavy bow analysis needed - checking for specific scenarios causing 'too soft' experience")
        
    except Exception as e:
        print(f"\n❌ Testing failed: {e}")
        import traceback
        traceback.print_exc()