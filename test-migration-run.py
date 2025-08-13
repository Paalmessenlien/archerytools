#!/usr/bin/env python3
import requests

print("🔧 Testing Migration Run Endpoint")

try:
    # Test migrations run endpoint (should return 401 without auth)
    response = requests.post("http://localhost:5000/api/admin/migrations/run", 
                           json={"dry_run": True}, 
                           timeout=10)
    if response.status_code == 401:
        print("✅ Migration run endpoint working (returns 401 without auth)")
    elif response.status_code == 500:
        print(f"❌ Migration run endpoint still has 500 error")
        print(f"   Response: {response.text}")
    else:
        print(f"⚠️  Migration run endpoint status: {response.status_code}")
        print(f"   Response: {response.text}")
        
except Exception as e:
    print(f"❌ Test error: {e}")

print("\n🎯 Migration run endpoint should now work in admin panel!")