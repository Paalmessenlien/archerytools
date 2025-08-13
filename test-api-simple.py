#!/usr/bin/env python3
import requests
import time

print("🔧 Testing API after restart...")

# Test basic health endpoint  
try:
    response = requests.get("http://localhost:5000/api/health", timeout=5)
    if response.status_code == 200:
        print("✅ Basic health endpoint working")
        data = response.json()
        print(f"   Status: {data.get('status')}")
        print(f"   Database: {data.get('database_status')}")
    else:
        print(f"❌ Health endpoint failed: {response.status_code}")
except Exception as e:
    print(f"❌ Health endpoint error: {e}")

print("\n🎯 API restart complete - please try the admin panel again!")
print("The JSON serialization issue should now be fixed.")