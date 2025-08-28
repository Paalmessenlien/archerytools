
import os
import jwt
from functools import wraps
from flask import request, jsonify
from google.oauth2 import id_token
from google.auth.transport import requests
import httplib2 # For making HTTP requests
import json # For parsing JSON responses
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables - try multiple locations for robustness
env_paths = [
    Path(__file__).parent.parent / '.env',  # Root .env (local development)
    Path(__file__).parent / '.env',         # Local .env (fallback)
    Path('.env'),                           # Current directory (Docker)
]

for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path)
        break

from unified_database import UnifiedDatabase

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]
        if not token:
            return jsonify({"message": "Token is missing!"}), 401

        try:
            data = jwt.decode(token, os.environ.get("SECRET_KEY"), algorithms=["HS256"])
            db = UnifiedDatabase()
            current_user = db.get_user_by_id(data["user_id"])
            if not current_user:
                return jsonify({"message": "User not found!"}), 401
            
            # Only block suspended users - allow all others to access
            user_status = current_user.get('status')
            
            # Only block suspended users (keep admin ability to suspend if needed)
            if user_status == 'suspended':
                return jsonify({"message": "Account is suspended. Please contact an administrator."}), 403
                
        except Exception as e:
            return jsonify({"message": "Token is invalid!", "error": str(e)}), 401

        return f(current_user, *args, **kwargs)

    return decorated

from google.auth.transport import requests as google_requests
import requests as req

def get_user_from_google_token(authorization_code):
    try:
        client_id = os.environ.get("NUXT_PUBLIC_GOOGLE_CLIENT_ID")
        client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")
        
        print(f"DEBUG: Using Client ID (first 10 chars): {client_id[:10] if client_id else 'Not Loaded'}")
        print(f"DEBUG: Using Client Secret (first 5 chars): {client_secret[:5] if client_secret else 'Not Loaded'}")

        redirect_uri = 'postmessage'

        if not client_id or not client_secret:
            print("ERROR: Missing Google Client ID or Secret in environment variables.")
            return None, False

        token_url = "https://oauth2.googleapis.com/token"
        payload = {
            "code": authorization_code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }
        
        response = req.post(token_url, data=payload)
        token_data = response.json()

        if not response.ok:
            print(f"ERROR: Google OAuth request failed with status {response.status_code}.")
            print(f"ERROR: Response from Google: {token_data}")
            return None, False

        id_token_jwt = token_data.get("id_token")
        if not id_token_jwt:
            print(f"ERROR: No 'id_token' in Google's response: {token_data}")
            return None, False

        request_session = google_requests.Request()
        idinfo = id_token.verify_oauth2_token(id_token_jwt, request_session, client_id)

        google_id = idinfo["sub"]
        email = idinfo["email"]
        name = idinfo.get("name")
        profile_picture_url = idinfo.get("picture")

        db = UnifiedDatabase()
        user = db.get_user_by_google_id(google_id)
        is_new_user = False

        if not user:
            user = db.create_user(google_id, email, name, profile_picture_url)
            is_new_user = True
            
            # Set new user status based on email
            if email == "messenlien@gmail.com":
                # Admin user is always active
                db.set_admin_status(user['id'], True)
                db.update_user_status(user['id'], 'active')
                user['is_admin'] = True
                user['status'] = 'active'
                print(f"✅ Automatically granted admin access to {email}")
            else:
                # All new users are automatically active - no approval required
                try:
                    db.update_user_status(user['id'], 'active')
                    user['status'] = 'active'
                    print(f"✅ New user {email} created with active status - immediate access granted")
                except Exception as e:
                    # If status column doesn't exist yet, allow user through (backwards compatibility)
                    print(f"⚠️ Could not set active status for new user {email} (pre-migration): {e}")
                    user['status'] = 'active'  # Allow access
        else:
            # Existing user login
            if email == "messenlien@gmail.com" and not user.get('is_admin'):
                db.set_admin_status(user['id'], True)
                user['is_admin'] = True
                print(f"✅ Restored admin access to {email}")
            
            # Ensure admin is always active (if status column exists)
            if email == "messenlien@gmail.com":
                try:
                    if user.get('status') != 'active':
                        db.update_user_status(user['id'], 'active')
                        user['status'] = 'active'
                        print(f"✅ Ensured admin {email} has active status")
                except Exception as e:
                    # If status column doesn't exist yet, just continue (backwards compatibility)
                    print(f"⚠️ Could not ensure admin status (pre-migration): {e}")
                    user['status'] = 'active'
        
        # Allow all users to login - no approval required
        user_status = user.get('status', 'active')  # Default to active if no status
        user['status'] = user_status
        
        # Only block suspended users (keep admin ability to suspend if needed)
        if user_status == 'suspended':
            print(f"⛔ User {email} attempted login but is suspended - access denied")
            return None, False  # Only deny access for suspended users
        
        # Allow access for all other users (active, pending, or no status)
        print(f"✅ User {email} granted access with status: {user_status}")
        
        needs_profile_completion = is_new_user and not user.get('name')

        return user, needs_profile_completion
    except Exception as e:
        import traceback
        print(f"ERROR in get_user_from_google_token: {e}")
        traceback.print_exc()
        return None, False
