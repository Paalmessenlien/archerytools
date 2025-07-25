#!/usr/bin/env python3
"""
Test script for the new spine-specific arrow data model
"""

import json
from models import ArrowSpecification, SpineSpecification

def test_spine_model():
    """Test the new spine-specific arrow model"""
    print("Testing new spine-specific arrow data model...")
    
    try:
        # Create spine specifications
        spine_specs = [
            SpineSpecification(
                spine=300,
                outer_diameter=0.244,
                gpi_weight=9.8,
                inner_diameter=0.234,
                length_options=[32, 33]
            ),
            SpineSpecification(
                spine=340,
                outer_diameter=0.246,
                gpi_weight=10.2,
                inner_diameter=0.236,
                length_options=[32, 33]
            ),
            SpineSpecification(
                spine=400,
                outer_diameter=0.248,
                gpi_weight=10.5,
                inner_diameter=0.238,
                length_options=[32, 33]
            )
        ]
        
        # Create arrow specification
        arrow = ArrowSpecification(
            manufacturer="Test Manufacturer",
            model_name="Test Arrow Model",
            spine_specifications=spine_specs,
            material="Carbon Fiber",
            arrow_type="hunting",
            recommended_use=["hunting", "target"],
            description="Test arrow with spine-specific specifications",
            source_url="https://example.com/test-arrow"
        )
        
        print("✓ Arrow specification created successfully")
        
        # Test helper methods
        spine_options = arrow.get_spine_options()
        print(f"✓ Spine options: {spine_options}")
        
        spec_340 = arrow.get_specification_for_spine(340)
        if spec_340:
            print(f"✓ Spine 340 spec: diameter={spec_340.outer_diameter}, gpi={spec_340.gpi_weight}")
        
        diameter_range = arrow.get_diameter_range()
        print(f"✓ Diameter range: {diameter_range[0]:.3f} - {diameter_range[1]:.3f}")
        
        gpi_range = arrow.get_gpi_range()
        print(f"✓ GPI range: {gpi_range[0]:.1f} - {gpi_range[1]:.1f}")
        
        # Test JSON serialization
        arrow_dict = arrow.model_dump()
        json_data = json.dumps(arrow_dict, indent=2, default=str)
        print("✓ JSON serialization successful")
        
        # Test JSON deserialization
        arrow_from_json = ArrowSpecification(**json.loads(json_data))
        print("✓ JSON deserialization successful")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

def test_validation():
    """Test data validation"""
    print("\nTesting data validation...")
    
    try:
        # Test invalid spine value
        try:
            invalid_spine = SpineSpecification(
                spine=-100,  # Invalid
                outer_diameter=0.244,
                gpi_weight=9.8
            )
            print("✗ Should have caught invalid spine value")
            return False
        except ValueError:
            print("✓ Caught invalid spine value")
        
        # Test duplicate spine values
        try:
            spine_specs = [
                SpineSpecification(spine=300, outer_diameter=0.244, gpi_weight=9.8),
                SpineSpecification(spine=300, outer_diameter=0.246, gpi_weight=10.2)  # Duplicate
            ]
            arrow = ArrowSpecification(
                manufacturer="Test",
                model_name="Test",
                spine_specifications=spine_specs,
                source_url="https://example.com"
            )
            print("✗ Should have caught duplicate spine values")
            return False
        except ValueError:
            print("✓ Caught duplicate spine values")
        
        return True
        
    except Exception as e:
        print(f"✗ Validation test failed: {e}")
        return False

def create_sample_data():
    """Create sample data showing the problem resolution"""
    print("\nCreating sample data to demonstrate the fix...")
    
    # This represents the Carbon Legacy arrow with different specs per spine
    carbon_legacy_specs = [
        SpineSpecification(spine=340, outer_diameter=0.289, gpi_weight=7.1),
        SpineSpecification(spine=400, outer_diameter=0.291, gpi_weight=7.5),
        SpineSpecification(spine=500, outer_diameter=0.296, gpi_weight=8.3),
        SpineSpecification(spine=600, outer_diameter=0.300, gpi_weight=8.8),
        SpineSpecification(spine=700, outer_diameter=0.305, gpi_weight=9.2)
    ]
    
    arrow = ArrowSpecification(
        manufacturer="Easton",
        model_name="Carbon Legacy",
        spine_specifications=carbon_legacy_specs,
        material="Carbon Fiber",
        arrow_type="hunting",
        recommended_use=["hunting"],
        description="Traditional wood-grained carbon arrow",
        source_url="https://eastonarchery.com/arrows_/carbon-legacy/"
    )
    
    print(f"Carbon Legacy - Spine options: {arrow.get_spine_options()}")
    print(f"Diameter range: {arrow.get_diameter_range()[0]:.3f}\" - {arrow.get_diameter_range()[1]:.3f}\"")
    print(f"GPI range: {arrow.get_gpi_range()[0]:.1f} - {arrow.get_gpi_range()[1]:.1f}")
    
    # Show individual spine specs
    for spec in arrow.spine_specifications:
        print(f"  Spine {spec.spine}: {spec.outer_diameter:.3f}\" dia, {spec.gpi_weight:.1f} GPI")
    
    return arrow

def main():
    """Run all tests"""
    print("Testing Updated Arrow Data Model")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 3
    
    if test_spine_model():
        tests_passed += 1
    
    if test_validation():
        tests_passed += 1
    
    sample_arrow = create_sample_data()
    if sample_arrow:
        tests_passed += 1
    
    print(f"\nResults: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! The spine-specific model is working correctly.")
        print("\nThe updated model now properly handles:")
        print("- Different GPI weights per spine option")
        print("- Different diameters per spine option")
        print("- Different length options per spine option")
        print("- Proper validation and data integrity")
    else:
        print("❌ Some tests failed. Please check the implementation.")

if __name__ == "__main__":
    main()