#!/usr/bin/env python3
"""
API-Only Flask Backend for Arrow Tuning System
Provides RESTful API endpoints for the Nuxt 3 frontend
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
import sqlite3
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

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional
import uuid

# Import our arrow tuning system components
from arrow_tuning_system import ArrowTuningSystem, ArcherProfile, TuningSession
from spine_calculator import BowConfiguration, BowType
from tuning_calculator import TuningGoal, ArrowType
from arrow_database import ArrowDatabase
from component_database import ComponentDatabase
from spine_service import UnifiedSpineService
from compatibility_engine import CompatibilityEngine

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'arrow-tuning-secret-key-change-in-production')

# Enable CORS in Flask (nginx CORS disabled to prevent duplicates)
CORS(app, 
     origins=[
         "http://localhost:3000",  # Nuxt dev server
         "http://localhost:3001",  # Nuxt dev server alternate port
         "http://localhost",       # Nginx proxy
         "http://localhost:80",    # Nginx proxy with port
         "https://archerytool.online", # Production domain
         "https://www.archerytool.online", # Production domain with www
     ], 
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'], 
     allow_headers=['Content-Type', 'Authorization'],
     supports_credentials=True)

# Global variables for lazy initialization
tuning_system = None
database = None
component_database = None
spine_service = None
compatibility_engine = None

# In-memory session storage (use Redis in production)
tuning_sessions = {}

def get_tuning_system():
    """Get tuning system with lazy initialization"""
    global tuning_system
    if tuning_system is None:
        try:
            # Get the database path from the database function to ensure consistency
            db = get_database()
            if db is None:
                return None
            
            # Use the same path the database is using
            db_path = db.db_path if hasattr(db, 'db_path') else 'arrow_database.db'
            tuning_system = ArrowTuningSystem(database_path=db_path)
        except Exception as e:
            import traceback
            tuning_system = None
    return tuning_system

def get_database():
    """Get database with unified path resolution"""
    global database
    if database is None:
        try:
            # Use ArrowDatabase's built-in unified path resolution
            database = ArrowDatabase()
            
        except Exception as e:
            import traceback
            print(f"Error creating ArrowDatabase: {e}")
            traceback.print_exc()
            database = None
    return database

def get_arrow_db():
    """Get arrow database connection with fallback locations - sync with ArrowDatabase class"""
    try:
        # UNIFIED DATABASE PATH RESOLUTION - NEW ARCHITECTURE (August 2025)
        db_paths = [
            '/app/databases/arrow_database.db',                    # 🔴 UNIFIED Docker path (HIGHEST PRIORITY)
            'databases/arrow_database.db',                         # 🔴 LOCAL subfolder (DEVELOPMENT - HIGHEST LOCAL PRIORITY)
            '../databases/arrow_database.db',                      # 🟡 UNIFIED parent folder path 
            '/app/arrow_data/arrow_database.db',                   # 🟡 Legacy Docker volume path
            '/app/arrow_database.db',                              # 🟡 Legacy Docker path
            'arrow_database.db',                                   # 🔴 Legacy current folder (LOWEST PRIORITY)
        ]
        
        database_path = None
        for db_path in db_paths:
            if os.path.exists(db_path):
                try:
                    # Quick check if database has data
                    import sqlite3
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM arrows")
                    count = cursor.fetchone()[0]
                    conn.close()
                    
                    if count > 0:
                        database_path = db_path
                        print(f"[get_arrow_db] Selected database: {db_path} with {count} arrows")  # Debug log
                        break
                except Exception as e:
                    continue
        
        if not database_path:
            return None
        
        # Return connection to the found database with row factory
        import sqlite3
        conn = sqlite3.connect(database_path)
        conn.row_factory = sqlite3.Row
        return conn
        
    except Exception as e:
        import traceback
        return None

def get_component_database():
    """Get component database with lazy initialization"""
    global component_database
    if component_database is None:
        try:
            # Use same database path as main database
            db = get_database()
            if db is None:
                return None
            
            db_path = db.db_path if hasattr(db, 'db_path') else 'arrow_database.db'
            component_database = ComponentDatabase(db_path)
        except Exception as e:
            import traceback
            component_database = None
    return component_database

def get_spine_service():
    """Get spine service with lazy initialization"""
    global spine_service
    if spine_service is None:
        try:
            spine_service = UnifiedSpineService()
        except Exception as e:
            print(f"Error initializing spine service: {e}")
            spine_service = None
    return spine_service

def get_compatibility_engine():
    """Get compatibility engine with lazy initialization"""
    global compatibility_engine
    if compatibility_engine is None:
        try:
            # Use same database path as main database
            db = get_database()
            if db is None:
                return None
            
            db_path = db.db_path if hasattr(db, 'db_path') else 'arrow_database.db'
            compatibility_engine = CompatibilityEngine(db_path)
        except Exception as e:
            import traceback
            compatibility_engine = None
    return compatibility_engine

# Error handler
@app.errorhandler(Exception)
def handle_error(error):
    """Global error handler"""
    import traceback
    # If it's a 404, return 404 status code
    if hasattr(error, 'code') and error.code == 404:
        return jsonify({
            'error': str(error),
            'type': type(error).__name__
        }), 404
    return jsonify({
        'error': str(error),
        'type': type(error).__name__
    }), 500

# Root endpoint
@app.route('/', methods=['GET'])
def root():
    """Root endpoint - redirect to health check"""
    return jsonify({
        'message': 'ArrowTuner API Server',
        'version': '1.0.0',
        'status': 'running',
        'environment_debug': {
            'env_file_loaded': 'Path loaded successfully' if 'Path' in globals() else 'Path not loaded',
            'secret_key_set': bool(os.environ.get('SECRET_KEY')),
            'google_client_set': bool(os.environ.get('NUXT_PUBLIC_GOOGLE_CLIENT_ID')),
        },
        'endpoints': {
            'health': '/api/health',
            'arrows': '/api/arrows',
            'manufacturers': '/api/manufacturers',
            'tuning': '/api/tuning/*'
        }
    })

# Simple health check that doesn't require database
@app.route('/api/simple-health', methods=['GET'])
def simple_health():
    """Simple health check without database dependency"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'version': '1.0.0',
        'test_message': 'BACKUP ENDPOINTS TEST - API FILE UPDATED',
        'environment_vars': {
            'SECRET_KEY': 'set' if os.environ.get('SECRET_KEY') else 'missing',
            'GOOGLE_CLIENT_ID': 'set' if os.environ.get('NUXT_PUBLIC_GOOGLE_CLIENT_ID') else 'missing',
            'GOOGLE_CLIENT_SECRET': 'set' if os.environ.get('GOOGLE_CLIENT_SECRET') else 'missing',
        }
    })

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """System health check"""
    try:
        # Test database connection with lazy initialization
        db = get_database()
        if db:
            stats = db.get_statistics()
            db_status = "healthy" if stats else "error"
            db_stats = {
                'total_arrows': stats.get('total_arrows', 0),
                'total_manufacturers': stats.get('total_manufacturers', 0)
            }
        else:
            db_status = "error"
            db_stats = {'total_arrows': 0, 'total_manufacturers': 0}
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'database_status': db_status,
            'database_stats': db_stats
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Database Stats API
@app.route('/api/database/stats', methods=['GET'])
def get_database_stats():
    """Get database statistics"""
    try:
        db = get_database()
        if not db:
            return jsonify({'error': 'Database not available'}), 500
            
        stats = db.get_statistics()
        
        return jsonify({
            'total_arrows': stats.get('total_arrows', 0),
            'total_manufacturers': len(stats.get('manufacturers', [])),
            'manufacturers': stats.get('manufacturers', []),
            'spine_range': {
                'min': stats.get('spine_range', {}).get('min_spine', 0),
                'max': stats.get('spine_range', {}).get('max_spine', 0)
            },
            'diameter_range': {
                'min': stats.get('diameter_range', {}).get('min_diameter', 0.0),
                'max': stats.get('diameter_range', {}).get('max_diameter', 0.0)
            },
            'gpi_range': {
                'min': stats.get('gpi_range', {}).get('min_gpi', 0.0),
                'max': stats.get('gpi_range', {}).get('max_gpi', 0.0)
            },
            'diameter_categories': stats.get('diameter_categories', [])
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Arrow Database API
@app.route('/api/arrows', methods=['GET'])
def get_arrows():
    """Get arrows with optional filtering"""
    try:
        # Get query parameters
        manufacturer = request.args.get('manufacturer')
        arrow_type = request.args.get('arrow_type')
        material = request.args.get('material')
        spine_min = request.args.get('spine_min', type=int)
        spine_max = request.args.get('spine_max', type=int)
        gpi_min = request.args.get('gpi_min', type=float)
        gpi_max = request.args.get('gpi_max', type=float)
        diameter_min = request.args.get('diameter_min', type=float)
        diameter_max = request.args.get('diameter_max', type=float)
        search_query = request.args.get('search')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Search arrows using database
        db = get_database()
        if not db:
            return jsonify({'error': 'Database not available'}), 500
            
        arrows = db.search_arrows(
            manufacturer=manufacturer,
            arrow_type=arrow_type,
            material=material,
            spine_min=spine_min,
            spine_max=spine_max,
            gpi_min=gpi_min,
            gpi_max=gpi_max,
            diameter_min=diameter_min,
            diameter_max=diameter_max,
            model_search=search_query,
            limit=per_page * 10  # Get more for pagination
        )
        
        # Enhance arrows with proper image URLs
        for arrow in arrows:
            arrow['primary_image_url'] = get_image_url(
                arrow_id=arrow['id'],
                image_url=arrow.get('image_url'),
                saved_images=arrow.get('saved_images'),
                local_image_path=arrow.get('local_image_path')
            )
        
        # Pagination
        total_arrows = len(arrows)
        total_pages = (total_arrows + per_page - 1) // per_page
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_arrows = arrows[start_idx:end_idx]
        
        return jsonify({
            'arrows': paginated_arrows,
            'total': total_arrows,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'has_prev': page > 1,
            'has_next': page < total_pages
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/arrows/<int:arrow_id>', methods=['GET'])
def get_arrow_details(arrow_id):
    """Get detailed information about a specific arrow"""
    try:
        # Add logging for debugging
        print(f"API: Requesting arrow details for ID {arrow_id}")
        
        db = get_database()
        if not db:
            print(f"API: Database not available for arrow {arrow_id}")
            return jsonify({'error': 'Database not available'}), 500
        
        print(f"API: Database available, calling get_arrow_details({arrow_id})")
        arrow_details = db.get_arrow_details(arrow_id)
        print(f"API: get_arrow_details returned: {type(arrow_details)} - {arrow_details is not None}")
        
        if not arrow_details:
            print(f"API: Arrow {arrow_id} not found, returning 404")
            return jsonify({'error': f'Arrow {arrow_id} not found'}), 404
        
        print(f"API: Arrow {arrow_id} found, enhancing with image URL")
        # Enhance with proper image URL
        try:
            arrow_details['primary_image_url'] = get_image_url(
                arrow_id=arrow_details['id'],
                image_url=arrow_details.get('image_url'),
                saved_images=arrow_details.get('saved_images'),
                local_image_path=arrow_details.get('local_image_path')
            )
            print(f"API: Image URL enhancement successful for arrow {arrow_id}")
        except Exception as img_error:
            print(f"API: Image URL enhancement failed for arrow {arrow_id}: {img_error}")
            # Continue without image URL rather than failing
            arrow_details['primary_image_url'] = None
        
        print(f"API: Returning arrow details for {arrow_id}")
        return jsonify(arrow_details)
        
    except Exception as e:
        print(f"API: Exception in get_arrow_details({arrow_id}): {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

# Manufacturers API
@app.route('/api/manufacturers', methods=['GET'])
def get_manufacturers():
    """Get list of all manufacturers with arrow counts"""
    try:
        db = get_database()
        if not db:
            return jsonify({'error': 'Database not available'}), 500
            
        stats = db.get_statistics()
        manufacturers = stats.get('manufacturers', [])
        
        # Return manufacturer data
        return jsonify(manufacturers)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Bow Equipment Manufacturers API
@app.route('/api/bow-equipment/manufacturers', methods=['GET'])
def get_bow_equipment_manufacturers():
    """Get manufacturers organized by bow equipment categories"""
    try:
        db = get_database()
        if not db:
            return jsonify({'error': 'Database not available'}), 500
        
        # Get category filter from query params
        category_filter = request.args.get('category')
        
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Define bow and equipment categories
        bow_categories = ['compound_bows', 'recurve_risers', 'recurve_limbs', 'traditional_risers', 'traditional_limbs', 'longbows']
        equipment_categories = ['strings', 'sights', 'stabilizers', 'arrow_rests', 'weights']
        all_categories = bow_categories + equipment_categories
        
        # Get manufacturers with equipment categories
        if category_filter:
            cursor.execute('''
                SELECT m.name, mec.category_name
                FROM manufacturers m
                JOIN manufacturer_equipment_categories mec ON m.id = mec.manufacturer_id
                WHERE mec.is_supported = 1 
                AND mec.category_name = ?
                ORDER BY m.name
            ''', (category_filter,))
        else:
            cursor.execute('''
                SELECT m.name, mec.category_name
                FROM manufacturers m
                JOIN manufacturer_equipment_categories mec ON m.id = mec.manufacturer_id
                WHERE mec.is_supported = 1 
                AND mec.category_name IN ({})
                ORDER BY m.name, mec.category_name
            '''.format(','.join(['?' for _ in all_categories])), all_categories)
        
        # Organize by category
        manufacturers_by_category = {}
        
        for row in cursor.fetchall():
            manufacturer_name = row['name']
            category_name = row['category_name']
            
            if category_name not in manufacturers_by_category:
                manufacturers_by_category[category_name] = []
            
            if manufacturer_name not in manufacturers_by_category[category_name]:
                manufacturers_by_category[category_name].append(manufacturer_name)
        
        # If specific category requested, return just that list
        if category_filter:
            return jsonify({
                'category': category_filter,
                'manufacturers': manufacturers_by_category.get(category_filter, [])
            })
        
        # Return all categories
        return jsonify({
            'categories': manufacturers_by_category
        })
        
    except Exception as e:
        print(f"Error getting bow equipment manufacturers: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/materials', methods=['GET'])
def get_materials():
    """Get list of all materials with arrow counts"""
    try:
        db = get_database()
        if not db:
            return jsonify({'error': 'Database not available'}), 500
            
        # Get materials directly from database
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT material, COUNT(*) as count 
            FROM arrows 
            WHERE material IS NOT NULL 
            GROUP BY material 
            ORDER BY material
        ''')
        
        materials = []
        for row in cursor.fetchall():
            materials.append({
                'material': row['material'],
                'count': row['count']
            })
        
        return jsonify(materials)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/materials/grouped', methods=['GET'])
def get_grouped_materials():
    """Get list of grouped material categories with arrow counts"""
    try:
        db = get_database()
        if not db:
            return jsonify({'error': 'Database not available'}), 500
            
        # Get materials directly from database
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT material, COUNT(*) as count 
            FROM arrows 
            WHERE material IS NOT NULL 
            GROUP BY material 
            ORDER BY material
        ''')
        
        # Group materials into categories
        material_groups = {
            'Carbon': 0,
            'Carbon / Aluminum': 0,
            'Aluminum': 0,
            'Wood': 0
        }
        
        for row in cursor.fetchall():
            material = row['material'].lower()
            count = row['count']
            
            # Categorize materials
            if 'wood' in material or 'cedar' in material or 'pine' in material or 'bamboo' in material:
                material_groups['Wood'] += count
            elif 'carbon' in material and 'aluminum' in material:
                material_groups['Carbon / Aluminum'] += count
            elif 'carbon' in material:
                material_groups['Carbon'] += count
            elif 'aluminum' in material or 'alloy' in material:
                material_groups['Aluminum'] += count
        
        # Convert to list format
        grouped_materials = []
        for material, count in material_groups.items():
            if count > 0:  # Only include categories with arrows
                grouped_materials.append({
                    'material': material,
                    'count': count
                })
        
        return jsonify(grouped_materials)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/arrow-types', methods=['GET'])
def get_arrow_types():
    """Get list of all arrow types with arrow counts"""
    try:
        db = get_database()
        if not db:
            return jsonify({'error': 'Database not available'}), 500
            
        # Get arrow types directly from database
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT arrow_type, COUNT(*) as count 
            FROM arrows 
            WHERE arrow_type IS NOT NULL 
            GROUP BY arrow_type 
            ORDER BY arrow_type
        ''')
        
        arrow_types = []
        for row in cursor.fetchall():
            arrow_types.append({
                'arrow_type': row['arrow_type'],
                'count': row['count']
            })
        
        return jsonify(arrow_types)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def calculate_simple_spine(draw_weight, arrow_length, point_weight, bow_type):
    """Simple spine calculation fallback when tuning system is unavailable"""
    # Basic spine calculation based on draw weight and arrow length
    base_spine = draw_weight * 12.5
    
    # Adjust for arrow length (longer = weaker/higher spine number)
    length_adjustment = (arrow_length - 28) * 25
    base_spine += length_adjustment
    
    # Adjust for point weight (heavier = weaker/higher spine number)
    point_adjustment = (point_weight - 125) * 0.5
    base_spine += point_adjustment
    
    # Bow type adjustments
    if bow_type == 'recurve':
        base_spine += 50  # Recurve typically needs weaker arrows
    elif bow_type == 'traditional':
        base_spine += 100  # Traditional bows need even weaker arrows
    
    calculated_spine = round(base_spine)
    
    # Create spine range (±25 spine)
    return {
        'calculated_spine': calculated_spine,
        'spine_range': {
            'minimum': calculated_spine - 25,
            'optimal': calculated_spine,
            'maximum': calculated_spine + 25
        },
        'adjustments': {
            'length_adjustment': length_adjustment,
            'point_weight_adjustment': point_adjustment,
            'bow_type': bow_type
        },
        'base_spine': base_spine - length_adjustment - point_adjustment,
        'total_adjustment': length_adjustment + point_adjustment,
        'bow_type': bow_type,
        'confidence': 'medium',
        'notes': ['Calculated using simplified spine formula']
    }

# Tuning Calculation API
@app.route('/api/tuning/calculate-spine', methods=['POST'])
def calculate_spine():
    """Calculate recommended spine for given bow configuration - UNIFIED VERSION"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        print(f"Received spine calculation request: {data}")  # Debug logging
        
        # Use the unified spine calculation service
        from spine_service import calculate_unified_spine
        
        spine_result = calculate_unified_spine(
            draw_weight=float(data.get('draw_weight', 45)),
            arrow_length=data.get('arrow_length', 29.0),
            point_weight=data.get('point_weight', 125.0),
            bow_type=data.get('bow_type', 'compound'),
            nock_weight=data.get('nock_weight', 10.0),
            fletching_weight=data.get('fletching_weight', 15.0),
            material_preference=data.get('arrow_material')
        )
        
        return jsonify({
            'recommended_spine': spine_result['calculated_spine'],
            'spine_range': {
                'min': spine_result['spine_range']['minimum'],
                'max': spine_result['spine_range']['maximum'],
                'optimal': spine_result['spine_range']['optimal']
            },
            'calculations': spine_result['calculations'],
            'notes': spine_result.get('notes', []),
            'source': spine_result.get('source', 'unified_service')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tuning/recommendations', methods=['POST'])
def get_arrow_recommendations():
    """Get arrow recommendations for given bow configuration"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Create bow configuration
        try:
            # Map longbow to traditional for backend compatibility
            bow_type_str = data['bow_type']
            if bow_type_str == 'longbow':
                bow_type_str = 'traditional'
            
            bow_config = BowConfiguration(
                draw_weight=float(data['draw_weight']),
                draw_length=float(data['draw_length']),
                bow_type=BowType(bow_type_str),
                cam_type=data.get('cam_type', 'medium'),
                arrow_rest_type=data.get('arrow_rest_type', 'drop_away')
            )
        except Exception as e:
            return jsonify({'error': f'Invalid bow configuration: {str(e)}'}), 400
        
        # Create archer profile
        try:
            archer_profile = ArcherProfile(
                name=data.get('archer_name', 'Anonymous'),
                bow_config=bow_config,
                shooting_style=data.get('shooting_style', 'target'),
                experience_level=data.get('experience_level', 'intermediate'),
                arrow_length=float(data.get('arrow_length', 29.0)),
                point_weight_preference=float(data.get('point_weight', 100.0)),
                preferred_manufacturers=data.get('preferred_manufacturers', [])
            )
        except Exception as e:
            return jsonify({'error': f'Invalid archer profile: {str(e)}'}), 400
        
        # Get tuning goals
        try:
            primary_goal = TuningGoal(data.get('primary_goal', 'maximum_accuracy'))
        except Exception as e:
            return jsonify({'error': f'Invalid tuning goal: {str(e)}'}), 400
        
        # Get recommendations from tuning system
        ts = get_tuning_system()
        if not ts:
            return jsonify({'error': 'Tuning system not available'}), 500
        
        try:
            # Normalize material preference to proper case for database matching
            material_pref = data.get('arrow_material')
            if material_pref:
                material_pref = material_pref.capitalize()  # "wood" -> "Wood", "Wood" -> "Wood"
            
            session = ts.create_tuning_session(
                archer_profile, 
                tuning_goals=[primary_goal],
                material_preference=material_pref
            )
        except Exception as e:
            return jsonify({'error': f'Failed to create tuning session: {str(e)}'}), 500
        
        # Get limit from request data, default to 20, max 300
        limit = min(int(data.get('limit', 20)), 300)
        recommendations = session.recommended_arrows[:limit]
        
        # Convert recommendations to API format
        api_recommendations = []
        try:
            for rec in recommendations:
                # Get spine specifications for min/max calculation
                spine_specs = getattr(rec, 'spine_specifications', [])
                spine_values = [spec['spine'] for spec in spine_specs if spec.get('spine') is not None]
                min_spine = min(spine_values) if spine_values else None
                max_spine = max(spine_values) if spine_values else None
                
                # Get GPI weight range for filtering/sorting
                gpi_values = [spec['gpi_weight'] for spec in spine_specs if spec.get('gpi_weight') is not None and spec['gpi_weight'] > 0]
                min_gpi = min(gpi_values) if gpi_values else None
                max_gpi = max(gpi_values) if gpi_values else None
                
                # Get diameter ranges for filtering/sorting
                inner_diameter_values = [spec.get('inner_diameter') for spec in spine_specs if spec.get('inner_diameter') is not None and spec.get('inner_diameter') > 0]
                outer_diameter_values = [spec.get('outer_diameter') for spec in spine_specs if spec.get('outer_diameter') is not None and spec.get('outer_diameter') > 0]
                
                min_inner_diameter = min(inner_diameter_values) if inner_diameter_values else None
                max_inner_diameter = max(inner_diameter_values) if inner_diameter_values else None
                min_outer_diameter = min(outer_diameter_values) if outer_diameter_values else None
                max_outer_diameter = max(outer_diameter_values) if outer_diameter_values else None
                
                # Safely access attributes with error handling
                rec_data = {
                    'arrow': {
                        'id': getattr(rec, 'arrow_id', None),
                        'manufacturer': getattr(rec, 'manufacturer', 'Unknown'),
                        'model_name': getattr(rec, 'model_name', 'Unknown Model'),
                        'spine_specifications': spine_specs,
                        'material': getattr(rec, 'material', None),
                        'arrow_type': getattr(rec, 'arrow_type', None),
                        'description': getattr(rec, 'description', None),
                        'price_range': getattr(rec, 'price_range', None),
                        # Show exact matched values instead of ranges
                        'matched_spine': getattr(rec, 'matched_spine', None),
                        'matched_gpi': getattr(rec, 'gpi_weight', None),
                        'matched_outer_diameter': getattr(rec, 'outer_diameter', None),
                        'matched_inner_diameter': getattr(rec, 'inner_diameter', None),
                        # Keep ranges for reference but prioritize matched values
                        'min_spine': min_spine,
                        'max_spine': max_spine,
                        'min_gpi': min_gpi,
                        'max_gpi': max_gpi,
                        'min_inner_diameter': min_inner_diameter,
                        'max_inner_diameter': max_inner_diameter,
                        'min_outer_diameter': min_outer_diameter,
                        'max_outer_diameter': max_outer_diameter,
                        # Add cascading image URL
                        'primary_image_url': get_image_url(
                            arrow_id=getattr(rec, 'arrow_id', None),
                            image_url=getattr(rec, 'image_url', None),
                            saved_images=getattr(rec, 'saved_images', None),
                            local_image_path=getattr(rec, 'local_image_path', None)
                        )
                    },
                    'spine_specification': {
                        'spine': getattr(rec, 'matched_spine', None),
                        'outer_diameter': getattr(rec, 'outer_diameter', None),
                        'inner_diameter': getattr(rec, 'inner_diameter', None),
                        'gpi_weight': getattr(rec, 'gpi_weight', None)
                    },
                    'compatibility_score': getattr(rec, 'match_score', 0),
                    'compatibility_rating': getattr(rec, 'confidence_level', 'unknown'),
                    'match_percentage': int(getattr(rec, 'match_score', 0)),
                    'reasons': getattr(rec, 'match_reasons', []),
                    'potential_issues': getattr(rec, 'potential_issues', [])
                }
                api_recommendations.append(rec_data)
        except Exception as e:
            return jsonify({'error': f'Failed to format recommendations: {str(e)}'}), 500
        
        return jsonify({
            'recommended_arrows': api_recommendations,
            'total_compatible': len(api_recommendations),
            'bow_config': data,
            'recommended_spine': getattr(session, 'recommended_spine', 'N/A'),
            'session_id': session.session_id
        })
        
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

# Tuning Sessions API
@app.route('/api/tuning/sessions', methods=['POST'])
def create_tuning_session():
    """Create a new tuning session"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        session_id = str(uuid.uuid4())
        session_data = {
            'id': session_id,
            'archer_name': data.get('archer_name', 'Anonymous'),
            'bow_config': data.get('bow_config', {}),
            'recommended_spine': data.get('recommended_spine'),
            'recommended_arrows': data.get('recommended_arrows', []),
            'created_at': datetime.now().isoformat(),
            'notes': data.get('notes', '')
        }
        
        # Store session (in production, use a proper database)
        tuning_sessions[session_id] = session_data
        
        return jsonify(session_data), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# User Authentication API
import jwt
from auth import token_required, get_user_from_google_token

@app.route('/api/auth/google', methods=['POST'])
def google_auth():
    data = request.get_json()
    token = data.get('token')

    if not token:
        return jsonify({'error': 'No token provided'}), 400

    user, needs_profile_completion = get_user_from_google_token(token)

    if not user:
        return jsonify({'error': 'Invalid token or user not found'}), 401

    # Create JWT
    jwt_token = jwt.encode({
        'user_id': user['id'],
        'needs_profile_completion': needs_profile_completion,
        'exp': datetime.now(timezone.utc) + timedelta(hours=24)
    }, app.config['SECRET_KEY'], algorithm='HS256')

    return jsonify({'token': jwt_token, 'needs_profile_completion': needs_profile_completion})

@app.route('/api/user', methods=['GET'])
@token_required
def get_user(current_user):
    """Get current authenticated user's details including archer profile"""
    # Convert SQLite Row object to dictionary for JSON serialization
    user_dict = dict(current_user)
    
    # Convert preferred_manufacturers JSON string to list if it exists
    if user_dict.get('preferred_manufacturers'):
        try:
            user_dict['preferred_manufacturers'] = json.loads(user_dict['preferred_manufacturers'])
        except (json.JSONDecodeError, TypeError):
            user_dict['preferred_manufacturers'] = []
    else:
        user_dict['preferred_manufacturers'] = []
    
    # Convert shooting_style JSON string to list if it exists
    if user_dict.get('shooting_style'):
        try:
            if user_dict['shooting_style'].startswith('['):
                user_dict['shooting_style'] = json.loads(user_dict['shooting_style'])
            else:
                # Legacy single value, convert to array
                user_dict['shooting_style'] = [user_dict['shooting_style']]
        except (json.JSONDecodeError, TypeError):
            user_dict['shooting_style'] = ['target']
    else:
        user_dict['shooting_style'] = ['target']
    
    return jsonify(user_dict)

@app.route('/api/user/profile', methods=['PUT'])
@token_required
def update_user_profile(current_user):
    """Update current authenticated user's profile details including archer-specific fields"""
    from user_database import UserDatabase
    user_db = UserDatabase()
    data = request.get_json()
    
    # Extract all possible fields from request
    name = data.get('name')
    draw_length = data.get('draw_length')
    skill_level = data.get('skill_level')
    shooting_style = data.get('shooting_style')
    preferred_manufacturers = data.get('preferred_manufacturers')
    notes = data.get('notes')
    
    # Validate fields
    if skill_level and skill_level not in ['beginner', 'intermediate', 'advanced']:
        return jsonify({'error': 'Invalid skill level. Must be beginner, intermediate, or advanced'}), 400
    
    # Validate shooting styles (can be array or single value)
    valid_styles = ['target', 'hunting', 'traditional', '3d']
    if shooting_style:
        if isinstance(shooting_style, list):
            # Multiple shooting styles
            for style in shooting_style:
                if style not in valid_styles:
                    return jsonify({'error': f'Invalid shooting style: {style}. Must be one of: {", ".join(valid_styles)}'}), 400
            # Convert to JSON string for storage
            shooting_style = json.dumps(shooting_style)
        elif isinstance(shooting_style, str):
            # Single shooting style - check if it's already JSON
            if shooting_style.startswith('['):
                # Already JSON, validate the parsed content
                try:
                    parsed_styles = json.loads(shooting_style)
                    for style in parsed_styles:
                        if style not in valid_styles:
                            return jsonify({'error': f'Invalid shooting style: {style}. Must be one of: {", ".join(valid_styles)}'}), 400
                except:
                    return jsonify({'error': 'Invalid shooting style format'}), 400
            else:
                # Single value, validate and convert to array
                if shooting_style not in valid_styles:
                    return jsonify({'error': f'Invalid shooting style: {shooting_style}. Must be one of: {", ".join(valid_styles)}'}), 400
                shooting_style = json.dumps([shooting_style])
        else:
            return jsonify({'error': 'Shooting style must be a string or array'}), 400
    
    if draw_length and (draw_length < 20 or draw_length > 36):
        return jsonify({'error': 'Draw length must be between 20 and 36 inches'}), 400
    
    # Convert preferred_manufacturers list to JSON string if provided
    if preferred_manufacturers and isinstance(preferred_manufacturers, list):
        preferred_manufacturers = json.dumps(preferred_manufacturers)
    
    try:
        updated_user = user_db.update_user_profile(
            current_user['id'], 
            name=name,
            draw_length=draw_length,
            skill_level=skill_level,
            shooting_style=shooting_style,
            preferred_manufacturers=preferred_manufacturers,
            notes=notes
        )
        
        if updated_user:
            # Convert preferred_manufacturers back to list for frontend
            user_dict = dict(updated_user)
            if user_dict.get('preferred_manufacturers'):
                try:
                    user_dict['preferred_manufacturers'] = json.loads(user_dict['preferred_manufacturers'])
                except (json.JSONDecodeError, TypeError):
                    user_dict['preferred_manufacturers'] = []
            else:
                user_dict['preferred_manufacturers'] = []
            
            return jsonify(user_dict)
        else:
            return jsonify({'error': 'Failed to update user profile'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Bow Setups API
@app.route('/api/bow-setups', methods=['GET'])
@token_required
def get_bow_setups(current_user):
    """Get all bow setups for the current user"""
    from user_database import UserDatabase
    user_db = UserDatabase()
    conn = user_db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bow_setups WHERE user_id = ?", (current_user['id'],))
    setups = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in setups])

@app.route('/api/bow-setups/<int:setup_id>', methods=['GET'])
@token_required
def get_bow_setup(current_user, setup_id):
    """Get a specific bow setup with its details"""
    from user_database import UserDatabase
    user_db = UserDatabase()
    conn = user_db.get_connection()
    cursor = conn.cursor()
    
    try:
        # Get the bow setup and verify ownership
        cursor.execute("SELECT * FROM bow_setups WHERE id = ? AND user_id = ?", (setup_id, current_user['id']))
        setup = cursor.fetchone()
        
        if not setup:
            return jsonify({'error': 'Bow setup not found or access denied'}), 404
        
        return jsonify(dict(setup))
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/bow-setups', methods=['POST'])
@token_required
def create_bow_setup(current_user):
    """Create a new bow setup"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    try:
        # Use the UserDatabase class method for creating bow setups
        from user_database import UserDatabase
        user_db = UserDatabase()
        new_setup = user_db.create_bow_setup(current_user['id'], data)
        
        if not new_setup:
            return jsonify({'error': 'Failed to create bow setup'}), 500
        
        return jsonify(new_setup), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bow-setups/<int:setup_id>', methods=['PUT'])
@token_required
def update_bow_setup(current_user, setup_id):
    """Update a bow setup with change logging"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    try:
        from user_database import UserDatabase
        from change_log_service import ChangeLogService
        
        user_db = UserDatabase()
        change_service = ChangeLogService()
        conn = user_db.get_connection()
        cursor = conn.cursor()
        
        # Get current setup data for change tracking
        cursor.execute("SELECT * FROM bow_setups WHERE id = ? AND user_id = ?", (setup_id, current_user['id']))
        current_setup = cursor.fetchone()
        
        if not current_setup:
            conn.close()
            return jsonify({'error': 'Setup not found or you do not have permission to edit it'}), 404
        
        # Extract user_note from data for change logging
        user_note = data.pop('user_note', None)
        
        # Update the setup using the existing method
        updated_setup = user_db.update_bow_setup(current_user['id'], setup_id, data)
        
        if not updated_setup:
            conn.close()
            return jsonify({'error': 'Failed to update setup'}), 500
        
        # Log the setup changes
        changes_logged = []
        trackable_fields = {
            'name': 'Setup name',
            'bow_type': 'Bow type', 
            'draw_weight': 'Draw weight',
            'bow_usage': 'Bow usage',
            'ibo_speed': 'IBO speed',
            'insert_weight': 'Insert weight',
            'compound_brand': 'Compound brand',
            'compound_model': 'Compound model',
            'riser_brand': 'Riser brand',
            'riser_model': 'Riser model',
            'riser_length': 'Riser length',
            'limb_brand': 'Limb brand',
            'limb_model': 'Limb model', 
            'limb_length': 'Limb length',
            'limb_fitting': 'Limb fitting',
            'construction': 'Construction',
            'bow_brand': 'Bow brand',
            'description': 'Description'
        }
        
        # Track individual field changes
        for field_key, field_name in trackable_fields.items():
            if field_key in data:
                old_value = str(current_setup[field_key] or '') if current_setup[field_key] is not None else ''
                new_value = str(data[field_key] or '') if data[field_key] is not None else ''
                
                if old_value != new_value:
                    change_service.log_setup_change(
                        bow_setup_id=setup_id,
                        user_id=current_user['id'],
                        change_type='setup_modified',
                        field_name=field_key,
                        old_value=old_value,
                        new_value=new_value,
                        change_description=f"{field_name} changed from '{old_value}' to '{new_value}'"
                    )
                    changes_logged.append(field_name)
        
        # Log overall setup update with user note
        if user_note or changes_logged:
            overall_description = user_note or f"Setup configuration updated ({', '.join(changes_logged)})"
            change_service.log_setup_change(
                bow_setup_id=setup_id,
                user_id=current_user['id'],
                change_type='setup_modified',
                field_name=None,
                old_value=None,
                new_value=None,
                change_description=overall_description
            )
        
        conn.close()
        return jsonify(updated_setup)
        
    except Exception as e:
        print(f"Error updating bow setup: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/bow-setups/<int:setup_id>', methods=['DELETE'])
@token_required
def delete_bow_setup(current_user, setup_id):
    """Delete a bow setup"""
    from user_database import UserDatabase
    user_db = UserDatabase()
    conn = user_db.get_connection()
    cursor = conn.cursor()

    # Verify the setup belongs to the current user
    cursor.execute("SELECT * FROM bow_setups WHERE id = ? AND user_id = ?", (setup_id, current_user['id']))
    setup = cursor.fetchone()
    if not setup:
        conn.close()
        return jsonify({'error': 'Setup not found or you do not have permission to delete it'}), 404

    try:
        cursor.execute("DELETE FROM bow_setups WHERE id = ?", (setup_id,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Setup deleted successfully'})
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500


@app.route('/api/bow-setups/<int:setup_id>/arrows', methods=['POST'])
@token_required
def add_arrow_to_setup(current_user, setup_id):
    """Add an arrow to a bow setup"""
    conn = None
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['arrow_id', 'arrow_length', 'point_weight']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Get user database connection
        from user_database import UserDatabase
        user_db = UserDatabase()
        conn = user_db.get_connection()
        cursor = conn.cursor()
        
        # Verify the bow setup belongs to the current user
        cursor.execute("SELECT * FROM bow_setups WHERE id = ? AND user_id = ?", (setup_id, current_user['id']))
        bow_setup = cursor.fetchone()
        
        if not bow_setup:
            return jsonify({'error': 'Bow setup not found or access denied'}), 404
        
        # Use the provided spine from the arrow selection (DO NOT recalculate)
        # The spine should come from the user's arrow selection, not from calculations
        calculated_spine = data.get('calculated_spine')
        compatibility_score = data.get('compatibility_score')
        
        # Only calculate spine as a fallback if absolutely no spine was provided
        if calculated_spine is None:
            try:
                print("Warning: No spine provided when adding arrow to setup - using fallback calculation")
                # Use unified spine calculation service (same as calculator page)
                from spine_service import calculate_spine_for_setup
                
                calculated_spine = calculate_spine_for_setup(
                    bow_setup_data=dict(bow_setup),
                    arrow_data=data
                )
                
                # Set a basic compatibility score if not provided
                if not compatibility_score:
                    compatibility_score = 85  # Default good match score
                    
            except Exception as e:
                print(f"Error calculating spine: {e}")
                # Continue without calculated spine if calculation fails
                calculated_spine = None
        
        # The setup_arrows table is now created in user_database.py initialization
        
        # Check if this exact combination already exists (but skip check if this is a duplicate operation)
        allow_duplicate = data.get('allow_duplicate', False)
        existing_record = None
        
        if not allow_duplicate:
            cursor.execute('''
                SELECT id FROM setup_arrows 
                WHERE setup_id = ? AND arrow_id = ? AND arrow_length = ? AND point_weight = ?
            ''', (setup_id, data['arrow_id'], data['arrow_length'], data['point_weight']))
            
            existing_record = cursor.fetchone()
        
        if existing_record and not allow_duplicate:
            # Update existing record with component weights
            cursor.execute('''
                UPDATE setup_arrows 
                SET calculated_spine = ?, compatibility_score = ?, notes = ?,
                    nock_weight = ?, insert_weight = ?, bushing_weight = ?
                WHERE id = ?
            ''', (
                calculated_spine,
                compatibility_score,
                data.get('notes'),
                data.get('nock_weight', 10),
                data.get('insert_weight', 0),
                data.get('bushing_weight', 0),
                existing_record[0]
            ))
            arrow_association_id = existing_record[0]
        else:
            # Insert new record with component weights
            cursor.execute('''
                INSERT INTO setup_arrows 
                (setup_id, arrow_id, arrow_length, point_weight, calculated_spine, compatibility_score, notes,
                 nock_weight, insert_weight, bushing_weight)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                setup_id,
                data['arrow_id'],
                data['arrow_length'],
                data['point_weight'],
                calculated_spine,
                compatibility_score,
                data.get('notes'),
                data.get('nock_weight', 10),
                data.get('insert_weight', 0),
                data.get('bushing_weight', 0)
            ))
            arrow_association_id = cursor.lastrowid
        
        conn.commit()
        print(f"🔍 [add_arrow_to_setup] Created arrow association with ID={arrow_association_id} for setup_id={setup_id}")
        
        # Log the arrow addition
        try:
            from change_log_service import ChangeLogService
            change_service = ChangeLogService()
            
            # Create change description with arrow details
            arrow_details = f"Length: {data['arrow_length']}\", Point: {data['point_weight']}gr"
            change_description = f"Arrow added to setup ({arrow_details})"
            user_note = data.get('user_note', data.get('notes', 'Arrow added to setup'))
            
            change_service.log_arrow_change(
                bow_setup_id=setup_id,
                arrow_id=data['arrow_id'],
                user_id=current_user['id'],
                change_type='arrow_added',
                change_description=change_description,
                user_note=user_note
            )
        except Exception as e:
            print(f"Warning: Failed to log arrow addition: {e}")
        
        # Get arrow details from arrow database
        arrow_conn = get_arrow_db()
        if arrow_conn:
            arrow_cursor = arrow_conn.cursor()
            arrow_cursor.execute('''
                SELECT manufacturer, model_name, material
                FROM arrows WHERE id = ?
            ''', (data['arrow_id'],))
            arrow_data = arrow_cursor.fetchone()
            arrow_conn.close()
        else:
            arrow_data = None
        
        # Get the created association
        cursor.execute('SELECT * FROM setup_arrows WHERE id = ?', (arrow_association_id,))
        result = cursor.fetchone()
        conn.close()
        
        # Safely access result data (handle both tuple and dict)
        if hasattr(result, 'keys'):  # Dictionary-like (sqlite3.Row)
            response_data = {
                'id': result['id'],
                'setup_id': result['setup_id'], 
                'arrow_id': result['arrow_id'],
                'arrow_length': result['arrow_length'],
                'point_weight': result['point_weight'],
                'calculated_spine': result['calculated_spine'],
                'compatibility_score': result['compatibility_score'],
                'notes': result['notes'],
                'created_at': result['created_at']
            }
        else:  # Tuple access
            response_data = {
                'id': result[0],
                'setup_id': result[1], 
                'arrow_id': result[2],
                'arrow_length': result[3],
                'point_weight': result[4],
                'calculated_spine': result[5],
                'compatibility_score': result[6],
                'notes': result[7],
                'created_at': result[8]
            }
        
        if arrow_data:
            # Safely access arrow data (handle both tuple and dict)
            if hasattr(arrow_data, 'keys'):  # Dictionary-like (sqlite3.Row)
                response_data['arrow'] = {
                    'manufacturer': arrow_data['manufacturer'],
                    'model_name': arrow_data['model_name'],
                    'material': arrow_data['material']
                }
            else:  # Tuple access (index based on SELECT order: manufacturer, model_name, material)
                response_data['arrow'] = {
                    'manufacturer': arrow_data[0],
                    'model_name': arrow_data[1],
                    'material': arrow_data[2]
                }
        
        return jsonify(response_data)
        
    except sqlite3.IntegrityError as e:
        if conn:
            conn.close()
        if 'UNIQUE constraint failed' in str(e):
            return jsonify({'error': 'This arrow configuration already exists in your setup'}), 409
        else:
            return jsonify({'error': f'Database constraint error: {str(e)}'}), 400
    except Exception as e:
        if conn:
            conn.close()
        print(f"Error adding arrow to setup: {e}")
        return jsonify({'error': 'Failed to add arrow to setup'}), 500


@app.route('/api/bow-setups/<int:setup_id>/arrows', methods=['GET'])
@token_required
def get_setup_arrows(current_user, setup_id):
    """Get all arrows associated with a bow setup"""
    conn = None
    try:
        # Get user database connection
        from user_database import UserDatabase
        user_db = UserDatabase()
        conn = user_db.get_connection()
        cursor = conn.cursor()
        
        # Verify the bow setup belongs to the current user
        cursor.execute("SELECT * FROM bow_setups WHERE id = ? AND user_id = ?", (setup_id, current_user['id']))
        bow_setup = cursor.fetchone()
        
        if not bow_setup:
            return jsonify({'error': 'Bow setup not found or access denied'}), 404
        
        # Get all arrows for this setup
        cursor.execute('''
            SELECT * FROM setup_arrows
            WHERE setup_id = ?
            ORDER BY created_at DESC
        ''', (setup_id,))
        
        rows = cursor.fetchall()
        print(f"🔍 [get_setup_arrows] Found {len(rows)} arrows for setup_id {setup_id}")
        for i, row in enumerate(rows):
            if hasattr(row, 'keys'):
                # sqlite3.Row objects have keys but not .get() method
                created_at = row['created_at'] if 'created_at' in row.keys() else 'unknown'
                print(f"  - Arrow {i+1}: ID={row['id']}, arrow_id={row['arrow_id']}, created_at={created_at}")
            else:
                print(f"  - Arrow {i+1}: ID={row[0] if len(row) > 0 else 'unknown'}")
        conn.close()
        
        # Get arrow details from arrow database
        arrow_conn = get_arrow_db()
        arrow_details = {}
        if arrow_conn:
            try:
                arrow_cursor = arrow_conn.cursor()
                for row in rows:
                    print(f"Looking for arrow_id: {row['arrow_id']}")  # Debug log
                    # Get basic arrow info
                    arrow_cursor.execute('''
                        SELECT manufacturer, model_name, material, description
                        FROM arrows WHERE id = ?
                    ''', (row['arrow_id'],))
                    arrow_data = arrow_cursor.fetchone()
                    
                    if arrow_data:
                        print(f"Found arrow data: {dict(arrow_data) if hasattr(arrow_data, 'keys') else arrow_data}")  # Debug log
                    else:
                        print(f"No arrow found for arrow_id: {row['arrow_id']}")  # Debug log
                    
                    # Get spine specifications for this arrow
                    arrow_cursor.execute('''
                        SELECT spine, outer_diameter, inner_diameter, gpi_weight, length_options
                        FROM spine_specifications WHERE arrow_id = ?
                        ORDER BY spine ASC
                    ''', (row['arrow_id'],))
                    spine_specs = arrow_cursor.fetchall()
                    
                    if arrow_data:
                        arrow_details[row['arrow_id']] = {
                            'basic_info': arrow_data,
                            'spine_specifications': [dict(spec) for spec in spine_specs] if spine_specs else []
                        }
                    else:
                        print(f"Warning: Arrow ID {row['arrow_id']} not found in arrow database")
                arrow_conn.close()
            except Exception as e:
                print(f"Error fetching arrow details: {e}")
                import traceback
                traceback.print_exc()
                if arrow_conn:
                    arrow_conn.close()
        else:
            print("Warning: Arrow database connection failed - arrow details will not be available")
        
        arrows = []
        for row in rows:
            arrow_info = {
                'id': row['id'],
                'setup_id': row['setup_id'],
                'arrow_id': row['arrow_id'],
                'arrow_length': row['arrow_length'],
                'point_weight': row['point_weight'],
                'calculated_spine': row['calculated_spine'],
                'compatibility_score': row['compatibility_score'],
                'notes': row['notes'],
                'created_at': row['created_at']
            }
            
            # Add arrow details if available
            if row['arrow_id'] in arrow_details:
                arrow_detail = arrow_details[row['arrow_id']]
                basic_info = arrow_detail['basic_info']
                spine_specifications = arrow_detail['spine_specifications']
                
                # Handle both dict (sqlite3.Row) and tuple access
                if hasattr(basic_info, 'keys'):  # Dictionary-like (sqlite3.Row)
                    arrow_info['arrow'] = {
                        'manufacturer': basic_info['manufacturer'], 
                        'model_name': basic_info['model_name'],
                        'material': basic_info['material'],
                        'description': basic_info['description'],
                        'spine_specifications': spine_specifications
                    }
                else:  # Tuple access (index based on SELECT order: manufacturer, model_name, material, description)
                    arrow_info['arrow'] = {
                        'manufacturer': basic_info[0] if len(basic_info) > 0 else 'Unknown Manufacturer', 
                        'model_name': basic_info[1] if len(basic_info) > 1 else 'Unknown Model',
                        'material': basic_info[2] if len(basic_info) > 2 else 'Unknown Material',
                        'description': basic_info[3] if len(basic_info) > 3 else 'No description available',
                        'spine_specifications': spine_specifications
                    }
                
                # Add component weights from setup_arrows table if available
                for field in ['nock_weight', 'insert_weight', 'bushing_weight', 'fletching_weight']:
                    if field in row and row[field] is not None:
                        arrow_info[field] = row[field]
                
            else:
                # Provide fallback arrow info when details are not available
                arrow_info['arrow'] = {
                    'manufacturer': 'Unknown Manufacturer',
                    'model_name': f'Arrow ID {row["arrow_id"]}',
                    'material': 'Unknown Material',
                    'description': 'Arrow details not available',
                    'spine_specifications': []
                }
            
            arrows.append(arrow_info)
        
        return jsonify({'arrows': arrows})
        
    except Exception as e:
        if conn:
            conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/setup-arrows/<int:arrow_setup_id>', methods=['DELETE'])
@token_required
def remove_arrow_from_setup(current_user, arrow_setup_id):
    """Remove an arrow from a bow setup"""
    conn = None
    try:
        # Get user database connection
        from user_database import UserDatabase
        user_db = UserDatabase()
        conn = user_db.get_connection()
        cursor = conn.cursor()
        
        # Get the arrow setup to verify ownership
        cursor.execute('''
            SELECT sa.*, bs.user_id 
            FROM setup_arrows sa
            JOIN bow_setups bs ON sa.setup_id = bs.id
            WHERE sa.id = ?
        ''', (arrow_setup_id,))
        
        arrow_setup = cursor.fetchone()
        
        if not arrow_setup:
            return jsonify({'error': 'Arrow setup not found'}), 404
        
        if arrow_setup['user_id'] != current_user['id']:
            return jsonify({'error': 'Access denied'}), 403
        
        # Log the arrow removal before deletion
        try:
            from change_log_service import ChangeLogService
            change_service = ChangeLogService()
            
            # Create change description with arrow details
            arrow_details = f"Length: {arrow_setup['arrow_length']}\", Point: {arrow_setup['point_weight']}gr"
            change_description = f"Arrow removed from setup ({arrow_details})"
            
            change_service.log_arrow_change(
                bow_setup_id=arrow_setup['setup_id'],
                arrow_id=arrow_setup['arrow_id'],
                user_id=current_user['id'],
                change_type='arrow_removed',
                change_description=change_description,
                user_note='Arrow removed from setup'
            )
        except Exception as e:
            print(f"Warning: Failed to log arrow removal: {e}")
        
        # Delete the arrow setup
        cursor.execute('DELETE FROM setup_arrows WHERE id = ?', (arrow_setup_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Arrow removed from setup successfully'})
        
    except Exception as e:
        if conn:
            conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/bow-setups/<int:setup_id>/arrows/<int:arrow_id>', methods=['PUT'])
@token_required  
def update_bow_setup_arrow(current_user, setup_id, arrow_id):
    """Update an arrow configuration in a bow setup by setup_id and arrow_id"""
    conn = None
    try:
        data = request.get_json()
        
        # Get user database connection
        from user_database import UserDatabase
        user_db = UserDatabase()
        conn = user_db.get_connection()
        cursor = conn.cursor()
        
        # Find the arrow setup record
        cursor.execute('''
            SELECT sa.id, sa.setup_id, sa.arrow_id, bs.user_id 
            FROM setup_arrows sa
            JOIN bow_setups bs ON sa.setup_id = bs.id
            WHERE sa.setup_id = ? AND sa.arrow_id = ?
        ''', (setup_id, arrow_id))
        
        arrow_setup = cursor.fetchone()
        
        if not arrow_setup:
            return jsonify({'error': 'Arrow setup not found'}), 404
        
        if arrow_setup['user_id'] != current_user['id']:
            return jsonify({'error': 'Access denied'}), 403
        
        # Update the arrow setup using the internal function
        return update_arrow_in_setup_internal(arrow_setup['id'], data, conn)
        
    except Exception as e:
        if conn:
            conn.close()
        return jsonify({'error': str(e)}), 500

def update_arrow_in_setup_internal(arrow_setup_id, data, conn, user_id=None):
    """Internal function to update arrow setup - shared by different endpoints"""
    cursor = conn.cursor()
    
    # Get the current arrow setup and bow setup info
    cursor.execute('''
        SELECT sa.*, bs.id as bow_setup_id
        FROM setup_arrows sa
        JOIN bow_setups bs ON sa.setup_id = bs.id
        WHERE sa.id = ?
    ''', (arrow_setup_id,))
    arrow_setup = cursor.fetchone()
    
    if not arrow_setup:
        return jsonify({'error': 'Arrow setup not found'}), 404
    
    # Convert sqlite3.Row to dict for easier access
    arrow_setup_dict = dict(arrow_setup) if hasattr(arrow_setup, 'keys') else arrow_setup
    old_data = dict(arrow_setup_dict)
    
    # Create new data dict with updates
    new_data = {
        'arrow_length': data.get('arrow_length', arrow_setup_dict['arrow_length']),
        'point_weight': data.get('point_weight', arrow_setup_dict['point_weight']),
        'calculated_spine': data.get('calculated_spine', arrow_setup_dict['calculated_spine']),
        'notes': data.get('notes', arrow_setup_dict['notes']),
        'nock_weight': data.get('nock_weight', arrow_setup_dict.get('nock_weight', 10)),
        'insert_weight': data.get('insert_weight', arrow_setup_dict.get('insert_weight', 0)),
        'bushing_weight': data.get('bushing_weight', arrow_setup_dict.get('bushing_weight', 0)),
        'compatibility_score': data.get('compatibility_score', arrow_setup_dict.get('compatibility_score'))
    }
    
    # Update the arrow setup with component weights
    cursor.execute('''
        UPDATE setup_arrows 
        SET arrow_length = ?, point_weight = ?, calculated_spine = ?, notes = ?,
            nock_weight = ?, insert_weight = ?, bushing_weight = ?, compatibility_score = ?
        WHERE id = ?
    ''', (
        new_data['arrow_length'],
        new_data['point_weight'],
        new_data['calculated_spine'],
        new_data['notes'],
        new_data['nock_weight'],
        new_data['insert_weight'],
        new_data['bushing_weight'],
        new_data['compatibility_score'],
        arrow_setup_id
    ))
    
    conn.commit()
    
    # Log the arrow changes if user_id is provided
    if user_id:
        try:
            from change_log_service import ChangeLogService
            change_service = ChangeLogService()
            
            user_note = data.get('user_note', 'Arrow settings updated')
            change_log_ids = change_service.log_arrow_field_changes(
                bow_setup_id=arrow_setup_dict['bow_setup_id'],
                arrow_id=arrow_setup_dict['arrow_id'],
                user_id=user_id,
                old_data=old_data,
                new_data=new_data,
                user_note=user_note
            )
            
            if change_log_ids:
                print(f"📝 Logged {len(change_log_ids)} arrow field changes")
                
        except Exception as e:
            print(f"Warning: Failed to log arrow changes: {e}")
    
    # Get the updated record
    cursor.execute('SELECT * FROM setup_arrows WHERE id = ?', (arrow_setup_id,))
    updated_record = cursor.fetchone()
    
    # Convert to dict for JSON response
    if hasattr(updated_record, 'keys'):  # sqlite3.Row object
        response_data = dict(updated_record)
    else:
        response_data = {
            'id': updated_record[0],
            'setup_id': updated_record[1],
            'arrow_id': updated_record[2],
            'arrow_length': updated_record[3],
            'point_weight': updated_record[4],
            'calculated_spine': updated_record[5],
            'compatibility_score': updated_record[6],
            'notes': updated_record[7],
            'created_at': updated_record[8]
        }
    
    return jsonify({
        'message': 'Arrow setup updated successfully',
        'arrow_setup': response_data
    })

@app.route('/api/setup-arrows/<int:arrow_setup_id>', methods=['PUT'])
@token_required
def update_arrow_in_setup(current_user, arrow_setup_id):
    """Update an arrow configuration in a bow setup"""
    conn = None
    try:
        data = request.get_json()
        
        # Get user database connection
        from user_database import UserDatabase
        user_db = UserDatabase()
        conn = user_db.get_connection()
        cursor = conn.cursor()
        
        # Get the arrow setup to verify ownership
        cursor.execute('''
            SELECT sa.*, bs.user_id 
            FROM setup_arrows sa
            JOIN bow_setups bs ON sa.setup_id = bs.id
            WHERE sa.id = ?
        ''', (arrow_setup_id,))
        
        arrow_setup = cursor.fetchone()
        
        if not arrow_setup:
            return jsonify({'error': 'Arrow setup not found'}), 404
        
        if arrow_setup['user_id'] != current_user['id']:
            return jsonify({'error': 'Access denied'}), 403
        
        # Use the internal update function
        result = update_arrow_in_setup_internal(arrow_setup_id, data, conn, user_id=current_user['id'])
        conn.close()
        return result
        
    except Exception as e:
        if conn:
            conn.close()
        return jsonify({'error': str(e)}), 500


@app.route('/api/tuning/sessions/<session_id>', methods=['GET'])
def get_tuning_session(session_id):
    """Get a specific tuning session"""
    try:
        session_data = tuning_sessions.get(session_id)
        
        if not session_data:
            return jsonify({'error': 'Session not found'}), 404
        
        return jsonify(session_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tuning/sessions', methods=['GET'])
def get_tuning_sessions():
    """Get all tuning sessions"""
    try:
        sessions = list(tuning_sessions.values())
        # Sort by creation date, most recent first
        sessions.sort(key=lambda x: x['created_at'], reverse=True)
        
        return jsonify(sessions)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Arrow compatibility check
@app.route('/api/arrows/compatible', methods=['POST'])
def check_arrow_compatibility():
    """Check arrow compatibility with bow configuration"""
    try:
        data = request.get_json()
        
        bow_config = data.get('bow_config', {})
        arrow_filters = data.get('filters', {})
        
        # Get compatible arrows
        db = get_database()
        if not db:
            return jsonify({'error': 'Database not available'}), 500
        
        # If wood material is selected, search for wood arrow manufacturers first
        compatible_arrows = []
        if bow_config.get('arrow_material') == 'wood':
            # Search specifically for wood arrow manufacturers
            wood_arrows_1 = db.search_arrows(
                manufacturer="Traditional Wood",
                arrow_type=bow_config.get('arrow_type'),
                model_search=arrow_filters.get('search'),
                limit=25
            )
            wood_arrows_2 = db.search_arrows(
                manufacturer="Traditional Wood Arrows", 
                arrow_type=bow_config.get('arrow_type'),
                model_search=arrow_filters.get('search'),
                limit=25
            )
            compatible_arrows = wood_arrows_1 + wood_arrows_2
        else:
            # Regular search for other materials
            compatible_arrows = db.search_arrows(
                manufacturer=arrow_filters.get('manufacturer'),
                arrow_type=bow_config.get('arrow_type'),
                model_search=arrow_filters.get('search'),
                limit=50
            )
        
        # Filter based on bow configuration compatibility
        filtered_arrows = []
        for arrow in compatible_arrows:
            # Basic compatibility check
            is_compatible = True
            
            # Material compatibility
            if bow_config.get('arrow_material'):
                arrow_material = arrow.get('material') or ''
                arrow_material = arrow_material.lower()
                selected_material = bow_config['arrow_material'].lower()
                
                if selected_material == 'wood':
                    # Wood arrows contain "wood" in their material name
                    if 'wood' not in arrow_material:
                        is_compatible = False
                elif selected_material == 'carbon':
                    # Carbon arrows typically have 'carbon' in material or no specific wood/aluminum mention
                    if 'wood' in arrow_material or 'aluminum' in arrow_material:
                        is_compatible = False
                elif selected_material == 'aluminum':
                    # Aluminum arrows contain 'aluminum' in material
                    if 'aluminum' not in arrow_material:
                        is_compatible = False
                elif selected_material == 'carbon-aluminum':
                    # Carbon-aluminum hybrid arrows
                    if not ('carbon' in arrow_material and 'aluminum' in arrow_material):
                        is_compatible = False
                else:
                    # For other materials, check if the material name matches
                    if selected_material not in arrow_material:
                        is_compatible = False
            
            if is_compatible:
                filtered_arrows.append(arrow)
        
        return jsonify({
            'compatible_arrows': filtered_arrows[:20],  # Limit results
            'total_compatible': len(filtered_arrows),
            'bow_config': bow_config
        })
        
    except Exception as e:
        import traceback
        return jsonify({'error': f'Compatible arrows error: {str(e)}'}), 500

# Static File Serving for Images
@app.route('/api/images/<filename>')
def serve_image(filename):
    """Serve downloaded arrow images"""
    try:
        images_dir = Path(__file__).parent / 'data' / 'images'
        
        # Check if file exists before trying to serve it
        file_path = images_dir / filename
        
        if not file_path.exists():
            return jsonify({'error': f'Image not found: {filename}'}), 404
        
        # Serve the file with appropriate MIME type
        if filename.endswith('.svg'):
            return send_from_directory(str(images_dir), filename, mimetype='image/svg+xml')
        else:
            return send_from_directory(str(images_dir), filename)
            
    except Exception as e:
        import traceback
        return jsonify({'error': f'Error serving image: {str(e)}'}), 500

def get_image_url(arrow_id, image_url=None, saved_images=None, local_image_path=None):
    """Get the best available image URL for an arrow"""
    try:
        # Handle HTTPS/HTTP protocol correctly for reverse proxy setups
        base_url = request.host_url.rstrip('/')
        
        # Check if request came through HTTPS (via headers from reverse proxy)
        if (request.headers.get('X-Forwarded-Proto') == 'https' or 
            request.headers.get('X-Forwarded-SSL') == 'on' or
            request.is_secure):
            base_url = base_url.replace('http://', 'https://')
        
        # Option 1: Try local image path from database
        if local_image_path:
            filename = Path(local_image_path).name
            # Verify the file actually exists before returning URL
            images_dir = Path(__file__).parent / 'data' / 'images'
            if (images_dir / filename).exists():
                return f"{base_url}/api/images/{filename}"
        
        # Option 2: Try saved_images parameter (for compatibility)
        if saved_images:
            for saved_image in saved_images:
                if saved_image:
                    filename = Path(saved_image).name
                    images_dir = Path(__file__).parent / 'data' / 'images'
                    if (images_dir / filename).exists():
                        return f"{base_url}/api/images/{filename}"
        
        # Option 3: Use original manufacturer image URL
        if image_url and image_url.startswith('http'):
            return image_url
        
        # Option 4: Use placeholder (always return this as fallback)
        return f"{base_url}/api/images/placeholder.svg"
        
    except Exception as e:
        print(f"Error generating image URL: {e}")
        # Return a protocol-relative placeholder if everything fails
        return "/api/images/placeholder.svg"

# ===== COMPONENT API ENDPOINTS =====

@app.route('/api/components', methods=['GET'])
def get_components():
    """Get components with optional filtering"""
    try:
        db = get_component_database()
        if not db:
            return jsonify({'error': 'Component database not available'}), 500
        
        # Get query parameters
        category = request.args.get('category')
        manufacturer = request.args.get('manufacturer')
        limit = int(request.args.get('limit', 50))
        
        components = db.get_components(
            category_name=category,
            manufacturer=manufacturer,
            limit=limit
        )
        
        return jsonify({
            'components': components,
            'total': len(components),
            'filters': {
                'category': category,
                'manufacturer': manufacturer,
                'limit': limit
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/components/categories', methods=['GET'])
def get_component_categories():
    """Get all component categories"""
    try:
        db = get_component_database()
        if not db:
            return jsonify({'error': 'Component database not available'}), 500
        
        stats = db.get_component_statistics()
        categories = stats.get('categories', [])
        
        return jsonify({
            'categories': categories,
            'total_categories': len(categories)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/components/statistics', methods=['GET'])
def get_component_statistics():
    """Get component database statistics"""
    try:
        db = get_component_database()
        if not db:
            return jsonify({'error': 'Component database not available'}), 500
        
        stats = db.get_component_statistics()
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/arrows/<int:arrow_id>/compatible-components', methods=['GET'])
def get_arrow_compatible_components(arrow_id):
    """Get components compatible with a specific arrow"""
    try:
        engine = get_compatibility_engine()
        if not engine:
            return jsonify({'error': 'Compatibility engine not available'}), 500
        
        # Get query parameters
        category = request.args.get('category')
        limit = int(request.args.get('limit', 20))
        
        compatible_components = engine.get_compatible_components(arrow_id, category)
        
        # Limit results
        if limit:
            compatible_components = compatible_components[:limit]
        
        return jsonify({
            'arrow_id': arrow_id,
            'compatible_components': compatible_components,
            'total': len(compatible_components),
            'category_filter': category
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/compatibility/check', methods=['POST'])
def check_compatibility():
    """Check compatibility between arrow and component"""
    try:
        data = request.get_json()
        arrow_id = data.get('arrow_id')
        component_id = data.get('component_id')
        
        if not arrow_id or not component_id:
            return jsonify({'error': 'arrow_id and component_id required'}), 400
        
        engine = get_compatibility_engine()
        if not engine:
            return jsonify({'error': 'Compatibility engine not available'}), 500
        
        result = engine.check_compatibility(arrow_id, component_id)
        
        return jsonify({
            'arrow_id': result.arrow_id,
            'component_id': result.component_id,
            'compatibility_type': result.compatibility_type,
            'score': result.score,
            'matching_rules': result.matching_rules,
            'notes': result.notes,
            'compatible': result.compatibility_type != 'incompatible'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/compatibility/batch', methods=['POST'])
def batch_compatibility_check():
    """Check compatibility for multiple arrow-component pairs"""
    try:
        data = request.get_json()
        arrow_ids = data.get('arrow_ids', [])
        component_ids = data.get('component_ids', [])
        
        if not arrow_ids or not component_ids:
            return jsonify({'error': 'arrow_ids and component_ids required'}), 400
        
        engine = get_compatibility_engine()
        if not engine:
            return jsonify({'error': 'Compatibility engine not available'}), 500
        
        results = engine.batch_compatibility_check(arrow_ids, component_ids)
        
        # Convert results to JSON-serializable format
        compatibility_results = []
        for result in results:
            compatibility_results.append({
                'arrow_id': result.arrow_id,
                'component_id': result.component_id,
                'compatibility_type': result.compatibility_type,
                'score': result.score,
                'matching_rules': result.matching_rules,
                'notes': result.notes
            })
        
        return jsonify({
            'results': compatibility_results,
            'total_combinations_checked': len(arrow_ids) * len(component_ids),
            'compatible_combinations': len(compatibility_results)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/components', methods=['POST'])
def add_component():
    """Add a new component (admin/scraper endpoint)"""
    try:
        data = request.get_json()
        
        required_fields = ['category', 'manufacturer', 'model_name', 'specifications']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        db = get_component_database()
        if not db:
            return jsonify({'error': 'Component database not available'}), 500
        
        component_id = db.add_component(
            category_name=data['category'],
            manufacturer=data['manufacturer'],
            model_name=data['model_name'],
            specifications=data['specifications'],
            image_url=data.get('image_url'),
            local_image_path=data.get('local_image_path'),
            price_range=data.get('price_range'),
            description=data.get('description'),
            source_url=data.get('source_url'),
            scraped_at=data.get('scraped_at')
        )
        
        if component_id:
            return jsonify({
                'message': 'Component added successfully',
                'component_id': component_id
            }), 201
        else:
            return jsonify({'error': 'Failed to add component'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== ADMIN API ENDPOINTS =====

def admin_required(f):
    """Decorator to require admin access"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(current_user, *args, **kwargs):
        from user_database import UserDatabase
        user_db = UserDatabase()
        
        if not user_db.is_user_admin(current_user['id']):
            return jsonify({'error': 'Admin access required'}), 403
        
        return f(current_user, *args, **kwargs)
    
    return decorated_function

@app.route('/api/admin/users', methods=['GET'])
@token_required
@admin_required
def get_all_users_admin(current_user):
    """Get all users (admin only)"""
    try:
        from user_database import UserDatabase
        user_db = UserDatabase()
        
        users = user_db.get_all_users()
        
        return jsonify({
            'users': users,
            'total': len(users)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/users/<int:user_id>/admin', methods=['PUT'])
@token_required
@admin_required
def set_user_admin_status(current_user, user_id):
    """Set admin status for a user (admin only)"""
    try:
        from user_database import UserDatabase
        user_db = UserDatabase()
        
        data = request.get_json()
        is_admin = data.get('is_admin', False)
        
        success = user_db.set_admin_status(user_id, is_admin)
        
        if success:
            return jsonify({
                'message': f'User {user_id} admin status updated to {is_admin}',
                'user_id': user_id,
                'is_admin': is_admin
            })
        else:
            return jsonify({'error': 'Failed to update admin status'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/check', methods=['GET'])
@token_required
def check_admin_status(current_user):
    """Check if current user has admin access"""
    try:
        from user_database import UserDatabase
        user_db = UserDatabase()
        
        is_admin = user_db.is_user_admin(current_user['id'])
        
        return jsonify({
            'is_admin': is_admin,
            'user_id': current_user['id'],
            'email': current_user.get('email')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== ADMIN BACKUP/RESTORE API ENDPOINTS =====

@app.route('/api/admin/backup-test', methods=['GET'])
def backup_test_new():
    """Simple backup test endpoint without auth"""
    from datetime import datetime
    print(f"🔧 NEW BACKUP TEST ENDPOINT CALLED - {datetime.now()}")
    return jsonify({'message': 'NEW Backup test endpoint works!', 'timestamp': datetime.now().isoformat()})

# Removed duplicate list_backups function - using the complete implementation later in the file

# Removed test routes - using actual implementations later in the file

# ===== ADMIN ARROW MANAGEMENT API ENDPOINTS =====

@app.route('/api/admin/arrows', methods=['GET'])
@token_required
@admin_required
def get_all_arrows_admin(current_user):
    """Get all arrows with pagination for admin management"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        search = request.args.get('search', '')
        manufacturer = request.args.get('manufacturer', '')
        
        db = get_database()
        
        # Build query conditions
        conditions = []
        params = []
        
        if search:
            conditions.append("(a.manufacturer LIKE ? OR a.model_name LIKE ? OR a.description LIKE ?)")
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param])
        
        if manufacturer:
            conditions.append("a.manufacturer = ?")
            params.append(manufacturer)
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        # Count total arrows
        count_query = f"""
            SELECT COUNT(DISTINCT a.id) as total
            FROM arrows a
            {where_clause}
        """
        
        cursor = db.get_connection().cursor()
        cursor.execute(count_query, params)
        total = cursor.fetchone()['total']
        
        # Get arrows with spine specifications
        offset = (page - 1) * per_page
        arrows_query = f"""
            SELECT DISTINCT
                a.id,
                a.manufacturer,
                a.model_name,
                a.material,
                a.arrow_type,
                a.description,
                a.image_url as primary_image_url,
                a.created_at,
                COUNT(s.id) as spine_count,
                MIN(s.spine) as min_spine,
                MAX(s.spine) as max_spine
            FROM arrows a
            LEFT JOIN spine_specifications s ON a.id = s.arrow_id
            {where_clause}
            GROUP BY a.id
            ORDER BY a.manufacturer, a.model_name
            LIMIT ? OFFSET ?
        """
        
        cursor.execute(arrows_query, params + [per_page, offset])
        arrows = [dict(row) for row in cursor.fetchall()]
        
        return jsonify({
            'arrows': arrows,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/arrows/<int:arrow_id>', methods=['GET'])
@token_required
@admin_required
def get_arrow_admin(current_user, arrow_id):
    """Get detailed arrow information for admin editing"""
    try:
        db = get_database()
        
        # Get arrow details with spine specifications
        query = """
            SELECT 
                a.*,
                COUNT(s.id) as spine_count
            FROM arrows a
            LEFT JOIN spine_specifications s ON a.id = s.arrow_id
            WHERE a.id = ?
            GROUP BY a.id
        """
        
        cursor = db.get_connection().cursor()
        cursor.execute(query, (arrow_id,))
        arrow = cursor.fetchone()
        
        if not arrow:
            return jsonify({'error': 'Arrow not found'}), 404
        
        arrow_data = dict(arrow)
        
        # Get spine specifications
        spine_query = """
            SELECT *
            FROM spine_specifications
            WHERE arrow_id = ?
            ORDER BY spine
        """
        
        cursor.execute(spine_query, (arrow_id,))
        spine_specs = [dict(row) for row in cursor.fetchall()]
        
        arrow_data['spine_specifications'] = spine_specs
        
        return jsonify(arrow_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/arrows/<int:arrow_id>', methods=['PUT'])
@token_required
@admin_required
def update_arrow_admin(current_user, arrow_id):
    """Update arrow information (admin only)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        db = get_database()
        cursor = db.get_connection().cursor()
        
        # Check if arrow exists
        cursor.execute("SELECT id FROM arrows WHERE id = ?", (arrow_id,))
        if not cursor.fetchone():
            return jsonify({'error': 'Arrow not found'}), 404
        
        # Build update query
        update_fields = []
        params = []
        
        # Only include fields that actually exist in the arrows table
        allowed_fields = [
            'manufacturer', 'model_name', 'material', 'arrow_type', 
            'description', 'image_url', 'carbon_content'
        ]
        
        for field in allowed_fields:
            if field in data:
                update_fields.append(f"{field} = ?")
                params.append(data[field])
        
        # Handle primary_image_url -> image_url mapping from frontend
        if 'primary_image_url' in data and 'image_url' not in data:
            update_fields.append("image_url = ?")
            params.append(data['primary_image_url'])
        
        if not update_fields:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        # Note: updated_at column doesn't exist in arrows table
        params.append(arrow_id)
        
        # Update arrow
        update_query = f"""
            UPDATE arrows 
            SET {', '.join(update_fields)}
            WHERE id = ?
        """
        
        cursor.execute(update_query, params)
        db.get_connection().commit()
        
        # Handle spine specifications update if provided
        if 'spine_specifications' in data:
            spine_specs = data['spine_specifications']
            
            # Delete existing spine specifications
            cursor.execute("DELETE FROM spine_specifications WHERE arrow_id = ?", (arrow_id,))
            
            # Insert new spine specifications
            for spec in spine_specs:
                spine_query = """
                    INSERT INTO spine_specifications 
                    (arrow_id, spine, outer_diameter, gpi_weight, inner_diameter, 
                     length_options, wall_thickness, insert_weight_range, nock_size, 
                     notes, straightness_tolerance, weight_tolerance, diameter_category)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                cursor.execute(spine_query, (
                    arrow_id,
                    spec.get('spine'),
                    spec.get('outer_diameter'),
                    spec.get('gpi_weight'),
                    spec.get('inner_diameter'),
                    json.dumps(spec.get('length_options', [])),
                    spec.get('wall_thickness'),
                    spec.get('insert_weight_range'),
                    spec.get('nock_size'),
                    spec.get('notes'),
                    spec.get('straightness_tolerance'),
                    spec.get('weight_tolerance'),
                    spec.get('diameter_category')
                ))
            
            db.get_connection().commit()
        
        return jsonify({
            'message': 'Arrow updated successfully',
            'arrow_id': arrow_id,
            'updated_by': current_user['email']
        })
        
    except Exception as e:
        db.get_connection().rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/arrows/<int:arrow_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_arrow_admin(current_user, arrow_id):
    """Delete arrow (admin only)"""
    try:
        db = get_database()
        cursor = db.get_connection().cursor()
        
        # Check if arrow exists
        cursor.execute("SELECT manufacturer, model_name FROM arrows WHERE id = ?", (arrow_id,))
        arrow = cursor.fetchone()
        if not arrow:
            return jsonify({'error': 'Arrow not found'}), 404
        
        arrow_info = dict(arrow)
        
        # Delete spine specifications first (foreign key constraint)
        cursor.execute("DELETE FROM spine_specifications WHERE arrow_id = ?", (arrow_id,))
        
        # Delete arrow
        cursor.execute("DELETE FROM arrows WHERE id = ?", (arrow_id,))
        
        db.get_connection().commit()
        
        return jsonify({
            'message': f'Arrow {arrow_info["manufacturer"]} {arrow_info["model_name"]} deleted successfully',
            'arrow_id': arrow_id,
            'deleted_by': current_user['email']
        })
        
    except Exception as e:
        db.get_connection().rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/arrows', methods=['POST'])
@token_required
@admin_required
def create_arrow_admin(current_user):
    """Create new arrow (admin only)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['manufacturer', 'model_name', 'spine_specifications']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Field {field} is required'}), 400
        
        if not isinstance(data['spine_specifications'], list) or len(data['spine_specifications']) == 0:
            return jsonify({'error': 'At least one spine specification is required'}), 400
        
        db = get_database()
        cursor = db.get_connection().cursor()
        
        # Insert arrow - only include fields that exist in arrows table
        arrow_query = """
            INSERT INTO arrows 
            (manufacturer, model_name, material, arrow_type, description, 
             image_url, carbon_content, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        # Handle primary_image_url -> image_url mapping from frontend
        image_url = data.get('image_url') or data.get('primary_image_url')
        
        now = datetime.utcnow().isoformat()
        cursor.execute(arrow_query, (
            data['manufacturer'],
            data['model_name'],
            data.get('material'),
            data.get('arrow_type'),
            data.get('description'),
            image_url,
            data.get('carbon_content'),
            now
        ))
        
        arrow_id = cursor.lastrowid
        
        # Insert spine specifications
        for spec in data['spine_specifications']:
            spine_query = """
                INSERT INTO spine_specifications 
                (arrow_id, spine, outer_diameter, gpi_weight, inner_diameter, 
                 length_options, wall_thickness, insert_weight_range, nock_size, 
                 notes, straightness_tolerance, weight_tolerance, diameter_category)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(spine_query, (
                arrow_id,
                spec.get('spine'),
                spec.get('outer_diameter'),
                spec.get('gpi_weight'),
                spec.get('inner_diameter'),
                json.dumps(spec.get('length_options', [])),
                spec.get('wall_thickness'),
                spec.get('insert_weight_range'),
                spec.get('nock_size'),
                spec.get('notes'),
                spec.get('straightness_tolerance'),
                spec.get('weight_tolerance'),
                spec.get('diameter_category')
            ))
        
        db.get_connection().commit()
        
        return jsonify({
            'message': 'Arrow created successfully',
            'arrow_id': arrow_id,
            'created_by': current_user['email']
        }), 201
        
    except Exception as e:
        db.get_connection().rollback()
        return jsonify({'error': str(e)}), 500

# ===== UNIFIED MANUFACTURER MANAGEMENT API ENDPOINTS (ADMIN) =====

@app.route('/api/admin/manufacturers', methods=['GET'])
@token_required
@admin_required
def get_manufacturers_admin(current_user):
    """Get all manufacturers with statistics (admin only)"""
    try:
        db = get_database()
        cursor = db.get_connection().cursor()
        
        # Get manufacturers with arrow and equipment counts
        query = """
            SELECT 
                m.id,
                m.name,
                m.website_url,
                m.logo_url,
                m.description,
                m.country,
                m.established_year,
                m.is_active,
                m.created_at,
                m.updated_at,
                COALESCE(arrow_stats.arrow_count, 0) as arrow_count,
                COALESCE(equipment_stats.equipment_count, 0) as equipment_count,
                arrow_stats.first_arrow_added,
                arrow_stats.last_arrow_added
            FROM manufacturers m
            LEFT JOIN (
                SELECT 
                    manufacturer_id,
                    COUNT(*) as arrow_count,
                    MIN(created_at) as first_arrow_added,
                    MAX(created_at) as last_arrow_added
                FROM arrows 
                WHERE manufacturer_id IS NOT NULL
                GROUP BY manufacturer_id
            ) arrow_stats ON m.id = arrow_stats.manufacturer_id
            LEFT JOIN (
                SELECT 
                    manufacturer_id,
                    COUNT(*) as equipment_count
                FROM equipment 
                WHERE manufacturer_id IS NOT NULL
                GROUP BY manufacturer_id
            ) equipment_stats ON m.id = equipment_stats.manufacturer_id
            ORDER BY m.name
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        manufacturers = []
        for row in results:
            # Get equipment categories for this manufacturer
            cursor.execute("""
                SELECT category_name, is_supported, notes 
                FROM manufacturer_equipment_categories 
                WHERE manufacturer_id = ?
                ORDER BY category_name
            """, (row[0],))
            
            categories = []
            for cat_row in cursor.fetchall():
                categories.append({
                    'name': cat_row[0],
                    'is_supported': bool(cat_row[1]),
                    'notes': cat_row[2]
                })
            
            manufacturers.append({
                'id': row[0],
                'name': row[1],
                'website_url': row[2],
                'logo_url': row[3],
                'description': row[4],
                'country': row[5],
                'established_year': row[6],
                'is_active': bool(row[7]),
                'created_at': row[8],
                'updated_at': row[9],
                'arrow_count': row[10],
                'equipment_count': row[11],
                'first_added': row[12],
                'last_added': row[13],
                'equipment_categories': categories
            })
        
        return jsonify({
            'manufacturers': manufacturers,
            'total_count': len(manufacturers)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/manufacturers/<int:manufacturer_id>', methods=['PUT'])
@token_required
@admin_required
def update_manufacturer_admin(current_user, manufacturer_id):
    """Update manufacturer details (admin only)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request data is required'}), 400
        
        db = get_database()
        cursor = db.get_connection().cursor()
        
        # Check if manufacturer exists
        cursor.execute("SELECT * FROM manufacturers WHERE id = ?", (manufacturer_id,))
        manufacturer = cursor.fetchone()
        if not manufacturer:
            return jsonify({'error': 'Manufacturer not found'}), 404
        
        # Build update query dynamically based on provided fields
        update_fields = []
        update_values = []
        
        # Updatable fields
        updatable_fields = ['name', 'website_url', 'logo_url', 'description', 'country', 'established_year', 'is_active']
        
        for field in updatable_fields:
            if field in data:
                if field == 'name':
                    # Check if new name already exists (case insensitive)
                    new_name = data[field].strip()
                    if not new_name:
                        return jsonify({'error': 'Manufacturer name cannot be empty'}), 400
                    
                    cursor.execute("SELECT id FROM manufacturers WHERE LOWER(name) = LOWER(?) AND id != ?", (new_name, manufacturer_id))
                    if cursor.fetchone():
                        return jsonify({'error': 'A manufacturer with this name already exists'}), 409
                    
                    update_fields.append('name = ?')
                    update_values.append(new_name)
                elif field == 'is_active':
                    update_fields.append('is_active = ?')
                    update_values.append(1 if data[field] else 0)
                elif field == 'established_year':
                    year = data[field]
                    if year is not None and (not isinstance(year, int) or year < 1800 or year > 2030):
                        return jsonify({'error': 'Established year must be between 1800 and 2030'}), 400
                    update_fields.append('established_year = ?')
                    update_values.append(year)
                else:
                    update_fields.append(f'{field} = ?')
                    update_values.append(data[field])
        
        if update_fields:
            # Add updated_at timestamp
            update_fields.append('updated_at = CURRENT_TIMESTAMP')
            update_values.append(manufacturer_id)
            
            query = f"UPDATE manufacturers SET {', '.join(update_fields)} WHERE id = ?"
            cursor.execute(query, update_values)
        
        db.get_connection().commit()
        
        # Get updated manufacturer data
        cursor.execute("SELECT * FROM manufacturers WHERE id = ?", (manufacturer_id,))
        updated_manufacturer = cursor.fetchone()
        
        return jsonify({
            'message': 'Manufacturer updated successfully',
            'manufacturer': {
                'id': updated_manufacturer[0],
                'name': updated_manufacturer[1],
                'website_url': updated_manufacturer[2],
                'logo_url': updated_manufacturer[3],
                'description': updated_manufacturer[4],
                'country': updated_manufacturer[5],
                'established_year': updated_manufacturer[6],
                'is_active': bool(updated_manufacturer[7]),
                'created_at': updated_manufacturer[8],
                'updated_at': updated_manufacturer[9]
            },
            'updated_by': current_user['email']
        }), 200
        
    except Exception as e:
        db.get_connection().rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/manufacturers/<int:manufacturer_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_manufacturer_admin(current_user, manufacturer_id):
    """Delete manufacturer and all associated data (admin only)"""
    try:
        db = get_database()
        cursor = db.get_connection().cursor()
        
        # Check if manufacturer exists and get statistics
        cursor.execute("SELECT name FROM manufacturers WHERE id = ?", (manufacturer_id,))
        manufacturer = cursor.fetchone()
        if not manufacturer:
            return jsonify({'error': 'Manufacturer not found'}), 404
        
        manufacturer_name = manufacturer[0]
        
        # Get counts for reporting
        cursor.execute("SELECT COUNT(*) FROM arrows WHERE manufacturer_id = ?", (manufacturer_id,))
        arrow_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM equipment WHERE manufacturer_id = ?", (manufacturer_id,))
        equipment_count = cursor.fetchone()[0]
        
        # Get arrow IDs for spine specifications cleanup
        cursor.execute("SELECT id FROM arrows WHERE manufacturer_id = ?", (manufacturer_id,))
        arrow_ids = [row[0] for row in cursor.fetchall()]
        
        # Delete spine specifications first (foreign key constraint)
        deleted_specs = 0
        if arrow_ids:
            placeholders = ','.join('?' * len(arrow_ids))
            cursor.execute(f"DELETE FROM spine_specifications WHERE arrow_id IN ({placeholders})", arrow_ids)
            deleted_specs = cursor.rowcount
        
        # Delete arrows
        cursor.execute("DELETE FROM arrows WHERE manufacturer_id = ?", (manufacturer_id,))
        deleted_arrows = cursor.rowcount
        
        # Delete equipment
        cursor.execute("DELETE FROM equipment WHERE manufacturer_id = ?", (manufacturer_id,))
        deleted_equipment = cursor.rowcount
        
        # Delete equipment category mappings (CASCADE should handle this, but explicit is better)
        cursor.execute("DELETE FROM manufacturer_equipment_categories WHERE manufacturer_id = ?", (manufacturer_id,))
        deleted_categories = cursor.rowcount
        
        # Finally, delete the manufacturer
        cursor.execute("DELETE FROM manufacturers WHERE id = ?", (manufacturer_id,))
        
        db.get_connection().commit()
        
        return jsonify({
            'message': f'Successfully deleted manufacturer "{manufacturer_name}" and all associated data',
            'deleted_arrows': deleted_arrows,
            'deleted_equipment': deleted_equipment,
            'deleted_spine_specifications': deleted_specs,
            'deleted_category_mappings': deleted_categories,
            'manufacturer_name': manufacturer_name,
            'deleted_by': current_user['email']
        }), 200
        
    except Exception as e:
        db.get_connection().rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/manufacturers', methods=['POST'])
@token_required
@admin_required
def create_manufacturer_admin(current_user):
    """Create a new manufacturer (admin only)"""
    try:
        data = request.get_json()
        
        if not data or 'name' not in data:
            return jsonify({'error': 'Manufacturer name is required'}), 400
        
        manufacturer_name = data['name'].strip()
        if not manufacturer_name:
            return jsonify({'error': 'Manufacturer name cannot be empty'}), 400
        
        db = get_database()
        cursor = db.get_connection().cursor()
        
        # Check if manufacturer already exists (case insensitive)
        cursor.execute("SELECT COUNT(*) FROM manufacturers WHERE LOWER(name) = LOWER(?)", (manufacturer_name,))
        if cursor.fetchone()[0] > 0:
            return jsonify({'error': 'A manufacturer with this name already exists'}), 409
        
        # Create manufacturer record
        cursor.execute("""
            INSERT INTO manufacturers 
            (name, website_url, logo_url, description, country, established_year, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            manufacturer_name,
            data.get('website_url'),
            data.get('logo_url'),
            data.get('description'),
            data.get('country'),
            data.get('established_year'),
            data.get('is_active', True)
        ))
        
        manufacturer_id = cursor.lastrowid
        
        # Set up default equipment and bow category mappings
        all_categories = [
            'arrows', 'strings', 'sights', 'stabilizers', 'arrow_rests', 'weights',
            'compound_bows', 'recurve_risers', 'recurve_limbs', 'traditional_risers', 
            'traditional_limbs', 'longbows'
        ]
        default_supported_categories = data.get('equipment_categories', ['arrows'])  # Default to arrows only
        
        for category in all_categories:
            is_supported = category in default_supported_categories
            cursor.execute("""
                INSERT INTO manufacturer_equipment_categories 
                (manufacturer_id, category_name, is_supported, notes)
                VALUES (?, ?, ?, ?)
            """, (manufacturer_id, category, is_supported, 'Manually configured' if is_supported else ''))
        
        db.get_connection().commit()
        
        # Get the created manufacturer with all data
        cursor.execute("SELECT * FROM manufacturers WHERE id = ?", (manufacturer_id,))
        created_manufacturer = cursor.fetchone()
        
        return jsonify({
            'message': f'Successfully created manufacturer "{manufacturer_name}"',
            'manufacturer': {
                'id': created_manufacturer[0],
                'name': created_manufacturer[1],
                'website_url': created_manufacturer[2],
                'logo_url': created_manufacturer[3],
                'description': created_manufacturer[4],
                'country': created_manufacturer[5],
                'established_year': created_manufacturer[6],
                'is_active': bool(created_manufacturer[7]),
                'created_at': created_manufacturer[8],
                'updated_at': created_manufacturer[9]
            },
            'created_by': current_user['email']
        }), 201
        
    except Exception as e:
        db.get_connection().rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/manufacturers/<int:manufacturer_id>/equipment-categories', methods=['GET'])
@token_required
@admin_required
def get_manufacturer_equipment_categories(current_user, manufacturer_id):
    """Get equipment categories for a manufacturer (admin only)"""
    try:
        db = get_database()
        cursor = db.get_connection().cursor()
        
        # Check if manufacturer exists
        cursor.execute("SELECT name FROM manufacturers WHERE id = ?", (manufacturer_id,))
        manufacturer = cursor.fetchone()
        if not manufacturer:
            return jsonify({'error': 'Manufacturer not found'}), 404
        
        # Get equipment categories
        cursor.execute("""
            SELECT category_name, is_supported, notes, created_at
            FROM manufacturer_equipment_categories 
            WHERE manufacturer_id = ?
            ORDER BY category_name
        """, (manufacturer_id,))
        
        categories = []
        for row in cursor.fetchall():
            categories.append({
                'category_name': row[0],
                'is_supported': bool(row[1]),
                'notes': row[2],
                'created_at': row[3]
            })
        
        return jsonify({
            'manufacturer_id': manufacturer_id,
            'manufacturer_name': manufacturer[0],
            'equipment_categories': categories
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/manufacturers/<int:manufacturer_id>/equipment-categories', methods=['PUT'])
@token_required
@admin_required
def update_manufacturer_equipment_categories(current_user, manufacturer_id):
    """Update equipment categories for a manufacturer (admin only)"""
    try:
        data = request.get_json()
        
        if not data or 'categories' not in data:
            return jsonify({'error': 'Categories data is required'}), 400
        
        db = get_database()
        cursor = db.get_connection().cursor()
        
        # Check if manufacturer exists
        cursor.execute("SELECT name FROM manufacturers WHERE id = ?", (manufacturer_id,))
        manufacturer = cursor.fetchone()
        if not manufacturer:
            return jsonify({'error': 'Manufacturer not found'}), 404
        
        # Update each category
        updated_categories = []
        for category_data in data['categories']:
            category_name = category_data.get('category_name')
            is_supported = category_data.get('is_supported', False)
            notes = category_data.get('notes', '')
            
            if not category_name:
                continue
            
            # Update or insert category mapping
            cursor.execute("""
                INSERT OR REPLACE INTO manufacturer_equipment_categories 
                (manufacturer_id, category_name, is_supported, notes)
                VALUES (?, ?, ?, ?)
            """, (manufacturer_id, category_name, is_supported, notes))
            
            updated_categories.append({
                'category_name': category_name,
                'is_supported': is_supported,
                'notes': notes
            })
        
        db.get_connection().commit()
        
        return jsonify({
            'message': f'Successfully updated equipment categories for {manufacturer[0]}',
            'manufacturer_id': manufacturer_id,
            'manufacturer_name': manufacturer[0],
            'updated_categories': updated_categories,
            'updated_by': current_user['email']
        }), 200
        
    except Exception as e:
        db.get_connection().rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/equipment-categories', methods=['GET'])
@token_required
@admin_required
def get_available_equipment_categories(current_user):
    """Get all available equipment categories (admin only)"""
    try:
        # Return all equipment and bow categories
        categories = [
            # Equipment Categories
            {
                'name': 'arrows',
                'display_name': 'Arrows',
                'description': 'Arrow shafts and complete arrows',
                'icon': 'fas fa-crosshairs'
            },
            {
                'name': 'strings',
                'display_name': 'Strings & Cables',
                'description': 'Bow strings, cables, and serving materials',
                'icon': 'fas fa-grip-lines'
            },
            {
                'name': 'sights',
                'display_name': 'Sights',
                'description': 'Bow sights, pins, and aiming systems',
                'icon': 'fas fa-bullseye'
            },
            {
                'name': 'stabilizers',
                'display_name': 'Stabilizers',
                'description': 'Front stabilizers, side rods, and balance systems',
                'icon': 'fas fa-balance-scale'
            },
            {
                'name': 'arrow_rests',
                'display_name': 'Arrow Rests',
                'description': 'Drop-away, containment, and launcher rests',
                'icon': 'fas fa-hand-paper'
            },
            {
                'name': 'weights',
                'display_name': 'Weights',
                'description': 'Stabilizer weights, balance bars, and dampeners',
                'icon': 'fas fa-weight-hanging'
            },
            # Bow Categories
            {
                'name': 'compound_bows',
                'display_name': 'Compound Bows',
                'description': 'Complete compound bow manufacturing',
                'icon': 'fas fa-bow-arrow'
            },
            {
                'name': 'recurve_risers',
                'display_name': 'Recurve Risers',
                'description': 'Recurve bow riser manufacturing',
                'icon': 'fas fa-mountain'
            },
            {
                'name': 'recurve_limbs',
                'display_name': 'Recurve Limbs',
                'description': 'Recurve bow limb manufacturing',
                'icon': 'fas fa-bezier-curve'
            },
            {
                'name': 'traditional_risers',
                'display_name': 'Traditional Risers',
                'description': 'Traditional bow riser manufacturing',
                'icon': 'fas fa-tree'
            },
            {
                'name': 'traditional_limbs',
                'display_name': 'Traditional Limbs',
                'description': 'Traditional bow limb manufacturing',
                'icon': 'fas fa-leaf'
            },
            {
                'name': 'longbows',
                'display_name': 'Longbows',
                'description': 'Complete longbow manufacturing',
                'icon': 'fas fa-archway'
            }
        ]
        
        return jsonify({
            'categories': categories,
            'total_count': len(categories)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== EQUIPMENT MANAGEMENT API ENDPOINTS =====

@app.route('/api/equipment/categories', methods=['GET'])
def get_equipment_categories():
    """Get all equipment categories with their schemas"""
    try:
        return jsonify([
            {'name': 'String', 'icon': 'fas fa-link'},
            {'name': 'Sight', 'icon': 'fas fa-crosshairs'},
            {'name': 'Scope', 'icon': 'fas fa-search'},
            {'name': 'Stabilizer', 'icon': 'fas fa-balance-scale'},
            {'name': 'Arrow Rest', 'icon': 'fas fa-hand-paper'},
            {'name': 'Plunger', 'icon': 'fas fa-bullseye'},
            {'name': 'Weight', 'icon': 'fas fa-weight-hanging'},
            {'name': 'Other', 'icon': 'fas fa-cog'}
        ]), 200
        
    except Exception as e:
        print(f"Error getting equipment categories: {e}")
        return jsonify({'error': 'Failed to get equipment categories'}), 500

@app.route('/api/equipment/search', methods=['GET'])
def search_equipment():
    """Search equipment by category, manufacturer, or keywords"""
    try:
        category = request.args.get('category')
        manufacturer = request.args.get('manufacturer') 
        keywords = request.args.get('keywords', '')
        
        db = get_database()
        cursor = db.get_connection().cursor()
        
        query = '''
            SELECT e.*, ec.name as category_name, ec.icon as category_icon
            FROM equipment e
            JOIN equipment_categories ec ON e.category_id = ec.id
            WHERE 1=1
        '''
        params = []
        
        if category:
            query += ' AND ec.name = ?'
            params.append(category)
            
        if manufacturer:
            query += ' AND e.manufacturer LIKE ?'
            params.append(f'%{manufacturer}%')
            
        if keywords:
            query += ' AND (e.model_name LIKE ? OR e.description LIKE ?)'
            params.extend([f'%{keywords}%', f'%{keywords}%'])
        
        query += ' ORDER BY e.manufacturer, e.model_name'
        
        cursor.execute(query, params)
        equipment = []
        for row in cursor.fetchall():
            item = dict(row)
            # Parse JSON specifications
            if item['specifications']:
                try:
                    item['specifications'] = json.loads(item['specifications'])
                except json.JSONDecodeError:
                    item['specifications'] = {}
            if item['compatibility_rules']:
                try:
                    item['compatibility_rules'] = json.loads(item['compatibility_rules'])
                except json.JSONDecodeError:
                    item['compatibility_rules'] = {}
            equipment.append(item)
        
        return jsonify(equipment), 200
        
    except Exception as e:
        print(f"Error searching equipment: {e}")
        return jsonify({'error': 'Failed to search equipment'}), 500

@app.route('/api/equipment/form-schema/<category>', methods=['GET'])
def get_equipment_form_schema(category):
    """Get form schema for a specific equipment category"""
    try:
        # Use get_database() to get the correct arrow database connection
        db = get_database()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Get field standards for the category
        cursor.execute('''
            SELECT field_name, field_type, label, unit, required,
                   validation_rules, field_options, default_value, help_text, display_order
            FROM equipment_field_standards 
            WHERE category_name = ?
            ORDER BY display_order, field_name
        ''', (category,))
        
        fields = []
        for row in cursor.fetchall():
            field_data = {
                'name': row[0],      # field_name
                'type': row[1],      # field_type
                'label': row[2],     # label
                'unit': row[3],      # unit
                'required': bool(row[4]),  # required
                'order': row[9]      # display_order
            }
            
            # Parse JSON fields
            if row[5]:  # validation_rules
                try:
                    field_data['validation'] = json.loads(row[5])
                except json.JSONDecodeError:
                    pass
                    
            if row[6]:  # field_options
                try:
                    field_data['options'] = json.loads(row[6])
                except json.JSONDecodeError:
                    field_data['options'] = []
                    
            if row[7]:  # default_value
                field_data['default'] = row[7]
                
            if row[8]:  # help_text
                field_data['help'] = row[8]
                
            fields.append(field_data)
        
        return jsonify({
            'category': category,
            'fields': fields
        }), 200
        
    except Exception as e:
        print(f"Error getting form schema for {category}: {e}")
        return jsonify({'error': f'Failed to get form schema for {category}'}), 500

@app.route('/api/equipment/manufacturers/suggest', methods=['GET'])
def suggest_equipment_manufacturers():
    """Get smart manufacturer suggestions for autocomplete with fuzzy matching"""
    try:
        query = request.args.get('q', '')
        category = request.args.get('category', '')
        limit = int(request.args.get('limit', 20))
        
        # Check if user is authenticated for pending manufacturer access
        current_user = None
        try:
            from auth import validate_jwt_token
            token = request.headers.get('Authorization')
            if token and token.startswith('Bearer '):
                token = token[7:]  # Remove 'Bearer ' prefix
                current_user = validate_jwt_token(token)
        except:
            pass  # Not authenticated, continue without pending manufacturers
        
        # Use get_database() to get the correct arrow database connection
        db = get_database()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Get all manufacturers from database
        cursor.execute('SELECT id, name, website_url, country FROM manufacturers ORDER BY name')
        all_manufacturers = []
        for row in cursor.fetchall():
            all_manufacturers.append({
                'id': row[0],
                'name': row[1],
                'website': row[2],
                'country': row[3] or 'Unknown'
            })
        
        conn.close()
        
        # Add user's pending manufacturers if authenticated
        pending_manufacturers = []
        if current_user:
            try:
                from user_database import UserDatabase
                user_db = UserDatabase()
                user_conn = user_db.get_connection()
                user_cursor = user_conn.cursor()
                
                # Get user's pending manufacturers (including those they didn't create)
                user_cursor.execute('''
                    SELECT DISTINCT pm.name, pm.category_context, pm.usage_count, pm.status
                    FROM pending_manufacturers pm
                    JOIN user_pending_manufacturers upm ON pm.id = upm.pending_manufacturer_id
                    WHERE upm.user_id = ? AND pm.status = 'pending'
                    ORDER BY upm.last_used DESC
                ''', (current_user['id'],))
                
                for row in user_cursor.fetchall():
                    pending_manufacturers.append({
                        'name': row['name'],
                        'website': None,
                        'country': 'Unknown',
                        'isPending': True,
                        'usageCount': row['usage_count'],
                        'categories': json.loads(row['category_context'] or '[]')
                    })
                
                user_conn.close()
                
            except Exception as e:
                print(f"Warning: Could not get pending manufacturers for user {current_user.get('id', 'unknown')}: {e}")
        
        # Use smart manufacturer matching for suggestions
        from manufacturer_matcher import ManufacturerMatcher
        matcher = ManufacturerMatcher()
        
        # Get intelligent suggestions from approved manufacturers
        suggestions = matcher.get_manufacturer_suggestions(
            query, all_manufacturers, category, limit // 2  # Leave room for pending manufacturers
        )
        
        # Format approved manufacturers
        manufacturers = []
        for manufacturer in suggestions:
            manufacturers.append({
                'name': manufacturer['name'],
                'website': manufacturer.get('website'),
                'country': manufacturer.get('country', 'Unknown'),
                'isPending': False
            })
        
        # Add matching pending manufacturers for the user
        if pending_manufacturers:
            query_lower = query.lower()
            matching_pending = []
            
            for pending in pending_manufacturers:
                # Include if no query or if query matches name
                if not query or query_lower in pending['name'].lower():
                    # Filter by category if specified
                    if not category or category in pending.get('categories', []):
                        matching_pending.append(pending)
            
            # Sort pending by usage count (most used first)
            matching_pending.sort(key=lambda x: x.get('usageCount', 0), reverse=True)
            
            # Add pending manufacturers to the beginning of results (prioritize for user)
            manufacturers = matching_pending[:limit//3] + manufacturers
            manufacturers = manufacturers[:limit]  # Respect total limit
        
        return jsonify({'manufacturers': manufacturers}), 200
        
    except Exception as e:
        print(f"Error getting smart manufacturer suggestions: {e}")
        # Fallback to basic suggestions if smart matching fails
        try:
            db = get_database()
            conn = db.get_connection()
            cursor = conn.cursor()
            
            # Basic fallback query
            if query:
                cursor.execute('''
                    SELECT DISTINCT name, website_url, country 
                    FROM manufacturers 
                    WHERE LOWER(name) LIKE ? 
                    ORDER BY name LIMIT ?
                ''', (f'%{query.lower()}%', limit))
            else:
                cursor.execute('SELECT DISTINCT name, website_url, country FROM manufacturers ORDER BY name LIMIT ?', (limit,))
            
            manufacturers = []
            for row in cursor.fetchall():
                manufacturers.append({
                    'name': row[0],
                    'website': row[1],
                    'country': row[2] or 'Unknown'
                })
            
            conn.close()
            return jsonify({'manufacturers': manufacturers}), 200
            
        except Exception as fallback_error:
            print(f"Fallback manufacturer suggestions also failed: {fallback_error}")
            return jsonify({'error': 'Failed to get manufacturer suggestions'}), 500

@app.route('/api/equipment/models/suggest', methods=['GET'])
def suggest_equipment_models():
    """Get smart model name suggestions based on manufacturer and category"""
    try:
        manufacturer = request.args.get('manufacturer', '')
        category = request.args.get('category', '')
        query = request.args.get('q', '')
        limit = int(request.args.get('limit', 10))
        
        if not manufacturer or not category:
            return jsonify({'error': 'manufacturer and category parameters are required'}), 400
        
        from equipment_learning_manager import EquipmentLearningManager
        learning = EquipmentLearningManager()
        
        # Get model suggestions
        suggestions = learning.get_model_suggestions(manufacturer, category, query, limit)
        
        return jsonify({
            'models': suggestions,
            'manufacturer': manufacturer,
            'category': category
        }), 200
        
    except Exception as e:
        print(f"Error getting model suggestions: {e}")
        return jsonify({'error': 'Failed to get model suggestions'}), 500

@app.route('/api/admin/pending-manufacturers', methods=['GET'])
@token_required
def get_pending_manufacturers(current_user):
    """Get pending manufacturers for admin approval"""
    try:
        # Check admin status
        if not current_user.get('is_admin'):
            return jsonify({'error': 'Admin access required'}), 403
        
        status = request.args.get('status', 'pending')
        limit = int(request.args.get('limit', 50))
        
        from equipment_learning_manager import EquipmentLearningManager
        learning = EquipmentLearningManager()
        
        pending_manufacturers = learning.get_pending_manufacturers(status, limit)
        
        return jsonify({
            'pending_manufacturers': pending_manufacturers,
            'status': status,
            'count': len(pending_manufacturers)
        }), 200
        
    except Exception as e:
        print(f"Error getting pending manufacturers: {e}")
        return jsonify({'error': 'Failed to get pending manufacturers'}), 500

@app.route('/api/admin/manufacturers/<int:pending_id>/approve', methods=['PUT'])
@token_required
def approve_manufacturer(current_user, pending_id):
    """Approve a pending manufacturer"""
    try:
        # Check admin status
        if not current_user.get('is_admin'):
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json() or {}
        admin_notes = data.get('admin_notes', '')
        
        from equipment_learning_manager import EquipmentLearningManager
        learning = EquipmentLearningManager()
        
        success = learning.approve_manufacturer(pending_id, admin_notes)
        
        if success:
            return jsonify({'message': 'Manufacturer approved successfully'}), 200
        else:
            return jsonify({'error': 'Failed to approve manufacturer'}), 400
        
    except Exception as e:
        print(f"Error approving manufacturer: {e}")
        return jsonify({'error': 'Failed to approve manufacturer'}), 500

@app.route('/api/admin/manufacturers/<int:pending_id>/reject', methods=['PUT'])
@token_required
def reject_manufacturer(current_user, pending_id):
    """Reject a pending manufacturer"""
    try:
        # Check admin status
        if not current_user.get('is_admin'):
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json() or {}
        admin_notes = data.get('admin_notes', '')
        
        from equipment_learning_manager import EquipmentLearningManager
        learning = EquipmentLearningManager()
        
        success = learning.reject_manufacturer(pending_id, admin_notes)
        
        if success:
            return jsonify({'message': 'Manufacturer rejected'}), 200
        else:
            return jsonify({'error': 'Failed to reject manufacturer'}), 400
        
    except Exception as e:
        print(f"Error rejecting manufacturer: {e}")
        return jsonify({'error': 'Failed to reject manufacturer'}), 500

@app.route('/api/admin/manufacturers/pending', methods=['GET'])
@token_required
def get_pending_manufacturers_list(current_user):
    """Get pending manufacturers for admin review"""
    try:
        # Check admin status
        if not current_user.get('is_admin'):
            return jsonify({'error': 'Admin access required'}), 403
        
        status = request.args.get('status', 'pending')
        limit = int(request.args.get('limit', 50))
        
        from equipment_learning_manager import EquipmentLearningManager
        learning = EquipmentLearningManager()
        
        pending_manufacturers = learning.get_pending_manufacturers(status, limit)
        
        return jsonify({
            'pending_manufacturers': pending_manufacturers,
            'total_count': len(pending_manufacturers)
        }), 200
        
    except Exception as e:
        print(f"Error getting pending manufacturers: {e}")
        return jsonify({'error': 'Failed to get pending manufacturers'}), 500

@app.route('/api/equipment/usage-analytics', methods=['GET'])
@token_required
def get_equipment_usage_analytics(current_user):
    """Get equipment usage analytics"""
    try:
        category = request.args.get('category')
        days = int(request.args.get('days', 30))
        
        from equipment_learning_manager import EquipmentLearningManager
        learning = EquipmentLearningManager()
        
        analytics = learning.get_equipment_usage_analytics(category, days)
        
        return jsonify(analytics), 200
        
    except Exception as e:
        print(f"Error getting usage analytics: {e}")
        return jsonify({'error': 'Failed to get usage analytics'}), 500

@app.route('/api/bow-setups/<int:setup_id>/equipment', methods=['GET'])
@token_required
def get_bow_equipment(current_user, setup_id):
    """Get all equipment for a bow setup (supports both custom and pre-chosen equipment)"""
    try:
        from user_database import UserDatabase
        user_db = UserDatabase()
        conn = user_db.get_connection()
        cursor = conn.cursor()
        
        # Verify the setup belongs to the current user
        cursor.execute('SELECT user_id FROM bow_setups WHERE id = ?', (setup_id,))
        setup = cursor.fetchone()
        if not setup or setup['user_id'] != current_user['id']:
            conn.close()
            return jsonify({'error': 'Setup not found or access denied'}), 404
        
        # Get all equipment for this bow setup
        cursor.execute('''
            SELECT * FROM bow_equipment 
            WHERE bow_setup_id = ? AND is_active = 1
            ORDER BY category_name, manufacturer_name, model_name
        ''', (setup_id,))
        
        bow_equipment_rows = cursor.fetchall()
        equipment = []
        
        for be_row in bow_equipment_rows:
            equipment_item = dict(be_row)
            
            # For custom equipment (is_custom = True), use the stored data directly
            if equipment_item.get('is_custom'):
                # Custom equipment - use stored data
                equipment_item['manufacturer'] = equipment_item['manufacturer_name']
                equipment_item['model_name'] = equipment_item['model_name']
                equipment_item['category_name'] = equipment_item['category_name']
                
                # Add category icon
                category_icons = {
                    'String': 'fas fa-link',
                    'Sight': 'fas fa-crosshairs', 
                    'Stabilizer': 'fas fa-balance-scale',
                    'Arrow Rest': 'fas fa-hand-paper',
                    'Weight': 'fas fa-weight-hanging'
                }
                equipment_item['category_icon'] = category_icons.get(equipment_item['category_name'], 'fas fa-cog')
                
                # Parse specifications JSON
                if equipment_item.get('custom_specifications'):
                    try:
                        equipment_item['specifications'] = json.loads(equipment_item['custom_specifications'])
                    except json.JSONDecodeError:
                        equipment_item['specifications'] = {}
                else:
                    equipment_item['specifications'] = {}
                    
            else:
                # Legacy pre-chosen equipment - get details from arrow database
                if equipment_item.get('equipment_id'):
                    try:
                        arrow_db = get_database()
                        arrow_cursor = arrow_db.get_connection().cursor()
                        
                        arrow_cursor.execute('''
                            SELECT e.*, ec.name as category_name, ec.icon as category_icon
                            FROM equipment e
                            JOIN equipment_categories ec ON e.category_id = ec.id
                            WHERE e.id = ?
                        ''', (equipment_item['equipment_id'],))
                        
                        equipment_row = arrow_cursor.fetchone()
                        if equipment_row:
                            equipment_data = dict(equipment_row)
                            # Merge with bow_equipment data, prioritizing bow_equipment values
                            for key, value in equipment_data.items():
                                if key not in equipment_item or equipment_item[key] is None:
                                    equipment_item[key] = value
                            
                            # Parse JSON fields
                            for field in ['specifications', 'custom_specifications']:
                                if equipment_item.get(field):
                                    try:
                                        equipment_item[field] = json.loads(equipment_item[field])
                                    except json.JSONDecodeError:
                                        equipment_item[field] = {}
                        
                        arrow_cursor.close()
                    except Exception as e:
                        print(f"Warning: Could not get legacy equipment details: {e}")
            
            # Clean up the response
            equipment_item['id'] = equipment_item['id']  # bow_equipment ID
            equipment_item['bow_equipment_id'] = equipment_item['id']
            
            equipment.append(equipment_item)
        
        conn.close()
        return jsonify({'equipment': equipment}), 200
        
    except Exception as e:
        print(f"Error getting bow equipment: {e}")
        return jsonify({'error': 'Failed to get bow equipment'}), 500

@app.route('/api/bow-setups/<int:setup_id>/equipment', methods=['POST'])
@token_required
def add_bow_equipment(current_user, setup_id):
    """Add custom equipment to a bow setup"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Equipment data is required'}), 400
        
        # Validate required fields for custom equipment
        required_fields = ['manufacturer_name', 'model_name', 'category_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        from user_database import UserDatabase
        user_db = UserDatabase()
        conn = user_db.get_connection()
        cursor = conn.cursor()
        
        # Verify the setup belongs to the current user
        cursor.execute('SELECT user_id FROM bow_setups WHERE id = ?', (setup_id,))
        setup = cursor.fetchone()
        if not setup or setup['user_id'] != current_user['id']:
            conn.close()
            return jsonify({'error': 'Setup not found or access denied'}), 404
        
        # Check for duplicate equipment (same manufacturer, model, category)
        cursor.execute('''
            SELECT id FROM bow_equipment 
            WHERE bow_setup_id = ? AND manufacturer_name = ? AND model_name = ? 
            AND category_name = ? AND is_active = 1
        ''', (setup_id, data['manufacturer_name'], data['model_name'], data['category_name']))
        if cursor.fetchone():
            conn.close()
            return jsonify({'error': 'This equipment is already added to the setup'}), 409
        
        # Convert weight to grams if provided in ounces
        weight_grams = data.get('weight_grams')
        if not weight_grams and data.get('weight_ounces'):
            weight_grams = float(data['weight_ounces']) * 28.3495  # Convert ounces to grams
        
        # Check if manufacturer exists in database (for linking existing ones only)
        equipment_id = None
        manufacturer_id = None
        linked_manufacturer_name = data['manufacturer_name']  # Always preserve user input
        
        try:
            arrow_db = ArrowDatabase()
            arrow_conn = arrow_db.get_connection()
            arrow_cursor = arrow_conn.cursor()
            
            # Check for exact manufacturer match first
            arrow_cursor.execute('SELECT id FROM manufacturers WHERE LOWER(name) = LOWER(?)', 
                               (data['manufacturer_name'],))
            exact_match = arrow_cursor.fetchone()
            
            if exact_match:
                # Exact match found - use existing manufacturer
                manufacturer_id = exact_match['id']
                print(f"✅ Exact manufacturer match found for: '{data['manufacturer_name']}'")
            else:
                # No exact match - this will become a pending manufacturer
                # Preserve the user's exact input without any smart matching alterations
                print(f"📝 New manufacturer: '{data['manufacturer_name']}' - will be saved as pending")
            
            arrow_conn.close()
        except Exception as e:
            print(f"Warning: Manufacturer lookup failed: {e}")
            manufacturer_id = None
        
        # Add custom equipment to bow setup
        cursor.execute('''
            INSERT INTO bow_equipment (
                bow_setup_id, equipment_id, manufacturer_name, model_name, category_name,
                weight_grams, description, image_url, installation_notes, 
                custom_specifications, is_custom
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            setup_id,
            equipment_id,  # Will be NULL for custom equipment (can link later)
            linked_manufacturer_name,  # Use smart-matched manufacturer name
            data['model_name'],
            data['category_name'],
            weight_grams,
            data.get('description', ''),
            data.get('image_url', ''),
            data.get('installation_notes', ''),
            json.dumps(data.get('specifications', {})),
            True  # is_custom = True
        ))
        
        bow_equipment_id = cursor.lastrowid
        conn.commit()
        
        # Auto-learn from this equipment entry
        try:
            from equipment_learning_manager import EquipmentLearningManager
            learning = EquipmentLearningManager()
            learning_info = learning.learn_equipment_entry(
                linked_manufacturer_name,
                data['model_name'], 
                data['category_name'],
                current_user['id']
            )
            
            if learning_info['new_manufacturer']:
                print(f"📚 New manufacturer learned: '{linked_manufacturer_name}' (pending approval)")
            if learning_info['new_model']:
                print(f"📚 New model learned: '{data['model_name']}' for {linked_manufacturer_name}")
            else:
                print(f"📊 Model usage updated: '{data['model_name']}' used {learning_info['model_usage_count']} times")
                
        except Exception as e:
            print(f"Warning: Auto-learning failed: {e}")
        
        # Return the added equipment
        cursor.execute('''
            SELECT * FROM bow_equipment WHERE id = ?
        ''', (bow_equipment_id,))
        
        result = dict(cursor.fetchone())
        
        # Parse JSON fields
        if result.get('custom_specifications'):
            try:
                result['custom_specifications'] = json.loads(result['custom_specifications'])
            except json.JSONDecodeError:
                result['custom_specifications'] = {}
        
        conn.close()
        return jsonify(result), 201
        
    except Exception as e:
        print(f"Error adding custom bow equipment: {e}")
        return jsonify({'error': 'Failed to add equipment'}), 500

@app.route('/api/bow-setups/<int:setup_id>/equipment/<int:equipment_id>', methods=['PUT'])
@token_required
def update_bow_equipment(current_user, setup_id, equipment_id):
    """Update custom equipment configuration in a bow setup with change logging"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        from user_database import UserDatabase
        from change_log_service import ChangeLogService
        
        user_db = UserDatabase()
        change_service = ChangeLogService()
        conn = user_db.get_connection()
        cursor = conn.cursor()
        
        # Get current equipment data for change logging
        cursor.execute('''
            SELECT be.* FROM bow_equipment be
            JOIN bow_setups bs ON be.bow_setup_id = bs.id
            WHERE be.bow_setup_id = ? AND be.id = ? 
            AND bs.user_id = ? AND be.is_active = 1
        ''', (setup_id, equipment_id, current_user['id']))
        
        bow_equipment = cursor.fetchone()
        if not bow_equipment:
            conn.close()
            return jsonify({'error': 'Equipment not found or access denied'}), 404
        
        # Store old data for change logging
        old_data = dict(bow_equipment)
        
        # Update equipment configuration
        updates = []
        params = []
        
        # For custom equipment, allow updating all fields
        if bow_equipment['is_custom']:
            updatable_fields = [
                'manufacturer_name', 'model_name', 'category_name', 'weight_grams',
                'description', 'image_url', 'installation_notes'
            ]
            
            for field in updatable_fields:
                if field in data:
                    updates.append(f'{field} = ?')
                    params.append(data[field])
            
            # Handle specifications separately
            if 'specifications' in data:
                updates.append('custom_specifications = ?')
                params.append(json.dumps(data['specifications']))
        else:
            # For legacy pre-chosen equipment, only allow certain updates
            if 'installation_notes' in data:
                updates.append('installation_notes = ?')
                params.append(data['installation_notes'])
            
            if 'custom_specifications' in data:
                updates.append('custom_specifications = ?')
                params.append(json.dumps(data['custom_specifications']))
        
        if updates:
            params.append(bow_equipment['id'])
            cursor.execute(f'''
                UPDATE bow_equipment SET {', '.join(updates)}
                WHERE id = ?
            ''', params)
            conn.commit()
            
            # Get updated data and log changes
            cursor.execute('SELECT * FROM bow_equipment WHERE id = ?', (equipment_id,))
            new_data = dict(cursor.fetchone())
            
            # Log the changes with reason if provided
            change_reason = data.get('change_reason', 'Equipment settings updated')
            change_log_ids = change_service.log_equipment_field_changes(
                setup_id, equipment_id, current_user['id'],
                old_data, new_data, change_reason
            )
            
            print(f"📝 Logged {len(change_log_ids)} equipment changes for equipment {equipment_id}")
        
        # Return updated equipment
        cursor.execute('''
            SELECT * FROM bow_equipment WHERE id = ?
        ''', (bow_equipment['id'],))
        
        result = dict(cursor.fetchone())
        
        # For custom equipment, format the response properly
        if result.get('is_custom'):
            result['manufacturer'] = result['manufacturer_name']
            result['specifications'] = {}
            
            if result.get('custom_specifications'):
                try:
                    result['specifications'] = json.loads(result['custom_specifications'])
                except json.JSONDecodeError:
                    result['specifications'] = {}
            
            # Add category icon
            category_icons = {
                'String': 'fas fa-link',
                'Sight': 'fas fa-crosshairs', 
                'Stabilizer': 'fas fa-balance-scale',
                'Arrow Rest': 'fas fa-hand-paper',
                'Weight': 'fas fa-weight-hanging'
            }
            result['category_icon'] = category_icons.get(result['category_name'], 'fas fa-cog')
        else:
            # Parse JSON fields for legacy equipment
            for field in ['custom_specifications']:
                if result.get(field):
                    try:
                        result[field] = json.loads(result[field])
                    except json.JSONDecodeError:
                        result[field] = {}
        
        conn.close()
        return jsonify(result), 200
        
    except Exception as e:
        print(f"Error updating bow equipment: {e}")
        return jsonify({'error': 'Failed to update equipment'}), 500

@app.route('/api/bow-setups/<int:setup_id>/equipment/<int:equipment_id>', methods=['DELETE'])
@token_required
def remove_bow_equipment(current_user, setup_id, equipment_id):
    """Soft delete equipment from a bow setup with enhanced tracking"""
    try:
        from user_database import UserDatabase
        from change_log_service import ChangeLogService
        
        user_db = UserDatabase()
        change_service = ChangeLogService()
        conn = user_db.get_connection()
        cursor = conn.cursor()
        
        # Get equipment details for logging before deletion
        cursor.execute('''
            SELECT be.*, bs.user_id 
            FROM bow_equipment be
            JOIN bow_setups bs ON be.bow_setup_id = bs.id
            WHERE be.bow_setup_id = ? AND be.id = ? 
            AND bs.user_id = ? AND be.is_active = 1
        ''', (setup_id, equipment_id, current_user['id']))
        
        equipment_row = cursor.fetchone()
        if not equipment_row:
            conn.close()
            return jsonify({'error': 'Equipment not found or access denied'}), 404
        
        # Convert row to dict for easier access
        equipment = dict(equipment_row) if hasattr(equipment_row, 'keys') else {
            'id': equipment_row[0] if len(equipment_row) > 0 else None,
            'manufacturer_name': equipment_row[1] if len(equipment_row) > 1 else None,
            'model_name': equipment_row[2] if len(equipment_row) > 2 else None,
            'category_name': equipment_row[3] if len(equipment_row) > 3 else None,
        }
        
        if not equipment.get('id'):
            conn.close()
            return jsonify({'error': 'Invalid equipment data'}), 400
        
        # Enhanced soft delete with tracking
        cursor.execute('''
            UPDATE bow_equipment 
            SET is_active = 0, 
                deleted_at = CURRENT_TIMESTAMP,
                deleted_by = ?
            WHERE id = ?
        ''', (current_user['id'], equipment['id']))
        
        # Log the equipment removal
        equipment_name = f"{equipment['manufacturer_name'] or 'Unknown'} {equipment['model_name'] or 'Equipment'}"
        category = equipment['category_name'] or 'Equipment'
        
        change_service.log_equipment_change(
            bow_setup_id=setup_id,
            equipment_id=equipment['id'],
            user_id=current_user['id'],
            change_type='remove',
            field_name=None,
            old_value=None,
            new_value=None,
            change_description=f"Removed {category}: {equipment_name}",
            change_reason=f"Equipment marked as deleted (can be restored)"
        )
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': 'Equipment removed successfully',
            'equipment_name': equipment_name,
            'can_restore': True,
            'deleted_at': 'now'
        }), 200
        
    except Exception as e:
        print(f"Error removing bow equipment: {e}")
        return jsonify({'error': 'Failed to remove equipment'}), 500

@app.route('/api/bow-setups/<int:setup_id>/equipment/<int:equipment_id>/restore', methods=['POST'])
@token_required
def restore_bow_equipment(current_user, setup_id, equipment_id):
    """Restore previously deleted equipment to a bow setup"""
    try:
        from user_database import UserDatabase
        from change_log_service import ChangeLogService
        
        user_db = UserDatabase()
        change_service = ChangeLogService()
        conn = user_db.get_connection()
        cursor = conn.cursor()
        
        # Get deleted equipment details
        cursor.execute('''
            SELECT be.*, bs.user_id 
            FROM bow_equipment be
            JOIN bow_setups bs ON be.bow_setup_id = bs.id
            WHERE be.bow_setup_id = ? AND be.id = ? 
            AND bs.user_id = ? AND be.is_active = 0
        ''', (setup_id, equipment_id, current_user['id']))
        
        equipment = cursor.fetchone()
        if not equipment:
            conn.close()
            return jsonify({'error': 'Deleted equipment not found or access denied'}), 404
        
        # Restore equipment (soft undelete)
        cursor.execute('''
            UPDATE bow_equipment 
            SET is_active = 1, 
                deleted_at = NULL,
                deleted_by = NULL
            WHERE id = ?
        ''', (equipment['id'],))
        
        # Log the equipment restoration
        equipment_name = f"{equipment['manufacturer_name'] or 'Unknown'} {equipment['model_name'] or 'Equipment'}"
        category = equipment['category_name'] or 'Equipment'
        
        change_service.log_equipment_change(
            bow_setup_id=setup_id,
            equipment_id=equipment['id'],
            user_id=current_user['id'],
            change_type='add',  # Restoration counts as re-adding
            field_name=None,
            old_value=None,
            new_value=None,
            change_description=f"Restored {category}: {equipment_name}",
            change_reason=f"Equipment restored from deleted state"
        )
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': 'Equipment restored successfully',
            'equipment_name': equipment_name,
            'restored_at': 'now'
        }), 200
        
    except Exception as e:
        print(f"Error restoring bow equipment: {e}")
        return jsonify({'error': 'Failed to restore equipment'}), 500

@app.route('/api/bow-setups/<int:setup_id>/equipment/deleted', methods=['GET'])
@token_required
def get_deleted_equipment(current_user, setup_id):
    """Get list of deleted equipment for a bow setup that can be restored"""
    try:
        from user_database import UserDatabase
        
        user_db = UserDatabase()
        conn = user_db.get_connection()
        cursor = conn.cursor()
        
        # Verify setup belongs to user
        cursor.execute("SELECT id FROM bow_setups WHERE id = ? AND user_id = ?", (setup_id, current_user['id']))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Setup not found or access denied'}), 404
        
        # Get deleted equipment
        cursor.execute('''
            SELECT be.*, u.email as deleted_by_email
            FROM bow_equipment be
            LEFT JOIN users u ON be.deleted_by = u.id
            WHERE be.bow_setup_id = ? AND be.is_active = 0
            ORDER BY be.deleted_at DESC
        ''', (setup_id,))
        
        deleted_equipment = []
        for row in cursor.fetchall():
            equipment = dict(row)
            # Format timestamps
            if equipment['deleted_at']:
                from datetime import datetime
                try:
                    equipment['deleted_at'] = datetime.fromisoformat(equipment['deleted_at']).isoformat()
                except:
                    pass
            deleted_equipment.append(equipment)
        
        conn.close()
        
        return jsonify({
            'deleted_equipment': deleted_equipment,
            'count': len(deleted_equipment)
        }), 200
        
    except Exception as e:
        print(f"Error getting deleted equipment: {e}")
        return jsonify({'error': 'Failed to get deleted equipment'}), 500

# ===== CHANGE LOG API ENDPOINTS =====

@app.route('/api/bow-setups/<int:setup_id>/change-log', methods=['GET'])
@token_required
def get_setup_change_log(current_user, setup_id):
    """Get change history for a bow setup"""
    try:
        from change_log_service import ChangeLogService
        
        # Get query parameters
        limit = request.args.get('limit', 50, type=int)
        days_back = request.args.get('days_back', type=int)
        
        change_service = ChangeLogService()
        changes = change_service.get_setup_change_history(
            setup_id, current_user['id'], limit, days_back
        )
        
        # Format timestamps for JSON serialization (ensure UTC timezone)
        from datetime import timezone
        for change in changes:
            # SQLite CURRENT_TIMESTAMP is UTC but creates naive datetime objects
            # Mark as UTC before serialization to ensure proper timezone handling
            if change['created_at'].tzinfo is None:
                change['created_at'] = change['created_at'].replace(tzinfo=timezone.utc)
            change['created_at'] = change['created_at'].isoformat()
        
        return jsonify({'changes': changes}), 200
        
    except Exception as e:
        print(f"Error getting setup change log: {e}")
        return jsonify({'error': 'Failed to get change log'}), 500

@app.route('/api/bow-setups/<int:setup_id>/equipment/<int:equipment_id>/change-log', methods=['GET'])
@token_required  
def get_equipment_change_log(current_user, setup_id, equipment_id):
    """Get change history for specific equipment"""
    try:
        from change_log_service import ChangeLogService
        
        limit = request.args.get('limit', 20, type=int)
        
        change_service = ChangeLogService()
        changes = change_service.get_equipment_change_history(
            equipment_id, current_user['id'], limit
        )
        
        # Format timestamps for JSON serialization (ensure UTC timezone)
        from datetime import timezone
        for change in changes:
            # SQLite CURRENT_TIMESTAMP is UTC but creates naive datetime objects
            # Mark as UTC before serialization to ensure proper timezone handling
            if change['created_at'].tzinfo is None:
                change['created_at'] = change['created_at'].replace(tzinfo=timezone.utc)
            change['created_at'] = change['created_at'].isoformat()
        
        return jsonify({'changes': changes}), 200
        
    except Exception as e:
        print(f"Error getting equipment change log: {e}")
        return jsonify({'error': 'Failed to get equipment change log'}), 500

@app.route('/api/bow-setups/<int:setup_id>/change-log/stats', methods=['GET'])
@token_required
def get_setup_change_stats(current_user, setup_id):
    """Get change statistics for a bow setup"""
    try:
        from change_log_service import ChangeLogService
        
        change_service = ChangeLogService()
        stats = change_service.get_change_statistics(setup_id, current_user['id'])
        
        return jsonify(stats), 200
        
    except Exception as e:
        print(f"Error getting change statistics: {e}")
        return jsonify({'error': 'Failed to get change statistics'}), 500

@app.route('/api/bow-setups/<int:setup_id>/change-log/add-note', methods=['POST'])
@token_required
def add_manual_change_note(current_user, setup_id):
    """Add a manual change note for a bow setup"""
    try:
        data = request.get_json()
        if not data or not data.get('description'):
            return jsonify({'error': 'Change description is required'}), 400
        
        from change_log_service import ChangeLogService
        
        change_service = ChangeLogService()
        
        # If equipment_id is provided, log as equipment change, otherwise as setup change
        if data.get('equipment_id'):
            change_log_id = change_service.log_equipment_change(
                setup_id, data['equipment_id'], current_user['id'],
                'modify', None, None, None,
                data['description'], data.get('reason', 'Manual note')
            )
        else:
            change_log_id = change_service.log_setup_change(
                setup_id, current_user['id'], 'setup_modified',
                None, None, None, data['description']
            )
        
        return jsonify({'id': change_log_id, 'message': 'Change note added successfully'}), 201
        
    except Exception as e:
        print(f"Error adding manual change note: {e}")
        return jsonify({'error': 'Failed to add change note'}), 500

# ===== GUIDE WALKTHROUGH API ENDPOINTS =====

@app.route('/api/guides', methods=['GET'])
def get_available_guides():
    """Get list of available guides for walkthrough"""
    guides = [
        {
            'id': 'paper-tuning',
            'name': 'Paper Tuning Guide',
            'description': 'Fine-tune your bow for perfect arrow flight through systematic paper testing',
            'type': 'tuning',
            'difficulty': 'intermediate',
            'estimated_time': 25,
            'total_steps': 8,
            'icon': 'arrows-alt-h',
            'color': 'indigo'
        },
        {
            'id': 'rest-adjustment',
            'name': 'Rest Adjustment',
            'description': 'Optimize arrow rest position for perfect clearance',
            'type': 'tuning',
            'difficulty': 'beginner',
            'estimated_time': 15,
            'total_steps': 6,
            'icon': 'wrench',
            'color': 'yellow'
        },
        {
            'id': 'sight-setup',
            'name': 'Sight Setup & Tuning',
            'description': 'Master bow sight installation and calibration',
            'type': 'setup',
            'difficulty': 'beginner',
            'estimated_time': 20,
            'total_steps': 7,
            'icon': 'bullseye',
            'color': 'purple'
        }
    ]
    return jsonify({'guides': guides})

@app.route('/api/guide-sessions', methods=['POST'])
@token_required
def start_guide_session(current_user):
    """Start a new guide walkthrough session"""
    conn = None
    try:
        data = request.get_json()
        guide_name = data.get('guide_name')
        guide_type = data.get('guide_type')
        bow_setup_id = data.get('bow_setup_id')
        total_steps = data.get('total_steps', 1)
        
        if not guide_name or not guide_type:
            return jsonify({'error': 'Guide name and type are required'}), 400
        
        # Get user database connection
        from user_database import UserDatabase
        user_db = UserDatabase()
        conn = user_db.get_connection()
        cursor = conn.cursor()
        
        # Verify bow setup belongs to user if provided
        if bow_setup_id:
            cursor.execute('SELECT id FROM bow_setups WHERE id = ? AND user_id = ?', 
                         (bow_setup_id, current_user['id']))
            if not cursor.fetchone():
                return jsonify({'error': 'Bow setup not found or access denied'}), 404
        
        # Create new guide session
        cursor.execute('''
            INSERT INTO guide_sessions (user_id, bow_setup_id, guide_name, guide_type, total_steps)
            VALUES (?, ?, ?, ?, ?)
        ''', (current_user['id'], bow_setup_id, guide_name, guide_type, total_steps))
        
        session_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'session_id': session_id,
            'message': 'Guide session started successfully'
        })
        
    except Exception as e:
        if conn:
            conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/guide-sessions/<int:session_id>/steps', methods=['POST'])
@token_required
def record_guide_step(current_user, session_id):
    """Record the result of a guide step"""
    conn = None
    try:
        data = request.get_json()
        step_number = data.get('step_number')
        step_name = data.get('step_name')
        result_type = data.get('result_type')
        result_value = data.get('result_value')
        measurements = data.get('measurements')
        adjustments_made = data.get('adjustments_made')
        notes = data.get('notes')
        
        if not step_number or not step_name:
            return jsonify({'error': 'Step number and name are required'}), 400
        
        # Get user database connection
        from user_database import UserDatabase
        user_db = UserDatabase()
        conn = user_db.get_connection()
        cursor = conn.cursor()
        
        # Verify session belongs to user
        cursor.execute('SELECT id FROM guide_sessions WHERE id = ? AND user_id = ?', 
                     (session_id, current_user['id']))
        if not cursor.fetchone():
            return jsonify({'error': 'Guide session not found or access denied'}), 404
        
        # Record step result
        cursor.execute('''
            INSERT INTO guide_step_results 
            (session_id, step_number, step_name, result_type, result_value, measurements, adjustments_made, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (session_id, step_number, step_name, result_type, result_value, 
              measurements, adjustments_made, notes))
        
        # Update session current step
        cursor.execute('UPDATE guide_sessions SET current_step = ? WHERE id = ?', 
                     (step_number + 1, session_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Step result recorded successfully'})
        
    except Exception as e:
        if conn:
            conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/guide-sessions/<int:session_id>/complete', methods=['POST'])
@token_required
def complete_guide_session(current_user, session_id):
    """Mark a guide session as completed"""
    conn = None
    try:
        data = request.get_json()
        notes = data.get('notes', '')
        
        # Get user database connection
        from user_database import UserDatabase
        user_db = UserDatabase()
        conn = user_db.get_connection()
        cursor = conn.cursor()
        
        # Verify session belongs to user
        cursor.execute('SELECT id FROM guide_sessions WHERE id = ? AND user_id = ?', 
                     (session_id, current_user['id']))
        if not cursor.fetchone():
            return jsonify({'error': 'Guide session not found or access denied'}), 404
        
        # Mark session as completed
        cursor.execute('''
            UPDATE guide_sessions 
            SET status = 'completed', completed_at = CURRENT_TIMESTAMP, notes = ?
            WHERE id = ?
        ''', (notes, session_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Guide session completed successfully'})
        
    except Exception as e:
        if conn:
            conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/guide-sessions/<int:session_id>/pause', methods=['POST'])
@token_required
def pause_guide_session(current_user, session_id):
    """Pause a guide session"""
    conn = None
    try:
        data = request.get_json() or {}
        notes = data.get('notes', '')
        
        # Get user database connection
        from user_database import UserDatabase
        user_db = UserDatabase()
        conn = user_db.get_connection()
        cursor = conn.cursor()
        
        # Verify session belongs to user and is in progress
        cursor.execute('SELECT id, status FROM guide_sessions WHERE id = ? AND user_id = ?', 
                     (session_id, current_user['id']))
        session = cursor.fetchone()
        if not session:
            return jsonify({'error': 'Guide session not found or access denied'}), 404
        
        if session['status'] != 'in_progress':
            return jsonify({'error': 'Can only pause sessions that are in progress'}), 400
        
        # Mark session as paused
        cursor.execute('''
            UPDATE guide_sessions 
            SET status = 'paused', notes = ?
            WHERE id = ?
        ''', (notes, session_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Guide session paused successfully'})
        
    except Exception as e:
        if conn:
            conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/guide-sessions/<int:session_id>/resume', methods=['POST'])
@token_required
def resume_guide_session(current_user, session_id):
    """Resume a paused guide session"""
    conn = None
    try:
        # Get user database connection
        from user_database import UserDatabase
        user_db = UserDatabase()
        conn = user_db.get_connection()
        cursor = conn.cursor()
        
        # Verify session belongs to user and is paused
        cursor.execute('SELECT id, status FROM guide_sessions WHERE id = ? AND user_id = ?', 
                     (session_id, current_user['id']))
        session = cursor.fetchone()
        if not session:
            return jsonify({'error': 'Guide session not found or access denied'}), 404
        
        if session['status'] != 'paused':
            return jsonify({'error': 'Can only resume sessions that are paused'}), 400
        
        # Mark session as in progress again
        cursor.execute('''
            UPDATE guide_sessions 
            SET status = 'in_progress'
            WHERE id = ?
        ''', (session_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Guide session resumed successfully'})
        
    except Exception as e:
        if conn:
            conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/guide-sessions', methods=['GET'])
@token_required
def get_guide_sessions(current_user):
    """Get user's guide session history"""
    conn = None
    try:
        # Get user database connection
        from user_database import UserDatabase
        user_db = UserDatabase()
        conn = user_db.get_connection()
        cursor = conn.cursor()
        
        # Get sessions with bow setup info
        cursor.execute('''
            SELECT gs.*, bs.name as bow_name, bs.bow_type,
                   COUNT(gsr.id) as completed_steps
            FROM guide_sessions gs
            LEFT JOIN bow_setups bs ON gs.bow_setup_id = bs.id
            LEFT JOIN guide_step_results gsr ON gs.id = gsr.session_id
            WHERE gs.user_id = ?
            GROUP BY gs.id
            ORDER BY gs.started_at DESC
        ''', (current_user['id'],))
        
        sessions = []
        for row in cursor.fetchall():
            session = dict(row)
            sessions.append(session)
        
        conn.close()
        
        return jsonify({'sessions': sessions})
        
    except Exception as e:
        if conn:
            conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/guide-sessions/<int:session_id>', methods=['GET'])
@token_required
def get_guide_session_details(current_user, session_id):
    """Get detailed information about a guide session"""
    conn = None
    try:
        # Get user database connection
        from user_database import UserDatabase
        user_db = UserDatabase()
        conn = user_db.get_connection()
        cursor = conn.cursor()
        
        # Get session info
        cursor.execute('''
            SELECT gs.*, bs.name as bow_name, bs.bow_type, bs.draw_weight, bs.draw_length
            FROM guide_sessions gs
            LEFT JOIN bow_setups bs ON gs.bow_setup_id = bs.id
            WHERE gs.id = ? AND gs.user_id = ?
        ''', (session_id, current_user['id']))
        
        session = cursor.fetchone()
        if not session:
            return jsonify({'error': 'Guide session not found or access denied'}), 404
        
        # Get step results
        cursor.execute('''
            SELECT * FROM guide_step_results 
            WHERE session_id = ? 
            ORDER BY step_number
        ''', (session_id,))
        
        steps = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'session': dict(session),
            'steps': steps
        })
        
    except Exception as e:
        if conn:
            conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/tuning-history', methods=['POST'])
@token_required
def record_tuning_adjustment(current_user):
    """Record a tuning adjustment to history"""
    conn = None
    try:
        data = request.get_json()
        bow_setup_id = data.get('bow_setup_id')
        guide_session_id = data.get('guide_session_id')
        adjustment_type = data.get('adjustment_type')
        before_value = data.get('before_value')
        after_value = data.get('after_value')
        improvement_score = data.get('improvement_score')
        confidence_rating = data.get('confidence_rating')
        shooting_distance = data.get('shooting_distance')
        conditions = data.get('conditions')
        
        if not adjustment_type:
            return jsonify({'error': 'Adjustment type is required'}), 400
        
        # Get user database connection
        from user_database import UserDatabase
        user_db = UserDatabase()
        conn = user_db.get_connection()
        cursor = conn.cursor()
        
        # Verify bow setup belongs to user if provided
        if bow_setup_id:
            cursor.execute('SELECT id FROM bow_setups WHERE id = ? AND user_id = ?', 
                         (bow_setup_id, current_user['id']))
            if not cursor.fetchone():
                return jsonify({'error': 'Bow setup not found or access denied'}), 404
        
        # Record tuning adjustment
        cursor.execute('''
            INSERT INTO tuning_history 
            (user_id, bow_setup_id, guide_session_id, adjustment_type, before_value, 
             after_value, improvement_score, confidence_rating, shooting_distance, conditions)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (current_user['id'], bow_setup_id, guide_session_id, adjustment_type, 
              before_value, after_value, improvement_score, confidence_rating, 
              shooting_distance, conditions))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Tuning adjustment recorded successfully'})
        
    except Exception as e:
        if conn:
            conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/tuning-history', methods=['GET'])
@token_required
def get_tuning_history(current_user):
    """Get user's tuning adjustment history"""
    conn = None
    try:
        bow_setup_id = request.args.get('bow_setup_id')
        limit = request.args.get('limit', 50)
        
        # Get user database connection
        from user_database import UserDatabase
        user_db = UserDatabase()
        conn = user_db.get_connection()
        cursor = conn.cursor()
        
        # Build query
        query = '''
            SELECT th.*, bs.name as bow_name, bs.bow_type, gs.guide_name
            FROM tuning_history th
            LEFT JOIN bow_setups bs ON th.bow_setup_id = bs.id
            LEFT JOIN guide_sessions gs ON th.guide_session_id = gs.id
            WHERE th.user_id = ?
        '''
        params = [current_user['id']]
        
        if bow_setup_id:
            query += ' AND th.bow_setup_id = ?'
            params.append(bow_setup_id)
        
        query += ' ORDER BY th.created_at DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        history = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({'history': history})
        
    except Exception as e:
        if conn:
            conn.close()
        return jsonify({'error': str(e)}), 500

# Configuration and setup
# ===== RETAILER ENHANCEMENT API ENDPOINTS =====

@app.route('/api/arrows/<int:arrow_id>/retailer-data', methods=['GET'])
def get_arrow_retailer_data(arrow_id):
    """Get retailer data for a specific arrow"""
    try:
        from enhance_database_schema import get_retailer_enhanced_data
        
        enhanced_data = get_retailer_enhanced_data('arrow_database.db', arrow_id)
        
        if not enhanced_data:
            return jsonify({'error': 'Arrow not found'}), 404
        
        return jsonify({
            'arrow_id': arrow_id,
            'basic_data': {
                'manufacturer': enhanced_data.get('manufacturer'),
                'model_name': enhanced_data.get('model_name'),
                'material': enhanced_data.get('material'),
                'arrow_type': enhanced_data.get('arrow_type')
            },
            'retailer_data': enhanced_data.get('retailer_data', []),
            'enhancements': enhanced_data.get('enhancements'),
            'price_history': enhanced_data.get('price_history', []),
            'total_retailer_sources': len(enhanced_data.get('retailer_data', [])),
            'has_pricing': any(d.get('price') for d in enhanced_data.get('retailer_data', []))
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/arrows/<int:arrow_id>/enhance-retailer-data', methods=['POST'])
def enhance_arrow_retailer_data(arrow_id):
    """Enhance arrow with retailer data from specified URLs"""
    try:
        import os
        from retailer_integration import RetailerIntegrationManager
        
        api_key = os.environ.get('DEEPSEEK_API_KEY')
        if not api_key:
            return jsonify({'error': 'DEEPSEEK_API_KEY not configured'}), 500
        
        data = request.get_json()
        retailer_urls = data.get('retailer_urls', []) if data else []
        
        # Create manager and enhance arrow
        manager = RetailerIntegrationManager(api_key)
        
        # Run async enhancement
        import asyncio
        result = asyncio.run(manager.enhance_arrow_with_retailer_data(arrow_id, retailer_urls))
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/arrows/batch-enhance-retailer-data', methods=['POST'])
def batch_enhance_retailer_data():
    """Batch enhance multiple arrows with retailer data"""
    try:
        import os
        from retailer_integration import RetailerIntegrationManager
        
        api_key = os.environ.get('DEEPSEEK_API_KEY')
        if not api_key:
            return jsonify({'error': 'DEEPSEEK_API_KEY not configured'}), 500
        
        data = request.get_json() or {}
        manufacturer = data.get('manufacturer')
        limit = int(data.get('limit', 5))  # Limit to 5 by default for safety
        
        # Create manager and run batch enhancement
        manager = RetailerIntegrationManager(api_key)
        
        import asyncio
        result = asyncio.run(manager.batch_enhance_arrows(manufacturer, limit))
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/retailers', methods=['GET'])
def get_retailers():
    """Get list of supported retailers"""
    try:
        conn = sqlite3.connect('arrow_database.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT rs.*, COUNT(rad.id) as arrow_count
            FROM retailer_sources rs
            LEFT JOIN retailer_arrow_data rad ON rs.id = rad.retailer_id
            GROUP BY rs.id
            ORDER BY rs.retailer_name
        """)
        
        retailers = []
        for row in cursor.fetchall():
            retailers.append({
                'id': row[0],
                'name': row[1],
                'base_url': row[2],
                'language': row[3],
                'currency': row[4],
                'arrow_count': row[6],
                'created_at': row[5]
            })
        
        conn.close()
        
        return jsonify({
            'retailers': retailers,
            'total_retailers': len(retailers)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/arrows/with-retailer-data', methods=['GET'])
def get_arrows_with_retailer_data():
    """Get arrows that have retailer enhancement data"""
    try:
        conn = sqlite3.connect('arrow_database.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get query parameters
        retailer_id = request.args.get('retailer_id', type=int)
        has_pricing = request.args.get('has_pricing', '').lower() == 'true'
        limit = request.args.get('limit', 20, type=int)
        
        # Build query
        query = """
            SELECT DISTINCT a.*, 
                   COUNT(rad.id) as retailer_count,
                   AVG(rad.price) as avg_price,
                   MIN(rad.price) as min_price,
                   MAX(rad.price) as max_price,
                   GROUP_CONCAT(rs.retailer_name) as retailers
            FROM arrows a
            JOIN retailer_arrow_data rad ON a.id = rad.arrow_id
            JOIN retailer_sources rs ON rad.retailer_id = rs.id
            WHERE 1=1
        """
        
        params = []
        
        if retailer_id:
            query += " AND rad.retailer_id = ?"
            params.append(retailer_id)
        
        if has_pricing:
            query += " AND rad.price IS NOT NULL"
        
        query += """
            GROUP BY a.id
            ORDER BY retailer_count DESC, a.manufacturer, a.model_name
            LIMIT ?
        """
        params.append(limit)
        
        cursor.execute(query, params)
        arrows = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'arrows': arrows,
            'total': len(arrows),
            'filters': {
                'retailer_id': retailer_id,
                'has_pricing': has_pricing,
                'limit': limit
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/debug/database', methods=['GET'])
def debug_database():
    """Debug database access and wood arrow search"""
    try:
        global tuning_system
        tuning_system = None  # Force reinitialize
        
        ts = get_tuning_system()
        if not ts:
            return jsonify({'error': 'Cannot initialize tuning system'}), 500
            
        # Test wood arrow search directly
        wood_arrows = ts.matching_engine.db.search_arrows(
            material='Wood',
            spine_min=40,
            spine_max=60,
            limit=10
        )
        
        return jsonify({
            'tuning_system_initialized': ts is not None,
            'wood_arrows_found': len(wood_arrows),
            'sample_arrows': [f"{arrow['manufacturer']} {arrow['model_name']}" for arrow in wood_arrows[:3]]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload/image', methods=['POST'])
@token_required
def upload_image(current_user):
    """Upload image to CDN and return URL"""
    try:
        # Check if image file was provided
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get upload parameters
        upload_path = request.form.get('upload_path', 'profile')
        filename = request.form.get('filename', '')
        
        # Validate file type
        allowed_extensions = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
        file_extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        
        if file_extension not in allowed_extensions:
            return jsonify({'error': f'File type not supported. Use: {", ".join(allowed_extensions.upper())}'}), 400
        
        # Validate file size (5MB max)
        max_size = 5 * 1024 * 1024  # 5MB
        file.seek(0, 2)  # Seek to end
        size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if size > max_size:
            return jsonify({'error': 'File too large. Maximum size: 5MB'}), 400
        
        # Import CDN uploader
        from cdn_uploader import CDNUploader
        
        # Get CDN type from environment (default to bunnycdn since it's configured)
        cdn_type = os.getenv('CDN_TYPE', 'bunnycdn')
        
        # Initialize CDN uploader
        try:
            uploader = CDNUploader(cdn_type)
        except Exception as e:
            print(f"CDN initialization error: {e}")
            # Fallback to local storage
            uploader = CDNUploader('local')
            cdn_type = 'local'
        
        # Create temporary file for upload
        import tempfile
        import uuid
        
        temp_dir = tempfile.gettempdir()
        temp_filename = f"upload_{uuid.uuid4().hex[:8]}.{file_extension}"
        temp_path = os.path.join(temp_dir, temp_filename)
        
        try:
            # Save file temporarily
            file.save(temp_path)
            
            # Generate CDN path based on upload type and user
            if upload_path == 'profile':
                manufacturer = f"user_{current_user['id']}"
                model_name = "profile_picture"
            else:
                manufacturer = upload_path
                model_name = filename or f"upload_{uuid.uuid4().hex[:8]}"
            
            # Upload to CDN
            result = uploader.upload_from_file(
                temp_path, 
                manufacturer, 
                model_name, 
                "primary"
            )
            
            if not result:
                return jsonify({'error': 'Upload to CDN failed'}), 500
            
            # Update user profile picture if this is a profile upload
            if upload_path == 'profile':
                from user_database import UserDatabase
                user_db = UserDatabase()
                updated_user = user_db.update_user_profile(
                    current_user['id'], 
                    profile_picture_url=result['cdn_url']
                )
                
                if not updated_user:
                    print(f"Warning: Failed to update user profile picture URL in database")
            
            return jsonify({
                'success': True,
                'cdn_url': result['cdn_url'],
                'cdn_type': result['cdn_type'],
                'upload_path': upload_path,
                'file_size': result.get('bytes', size)
            })
                
        except Exception as e:
            print(f"Image upload error: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': 'Upload failed. Please try again.'}), 500
        finally:
            # Clean up temporary file
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.remove(temp_path)
    
    except Exception as e:
        print(f"Upload image function error: {e}")
        return jsonify({'error': 'Image upload failed'}), 500

# Debug route removed

@app.route('/api/admin/backup', methods=['POST'])
@token_required
@admin_required
def create_backup(current_user):
    """Create database backup and upload to CDN"""
    try:
        from backup_manager import BackupManager
        from cdn_uploader import CDNUploader
        import tempfile
        import uuid
        from datetime import datetime
        
        data = request.get_json() or {}
        backup_name = data.get('backup_name')
        include_arrow_db = data.get('include_arrow_db', True)
        include_user_db = data.get('include_user_db', True)
        
        if not include_arrow_db and not include_user_db:
            return jsonify({'error': 'At least one database must be selected for backup'}), 400
        
        # Create backup manager
        backup_manager = BackupManager()
        
        # Generate backup name if not provided
        if not backup_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            db_types = []
            if include_arrow_db:
                db_types.append("arrows")
            if include_user_db:
                db_types.append("users")
            backup_name = f"admin_backup_{'-'.join(db_types)}_{timestamp}"
        
        # Create local backup
        local_backup_path = backup_manager.create_backup(
            backup_name=backup_name,
            include_arrow_db=include_arrow_db,
            include_user_db=include_user_db
        )
        
        if not local_backup_path or not os.path.exists(local_backup_path):
            return jsonify({'error': 'Failed to create local backup'}), 500
        
        # Upload to CDN using centralized CDN backup manager
        cdn_url = None
        result = None
        try:
            from cdn_backup_manager import CDNBackupManager
            
            cdn_manager = CDNBackupManager()
            
            # Create environment-aware backup filename
            environment = os.getenv('FLASK_ENV', 'development')
            backup_type = 'full'
            if not include_arrow_db:
                backup_type = 'user_only'
            elif not include_user_db:
                backup_type = 'arrow_only'
            
            # Generate structured filename: {env}_{type}_{timestamp}.tar.gz
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            structured_filename = f"{environment}_{backup_type}_{timestamp}.tar.gz"
            
            cdn_url = cdn_manager.upload_backup(local_backup_path, structured_filename)
            
            if cdn_url:
                print(f"✅ Backup uploaded to CDN: {cdn_url}")
                cdn_type = os.getenv('CDN_TYPE', 'bunnycdn')
                result = {
                    'success': True,
                    'url': cdn_url,
                    'cdn_url': cdn_url,  # Add both keys for compatibility
                    'cdn_type': cdn_type,
                    'filename': structured_filename
                }
            else:
                # Fallback to legacy CDN uploader
                raise Exception("CDN backup manager upload failed")
                
        except Exception as e:
            print(f"❌ CDN backup manager upload failed: {e}")
            
            # Fallback to legacy CDN uploader
            try:
                from cdn_uploader import CDNUploader
                
                cdn_type = os.getenv('CDN_TYPE', 'bunnycdn')
                uploader = CDNUploader(cdn_type)
                
                # Upload backup to CDN using legacy method
                result = uploader.upload_from_file(
                    local_backup_path,
                    manufacturer="backups",
                    model_name=backup_name,
                    image_type="backup"
                )
                
                if result.get('success') and result.get('url'):
                    cdn_url = result['url']
                    # Ensure cdn_url key is present for consistency
                    result['cdn_url'] = cdn_url
                    result['cdn_type'] = os.getenv('CDN_TYPE', 'bunnycdn')
                    print(f"✅ Backup uploaded via legacy CDN uploader: {cdn_url}")
                else:
                    print("❌ Legacy CDN uploader also failed")
                    result = {'success': False}
                    
            except Exception as fallback_error:
                print(f"❌ Both CDN methods failed: {fallback_error}")
                result = {'success': False}
        
        if not result or not result.get('success'):
            return jsonify({'error': 'Failed to upload backup to CDN'}), 500
        
        # Ensure result has required keys
        if 'cdn_url' not in result:
            return jsonify({'error': 'Backup creation failed: CDN URL not available'}), 500
        
        # Get backup file size
        backup_size = os.path.getsize(local_backup_path) / (1024 * 1024)  # MB
        
        # Store backup metadata in user database
        from user_database import UserDatabase
        user_db = UserDatabase()
        conn = user_db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO backup_metadata 
            (backup_name, cdn_url, cdn_type, file_size_mb, include_arrow_db, include_user_db, 
             created_by, local_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            backup_name, result['cdn_url'], result.get('cdn_type', 'unknown'), backup_size,
            include_arrow_db, include_user_db, current_user['id'], local_backup_path
        ))
        
        backup_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Backup "{backup_name}" created and uploaded successfully',
            'backup_id': backup_id,
            'backup_name': backup_name,
            'cdn_url': result['cdn_url'],
            'cdn_type': result['cdn_type'],
            'file_size_mb': backup_size,
            'includes': {
                'arrow_database': include_arrow_db,
                'user_database': include_user_db
            },
            'created_by': current_user['email'],
            'local_path': local_backup_path
        })
        
    except Exception as e:
        print(f"Backup creation error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Backup creation failed: {str(e)}'}), 500

@app.route('/api/admin/backup-test-post', methods=['POST'])
def backup_test_post():
    """Test POST route registration after create_backup function"""
    return jsonify({'message': 'POST route registration works', 'status': 'ok'})

# Helper functions for CDN backup management

def get_cdn_backups():
    """Get all CDN backups using the centralized CDN backup manager"""
    try:
        from cdn_backup_manager import CDNBackupManager
        
        # Initialize the CDN backup manager
        cdn_manager = CDNBackupManager()
        
        # Get backups from all configured CDN providers
        cdn_backups = cdn_manager.list_all_backups()
        
        # Convert BackupInfo objects to dictionaries for JSON serialization
        backup_dicts = []
        for backup in cdn_backups:
            backup_dict = {
                'id': backup.id,
                'name': backup.name,
                'backup_name': backup.name,  # Legacy compatibility
                'filename': backup.filename,
                'created_at': backup.created_at,
                'file_size_mb': backup.file_size_mb,
                'environment': backup.environment,
                'backup_type': backup.backup_type,
                'cdn_url': backup.cdn_url,
                'cdn_type': backup.cdn_type,
                'include_arrow_db': backup.include_arrow_db,
                'include_user_db': backup.include_user_db,
                'is_cdn_direct': backup.is_cdn_direct,
                'source': backup.source,
                'source_description': backup.source_description,
                'file': backup.filename,  # Legacy compatibility
                'is_remote': True
            }
            backup_dicts.append(backup_dict)
        
        print(f"✅ Retrieved {len(backup_dicts)} backups from CDN backup manager")
        return backup_dicts
        
    except Exception as e:
        print(f"❌ Failed to get CDN backups: {e}")
        # Fallback to legacy method if CDN manager fails
        return get_legacy_bunny_cdn_backups()

def get_legacy_bunny_cdn_backups():
    """Legacy Bunny CDN backup fetching (fallback)"""
    import requests
    
    # Get Bunny CDN configuration from environment
    storage_zone = os.getenv('BUNNY_STORAGE_ZONE', 'arrowtuner-images')
    access_key = os.getenv('BUNNY_ACCESS_KEY')
    region = os.getenv('BUNNY_REGION', 'de')
    
    if not access_key:
        print("❌ Bunny CDN access key not configured")
        print("ℹ️  Set BUNNY_ACCESS_KEY environment variable to enable CDN backup listing")
        return []
    
    # Determine API endpoint based on region
    if region == 'de':
        api_base = 'https://storage.bunnycdn.com'
    elif region == 'uk':
        api_base = 'https://uk.storage.bunnycdn.com'
    elif region == 'la':
        api_base = 'https://la.storage.bunnycdn.com'
    elif region == 'ny':
        api_base = 'https://ny.storage.bunnycdn.com'
    elif region == 'sg':
        api_base = 'https://sg.storage.bunnycdn.com'
    elif region == 'syd':
        api_base = 'https://syd.storage.bunnycdn.com'
    else:
        api_base = 'https://storage.bunnycdn.com'  # Default to main region
    
    # API endpoint to list files in storage zone (matches CDN uploader path structure)
    api_url = f"{api_base}/{storage_zone}/arrows/backups/"
    
    headers = {
        'AccessKey': access_key,
        'Accept': 'application/json'
    }
    
    try:
        print(f"🌐 Fetching backups from Legacy Bunny CDN: {api_url}")
        response = requests.get(api_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            files = response.json()
            cdn_backups = []
            
            for file_info in files:
                filename = file_info.get('ObjectName', '')
                if filename.endswith('.tar.gz') or filename.endswith('.gz'):
                    import hashlib
                    clean_name = filename.replace('.tar.gz', '').replace('.gz', '')
                    cdn_backup_id = hashlib.md5(filename.encode()).hexdigest()[:8]
                    
                    # Get file size in MB
                    file_size_bytes = file_info.get('Length', 0)
                    file_size_mb = file_size_bytes / (1024 * 1024) if file_size_bytes else 0.0
                    
                    backup_info = {
                        'id': f'legacy_cdn_{cdn_backup_id}',
                        'name': clean_name,
                        'backup_name': clean_name,
                        'created_at': file_info.get('LastChanged', datetime.now().isoformat()),
                        'file_size_mb': round(file_size_mb, 2),
                        'cdn_url': f"https://{os.getenv('BUNNY_HOSTNAME', f'{storage_zone}.b-cdn.net')}/arrows/backups/{filename}",
                        'cdn_type': 'bunnycdn',
                        'include_arrow_db': True,
                        'include_user_db': True,
                        'file': filename,
                        'is_cdn_direct': True,
                        'source': 'cdn',
                        'source_description': 'Legacy CDN (Bunny)',
                        'environment': 'unknown',
                        'backup_type': 'full',
                        'is_remote': True
                    }
                    cdn_backups.append(backup_info)
            
            print(f"✅ Found {len(cdn_backups)} backup files on Legacy Bunny CDN")
            return cdn_backups
        else:
            print(f"❌ Legacy Bunny CDN API error: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Legacy Bunny CDN request failed: {e}")
        return []

def get_database_cdn_backups():
    """Fallback: Get CDN backups from database metadata"""
    from user_database import UserDatabase
    user_db = UserDatabase()
    conn = user_db.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT bm.*, u.name as created_by_name, u.email as created_by_email
            FROM backup_metadata bm
            LEFT JOIN users u ON bm.created_by = u.id
            WHERE bm.cdn_url IS NOT NULL
            ORDER BY bm.created_at DESC
        ''')
        
        cdn_backups = []
        rows = cursor.fetchall()
        print(f"📊 Found {len(rows)} backups in database metadata")
        
        for row in rows:
            backup_info = dict(row)
            # Ensure database backups have consistent ID format
            if 'id' not in backup_info or not backup_info['id']:
                backup_info['id'] = f"db_{backup_info.get('backup_name', 'unknown')}"
            
            # Ensure consistent field names
            if 'name' not in backup_info and 'backup_name' in backup_info:
                backup_info['name'] = backup_info['backup_name']
            
            # Add status based on whether local file still exists
            backup_info['local_exists'] = os.path.exists(backup_info['local_path']) if backup_info['local_path'] else False
            backup_info['is_cdn_direct'] = False  # Flag to indicate this came from database
            
            # Add file size if missing (database backups might not have it)
            if 'file_size_mb' not in backup_info:
                backup_info['file_size_mb'] = backup_info.get('file_size_mb', 0.0)
            
            cdn_backups.append(backup_info)
        
        return cdn_backups
        
    finally:
        conn.close()

# Re-added the list_backups function after accidentally removing all instances

@app.route('/api/admin/backups', methods=['GET'])
@token_required
@admin_required
def list_backups(current_user):
    """List all available backups from both local and CDN"""
    try:
        from backup_manager import BackupManager
        
        # Get local backups
        backup_manager = BackupManager()
        local_backups = backup_manager.list_backups()
        print(f"📁 Found {len(local_backups)} local backups")
        
        # Get CDN backups using centralized CDN backup manager (CDN-first approach)
        cdn_backups = []
        try:
            cdn_backups = get_cdn_backups()
            print(f"🌐 Retrieved {len(cdn_backups)} backups from CDN backup manager")
        except Exception as cdn_error:
            print(f"⚠️  Could not fetch CDN backups: {cdn_error}")
            # Fallback to database metadata if CDN manager fails
            try:
                cdn_backups = get_database_cdn_backups()
                print(f"📊 Using {len(cdn_backups)} backups from database metadata (fallback)")
            except Exception as db_error:
                print(f"❌ Database fallback also failed: {db_error}")
                cdn_backups = []
        
        # No need to close connection here since it's handled in helper functions
        
        # Enhance backup information with source indicators
        for backup in local_backups:
            backup['source'] = 'local'
            backup['source_description'] = 'Local Development'
            # Normalize property names: local backups use 'size_mb', frontend expects 'file_size_mb'
            if 'size_mb' in backup and 'file_size_mb' not in backup:
                backup['file_size_mb'] = backup['size_mb']
            
        for backup in cdn_backups:
            backup['source'] = 'cdn'
            backup['is_remote'] = True
            
            # Different descriptions based on data source
            if backup.get('is_cdn_direct', False):
                backup['source_description'] = 'Production/CDN (Live)'
                # Ensure CDN direct backups have consistent property names
                if 'file_size_mb' not in backup:
                    backup['file_size_mb'] = 0.0  # Default value if missing
            else:
                backup['source_description'] = 'Production/CDN (Metadata)'
                # Ensure database CDN backups have consistent property names
                if 'file_size_mb' not in backup:
                    backup['file_size_mb'] = 0.0  # Default value if missing
        
        # Combine and sort by creation date for unified display
        all_backups = local_backups + cdn_backups
        all_backups.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        print(f"✅ Total backups found: {len(all_backups)} ({len(local_backups)} local, {len(cdn_backups)} CDN)")
        
        return jsonify({
            'success': True,
            'local_backups': local_backups,
            'cdn_backups': cdn_backups,
            'all_backups': all_backups,  # Combined and sorted list
            'total_local': len(local_backups),
            'total_cdn': len(cdn_backups),
            'total_all': len(all_backups)
        })
        
    except Exception as e:
        print(f"List backups error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to list backups: {str(e)}'}), 500

@app.route('/api/admin/backup/<int:backup_id>/restore', methods=['POST'])
@token_required
@admin_required
def restore_backup_from_cdn(current_user, backup_id):
    """Restore database from CDN backup"""
    try:
        from backup_manager import BackupManager
        import tempfile
        import requests
        
        data = request.get_json() or {}
        restore_arrow_db = data.get('restore_arrow_db', True)
        restore_user_db = data.get('restore_user_db', True)
        force = data.get('force', False)
        
        if not restore_arrow_db and not restore_user_db:
            return jsonify({'error': 'At least one database must be selected for restore'}), 400
        
        # Get backup metadata from database
        from user_database import UserDatabase
        user_db = UserDatabase()
        conn = user_db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM backup_metadata WHERE id = ?', (backup_id,))
        backup_record = cursor.fetchone()
        conn.close()
        
        if not backup_record:
            return jsonify({'error': 'Backup not found'}), 404
        
        backup_record = dict(backup_record)
        
        # Check if backup contains the requested databases
        if restore_arrow_db and not backup_record['include_arrow_db']:
            return jsonify({'error': 'Backup does not contain arrow database'}), 400
        if restore_user_db and not backup_record['include_user_db']:
            return jsonify({'error': 'Backup does not contain user database'}), 400
        
        # Try to use local file first if it exists
        backup_file_path = None
        if backup_record['local_path'] and os.path.exists(backup_record['local_path']):
            backup_file_path = backup_record['local_path']
        else:
            # Download from CDN
            temp_dir = tempfile.gettempdir()
            backup_filename = f"restore_{backup_record['backup_name']}.tar.gz"
            backup_file_path = os.path.join(temp_dir, backup_filename)
            
            print(f"Downloading backup from CDN: {backup_record['cdn_url']}")
            
            response = requests.get(backup_record['cdn_url'], timeout=300)  # 5 minute timeout
            response.raise_for_status()
            
            with open(backup_file_path, 'wb') as f:
                f.write(response.content)
        
        # Restore using backup manager
        backup_manager = BackupManager()
        success = backup_manager.restore_backup(
            backup_path=backup_file_path,
            restore_arrow_db=restore_arrow_db,
            restore_user_db=restore_user_db,
            force=True  # Force restore in API mode
        )
        
        if not success:
            return jsonify({'error': 'Backup restore failed'}), 500
        
        # Clean up downloaded file if it was temporary
        if backup_record['local_path'] != backup_file_path and os.path.exists(backup_file_path):
            os.remove(backup_file_path)
        
        # Record restore activity
        from user_database import UserDatabase
        user_db = UserDatabase()
        conn = user_db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO backup_restore_log 
            (backup_id, restored_by, restore_arrow_db, restore_user_db)
            VALUES (?, ?, ?, ?)
        ''', (backup_id, current_user['id'], restore_arrow_db, restore_user_db))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Successfully restored from backup "{backup_record["backup_name"]}"',
            'backup_name': backup_record['backup_name'],
            'restored': {
                'arrow_database': restore_arrow_db,
                'user_database': restore_user_db
            },
            'restored_by': current_user['email']
        })
        
    except Exception as e:
        print(f"Backup restore error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Backup restore failed: {str(e)}'}), 500

@app.route('/api/admin/backup/<int:backup_id>/download', methods=['GET'])
@token_required
@admin_required
def download_backup(current_user, backup_id):
    """Get download URL for backup"""
    try:
        from user_database import UserDatabase
        user_db = UserDatabase()
        conn = user_db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM backup_metadata WHERE id = ?', (backup_id,))
        backup_record = cursor.fetchone()
        conn.close()
        
        if not backup_record:
            return jsonify({'error': 'Backup not found'}), 404
        
        backup_record = dict(backup_record)
        
        return jsonify({
            'success': True,
            'backup_name': backup_record['backup_name'],
            'cdn_url': backup_record['cdn_url'],
            'cdn_type': backup_record['cdn_type'],
            'file_size_mb': backup_record['file_size_mb'],
            'local_exists': os.path.exists(backup_record['local_path']) if backup_record['local_path'] else False
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get backup download info: {str(e)}'}), 500

@app.route('/api/admin/backup/<backup_id>/restore', methods=['POST'])
@token_required
@admin_required
def restore_backup_new_format(current_user, backup_id):
    """Restore database from backup (supports new string ID format)"""
    try:
        from backup_manager import BackupManager
        
        data = request.get_json() or {}
        restore_arrow_db = data.get('restore_arrow_db', True)
        restore_user_db = data.get('restore_user_db', True)
        force = data.get('force', False)
        
        if not restore_arrow_db and not restore_user_db:
            return jsonify({'error': 'At least one database must be selected for restore'}), 400
        
        print(f"Restoring backup {backup_id}, arrow_db: {restore_arrow_db}, user_db: {restore_user_db}")
        
        backup_manager = BackupManager()
        
        # Handle different backup ID formats
        if backup_id.startswith('local_'):
            # Local file backup - find the matching backup file
            backups = backup_manager.list_backups()
            backup_file = None
            
            for backup in backups:
                if backup.get('id') == backup_id:
                    backup_file = backup.get('file')
                    break
            
            if not backup_file or not os.path.exists(backup_file):
                return jsonify({'error': 'Local backup file not found'}), 404
            
            # Restore from local file
            success = backup_manager.restore_backup(
                backup_path=backup_file,
                restore_arrow_db=restore_arrow_db,
                restore_user_db=restore_user_db,
                force=force
            )
            
        elif backup_id.startswith('cdn_'):
            return jsonify({'error': 'CDN backup restore not yet implemented'}), 501
            
        else:
            # Legacy integer backup ID - delegate to old endpoint logic
            try:
                backup_id_int = int(backup_id)
                # Call the existing restore logic
                return restore_backup_from_cdn(current_user, backup_id_int)
            except ValueError:
                return jsonify({'error': 'Invalid backup ID format'}), 400
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Backup restored successfully',
                'restored_databases': {
                    'arrow_db': restore_arrow_db,
                    'user_db': restore_user_db
                }
            })
        else:
            return jsonify({'error': 'Backup restore failed'}), 500
            
    except Exception as e:
        print(f"Backup restore error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Backup restore failed: {str(e)}'}), 500

@app.route('/api/admin/backup/<backup_id>/download', methods=['GET'])
@token_required
@admin_required
def download_backup_new_format(current_user, backup_id):
    """Get download URL for backup (supports new string ID format)"""
    try:
        print(f"Download request for backup {backup_id}")
        
        # Handle different backup ID formats
        if backup_id.startswith('local_'):
            # Local file backup - provide direct file access
            from backup_manager import BackupManager
            backup_manager = BackupManager()
            backups = backup_manager.list_backups()
            
            for backup in backups:
                if backup.get('id') == backup_id:
                    backup_file = backup.get('file')
                    if backup_file and os.path.exists(backup_file):
                        # For local files, we'll need to create a download endpoint
                        # For now, return file info so frontend can handle appropriately
                        return jsonify({
                            'success': True,
                            'backup_name': backup.get('backup_name', backup.get('name')),
                            'local_path': backup_file,
                            'file_size_mb': backup.get('size_mb'),
                            'local_exists': True,
                            'download_type': 'local_file'
                        })
                    else:
                        return jsonify({'error': 'Local backup file not found'}), 404
            
            return jsonify({'error': 'Backup not found'}), 404
            
        elif backup_id.startswith('cdn_'):
            return jsonify({'error': 'CDN backup download not yet implemented'}), 501
            
        else:
            # Legacy integer backup ID - delegate to old endpoint logic
            try:
                backup_id_int = int(backup_id)
                # Call the existing download logic
                return download_backup(current_user, backup_id_int)
            except ValueError:
                return jsonify({'error': 'Invalid backup ID format'}), 400
                
    except Exception as e:
        print(f"Backup download error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to get backup download info: {str(e)}'}), 500

@app.route('/api/admin/backup/download-file', methods=['POST'])
@token_required
@admin_required
def download_backup_file(current_user):
    """Download a local backup file"""
    try:
        data = request.get_json() or {}
        local_path = data.get('local_path')
        
        if not local_path or not os.path.exists(local_path):
            return jsonify({'error': 'Backup file not found'}), 404
        
        # Security check - ensure file is in backups directory
        backup_dir = os.path.abspath('backups')
        file_path = os.path.abspath(local_path)
        
        if not file_path.startswith(backup_dir):
            return jsonify({'error': 'Access denied'}), 403
        
        # Send file
        from flask import send_file
        filename = os.path.basename(local_path)
        return send_file(local_path, as_attachment=True, download_name=filename)
        
    except Exception as e:
        print(f"File download error: {e}")
        return jsonify({'error': f'Failed to download file: {str(e)}'}), 500

@app.route('/api/admin/backup/<backup_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_backup(current_user, backup_id):
    """Delete backup from local storage, CDN, or database metadata"""
    try:
        # Handle different backup ID formats
        if backup_id.startswith('local_'):
            # Local file backup
            return delete_local_backup(backup_id)
        elif backup_id.startswith('cdn_'):
            # CDN backup
            return delete_cdn_backup(backup_id)
        else:
            # Legacy database backup ID (integer)
            try:
                db_backup_id = int(backup_id)
                return delete_database_backup(db_backup_id)
            except ValueError:
                return jsonify({'error': 'Invalid backup ID format'}), 400
                
    except Exception as e:
        print(f"Error deleting backup {backup_id}: {e}")
        return jsonify({'error': 'Failed to delete backup'}), 500

def delete_local_backup(backup_id):
    """Delete local backup file"""
    try:
        from backup_manager import BackupManager
        backup_manager = BackupManager()
        
        # Get all local backups to find the matching one
        local_backups = backup_manager.list_backups()
        target_backup = None
        
        for backup in local_backups:
            if backup.get('id') == backup_id:
                target_backup = backup
                break
        
        if not target_backup:
            return jsonify({'error': 'Local backup not found'}), 404
        
        # Delete the local file
        backup_file_path = target_backup.get('file')
        if backup_file_path and os.path.exists(backup_file_path):
            os.remove(backup_file_path)
            return jsonify({'message': 'Local backup deleted successfully'})
        else:
            return jsonify({'error': 'Backup file not found'}), 404
            
    except Exception as e:
        print(f"Error deleting local backup {backup_id}: {e}")
        return jsonify({'error': 'Failed to delete local backup'}), 500

def delete_cdn_backup(backup_id):
    """Delete CDN backup (not implemented yet)"""
    # TODO: Implement CDN backup deletion using Bunny CDN API
    return jsonify({'error': 'CDN backup deletion not yet implemented'}), 501

def delete_database_backup(backup_id):
    """Delete database backup record (legacy)"""
    try:
        from user_database import UserDatabase
        user_db = UserDatabase()
        conn = user_db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM backup_metadata WHERE id = ?', (backup_id,))
        backup_record = cursor.fetchone()
        
        if not backup_record:
            conn.close()
            return jsonify({'error': 'Backup not found'}), 404
        
        backup_record = dict(backup_record)
        
        # Delete local file if it exists
        local_deleted = False
        if backup_record['local_path'] and os.path.exists(backup_record['local_path']):
            try:
                os.remove(backup_record['local_path'])
                local_deleted = True
            except Exception as e:
                print(f"Warning: Could not delete local backup file: {e}")
        
        # TODO: Delete from CDN if CDN supports deletion
        # For now, we just remove from our metadata
        
        # Delete from metadata
        cursor.execute('DELETE FROM backup_metadata WHERE id = ?', (backup_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Database backup deleted successfully'})
        
    except Exception as e:
        print(f"Error deleting database backup {backup_id}: {e}")
        return jsonify({'error': 'Failed to delete database backup'}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/api/admin/backup/upload', methods=['POST'])
@token_required
@admin_required
def upload_backup_file(current_user):
    """Upload and restore from backup file"""
    try:
        from backup_manager import BackupManager
        from user_database import UserDatabase
        from werkzeug.utils import secure_filename
        import tempfile
        import uuid
        from datetime import datetime
        
        # Check if file was uploaded
        if 'backup_file' not in request.files:
            return jsonify({'error': 'No backup file provided'}), 400
        
        file = request.files['backup_file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file extension - support both .tar.gz and .gz files
        filename_lower = file.filename.lower()
        if not (filename_lower.endswith('.tar.gz') or filename_lower.endswith('.gz')):
            return jsonify({'error': 'Invalid file format. Only .tar.gz and .gz files are supported'}), 400
        
        # Get restore options from form data
        restore_arrow_db = request.form.get('restore_arrow_db', 'true').lower() == 'true'
        restore_user_db = request.form.get('restore_user_db', 'true').lower() == 'true'
        force_restore = request.form.get('force_restore', 'false').lower() == 'true'
        
        if not restore_arrow_db and not restore_user_db:
            return jsonify({'error': 'At least one database must be selected for restore'}), 400
        
        # Create secure filename
        filename = secure_filename(file.filename)
        
        # Save uploaded file to temporary location
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, filename)
        file.save(temp_file_path)
        
        # Verify the backup file first
        backup_manager = BackupManager()
        
        print(f"🔍 Verifying uploaded backup file: {filename}")
        if not backup_manager.verify_backup(temp_file_path):
            # Cleanup temp file
            try:
                os.remove(temp_file_path)
                os.rmdir(temp_dir)
            except:
                pass
            return jsonify({'error': 'Invalid or corrupted backup file'}), 400
        
        print(f"✅ Backup verification successful")
        
        # Perform the restore
        print(f"🔄 Restoring from uploaded backup...")
        print(f"   Arrow DB: {'Yes' if restore_arrow_db else 'No'}")
        print(f"   User DB: {'Yes' if restore_user_db else 'No'}")
        print(f"   Force: {'Yes' if force_restore else 'No'}")
        
        success = backup_manager.restore_backup(
            backup_path=temp_file_path,
            restore_arrow_db=restore_arrow_db,
            restore_user_db=restore_user_db,
            force=True  # Always force in API context
        )
        
        # Cleanup temp file
        try:
            os.remove(temp_file_path)
            os.rmdir(temp_dir)
        except Exception as cleanup_error:
            print(f"⚠️  Cleanup warning: {cleanup_error}")
        
        if not success:
            return jsonify({'error': 'Failed to restore from backup file'}), 500
        
        # Record the restore operation in the database
        try:
            from user_database import UserDatabase
            user_db = UserDatabase()
            conn = user_db.get_connection()
            cursor = conn.cursor()
            
            # Insert restore record
            cursor.execute('''
                INSERT INTO backup_operations 
                (operation_type, backup_name, user_email, timestamp, details, status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                'restore_upload',
                filename,
                current_user['email'],
                datetime.now().isoformat(),
                json.dumps({
                    'restore_arrow_db': restore_arrow_db,
                    'restore_user_db': restore_user_db,
                    'uploaded_filename': filename,
                    'file_size_bytes': os.path.getsize(temp_file_path) if os.path.exists(temp_file_path) else 0
                }),
                'success'
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as db_error:
            print(f"⚠️  Failed to record restore operation: {db_error}")
        
        return jsonify({
            'success': True,
            'message': f'Successfully restored from uploaded backup: {filename}',
            'restored': {
                'arrow_database': restore_arrow_db,
                'user_database': restore_user_db
            },
            'restored_by': current_user['email'],
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Upload restore error: {e}")
        return jsonify({'error': f'Failed to restore from uploaded file: {str(e)}'}), 500

@app.route('/api/admin/system-info', methods=['GET'])
@token_required
@admin_required
def get_system_info(current_user):
    """Get comprehensive system information for admin panel"""
    try:
        import platform
        import psutil
        from arrow_database import ArrowDatabase
        from user_database import UserDatabase
        
        # Get database information
        arrow_db = ArrowDatabase()
        arrow_db_path = str(arrow_db.db_path)
        
        user_db = UserDatabase()
        user_db_path = str(user_db.db_path)
        
        # Get arrow database statistics
        arrow_conn = arrow_db.get_connection()
        arrow_cursor = arrow_conn.cursor()
        
        # Count arrows and manufacturers
        arrow_cursor.execute("SELECT COUNT(*) FROM arrows")
        arrow_count = arrow_cursor.fetchone()[0]
        
        arrow_cursor.execute("SELECT COUNT(DISTINCT manufacturer) FROM arrows")
        manufacturer_count = arrow_cursor.fetchone()[0]
        
        # Count spine specifications
        arrow_cursor.execute("SELECT COUNT(*) FROM spine_specifications")
        spine_spec_count = arrow_cursor.fetchone()[0]
        
        # Get database file size
        import os
        arrow_db_size = os.path.getsize(arrow_db_path) if os.path.exists(arrow_db_path) else 0
        
        arrow_conn.close()
        
        # Get user database statistics
        user_conn = user_db.get_connection()
        user_cursor = user_conn.cursor()
        
        user_cursor.execute("SELECT COUNT(*) FROM users")
        user_count = user_cursor.fetchone()[0]
        
        user_cursor.execute("SELECT COUNT(*) FROM bow_setups")
        bow_setup_count = user_cursor.fetchone()[0]
        
        user_cursor.execute("SELECT COUNT(*) FROM setup_arrows")
        setup_arrow_count = user_cursor.fetchone()[0]
        
        # Get user database file size
        user_db_size = os.path.getsize(user_db_path) if os.path.exists(user_db_path) else 0
        
        user_conn.close()
        
        # Get system information
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Calculate uptime in hours
        import time
        start_time_value = globals().get('start_time', time.time())
        uptime_seconds = time.time() - start_time_value
        uptime_hours = round(uptime_seconds / 3600, 1)
        
        # Environment information
        environment = os.environ.get('NODE_ENV', 'development')
        api_port = os.environ.get('API_PORT', '5000')
        domain = os.environ.get('DOMAIN_NAME', 'localhost')
        ssl_enabled = os.environ.get('SSL_ENABLED', 'false').lower() == 'true'
        
        # Calculate response time (simple estimate)
        request_start_time = time.time()
        response_time_ms = round((time.time() - request_start_time) * 1000, 1)
        
        system_info = {
            'system': {
                'platform': platform.system(),
                'platform_release': platform.release(),
                'platform_version': platform.version(),
                'architecture': platform.machine(),
                'processor': platform.processor(),
                'python_version': platform.python_version(),
                'hostname': platform.node()
            },
            'resources': {
                'memory_total_gb': round(memory.total / (1024**3), 2),
                'memory_used_gb': round((memory.total - memory.available) / (1024**3), 2),
                'memory_usage_percent': round(memory.percent, 1),
                'disk_total_gb': round(disk.total / (1024**3), 2),
                'disk_used_gb': round(disk.used / (1024**3), 2),
                'disk_free_gb': round(disk.free / (1024**3), 2),
                'disk_usage_percent': round(disk.percent, 1),
                'uptime_hours': uptime_hours
            },
            'environment': {
                'node_env': environment,
                'api_port': api_port,
                'domain_name': domain,
                'ssl_enabled': ssl_enabled,
                'api_base_url': f"{'https' if ssl_enabled else 'http'}://{domain}:{api_port}" if domain != 'localhost' else f"http://localhost:{api_port}"
            },
            'databases': {
                'arrow_db': {
                    'location': arrow_db_path,
                    'size_bytes': arrow_db_size,
                    'size_mb': round(arrow_db_size / (1024 * 1024), 2),
                    'exists': os.path.exists(arrow_db_path),
                    'readable': os.access(arrow_db_path, os.R_OK) if os.path.exists(arrow_db_path) else False,
                    'writable': os.access(arrow_db_path, os.W_OK) if os.path.exists(arrow_db_path) else False,
                    'stats': {
                        'total_arrows': arrow_count,
                        'total_manufacturers': manufacturer_count,
                        'total_specifications': spine_spec_count
                    }
                },
                'user_db': {
                    'location': user_db_path,
                    'size_bytes': user_db_size,
                    'size_mb': round(user_db_size / (1024 * 1024), 2),
                    'exists': os.path.exists(user_db_path),
                    'readable': os.access(user_db_path, os.R_OK) if os.path.exists(user_db_path) else False,
                    'writable': os.access(user_db_path, os.W_OK) if os.path.exists(user_db_path) else False,
                    'stats': {
                        'total_users': user_count,
                        'total_bow_setups': bow_setup_count,
                        'total_setup_arrows': setup_arrow_count
                    }
                }
            },
            'health': {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'response_time_ms': response_time_ms
            }
        }
        
        return jsonify(system_info)
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to get system information: {str(e)}',
            'health': {
                'status': 'error',
                'timestamp': datetime.now().isoformat()
            }
        }), 500

@app.route('/api/admin/batch-fill/preview', methods=['POST'])
@token_required
@admin_required
def preview_batch_fill(current_user):
    """Preview batch fill operation for missing length data"""
    try:
        data = request.get_json()
        manufacturer = data.get('manufacturer')
        reference_arrow_id = data.get('reference_arrow_id')
        
        if not manufacturer or not reference_arrow_id:
            return jsonify({'error': 'Manufacturer and reference arrow ID are required'}), 400
        
        arrow_db = ArrowDatabase()
        conn = arrow_db.get_connection()
        cursor = conn.cursor()
        
        # Get reference arrow with complete length data
        cursor.execute('''
            SELECT a.id, a.model_name, a.manufacturer,
                   COUNT(ss.id) as spine_count,
                   SUM(CASE WHEN ss.length_options IS NOT NULL AND ss.length_options != '[]' AND ss.length_options != 'null' THEN 1 ELSE 0 END) as complete_lengths
            FROM arrows a
            JOIN spine_specifications ss ON a.id = ss.arrow_id
            WHERE a.id = ? AND a.manufacturer = ?
            GROUP BY a.id, a.model_name, a.manufacturer
        ''', (reference_arrow_id, manufacturer))
        
        reference_arrow = cursor.fetchone()
        
        if not reference_arrow:
            conn.close()
            return jsonify({'error': 'Reference arrow not found'}), 404
        
        if reference_arrow['complete_lengths'] == 0:
            conn.close()
            return jsonify({'error': 'Reference arrow has no length data to copy'}), 400
        
        # Get reference length data by spine
        cursor.execute('''
            SELECT spine, length_options
            FROM spine_specifications
            WHERE arrow_id = ? AND length_options IS NOT NULL 
            AND length_options != '[]' AND length_options != 'null'
        ''', (reference_arrow_id,))
        
        reference_lengths = {str(row['spine']): row['length_options'] for row in cursor.fetchall()}
        
        if not reference_lengths:
            conn.close()
            return jsonify({'error': 'Reference arrow has no valid length data'}), 400
        
        # Find arrows from same manufacturer with missing length data
        cursor.execute('''
            SELECT DISTINCT a.id, a.model_name, a.manufacturer,
                   COUNT(ss.id) as total_spines,
                   SUM(CASE WHEN ss.length_options IS NULL OR ss.length_options = '[]' OR ss.length_options = 'null' THEN 1 ELSE 0 END) as missing_lengths,
                   GROUP_CONCAT(CASE WHEN ss.length_options IS NULL OR ss.length_options = '[]' OR ss.length_options = 'null' THEN ss.spine END) as missing_spine_list
            FROM arrows a
            JOIN spine_specifications ss ON a.id = ss.arrow_id
            WHERE a.manufacturer = ? AND a.id != ?
            GROUP BY a.id, a.model_name, a.manufacturer
            HAVING missing_lengths > 0
            ORDER BY a.model_name
        ''', (manufacturer, reference_arrow_id))
        
        target_arrows = cursor.fetchall()
        
        # Calculate what would be filled for each arrow
        preview_results = []
        total_updates = 0
        
        for arrow in target_arrows:
            missing_spines = arrow['missing_spine_list'].split(',') if arrow['missing_spine_list'] else []
            fillable_spines = []
            
            for spine in missing_spines:
                if spine.strip() in reference_lengths:
                    fillable_spines.append({
                        'spine': spine.strip(),
                        'length_data': reference_lengths[spine.strip()]
                    })
            
            if fillable_spines:
                preview_results.append({
                    'arrow_id': arrow['id'],
                    'model_name': arrow['model_name'],
                    'total_spines': arrow['total_spines'],
                    'missing_lengths': arrow['missing_lengths'],
                    'fillable_count': len(fillable_spines),
                    'fillable_spines': fillable_spines
                })
                total_updates += len(fillable_spines)
        
        conn.close()
        
        return jsonify({
            'reference_arrow': {
                'id': reference_arrow['id'],
                'model_name': reference_arrow['model_name'],
                'manufacturer': reference_arrow['manufacturer'],
                'complete_lengths': reference_arrow['complete_lengths'],
                'available_spines': list(reference_lengths.keys())
            },
            'target_arrows': preview_results,
            'summary': {
                'manufacturer': manufacturer,
                'arrows_to_update': len(preview_results),
                'total_spine_updates': total_updates,
                'reference_spines_available': len(reference_lengths)
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to preview batch fill: {str(e)}'}), 500

@app.route('/api/admin/batch-fill/execute', methods=['POST'])
@token_required
@admin_required
def execute_batch_fill(current_user):
    """Execute batch fill operation for missing length data"""
    try:
        data = request.get_json()
        manufacturer = data.get('manufacturer')
        reference_arrow_id = data.get('reference_arrow_id')
        confirm = data.get('confirm', False)
        
        if not manufacturer or not reference_arrow_id:
            return jsonify({'error': 'Manufacturer and reference arrow ID are required'}), 400
        
        if not confirm:
            return jsonify({'error': 'Confirmation required for batch operation'}), 400
        
        arrow_db = ArrowDatabase()
        conn = arrow_db.get_connection()
        cursor = conn.cursor()
        
        # Get reference length data by spine
        cursor.execute('''
            SELECT spine, length_options
            FROM spine_specifications
            WHERE arrow_id = ? AND length_options IS NOT NULL 
            AND length_options != '[]' AND length_options != 'null'
        ''', (reference_arrow_id,))
        
        reference_lengths = {str(row['spine']): row['length_options'] for row in cursor.fetchall()}
        
        if not reference_lengths:
            conn.close()
            return jsonify({'error': 'Reference arrow has no valid length data'}), 400
        
        # Find spine specifications that need updates
        cursor.execute('''
            SELECT ss.id, ss.arrow_id, ss.spine, a.model_name
            FROM spine_specifications ss
            JOIN arrows a ON ss.arrow_id = a.id
            WHERE a.manufacturer = ? AND a.id != ? 
            AND (ss.length_options IS NULL OR ss.length_options = '[]' OR ss.length_options = 'null')
            AND CAST(ss.spine AS TEXT) IN ({})
        '''.format(','.join('?' * len(reference_lengths))), 
        (manufacturer, reference_arrow_id, *reference_lengths.keys()))
        
        specs_to_update = cursor.fetchall()
        
        # Execute updates
        updated_count = 0
        updated_arrows = set()
        
        for spec in specs_to_update:
            spine_str = str(spec['spine'])
            if spine_str in reference_lengths:
                cursor.execute('''
                    UPDATE spine_specifications 
                    SET length_options = ?
                    WHERE id = ?
                ''', (reference_lengths[spine_str], spec['id']))
                updated_count += 1
                updated_arrows.add(spec['model_name'])
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Successfully updated {updated_count} spine specifications',
            'summary': {
                'manufacturer': manufacturer,
                'updated_spine_specs': updated_count,
                'updated_arrows_count': len(updated_arrows),
                'updated_arrows': sorted(list(updated_arrows)),
                'reference_arrow_id': reference_arrow_id
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to execute batch fill: {str(e)}'}), 500

@app.route('/api/admin/manufacturers/<manufacturer>/length-stats', methods=['GET'])
@token_required
@admin_required
def get_manufacturer_length_stats(current_user, manufacturer):
    """Get length data completeness stats for a manufacturer"""
    try:
        arrow_db = ArrowDatabase()
        conn = arrow_db.get_connection()
        cursor = conn.cursor()
        
        # Get arrows with length data stats
        cursor.execute('''
            SELECT a.id, a.model_name,
                   COUNT(ss.id) as total_spines,
                   SUM(CASE WHEN ss.length_options IS NOT NULL AND ss.length_options != '[]' AND ss.length_options != 'null' THEN 1 ELSE 0 END) as complete_lengths,
                   ROUND(
                       CAST(SUM(CASE WHEN ss.length_options IS NOT NULL AND ss.length_options != '[]' AND ss.length_options != 'null' THEN 1 ELSE 0 END) AS FLOAT) * 100.0 / COUNT(ss.id)
                   , 1) as completion_percentage
            FROM arrows a
            JOIN spine_specifications ss ON a.id = ss.arrow_id
            WHERE a.manufacturer = ?
            GROUP BY a.id, a.model_name
            ORDER BY completion_percentage DESC, a.model_name
        ''', (manufacturer,))
        
        arrows = cursor.fetchall()
        
        # Find potential reference arrows (100% complete)
        reference_candidates = [arrow for arrow in arrows if arrow['completion_percentage'] == 100.0]
        
        # Calculate overall stats
        total_arrows = len(arrows)
        fully_complete = len(reference_candidates)
        partially_complete = len([arrow for arrow in arrows if 0 < arrow['completion_percentage'] < 100])
        completely_missing = len([arrow for arrow in arrows if arrow['completion_percentage'] == 0])
        
        conn.close()
        
        return jsonify({
            'manufacturer': manufacturer,
            'statistics': {
                'total_arrows': total_arrows,
                'fully_complete': fully_complete,
                'partially_complete': partially_complete,
                'completely_missing': completely_missing
            },
            'arrows': [dict(arrow) for arrow in arrows],
            'reference_candidates': [dict(arrow) for arrow in reference_candidates]
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get manufacturer length stats: {str(e)}'}), 500

@app.route('/api/admin/scrape-url', methods=['POST'])
@token_required
@admin_required
def scrape_url_admin(current_user):
    """Scrape arrow data from a specific URL and update existing records"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        manufacturer = data.get('manufacturer', '').strip()
        
        if not manufacturer:
            return jsonify({'error': 'Manufacturer name is required'}), 400
        
        import subprocess
        import tempfile
        import json
        from datetime import datetime
        from arrow_database import ArrowDatabase
        import requests
        from urllib.parse import urlparse
        
        # If URL is provided, try to scrape it specifically
        if url:
            try:
                # Create a simple web scraper for the specific URL
                import requests
                from bs4 import BeautifulSoup
                
                # Get the webpage content
                response = requests.get(url, timeout=30, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                })
                
                if response.status_code != 200:
                    return jsonify({'error': f'Failed to fetch URL: HTTP {response.status_code}'}), 400
                
                # Parse the content
                soup = BeautifulSoup(response.content, 'html.parser')
                page_text = soup.get_text()
                
                # Look for arrow specifications in the text
                import re
                
                # First try to extract from HTML tables (more reliable)
                specifications = []
                
                # Look for specification tables (like Easton's format)
                tables = soup.find_all('table')
                
                for table in tables:
                    # Check if this looks like a specifications table
                    header_row = table.find('thead')
                    if header_row:
                        headers = [th.get_text().strip().lower() for th in header_row.find_all('th')]
                        
                        # Look for columns that indicate spine specifications
                        if any('gpi' in h or 'weight' in h for h in headers) and any('size' in h or 'spine' in h for h in headers):
                            print(f"Found specifications table with headers: {headers}")
                            
                            # Extract data from table rows
                            tbody = table.find('tbody')
                            if tbody:
                                for row in tbody.find_all('tr'):
                                    cells = row.find_all('td')
                                    if len(cells) >= 3:
                                        try:
                                            # Assume: Column 1 = spine, Column 2 = GPI, Column 3 = diameter
                                            spine_text = cells[0].get_text().strip()
                                            gpi_text = cells[1].get_text().strip()
                                            diameter_text = cells[2].get_text().strip()
                                            
                                            # Extract numeric values
                                            spine_num = int(re.search(r'\d+', spine_text).group())
                                            gpi_num = float(re.search(r'\d+\.?\d*', gpi_text).group())
                                            diameter_num = float(re.search(r'\d+\.?\d*', diameter_text).group())
                                            
                                            specifications.append({
                                                'spine': spine_num,
                                                'gpi': gpi_num,
                                                'diameter': diameter_num
                                            })
                                            
                                        except (ValueError, AttributeError):
                                            continue
                
                # Fallback to text-based extraction if no table found
                if not specifications:
                    # Extract potential spine values
                    spine_matches = re.findall(r'\b(\d{2,4})\s*(?:spine|stiffness)', page_text, re.IGNORECASE)
                    
                    # Extract potential GPI values
                    gpi_matches = re.findall(r'(\d+\.?\d*)\s*gpi', page_text, re.IGNORECASE)
                
                    # Extract diameter values (fallback)
                    diameter_matches = re.findall(r'(\d+\.?\d*)\s*(?:diameter|dia)', page_text, re.IGNORECASE)
                    
                    # Convert text matches to specifications format
                    for spine_str in spine_matches:
                        try:
                            spine_num = int(spine_str)
                            # Try to find corresponding GPI and diameter
                            gpi_num = float(gpi_matches[0]) if gpi_matches else 8.0  # Default GPI
                            diameter_num = float(diameter_matches[0]) if diameter_matches else 0.246  # Default diameter
                            
                            specifications.append({
                                'spine': spine_num,
                                'gpi': gpi_num,
                                'diameter': diameter_num
                            })
                        except ValueError:
                            continue
                
                # Extract potential model name
                title = soup.find('title')
                model_name = title.text.strip() if title else urlparse(url).path.split('/')[-1]
                
                if not specifications:
                    return jsonify({
                        'error': 'No spine specifications found on the webpage. Please ensure the URL contains arrow specification tables or spine data.',
                        'extracted_text_sample': page_text[:500] + '...' if len(page_text) > 500 else page_text
                    }), 400
                
                # Try to find existing arrow in database
                arrow_db = ArrowDatabase()
                conn = arrow_db.get_connection()
                cursor = conn.cursor()
                
                # Look for existing arrows from this manufacturer
                cursor.execute('''
                    SELECT a.id, a.model_name, a.description, COUNT(ss.id) as existing_spine_count
                    FROM arrows a
                    LEFT JOIN spine_specifications ss ON a.id = ss.arrow_id  
                    WHERE a.manufacturer LIKE ? OR a.manufacturer LIKE ?
                    GROUP BY a.id, a.model_name, a.description
                    ORDER BY a.created_at DESC
                    LIMIT 10
                ''', (f"%{manufacturer}%", manufacturer))
                
                existing_arrows = cursor.fetchall()
                
                # Process spine specifications
                specs_updated = 0
                arrows_updated = 0
                
                if existing_arrows:
                    # Try to match and update existing arrows
                    for arrow_row in existing_arrows:
                        arrow_id = arrow_row['id']
                        existing_spine_count = arrow_row['existing_spine_count']
                        
                        arrow_updated = False
                        
                        # Add missing spine specifications
                        for spec in specifications:
                            spine_val = spec['spine']
                            gpi_val = spec['gpi']
                            diameter_val = spec['diameter']
                            
                            try:
                                # Check if this spine already exists
                                cursor.execute('SELECT id FROM spine_specifications WHERE arrow_id = ? AND spine = ?', (arrow_id, spine_val))
                                existing_spec = cursor.fetchone()
                                
                                if existing_spec:
                                    # Update existing specification with better data
                                    cursor.execute('''
                                        UPDATE spine_specifications 
                                        SET gpi_weight = ?, outer_diameter = ?
                                        WHERE arrow_id = ? AND spine = ?
                                    ''', (gpi_val, diameter_val, arrow_id, spine_val))
                                    specs_updated += 1
                                    arrow_updated = True
                                else:
                                    # Insert new spine specification
                                    cursor.execute('''
                                        INSERT INTO spine_specifications (arrow_id, spine, outer_diameter, gpi_weight)
                                        VALUES (?, ?, ?, ?)
                                    ''', (arrow_id, spine_val, diameter_val, gpi_val))
                                    specs_updated += 1
                                    arrow_updated = True
                                
                            except (ValueError, TypeError) as e:
                                print(f"Error processing specification: {e}")
                                continue
                        
                        if arrow_updated:
                            # Update the arrow's scraped_at timestamp and source URL
                            cursor.execute('''
                                UPDATE arrows SET source_url = ?, scraped_at = CURRENT_TIMESTAMP WHERE id = ?
                            ''', (url, arrow_id))
                            arrows_updated += 1
                
                else:
                    # Create new arrow if none found
                    cursor.execute('''
                        INSERT INTO arrows (manufacturer, model_name, source_url, scraped_at)
                        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                    ''', (manufacturer, model_name[:100], url))
                    
                    arrow_id = cursor.lastrowid
                    arrows_updated = 1
                    
                    # Add spine specifications
                    for spec in specifications:
                        spine_val = spec['spine']
                        gpi_val = spec['gpi']
                        diameter_val = spec['diameter']
                        
                        try:
                            cursor.execute('''
                                INSERT INTO spine_specifications (arrow_id, spine, outer_diameter, gpi_weight)
                                VALUES (?, ?, ?, ?)
                            ''', (arrow_id, spine_val, diameter_val, gpi_val))
                            
                            specs_updated += 1
                            
                        except (ValueError, TypeError) as e:
                            print(f"Error inserting specification: {e}")
                            continue
                
                conn.commit()
                conn.close()
                
                if arrows_updated > 0 or specs_updated > 0:
                    return jsonify({
                        'success': True,
                        'message': f'Successfully updated {arrows_updated} arrow(s) with {specs_updated} spine specifications from URL',
                        'data': {
                            'manufacturer': manufacturer,
                            'arrows_updated': arrows_updated,
                            'spine_specs_added': specs_updated,
                            'url': url,
                            'extracted_specifications': specifications,
                            'specifications_count': len(specifications)
                        }
                    })
                else:
                    return jsonify({
                        'error': 'No new data was added. The specifications may already exist or could not be parsed.',
                        'extracted_specifications': specifications,
                        'specifications_count': len(specifications)
                    }), 400
                
            except requests.RequestException as e:
                return jsonify({'error': f'Failed to fetch URL: {str(e)}'}), 400
            except Exception as e:
                return jsonify({'error': f'Error processing URL: {str(e)}'}), 500
        
        else:
            # Fall back to manufacturer scraper if no URL provided
            try:
                # Get initial spine spec count for the manufacturer
                arrow_db = ArrowDatabase()
                conn = arrow_db.get_connection()
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT COUNT(ss.id) as spec_count
                    FROM arrows a
                    JOIN spine_specifications ss ON a.id = ss.arrow_id
                    WHERE a.manufacturer LIKE ?
                ''', (f"%{manufacturer}%",))
                
                initial_specs = cursor.fetchone()['spec_count']
                conn.close()
                
                # Run the scraper using subprocess
                script_dir = os.path.dirname(os.path.abspath(__file__))
                
                venv_python = os.path.join(script_dir, 'venv', 'bin', 'python')
                python_cmd = venv_python if os.path.exists(venv_python) else 'python3'
                
                cmd = [python_cmd, 'main.py', '--manufacturer', manufacturer, '--limit', '3', '--use-deepseek']
                
                process = subprocess.run(
                    cmd, 
                    cwd=script_dir,
                    capture_output=True, 
                    text=True, 
                    timeout=180,  # 3 minute timeout
                    env={**os.environ, 'PYTHONPATH': script_dir}
                )
                
                if process.returncode != 0:
                    error_msg = process.stderr if process.stderr else "Unknown error occurred"
                    return jsonify({
                        'error': f'Scraper process failed: {error_msg[:300]}...',
                        'stdout': process.stdout[-300:] if process.stdout else ''
                    }), 500
                
                # Get final spine spec count
                conn = arrow_db.get_connection()
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT COUNT(ss.id) as spec_count
                    FROM arrows a
                    JOIN spine_specifications ss ON a.id = ss.arrow_id
                    WHERE a.manufacturer LIKE ?
                ''', (f"%{manufacturer}%",))
                
                final_specs = cursor.fetchone()['spec_count']
                
                cursor.execute('''
                    SELECT model_name
                    FROM arrows a
                    WHERE a.manufacturer LIKE ? AND a.scraped_at > datetime('now', '-10 minutes')
                    ORDER BY a.scraped_at DESC
                    LIMIT 5
                ''', (f"%{manufacturer}%",))
                
                recent_arrows = [row['model_name'] for row in cursor.fetchall()]
                conn.close()
                
                specs_added = final_specs - initial_specs
                
                return jsonify({
                    'success': True,
                    'message': f'Successfully ran manufacturer scraper and added {specs_added} spine specifications',
                    'data': {
                        'manufacturer': manufacturer,
                        'arrows_updated': len(recent_arrows),
                        'spine_specs_added': specs_added,
                        'arrow_models': recent_arrows,
                        'scraper_output': process.stdout[-500:] if process.stdout else ''
                    }
                })
                
            except subprocess.TimeoutExpired:
                return jsonify({'error': 'Scraping timed out after 3 minutes'}), 408
            except Exception as e:
                return jsonify({'error': f'Scraping process error: {str(e)}'}), 500
        
    except Exception as e:
        return jsonify({'error': f'Failed to process scraping request: {str(e)}'}), 500

@app.route('/api/admin/scrape-status/<task_id>', methods=['GET'])
@token_required
@admin_required
def get_scrape_status(current_user, task_id):
    """Get status of a scraping task (for future async implementation)"""
    # Placeholder for future async scraping with task tracking
    return jsonify({
        'task_id': task_id,
        'status': 'completed',
        'message': 'Scraping completed successfully'
    })

# ================================
# SPINE DATA MANAGEMENT ENDPOINTS
# ================================

@app.route('/api/admin/spine-data/parameters', methods=['GET'])
@token_required
@admin_required
def get_spine_calculation_parameters(current_user):
    """Get all spine calculation parameters"""
    try:
        spine_service = get_spine_service()
        if not spine_service:
            return jsonify({'error': 'Spine service not available'}), 500
        
        # Get parameters by group
        base_params = spine_service.get_calculation_parameters('base_calculation')
        bow_adjustments = spine_service.get_calculation_parameters('bow_adjustments')
        safety_factors = spine_service.get_calculation_parameters('safety_factors')
        material_factors = spine_service.get_calculation_parameters('material_factors')
        
        return jsonify({
            'base_calculation': base_params,
            'bow_adjustments': bow_adjustments,
            'safety_factors': safety_factors,
            'material_factors': material_factors
        })
    except Exception as e:
        print(f"Error getting spine calculation parameters: {e}")
        return jsonify({'error': 'Failed to get spine calculation parameters'}), 500

@app.route('/api/admin/spine-data/parameters/<parameter_group>/<parameter_name>', methods=['PUT'])
@token_required
@admin_required
def update_spine_calculation_parameter(current_user, parameter_group, parameter_name):
    """Update a spine calculation parameter"""
    try:
        data = request.get_json()
        new_value = data.get('value')
        
        if new_value is None:
            return jsonify({'error': 'Parameter value is required'}), 400
        
        # Update parameter in database
        from arrow_database import ArrowDatabase
        db = ArrowDatabase()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE calculation_parameters 
            SET parameter_value = ?, updated_at = CURRENT_TIMESTAMP, last_modified_by = ?
            WHERE parameter_group = ? AND parameter_name = ?
        """, (new_value, current_user['id'], parameter_group, parameter_name))
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'error': 'Parameter not found'}), 404
        
        conn.commit()
        conn.close()
        
        # Clear cache to force refresh
        spine_service = get_spine_service()
        if spine_service:
            cache_key = f"params_{parameter_group}"
            if cache_key in spine_service._cache:
                del spine_service._cache[cache_key]
        
        return jsonify({'message': 'Parameter updated successfully'})
    except Exception as e:
        print(f"Error updating spine calculation parameter: {e}")
        return jsonify({'error': 'Failed to update parameter'}), 500

@app.route('/api/admin/spine-data/materials', methods=['GET'])
@token_required
@admin_required
def get_spine_materials(current_user):
    """Get all arrow material properties"""
    try:
        spine_service = get_spine_service()
        if not spine_service:
            return jsonify({'error': 'Spine service not available'}), 500
        
        materials = spine_service.get_material_properties()
        return jsonify({'materials': materials})
    except Exception as e:
        print(f"Error getting spine materials: {e}")
        return jsonify({'error': 'Failed to get material properties'}), 500

@app.route('/api/admin/spine-data/materials/<material_name>', methods=['PUT'])
@token_required
@admin_required
def update_spine_material(current_user, material_name):
    """Update arrow material properties"""
    try:
        data = request.get_json()
        
        # Update material in database
        from arrow_database import ArrowDatabase
        db = ArrowDatabase()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Build update query dynamically
        update_fields = []
        params = []
        
        for field in ['density', 'elasticity_modulus', 'strength_factor', 'spine_adjustment_factor',
                     'temperature_coefficient', 'humidity_resistance_rating', 'description', 'typical_use']:
            if field in data:
                update_fields.append(f"{field} = ?")
                params.append(data[field])
        
        if not update_fields:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        params.append(material_name)
        
        cursor.execute(f"""
            UPDATE arrow_material_properties 
            SET {', '.join(update_fields)}
            WHERE material_name = ?
        """, params)
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'error': 'Material not found'}), 404
        
        conn.commit()
        conn.close()
        
        # Clear cache to force refresh
        spine_service = get_spine_service()
        if spine_service:
            cache_key = f"materials_{material_name.lower()}"
            if cache_key in spine_service._cache:
                del spine_service._cache[cache_key]
            if "materials_all" in spine_service._cache:
                del spine_service._cache["materials_all"]
        
        return jsonify({'message': 'Material updated successfully'})
    except Exception as e:
        print(f"Error updating spine material: {e}")
        return jsonify({'error': 'Failed to update material'}), 500

@app.route('/api/admin/spine-data/materials', methods=['POST'])
@token_required
@admin_required
def create_spine_material(current_user):
    """Create new arrow material properties"""
    try:
        data = request.get_json()
        material_name = data.get('material_name')
        
        if not material_name:
            return jsonify({'error': 'Material name is required'}), 400
        
        # Insert new material in database
        from arrow_database import ArrowDatabase
        db = ArrowDatabase()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO arrow_material_properties 
            (material_name, density, elasticity_modulus, strength_factor, spine_adjustment_factor,
             temperature_coefficient, humidity_resistance_rating, description, typical_use)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            material_name,
            data.get('density', 1.0),
            data.get('elasticity_modulus', 100.0),
            data.get('strength_factor', 1.0),
            data.get('spine_adjustment_factor', 1.0),
            data.get('temperature_coefficient', 0.0001),
            data.get('humidity_resistance_rating', 5),
            data.get('description', f'Properties for {material_name} arrows'),
            data.get('typical_use', 'General use')
        ))
        
        conn.commit()
        conn.close()
        
        # Clear cache to force refresh
        spine_service = get_spine_service()
        if spine_service:
            if "materials_all" in spine_service._cache:
                del spine_service._cache["materials_all"]
        
        return jsonify({'message': 'Material created successfully'}), 201
    except Exception as e:
        print(f"Error creating spine material: {e}")
        return jsonify({'error': 'Failed to create material'}), 500

@app.route('/api/admin/spine-data/manufacturer-charts', methods=['GET'])
@token_required
@admin_required
def get_manufacturer_spine_charts(current_user):
    """Get all manufacturer spine charts"""
    try:
        from arrow_database import ArrowDatabase
        db = ArrowDatabase()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM manufacturer_spine_charts 
            WHERE is_active = 1 
            ORDER BY manufacturer, bow_type, draw_weight_min
        """)
        
        charts = []
        for row in cursor.fetchall():
            charts.append(dict(row))
        
        conn.close()
        return jsonify({'charts': charts})
    except Exception as e:
        print(f"Error getting manufacturer spine charts: {e}")
        return jsonify({'error': 'Failed to get manufacturer spine charts'}), 500

@app.route('/api/admin/spine-data/flight-problems', methods=['GET'])
@token_required
@admin_required
def get_flight_problems(current_user):
    """Get all flight problem diagnostics"""
    try:
        spine_service = get_spine_service()
        if not spine_service:
            return jsonify({'error': 'Spine service not available'}), 500
        
        problems = spine_service.get_flight_problem_diagnostics()
        return jsonify({'problems': problems})
    except Exception as e:
        print(f"Error getting flight problems: {e}")
        return jsonify({'error': 'Failed to get flight problem diagnostics'}), 500

@app.route('/api/admin/spine-data/test-calculation', methods=['POST'])
@token_required
@admin_required
def test_spine_calculation(current_user):
    """Test spine calculation with current parameters"""
    try:
        data = request.get_json()
        
        spine_service = get_spine_service()
        if not spine_service:
            return jsonify({'error': 'Spine service not available'}), 500
        
        # Test both standard and enhanced calculations
        standard_result = spine_service.calculate_spine(
            draw_weight=data.get('draw_weight', 50.0),
            arrow_length=data.get('arrow_length', 29.0),
            point_weight=data.get('point_weight', 125.0),
            bow_type=data.get('bow_type', 'compound')
        )
        
        enhanced_result = spine_service.calculate_enhanced_spine(
            draw_weight=data.get('draw_weight', 50.0),
            arrow_length=data.get('arrow_length', 29.0),
            point_weight=data.get('point_weight', 125.0),
            bow_type=data.get('bow_type', 'compound'),
            material_preference=data.get('material_preference'),
            manufacturer_preference=data.get('manufacturer_preference')
        )
        
        return jsonify({
            'standard_calculation': standard_result,
            'enhanced_calculation': enhanced_result
        })
    except Exception as e:
        print(f"Error testing spine calculation: {e}")
        return jsonify({'error': 'Failed to test spine calculation'}), 500

# ==========================================
# Enhanced Manufacturer Spine Chart API Endpoints
# ==========================================

@app.route('/api/calculator/manufacturers', methods=['GET'])
def get_spine_chart_manufacturers():
    """Get list of manufacturers with spine charts available"""
    try:
        db = get_database()
        if not db:
            return jsonify({'error': 'Database not available'}), 500
        
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Get manufacturers from enhanced spine charts
        cursor.execute("""
            SELECT DISTINCT manufacturer, 
                   COUNT(*) as chart_count,
                   GROUP_CONCAT(DISTINCT bow_type) as bow_types
            FROM manufacturer_spine_charts_enhanced 
            WHERE is_active = 1 
            GROUP BY manufacturer
            ORDER BY manufacturer
        """)
        
        manufacturers = []
        for row in cursor.fetchall():
            manufacturers.append({
                'manufacturer': row[0],
                'chart_count': row[1],
                'bow_types': row[2].split(',') if row[2] else []
            })
        
        conn.close()
        return jsonify({'manufacturers': manufacturers})
    except Exception as e:
        print(f"Error getting spine chart manufacturers: {e}")
        return jsonify({'error': 'Failed to get manufacturers'}), 500

@app.route('/api/calculator/manufacturers/<manufacturer>/charts', methods=['GET'])
def get_manufacturer_charts_for_calculator(manufacturer):
    """Get spine charts for a specific manufacturer"""
    try:
        db = get_database()
        if not db:
            return jsonify({'error': 'Database not available'}), 500
        
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Get charts for the manufacturer
        cursor.execute("""
            SELECT id, manufacturer, model, bow_type, grid_definition, spine_grid, 
                   provenance, spine_system, chart_notes, created_at
            FROM manufacturer_spine_charts_enhanced 
            WHERE manufacturer = ? AND is_active = 1 
            ORDER BY bow_type, model
        """, (manufacturer,))
        
        charts = []
        for row in cursor.fetchall():
            chart = {
                'id': row[0],
                'manufacturer': row[1],
                'model': row[2],
                'bow_type': row[3],
                'grid_definition': json.loads(row[4]) if row[4] else {},
                'spine_grid': json.loads(row[5]) if row[5] else [],
                'provenance': row[6],
                'spine_system': row[7],
                'chart_notes': row[8],
                'created_at': row[9]
            }
            charts.append(chart)
        
        conn.close()
        return jsonify({
            'manufacturer': manufacturer,
            'charts': charts
        })
    except Exception as e:
        print(f"Error getting charts for manufacturer {manufacturer}: {e}")
        return jsonify({'error': f'Failed to get charts for {manufacturer}'}), 500

@app.route('/api/calculator/spine-recommendation-enhanced', methods=['POST'])
def calculate_enhanced_spine_recommendation():
    """Enhanced spine calculation using manufacturer-specific charts"""
    try:
        data = request.get_json()
        
        # Extract bow configuration
        bow_config = data.get('bow_config', {})
        manufacturer_preference = data.get('manufacturer_preference')
        chart_id = data.get('chart_id')  # Specific chart to use
        
        # Get basic spine calculation first
        draw_weight = bow_config.get('draw_weight', 50)
        draw_length = bow_config.get('draw_length', 29)
        arrow_length = bow_config.get('arrow_length', 29)
        bow_type = bow_config.get('bow_type', 'compound')
        point_weight = bow_config.get('point_weight', 125)
        arrow_material = bow_config.get('arrow_material', 'carbon')
        
        # Calculate adjustments using imported formulas
        effective_bow_weight = calculate_effective_bow_weight(
            draw_weight, arrow_length, point_weight, bow_config
        )
        
        # Get manufacturer-specific recommendation if available
        manufacturer_recommendation = None
        if manufacturer_preference or chart_id:
            manufacturer_recommendation = get_manufacturer_spine_recommendation(
                manufacturer_preference, chart_id, bow_type, effective_bow_weight, arrow_length
            )
        
        # Get generic recommendation as fallback
        generic_recommendation = calculate_generic_spine(
            effective_bow_weight, bow_type, arrow_material
        )
        
        result = {
            'effective_bow_weight': effective_bow_weight,
            'adjustments_applied': get_applied_adjustments(bow_config),
            'generic_recommendation': generic_recommendation,
            'manufacturer_recommendation': manufacturer_recommendation,
            'recommended_spine': manufacturer_recommendation['spine'] if manufacturer_recommendation else generic_recommendation['spine'],
            'calculation_notes': get_calculation_notes(bow_config, manufacturer_recommendation)
        }
        
        return jsonify(result)
    except Exception as e:
        print(f"Error calculating enhanced spine recommendation: {e}")
        return jsonify({'error': 'Failed to calculate spine recommendation'}), 500

@app.route('/api/calculator/convert-spine', methods=['POST'])
def convert_spine_values():
    """Convert spine values between different systems"""
    try:
        data = request.get_json()
        
        from_spine = data.get('from_spine')
        from_system = data.get('from_system')  # carbon, aluminum, wood
        to_system = data.get('to_system')
        
        if not all([from_spine, from_system, to_system]):
            return jsonify({'error': 'Missing required parameters'}), 400
        
        db = get_database()
        if not db:
            return jsonify({'error': 'Database not available'}), 500
        
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Look up conversion
        conversion_type = f"{from_system}_to_{to_system}"
        cursor.execute("""
            SELECT to_spine, accuracy_note 
            FROM spine_conversion_tables 
            WHERE conversion_type = ? AND from_spine = ?
        """, (conversion_type, str(from_spine)))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return jsonify({
                'from_spine': from_spine,
                'from_system': from_system,
                'to_spine': result[0],
                'to_system': to_system,
                'accuracy_note': result[1],
                'conversion_available': True
            })
        else:
            return jsonify({
                'from_spine': from_spine,
                'from_system': from_system,
                'to_spine': None,
                'to_system': to_system,
                'accuracy_note': 'No direct conversion available',
                'conversion_available': False
            })
    except Exception as e:
        print(f"Error converting spine values: {e}")
        return jsonify({'error': 'Failed to convert spine values'}), 500

@app.route('/api/admin/spine-charts', methods=['GET'])
@token_required
@admin_required
def get_all_spine_charts(current_user):
    """Get all spine charts (manufacturer + custom) for admin"""
    try:
        db = get_database()
        if not db:
            return jsonify({'error': 'Database not available'}), 500
        
        print(f"Database path being used: {getattr(db, 'db_path', 'Unknown')}")
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%spine%'")
        tables = cursor.fetchall()
        print(f"Spine-related tables found: {[table[0] for table in tables]}")
        
        # Get manufacturer charts
        cursor.execute("""
            SELECT 'manufacturer' as chart_type, id, manufacturer, model, bow_type, 
                   spine_system, chart_notes, provenance, is_active, created_at,
                   grid_definition, spine_grid
            FROM manufacturer_spine_charts_enhanced
            ORDER BY manufacturer, model, bow_type
        """)
        
        manufacturer_charts = []
        for row in cursor.fetchall():
            manufacturer_charts.append({
                'chart_type': row[0],
                'id': row[1],
                'manufacturer': row[2],
                'model': row[3],
                'bow_type': row[4],
                'spine_system': row[5],
                'chart_notes': row[6],
                'provenance': row[7],
                'is_active': bool(row[8]),
                'created_at': row[9],
                'grid_definition': json.loads(row[10]) if row[10] else {},
                'spine_grid': json.loads(row[11]) if row[11] else []
            })
        
        # Get custom charts
        cursor.execute("""
            SELECT 'custom' as chart_type, id, manufacturer, model, bow_type, 
                   spine_system, chart_notes, created_by, is_active, created_at,
                   grid_definition, spine_grid
            FROM custom_spine_charts
            ORDER BY chart_name
        """)
        
        custom_charts = []
        for row in cursor.fetchall():
            custom_charts.append({
                'chart_type': row[0],
                'id': row[1],
                'manufacturer': row[2],
                'model': row[3],
                'bow_type': row[4],
                'spine_system': row[5],
                'chart_notes': row[6],
                'created_by': row[7],
                'is_active': bool(row[8]),
                'created_at': row[9],
                'grid_definition': json.loads(row[10]) if row[10] else {},
                'spine_grid': json.loads(row[11]) if row[11] else []
            })
        
        conn.close()
        return jsonify({
            'manufacturer_charts': manufacturer_charts,
            'custom_charts': custom_charts,
            'total_charts': len(manufacturer_charts) + len(custom_charts)
        })
    except Exception as e:
        import traceback
        print(f"Error getting all spine charts: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': f'Failed to get spine charts: {str(e)}'}), 500

@app.route('/api/admin/spine-charts/custom', methods=['POST'])
@token_required
@admin_required
def create_custom_spine_chart(current_user):
    """Create a new custom spine chart"""
    try:
        data = request.get_json()
        
        required_fields = ['chart_name', 'bow_type', 'spine_grid']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        db = get_database()
        if not db:
            return jsonify({'error': 'Database not available'}), 500
        
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO custom_spine_charts 
            (chart_name, manufacturer, model, bow_type, grid_definition, 
             spine_grid, spine_system, chart_notes, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['chart_name'],
            data.get('manufacturer', ''),
            data.get('model', ''),
            data['bow_type'],
            json.dumps(data.get('grid_definition', {})),
            json.dumps(data['spine_grid']),
            data.get('spine_system', 'standard_deflection'),
            data.get('chart_notes', ''),
            current_user['email']
        ))
        
        chart_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': 'Custom spine chart created successfully',
            'chart_id': chart_id
        }), 201
    except Exception as e:
        print(f"Error creating custom spine chart: {e}")
        return jsonify({'error': 'Failed to create custom spine chart'}), 500

@app.route('/api/admin/spine-charts/custom/<int:chart_id>', methods=['PUT'])
@token_required
@admin_required
def update_custom_spine_chart(current_user, chart_id):
    """Update a custom spine chart"""
    try:
        data = request.get_json()
        
        db = get_database()
        if not db:
            return jsonify({'error': 'Database not available'}), 500
        
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Check if chart exists and is custom
        cursor.execute("""
            SELECT created_by FROM custom_spine_charts WHERE id = ?
        """, (chart_id,))
        chart = cursor.fetchone()
        
        if not chart:
            return jsonify({'error': 'Custom chart not found'}), 404
        
        # Update the chart
        cursor.execute("""
            UPDATE custom_spine_charts 
            SET manufacturer = ?, model = ?, bow_type = ?, spine_system = ?, 
                chart_notes = ?, is_active = ?, spine_grid = ?, grid_definition = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            data.get('manufacturer', ''),
            data.get('model', ''),
            data.get('bow_type', 'compound'),
            data.get('spine_system', 'standard_deflection'),
            data.get('chart_notes', ''),
            data.get('is_active', True),
            json.dumps(data.get('spine_grid', [])),
            json.dumps(data.get('grid_definition', {})),
            chart_id
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Custom spine chart updated successfully'}), 200
    except Exception as e:
        print(f"Error updating custom spine chart: {e}")
        return jsonify({'error': 'Failed to update custom spine chart'}), 500

@app.route('/api/admin/spine-charts/custom/<int:chart_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_custom_spine_chart(current_user, chart_id):
    """Delete a custom spine chart"""
    try:
        db = get_database()
        if not db:
            return jsonify({'error': 'Database not available'}), 500
        
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Check if chart exists and is custom
        cursor.execute("""
            SELECT created_by FROM custom_spine_charts WHERE id = ?
        """, (chart_id,))
        chart = cursor.fetchone()
        
        if not chart:
            return jsonify({'error': 'Custom chart not found'}), 404
        
        # Delete the chart
        cursor.execute("DELETE FROM custom_spine_charts WHERE id = ?", (chart_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Custom spine chart deleted successfully'}), 200
    except Exception as e:
        print(f"Error deleting custom spine chart: {e}")
        return jsonify({'error': 'Failed to delete custom spine chart'}), 500

@app.route('/api/admin/spine-charts/manufacturer/<int:chart_id>/override', methods=['POST'])
@token_required
@admin_required
def create_manufacturer_override(current_user, chart_id):
    """Create a custom chart based on manufacturer chart for editing"""
    try:
        db = get_database()
        if not db:
            return jsonify({'error': 'Database not available'}), 500
        
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Get the original manufacturer chart
        cursor.execute("""
            SELECT manufacturer, model, bow_type, grid_definition, spine_grid, 
                   spine_system, chart_notes, provenance
            FROM manufacturer_spine_charts_enhanced 
            WHERE id = ?
        """, (chart_id,))
        
        original_chart = cursor.fetchone()
        if not original_chart:
            return jsonify({'error': 'Manufacturer chart not found'}), 404
        
        # Create custom chart based on manufacturer chart
        cursor.execute("""
            INSERT INTO custom_spine_charts 
            (chart_name, manufacturer, model, bow_type, grid_definition, 
             spine_grid, spine_system, chart_notes, created_by, overrides_manufacturer_chart)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            f"{original_chart[0]} {original_chart[1]} (Custom Override)",
            original_chart[0],  # manufacturer
            f"{original_chart[1]} (Custom)",  # model
            original_chart[2],  # bow_type
            original_chart[3],  # grid_definition
            original_chart[4],  # spine_grid
            original_chart[5],  # spine_system
            f"Custom override of {original_chart[0]} {original_chart[1]}. Original notes: {original_chart[6] or 'None'}",
            current_user['email'],
            True  # overrides_manufacturer_chart
        ))
        
        custom_chart_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': 'Custom override chart created successfully',
            'custom_chart_id': custom_chart_id
        }), 201
    except Exception as e:
        print(f"Error creating manufacturer override: {e}")
        return jsonify({'error': 'Failed to create manufacturer override'}), 500

# Database Migration Management API Endpoints

@app.route('/api/admin/migrations/status', methods=['GET'])
@token_required
@admin_required
def get_migration_status(current_user):
    """Get comprehensive migration status"""
    try:
        from database_migration_manager import DatabaseMigrationManager
        import json
        
        # Find database path and ensure it's a string
        db = get_database()
        if not db:
            return jsonify({'error': 'Database not available'}), 500
        
        # Always convert Path objects to strings
        if hasattr(db, 'db_path'):
            db_path = str(db.db_path)
        else:
            db_path = 'arrow_database.db'
        
        # Initialize migration manager with correct migrations directory
        migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')
        manager = DatabaseMigrationManager(db_path, migrations_dir)
        status = manager.get_migration_status()
        
        # Ensure all paths are strings for JSON serialization
        def convert_paths_to_strings(obj):
            if isinstance(obj, dict):
                return {k: convert_paths_to_strings(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_paths_to_strings(item) for item in obj]
            elif hasattr(obj, '__fspath__'):  # Path objects
                return str(obj)
            elif str(type(obj)).find('Path') != -1:  # Various Path types
                return str(obj)
            elif hasattr(obj, '__str__') and 'Path' in str(type(obj)):  # Additional Path check
                return str(obj)
            else:
                return obj
        
        # Clean the status to ensure JSON serialization
        clean_status = convert_paths_to_strings(status)
        
        return jsonify(clean_status), 200
    except Exception as e:
        print(f"Error getting migration status: {e}")
        return jsonify({'error': 'Failed to get migration status'}), 500

@app.route('/api/admin/migrations/run', methods=['POST'])
@token_required
@admin_required
def run_migrations(current_user):
    """Run pending database migrations"""
    try:
        from database_migration_manager import DatabaseMigrationManager
        import json
        
        data = request.get_json() or {}
        target_version = data.get('target_version')
        dry_run = data.get('dry_run', False)
        
        # Find database path and ensure it's a string
        db = get_database()
        if not db:
            return jsonify({'error': 'Database not available'}), 500
        
        # Always convert Path objects to strings
        if hasattr(db, 'db_path'):
            db_path = str(db.db_path)
        else:
            db_path = 'arrow_database.db'
        
        # Initialize migration manager with correct migrations directory
        migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')
        manager = DatabaseMigrationManager(db_path, migrations_dir)
        
        # Get pending migrations first
        pending = manager.get_pending_migrations()
        if not pending:
            return jsonify({
                'success': True,
                'message': 'No pending migrations',
                'applied_count': 0,
                'applied_migrations': []
            }), 200
        
        # Run migrations
        success = manager.migrate(target_version, dry_run)
        
        # Get status after migration
        status = manager.get_migration_status()
        
        # Ensure all paths are strings for JSON serialization
        def convert_paths_to_strings(obj):
            if isinstance(obj, dict):
                return {k: convert_paths_to_strings(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_paths_to_strings(item) for item in obj]
            elif hasattr(obj, '__fspath__'):  # Path objects
                return str(obj)
            elif str(type(obj)).find('Path') != -1:  # Various Path types
                return str(obj)
            elif hasattr(obj, '__str__') and 'Path' in str(type(obj)):  # Additional Path check
                return str(obj)
            else:
                return obj
        
        # Clean the status to ensure JSON serialization
        clean_status = convert_paths_to_strings(status)
        
        if success:
            response_data = {
                'success': True,
                'message': f'Successfully {"simulated" if dry_run else "applied"} {len(pending)} migrations',
                'applied_count': len(pending) if not dry_run else 0,
                'applied_migrations': [m.version for m in pending],
                'status': clean_status,
                'dry_run': dry_run
            }
            return jsonify(convert_paths_to_strings(response_data)), 200
        else:
            response_data = {
                'success': False,
                'error': 'Some migrations failed',
                'status': clean_status
            }
            return jsonify(convert_paths_to_strings(response_data)), 500
    except Exception as e:
        print(f"Error running migrations: {e}")
        return jsonify({'error': f'Failed to run migrations: {str(e)}'}), 500

@app.route('/api/admin/migrations/history', methods=['GET'])
@token_required
@admin_required
def get_migration_history(current_user):
    """Get migration history and details"""
    try:
        # Find database path
        db = get_database()
        if not db:
            return jsonify({'error': 'Database not available'}), 500
        
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Check if migrations table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='database_migrations'
        """)
        
        if not cursor.fetchone():
            return jsonify({
                'history': [],
                'total_count': 0
            }), 200
        
        # Get migration history
        cursor.execute("""
            SELECT version, name, applied_at, applied_by, environment, 
                   success, error_message, checksum
            FROM database_migrations
            ORDER BY applied_at DESC
        """)
        
        history = []
        for row in cursor.fetchall():
            history.append({
                'version': row[0],
                'name': row[1],
                'applied_at': row[2],
                'applied_by': row[3],
                'environment': row[4],
                'success': bool(row[5]),
                'error_message': row[6],
                'checksum': row[7]
            })
        
        conn.close()
        
        return jsonify({
            'history': history,
            'total_count': len(history)
        }), 200
    except Exception as e:
        print(f"Error getting migration history: {e}")
        return jsonify({'error': 'Failed to get migration history'}), 500

@app.route('/api/admin/migrations/<version>/details', methods=['GET'])
@token_required
@admin_required
def get_migration_details(current_user, version):
    """Get detailed information about a specific migration"""
    try:
        from database_migration_manager import DatabaseMigrationManager
        
        # Find database path
        db = get_database()
        if not db:
            return jsonify({'error': 'Database not available'}), 500
        
        db_path = db.db_path if hasattr(db, 'db_path') else 'arrow_database.db'
        
        # Initialize migration manager with correct migrations directory
        migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')
        manager = DatabaseMigrationManager(db_path, migrations_dir)
        details = manager.get_migration_details(version)
        
        if details:
            return jsonify(details), 200
        else:
            return jsonify({'error': f'Migration {version} not found'}), 404
    except Exception as e:
        print(f"Error getting migration details: {e}")
        return jsonify({'error': 'Failed to get migration details'}), 500

@app.route('/api/admin/migrations/validate', methods=['GET'])
@token_required
@admin_required
def validate_migrations(current_user):
    """Validate migration sequence and dependencies"""
    try:
        from database_migration_manager import DatabaseMigrationManager
        
        # Find database path
        db = get_database()
        if not db:
            return jsonify({'error': 'Database not available'}), 500
        
        db_path = db.db_path if hasattr(db, 'db_path') else 'arrow_database.db'
        
        # Initialize migration manager with correct migrations directory
        migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')
        manager = DatabaseMigrationManager(db_path, migrations_dir)
        validation_results = manager.validate_migration_sequence()
        
        return jsonify(validation_results), 200
    except Exception as e:
        print(f"Error validating migrations: {e}")
        return jsonify({'error': 'Failed to validate migrations'}), 500

# Database Health Management API Endpoints

@app.route('/api/admin/database/health', methods=['GET'])
@token_required
@admin_required
def get_database_health(current_user):
    """Get comprehensive database health report"""
    try:
        from database_health_checker import run_health_check
        import json
        
        # Find database path and ensure it's a string
        db = get_database()
        if not db:
            return jsonify({'error': 'Database not available'}), 500
        
        # Always convert Path objects to strings
        if hasattr(db, 'db_path'):
            db_path = str(db.db_path)
        else:
            db_path = 'arrow_database.db'
        
        # Run health check
        health_report = run_health_check(db_path)
        
        # Ensure all paths are strings for JSON serialization
        def convert_paths_to_strings(obj):
            if isinstance(obj, dict):
                return {k: convert_paths_to_strings(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_paths_to_strings(item) for item in obj]
            elif hasattr(obj, '__fspath__'):  # Path objects
                return str(obj)
            elif str(type(obj)).find('Path') != -1:  # Various Path types
                return str(obj)
            elif hasattr(obj, '__str__') and 'Path' in str(type(obj)):  # Additional Path check
                return str(obj)
            else:
                return obj
        
        # Clean the report to ensure JSON serialization
        clean_report = convert_paths_to_strings(health_report)
        
        return jsonify(clean_report), 200
    except Exception as e:
        print(f"Error getting database health: {e}")
        return jsonify({'error': f'Failed to get database health: {str(e)}'}), 500

@app.route('/api/admin/database/optimize', methods=['POST'])
@token_required
@admin_required
def optimize_database(current_user):
    """Run database optimization operations"""
    try:
        from database_health_checker import DatabaseHealthChecker
        
        # Find database path
        db = get_database()
        if not db:
            return jsonify({'error': 'Database not available'}), 500
        
        db_path = db.db_path if hasattr(db, 'db_path') else 'arrow_database.db'
        
        # Run optimization
        checker = DatabaseHealthChecker(db_path)
        optimization_results = checker.run_database_optimization()
        
        return jsonify({
            'success': True,
            'message': 'Database optimization completed',
            'results': optimization_results
        }), 200
    except Exception as e:
        print(f"Error optimizing database: {e}")
        return jsonify({'error': f'Failed to optimize database: {str(e)}'}), 500

@app.route('/api/admin/database/schema-verify', methods=['GET'])
@token_required
@admin_required
def verify_database_schema(current_user):
    """Verify database schema integrity"""
    try:
        from database_health_checker import DatabaseHealthChecker
        
        # Find database path
        db = get_database()
        if not db:
            return jsonify({'error': 'Database not available'}), 500
        
        db_path = db.db_path if hasattr(db, 'db_path') else 'arrow_database.db'
        
        # Verify schema
        checker = DatabaseHealthChecker(db_path)
        verification_results = checker.verify_schema_integrity()
        
        return jsonify(verification_results), 200
    except Exception as e:
        print(f"Error verifying database schema: {e}")
        return jsonify({'error': f'Failed to verify database schema: {str(e)}'}), 500

@app.route('/api/admin/database/vacuum', methods=['POST'])
@token_required
@admin_required
def vacuum_database(current_user):
    """Run VACUUM command to reclaim space"""
    try:
        # Find database path
        db = get_database()
        if not db:
            return jsonify({'error': 'Database not available'}), 500
        
        import sqlite3
        import time
        from pathlib import Path
        
        db_path = db.db_path if hasattr(db, 'db_path') else 'arrow_database.db'
        
        # Get size before
        size_before = Path(db_path).stat().st_size
        
        # Run VACUUM
        start_time = time.time()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("VACUUM")
        conn.close()
        
        # Get size after
        size_after = Path(db_path).stat().st_size
        execution_time = (time.time() - start_time) * 1000
        
        space_reclaimed_mb = (size_before - size_after) / (1024 * 1024)
        
        return jsonify({
            'success': True,
            'message': 'Database VACUUM completed',
            'execution_time_ms': round(execution_time, 2),
            'space_reclaimed_mb': round(space_reclaimed_mb, 2),
            'size_before_mb': round(size_before / (1024 * 1024), 2),
            'size_after_mb': round(size_after / (1024 * 1024), 2)
        }), 200
    except Exception as e:
        print(f"Error running VACUUM: {e}")
        return jsonify({'error': f'Failed to run VACUUM: {str(e)}'}), 500

# Helper functions for enhanced spine calculations

def calculate_effective_bow_weight(draw_weight, arrow_length, point_weight, bow_config):
    """Calculate effective bow weight with adjustments"""
    effective_weight = draw_weight
    
    # Arrow length adjustment (5 lbs per inch difference from 28")
    length_adjustment = (arrow_length - 28) * 5
    effective_weight += length_adjustment
    
    # Point weight adjustment (5 lbs per 25 grain difference from 125gr)
    point_adjustment = ((point_weight - 125) / 25) * 5
    effective_weight += point_adjustment
    
    # Bow speed adjustment (if available)
    bow_speed = bow_config.get('bow_speed')
    if bow_speed:
        if bow_speed <= 275:
            effective_weight -= 10
        elif bow_speed <= 300:
            effective_weight -= 5
        elif bow_speed <= 320:
            pass  # no adjustment
        elif bow_speed <= 340:
            effective_weight += 5
        elif bow_speed <= 350:
            effective_weight += 10
        else:
            effective_weight += 15
    
    # Release type adjustment
    release_type = bow_config.get('release_type', 'mechanical')
    if release_type == 'finger_release':
        effective_weight += 5
    
    return round(effective_weight, 1)

def get_manufacturer_spine_recommendation(manufacturer, chart_id, bow_type, effective_weight, arrow_length):
    """Get spine recommendation from manufacturer chart"""
    try:
        db = get_database()
        if not db:
            return None
        
        conn = db.get_connection()
        cursor = conn.cursor()
        
        if chart_id:
            # Use specific chart
            cursor.execute("""
                SELECT manufacturer, model, spine_grid, spine_system, chart_notes
                FROM manufacturer_spine_charts_enhanced 
                WHERE id = ? AND is_active = 1
            """, (chart_id,))
        else:
            # Find best matching chart for manufacturer and bow type
            cursor.execute("""
                SELECT manufacturer, model, spine_grid, spine_system, chart_notes
                FROM manufacturer_spine_charts_enhanced 
                WHERE manufacturer = ? AND bow_type = ? AND is_active = 1
                LIMIT 1
            """, (manufacturer, bow_type))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return None
        
        manufacturer_name, model, spine_grid_json, spine_system, notes = result
        spine_grid = json.loads(spine_grid_json)
        
        # Find matching spine from grid
        recommended_spine = find_spine_from_grid(spine_grid, effective_weight, arrow_length)
        
        if recommended_spine:
            return {
                'manufacturer': manufacturer_name,
                'model': model,
                'spine': recommended_spine,
                'spine_system': spine_system,
                'chart_notes': notes,
                'source': 'manufacturer_chart'
            }
    except Exception as e:
        print(f"Error getting manufacturer spine recommendation: {e}")
    
    return None

def find_spine_from_grid(spine_grid, effective_weight, arrow_length):
    """Find appropriate spine from manufacturer grid"""
    try:
        for entry in spine_grid:
            weight_range = entry.get('draw_weight_range_lbs', '')
            arrow_length_in_chart = entry.get('arrow_length_in', 28)
            
            # Parse weight range (e.g., "50-54")
            if '-' in weight_range:
                min_weight, max_weight = map(int, weight_range.split('-'))
            else:
                min_weight = max_weight = int(weight_range)
            
            # Check if effective weight falls in range
            if min_weight <= effective_weight <= max_weight:
                # Adjust for arrow length if needed (most charts are for 28")
                if arrow_length_in_chart == arrow_length or abs(arrow_length_in_chart - arrow_length) <= 1:
                    return entry.get('spine')
        
        # If no exact match, find closest
        closest_entry = None
        min_diff = float('inf')
        
        for entry in spine_grid:
            weight_range = entry.get('draw_weight_range_lbs', '')
            if '-' in weight_range:
                min_weight, max_weight = map(int, weight_range.split('-'))
                mid_weight = (min_weight + max_weight) / 2
            else:
                mid_weight = int(weight_range)
            
            diff = abs(mid_weight - effective_weight)
            if diff < min_diff:
                min_diff = diff
                closest_entry = entry
        
        return closest_entry.get('spine') if closest_entry else None
    except Exception as e:
        print(f"Error finding spine from grid: {e}")
        return None

def calculate_generic_spine(effective_weight, bow_type, arrow_material):
    """Calculate generic spine recommendation as fallback"""
    # Basic spine calculation logic
    if arrow_material == 'wood':
        # Wood spine system (pounds)
        if effective_weight <= 35:
            spine = "55-60"
        elif effective_weight <= 45:
            spine = "45-50"
        elif effective_weight <= 55:
            spine = "35-40"
        elif effective_weight <= 65:
            spine = "26-30"
        else:
            spine = "20-25"
    else:
        # Carbon/aluminum spine system
        if bow_type == 'compound':
            if effective_weight <= 35:
                spine = 600
            elif effective_weight <= 45:
                spine = 500
            elif effective_weight <= 55:
                spine = 400
            elif effective_weight <= 65:
                spine = 340
            elif effective_weight <= 75:
                spine = 300
            else:
                spine = 250
        else:  # recurve/longbow
            if effective_weight <= 35:
                spine = 700
            elif effective_weight <= 45:
                spine = 600
            elif effective_weight <= 55:
                spine = 500
            elif effective_weight <= 65:
                spine = 400
            else:
                spine = 340
    
    return {
        'spine': spine,
        'source': 'generic_calculation',
        'system': 'wood' if arrow_material == 'wood' else 'standard'
    }

def get_applied_adjustments(bow_config):
    """Get list of adjustments applied to base weight"""
    adjustments = []
    
    arrow_length = bow_config.get('arrow_length', 29)
    if arrow_length != 28:
        diff = arrow_length - 28
        adjustments.append(f"Arrow length: {diff:+.1f}\" = {diff*5:+.0f} lbs")
    
    point_weight = bow_config.get('point_weight', 125)
    if point_weight != 125:
        diff = point_weight - 125
        adj = (diff / 25) * 5
        adjustments.append(f"Point weight: {diff:+.0f} gr = {adj:+.1f} lbs")
    
    bow_speed = bow_config.get('bow_speed')
    if bow_speed:
        if bow_speed <= 275:
            adjustments.append(f"Bow speed: {bow_speed} fps = -10 lbs")
        elif bow_speed <= 300:
            adjustments.append(f"Bow speed: {bow_speed} fps = -5 lbs")
        elif bow_speed <= 320:
            adjustments.append(f"Bow speed: {bow_speed} fps = 0 lbs")
        elif bow_speed <= 340:
            adjustments.append(f"Bow speed: {bow_speed} fps = +5 lbs")
        elif bow_speed <= 350:
            adjustments.append(f"Bow speed: {bow_speed} fps = +10 lbs")
        else:
            adjustments.append(f"Bow speed: {bow_speed} fps = +15 lbs")
    
    release_type = bow_config.get('release_type', 'mechanical')
    if release_type == 'finger_release':
        adjustments.append("Finger release: +5 lbs")
    
    return adjustments

def get_calculation_notes(bow_config, manufacturer_recommendation):
    """Get calculation notes and explanations"""
    notes = []
    
    if manufacturer_recommendation:
        notes.append(f"Using {manufacturer_recommendation['manufacturer']} {manufacturer_recommendation['model']} spine chart")
        if manufacturer_recommendation.get('chart_notes'):
            notes.append(manufacturer_recommendation['chart_notes'])
    else:
        notes.append("Using generic spine calculation (no manufacturer chart selected)")
    
    arrow_material = bow_config.get('arrow_material', 'carbon')
    if arrow_material == 'wood':
        notes.append("Wood arrow spine measured in pounds (traditional system)")
    
    return notes

@app.route('/api/bow-setups/<int:setup_id>/change-log', methods=['GET'])
@token_required
def get_bow_setup_change_history(current_user, setup_id):
    """Get unified change history for a bow setup (arrows + equipment + setup)"""
    try:
        from change_log_service import ChangeLogService
        change_service = ChangeLogService()
        
        # Get query parameters
        limit = request.args.get('limit', 50, type=int)
        days_back = request.args.get('days_back', type=int)
        
        # Get unified change history
        changes = change_service.get_unified_change_history(
            bow_setup_id=setup_id,
            user_id=current_user['id'],
            limit=limit,
            days_back=days_back
        )
        
        # Format timestamps for JSON response (ensure UTC timezone)
        from datetime import timezone
        for change in changes:
            if hasattr(change['created_at'], 'isoformat'):
                # SQLite CURRENT_TIMESTAMP is UTC but creates naive datetime objects
                # Mark as UTC before serialization to ensure proper timezone handling
                if change['created_at'].tzinfo is None:
                    change['created_at'] = change['created_at'].replace(tzinfo=timezone.utc)
                change['created_at'] = change['created_at'].isoformat()
        
        return jsonify({
            'changes': changes,
            'total_count': len(changes)
        })
        
    except Exception as e:
        print(f"Error getting change history: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/bow-setups/<int:setup_id>/change-log/statistics', methods=['GET'])
@token_required
def get_bow_setup_change_statistics(current_user, setup_id):
    """Get change statistics for a bow setup"""
    try:
        from change_log_service import ChangeLogService
        change_service = ChangeLogService()
        
        # Get change statistics
        stats = change_service.get_change_statistics(
            bow_setup_id=setup_id,
            user_id=current_user['id']
        )
        
        return jsonify(stats)
        
    except Exception as e:
        print(f"Error getting change statistics: {e}")
        return jsonify({'error': str(e)}), 500

# Run the app
if __name__ == '__main__':
    port = int(os.environ.get('API_PORT', 5000))
    print(f"🚀 Starting ArrowTuner API on port {port}")
    print(f"🎯 Environment: {os.environ.get('NODE_ENV', 'development')}")
    print(f"📊 Arrow Database: {os.environ.get('ARROW_DATABASE_PATH', '/app/arrow_database.db')}")
    print(f"👤 User Database: {os.environ.get('USER_DATABASE_PATH', '/app/user_data/user_data.db')}")
    app.run(host='0.0.0.0', port=port, debug=False)

