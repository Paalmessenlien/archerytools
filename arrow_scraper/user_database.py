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

    def get_connection(self):
        """Get a database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize_db(self):
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    google_id TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    name TEXT,
                    profile_picture_url TEXT,
                    is_admin BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create bow_setups table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bow_setups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    bow_type TEXT NOT NULL,
                    draw_weight REAL NOT NULL,
                    draw_length REAL NOT NULL,
                    arrow_length REAL,
                    point_weight REAL,
                    nock_weight REAL,
                    fletching_weight REAL,
                    insert_weight REAL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            """)
            
            conn.commit()
            print(f"✅ User database initialized at {self.db_path}")
        except sqlite3.Error as e:
            print(f"❌ Error initializing user database at {self.db_path}: {e}")
        finally:
            if conn:
                conn.close()

    def create_user(self, google_id, email, name=None, profile_picture_url=None):
        """Create a new user and return user data"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO users (google_id, email, name, profile_picture_url)
                VALUES (?, ?, ?, ?)
            """, (google_id, email, name, profile_picture_url))
            
            user_id = cursor.lastrowid
            conn.commit()
            
            # Return the created user
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            return dict(cursor.fetchone())
            
        except sqlite3.Error as e:
            print(f"Error creating user: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def get_user_by_google_id(self, google_id):
        """Get user by Google ID"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM users WHERE google_id = ?", (google_id,))
            user = cursor.fetchone()
            return dict(user) if user else None
            
        except sqlite3.Error as e:
            print(f"Error getting user by Google ID: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def get_user_by_id(self, user_id):
        """Get user by ID"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            return dict(user) if user else None
            
        except sqlite3.Error as e:
            print(f"Error getting user by ID: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def update_user_profile(self, user_id, name=None, profile_picture_url=None):
        """Update user profile"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            update_fields = []
            params = []
            
            if name is not None:
                update_fields.append("name = ?")
                params.append(name)
            
            if profile_picture_url is not None:
                update_fields.append("profile_picture_url = ?")
                params.append(profile_picture_url)
                
            if not update_fields:
                return None
                
            params.append(user_id)
            
            cursor.execute(f"""
                UPDATE users SET {', '.join(update_fields)}
                WHERE id = ?
            """, params)
            
            conn.commit()
            
            # Return updated user
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            return dict(cursor.fetchone())
            
        except sqlite3.Error as e:
            print(f"Error updating user profile: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def delete_user(self, user_id):
        """Delete user and all related data"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            
            return cursor.rowcount > 0
            
        except sqlite3.Error as e:
            print(f"Error deleting user: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def get_user_bow_setups(self, user_id):
        """Get all bow setups for a user"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM bow_setups WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
            setups = cursor.fetchall()
            return [dict(setup) for setup in setups]
            
        except sqlite3.Error as e:
            print(f"Error getting bow setups: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def create_bow_setup(self, user_id, setup_data):
        """Create a new bow setup for a user"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO bow_setups (
                    user_id, name, bow_type, draw_weight, draw_length,
                    arrow_length, point_weight, nock_weight, fletching_weight,
                    insert_weight, description
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                setup_data.get('name'),
                setup_data.get('bow_type'),
                setup_data.get('draw_weight'),
                setup_data.get('draw_length'),
                setup_data.get('arrow_length'),
                setup_data.get('point_weight'),
                setup_data.get('nock_weight'),
                setup_data.get('fletching_weight'),
                setup_data.get('insert_weight'),
                setup_data.get('description')
            ))
            
            setup_id = cursor.lastrowid
            conn.commit()
            
            # Return the created setup
            cursor.execute("SELECT * FROM bow_setups WHERE id = ?", (setup_id,))
            return dict(cursor.fetchone())
            
        except sqlite3.Error as e:
            print(f"Error creating bow setup: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def delete_bow_setup(self, user_id, setup_id):
        """Delete a bow setup if it belongs to the user"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM bow_setups WHERE id = ? AND user_id = ?", (setup_id, user_id))
            conn.commit()
            
            return cursor.rowcount > 0
            
        except sqlite3.Error as e:
            print(f"Error deleting bow setup: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def is_user_admin(self, user_id):
        """Check if a user is an admin"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT is_admin FROM users WHERE id = ?", (user_id,))
            result = cursor.fetchone()
            return bool(result[0]) if result else False
            
        except sqlite3.Error as e:
            print(f"Error checking admin status: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def get_all_users(self):
        """Get all users (admin only)"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
            users = cursor.fetchall()
            return [dict(user) for user in users]
            
        except sqlite3.Error as e:
            print(f"Error getting all users: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def set_admin_status(self, user_id, is_admin):
        """Set admin status for a user"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("UPDATE users SET is_admin = ? WHERE id = ?", (is_admin, user_id))
            conn.commit()
            
            return cursor.rowcount > 0
            
        except sqlite3.Error as e:
            print(f"Error setting admin status: {e}")
            return False
        finally:
            if conn:
                conn.close()
