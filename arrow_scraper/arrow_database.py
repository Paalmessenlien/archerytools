#!/usr/bin/env python3
"""
Arrow Database Management System
Consolidates extracted arrow data into a searchable database for Phase 2 tuning engine
"""

import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import re
import threading
try:
    from models import classify_diameter, DiameterCategory
except ImportError:
    # Fallback for Docker environments where models.py dependencies might not be available
    def classify_diameter(inner_diameter, outer_diameter=None):
        """Fallback diameter classification"""
        if inner_diameter and inner_diameter < 0.200:
            return "Ultra-thin"
        elif inner_diameter and inner_diameter < 0.220:
            return "Thin"
        elif inner_diameter and inner_diameter < 0.250:
            return "Small hunting"
        elif inner_diameter and inner_diameter < 0.270:
            return "Standard target"
        elif inner_diameter and inner_diameter < 0.320:
            return "Standard hunting"
        elif inner_diameter and inner_diameter < 0.360:
            return "Large hunting"
        else:
            return "Heavy hunting"
    
    class DiameterCategory:
        """Fallback diameter category"""
        pass

def normalize_material(material: Optional[str], description: Optional[str] = None) -> str:
    """
    Normalize arrow material to one of the four standard types.
    
    Args:
        material: Raw material string from scraper
        description: Arrow description text (optional, for enhanced detection)
        
    Returns:
        Normalized material: "Carbon", "Carbon / Aluminum", "Aluminum", or "Wood"
    """
    # Combine material and description for analysis
    combined_text = ""
    
    if material:
        combined_text += material
    
    if description:
        combined_text += " " + description
    
    if not combined_text.strip():
        return "Carbon"  # Default for null/empty materials
    
    # Convert to lowercase for analysis
    material_lower = combined_text.lower()
    
    # Wood materials (check first - most specific)
    # Use word boundaries and exclude cosmetic descriptions
    
    # First check for carbon/aluminum indicators - if present, not wood
    if any(keyword in material_lower for keyword in ['carbon', 'aluminum', 'alloy', '100% carbon']):
        # Skip wood classification if it's clearly carbon/aluminum
        pass
    else:
        # Check for wood patterns but exclude cosmetic descriptions
        wood_patterns = [
            r'\bwood\b', r'\bcedar\b', r'\bpine\b', r'\boak\b', r'\bash\b', r'\bbirch\b', 
            r'\bhickory\b', r'\bbamboo\b', r'\bdouglas fir\b', r'\bsitka spruce\b', 
            r'\bport orford cedar\b'
        ]
        
        # Exclude cosmetic descriptions
        cosmetic_exclusions = [
            r'bamboo look', r'wood-grained', r'wood grain', r'cedar look', 
            r'wood appearance', r'wooden look', r'wood finish'
        ]
        
        # Check if it matches wood patterns but not cosmetic descriptions
        has_wood_pattern = any(re.search(pattern, material_lower) for pattern in wood_patterns)
        has_cosmetic_exclusion = any(re.search(exclusion, material_lower) for exclusion in cosmetic_exclusions)
        
        if has_wood_pattern and not has_cosmetic_exclusion:
            return "Wood"
    
    # Carbon/Aluminum composites (check before pure carbon)
    carbon_aluminum_keywords = [
        'carbon core with 7075 alloy jacket',
        'carbon-core with 7075-alloy metal jacket', 
        'carbon core with aluminum jacket',
        'carbon with aluminum jacket',
        'carbon fiber bonded to a 7075 alloy core',
        'carbon fiber bonded to a precision 7075 alloy core',
        'carbon and 7075 aluminum composited',
        'carbon and aluminum',
        'carbon fiber on a precision, thin-wall aluminum core',  # Easton X10 pattern
        'carbon fiber on aluminum core',  # Variations of the X10 pattern
        'carbon fiber on a aluminum core',
        'carbon on aluminum core',
        'carbon fiber with aluminum core',
        'fmj construction',  # FMJ typically means carbon core with aluminum jacket
        'fmj'
    ]
    
    if any(keyword in material_lower for keyword in carbon_aluminum_keywords):
        return "Carbon / Aluminum"
    
    # Pure Aluminum materials  
    aluminum_keywords = ['aluminum', 'aluminium', 'alloy', 'enaw', '7075', '7001']
    
    # Check if it's pure aluminum (has aluminum keywords but no carbon keywords)
    has_aluminum = any(keyword in material_lower for keyword in aluminum_keywords)
    has_carbon = any(keyword in material_lower for keyword in ['carbon', 'carb'])
    
    if has_aluminum and not has_carbon:
        return "Aluminum"
    
    # Carbon materials (default for most arrows)
    # Most modern arrows are carbon unless specifically mentioned otherwise
    return "Carbon"

