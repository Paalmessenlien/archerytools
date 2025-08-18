#!/usr/bin/env python3
"""
Test API chronograph integration using the actual calculate_enhanced_arrow_speed_internal function
"""

import sqlite3
import sys
from pathlib import Path

# Add the parent directory to path to import api
sys.path.append(str(Path(__file__).parent))

def test_api_chronograph_integration():
    """Test the API chronograph integration"""
    
    print("🧪 Testing API chronograph integration...")
    
    try:
        # Import the API function
        from api import calculate_enhanced_arrow_speed_internal
        
        # Test data - these match our test chronograph entries
        test_cases = [
            {
                'name': 'Test Compound Bow',
                'setup_id': 1,
                'arrow_id': 1,
                'bow_ibo_speed': 330,
                'bow_draw_weight': 60.0,
                'bow_draw_length': 29.0,
                'bow_type': 'compound',
                'arrow_weight_grains': 345,
                'expected_chronograph_speed': 285.4
            },
            {
                'name': 'Test Recurve Bow',
                'setup_id': 2,
                'arrow_id': 2,
                'bow_ibo_speed': 180,
                'bow_draw_weight': 45.0,
                'bow_draw_length': 28.5,
                'bow_type': 'recurve',
                'arrow_weight_grains': 420,
                'expected_chronograph_speed': 165.8
            },
            {
                'name': 'Test Traditional Bow',
                'setup_id': 3,
                'arrow_id': 3,
                'bow_ibo_speed': 160,
                'bow_draw_weight': 55.0,
                'bow_draw_length': 27.5,
                'bow_type': 'traditional',
                'arrow_weight_grains': 460,
                'expected_chronograph_speed': 152.6
            }
        ]
        
        print("🎯 API Chronograph Integration Test Results:")
        print("-" * 100)
        print("Setup Name               | Expected Speed | API Result | Source        | Status")
        print("-" * 100)
        
        all_tests_passed = True
        
        for test_case in test_cases:
            try:
                api_result = calculate_enhanced_arrow_speed_internal(
                    bow_ibo_speed=test_case['bow_ibo_speed'],
                    bow_draw_weight=test_case['bow_draw_weight'],
                    bow_draw_length=test_case['bow_draw_length'],
                    bow_type=test_case['bow_type'],
                    arrow_weight_grains=test_case['arrow_weight_grains'],
                    setup_id=test_case['setup_id'],
                    arrow_id=test_case['arrow_id']
                )
                
                expected = test_case['expected_chronograph_speed']
                
                # Check if API returned chronograph data (exact match) or calculated data
                if abs(api_result - expected) < 0.1:
                    source = "CHRONOGRAPH"
                    status = "✅ PASS"
                else:
                    source = "CALCULATED"
                    status = "⚠️ CALCULATED" if api_result > 0 else "❌ FAIL"
                    all_tests_passed = False
                
                print(f"{test_case['name']:24} | {expected:14.1f} | {api_result:10.1f} | {source:13} | {status}")
                
            except Exception as e:
                print(f"{test_case['name']:24} | {test_case['expected_chronograph_speed']:14.1f} | ERROR      | API ERROR     | ❌ FAIL ({e})")
                all_tests_passed = False
        
        # Test without chronograph data (should fall back to calculation)
        print("\n🧮 Fallback Calculation Test (no chronograph data):")
        print("-" * 100)
        
        try:
            fallback_result = calculate_enhanced_arrow_speed_internal(
                bow_ibo_speed=320,
                bow_draw_weight=65.0,
                bow_draw_length=28.0,
                bow_type='compound',
                arrow_weight_grains=350,
                setup_id=999,  # Non-existent setup
                arrow_id=999   # Non-existent arrow
            )
            
            print(f"Non-existent setup       | No data        | {fallback_result:10.1f} | CALCULATED    | {'✅ PASS' if fallback_result > 200 else '⚠️ LOW'}")
            
        except Exception as e:
            print(f"Non-existent setup       | No data        | ERROR      | API ERROR     | ❌ FAIL ({e})")
            all_tests_passed = False
        
        if all_tests_passed:
            print(f"\n✅ All API chronograph integration tests passed!")
            print("   The API correctly uses chronograph data when available and falls back to calculations when not.")
        else:
            print(f"\n⚠️ Some tests did not return chronograph data as expected.")
            print("   This might indicate the API is using calculated speeds instead of measured chronograph data.")
        
        return all_tests_passed
        
    except ImportError as e:
        print(f"❌ Could not import API function: {e}")
        print("   This test needs to be run from the arrow_scraper directory with Flask dependencies.")
        return False
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False


if __name__ == "__main__":
    success = test_api_chronograph_integration()
    exit(0 if success else 1)