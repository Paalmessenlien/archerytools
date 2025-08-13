#!/usr/bin/env python3
import requests

print("🔧 Testing Migration Status Endpoint")

try:
    # Test health endpoint
    response = requests.get("http://localhost:5000/api/health", timeout=5)
    if response.status_code == 200:
        print("✅ Basic health endpoint working")
    else:
        print(f"❌ Health endpoint failed: {response.status_code}")
        
    # Test migrations endpoint (should return 401 without auth)
    response = requests.get("http://localhost:5000/api/admin/migrations/status", timeout=5)
    if response.status_code == 401:
        print("✅ Migration status endpoint working (returns 401 without auth)")
    elif response.status_code == 500:
        print(f"❌ Migration status endpoint still has 500 error")
        print(f"   Response: {response.text}")
    else:
        print(f"⚠️  Migration status endpoint status: {response.status_code}")
        print(f"   Response: {response.text}")
        
except Exception as e:
    print(f"❌ Test error: {e}")

print("\n🎯 Now try the admin panel - both endpoints should work!")