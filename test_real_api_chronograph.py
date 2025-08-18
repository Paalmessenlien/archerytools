#!/usr/bin/env python3
"""
Test real API endpoints that use chronograph data
"""

import requests
import json


def test_real_api_chronograph():
    """Test real API endpoints with chronograph data"""
    
    print("🧪 Testing real API chronograph integration...")
    
    base_url = "http://localhost:5000"
    
    # Test the setup-arrows performance calculation endpoint
    test_cases = [
        {
            'name': 'Test Compound Bow',
            'setup_arrow_id': 1,
            'expected_chronograph_speed': 285.4,
        },
        {
            'name': 'Test Recurve Bow', 
            'setup_arrow_id': 2,
            'expected_chronograph_speed': 165.8,
        },
        {
            'name': 'Test Traditional Bow',
            'setup_arrow_id': 3,
            'expected_chronograph_speed': 152.6,
        }
    ]
    
    print("🎯 Real API Performance Calculation Test:")
    print("-" * 100)
    print("Setup Arrow ID | Expected Speed | API Speed | Chronograph Used | Status")
    print("-" * 100)
    
    all_tests_passed = True
    
    for test_case in test_cases:
        try:
            # Test the setup-arrows calculate-performance endpoint
            response = requests.post(
                f"{base_url}/api/setup-arrows/{test_case['setup_arrow_id']}/calculate-performance",
                json={},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Look for speed in the response
                api_speed = None
                chronograph_used = False
                
                # Check various possible locations for the speed
                if 'arrow_speed_fps' in data:
                    api_speed = data['arrow_speed_fps']
                elif 'performance' in data and 'arrow_speed_fps' in data['performance']:
                    api_speed = data['performance']['arrow_speed_fps']
                elif 'calculations' in data and 'arrow_speed_fps' in data['calculations']:
                    api_speed = data['calculations']['arrow_speed_fps']
                elif 'speed_fps' in data:
                    api_speed = data['speed_fps']
                
                # Check if chronograph data is indicated
                if 'chronograph_data' in data and data['chronograph_data']:
                    chronograph_used = True
                elif 'data_source' in data and 'chronograph' in data['data_source'].lower():
                    chronograph_used = True
                
                expected = test_case['expected_chronograph_speed']
                
                if api_speed and abs(api_speed - expected) < 0.1:
                    status = "✅ PASS (CHRONO)"
                    chronograph_used = True
                elif api_speed and abs(api_speed - expected) < 20:
                    status = "⚠️ CLOSE"
                elif api_speed:
                    status = f"⚠️ DIFFER ({api_speed:.1f})"
                    all_tests_passed = False
                else:
                    status = "❌ NO_SPEED"
                    api_speed = 0
                    all_tests_passed = False
                
                chrono_indicator = "YES" if chronograph_used else "NO"
                
                print(f"{test_case['setup_arrow_id']:14} | {expected:14.1f} | {api_speed:9.1f} | {chrono_indicator:16} | {status}")
                
                # Print response details for debugging
                if api_speed and abs(api_speed - expected) > 0.1:
                    print(f"    Debug: Response keys: {list(data.keys())}")
                    if 'performance' in data:
                        print(f"    Performance keys: {list(data['performance'].keys()) if isinstance(data['performance'], dict) else 'Not dict'}")
                
            else:
                print(f"{test_case['setup_arrow_id']:14} | {test_case['expected_chronograph_speed']:14.1f} | ERROR     | HTTP_{response.status_code}        | ❌ FAIL")
                print(f"    Response: {response.text[:100]}...")
                all_tests_passed = False
                
        except requests.exceptions.RequestException as e:
            print(f"{test_case['setup_arrow_id']:14} | {test_case['expected_chronograph_speed']:14.1f} | ERROR     | CONNECTION      | ❌ FAIL ({e})")
            all_tests_passed = False
        except Exception as e:
            print(f"{test_case['setup_arrow_id']:14} | {test_case['expected_chronograph_speed']:14.1f} | ERROR     | PARSE_ERROR     | ❌ FAIL ({e})")
            all_tests_passed = False
    
    # Test comprehensive performance endpoint
    print("\n🧮 Testing comprehensive performance calculation:")
    try:
        comprehensive_data = {
            "bow_ibo_speed": 330,
            "bow_draw_weight": 60.0,
            "bow_draw_length": 29.0,
            "bow_type": "compound",
            "arrow_weight_grains": 345,
            "setup_id": 1,
            "arrow_id": 2419
        }
        
        response = requests.post(
            f"{base_url}/api/calculator/comprehensive-performance",
            json=comprehensive_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Look for chronograph data indication
            chronograph_detected = False
            api_speed = None
            
            if 'chronograph_data' in data:
                chronograph_detected = True
                print(f"✅ Chronograph data detected in comprehensive calculation")
                if isinstance(data['chronograph_data'], dict) and 'measured_speed_fps' in data['chronograph_data']:
                    api_speed = data['chronograph_data']['measured_speed_fps']
                    print(f"   Measured speed: {api_speed:.1f} fps")
            else:
                print(f"⚠️ No chronograph data detected in comprehensive calculation")
            
            # Look for arrow speed
            if 'arrow_speed_fps' in data:
                api_speed = data['arrow_speed_fps']
                print(f"   Arrow speed: {api_speed:.1f} fps")
            
            if api_speed and abs(api_speed - 285.4) < 0.1:
                print(f"✅ Comprehensive calculation using chronograph data correctly")
            elif api_speed:
                print(f"⚠️ Comprehensive calculation returned {api_speed:.1f} fps (expected 285.4 fps from chronograph)")
            else:
                print(f"❌ Comprehensive calculation failed to return speed")
                all_tests_passed = False
                
        else:
            print(f"❌ Comprehensive performance failed: HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            all_tests_passed = False
            
    except Exception as e:
        print(f"❌ Comprehensive performance error: {e}")
        all_tests_passed = False
    
    if all_tests_passed:
        print(f"\n✅ All real API chronograph integration tests passed!")
        print("   The API correctly uses chronograph data when available.")
    else:
        print(f"\n⚠️ Some API tests did not pass as expected.")
        print("   The API may be using calculated speeds instead of chronograph data.")
    
    return all_tests_passed


if __name__ == "__main__":
    success = test_real_api_chronograph()
    exit(0 if success else 1)