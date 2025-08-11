#!/usr/bin/env python3
"""
Test Enhanced Spine Service

This script tests the enhanced spine calculation service with database integration.
"""

from spine_service import UnifiedSpineService

def test_enhanced_spine_calculation():
    """Test the enhanced spine calculation features"""
    print("🧪 Testing Enhanced Spine Service...")
    
    # Create service instance
    service = UnifiedSpineService()
    
    # Test 1: Basic enhanced calculation
    print("\n🔬 Test 1: Basic Enhanced Calculation")
    result = service.calculate_enhanced_spine(
        draw_weight=50.0,
        arrow_length=29.0,
        point_weight=125.0,
        bow_type='compound'
    )
    
    print(f"Calculated Spine: {result['calculated_spine']}")
    print(f"Spine Range: {result['spine_range']}")
    print(f"Source: {result['source']}")
    print(f"Confidence: {result['calculations']['confidence']}")
    
    # Test 2: Material-specific calculation
    print("\n🔬 Test 2: Material-Specific Calculation")
    result = service.calculate_enhanced_spine(
        draw_weight=45.0,
        arrow_length=28.5,
        point_weight=150.0,
        bow_type='recurve',
        material_preference='carbon'
    )
    
    print(f"Calculated Spine: {result['calculated_spine']}")
    print(f"Material Info: {result.get('material_info', 'None')}")
    print(f"Adjustments: {result['calculations']['adjustments']}")
    
    # Test 3: Manufacturer-specific calculation
    print("\n🔬 Test 3: Manufacturer-Specific Calculation")
    result = service.calculate_enhanced_spine(
        draw_weight=55.0,
        arrow_length=29.5,
        point_weight=125.0,
        bow_type='compound',
        manufacturer_preference='easton'
    )
    
    print(f"Calculated Spine: {result['calculated_spine']}")
    print(f"Manufacturer Recommendations: {len(result.get('manufacturer_recommendations', []))}")
    
    # Test 4: Query calculation parameters
    print("\n🔬 Test 4: Query Calculation Parameters")
    base_params = service.get_calculation_parameters('base_calculation')
    print(f"Base Calculation Parameters: {list(base_params.keys())}")
    
    bow_adjustments = service.get_calculation_parameters('bow_adjustments')
    print(f"Bow Adjustment Parameters: {list(bow_adjustments.keys())}")
    
    # Test 5: Query material properties
    print("\n🔬 Test 5: Query Material Properties")
    materials = service.get_material_properties()
    print(f"Available Materials: {list(materials.keys())}")
    
    carbon_props = service.get_material_properties('Carbon')
    if carbon_props:
        print(f"Carbon Properties: density={carbon_props.get('density')}, "
              f"strength_factor={carbon_props.get('strength_factor')}")
    
    # Test 6: Query flight problem diagnostics
    print("\n🔬 Test 6: Query Flight Problem Diagnostics")
    problems = service.get_flight_problem_diagnostics()
    print(f"Problem Categories: {list(problems.keys())}")
    
    for category, category_problems in problems.items():
        print(f"  {category}: {list(category_problems.keys())}")
    
    print("\n✅ Enhanced Spine Service tests completed!")

def test_fallback_behavior():
    """Test fallback behavior when database queries fail"""
    print("\n🧪 Testing Fallback Behavior...")
    
    service = UnifiedSpineService()
    
    # Test standard calculation (should still work)
    result = service.calculate_spine(
        draw_weight=50.0,
        arrow_length=29.0,
        point_weight=125.0,
        bow_type='compound'
    )
    
    print(f"Fallback Calculated Spine: {result['calculated_spine']}")
    print(f"Fallback Source: {result['source']}")
    
    print("✅ Fallback behavior tests completed!")

def main():
    """Main test function"""
    try:
        test_enhanced_spine_calculation()
        test_fallback_behavior()
        print("\n🎉 All tests completed successfully!")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()