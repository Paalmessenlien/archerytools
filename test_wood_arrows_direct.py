#!/usr/bin/env python3
import requests
import json

def test_wood_arrows():
    # Test with longbow and wood material preference
    api_url = "http://localhost:5000/api/tuning/recommendations"
    
    test_payload = {
        "draw_weight": 45,
        "draw_length": 28,
        "bow_type": "longbow",  # Maps to traditional
        "arrow_length": 29,
        "arrow_material": "Wood",  # Capitalized as frontend would send
        "arrow_rest_type": "drop_away",
        "point_weight": 100,
        "nock_type": "pin",
        "primary_goal": "maximum_accuracy"
    }
    
    print(f"Testing wood arrow API with payload:")
    print(json.dumps(test_payload, indent=2))
    print()
    
    try:
        response = requests.post(api_url, json=test_payload)
        result = response.json()
        
        if response.status_code == 200:
            print("✅ API call successful")
            print(f"Recommended spine: {result.get('recommended_spine', 'N/A')}")
            
            arrows = result.get('recommendations', [])
            print(f"Found {len(arrows)} recommendations")
            
            if arrows:
                print("\nFirst 3 wood arrow recommendations:")
                for i, arrow in enumerate(arrows[:3], 1):
                    arrow_data = arrow.get('arrow', arrow)
                    manufacturer = arrow_data.get('manufacturer', 'Unknown')
                    model_name = arrow_data.get('model_name', 'Unknown')
                    material = arrow_data.get('material', 'Unknown')
                    match_score = arrow.get('compatibility_score', arrow.get('match_score', 'N/A'))
                    
                    print(f"{i}. {manufacturer} {model_name}")
                    print(f"   Material: {material}")
                    print(f"   Match Score: {match_score}")
                    
                    # Check spine specs
                    spine_specs = arrow_data.get('spine_specifications', [])
                    if spine_specs:
                        spec = spine_specs[0]
                        print(f"   Spine: {spec.get('spine', 'N/A')}# | GPI: {spec.get('gpi_weight', 'N/A')}")
                    print()
            else:
                print("❌ No wood arrows found!")
                print("Issue: Material preference or spine matching problem")
        else:
            print(f"❌ API error: {response.status_code}")
            print(result)
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_wood_arrows()