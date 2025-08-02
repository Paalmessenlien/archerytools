#!/usr/bin/env python3
"""
Enhanced Spine Calculation Test Suite
Tests all improvements made to the spine calculation system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from arrow_scraper.spine_calculator import SpineCalculator, BowConfiguration, BowType

def test_phase_1_critical_fixes():
    """Test Phase 1 critical fixes: recurve calculations, speed adjustments, point weight precision"""
    
    calculator = SpineCalculator()
    print("=" * 80)
    print("PHASE 1 CRITICAL FIXES TESTING")
    print("=" * 80)
    
    # Test 1.1: Fixed Recurve Bow Calculations
    print("\n1.1 RECURVE BOW CALCULATION FIX")
    print("-" * 40)
    
    recurve_config = BowConfiguration(
        draw_weight=35.0,
        draw_length=28.0,
        bow_type=BowType.RECURVE,
        release_type="finger"
    )
    
    result = calculator.calculate_required_spine(
        bow_config=recurve_config,
        arrow_length=30.0,
        point_weight=125.0
    )
    
    print(f"35# Recurve @ 30\" with 125gr point:")
    print(f"  Calculated spine: {result['calculated_spine']}")
    print(f"  Expected (Easton chart): ~500")
    print(f"  Difference: {abs(result['calculated_spine'] - 500)}")
    print(f"  FIXED: {'✅' if abs(result['calculated_spine'] - 500) < 100 else '❌'}")
    
    # Test 1.2: IBO Speed Adjustments
    print("\n1.2 IBO SPEED ADJUSTMENTS")
    print("-" * 40)
    
    # Test different IBO speeds
    speed_tests = [
        (270, "Slow bow", -10),
        (295, "Medium-slow", -5), 
        (315, "Baseline", 0),
        (335, "Fast", +5),
        (355, "Very fast", +15)
    ]
    
    for ibo_speed, description, expected_adjustment in speed_tests:
        compound_config = BowConfiguration(
            draw_weight=45.0,
            draw_length=28.0,
            bow_type=BowType.COMPOUND,
            ibo_speed=ibo_speed
        )
        
        result = calculator.calculate_required_spine(
            bow_config=compound_config,
            arrow_length=29.0,
            point_weight=100.0
        )
        
        actual_adjustment = result['adjustments'].get('bow_speed', 0)
        print(f"  {ibo_speed} FPS ({description}): {actual_adjustment:+.1f} lbs (expected: {expected_adjustment:+.1f})")
    
    # Test 1.3: Enhanced Point Weight Precision
    print("\n1.3 ENHANCED POINT WEIGHT PRECISION")
    print("-" * 40)
    
    compound_config = BowConfiguration(
        draw_weight=45.0,
        draw_length=28.0,
        bow_type=BowType.COMPOUND
    )
    
    point_weight_tests = [
        (75, -3),   # 25gr under 100gr = -3 lbs
        (100, 0),   # Baseline
        (125, 3),   # 25gr over 100gr = +3 lbs
        (150, 6),   # 50gr over 100gr = +6 lbs
    ]
    
    for point_weight, expected_adjustment in point_weight_tests:
        result = calculator.calculate_required_spine(
            bow_config=compound_config,
            arrow_length=29.0,
            point_weight=point_weight
        )
        
        actual_adjustment = result['adjustments'].get('point_weight', 0)
        print(f"  {point_weight}gr point: {actual_adjustment:+.1f} lbs (expected: {expected_adjustment:+.1f})")


def test_comprehensive_spine_accuracy():
    """Test spine calculation accuracy against known manufacturer charts"""
    
    calculator = SpineCalculator()
    print("\n" + "=" * 80)
    print("COMPREHENSIVE SPINE ACCURACY TESTING")
    print("=" * 80)
    
    # Test cases based on manufacturer charts
    test_cases = [
        # Format: (bow_type, draw_weight, arrow_length, point_weight, expected_spine, description)
        (BowType.COMPOUND, 45, 29, 100, 400, "45# compound, 29\", 100gr"),
        (BowType.COMPOUND, 60, 28, 100, 340, "60# compound, 28\", 100gr"),
        (BowType.RECURVE, 35, 30, 125, 500, "35# recurve, 30\", 125gr"),
        (BowType.RECURVE, 50, 29, 100, 400, "50# recurve, 29\", 100gr"),
        (BowType.COMPOUND, 70, 30, 100, 300, "70# compound, 30\", 100gr"),
    ]
    
    print("Testing against known manufacturer chart values:")
    print("-" * 60)
    
    for bow_type, draw_weight, arrow_length, point_weight, expected_spine, description in test_cases:
        bow_config = BowConfiguration(
            draw_weight=draw_weight,
            draw_length=28.0,
            bow_type=bow_type,
            release_type="finger" if bow_type == BowType.RECURVE else "mechanical"
        )
        
        result = calculator.calculate_required_spine(
            bow_config=bow_config,
            arrow_length=arrow_length,
            point_weight=point_weight
        )
        
        calculated = result['calculated_spine']
        difference = abs(calculated - expected_spine)
        tolerance = 50 if bow_type == BowType.RECURVE else 25
        passed = difference <= tolerance
        
        print(f"{description}:")
        print(f"  Calculated: {calculated}, Expected: {expected_spine}")
        print(f"  Difference: {difference} ({'✅ PASS' if passed else '❌ FAIL'})")
        print()


def test_wood_arrow_calculations():
    """Test wood arrow spine calculations"""
    
    calculator = SpineCalculator()
    print("=" * 80)
    print("WOOD ARROW CALCULATION TESTING")
    print("=" * 80)
    
    traditional_config = BowConfiguration(
        draw_weight=45.0,
        draw_length=28.0,
        bow_type=BowType.TRADITIONAL
    )
    
    result = calculator.calculate_required_spine(
        bow_config=traditional_config,
        arrow_length=29.0,
        point_weight=125.0,
        material_preference="wood"
    )
    
    print(f"45# Traditional bow, 29\" arrow, 125gr point (wood):")
    print(f"  Calculated spine: {result['calculated_spine']} pounds")
    print(f"  Spine units: {result.get('spine_units', 'carbon')}")
    print(f"  Base spine: {result['base_spine']}")
    print(f"  Adjustments: {result['adjustments']}")


def main():
    """Run all enhanced spine calculation tests"""
    
    print("Enhanced Spine Calculation Test Suite")
    print("Testing all Phase 1-4 improvements")
    print("Generated: August 2025")
    
    try:
        test_phase_1_critical_fixes()
        test_comprehensive_spine_accuracy()
        test_wood_arrow_calculations()
        
        print("\n" + "=" * 80)
        print("TEST SUITE COMPLETED")
        print("=" * 80)
        print("All enhanced spine calculation features tested.")
        print("Check output above for any ❌ FAIL results that need attention.")
        
    except Exception as e:
        print(f"ERROR during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()