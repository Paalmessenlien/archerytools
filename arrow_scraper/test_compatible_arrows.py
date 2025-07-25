#!/usr/bin/env python3
"""
Test compatible arrows endpoint directly
"""

import requests
import json

def test_compatible_arrows_api():
    """Test the compatible arrows API endpoint directly"""
    
    print("🔧 Testing compatible arrows API endpoint...")
    
    # Test data similar to what frontend would send
    test_payload = {
        'bow_config': {
            'bow_type': 'traditional',
            'draw_weight': 45,
            'draw_length': 28.0,
            'arrow_material': 'wood',
            'arrow_length': 29.0
        },
        'filters': {
            'manufacturer': None,
            'search': None
        }
    }
    
    print(f"📊 Sending payload: {json.dumps(test_payload, indent=2)}")
    
    try:
        # Send POST request to compatible arrows endpoint
        response = requests.post(
            'http://127.0.0.1:5000/api/arrows/compatible',
            json=test_payload,
            timeout=30
        )
        
        print(f"📡 Response status: {response.status_code}")
        print(f"📡 Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success!")
            print(f"   Compatible arrows: {len(data.get('compatible_arrows', []))}")
            print(f"   Total compatible: {data.get('total_compatible', 0)}")
            
            # Show first few arrows
            if data.get('compatible_arrows'):
                print(f"\n🎯 First few compatible arrows:")
                for i, arrow in enumerate(data['compatible_arrows'][:3]):
                    print(f"   {i+1}. {arrow['manufacturer']} {arrow['model_name']}")
                    print(f"      Material: {arrow.get('material', 'N/A')}")
                    print(f"      Spine: {arrow.get('spine_display', arrow.get('min_spine', 'N/A'))}")
        else:
            print(f"❌ Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Raw response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: API server not running on localhost:5000")
    except Exception as e:
        print(f"❌ Request error: {e}")

def test_database_directly():
    """Test the database search functionality directly"""
    
    print("\n🔧 Testing database search directly...")
    
    try:
        from arrow_database import ArrowDatabase
        
        db = ArrowDatabase()
        
        # Test search with similar parameters
        print("🔍 Searching for arrows...")
        results = db.search_arrows(limit=10)
        
        print(f"Found {len(results)} arrows")
        
        # Test material filtering logic
        print("\n🔍 Testing material filtering...")
        for arrow in results[:5]:
            arrow_material = arrow.get('material', '').lower()
            is_wood = 'wood' in arrow_material
            print(f"   {arrow['model_name'][:30]:30} | Material: {arrow.get('material', 'N/A'):15} | Wood: {is_wood}")
            
    except Exception as e:
        print(f"❌ Database test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_database_directly()
    print("\n" + "="*50)
    test_compatible_arrows_api()