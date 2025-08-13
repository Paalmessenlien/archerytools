#!/usr/bin/env python3
"""
Test which database path the API is actually using
"""

import requests
import json

def test_api_database():
    """Test API database path and equipment tables"""
    
    print("🔍 Testing API Database Connection")
    print("=" * 50)
    
    # Test categories endpoint (should work)
    try:
        response = requests.get('http://localhost:5000/api/equipment/categories')
        if response.status_code == 200:
            categories = response.json()
            print(f"✅ Categories API: {len(categories)} categories")
            category_names = [cat['name'] for cat in categories]
            print(f"   Categories: {', '.join(category_names)}")
        else:
            print(f"❌ Categories API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Categories API error: {e}")
    
    # Test form schema for each new category
    new_categories = ['Scope', 'Plunger', 'Other']
    
    for category in new_categories:
        try:
            response = requests.get(f'http://localhost:5000/api/equipment/form-schema/{category}')
            print(f"\n📋 {category} Form Schema:")
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                schema = response.json()
                fields = schema.get('fields', [])
                print(f"   ✅ Schema: {len(fields)} fields")
                field_names = [f['name'] for f in fields]
                print(f"   Fields: {', '.join(field_names)}")
            else:
                error_response = response.json() if response.content else {}
                print(f"   ❌ Error: {error_response.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"   ❌ Request error: {e}")
    
    # Test database stats to see which database is being used
    try:
        response = requests.get('http://localhost:5000/api/database/stats')
        if response.status_code == 200:
            stats = response.json()
            print(f"\n📊 Database Stats:")
            print(f"   Total arrows: {stats.get('total_arrows', 0)}")
            print(f"   Total manufacturers: {stats.get('total_manufacturers', 0)}")
        else:
            print(f"\n❌ Database stats failed: {response.status_code}")
    except Exception as e:
        print(f"\n❌ Database stats error: {e}")

if __name__ == '__main__':
    test_api_database()