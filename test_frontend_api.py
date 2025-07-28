#!/usr/bin/env python3
"""Test the frontend API endpoint directly"""

import requests
import json

def test_frontend_api():
    print("🎯 Testing Frontend API Endpoint")
    print("=" * 50)
    
    # Test the exact API call that frontend would make
    api_url = "http://localhost:5000/api/tuning/recommendations"
    
    payload = {
        "draw_weight": 24,
        "draw_length": 28,
        "bow_type": "recurve",
        "arrow_length": 26,
        "point_weight": 100,
        "primary_goal": "maximum_accuracy",
        "shooting_style": "target",
        "experience_level": "intermediate"
    }
    
    print(f"📤 Sending API request:")
    print(f"   URL: {api_url}")
    print(f"   Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(api_url, json=payload, timeout=30)
        
        print(f"\n📥 API Response:")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            recommendations = data.get('recommendations', [])
            
            print(f"   Found {len(recommendations)} recommendations")
            
            if recommendations:
                for i, rec in enumerate(recommendations[:5]):
                    print(f"   {i+1}. {rec.get('manufacturer', 'Unknown')} {rec.get('model_name', 'Unknown')}")
                    print(f"      Spine: {rec.get('matched_spine', 'N/A')} (deviation: ±{rec.get('spine_deviation', 'N/A')})")
                    print(f"      Score: {rec.get('match_score', 'N/A')}")
                    print()
            else:
                print("   ❌ No recommendations returned!")
                print(f"   Full response: {json.dumps(data, indent=2)}")
        else:
            print(f"   Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Could not connect to API server")
        print("   Let's test the backend directly instead...")
        
        # Test backend directly
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'arrow_scraper'))
        
        from arrow_tuning_system import ArrowTuningSystem, ArcherProfile, BowConfiguration, BowType, TuningGoal
        
        print("\n🔧 Testing backend directly:")
        
        bow_config = BowConfiguration(
            draw_weight=payload['draw_weight'],
            draw_length=payload['draw_length'], 
            bow_type=BowType(payload['bow_type'])
        )
        
        archer_profile = ArcherProfile(
            name="Test User",
            bow_config=bow_config,
            shooting_style=payload['shooting_style'],
            experience_level=payload['experience_level'],
            arrow_length=float(payload['arrow_length']),
            point_weight_preference=float(payload['point_weight'])
        )
        
        ts = ArrowTuningSystem()
        session = ts.create_tuning_session(
            archer_profile,
            tuning_goals=[TuningGoal(payload['primary_goal'].upper())]
        )
        
        print(f"   Backend found {len(session.recommended_arrows)} arrows:")
        for i, arrow in enumerate(session.recommended_arrows[:5]):
            print(f"   {i+1}. {arrow.manufacturer} {arrow.model_name}")
            print(f"      Spine: {arrow.matched_spine} (deviation: ±{arrow.spine_deviation:.0f})")
            print(f"      Score: {arrow.match_score:.1f}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_frontend_api()