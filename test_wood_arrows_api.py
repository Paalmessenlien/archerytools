#!/usr/bin/env python3

import requests
import json

# Test the API directly to see if wood arrow material preference works
api_url = "http://localhost:5000/api/tuning/recommendations"

# Test payload with wood material preference
test_payload = {
    "draw_weight": 45,
    "draw_length": 28,
    "bow_type": "longbow",
    "arrow_length": 29,
    "arrow_material": "wood",  # This is the key field
    "arrow_rest_type": "drop_away",
    "point_weight": 100,
    "nock_type": "pin",
    "vane_type": "plastic",
    "vane_length": 4,
    "number_of_vanes": 3
}

print("Testing wood arrow API request:")
print(f"URL: {api_url}")
print(f"Payload: {json.dumps(test_payload, indent=2)}")
print()

try:
    response = requests.post(api_url, json=test_payload, timeout=30)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        arrows = result.get('recommended_arrows', [])
        print(f"Found {len(arrows)} arrow recommendations")
        
        if arrows:
            print(f"Recommended spine: {result.get('recommended_spine', 'N/A')}")
            print("\nRaw first recommendation data:")
            print(json.dumps(arrows[0], indent=2))
            print("\nFirst few recommendations:")
            for i, arrow in enumerate(arrows[:3], 1):
                # Check both possible structures
                arrow_data = arrow.get('arrow', arrow)  # Handle nested structure
                material = arrow_data.get('material', 'Unknown')
                manufacturer = arrow_data.get('manufacturer', 'Unknown')
                model_name = arrow_data.get('model_name', 'Unknown')
                match_score = arrow.get('compatibility_score', arrow.get('match_score', 'N/A'))
                
                print(f"{i}. {manufacturer} {model_name}")
                print(f"   Material: {material}")
                print(f"   Match Score: {match_score}")
                print()
        else:
            print("No arrow recommendations found!")
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"Request failed: {e}")