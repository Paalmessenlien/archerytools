#!/usr/bin/env python3

import requests
import json

# Test the API with debugging
api_url = "http://localhost:5000/api/tuning/recommendations"

# Test with explicit material preference
test_payload = {
    "draw_weight": 45,
    "draw_length": 28,
    "bow_type": "longbow",  # Maps to traditional
    "arrow_length": 29,
    "arrow_material": "Wood",
    "point_weight": 100
}

print("Testing material preference passing:")
print(f"Sending: arrow_material = '{test_payload['arrow_material']}'")
print()

try:
    response = requests.post(api_url, json=test_payload, timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        arrows = result.get('recommended_arrows', [])
        print(f"Status: {response.status_code}")
        print(f"Found {len(arrows)} arrows")
        
        # Test spine calculation directly too
        spine_url = "http://localhost:5000/api/tuning/calculate-spine"
        spine_response = requests.post(spine_url, json=test_payload, timeout=30)
        
        if spine_response.status_code == 200:
            spine_result = spine_response.json()
            print(f"Calculated spine: {spine_result.get('recommended_spine')}")
            print(f"Spine range: {spine_result.get('spine_range')}")
            if 'notes' in spine_result:
                print("Notes:")
                for note in spine_result['notes']:
                    print(f"  - {note}")
        
    else:
        print(f"Error: {response.status_code} - {response.text}")
        
except Exception as e:
    print(f"Request failed: {e}")