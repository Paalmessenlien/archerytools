#!/usr/bin/env python3

import requests
import json

# Test the spine calculation endpoint specifically
api_url = "http://localhost:5000/api/tuning/calculate-spine"

# Test payload with wood material preference and longbow
test_payload = {
    "draw_weight": 45,
    "draw_length": 28,
    "bow_type": "longbow",
    "arrow_length": 29,
    "arrow_material": "wood",
    "point_weight": 100
}

print("Testing spine calculation API:")
print(f"URL: {api_url}")
print(f"Payload: {json.dumps(test_payload, indent=2)}")
print()

try:
    response = requests.post(api_url, json=test_payload, timeout=30)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("Spine calculation result:")
        print(json.dumps(result, indent=2))
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"Request failed: {e}")