class ArrowDatabase:
    """Database for managing extracted arrow specifications"""
    
    def __init__(self, db_path: str = "arrow_database.db"):
        self.db_path = Path(db_path)
        self.local = threading.local()  # Thread-local storage for connections
        self.create_database()
    
    def get_connection(self):
        """Get thread-local database connection"""
        if not hasattr(self.local, 'conn') or self.local.conn is None:
            self.local.conn = sqlite3.connect(
                self.db_path, 
                check_same_thread=False,  # Allow connection sharing across threads
                timeout=30.0  # 30 second timeout for database locks
            )
            self.local.conn.row_factory = sqlite3.Row  # Enable column access by name
        return self.local.conn
    
    def _format_spine_display(self, arrow_data: Dict[str, Any]) -> str:
        """Format spine display for different arrow types"""
        min_spine = arrow_data.get('min_spine')
        max_spine = arrow_data.get('max_spine')
        material = arrow_data.get('material') or ''
        material = material.lower()
        
        if not min_spine or not max_spine:
            return 'N/A'
        
        # Wood arrows use traditional spine format (40-45#)
        if 'wood' in material:
            if min_spine == max_spine:
                return f"{min_spine}#"
            else:
                return f"{min_spine}-{max_spine}#"
        else:
            # Carbon and aluminum arrows use carbon spine numbers
            if min_spine == max_spine:
                return str(min_spine)
            else:
                return f"{min_spine}-{max_spine}"
        
    def create_database(self):
        """Create database tables if they don't exist"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if database already has data (from Docker build)
        try:
            cursor.execute("SELECT COUNT(*) FROM arrows")
            arrow_count = cursor.fetchone()[0]
            if arrow_count > 0:
                print(f"🗄️  Database already initialized with {arrow_count} arrows")
                # Also check for user tables
                try:
                    cursor.execute("SELECT COUNT(*) FROM users")
                    return # Assume all tables are created
                except sqlite3.OperationalError:
                    pass # users table doesn't exist, so create it
        except sqlite3.OperationalError:
            # Table doesn't exist, create it
            pass
        
        print("🏗️  Creating database tables...")
        
        # Arrows table - main arrow information
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS arrows (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            manufacturer TEXT NOT NULL,
            model_name TEXT NOT NULL,
            material TEXT,
            carbon_content TEXT,
            arrow_type TEXT,  -- target, hunting, etc.
            description TEXT,
            image_url TEXT,
            source_url TEXT,
            scraped_at TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(manufacturer, model_name)
        )
        ''')
        
        # Spine specifications table - detailed spine data
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS spine_specifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            arrow_id INTEGER NOT NULL,
            spine INTEGER NOT NULL,
            outer_diameter REAL,
            gpi_weight REAL NOT NULL,
            inner_diameter REAL,
            diameter_category TEXT,  -- Categorized diameter classification
            length_options TEXT,  -- JSON array of available lengths
            wall_thickness REAL,
            insert_weight_range TEXT,
            nock_size TEXT,
            notes TEXT,
            straightness_tolerance TEXT,
            weight_tolerance TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (arrow_id) REFERENCES arrows (id),
            UNIQUE(arrow_id, spine)
        )
        ''')

        # Users table - for user accounts
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            google_id TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            name TEXT,
            profile_picture_url TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Bow setups table - for user-saved bow configurations
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS bow_setups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            bow_type TEXT NOT NULL,
            draw_weight REAL NOT NULL,
            draw_length REAL NOT NULL,
            arrow_length REAL NOT NULL,
            point_weight REAL NOT NULL,
            nock_weight REAL,
            fletching_weight REAL,
            insert_weight REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        # Create indexes for performance (only if we're creating the schema)
        try:
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_arrows_manufacturer ON arrows (manufacturer)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_arrows_type ON arrows (arrow_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_spine_spine ON spine_specifications (spine)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_spine_gpi ON spine_specifications (gpi_weight)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_spine_diameter ON spine_specifications (outer_diameter)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_spine_diameter_category ON spine_specifications (diameter_category)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_google_id ON users (google_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_bow_setups_user_id ON bow_setups (user_id)')
            conn.commit()
            print("✅ Database schema created successfully")
        except sqlite3.OperationalError as e:
            print(f"⚠️  Could not create indexes (database may be read-only): {e}")
            # Don't fail if we can't create indexes on an existing database
        print(f"✅ Database initialized: {self.db_path}")
    
    def load_from_json_files(self, data_dir: str = "data/processed"):
        """Load arrow data from extracted JSON files with validation and duplicate checking"""
        data_dir = Path(data_dir)
        
        if not data_dir.exists():
            print(f"❌ Data directory not found: {data_dir}")
            return 0, 0
        
        total_arrows = 0
        total_specs = 0
        skipped_arrows = 0
        updated_arrows = 0
        
        print(f"🔄 Loading arrow data from {data_dir}")
        
        # Sort files to process in consistent order
        json_files = sorted(data_dir.glob("*.json"))
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Skip files with no arrows or invalid structure
                if not data.get('arrows'):
                    print(f"  ⏭️  Skipping {json_file.name}: No arrows found")
                    continue
                
                if data.get('total_arrows', 0) == 0:
                    print(f"  ⏭️  Skipping {json_file.name}: Empty file")
                    continue
                
                arrows_added, specs_added = self._process_json_data(data)
                total_arrows += arrows_added
                total_specs += specs_added
                
                if arrows_added > 0:
                    print(f"  ✅ {json_file.name}: {arrows_added} arrows, {specs_added} specs")
                else:
                    print(f"  ⚠️  {json_file.name}: No valid arrows to import")
                
            except json.JSONDecodeError as e:
                print(f"  ❌ Invalid JSON in {json_file.name}: {e}")
                continue
            except Exception as e:
                print(f"  ❌ Error processing {json_file.name}: {e}")
                continue
        
        print(f"🎯 Database sync complete:")
        print(f"   📊 Total arrows: {total_arrows}")
        print(f"   🎯 Spine specifications: {total_specs}")
        
        return total_arrows, total_specs
    
    def _process_json_data(self, data: Dict[str, Any]) -> Tuple[int, int]:
        """Process a single JSON extraction file"""
        arrows_added = 0
        specs_added = 0
        
        manufacturer = data.get('manufacturer', 'Unknown')
        
        for arrow_data in data.get('arrows', []):
            arrow_id = self._add_arrow(arrow_data, manufacturer)
            
            if arrow_id:
                arrows_added += 1
                
                # Add spine specifications
                for spec in arrow_data.get('spine_specifications', []):
                    if self._add_spine_specification(arrow_id, spec):
                        specs_added += 1
        
        return arrows_added, specs_added
    
    def _validate_arrow_data(self, arrow_data: Dict[str, Any]) -> bool:
        """Validate arrow data before importing"""
        # Required fields
        if not arrow_data.get('model_name'):
            return False
            
        # Model name should not be generic/unknown
        model_name = arrow_data.get('model_name', '').lower()
        invalid_names = ['unknown model', 'unknown', 'n/a', 'none', '']
        if model_name in invalid_names:
            return False
            
        # Should have at least some spine specifications or basic data
        has_specs = bool(arrow_data.get('spine_specifications'))
        has_basic_data = bool(arrow_data.get('description') or arrow_data.get('material'))
        
        return has_specs or has_basic_data
    
    def _add_arrow(self, arrow_data: Dict[str, Any], manufacturer: str) -> Optional[int]:
        """Add an arrow to the database with validation and duplicate checking"""
        try:
            # Validate arrow data first
            if not self._validate_arrow_data(arrow_data):
                print(f"  ⚠️  Skipping invalid arrow: {arrow_data.get('model_name', 'Unknown')}")
                return None
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Handle manufacturer field (some data has both in arrow_data and passed parameter)
            arrow_manufacturer = arrow_data.get('manufacturer', manufacturer)
            if arrow_manufacturer != manufacturer:
                arrow_manufacturer = manufacturer  # Use the file-level manufacturer as authoritative
            
            model_name = arrow_data.get('model_name', 'Unknown Model')
            
            # Check if arrow already exists (improved duplicate detection)
            cursor.execute('''
                SELECT id, material, description FROM arrows 
                WHERE manufacturer = ? AND model_name = ?
            ''', (arrow_manufacturer, model_name))
            
            existing = cursor.fetchone()
            
            if existing:
                # Arrow exists - check if we should update it
                existing_id = existing['id']
                existing_material = existing['material']
                existing_description = existing['description']
                
                # Calculate new material classification
                new_material = normalize_material(arrow_data.get('material'), arrow_data.get('description'))
                
                # Update if material classification would change or description is better
                should_update = False
                new_description = arrow_data.get('description')
                
                if existing_material != new_material:
                    should_update = True
                    print(f"  🔄 Updating material: {arrow_manufacturer} {model_name} ({existing_material} → {new_material})")
                
                if new_description and len(new_description) > len(existing_description or ''):
                    should_update = True
                    print(f"  📝 Updating description: {arrow_manufacturer} {model_name}")
                
                if should_update:
                    cursor.execute('''
                        UPDATE arrows SET 
                            material = ?, 
                            carbon_content = ?, 
                            arrow_type = ?, 
                            description = ?, 
                            image_url = ?
                        WHERE id = ?
                    ''', (
                        new_material,
                        arrow_data.get('carbon_content'),
                        arrow_data.get('arrow_type'),
                        new_description or existing_description,
                        arrow_data.get('image_url'),
                        existing_id
                    ))
                    conn.commit()
                
                return existing_id
            else:
                # Insert new arrow
                cursor.execute('''
                INSERT INTO arrows 
                (manufacturer, model_name, material, carbon_content, arrow_type, 
                 description, image_url)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    arrow_manufacturer,
                    model_name,
                    normalize_material(arrow_data.get('material'), arrow_data.get('description')),
                    arrow_data.get('carbon_content'),
                    arrow_data.get('arrow_type'),
                    arrow_data.get('description'),
                    arrow_data.get('image_url')
                ))
                
                arrow_id = cursor.lastrowid
                conn.commit()
                return arrow_id
                
        except Exception as e:
            print(f"Error adding arrow: {e}")
            return None
    
    def _add_spine_specification(self, arrow_id: int, spec_data: Dict[str, Any]) -> bool:
        """Add a spine specification to the database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Convert length_options to JSON string
            length_options = spec_data.get('length_options', [])
            if length_options:
                length_options_json = json.dumps(length_options)
            else:
                length_options_json = None
            
            # Calculate diameter category
            diameter_category = None
            if spec_data.get('outer_diameter'):
                # Use inner diameter if available, otherwise outer diameter
                effective_diameter = spec_data.get('inner_diameter') or spec_data.get('outer_diameter')
                diameter_result = classify_diameter(effective_diameter)
                # Handle both enum and string returns
                diameter_category = getattr(diameter_result, 'value', diameter_result)
            
            cursor.execute('''
            INSERT OR IGNORE INTO spine_specifications
            (arrow_id, spine, outer_diameter, gpi_weight, inner_diameter,
             length_options, wall_thickness, insert_weight_range, nock_size, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                arrow_id,
                spec_data.get('spine'),
                spec_data.get('outer_diameter'),
                spec_data.get('gpi_weight'),
                spec_data.get('inner_diameter'),
                length_options_json,
                spec_data.get('wall_thickness'),
                spec_data.get('insert_weight_range'),
                spec_data.get('nock_size'),
                spec_data.get('notes')
            ))
            
            if cursor.rowcount > 0:
                conn.commit()
                return True
            return False
            
        except Exception as e:
            print(f"Error adding spine specification: {e}")
            return False
    
    def get_arrows_by_manufacturer(self, manufacturer: str) -> List[Dict[str, Any]]:
        """Get all arrows from a specific manufacturer"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT a.id, a.manufacturer, a.model_name, a.material, a.arrow_type, 
                       a.description, a.image_url
                FROM arrows a
                WHERE LOWER(a.manufacturer) LIKE ?
            ''', (f'%{manufacturer.lower()}%',))
            
            rows = cursor.fetchall()
            arrows = []
            for row in rows:
                arrows.append({
                    'id': row['id'],
                    'manufacturer': row['manufacturer'],
                    'model_name': row['model_name'],
                    'material': row['material'],
                    'arrow_type': row['arrow_type'],
                    'description': row['description'],
                    'image_url': row['image_url']
                })
            
            return arrows
            
        except Exception as e:
            print(f"Error getting arrows by manufacturer: {e}")
            return []

    def search_arrows(self, manufacturer: str = None, arrow_type: str = None, 
                     material: str = None, spine_min: int = None, spine_max: int = None,
                     gpi_min: float = None, gpi_max: float = None,
                     diameter_min: float = None, diameter_max: float = None,
                     diameter_category: str = None, model_search: str = None, 
                     limit: int = 50) -> List[Dict[str, Any]]:
        """Search for arrows based on criteria"""
        
        query = '''
        SELECT DISTINCT 
            a.id, a.manufacturer, a.model_name, a.material, a.arrow_type, 
            a.description, a.image_url,
            COUNT(s.id) as spine_count,
            MIN(s.spine) as min_spine, MAX(s.spine) as max_spine,
            MIN(s.gpi_weight) as min_gpi, MAX(s.gpi_weight) as max_gpi,
            MIN(s.outer_diameter) as min_diameter, MAX(s.outer_diameter) as max_diameter
        FROM arrows a
        LEFT JOIN spine_specifications s ON a.id = s.arrow_id
        WHERE 1=1
        '''
        
        params = []
        
        if manufacturer:
            query += ' AND a.manufacturer LIKE ?'
            params.append(f'%{manufacturer}%')
            
        if arrow_type:
            query += ' AND a.arrow_type = ?'
            params.append(arrow_type)
            
        if material:
            # For broad categories like "Wood", match any material containing that term
            if material in ['Wood', 'Carbon', 'Aluminum']:
                query += ' AND a.material LIKE ?'
                params.append(f'%{material}%')
            else:
                # For specific materials, use exact match
                query += ' AND a.material = ?'
                params.append(material)
            
        if model_search:
            query += ' AND a.model_name LIKE ?'
            params.append(f'%{model_search}%')
        
        # Add spine/gpi/diameter filters
        if any([spine_min, spine_max, gpi_min, gpi_max, diameter_min, diameter_max, diameter_category]):
            query += ''' AND a.id IN (
                SELECT DISTINCT arrow_id FROM spine_specifications 
                WHERE 1=1
            '''
            
            if spine_min:
                query += ' AND spine >= ?'
                params.append(spine_min)
            if spine_max:
                query += ' AND spine <= ?'
                params.append(spine_max)
            if gpi_min:
                query += ' AND gpi_weight >= ?'
                params.append(gpi_min)
            if gpi_max:
                query += ' AND gpi_weight <= ?'
                params.append(gpi_max)
            if diameter_min:
                query += ' AND outer_diameter >= ?'
                params.append(diameter_min)
            if diameter_max:
                query += ' AND outer_diameter <= ?'
                params.append(diameter_max)
            if diameter_category:
                query += ' AND diameter_category = ?'
                params.append(diameter_category)
                
            query += ')'
        
        query += '''
        GROUP BY a.id
        ORDER BY a.manufacturer, a.model_name
        LIMIT ?
        '''
        params.append(limit)
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(query, params)
        
        results = []
        rows = cursor.fetchall()
        
        for row in rows:
            result = dict(row)
            # Add formatted spine display for wood arrows
            result['spine_display'] = self._format_spine_display(result)
            results.append(result)
        
        return results
    
    def get_arrow_details(self, arrow_id: int) -> Optional[Dict[str, Any]]:
        """Get complete arrow details including all spine specifications"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get arrow info
        cursor.execute('SELECT * FROM arrows WHERE id = ?', (arrow_id,))
        arrow = cursor.fetchone()
        
        if not arrow:
            return None
        
        # Get spine specifications
        cursor.execute('''
        SELECT * FROM spine_specifications 
        WHERE arrow_id = ? 
        ORDER BY spine
        ''', (arrow_id,))
        
        spine_specs = []
        for spec_row in cursor.fetchall():
            spec = dict(spec_row)
            # Parse length_options back from JSON
            if spec['length_options']:
                try:
                    spec['length_options'] = json.loads(spec['length_options'])
                except:
                    spec['length_options'] = []
            else:
                spec['length_options'] = []
            spine_specs.append(spec)
        
        result = dict(arrow)
        result['spine_specifications'] = spine_specs
        
        return result
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total counts
        cursor.execute('SELECT COUNT(*) as count FROM arrows')
        arrow_count = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM spine_specifications')
        spec_count = cursor.fetchone()['count']
        
        # Manufacturer breakdown
        cursor.execute('''
        SELECT manufacturer, COUNT(*) as arrow_count,
               SUM((SELECT COUNT(*) FROM spine_specifications WHERE arrow_id = arrows.id)) as spec_count
        FROM arrows 
        GROUP BY manufacturer 
        ORDER BY arrow_count DESC
        ''')
        
        manufacturers = []
        for row in cursor.fetchall():
            manufacturers.append(dict(row))
        
        # Spine range
        cursor.execute('SELECT MIN(spine) as min_spine, MAX(spine) as max_spine FROM spine_specifications')
        spine_range = cursor.fetchone()
        
        # GPI range
        cursor.execute('SELECT MIN(gpi_weight) as min_gpi, MAX(gpi_weight) as max_gpi FROM spine_specifications WHERE gpi_weight IS NOT NULL')
        gpi_range = cursor.fetchone()
        
        # Diameter range
        cursor.execute('SELECT MIN(outer_diameter) as min_diameter, MAX(outer_diameter) as max_diameter FROM spine_specifications WHERE outer_diameter IS NOT NULL')
        diameter_range = cursor.fetchone()
        
        # Diameter category distribution (if column exists)
        diameter_categories = []
        try:
            cursor.execute('''
            SELECT diameter_category, COUNT(*) as count 
            FROM spine_specifications 
            WHERE diameter_category IS NOT NULL 
            GROUP BY diameter_category 
            ORDER BY count DESC
            ''')
            for row in cursor.fetchall():
                diameter_categories.append(dict(row))
        except sqlite3.OperationalError:
            # diameter_category column doesn't exist in this database
            pass
        
        return {
            'total_arrows': arrow_count,
            'total_specifications': spec_count,
            'total_manufacturers': len(manufacturers),
            'manufacturers': manufacturers,
            'spine_range': dict(spine_range) if spine_range else {},
            'gpi_range': dict(gpi_range) if gpi_range else {},
            'diameter_range': dict(diameter_range) if diameter_range else {},
            'diameter_categories': diameter_categories
        }
    
    def close(self):
        """Close database connection"""
        if hasattr(self.local, 'conn') and self.local.conn:
            self.local.conn.close()
            self.local.conn = None
            
    def __del__(self):
        """Cleanup on deletion"""
        self.close()


# Example usage and testing
if __name__ == "__main__":
    print("🚀 Arrow Database System")
    print("=" * 50)
    
    # Initialize database
    db = ArrowDatabase()
    
    # Load data from JSON files
    db.load_from_json_files()
    
    # Show statistics
    stats = db.get_statistics()
    print(f"\n📊 DATABASE STATISTICS:")
    print(f"   Total arrows: {stats['total_arrows']}")
    print(f"   Total specifications: {stats['total_specifications']}")
    
    print(f"\n🏭 MANUFACTURERS:")
    if stats.get('manufacturers') and len(stats['manufacturers']) > 0:
        for mfr in stats['manufacturers']:
            print(f"   {mfr['manufacturer']}: {mfr['arrow_count']} arrows, {mfr['spec_count']} specs")
    else:
        print("   No manufacturers found - database appears to be empty")
    
    if stats.get('spine_range') and stats['spine_range']['min_spine'] is not None and stats['spine_range']['max_spine'] is not None:
        print(f"\n🎯 SPINE RANGE: {stats['spine_range']['min_spine']} - {stats['spine_range']['max_spine']}")
    else:
        print(f"\n🎯 SPINE RANGE: No spine data available")
    
    if stats.get('gpi_range') and stats['gpi_range']['min_gpi'] is not None and stats['gpi_range']['max_gpi'] is not None:
        print(f"⚖️  GPI RANGE: {stats['gpi_range']['min_gpi']:.1f} - {stats['gpi_range']['max_gpi']:.1f}")
    else:
        print(f"⚖️  GPI RANGE: No GPI data available")
    
    # Test search
    print(f"\n🔍 SEARCH TEST - Target arrows:")
    results = db.search_arrows(arrow_type="target", limit=5)
    if results and len(results) > 0:
        for arrow in results:
            print(f"   {arrow['manufacturer']} {arrow['model_name']}: {arrow['spine_count']} spine options")
    else:
        print("   No target arrows found")
    
    print(f"\n🔍 SEARCH TEST - Spine 300-400:")
    results = db.search_arrows(spine_min=300, spine_max=400, limit=5)
    if results and len(results) > 0:
        for arrow in results:
            print(f"   {arrow['manufacturer']} {arrow['model_name']}: spine {arrow['min_spine']}-{arrow['max_spine']}")
    else:
        print("   No arrows found in spine range 300-400")