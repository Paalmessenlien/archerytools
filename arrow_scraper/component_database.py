#!/usr/bin/env python3
"""
Component Database Extension for Arrow Scraper
Handles components (points, nocks, fletchings, inserts) and their compatibility with arrows
"""

import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import threading

class ComponentDatabase:
    """Database extension for managing arrow components and compatibility"""
    
    def __init__(self, db_path: str = "arrow_database.db"):
        self.db_path = Path(db_path)
        self.local = threading.local()
        self.component_types = [
            'points', 'nocks', 'fletchings', 'inserts', 
            'strings', 'rests', 'accessories'
        ]
        self.create_component_tables()
    
    def get_connection(self):
        """Get thread-local database connection"""
        if not hasattr(self.local, 'conn') or self.local.conn is None:
            self.local.conn = sqlite3.connect(
                self.db_path, 
                check_same_thread=False,
                timeout=30.0
            )
            self.local.conn.row_factory = sqlite3.Row
        return self.local.conn
    
    def create_component_tables(self):
        """Create component-related database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if component tables already exist
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='component_categories'
        """)
        if cursor.fetchone():
            print("🗄️  Component tables already exist")
            return
        
        print("🏗️  Creating component database tables...")
        
        # Component Categories table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS component_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            specifications_schema TEXT,  -- JSON schema for this category
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Components table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS components (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            manufacturer TEXT NOT NULL,
            model_name TEXT NOT NULL,
            specifications TEXT,  -- JSON field for type-specific specs
            compatibility_rules TEXT,  -- JSON field for compatibility logic
            image_url TEXT,
            local_image_path TEXT,
            price_range TEXT,
            description TEXT,
            source_url TEXT,
            scraped_at TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES component_categories (id),
            UNIQUE(manufacturer, model_name, category_id)
        )
        ''')
        
        # Arrow-Component Compatibility table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS arrow_component_compatibility (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            arrow_id INTEGER NOT NULL,
            component_id INTEGER NOT NULL,
            compatibility_type TEXT CHECK(compatibility_type IN ('direct', 'universal', 'adapter_required', 'incompatible')),
            compatibility_score REAL DEFAULT 0.0,  -- 0.0 to 1.0
            notes TEXT,
            verified BOOLEAN DEFAULT FALSE,
            verified_by TEXT,  -- User ID who verified
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (arrow_id) REFERENCES arrows (id),
            FOREIGN KEY (component_id) REFERENCES components (id),
            UNIQUE(arrow_id, component_id)
        )
        ''')
        
        # Component compatibility rules table (for automatic matching)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS compatibility_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT NOT NULL,
            rule_name TEXT NOT NULL,
            rule_logic TEXT NOT NULL,  -- JSON field with matching logic
            priority INTEGER DEFAULT 1,
            active BOOLEAN DEFAULT TRUE,
            description TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_components_category ON components (category_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_components_manufacturer ON components (manufacturer)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_compatibility_arrow ON arrow_component_compatibility (arrow_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_compatibility_component ON arrow_component_compatibility (component_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_compatibility_type ON arrow_component_compatibility (compatibility_type)')
        
        # Insert default component categories
        self._insert_default_categories(cursor)
        
        conn.commit()
        print("✅ Component database schema created successfully")
    
    def _insert_default_categories(self, cursor):
        """Insert default component categories with their schemas"""
        
        categories = [
            {
                'name': 'points',
                'description': 'Arrow points including field points, broadheads, and blunts',
                'schema': {
                    'weight': {'type': 'string', 'examples': ['100gr', '125gr', '150gr']},
                    'thread_type': {'type': 'string', 'examples': ['8-32', '5/16-24']},
                    'diameter': {'type': 'float', 'unit': 'inches'},
                    'length': {'type': 'float', 'unit': 'inches'},
                    'material': {'type': 'string', 'examples': ['stainless_steel', 'carbon_steel']},
                    'point_type': {'type': 'string', 'examples': ['field', 'broadhead', 'blunt', 'judo']}
                }
            },
            {
                'name': 'nocks',
                'description': 'Arrow nocks for string attachment',
                'schema': {
                    'nock_size': {'type': 'string', 'examples': ['0.244', '0.246', '0.300']},
                    'fit_type': {'type': 'string', 'examples': ['push_in', 'snap_on', 'pin']},
                    'material': {'type': 'string', 'examples': ['plastic', 'aluminum']},
                    'colors': {'type': 'array', 'examples': [['red', 'yellow', 'green']]},
                    'weight': {'type': 'string', 'examples': ['7gr', '8gr', '9gr']},
                    'throat_size': {'type': 'float', 'unit': 'inches'}
                }
            },
            {
                'name': 'fletchings',
                'description': 'Arrow fletching including vanes and feathers',
                'schema': {
                    'length': {'type': 'float', 'unit': 'inches'},
                    'height': {'type': 'float', 'unit': 'inches'},
                    'material': {'type': 'string', 'examples': ['plastic', 'feather']},
                    'profile': {'type': 'string', 'examples': ['low', 'high', 'parabolic']},
                    'attachment': {'type': 'string', 'examples': ['adhesive', 'wrap']},
                    'colors': {'type': 'array', 'examples': [['white', 'orange', 'yellow']]},
                    'weight': {'type': 'string', 'examples': ['5gr', '7gr', '10gr']}
                }
            },
            {
                'name': 'inserts',
                'description': 'Arrow inserts and outserts for point attachment',
                'schema': {
                    'outer_diameter': {'type': 'float', 'unit': 'inches'},
                    'inner_diameter': {'type': 'float', 'unit': 'inches'},
                    'thread': {'type': 'string', 'examples': ['8-32', '5/16-24']},
                    'length': {'type': 'float', 'unit': 'inches'},
                    'weight': {'type': 'string', 'examples': ['12gr', '15gr', '20gr']},
                    'material': {'type': 'string', 'examples': ['aluminum', 'stainless', 'brass']},
                    'type': {'type': 'string', 'examples': ['insert', 'outsert', 'combo']}
                }
            },
            {
                'name': 'strings',
                'description': 'Bow strings and cables',
                'schema': {
                    'bow_type': {'type': 'string', 'examples': ['recurve', 'compound', 'traditional']},
                    'length': {'type': 'string', 'examples': ['68"', '70"', 'custom']},
                    'strand_count': {'type': 'integer', 'examples': [12, 14, 16]},
                    'material': {'type': 'string', 'examples': ['dacron', 'fastflight', 'dyneema']},
                    'serving': {'type': 'string', 'examples': ['included', 'not_included']}
                }
            },
            {
                'name': 'rests',
                'description': 'Arrow rests and launching systems',
                'schema': {
                    'bow_type': {'type': 'string', 'examples': ['recurve', 'compound']},
                    'rest_type': {'type': 'string', 'examples': ['drop_away', 'whisker_biscuit', 'magnetic']},
                    'adjustment': {'type': 'string', 'examples': ['micro_adjust', 'standard']},
                    'mounting': {'type': 'string', 'examples': ['berger_hole', 'side_mount']}
                }
            },
            {
                'name': 'accessories',
                'description': 'Other archery accessories',
                'schema': {
                    'accessory_type': {'type': 'string', 'examples': ['sight', 'stabilizer', 'quiver', 'release']},
                    'mounting': {'type': 'string', 'examples': ['dovetail', 'screw_on', 'clamp']},
                    'adjustment_range': {'type': 'string', 'examples': ['micro', 'coarse', 'both']}
                }
            }
        ]
        
        for category in categories:
            cursor.execute('''
                INSERT OR IGNORE INTO component_categories (name, description, specifications_schema)
                VALUES (?, ?, ?)
            ''', (category['name'], category['description'], json.dumps(category['schema'])))
    
    def add_component(self, category_name: str, manufacturer: str, model_name: str,
                     specifications: Dict[str, Any], **kwargs) -> Optional[int]:
        """Add a component to the database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get category ID
            cursor.execute('SELECT id FROM component_categories WHERE name = ?', (category_name,))
            category_row = cursor.fetchone()
            if not category_row:
                print(f"❌ Unknown component category: {category_name}")
                return None
            
            category_id = category_row['id']
            
            # Insert component
            cursor.execute('''
                INSERT OR REPLACE INTO components 
                (category_id, manufacturer, model_name, specifications, compatibility_rules,
                 image_url, local_image_path, price_range, description, source_url, scraped_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                category_id,
                manufacturer,
                model_name,
                json.dumps(specifications),
                json.dumps(kwargs.get('compatibility_rules', {})),
                kwargs.get('image_url'),
                kwargs.get('local_image_path'),
                kwargs.get('price_range'),
                kwargs.get('description'),
                kwargs.get('source_url'),
                kwargs.get('scraped_at', datetime.now().isoformat())
            ))
            
            component_id = cursor.lastrowid
            conn.commit()
            
            print(f"✅ Added {category_name}: {manufacturer} {model_name}")
            return component_id
            
        except Exception as e:
            print(f"❌ Error adding component: {e}")
            return None
    
    def get_components(self, category_name: str = None, manufacturer: str = None,
                      limit: int = 50) -> List[Dict[str, Any]]:
        """Get components with optional filtering"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = '''
                SELECT c.*, cc.name as category_name, cc.description as category_description
                FROM components c
                JOIN component_categories cc ON c.category_id = cc.id
                WHERE 1=1
            '''
            params = []
            
            if category_name:
                query += ' AND cc.name = ?'
                params.append(category_name)
            
            if manufacturer:
                query += ' AND c.manufacturer LIKE ?'
                params.append(f'%{manufacturer}%')
            
            query += ' ORDER BY c.manufacturer, c.model_name LIMIT ?'
            params.append(limit)
            
            cursor.execute(query, params)
            components = []
            
            for row in cursor.fetchall():
                component = dict(row)
                # Parse JSON fields
                component['specifications'] = json.loads(component['specifications'] or '{}')
                component['compatibility_rules'] = json.loads(component['compatibility_rules'] or '{}')
                components.append(component)
            
            return components
            
        except Exception as e:
            print(f"❌ Error getting components: {e}")
            return []
    
    def add_compatibility(self, arrow_id: int, component_id: int, 
                         compatibility_type: str, score: float = 0.0,
                         notes: str = None, verified: bool = False) -> bool:
        """Add arrow-component compatibility relationship"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO arrow_component_compatibility
                (arrow_id, component_id, compatibility_type, compatibility_score, notes, verified)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (arrow_id, component_id, compatibility_type, score, notes, verified))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"❌ Error adding compatibility: {e}")
            return False
    
    def get_compatible_components(self, arrow_id: int, 
                                 category_name: str = None) -> List[Dict[str, Any]]:
        """Get components compatible with a specific arrow"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = '''
                SELECT c.*, cc.name as category_name, 
                       acc.compatibility_type, acc.compatibility_score, acc.notes
                FROM components c
                JOIN component_categories cc ON c.category_id = cc.id
                JOIN arrow_component_compatibility acc ON c.id = acc.component_id
                WHERE acc.arrow_id = ? AND acc.compatibility_type != 'incompatible'
            '''
            params = [arrow_id]
            
            if category_name:
                query += ' AND cc.name = ?'
                params.append(category_name)
            
            query += ' ORDER BY acc.compatibility_score DESC, c.manufacturer, c.model_name'
            
            cursor.execute(query, params)
            components = []
            
            for row in cursor.fetchall():
                component = dict(row)
                component['specifications'] = json.loads(component['specifications'] or '{}')
                components.append(component)
            
            return components
            
        except Exception as e:
            print(f"❌ Error getting compatible components: {e}")
            return []
    
    def get_component_statistics(self) -> Dict[str, Any]:
        """Get component database statistics"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Total components by category
            cursor.execute('''
                SELECT cc.name, COUNT(c.id) as count
                FROM component_categories cc
                LEFT JOIN components c ON cc.id = c.category_id
                GROUP BY cc.name
                ORDER BY count DESC
            ''')
            
            categories = []
            total_components = 0
            for row in cursor.fetchall():
                category_data = dict(row)
                categories.append(category_data)
                total_components += category_data['count']
            
            # Compatibility statistics
            cursor.execute('''
                SELECT compatibility_type, COUNT(*) as count
                FROM arrow_component_compatibility
                GROUP BY compatibility_type
            ''')
            
            compatibility_stats = {}
            for row in cursor.fetchall():
                compatibility_stats[row['compatibility_type']] = row['count']
            
            # Manufacturers
            cursor.execute('''
                SELECT manufacturer, COUNT(*) as component_count
                FROM components
                GROUP BY manufacturer
                ORDER BY component_count DESC
            ''')
            
            manufacturers = []
            for row in cursor.fetchall():
                manufacturers.append(dict(row))
            
            return {
                'total_components': total_components,
                'categories': categories,
                'compatibility_stats': compatibility_stats,
                'manufacturers': manufacturers
            }
            
        except Exception as e:
            print(f"❌ Error getting component statistics: {e}")
            return {}

# Example usage and testing
if __name__ == "__main__":
    print("🧪 Testing Component Database System")
    print("=" * 50)
    
    # Initialize database
    db = ComponentDatabase()
    
    # Test adding components
    print("\n📦 Adding test components...")
    
    # Add a point
    point_id = db.add_component(
        'points', 
        'Easton Archery', 
        'Field Point 100gr',
        {
            'weight': '100gr',
            'thread_type': '8-32',
            'diameter': 0.945,
            'length': 2.5,
            'material': 'stainless_steel',
            'point_type': 'field'
        },
        description="Standard field point for target practice",
        price_range="$5-10"
    )
    
    # Add a nock
    nock_id = db.add_component(
        'nocks',
        'Easton Archery',
        'G Nock',
        {
            'nock_size': '0.244',
            'fit_type': 'push_in',
            'material': 'plastic',
            'colors': ['red', 'yellow', 'green'],
            'weight': '7gr',
            'throat_size': 0.088
        },
        description="Standard G nock for carbon arrows",
        price_range="$10-15 per dozen"
    )
    
    # Test compatibility (assuming arrow ID 1 exists)
    if point_id and nock_id:
        db.add_compatibility(1, point_id, 'direct', 0.95, "Standard compatibility")
        db.add_compatibility(1, nock_id, 'direct', 0.90, "Fits standard carbon arrows")
    
    # Get statistics
    stats = db.get_component_statistics()
    print(f"\n📊 Component Statistics:")
    print(f"   Total components: {stats['total_components']}")
    
    for category in stats['categories']:
        print(f"   {category['name']}: {category['count']} components")
    
    print(f"\n🔗 Compatibility relationships: {sum(stats['compatibility_stats'].values())}")
    for comp_type, count in stats['compatibility_stats'].items():
        print(f"   {comp_type}: {count}")
    
    # Test getting components
    points = db.get_components('points')
    print(f"\n🎯 Found {len(points)} points")
    for point in points:
        print(f"   • {point['manufacturer']} {point['model_name']}")
    
    print(f"\n✅ Component database test completed!")