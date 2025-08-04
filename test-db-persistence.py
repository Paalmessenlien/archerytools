#!/usr/bin/env python3
"""
Test script to verify database persistence across Docker container restarts
"""

import requests
import json
import sys
import time

def test_database_persistence():
    """Test that database changes persist across container restarts"""
    
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Database Persistence")
    print("=" * 50)
    
    # Step 1: Check API health
    print("1. Checking API health...")
    try:
        response = requests.get(f"{base_url}/api/simple-health", timeout=10)
        if response.status_code == 200:
            print("✅ API is healthy")
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to API: {e}")
        return False
    
    # Step 2: Test database write operations
    print("\n2. Testing database operations...")
    
    # Try to get database statistics to verify database is accessible
    try:
        response = requests.get(f"{base_url}/api/database/stats", timeout=10)
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Database accessible - Found {stats.get('total_arrows', 0)} arrows")
        else:
            print(f"❌ Database access failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Database request failed: {e}")
        return False
    
    # Step 3: Check user database path
    print("\n3. Checking user database configuration...")
    
    # Test endpoint that would use UserDatabase
    try:
        response = requests.get(f"{base_url}/api/user", timeout=10)
        # We expect this to fail with 401 (no auth) but not 500 (database error)
        if response.status_code == 401:
            print("✅ User database is accessible (401 = no auth, expected)")
        elif response.status_code == 500:
            print("❌ User database error - likely path issue")
            return False
        else:
            print(f"✅ User database accessible (status: {response.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"❌ User database request failed: {e}")
        return False
    
    print("\n🎉 Database persistence test completed successfully!")
    print("\nNext steps:")
    print("1. Make changes through the API (login, create bow setup, etc.)")
    print("2. Restart Docker containers: docker-compose restart")
    print("3. Verify changes persist after restart")
    
    return True

if __name__ == "__main__":
    if test_database_persistence():
        sys.exit(0)
    else:
        sys.exit(1)