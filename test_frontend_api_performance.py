#!/usr/bin/env python3
"""
Test the exact API endpoint that the frontend uses for performance analysis
This simulates the ArrowPerformanceAnalysis.vue component behavior
"""

import requests
import json


def test_frontend_performance_api():
    """Test the exact API endpoint the frontend calls"""
    
    print("🧪 Testing frontend performance analysis API endpoint...")
    print("   This simulates ArrowPerformanceAnalysis.vue calling the API")
    
    base_url = "http://localhost:5000"
    
    # The frontend calls: api.post(`/setup-arrows/${props.setupArrow.id}/calculate-performance`)
    # Test with our known setup_arrow IDs that have chronograph data
    test_cases = [
        {
            'name': 'Test Compound Setup',
            'setup_arrow_id': 1,
            'expected_chronograph_speed': 285.4,
            'bow_config': {
                'draw_weight': 60.0,
                'draw_length': 29.0,
                'bow_type': 'compound',
                'ibo_speed': 330
            }
        },
        {
            'name': 'Test Recurve Setup',
            'setup_arrow_id': 2,
            'expected_chronograph_speed': 165.8,
            'bow_config': {
                'draw_weight': 45.0,
                'draw_length': 28.5,
                'bow_type': 'recurve',
                'ibo_speed': 180
            }
        }
    ]
    
    print("🎯 Frontend API Performance Test (requires authentication):")
    print("-" * 100)
    print("Setup Arrow ID | Expected Chrono | API Result | Status")
    print("-" * 100)
    
    for test_case in test_cases:
        try:
            # This is the exact call the frontend makes
            response = requests.post(
                f"{base_url}/api/setup-arrows/{test_case['setup_arrow_id']}/calculate-performance",
                json={
                    'bow_config': test_case['bow_config']
                },
                timeout=10
            )
            
            if response.status_code == 401:
                print(f"{test_case['setup_arrow_id']:14} | {test_case['expected_chronograph_speed']:15.1f} | AUTH_REQUIRED  | ❌ Authentication needed")
                print(f"    Response: {response.json().get('message', 'Unknown auth error')}")
                
            elif response.status_code == 200:
                data = response.json()
                
                # Look for speed in the performance data
                api_speed = None
                speed_source = "unknown"
                
                if 'performance' in data and 'performance_summary' in data['performance']:
                    summary = data['performance']['performance_summary']
                    api_speed = summary.get('estimated_speed_fps')
                    speed_source = summary.get('speed_source', 'estimated')
                
                expected = test_case['expected_chronograph_speed']
                
                if api_speed and abs(api_speed - expected) < 0.1:
                    status = f"✅ PASS ({speed_source})"
                elif api_speed:
                    status = f"⚠️ SPEED_MISMATCH ({api_speed:.1f} fps, source: {speed_source})"
                else:
                    status = "❌ NO_SPEED_DATA"
                
                print(f"{test_case['setup_arrow_id']:14} | {expected:15.1f} | {api_speed or 0:10.1f} | {status}")
                
                # If the speed doesn't match, it might indicate the issue
                if api_speed and abs(api_speed - expected) > 0.1:
                    if abs(api_speed - 276.1) < 0.1:
                        print(f"    🎯 FOUND THE SOURCE! This returns 276.1 fps")
                    print(f"    Debug: Full response structure: {list(data.keys())}")
                    if 'performance' in data:
                        print(f"    Performance keys: {list(data['performance'].keys())}")
                        if 'performance_summary' in data['performance']:
                            print(f"    Summary keys: {list(data['performance']['performance_summary'].keys())}")
                
            else:
                print(f"{test_case['setup_arrow_id']:14} | {test_case['expected_chronograph_speed']:15.1f} | HTTP_ERROR    | ❌ HTTP {response.status_code}")
                print(f"    Response: {response.text[:100]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"{test_case['setup_arrow_id']:14} | {test_case['expected_chronograph_speed']:15.1f} | NETWORK_ERROR  | ❌ {str(e)[:50]}...")
    
    print(f"\n📋 Analysis:")
    print("   The frontend calls `/api/setup-arrows/<id>/calculate-performance` with authentication.")
    print("   If authentication fails, the API returns 401 and the frontend might:")
    print("   1. Show cached/default performance data")
    print("   2. Fall back to client-side calculations")
    print("   3. Display previously calculated values (276.1 fps)")
    print("")
    print("   To fix the 276.1 fps issue:")
    print("   1. Ensure user is properly authenticated in frontend")
    print("   2. Clear any cached performance data")
    print("   3. Verify the correct setup_arrow_id is being used")
    
    # Test if there's an unauthenticated endpoint that might return 276.1 fps
    print(f"\n🔍 Testing for unauthenticated endpoints that might return 276.1 fps...")
    
    # Test some calculation endpoints that might not require auth
    try:
        test_params = {
            "bow_ibo_speed": 320,
            "bow_draw_weight": 60,
            "bow_draw_length": 29,
            "bow_type": "compound",
            "arrow_weight_grains": 418.8,  # From our test data that might produce 276.1
        }
        
        response = requests.post(
            f"{base_url}/api/calculator/arrow-speed-estimate",
            json=test_params,
            timeout=10
        )
        
        if response.status_code == 200:
            speed_data = response.json()
            speed = speed_data.get('arrow_speed_fps', 0)
            if abs(speed - 276.1) < 0.5:
                print(f"✅ Found potential source: /api/calculator/arrow-speed-estimate returns {speed:.1f} fps")
                print(f"   This might be used as fallback when authentication fails")
            else:
                print(f"⚪ /api/calculator/arrow-speed-estimate returns {speed:.1f} fps (not 276.1)")
        else:
            print(f"❌ /api/calculator/arrow-speed-estimate failed: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing calculation endpoint: {e}")


if __name__ == "__main__":
    test_frontend_performance_api()