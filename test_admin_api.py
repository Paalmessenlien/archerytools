#!/usr/bin/env python3
"""
Test script to verify admin API functionality
"""

import requests
import json

# Test the admin check endpoint with a mock JWT token
# In a real scenario, you'd get this from the Google login flow

def test_admin_endpoints():
    base_url = "http://localhost:5000/api"
    
    print("Testing admin API endpoints...")
    
    # Test 1: Admin check without token (should fail)
    print("\n1. Testing admin check without token:")
    response = requests.get(f"{base_url}/admin/check")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 2: Check if database connection is working for bow setups
    print("\n2. Testing if UserDatabase.get_connection() method works:")
    try:
        from arrow_scraper.user_database import UserDatabase
        user_db = UserDatabase()
        conn = user_db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        conn.close()
        print(f"✅ UserDatabase.get_connection() works! Found {user_count} users.")
    except Exception as e:
        print(f"❌ UserDatabase.get_connection() failed: {e}")
    
    # Test 3: Check admin status directly from database
    print("\n3. Checking admin status from database:")
    try:
        from arrow_scraper.user_database import UserDatabase
        user_db = UserDatabase()
        
        # Check admin status for messenlien@gmail.com
        user = user_db.get_user_by_google_id('107018713238040970144')
        if user:
            print(f"✅ User: {user['email']}")
            print(f"✅ Admin status: {user.get('is_admin', False)}")
            print(f"✅ User ID: {user['id']}")
        else:
            print("❌ User not found")
    except Exception as e:
        print(f"❌ Error checking user: {e}")

if __name__ == "__main__":
    test_admin_endpoints()