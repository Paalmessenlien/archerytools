#!/usr/bin/env python3
import requests
import json

def test_wood_arrows_comprehensive():
    """Test wood arrow API with comprehensive debug output"""
    
    # Test exactly what frontend should send for longbow + wood
    api_url = "http://localhost:5000/api/tuning/recommendations"
    
    test_payload = {
        "draw_weight": 42,  # User mentioned 42 spine
        "draw_length": 28,
        "bow_type": "longbow",
        "arrow_length": 30,  # User mentioned 30 arrow length
        "arrow_material": "Wood",
        "arrow_rest_type": "drop_away",
        "point_weight": 100,
        "nock_type": "pin",
        "primary_goal": "maximum_accuracy"
    }
    
    print(f"🏹 Testing Wood Arrow API")
    print(f"URL: {api_url}")
    print(f"Payload:")
    print(json.dumps(test_payload, indent=2))
    print()
    
    try:
        response = requests.post(api_url, json=test_payload, timeout=10)
        result = response.json()
        
        if response.status_code == 200:
            print("✅ API Response successful")
            print(f"Recommended spine: {result.get('recommended_spine', 'Not provided')}")
            
            arrows = result.get('recommendations', [])
            print(f"📊 Found {len(arrows)} recommendations")
            
            if arrows:
                print("\n🎯 Wood Arrow Recommendations:")
                for i, arrow in enumerate(arrows[:5], 1):
                    arrow_data = arrow.get('arrow', arrow)
                    manufacturer = arrow_data.get('manufacturer', 'Unknown')
                    model_name = arrow_data.get('model_name', 'Unknown')
                    material = arrow_data.get('material', 'Unknown')
                    match_score = arrow.get('compatibility_score', arrow.get('match_score', 'N/A'))
                    
                    print(f"  {i}. {manufacturer} {model_name}")
                    print(f"     Material: {material}")
                    print(f"     Compatibility: {match_score}")
                    
                    # Show spine information
                    spine_specs = arrow_data.get('spine_specifications', [])
                    if spine_specs:
                        spec = spine_specs[0]
                        spine = spec.get('spine', 'N/A')
                        gpi = spec.get('gpi_weight', 'N/A')
                        diameter = spec.get('outer_diameter', 'N/A')
                        print(f"     Spine: {spine}# | GPI: {gpi} | Diameter: {diameter}\"")
                    print()
                
                print("✅ SUCCESS: Wood arrows are being returned!")
            else:
                print("❌ FAILURE: No wood arrows found")
                print("📋 Debug info:")
                print(f"   - Session ID: {result.get('session_id', 'N/A')}")
                print(f"   - Error: {result.get('error', 'No error message')}")
                print(f"   - Response keys: {list(result.keys())}")
        else:
            print(f"❌ API Error: HTTP {response.status_code}")
            print(json.dumps(result, indent=2))
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network Error: {e}")
    except json.JSONDecodeError as e:
        print(f"❌ JSON Error: {e}")
        print(f"Raw response: {response.text}")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

if __name__ == "__main__":
    test_wood_arrows_comprehensive()