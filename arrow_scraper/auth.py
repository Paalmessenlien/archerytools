
import os
import jwt
from functools import wraps
from flask import request, jsonify
from google.oauth2 import id_token
from google.auth.transport import requests

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

def get_user_from_google_token(token):
    try:
        # Specify the CLIENT_ID of the app that accesses the backend
        CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)

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
            cursor.execute(
                "INSERT INTO users (google_id, email, name, profile_picture_url) VALUES (?, ?, ?, ?)",
                (google_id, email, name, profile_picture_url),
            )
            conn.commit()
            cursor.execute("SELECT * FROM users WHERE google_id = ?", (google_id,))
            user = cursor.fetchone()

        return user
    except ValueError:
        # Invalid token
        return None
