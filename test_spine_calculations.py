#!/usr/bin/env python3
"""
Test script to validate corrected spine calculations against German calculator standards
Tests the specific scenarios that revealed the calculation errors.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'arrow_scraper'))

from arrow_scraper.spine_service import calculate_unified_spine

def test_german_calculator_scenarios():
    """Test the scenarios that revealed calculation errors"""
    
    print("🧪 Testing Corrected Spine Calculations vs German Calculator")
    print("=" * 60)
    
    # Test cases based on German calculator analysis
    test_cases = [
        {
            'name': '40lbs Recurve, 28" arrows, 125gr points, FastFlight',
            'draw_weight': 40,
            'arrow_length': 28,
            'point_weight': 125,
            'bow_type': 'recurve',
            'string_material': 'fastflight',
            'expected_german': 700,  # German calculator result
            'old_system': 550  # Old incorrect result (40 × 12.5 + 50)
        },
        {
            'name': '40lbs Traditional, 28" arrows, 125gr points, Dacron',
            'draw_weight': 40,
            'arrow_length': 28,
            'point_weight': 125,
            'bow_type': 'traditional',
            'string_material': 'dacron',
            'expected_german': 715,  # German calculator result (700 + 15 for Dacron)
            'old_system': 600  # Old incorrect result (40 × 12.5 + 100)
        },
        {
            'name': '50lbs Compound, 29" arrows, 100gr points',
            'draw_weight': 50,
            'arrow_length': 29,
            'point_weight': 100,
            'bow_type': 'compound',
            'string_material': None,
            'expected_german': None,  # German calc doesn't handle compound well
            'old_system': 650  # Old system: 50 × 12.5 + 25 + (-12.5) = 637.5
        },
        {
            'name': '35lbs Recurve, 30" arrows, 140gr points, FastFlight',
            'draw_weight': 35,
            'arrow_length': 30,
            'point_weight': 140,
            'bow_type': 'recurve',
            'string_material': 'fastflight',
            'expected_german': 857.5,  # 1100-(35×10) + (30-28)×25 + (140-125)×0.5 = 800+50+7.5
            'old_system': None
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. {case['name']}")
        print("-" * 50)
        
        # Calculate using our corrected system
        result = calculate_unified_spine(
            draw_weight=case['draw_weight'],
            arrow_length=case['arrow_length'],
            point_weight=case['point_weight'],
            bow_type=case['bow_type'],
            string_material=case['string_material']
        )
        
        calculated_spine = result['calculated_spine']
        calculations = result['calculations']
        
        print(f"📊 Our Corrected Result: {calculated_spine}")
        print(f"   Base Spine: {calculations['base_spine']:.1f}")
        print(f"   Length Adj: {calculations['adjustments']['length_adjustment']:.1f}")
        print(f"   Point Adj:  {calculations['adjustments']['point_weight_adjustment']:.1f}")
        print(f"   String Adj: {calculations['adjustments']['string_material_adjustment']:.1f}")
        print(f"   Total Adj:  {calculations['total_adjustment']:.1f}")
        
        if case['expected_german']:
            difference = calculated_spine - case['expected_german']
            print(f"🎯 German Calculator: {case['expected_german']}")
            print(f"📏 Difference: {difference:+.1f} ({difference/case['expected_german']*100:+.1f}%)")
            
            # Acceptable difference is within 5% or ±25 spine units
            acceptable = abs(difference) <= 25 or abs(difference/case['expected_german']) <= 0.05
            status = "✅ PASS" if acceptable else "❌ FAIL"
            print(f"🔍 Validation: {status}")
        
        if case['old_system']:
            old_difference = calculated_spine - case['old_system']
            print(f"🗂️  Old System: {case['old_system']}")
            print(f"📈 Improvement: {old_difference:+.1f} spine units")

def test_string_material_effects():
    """Test string material effects specifically"""
    print("\n\n🎯 String Material Effect Testing")
    print("=" * 60)
    
    base_config = {
        'draw_weight': 40,
        'arrow_length': 28,
        'point_weight': 125,
        'bow_type': 'recurve'
    }
    
    string_materials = [
        ('fastflight', 'FastFlight/Spectra'),
        ('dacron', 'Dacron/B50'),
        (None, 'Not Specified')
    ]
    
    for string_code, string_name in string_materials:
        result = calculate_unified_spine(**base_config, string_material=string_code)
        spine = result['calculated_spine']
        string_adj = result['calculations']['adjustments']['string_material_adjustment']
        
        print(f"{string_name:15}: {spine:3d} spine (adjustment: {string_adj:+.0f})")

def test_bow_type_formulas():
    """Test the different bow type formulas"""
    print("\n\n🏹 Bow Type Formula Testing")
    print("=" * 60)
    
    base_config = {
        'draw_weight': 45,
        'arrow_length': 28,
        'point_weight': 125,
        'string_material': 'fastflight'
    }
    
    bow_types = ['compound', 'recurve', 'traditional']
    
    for bow_type in bow_types:
        result = calculate_unified_spine(**base_config, bow_type=bow_type)
        spine = result['calculated_spine']
        base_spine = result['calculations']['base_spine']
        method = result['calculations']['adjustments']['bow_type_method']
        
        print(f"{bow_type.capitalize():12}: {spine:3d} spine (base: {base_spine:.1f}, method: {method})")

if __name__ == "__main__":
    try:
        test_german_calculator_scenarios()
        test_string_material_effects()
        test_bow_type_formulas()
        print("\n✅ Spine calculation testing completed!")
        
    except Exception as e:
        print(f"\n❌ Testing failed: {e}")
        import traceback
        traceback.print_exc()