#!/usr/bin/env python3
"""
Test local development authentication and admin status
"""

import requests
import json
import sys

def test_local_auth():
    """Test authentication and admin status on local development"""
    
    # Local development URLs
    api_url = "http://localhost:5000/api"
    frontend_url = "http://localhost:3000"
    
    print("🔧 Testing Local Development Authentication & Admin Status")
    print("=" * 70)
    
    # Test 1: Direct Flask API health check
    print("\n1. Testing Flask API health (direct)...")
    try:
        response = requests.get(f"{api_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Flask API health check successful")
            health_data = response.json()
            print(f"   Status: {health_data.get('status')}")
            print(f"   Database: {health_data.get('database_status')}")
        else:
            print(f"❌ Flask API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Flask API health check error: {e}")
        print("⚠️  Make sure Flask API is running: cd arrow_scraper && python api.py")
        return False
    
    # Test 2: Test admin endpoints (should return 401)
    print("\n2. Testing admin endpoints (should return 401)...")
    admin_endpoints = [
        "/admin/check",
        "/admin/manufacturers", 
        "/admin/migrations/status",
        "/admin/database/health"
    ]
    
    all_401 = True
    for endpoint in admin_endpoints:
        try:
            response = requests.get(f"{api_url}{endpoint}", timeout=5)
            if response.status_code == 401:
                print(f"✅ {endpoint}: Returns 401 (needs auth)")
            else:
                print(f"❌ {endpoint}: Unexpected status {response.status_code}")
                all_401 = False
        except Exception as e:
            print(f"❌ {endpoint}: Error - {e}")
            all_401 = False
    
    # Test 3: Check if Nuxt dev server is running
    print("\n3. Testing Nuxt frontend...")
    try:
        response = requests.get(frontend_url, timeout=5)
        if response.status_code == 200:
            print("✅ Nuxt dev server is running")
        else:
            print(f"⚠️  Nuxt dev server status: {response.status_code}")
    except Exception as e:
        print(f"❌ Nuxt dev server error: {e}")
        print("⚠️  Make sure Nuxt is running: cd frontend && npm run dev")
    
    # Test 4: Check if Nuxt is trying to proxy API calls
    print("\n4. Testing API proxy...")
    try:
        response = requests.get(f"{frontend_url}/api/health", timeout=5)
        if response.status_code == 404:
            print("❌ Nuxt returns 404 for /api/health - API proxy not configured")
            print("💡 This is the source of the problem!")
        elif response.status_code == 200:
            print("✅ Nuxt proxy working")
        else:
            print(f"⚠️  Nuxt proxy status: {response.status_code}")
    except Exception as e:
        print(f"❌ Nuxt proxy error: {e}")
    
    print("\n" + "=" * 70)
    print("🔍 DIAGNOSIS RESULTS:")
    
    if all_401:
        print("✅ Flask API is working correctly (returns 401 for protected endpoints)")
    else:
        print("❌ Flask API has issues")
    
    print("\n💡 SOLUTION FOR 404 ERRORS:")
    print("The frontend is making requests to localhost:3000/api/* instead of localhost:5000/api/*")
    print("This means the useRuntimeConfig is not working as expected.")
    print("\nTry:")
    print("1. Clear frontend cache: rm -rf .nuxt dist")
    print("2. Restart frontend: npm run dev")
    print("3. Check browser console for actual API URLs being used")
    print("4. Verify authentication: log out and log in again")
    
    return True

if __name__ == "__main__":
    test_local_auth()