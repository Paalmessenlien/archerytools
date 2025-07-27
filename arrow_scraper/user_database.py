import sqlite3
import os
from pathlib import Path

class UserDatabase:
    def __init__(self, db_path="user_data.db"):
        self.db_path = self._resolve_db_path(db_path)
        self._initialize_db()

    def _resolve_db_path(self, db_path):
        # Prioritize absolute path if provided
        if Path(db_path).is_absolute():
            return db_path
        
        # Try common locations for user_data.db
        possible_paths = [
            Path("/app") / db_path,  # Docker/production path
            Path(__file__).parent / db_path, # Default development path (arrow_scraper/)
            Path(__file__).parent.parent / db_path # Root directory path
        ]

        for p in possible_paths:
            if p.parent.exists(): # Ensure parent directory exists before trying to create file
                print(f"Attempting to use user database path: {p}")
                return str(p)
        
        # Fallback to default if no suitable path found
        print(f"Warning: No ideal path found for user database. Defaulting to: {db_path}")
        return db_path

    def _initialize_db(self):
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    google_id TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    name TEXT,
                    profile_picture_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            print(f"✅ User database initialized at {self.db_path}")
        except sqlite3.Error as e:
            print(f"❌ Error initializing user database at {self.db_path}: {e}")
        finally:
            if conn:
                conn.close()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row # Return rows as dictionary-like objects
        return conn

    def get_user_by_google_id(self, google_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE google_id = ?", (google_id,))
        user = cursor.fetchone()
        conn.close()
        return user

    def create_user(self, google_id, email, name, profile_picture_url):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (google_id, email, name, profile_picture_url) VALUES (?, ?, ?, ?)",
                (google_id, email, name, profile_picture_url),
            )
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            return self.get_user_by_id(user_id)
        except sqlite3.IntegrityError as e:
            print(f"Error creating user (likely duplicate): {e}")
            conn.close()
            return None
        except Exception as e:
            print(f"Error creating user: {e}")
            conn.close()
            raise

    def get_user_by_id(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()
        return user

    def update_user_profile(self, user_id, name=None, profile_picture_url=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        updates = []
        params = []
        if name is not None:
            updates.append("name = ?")
            params.append(name)
        if profile_picture_url is not None:
            updates.append("profile_picture_url = ?")
            params.append(profile_picture_url)
        
        if not updates:
            conn.close()
            return self.get_user_by_id(user_id) # No updates, return current user

        params.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
        
        try:
            cursor.execute(query, tuple(params))
            conn.commit()
            conn.close()
            return self.get_user_by_id(user_id)
        except Exception as e:
            print(f"Error updating user profile: {e}")
            conn.close()
            raise

if __name__ == "__main__":
    # Example Usage
    print("--- Initializing User Database ---")
    user_db = UserDatabase()
    
    # Test creating a user
    print("\n--- Creating Test User ---")
    test_google_id = "test_google_id_123"
    test_email = "test@example.com"
    test_name = "Test User"
    test_picture = "http://example.com/pic.jpg"

    user = user_db.get_user_by_google_id(test_google_id)
    if not user:
        new_user = user_db.create_user(test_google_id, test_email, test_name, test_picture)
        if new_user:
            print(f"Created user: {dict(new_user)}")
        else:
            print("Failed to create user.")
    else:
        print(f"User already exists: {dict(user)}")

    # Test updating user
    print("\n--- Updating Test User ---")
    if user:
        updated_user = user_db.update_user_profile(user["id"], name="Updated Test User", profile_picture_url="http://example.com/new_pic.jpg")
        if updated_user:
            print(f"Updated user: {dict(updated_user)}")
        else:
            print("Failed to update user.")
    
    # Test fetching user by ID
    print("\n--- Fetching User by ID ---")
    if user:
        fetched_user = user_db.get_user_by_id(user["id"])
        if fetched_user:
            print(f"Fetched user by ID: {dict(fetched_user)}")
        else:
            print("User not found by ID.")
    
    print("\n--- User Database Operations Complete ---")
