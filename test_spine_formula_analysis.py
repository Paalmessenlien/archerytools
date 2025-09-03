#!/usr/bin/env python3
"""
Analyze spine calculation formulas across different poundage ranges
to identify if light bows are too stiff and heavy bows are too soft
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'arrow_scraper'))

from arrow_scraper.spine_service import calculate_unified_spine

def analyze_spine_formulas():
    """Analyze spine calculations across poundage ranges"""
    
    print("🎯 Spine Formula Analysis - Light vs Heavy Bow Issues")
    print("=" * 70)
    
    # Test different poundage ranges with standard 28" arrows, 125gr points
    test_weights = [20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70]
    
    print(f"{'Weight':<6} {'Recurve':<8} {'Traditional':<12} {'Compound':<9} {'Formula Used'}")
    print("-" * 70)
    
    for weight in test_weights:
        # Test recurve
        recurve_result = calculate_unified_spine(
            draw_weight=weight,
            arrow_length=28,
            point_weight=125,
            bow_type='recurve'
        )
        recurve_spine = recurve_result['calculated_spine']
        
        # Test traditional
        trad_result = calculate_unified_spine(
            draw_weight=weight,
            arrow_length=28,
            point_weight=125,
            bow_type='traditional'
        )
        trad_spine = trad_result['calculated_spine']
        
        # Test compound
        compound_result = calculate_unified_spine(
            draw_weight=weight,
            arrow_length=28,
            point_weight=125,
            bow_type='compound'
        )
        compound_spine = compound_result['calculated_spine']
        
        # Determine which formula was used
        if weight <= 25:
            formula_type = "Very Light"
        elif weight <= 35:
            formula_type = "Light"
        else:
            formula_type = "Standard"
        
        print(f"{weight}lbs   {recurve_spine:<8} {trad_spine:<12} {compound_spine:<9} {formula_type}")
    
    print("\n" + "=" * 70)
    print("🔍 ANALYSIS:")
    
    # Analyze light bow issues (your concern: too stiff)
    print(f"\n📊 LIGHT BOW ANALYSIS (20-35lbs):")
    print(f"Current recommendations for traditional archery:")
    light_weights = [20, 25, 30, 35]
    for weight in light_weights:
        result = calculate_unified_spine(weight, 28, 125, 'traditional')
        spine = result['calculated_spine']
        
        # Traditional archery typically uses 600-1000 spine
        if spine < 700:
            status = "❌ TOO STIFF (may be too low for traditional)"
        elif spine > 900:
            status = "⚠️  VERY WEAK (check if appropriate)"
        else:
            status = "✅ GOOD (within traditional range)"
        
        print(f"   {weight}lbs → {spine} spine {status}")
    
    # Analyze heavy bow issues (your concern: too soft)
    print(f"\n📊 HEAVY BOW ANALYSIS (60-70lbs):")
    print(f"Current recommendations for compound bows:")
    heavy_weights = [60, 65, 70]
    for weight in heavy_weights:
        result = calculate_unified_spine(weight, 28, 125, 'compound')
        spine = result['calculated_spine']
        
        # Compound bows typically use 200-500 spine
        if spine < 200:
            status = "❌ TOO STIFF (extremely low spine)"
        elif spine > 500:
            status = "❌ TOO SOFT (may be too high for compound)"
        else:
            status = "✅ GOOD (within compound range)"
        
        print(f"   {weight}lbs → {spine} spine {status}")

def compare_with_industry_standards():
    """Compare with known industry standards"""
    
    print(f"\n🏭 INDUSTRY STANDARD COMPARISON:")
    print("=" * 70)
    
    # Known industry benchmarks
    industry_benchmarks = [
        {"weight": 25, "bow_type": "recurve", "expected_range": (800, 900), "source": "Youth archery standards"},
        {"weight": 35, "bow_type": "recurve", "expected_range": (700, 800), "source": "Traditional archery"},
        {"weight": 45, "bow_type": "recurve", "expected_range": (600, 700), "source": "Olympic recurve"},
        {"weight": 60, "bow_type": "compound", "expected_range": (300, 400), "source": "Hunting compound"},
        {"weight": 70, "bow_type": "compound", "expected_range": (250, 350), "source": "Target compound"}
    ]
    
    for benchmark in industry_benchmarks:
        result = calculate_unified_spine(
            benchmark["weight"], 28, 125, benchmark["bow_type"]
        )
        actual_spine = result['calculated_spine']
        expected_min, expected_max = benchmark["expected_range"]
        
        if expected_min <= actual_spine <= expected_max:
            status = "✅ WITHIN RANGE"
        elif actual_spine < expected_min:
            diff = expected_min - actual_spine
            status = f"❌ TOO STIFF (-{diff} spine)"
        else:
            diff = actual_spine - expected_max
            status = f"❌ TOO SOFT (+{diff} spine)"
        
        print(f"{benchmark['weight']}lbs {benchmark['bow_type']:<9}: {actual_spine:<4} (expected {expected_min}-{expected_max}) {status}")
        print(f"   Source: {benchmark['source']}")

if __name__ == "__main__":
    try:
        analyze_spine_formulas()
        compare_with_industry_standards()
        
        print(f"\n🔧 RECOMMENDATIONS:")
        print(f"1. Light bows (20-35lbs): Current formulas may need slight weakening adjustments")
        print(f"2. Heavy bows (60lbs+): Current formulas may need strengthening adjustments")
        print(f"3. Test with real-world archer feedback for validation")
        
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()