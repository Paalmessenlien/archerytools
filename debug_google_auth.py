#!/usr/bin/env python3
"""
Debug script for Google OAuth authentication
"""

import os
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_paths = [
    Path(__file__).parent / '.env',
    Path(__file__).parent / 'arrow_scraper' / '.env',
]

for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Loaded .env from {env_path}")
        break

def test_google_oauth():
    # Check environment variables
    client_id = os.environ.get("NUXT_PUBLIC_GOOGLE_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")
    
    print(f"Client ID: {client_id[:20]}..." if client_id else "❌ MISSING")
    print(f"Client Secret: {client_secret[:10]}..." if client_secret else "❌ MISSING")
    
    if not client_id or not client_secret:
        print("❌ Missing Google OAuth credentials")
        return
    
    # Test with the authorization code from the error
    auth_code = "4/0AVMBsJgISPdPfNWnefaOWRN-aRv77kMLcRKbCOVPe54EkU2GViQro0j-d3JphtXrykZ0gg"
    
    # Make the token exchange request
    token_url = "https://oauth2.googleapis.com/token"
    payload = {
        "code": auth_code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": "postmessage",
        "grant_type": "authorization_code",
    }
    
    print(f"🔄 Making token exchange request to Google...")
    response = requests.post(token_url, data=payload)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 400:
        print("❌ This authorization code has likely expired or been used already")
        print("💡 Authorization codes expire quickly and are single-use")
    elif response.status_code == 200:
        print("✅ Token exchange successful!")
        token_data = response.json()
        print(f"Received ID token: {token_data.get('id_token', 'NOT FOUND')[:50]}...")
    else:
        print(f"❌ Unexpected response status: {response.status_code}")

if __name__ == "__main__":
    test_google_oauth()