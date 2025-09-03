#!/usr/bin/env python3
"""
Test spine calculations that match user's experience of:
- Light bows giving too stiff spines
- Heavy bows giving too soft spines
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'arrow_scraper'))

from arrow_scraper.spine_service import calculate_unified_spine

def test_user_experience_scenarios():
    """Test scenarios that might reveal the user's experienced issues"""
    
    print("🎯 User Experience Scenario Testing")
    print("Testing specific scenarios where calculations might not match real-world expectations")
    print("=" * 80)
    
    # Scenario 1: Light traditional bows with different arrow lengths
    print(f"\n🏹 LIGHT TRADITIONAL BOW SCENARIOS:")
    print(f"Testing various configurations that might give 'too stiff' results")
    print("-" * 60)
    
    light_scenarios = [
        {"weight": 25, "length": 26, "points": 100, "desc": "25lbs youth bow, short arrows, light points"},
        {"weight": 25, "length": 28, "points": 125, "desc": "25lbs youth bow, standard setup"},  
        {"weight": 25, "length": 30, "points": 145, "desc": "25lbs youth bow, long arrows, heavy points"},
        {"weight": 30, "length": 28, "points": 125, "desc": "30lbs beginner traditional"},
        {"weight": 35, "length": 28, "points": 125, "desc": "35lbs traditional recurve"},
    ]
    
    for scenario in light_scenarios:
        result = calculate_unified_spine(
            draw_weight=scenario["weight"],
            arrow_length=scenario["length"], 
            point_weight=scenario["points"],
            bow_type='traditional',
            string_material='dacron'  # Traditional string
        )
        
        spine = result['calculated_spine']
        
        # Evaluate if result seems appropriate for traditional archery
        if spine > 850:
            assessment = "❌ VERY WEAK - may be too soft for beginners"
        elif spine > 750:
            assessment = "⚠️  WEAK - check if appropriate for traditional"
        elif spine > 650:
            assessment = "✅ GOOD - traditional range"
        else:
            assessment = "❌ STIFF - may be too hard for traditional"
        
        print(f"{scenario['desc']:<45}: {spine:<4} {assessment}")
    
    # Scenario 2: Heavy compound bows
    print(f"\n💪 HEAVY COMPOUND BOW SCENARIOS:")
    print(f"Testing configurations that might give 'too soft' results")
    print("-" * 60)
    
    heavy_scenarios = [
        {"weight": 60, "length": 28, "points": 100, "desc": "60lbs hunting compound, light points"},
        {"weight": 65, "length": 29, "points": 125, "desc": "65lbs target compound, standard setup"},
        {"weight": 70, "length": 30, "points": 150, "desc": "70lbs heavy compound, long arrows"},
        {"weight": 75, "length": 28, "points": 125, "desc": "75lbs high-performance compound"},
        {"weight": 80, "length": 28, "points": 100, "desc": "80lbs extreme compound"},
    ]
    
    for scenario in heavy_scenarios:
        result = calculate_unified_spine(
            draw_weight=scenario["weight"],
            arrow_length=scenario["length"],
            point_weight=scenario["points"], 
            bow_type='compound'
        )
        
        spine = result['calculated_spine']
        
        # Evaluate if result seems appropriate for heavy compound bows
        if spine < 200:
            assessment = "❌ VERY STIFF - extremely low spine"
        elif spine < 300:
            assessment = "✅ STIFF - appropriate for heavy compound"
        elif spine < 400:
            assessment = "✅ GOOD - standard compound range"
        else:
            assessment = "❌ SOFT - may be too weak for heavy bow"
        
        print(f"{scenario['desc']:<45}: {spine:<4} {assessment}")

def test_professional_mode_effects():
    """Test if Professional mode parameters are causing the discrepancy"""
    
    print(f"\n🎓 PROFESSIONAL MODE PARAMETER EFFECTS:")
    print(f"Testing if bow speed and release type adjustments cause issues")
    print("-" * 60)
    
    base_config = {
        'draw_weight': 35,
        'arrow_length': 28,
        'point_weight': 125,
        'bow_type': 'recurve'
    }
    
    # Test baseline
    baseline = calculate_unified_spine(**base_config)
    print(f"Baseline (35lbs recurve):     {baseline['calculated_spine']}")
    
    # Test with finger release (should add ~5lbs effective weight)
    finger_result = calculate_unified_spine(**base_config, release_type='finger')
    print(f"With finger release:         {finger_result['calculated_spine']}")
    
    # Test with slow bow speed (should subtract weight)
    slow_result = calculate_unified_spine(**base_config, bow_speed=180)
    print(f"With slow bow (180fps):      {slow_result['calculated_spine']}")
    
    # Test with fast bow speed (should add weight)  
    fast_result = calculate_unified_spine(**base_config, bow_speed=220)
    print(f"With fast bow (220fps):      {fast_result['calculated_spine']}")
    
    print(f"\n🔍 Analysis:")
    print(f"Finger release effect: {finger_result['calculated_spine'] - baseline['calculated_spine']:+d} spine")
    print(f"Slow bow effect:       {slow_result['calculated_spine'] - baseline['calculated_spine']:+d} spine")
    print(f"Fast bow effect:       {fast_result['calculated_spine'] - baseline['calculated_spine']:+d} spine")

def test_real_world_expectations():
    """Test against expected real-world values"""
    
    print(f"\n🌍 REAL-WORLD EXPECTATION TESTING:")
    print(f"Testing against typical archer equipment choices")
    print("-" * 60)
    
    real_world_cases = [
        {
            'config': {'weight': 25, 'length': 28, 'bow': 'recurve'},
            'expected_spine_range': (650, 750),
            'common_choice': "700-750 spine (youth traditional)",
            'reason': "Beginner traditional bows need moderate spine"
        },
        {
            'config': {'weight': 35, 'length': 28, 'bow': 'recurve'}, 
            'expected_spine_range': (600, 700),
            'common_choice': "600-650 spine (entry traditional)",
            'reason': "Entry-level traditional needs moderate-stiff spine"
        },
        {
            'config': {'weight': 60, 'length': 28, 'bow': 'compound'},
            'expected_spine_range': (300, 400),
            'common_choice': "350-400 spine (hunting compound)",
            'reason': "Heavy compounds need stiff arrows for accuracy"
        }
    ]
    
    for case in real_world_cases:
        result = calculate_unified_spine(
            draw_weight=case['config']['weight'],
            arrow_length=case['config']['length'],
            point_weight=125,
            bow_type=case['config']['bow']
        )
        
        actual_spine = result['calculated_spine']
        expected_min, expected_max = case['expected_spine_range']
        
        if expected_min <= actual_spine <= expected_max:
            status = "✅ MATCHES"
        elif actual_spine < expected_min:
            diff = expected_min - actual_spine
            status = f"❌ TOO STIFF (-{diff})"
        else:
            diff = actual_spine - expected_max
            status = f"❌ TOO SOFT (+{diff})"
        
        print(f"{case['config']['weight']}lbs {case['config']['bow']}: {actual_spine} (expect {expected_min}-{expected_max}) {status}")
        print(f"   Common choice: {case['common_choice']}")
        print(f"   Reason: {case['reason']}")
        print()

if __name__ == "__main__":
    try:
        test_user_experience_scenarios()
        test_professional_mode_effects()
        test_real_world_expectations()
        
    except Exception as e:
        print(f"\n❌ Testing failed: {e}")
        import traceback
        traceback.print_exc()