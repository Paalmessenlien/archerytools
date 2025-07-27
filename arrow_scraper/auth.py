
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

from arrow_database import ArrowDatabase
from user_database import UserDatabase

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
            user_db = UserDatabase()
            current_user = user_db.get_user_by_id(data["user_id"])
            if not current_user:
                return jsonify({"message": "User not found!"}), 401
        except Exception as e:
            return jsonify({"message": "Token is invalid!", "error": str(e)}), 401

        return f(current_user, *args, **kwargs)

    return decorated

def get_user_from_google_token(authorization_code):
    try:
        # Exchange authorization code for access token and ID token
        client_id = os.environ.get("NUXT_PUBLIC_GOOGLE_CLIENT_ID") # Use NUXT_PUBLIC_GOOGLE_CLIENT_ID from frontend
        client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")
        
        # The redirect_uri must match what you configured in Google Cloud Console
        # For the initCodeClient flow, it's often 'postmessage' or the base URL of your app
        # Use environment variable for production, fallback to localhost for development
        redirect_uri = os.environ.get('GOOGLE_REDIRECT_URI', 'http://localhost:3000')

        if not client_id or not client_secret:
            return None

        # Build the request to Google's token endpoint
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": authorization_code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }

        import urllib.parse
        encoded_data = urllib.parse.urlencode(data)
        
        http = httplib2.Http()
        resp, content = http.request(
            token_url,
            "POST",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            body=encoded_data
        )
        
        token_data = json.loads(content.decode("utf-8"))

        if "error" in token_data:
            return None

        id_token_jwt = token_data.get("id_token")
        if not id_token_jwt:
            return None

        # Verify the ID token
        idinfo = id_token.verify_oauth2_token(id_token_jwt, requests.Request(), client_id)

        # ID token is valid. Get the user's Google Account ID from the decoded token.
        google_id = idinfo["sub"]
        email = idinfo["email"]
        name = idinfo.get("name")
        profile_picture_url = idinfo.get("picture")

        user_db = UserDatabase()

        # Check if user already exists
        user = user_db.get_user_by_google_id(google_id)
        is_new_user = False

        if not user:
            # Create new user
            user = user_db.create_user(google_id, email, name, profile_picture_url)
            is_new_user = True
        
        # Check if user needs profile completion (True for all new users)
        needs_profile_completion = is_new_user

        return user, needs_profile_completion
    except ValueError as e:
        return None, False
    except Exception as e:
        import traceback
        return None, False
