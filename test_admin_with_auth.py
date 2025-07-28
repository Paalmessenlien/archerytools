#!/usr/bin/env python3
"""
Test admin functionality with authentication token
"""

import jwt
import requests
import json
from datetime import datetime, timedelta, timezone

def test_admin_with_token():
    """Test admin endpoints with a real JWT token"""
    
    # Create a test JWT token for messenlien@gmail.com (same format as the real auth flow)
    secret_key = "dev-secret-key-change-for-production"  # From .env file
    user_id = 1  # The user ID we know from the database
    
    # Create JWT token
    token_payload = {
        'user_id': user_id,
        'exp': datetime.now(timezone.utc) + timedelta(hours=24)
    }
    
    test_token = jwt.encode(token_payload, secret_key, algorithm='HS256')
    print(f"Created test token for user_id: {user_id}")
    
    base_url = "http://localhost:5000/api"
    headers = {'Authorization': f'Bearer {test_token}'}
    
    # Test 1: Check admin status
    print("\n1. Testing admin check with token:")
    response = requests.get(f"{base_url}/admin/check", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 2: Get all users (admin only)
    print("\n2. Testing get all users (admin only):")
    response = requests.get(f"{base_url}/admin/users", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {data.get('total', 0)} users")
        for user in data.get('users', []):
            print(f"  - {user.get('email')} (Admin: {user.get('is_admin', False)})")
    else:
        print(f"Error: {response.text}")
    
    # Test 3: Get user details
    print("\n3. Testing get user details:")
    response = requests.get(f"{base_url}/user", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

if __name__ == "__main__":
    test_admin_with_token()