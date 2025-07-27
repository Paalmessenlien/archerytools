
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

# Load environment variables from root .env file
load_dotenv(Path(__file__).parent.parent / '.env')

from arrow_database import ArrowDatabase

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
            db = ArrowDatabase()
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (data["user_id"],))
            current_user = cursor.fetchone()
            if not current_user:
                return jsonify({"message": "User not found!"}), 401
        except Exception as e:
            return jsonify({"message": "Token is invalid!", "error": str(e)}), 401

        return f(current_user, *args, **kwargs)

    return decorated

def get_user_from_google_token(authorization_code):
    print("[Auth Debug] Entering get_user_from_google_token")
    print(f"[Auth Debug] Received authorization_code: {authorization_code[:10]}...")
    try:
        # Exchange authorization code for access token and ID token
        client_id = os.environ.get("NUXT_PUBLIC_GOOGLE_CLIENT_ID") # Use NUXT_PUBLIC_GOOGLE_CLIENT_ID from frontend
        client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")
        
        # The redirect_uri must match what you configured in Google Cloud Console
        # For the initCodeClient flow, it's often 'postmessage' or the base URL of your app
        # Use environment variable for production, fallback to localhost for development
        redirect_uri = os.environ.get('GOOGLE_REDIRECT_URI', 'http://localhost:3000')

        print(f"[Auth Debug] CLIENT_ID: {client_id}")
        print(f"[Auth Debug] CLIENT_SECRET: {client_secret[:5]}...{client_secret[-5:]}" if client_secret else "[Auth Debug] CLIENT_SECRET: NOT SET")
        print(f"[Auth Debug] REDIRECT_URI: {redirect_uri}")

        if not client_id or not client_secret:
            print("Error: GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET not set in environment variables.")
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
        
        print(f"[Auth Debug] Google Token Endpoint Response Status: {resp.status}")
        print(f"[Auth Debug] Google Token Endpoint Response Content: {content.decode('utf-8')}")

        token_data = json.loads(content.decode("utf-8"))
        print(f"[Auth Debug] Parsed Token Data: {token_data}")

        if "error" in token_data:
            print(f"Error exchanging code for token: {token_data.get('error_description', token_data['error'])}")
            return None

        id_token_jwt = token_data.get("id_token")
        print(f"[Auth Debug] ID Token JWT: {id_token_jwt[:10]}..." if id_token_jwt else "[Auth Debug] ID Token JWT: NOT FOUND")
        if not id_token_jwt:
            print("Error: No ID token found in response from Google.")
            return None

        # Verify the ID token
        idinfo = id_token.verify_oauth2_token(id_token_jwt, requests.Request(), client_id)
        print(f"[Auth Debug] ID Token Verified. idinfo: {idinfo}")

        # ID token is valid. Get the user's Google Account ID from the decoded token.
        google_id = idinfo["sub"]
        email = idinfo["email"]
        name = idinfo.get("name")
        profile_picture_url = idinfo.get("picture")

        db = ArrowDatabase()
        conn = db.get_connection()
        cursor = conn.cursor()

        # Check if user already exists
        cursor.execute("SELECT * FROM users WHERE google_id = ?", (google_id,))
        user = cursor.fetchone()

        if not user:
            # Create new user
            print(f"[Auth Debug] Creating new user: {email}")
            cursor.execute(
                "INSERT INTO users (google_id, email, name, profile_picture_url) VALUES (?, ?, ?, ?)",
                (google_id, email, name, profile_picture_url),
            )
            conn.commit()
            cursor.execute("SELECT * FROM users WHERE google_id = ?", (google_id,))
            user = cursor.fetchone()
            print(f"[Auth Debug] New user created: {user}")
        else:
            print(f"[Auth Debug] User already exists: {email}")

        return user
    except ValueError as e:
        print(f"[Auth Error] ValueError during Google token verification: {e}")
        return None
    except Exception as e:
        print(f"[Auth Error] Unexpected error in get_user_from_google_token: {e}")
        import traceback
        traceback.print_exc()
        return None
