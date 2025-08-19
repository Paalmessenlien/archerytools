#!/usr/bin/env python3
"""
Direct test of the ballistics calculator to verify the physics fix
"""

import sys
import os

# Add the arrow_scraper directory to the path
sys.path.insert(0, '/home/paal/archerytools/arrow_scraper')

from ballistics_calculator import BallisticsCalculator, ArrowType, EnvironmentalConditions, ShootingConditions

def test_ballistics_calculator():
    """Test the ballistics calculator directly"""
    print("🎯 Testing Ballistics Calculator Physics")
    print("=" * 50)
    
    # Initialize calculator
    calculator = BallisticsCalculator()
    
    # Test parameters
    arrow_speed_fps = 350.0
    arrow_weight_grains = 420.2
    arrow_diameter_inches = 0.239
    arrow_type = ArrowType.TARGET
    
    # Environmental conditions
    environmental = EnvironmentalConditions(
        temperature_f=70.0,
        wind_speed_mph=0.0,
        altitude_feet=0.0,
        humidity_percent=50.0,
        wind_direction_degrees=90.0,
        air_pressure_inHg=29.92
    )
    
    # Shooting conditions
    shooting = ShootingConditions(
        shot_angle_degrees=0.0,
        sight_height_inches=7.0,
        zero_distance_yards=20.0,
        max_range_yards=80.0
    )
    
    print(f"📊 Test Parameters:")
    print(f"   Arrow Speed: {arrow_speed_fps} fps")
    print(f"   Arrow Weight: {arrow_weight_grains} grains") 
    print(f"   Arrow Diameter: {arrow_diameter_inches} inches")
    print(f"   Sight Height: {shooting.sight_height_inches} inches")
    print(f"   Zero Distance: {shooting.zero_distance_yards} yards")
    
    try:
        # Calculate trajectory
        print(f"\n🔄 Calculating trajectory...")
        result = calculator.calculate_trajectory(
            arrow_speed_fps=arrow_speed_fps,
            arrow_weight_grains=arrow_weight_grains,
            arrow_diameter_inches=arrow_diameter_inches,
            arrow_type=arrow_type,
            environmental=environmental,
            shooting=shooting
        )
        
        if result and result.get('trajectory_points'):
            points = result['trajectory_points']
            print(f"✅ Trajectory calculation successful!")
            print(f"   Generated {len(points)} trajectory points")
            
            # Find key trajectory metrics
            max_height = max(p['height_inches'] - shooting.sight_height_inches for p in points)
            point_40yd = next((p for p in points if abs(p['distance_yards'] - 40) <= 2), None)
            
            print(f"\n📈 Trajectory Results:")
            print(f"   Max Height: {max_height:.1f} inches above sight line")
            if point_40yd:
                drop_at_40 = abs(point_40yd['height_inches'] - shooting.sight_height_inches)
                print(f"   Drop at 40yd: {drop_at_40:.1f} inches below sight line")
            else:
                print(f"   Drop at 40yd: No data point found")
            
            # Test the launch angle calculation directly
            print(f"\n🎯 Launch Angle Analysis:")
            launch_angle_rad = calculator._calculate_launch_angle(
                arrow_speed_fps, shooting.sight_height_inches, shooting.zero_distance_yards
            )
            launch_angle_deg = launch_angle_rad * 180 / 3.14159
            print(f"   Launch Angle: {launch_angle_deg:.2f} degrees")
            print(f"   Launch Angle: {launch_angle_rad:.4f} radians")
            
            # Show first few trajectory points to verify physics
            print(f"\n🔍 First 10 trajectory points:")
            for i, point in enumerate(points[:10]):
                height_relative = point['height_inches'] - shooting.sight_height_inches
                print(f"   {point['distance_yards']:.1f}yd: {height_relative:+.2f}in ({point['velocity_fps']:.0f}fps)")
                
            # Check if we have realistic trajectory (should start positive, then go negative)
            start_heights = [p['height_inches'] - shooting.sight_height_inches for p in points[:5]]
            end_heights = [p['height_inches'] - shooting.sight_height_inches for p in points[-5:]]
            
            print(f"\n✅ Physics Check:")
            print(f"   Early trajectory (0-10yd): {[f'{h:+.2f}' for h in start_heights]}")
            print(f"   Late trajectory (70-80yd): {[f'{h:+.2f}' for h in end_heights]}")
            
            # Verify we have realistic values (not all zeros)
            if max_height > 0.1 and point_40yd and abs(point_40yd['height_inches'] - shooting.sight_height_inches) > 0.1:
                print(f"✅ Physics appears correct - trajectory shows realistic rise and fall")
            else:
                print(f"❌ Physics may be incorrect - trajectory values seem unrealistic")
                
        else:
            print(f"❌ Trajectory calculation failed or returned no points")
            if 'error' in result:
                print(f"   Error: {result['error']}")
                
    except Exception as e:
        print(f"❌ Calculation failed with exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ballistics_calculator()