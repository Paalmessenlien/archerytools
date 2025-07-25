#!/usr/bin/env python3
"""
Test the recommendations API endpoint directly
"""

import requests
import json

def test_recommendations_api():
    """Test the recommendations API endpoint"""
    
    print("🔧 Testing recommendations API endpoint...")
    
    # Test data
    test_payload = {
        'draw_weight': 45.0,
        'draw_length': 28.0,
        'bow_type': 'traditional',
        'shooting_style': 'target',
        'archer_name': 'Test Archer',
        'experience_level': 'intermediate',
        'primary_goal': 'maximum_accuracy',
        'arrow_type': 'target_outdoor'
    }
    
    print(f"📊 Sending payload: {test_payload}")
    
    try:
        # Send POST request to recommendations endpoint
        response = requests.post(
            'http://127.0.0.1:5000/api/tuning/recommendations',
            json=test_payload,
            timeout=30
        )
        
        print(f"📡 Response status: {response.status_code}")
        print(f"📡 Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success!")
            print(f"   Recommended arrows: {len(data.get('recommended_arrows', []))}")
            print(f"   Total compatible: {data.get('total_compatible', 0)}")
            
            # Show first recommendation
            if data.get('recommended_arrows'):
                first_rec = data['recommended_arrows'][0]
                arrow_info = first_rec['arrow']
                print(f"\n🎯 First recommendation:")
                print(f"   {arrow_info['manufacturer']} {arrow_info['model_name']}")
                print(f"   Compatibility score: {first_rec['compatibility_score']}")
                print(f"   Match percentage: {first_rec['match_percentage']}%")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response text: {response.text}")
            
    except Exception as e:
        print(f"❌ Request error: {e}")

if __name__ == "__main__":
    test_recommendations_api()