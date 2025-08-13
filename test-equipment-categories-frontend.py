#!/usr/bin/env python3
"""
Test script to verify equipment categories are working via frontend proxy
"""

import requests
import json
import time

def test_equipment_categories():
    """Test equipment categories via different endpoints"""
    
    print("🧪 Testing Equipment Categories Integration")
    print("=" * 50)
    
    # Test direct API endpoint
    print("\n1. Testing Direct API Endpoint (port 5000):")
    try:
        response = requests.get('http://localhost:5000/api/equipment/categories', timeout=5)
        if response.status_code == 200:
            categories = response.json()
            print(f"✅ Direct API: {len(categories)} categories found")
            category_names = [cat['name'] for cat in categories]
            print(f"   Categories: {', '.join(category_names)}")
            
            # Check for new categories
            new_categories = ['Scope', 'Plunger', 'Other']
            found_new = [cat for cat in new_categories if cat in category_names]
            print(f"   New categories found: {', '.join(found_new)}")
        else:
            print(f"❌ Direct API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Direct API error: {e}")
    
    # Test frontend proxy (if available)
    print("\n2. Testing Frontend Proxy (port 3001):")
    try:
        response = requests.get('http://localhost:3001/api/equipment/categories', timeout=5)
        if response.status_code == 200:
            categories = response.json()
            print(f"✅ Frontend Proxy: {len(categories)} categories found")
            category_names = [cat['name'] for cat in categories]
            print(f"   Categories: {', '.join(category_names)}")
        else:
            print(f"❌ Frontend proxy failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Frontend proxy error: {e}")
    
    # Test equipment form schemas for new categories
    print("\n3. Testing Form Schemas for New Categories:")
    new_categories = ['Scope', 'Plunger', 'Other']
    
    for category in new_categories:
        try:
            response = requests.get(f'http://localhost:5000/api/equipment/form-schema/{category}', timeout=5)
            if response.status_code == 200:
                schema = response.json()
                print(f"✅ {category}: Schema with {len(schema.get('fields', []))} fields")
            else:
                print(f"❌ {category}: Schema failed ({response.status_code})")
        except Exception as e:
            print(f"❌ {category}: Schema error - {e}")
    
    print(f"\n{'='*50}")
    print("Test completed! Equipment categories should now be available in the frontend modal.")

if __name__ == '__main__':
    test_equipment_categories()