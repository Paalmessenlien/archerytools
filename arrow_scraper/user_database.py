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
                    draw_length REAL DEFAULT 28.0,
                    skill_level TEXT DEFAULT 'intermediate',
                    shooting_style TEXT DEFAULT 'target',
                    preferred_manufacturers TEXT,
                    notes TEXT,
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
            
            # Run migration to add new columns if they don't exist
            self._migrate_user_profile_fields(cursor)
            
            print(f"✅ User database initialized at {self.db_path}")
        except sqlite3.Error as e:
            print(f"❌ Error initializing user database at {self.db_path}: {e}")
        finally:
            if conn:
                conn.close()

    def _migrate_user_profile_fields(self, cursor):
        """Add new archer profile fields to existing users table"""
        try:
            # Check if new columns exist, add if they don't
            cursor.execute("PRAGMA table_info(users)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'draw_length' not in columns:
                cursor.execute("ALTER TABLE users ADD COLUMN draw_length REAL DEFAULT 28.0")
                print("✅ Added draw_length column to users table")
                
            if 'skill_level' not in columns:
                cursor.execute("ALTER TABLE users ADD COLUMN skill_level TEXT DEFAULT 'intermediate'")
                print("✅ Added skill_level column to users table")
                
            if 'shooting_style' not in columns:
                cursor.execute("ALTER TABLE users ADD COLUMN shooting_style TEXT DEFAULT 'target'")
                print("✅ Added shooting_style column to users table")
                
            if 'preferred_manufacturers' not in columns:
                cursor.execute("ALTER TABLE users ADD COLUMN preferred_manufacturers TEXT")
                print("✅ Added preferred_manufacturers column to users table")
                
            if 'notes' not in columns:
                cursor.execute("ALTER TABLE users ADD COLUMN notes TEXT")
                print("✅ Added notes column to users table")
                
        except sqlite3.Error as e:
            print(f"⚠️ Warning during migration: {e}")

    def migrate_draw_length_to_users(self):
        """Migration: Move draw_length from bow_setups to users table"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Check if users already have draw_length values
            cursor.execute("SELECT COUNT(*) FROM users WHERE draw_length != 28.0")
            users_with_custom_draw_length = cursor.fetchone()[0]
            
            if users_with_custom_draw_length > 0:
                print("✅ Users already have custom draw_length values, skipping migration")
                return
            
            print("🔄 Migrating draw_length from bow_setups to users...")
            
            # Get all users and their bow setups
            cursor.execute("""
                SELECT u.id as user_id, bs.draw_length, COUNT(*) as setup_count
                FROM users u
                LEFT JOIN bow_setups bs ON u.id = bs.user_id
                WHERE bs.draw_length IS NOT NULL
                GROUP BY u.id, bs.draw_length
                ORDER BY u.id, setup_count DESC
            """)
            
            user_draw_lengths = {}
            for row in cursor.fetchall():
                user_id = row['user_id']
                draw_length = row['draw_length']
                setup_count = row['setup_count']
                
                # Use the most common draw_length for each user
                if user_id not in user_draw_lengths:
                    user_draw_lengths[user_id] = draw_length
            
            # Update users with their most common draw_length
            migration_count = 0
            for user_id, draw_length in user_draw_lengths.items():
                cursor.execute("UPDATE users SET draw_length = ? WHERE id = ?", 
                             (draw_length, user_id))
                migration_count += 1
            
            conn.commit()
            print(f"✅ Migrated draw_length for {migration_count} users")
            
        except sqlite3.Error as e:
            print(f"❌ Error during draw_length migration: {e}")
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
            if user:
                user_dict = dict(user)
                # Parse preferred_manufacturers JSON string back to list
                if user_dict.get('preferred_manufacturers'):
                    try:
                        import json
                        user_dict['preferred_manufacturers'] = json.loads(user_dict['preferred_manufacturers'])
                    except (json.JSONDecodeError, TypeError):
                        user_dict['preferred_manufacturers'] = []
                else:
                    user_dict['preferred_manufacturers'] = []
                return user_dict
            return None
            
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
            if user:
                user_dict = dict(user)
                # Parse preferred_manufacturers JSON string back to list
                if user_dict.get('preferred_manufacturers'):
                    try:
                        import json
                        user_dict['preferred_manufacturers'] = json.loads(user_dict['preferred_manufacturers'])
                    except (json.JSONDecodeError, TypeError):
                        user_dict['preferred_manufacturers'] = []
                else:
                    user_dict['preferred_manufacturers'] = []
                return user_dict
            return None
            
        except sqlite3.Error as e:
            print(f"Error getting user by ID: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def update_user_profile(self, user_id, name=None, profile_picture_url=None, 
                           draw_length=None, skill_level=None, shooting_style=None, 
                           preferred_manufacturers=None, notes=None):
        """Update user profile with archer-specific fields"""
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
                
            if draw_length is not None:
                update_fields.append("draw_length = ?")
                params.append(draw_length)
                
            if skill_level is not None:
                update_fields.append("skill_level = ?")
                params.append(skill_level)
                
            if shooting_style is not None:
                update_fields.append("shooting_style = ?")
                params.append(shooting_style)
                
            if preferred_manufacturers is not None:
                update_fields.append("preferred_manufacturers = ?")
                # Convert list to JSON string for SQLite storage
                if isinstance(preferred_manufacturers, list):
                    import json
                    params.append(json.dumps(preferred_manufacturers))
                else:
                    params.append(preferred_manufacturers)
                
            if notes is not None:
                update_fields.append("notes = ?")
                params.append(notes)
                
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
            user = cursor.fetchone()
            if user:
                user_dict = dict(user)
                # Parse preferred_manufacturers JSON string back to list
                if user_dict.get('preferred_manufacturers'):
                    try:
                        import json
                        user_dict['preferred_manufacturers'] = json.loads(user_dict['preferred_manufacturers'])
                    except (json.JSONDecodeError, TypeError):
                        user_dict['preferred_manufacturers'] = []
                else:
                    user_dict['preferred_manufacturers'] = []
                return user_dict
            return None
            
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
