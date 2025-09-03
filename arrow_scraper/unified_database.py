#!/usr/bin/env python3
"""
Unified Database Class
Provides access to both arrow and user data in a single database
Replaces the dual database architecture with unified approach
"""

import sqlite3
import os
from pathlib import Path
from typing import Optional, Dict, Any, List

class UnifiedDatabase:
    """
    Unified database class that combines arrow and user data functionality
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize unified database connection
        
        Args:
            db_path: Path to unified database file (defaults to arrow_database.db)
        """
        self.db_path = self._resolve_database_path(db_path or "arrow_database.db")
        print(f"🎯 Unified database initialized: {self.db_path}")
        
    def _resolve_database_path(self, db_path: str) -> str:
        """Resolve database path with environment awareness"""
        # Check for environment variable first (Docker deployment)
        env_db_path = os.environ.get('ARROW_DATABASE_PATH')
        if env_db_path:
            print(f"🔧 Using ARROW_DATABASE_PATH environment variable: {env_db_path}")
            return env_db_path
            
        # If absolute path provided, use it directly
        if Path(db_path).is_absolute():
            return db_path
        
        # Try unified database paths
        possible_paths = [
            Path("/app/databases") / db_path,  # Docker unified path
            Path(__file__).parent / "databases" / db_path,  # Local development
            Path("/app") / db_path,  # Legacy Docker path
            Path(__file__).parent / db_path,  # Legacy local path
        ]
        
        for path in possible_paths:
            try:
                if path.exists():
                    print(f"Found existing database at: {path}")
                    return str(path)
                # Try to create directory if it doesn't exist
                path.parent.mkdir(parents=True, exist_ok=True)
                return str(path)
            except PermissionError:
                continue
        
        # Fallback
        return str(Path(__file__).parent / db_path)
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    # User-related methods (migrated from UserDatabase)
    
    def create_user(self, google_id: str, email: str, name: str = None, 
                   profile_picture_url: str = None) -> Dict[str, Any]:
        """Create a new user and return user dict (backwards compatible)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if status column exists (backwards compatibility)
            cursor.execute('PRAGMA table_info(users)')
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'status' in columns:
                # New schema with status column
                cursor.execute('''
                    INSERT INTO users (google_id, email, name, profile_picture_url, status)
                    VALUES (?, ?, ?, ?, ?)
                ''', (google_id, email, name, profile_picture_url, 'active'))
            else:
                # Legacy schema without status column
                cursor.execute('''
                    INSERT INTO users (google_id, email, name, profile_picture_url)
                    VALUES (?, ?, ?, ?)
                ''', (google_id, email, name, profile_picture_url))
            
            user_id = cursor.lastrowid
            
            # Return the created user
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            user_dict = dict(row) if row else None
            
            # Add status field if it doesn't exist in database
            if user_dict and 'status' not in user_dict:
                user_dict['status'] = 'active'  # Default for backwards compatibility
                
            return user_dict
    
    def get_user_by_google_id(self, google_id: str) -> Optional[Dict[str, Any]]:
        """Get user by Google ID (backwards compatible)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE google_id = ?', (google_id,))
            row = cursor.fetchone()
            if row:
                user_dict = dict(row)
                # Add status field if it doesn't exist in database (backwards compatibility)
                if 'status' not in user_dict:
                    user_dict['status'] = 'active'  # Default for existing users
                return user_dict
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def update_user(self, user_id: int, **kwargs) -> bool:
        """Update user information"""
        if not kwargs:
            return False
            
        set_clause = ', '.join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values()) + [user_id]
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'UPDATE users SET {set_clause} WHERE id = ?', values)
            return cursor.rowcount > 0
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID (backwards compatible)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            if row:
                user_dict = dict(row)
                # Add status field if it doesn't exist in database (backwards compatibility)
                if 'status' not in user_dict:
                    user_dict['status'] = 'active'  # Default for existing users
                return user_dict
            return None
    
    def set_admin_status(self, user_id: int, is_admin: bool = True) -> bool:
        """Set user admin status"""
        return self.update_user(user_id, is_admin=is_admin)
    
    def set_user_admin(self, user_id: int, is_admin: bool = True) -> bool:
        """Set user admin status (alias for backwards compatibility)"""
        return self.set_admin_status(user_id, is_admin)
    
    def update_user_status(self, user_id: int, status: str) -> bool:
        """Update user status (active, pending, suspended) - backwards compatible"""
        try:
            return self.update_user(user_id, status=status)
        except Exception as e:
            # If status column doesn't exist, just return True (backwards compatibility)
            if "no such column" in str(e).lower() and "status" in str(e).lower():
                print(f"⚠️ Status column doesn't exist, ignoring status update: {e}")
                return True
            else:
                raise e
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users ORDER BY created_at DESC')
            return [dict(row) for row in cursor.fetchall()]
    
    # Bow setup methods
    
    def create_bow_setup(self, user_id: int, **setup_data) -> int:
        """Create a new bow setup"""
        required_fields = ['name', 'bow_type', 'draw_weight']
        for field in required_fields:
            if field not in setup_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Add user_id to setup data
        setup_data['user_id'] = user_id
        
        columns = ', '.join(setup_data.keys())
        placeholders = ', '.join(['?' for _ in setup_data])
        values = list(setup_data.values())
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                INSERT INTO bow_setups ({columns})
                VALUES ({placeholders})
            ''', values)
            return cursor.lastrowid
    
    def get_user_bow_setups(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all bow setups for a user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM bow_setups WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_bow_setup(self, setup_id: int) -> Optional[Dict[str, Any]]:
        """Get bow setup by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM bow_setups WHERE id = ?', (setup_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def update_bow_setup(self, setup_id: int, **kwargs) -> bool:
        """Update bow setup"""
        if not kwargs:
            return False
            
        set_clause = ', '.join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values()) + [setup_id]
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'UPDATE bow_setups SET {set_clause} WHERE id = ?', values)
            return cursor.rowcount > 0
    
    def delete_bow_setup(self, setup_id: int) -> bool:
        """Delete bow setup (cascades to related records)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM bow_setups WHERE id = ?', (setup_id,))
            return cursor.rowcount > 0
    
    # Arrow methods (enhanced to work with unified database)
    
    def search_arrows(self, manufacturer: str = None, arrow_type: str = None, 
                     material: str = None, spine_min: int = None, spine_max: int = None,
                     gpi_min: float = None, gpi_max: float = None,
                     diameter_min: float = None, diameter_max: float = None,
                     diameter_category: str = None, model_search: str = None,
                     limit: int = 50, include_inactive: bool = False) -> List[Dict[str, Any]]:
        """Search arrows with enhanced filtering and manufacturer active status filtering"""
        conditions = []
        params = []
        
        # Always filter by active manufacturers unless explicitly requested otherwise (admin)
        if not include_inactive:
            conditions.append("m.is_active = TRUE")
        
        if manufacturer:
            conditions.append("a.manufacturer LIKE ?")
            params.append(f"%{manufacturer}%")
            
        if arrow_type:
            conditions.append("a.arrow_type = ?")
            params.append(arrow_type)
            
        if material:
            conditions.append("a.material = ?")
            params.append(material)
            
        if model_search:
            conditions.append("(a.model_name LIKE ? OR a.description LIKE ?)")
            params.extend([f"%{model_search}%", f"%{model_search}%"])
        
        if spine_min:
            conditions.append("ss.spine >= ?")
            params.append(spine_min)
            
        if spine_max:
            conditions.append("ss.spine <= ?")
            params.append(spine_max)
            
        if gpi_min:
            conditions.append("ss.gpi_weight >= ?")
            params.append(gpi_min)
            
        if gpi_max:
            conditions.append("ss.gpi_weight <= ?")
            params.append(gpi_max)
            
        if diameter_min:
            conditions.append("ss.outer_diameter >= ?")
            params.append(diameter_min)
            
        if diameter_max:
            conditions.append("ss.outer_diameter <= ?")
            params.append(diameter_max)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if manufacturers table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='manufacturers';")
            has_manufacturers_table = cursor.fetchone() is not None
            
            if has_manufacturers_table:
                # Use manufacturer active status filtering when table exists
                query = f'''
                    SELECT DISTINCT a.*, ss.spine, ss.outer_diameter, ss.gpi_weight, m.is_active as manufacturer_active
                    FROM arrows a
                    JOIN manufacturers m ON a.manufacturer = m.name
                    LEFT JOIN spine_specifications ss ON a.id = ss.arrow_id
                    WHERE {where_clause}
                    ORDER BY a.manufacturer, a.model_name, ss.spine
                    LIMIT ?
                '''
            else:
                # Fallback: search without manufacturer filtering, treat all as active
                # Remove manufacturer active status conditions if manufacturers table doesn't exist
                fallback_conditions = [c for c in conditions if not c.startswith("m.is_active")]
                fallback_params = []
                param_index = 0
                
                for condition in conditions:
                    if not condition.startswith("m.is_active"):
                        # Count placeholders in this condition
                        placeholders = condition.count('?')
                        fallback_params.extend(params[param_index:param_index + placeholders])
                    param_index += condition.count('?')
                    
                fallback_where_clause = " AND ".join(fallback_conditions) if fallback_conditions else "1=1"
                
                query = f'''
                    SELECT DISTINCT a.*, ss.spine, ss.outer_diameter, ss.gpi_weight, 1 as manufacturer_active
                    FROM arrows a
                    LEFT JOIN spine_specifications ss ON a.id = ss.arrow_id
                    WHERE {fallback_where_clause}
                    ORDER BY a.manufacturer, a.model_name, ss.spine
                    LIMIT ?
                '''
                params = fallback_params
            
            cursor.execute(query, params + [limit])
            return [dict(row) for row in cursor.fetchall()]
    
    def get_arrow_by_id(self, arrow_id: int, include_inactive: bool = False) -> Optional[Dict[str, Any]]:
        """Get arrow with spine specifications, filtering by manufacturer active status"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if manufacturers table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='manufacturers';")
            has_manufacturers_table = cursor.fetchone() is not None
            
            if has_manufacturers_table:
                # Build WHERE clause based on active status filtering
                where_conditions = ["a.id = ?"]
                params = [arrow_id]
                
                if not include_inactive:
                    where_conditions.append("m.is_active = TRUE")
                
                where_clause = " AND ".join(where_conditions)
                
                cursor.execute(f'''
                    SELECT a.*, m.is_active as manufacturer_active,
                           GROUP_CONCAT(ss.spine) as spines,
                           GROUP_CONCAT(ss.outer_diameter) as diameters,
                           GROUP_CONCAT(ss.gpi_weight) as gpi_weights
                    FROM arrows a
                    JOIN manufacturers m ON a.manufacturer = m.name
                    LEFT JOIN spine_specifications ss ON a.id = ss.arrow_id
                    WHERE {where_clause}
                    GROUP BY a.id
                ''', params)
            else:
                # Fallback: get arrow without manufacturer filtering
                cursor.execute('''
                    SELECT a.*, 1 as manufacturer_active,
                           GROUP_CONCAT(ss.spine) as spines,
                           GROUP_CONCAT(ss.outer_diameter) as diameters,
                           GROUP_CONCAT(ss.gpi_weight) as gpi_weights
                    FROM arrows a
                    LEFT JOIN spine_specifications ss ON a.id = ss.arrow_id
                    WHERE a.id = ?
                    GROUP BY a.id
                ''', [arrow_id])
                
            row = cursor.fetchone()
            return dict(row) if row else None
    
    # Setup arrows methods
    
    def add_arrow_to_setup(self, setup_id: int, arrow_id: int, arrow_length: float,
                          point_weight: float, **kwargs) -> int:
        """Add arrow to bow setup"""
        arrow_data = {
            'setup_id': setup_id,
            'arrow_id': arrow_id,
            'arrow_length': arrow_length,
            'point_weight': point_weight,
            **kwargs
        }
        
        columns = ', '.join(arrow_data.keys())
        placeholders = ', '.join(['?' for _ in arrow_data])
        values = list(arrow_data.values())
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                INSERT INTO setup_arrows ({columns})
                VALUES ({placeholders})
            ''', values)
            return cursor.lastrowid
    
    def get_setup_arrows(self, setup_id: int) -> List[Dict[str, Any]]:
        """Get all arrows for a bow setup with full arrow details (includes inactive manufacturers for existing setups)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT sa.*, a.manufacturer, a.model_name, a.material,
                       ss.spine, ss.outer_diameter, ss.gpi_weight, m.is_active as manufacturer_active
                FROM setup_arrows sa
                JOIN arrows a ON sa.arrow_id = a.id
                LEFT JOIN manufacturers m ON a.manufacturer = m.name
                LEFT JOIN spine_specifications ss ON a.id = ss.arrow_id 
                    AND ss.spine = sa.calculated_spine
                WHERE sa.setup_id = ?
                ORDER BY sa.created_at DESC
            ''', (setup_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    # Guide session methods
    
    def create_guide_session(self, user_id: int, guide_name: str, guide_type: str,
                           bow_setup_id: int = None, total_steps: int = None) -> int:
        """Create new guide session"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO guide_sessions 
                (user_id, bow_setup_id, guide_name, guide_type, total_steps)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, bow_setup_id, guide_name, guide_type, total_steps))
            return cursor.lastrowid
    
    def get_user_guide_sessions(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all guide sessions for user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT gs.*, bs.name as bow_setup_name
                FROM guide_sessions gs
                LEFT JOIN bow_setups bs ON gs.bow_setup_id = bs.id
                WHERE gs.user_id = ?
                ORDER BY gs.started_at DESC
            ''', (user_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    # Database statistics
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get comprehensive database statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Arrow statistics
            cursor.execute('SELECT COUNT(*) FROM arrows')
            stats['total_arrows'] = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(DISTINCT manufacturer) FROM arrows')
            stats['total_manufacturers'] = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM spine_specifications')
            stats['total_spine_specs'] = cursor.fetchone()[0]
            
            # User statistics
            cursor.execute('SELECT COUNT(*) FROM users')
            stats['total_users'] = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM bow_setups')
            stats['total_bow_setups'] = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM setup_arrows')
            stats['total_setup_arrows'] = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM guide_sessions')
            stats['total_guide_sessions'] = cursor.fetchone()[0]
            
            return stats
    
    def close(self):
        """Close database connection (for compatibility)"""
        # Connection is handled by context manager, no action needed
        pass