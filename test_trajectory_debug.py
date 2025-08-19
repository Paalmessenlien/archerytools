#!/usr/bin/env python3
"""
Direct test of trajectory calculation API to debug parameter mismatch issues
"""

import requests
import json

# API endpoint
API_BASE = "http://localhost:5000/api"

# Test data that mimics what the frontend would send
test_data = {
    "arrow_data": {
        "manufacturer": "Aurel Archery",
        "model_name": "ORYX",
        "spine": 400,
        "outer_diameter": 0.239,  # This should map to arrow_diameter
        "gpi_weight": 9.1,
        "total_weight": 420.2,    # This should map to arrow_weight
        "total_arrow_weight_grains": 420.2,
        "estimated_speed_fps": 350.0,  # This should map to arrow_speed
        "speed_fps": 350.0,
        "arrow_speed_fps": 350.0,
        "diameter_inches": 0.239,
        "weight_grains": 420.2,
        "performance": {
            "performance_summary": {
                "estimated_speed_fps": 350.0,
                "total_arrow_weight_grains": 420.2
            }
        }
    },
    "bow_config": {
        "draw_weight": 50,
        "draw_length": 28,
        "bow_type": "compound",
        "ibo_speed": 320
    },
    "environmental_conditions": {
        "temperature_f": 70.0,
        "wind_speed_mph": 0.0,
        "altitude_feet": 0.0,
        "humidity_percent": 50.0,
        "wind_direction_degrees": 90.0,
        "air_pressure_inHg": 29.92
    },
    "shooting_conditions": {
        "shot_angle_degrees": 0.0,
        "sight_height_inches": 7.0,
        "zero_distance_yards": 20.0,
        "max_range_yards": 80.0
    }
}

def test_trajectory_calculation():
    """Test the trajectory calculation endpoint directly"""
    print("🎯 Testing Trajectory Calculation API")
    print("=" * 50)
    
    # Test the calculation endpoint
    try:
        print(f"Sending POST request to: {API_BASE}/calculate-trajectory")
        print(f"Arrow data keys: {list(test_data['arrow_data'].keys())}")
        print(f"Arrow speed fields:")
        for key, value in test_data['arrow_data'].items():
            if 'speed' in key.lower():
                print(f"  {key}: {value}")
        print(f"Arrow weight fields:")
        for key, value in test_data['arrow_data'].items():
            if 'weight' in key.lower():
                print(f"  {key}: {value}")
        print(f"Arrow diameter fields:")
        for key, value in test_data['arrow_data'].items():
            if 'diameter' in key.lower():
                print(f"  {key}: {value}")
        
        response = requests.post(
            f"{API_BASE}/calculate-trajectory",
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"\n✅ Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Response Success: {result.get('success', False)}")
            
            if result.get('success') and result.get('trajectory_data'):
                traj_data = result['trajectory_data']
                if traj_data.get('trajectory_points'):
                    points = traj_data['trajectory_points']
                    print(f"✅ Trajectory Points: {len(points)}")
                    
                    # Find max height and drop at 40yd
                    max_height = max(p['height_inches'] - 7.0 for p in points)  # Adjust for sight height
                    point_40yd = next((p for p in points if abs(p['distance_yards'] - 40) <= 2), None)
                    
                    print(f"📊 Trajectory Results:")
                    print(f"   Max Height: {max_height:.1f} inches")
                    if point_40yd:
                        drop_at_40 = abs(point_40yd['height_inches'] - 7.0)
                        print(f"   Drop at 40yd: {drop_at_40:.1f} inches")
                    else:
                        print(f"   Drop at 40yd: No data point found")
                        
                    # Show first few trajectory points
                    print(f"\n🔍 First few trajectory points:")
                    for i, point in enumerate(points[:5]):
                        print(f"   {i+1}: {point['distance_yards']:.1f}yd → {point['height_inches']:.1f}in ({point['velocity_fps']:.0f}fps)")
                else:
                    print("❌ No trajectory points in response")
            else:
                print("❌ Trajectory calculation failed or returned no data")
                if 'error' in result:
                    print(f"   Error: {result['error']}")
        else:
            print(f"❌ HTTP Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_trajectory_calculation()