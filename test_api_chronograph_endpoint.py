#!/usr/bin/env python3
"""
Test actual API endpoints to verify chronograph data integration
"""

import requests
import json


def test_api_chronograph_endpoints():
    """Test API endpoints with chronograph data"""
    
    print("🧪 Testing API chronograph integration via HTTP endpoints...")
    
    base_url = "http://localhost:5000"
    
    # Test setup IDs that have chronograph data
    test_cases = [
        {
            'name': 'Test Compound Bow',
            'setup_id': 1,
            'arrow_id': 2419,
            'expected_speed': 285.4,
            'bow_type': 'compound'
        },
        {
            'name': 'Test Recurve Bow', 
            'setup_id': 2,
            'arrow_id': 2416,
            'expected_speed': 165.8,
            'bow_type': 'recurve'
        },
        {
            'name': 'Test Traditional Bow',
            'setup_id': 3,
            'arrow_id': 2417,
            'expected_speed': 152.6,
            'bow_type': 'traditional'
        }
    ]
    
    print("🎯 API Endpoint Chronograph Integration Test:")
    print("-" * 100)
    print("Setup Name               | Expected Speed | API Response | Source        | Status")
    print("-" * 100)
    
    all_tests_passed = True
    
    for test_case in test_cases:
        try:
            # Test the arrow performance analysis endpoint
            response = requests.get(f"{base_url}/api/arrow-performance-analysis", params={
                'setup_id': test_case['setup_id'],
                'arrow_id': test_case['arrow_id']
            }, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Look for chronograph data in the response
                api_speed = None
                source = "UNKNOWN"
                
                if 'chronograph_data' in data and data['chronograph_data']:
                    api_speed = data['chronograph_data'].get('measured_speed_fps')
                    source = "CHRONOGRAPH"
                elif 'calculations' in data:
                    api_speed = data['calculations'].get('arrow_speed_fps')
                    source = "CALCULATED"
                elif 'speed_fps' in data:
                    api_speed = data['speed_fps']
                    source = "API_SPEED"
                
                expected = test_case['expected_speed']
                
                if api_speed and abs(api_speed - expected) < 0.1:
                    status = "✅ PASS"
                elif api_speed:
                    status = f"⚠️ DIFFER ({api_speed:.1f})"
                    all_tests_passed = False
                else:
                    status = "❌ NO_SPEED"
                    api_speed = 0
                    all_tests_passed = False
                
                print(f"{test_case['name']:24} | {expected:14.1f} | {api_speed:12.1f} | {source:13} | {status}")
                
            else:
                print(f"{test_case['name']:24} | {test_case['expected_speed']:14.1f} | ERROR        | HTTP_{response.status_code}    | ❌ FAIL")
                all_tests_passed = False
                
        except requests.exceptions.RequestException as e:
            print(f"{test_case['name']:24} | {test_case['expected_speed']:14.1f} | ERROR        | CONNECTION   | ❌ FAIL ({e})")
            all_tests_passed = False
        except Exception as e:
            print(f"{test_case['name']:24} | {test_case['expected_speed']:14.1f} | ERROR        | PARSE_ERROR  | ❌ FAIL ({e})")
            all_tests_passed = False
    
    # Test health endpoint
    print("\n🔍 Testing API health endpoint:")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ API health: {health_data.get('status', 'unknown')}")
            print(f"   Database: {health_data.get('database_status', 'unknown')}")
            print(f"   Arrows: {health_data.get('database_stats', {}).get('total_arrows', 'unknown')}")
        else:
            print(f"❌ Health check failed: HTTP {response.status_code}")
            all_tests_passed = False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        all_tests_passed = False
    
    # Test a specific calculation endpoint
    print("\n🧮 Testing arrow speed calculation endpoint:")
    try:
        calc_params = {
            'bow_ibo_speed': 330,
            'bow_draw_weight': 60,
            'bow_draw_length': 29,
            'bow_type': 'compound',
            'arrow_weight_grains': 345,
            'setup_id': 1,
            'arrow_id': 2419
        }
        
        response = requests.get(f"{base_url}/api/calculate-arrow-speed", params=calc_params, timeout=10)
        
        if response.status_code == 200:
            calc_data = response.json()
            calculated_speed = calc_data.get('arrow_speed_fps', 0)
            
            # Check if it returned chronograph data (should be 285.4) or calculated (~302)
            if abs(calculated_speed - 285.4) < 0.1:
                print(f"✅ Calculation endpoint returned chronograph data: {calculated_speed:.1f} fps")
            elif calculated_speed > 250:
                print(f"⚠️ Calculation endpoint returned calculated data: {calculated_speed:.1f} fps (expected chronograph: 285.4)")
            else:
                print(f"❌ Calculation endpoint returned unexpected value: {calculated_speed:.1f} fps")
                all_tests_passed = False
                
        else:
            print(f"❌ Calculation endpoint failed: HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            all_tests_passed = False
            
    except Exception as e:
        print(f"❌ Calculation endpoint error: {e}")
        all_tests_passed = False
    
    if all_tests_passed:
        print(f"\n✅ All API chronograph integration tests passed!")
        print("   The API correctly uses chronograph data when available.")
    else:
        print(f"\n⚠️ Some API tests did not pass as expected.")
        print("   Check the API implementation and database connectivity.")
    
    return all_tests_passed


if __name__ == "__main__":
    success = test_api_chronograph_endpoints()
    exit(0 if success else 1)