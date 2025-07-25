#!/usr/bin/env python3

from spine_calculator import SpineCalculator, BowConfiguration, BowType

calculator = SpineCalculator()
bow_config = BowConfiguration(
    draw_weight=45,
    draw_length=28,
    bow_type=BowType.TRADITIONAL,
    cam_type='medium',
    arrow_rest_type='drop_away'
)

print("Testing different material preference formats:")

# Test with different formats
for material in ['Wood', 'wood', None]:
    print(f"\nTesting material_preference='{material}':")
    
    result = calculator.calculate_required_spine(
        bow_config=bow_config,
        arrow_length=29,
        point_weight=100,
        nock_weight=10,
        fletching_weight=15,
        material_preference=material
    )
    
    print(f"  Calculated spine: {result['calculated_spine']}")
    print(f"  Spine units: {result.get('spine_units', 'not specified')}")
    if 'notes' in result:
        print(f"  Notes: {result['notes'][0]}")