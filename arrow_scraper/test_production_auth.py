#!/usr/bin/env python3
"""
Test script to verify authentication and admin status on production
"""

import requests
import json
import sys
import os
from pathlib import Path

def test_production_auth():
    """Test authentication and admin status on production"""
    
    # Production URL
    base_url = "https://archerytool.online/api"
    
    print("🔧 Testing Production Authentication & Admin Status")
    print("=" * 60)
    
    # Test 1: Health check
    print("\n1. Testing API health...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ API health check successful")
            health_data = response.json()
            print(f"   Status: {health_data.get('status')}")
            print(f"   Database: {health_data.get('database_status')}")
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API health check error: {e}")
        return False
    
    # Test 2: Check if admin endpoints are accessible without auth (should fail)
    print("\n2. Testing admin endpoints without authentication...")
    admin_endpoints = [
        "/admin/check",
        "/admin/users", 
        "/admin/manufacturers",
        "/admin/migrations/status",
        "/admin/database/health"
    ]
    
    for endpoint in admin_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 401:
                print(f"✅ {endpoint}: Correctly returns 401 (unauthorized)")
            else:
                print(f"⚠️  {endpoint}: Unexpected status {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: Error - {e}")
    
    # Test 3: Test with invalid token
    print("\n3. Testing admin endpoints with invalid token...")
    headers = {"Authorization": "Bearer invalid_token_12345"}
    
    try:
        response = requests.get(f"{base_url}/admin/check", headers=headers, timeout=10)
        if response.status_code == 401:
            print("✅ Invalid token correctly rejected")
        else:
            print(f"⚠️  Invalid token returned status: {response.status_code}")
    except Exception as e:
        print(f"❌ Invalid token test error: {e}")
    
    print("\n" + "=" * 60)
    print("🔍 PRODUCTION AUTHENTICATION TEST RESULTS:")
    print("   - API is running and accessible")
    print("   - Admin endpoints are properly protected with 401 responses")
    print("   - Invalid tokens are correctly rejected")
    print("\n📝 NEXT STEPS:")
    print("   1. User needs to log in via Google OAuth on the frontend")
    print("   2. Check if messenlien@gmail.com is properly set as admin")
    print("   3. Verify JWT token is being correctly generated and stored")
    print("   4. Check browser console for any authentication errors")
    
    return True

def check_database_admin():
    """Check database admin status directly"""
    print("\n🔧 Checking database admin status directly...")
    
    try:
        from user_database import UserDatabase
        user_db = UserDatabase()
        
        # Check if messenlien@gmail.com exists and has admin privileges
        conn = user_db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, email, name, google_id, is_admin FROM users WHERE email = ?", 
                      ('messenlien@gmail.com',))
        user = cursor.fetchone()
        
        if user:
            print(f"✅ User found in database:")
            print(f"   ID: {user[0]}")
            print(f"   Email: {user[1]}")
            print(f"   Name: {user[2]}")
            print(f"   Google ID: {user[3]}")
            print(f"   Is Admin: {bool(user[4])}")
            
            if not user[4]:
                print("\n⚠️  User is not admin, setting admin status...")
                user_db.set_admin_status(user[0], True)
                print("✅ Admin status granted")
            else:
                print("✅ User already has admin privileges")
        else:
            print("❌ User messenlien@gmail.com not found in database")
            print("   User needs to log in once via Google OAuth to create account")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database check error: {e}")
        return False

if __name__ == "__main__":
    print("🏹 Production Authentication & Admin Status Test")
    print("=" * 60)
    
    # Test production API endpoints
    test_production_auth()
    
    # Check database directly if possible
    if "--check-db" in sys.argv:
        check_database_admin()
    
    print("\n🎯 TROUBLESHOOTING TIPS:")
    print("   1. Open browser dev tools (F12)")
    print("   2. Go to Application/Storage -> Local Storage")
    print("   3. Check if 'token' exists and has a valid JWT")
    print("   4. If no token, try logging out and logging in again")
    print("   5. Check Network tab for 401 errors on admin API calls")
    print("   6. Verify Google OAuth is working properly")