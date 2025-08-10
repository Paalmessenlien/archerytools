#!/usr/bin/env python3
"""
API-Only Flask Backend for Arrow Tuning System
Provides RESTful API endpoints for the Nuxt 3 frontend
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
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
    """Get database with fallback locations"""
    global database
    if database is None:
        try:
            # Try multiple database locations
            db_paths = [
                '/app/arrow_database.db',          # Primary location
                '/app/arrow_database_backup.db',   # Backup location
                'arrow_database.db',               # Development location
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
                            break
                    except Exception as e:
                        continue
            
            if not database_path:
                return None
            
            database = ArrowDatabase(database_path)
            
        except Exception as e:
            import traceback
            database = None
    return database

def get_arrow_db():
    """Get arrow database connection with fallback locations - sync with ArrowDatabase class"""
    try:
        # UNIFIED DATABASE PATH RESOLUTION - NEW ARCHITECTURE (August 2025)
        db_paths = [
            '/app/databases/arrow_database.db',                    # 🔴 UNIFIED Docker path (HIGHEST PRIORITY)
            '../databases/arrow_database.db',                      # 🔴 UNIFIED local path (PRODUCTION READY)
            'databases/arrow_database.db',                         # 🟡 Legacy unified subfolder
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
    """Update a bow setup"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    try:
        # Use the user database method for updating
        from user_database import UserDatabase
        user_db = UserDatabase()
        updated_setup = user_db.update_bow_setup(current_user['id'], setup_id, data)
        
        if not updated_setup:
            return jsonify({'error': 'Setup not found or you do not have permission to edit it'}), 404
        
        return jsonify(updated_setup)
    except Exception as e:
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
        
        # Check if this exact combination already exists
        cursor.execute('''
            SELECT id FROM setup_arrows 
            WHERE setup_id = ? AND arrow_id = ? AND arrow_length = ? AND point_weight = ?
        ''', (setup_id, data['arrow_id'], data['arrow_length'], data['point_weight']))
        
        existing_record = cursor.fetchone()
        
        if existing_record:
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
        
    except Exception as e:
        if conn:
            conn.close()
        return jsonify({'error': str(e)}), 500


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

def update_arrow_in_setup_internal(arrow_setup_id, data, conn):
    """Internal function to update arrow setup - shared by different endpoints"""
    cursor = conn.cursor()
    
    # Get the current arrow setup
    cursor.execute('SELECT * FROM setup_arrows WHERE id = ?', (arrow_setup_id,))
    arrow_setup = cursor.fetchone()
    
    if not arrow_setup:
        return jsonify({'error': 'Arrow setup not found'}), 404
    
    # Convert sqlite3.Row to dict for easier access
    arrow_setup_dict = dict(arrow_setup) if hasattr(arrow_setup, 'keys') else arrow_setup
    
    # Update the arrow setup with component weights
    # Allow spine updates when user selects different spine from same arrow's options
    cursor.execute('''
        UPDATE setup_arrows 
        SET arrow_length = ?, point_weight = ?, calculated_spine = ?, notes = ?,
            nock_weight = ?, insert_weight = ?, bushing_weight = ?, compatibility_score = ?
        WHERE id = ?
    ''', (
        data.get('arrow_length', arrow_setup_dict['arrow_length']),
        data.get('point_weight', arrow_setup_dict['point_weight']),
        data.get('calculated_spine', arrow_setup_dict['calculated_spine']),
        data.get('notes', arrow_setup_dict['notes']),
        data.get('nock_weight', arrow_setup_dict.get('nock_weight', 10)),
        data.get('insert_weight', arrow_setup_dict.get('insert_weight', 0)),
        data.get('bushing_weight', arrow_setup_dict.get('bushing_weight', 0)),
        data.get('compatibility_score', arrow_setup_dict.get('compatibility_score')),
        arrow_setup_id
    ))
    
    conn.commit()
    
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
        result = update_arrow_in_setup_internal(arrow_setup_id, data, conn)
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

# ===== MANUFACTURER MANAGEMENT API ENDPOINTS (ADMIN) =====

@app.route('/api/admin/manufacturers', methods=['GET'])
@token_required
@admin_required
def get_manufacturers_admin(current_user):
    """Get all manufacturers with arrow counts (admin only)"""
    try:
        db = get_database()
        cursor = db.get_connection().cursor()
        
        # Get manufacturers with arrow counts
        query = """
            SELECT 
                manufacturer,
                COUNT(*) as arrow_count,
                MIN(created_at) as first_added,
                MAX(created_at) as last_added
            FROM arrows 
            GROUP BY manufacturer 
            ORDER BY manufacturer
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        manufacturers = []
        for row in results:
            manufacturers.append({
                'name': row[0],
                'arrow_count': row[1],
                'first_added': row[2],
                'last_added': row[3]
            })
        
        return jsonify({
            'manufacturers': manufacturers,
            'total_count': len(manufacturers)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/manufacturers/<manufacturer_name>', methods=['PUT'])
@token_required
@admin_required
def update_manufacturer_admin(current_user, manufacturer_name):
    """Update manufacturer name for all arrows (admin only)"""
    try:
        data = request.get_json()
        
        if not data or 'new_name' not in data:
            return jsonify({'error': 'new_name is required'}), 400
        
        new_name = data['new_name'].strip()
        if not new_name:
            return jsonify({'error': 'new_name cannot be empty'}), 400
        
        # URL decode the manufacturer name
        import urllib.parse
        manufacturer_name = urllib.parse.unquote(manufacturer_name)
        
        db = get_database()
        cursor = db.get_connection().cursor()
        
        # Check if manufacturer exists
        cursor.execute("SELECT COUNT(*) FROM arrows WHERE manufacturer = ?", (manufacturer_name,))
        if cursor.fetchone()[0] == 0:
            return jsonify({'error': 'Manufacturer not found'}), 404
        
        # Check if new name already exists (case insensitive)
        cursor.execute("SELECT COUNT(*) FROM arrows WHERE LOWER(manufacturer) = LOWER(?)", (new_name,))
        if cursor.fetchone()[0] > 0 and new_name.lower() != manufacturer_name.lower():
            return jsonify({'error': 'A manufacturer with this name already exists'}), 409
        
        # Update all arrows with this manufacturer
        cursor.execute("""
            UPDATE arrows 
            SET manufacturer = ? 
            WHERE manufacturer = ?
        """, (new_name, manufacturer_name))
        
        affected_rows = cursor.rowcount
        db.get_connection().commit()
        
        return jsonify({
            'message': f'Successfully updated manufacturer from "{manufacturer_name}" to "{new_name}"',
            'affected_arrows': affected_rows,
            'updated_by': current_user['email']
        }), 200
        
    except Exception as e:
        db.get_connection().rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/manufacturers/<manufacturer_name>', methods=['DELETE'])
@token_required
@admin_required
def delete_manufacturer_admin(current_user, manufacturer_name):
    """Delete manufacturer and all associated arrows (admin only)"""
    try:
        # URL decode the manufacturer name
        import urllib.parse
        manufacturer_name = urllib.parse.unquote(manufacturer_name)
        
        db = get_database()
        cursor = db.get_connection().cursor()
        
        # Check if manufacturer exists and get arrow count
        cursor.execute("SELECT COUNT(*) FROM arrows WHERE manufacturer = ?", (manufacturer_name,))
        arrow_count = cursor.fetchone()[0]
        
        if arrow_count == 0:
            return jsonify({'error': 'Manufacturer not found'}), 404
        
        # Get arrow IDs for spine specifications cleanup
        cursor.execute("SELECT id FROM arrows WHERE manufacturer = ?", (manufacturer_name,))
        arrow_ids = [row[0] for row in cursor.fetchall()]
        
        # Delete spine specifications first (foreign key constraint)
        if arrow_ids:
            placeholders = ','.join('?' * len(arrow_ids))
            cursor.execute(f"DELETE FROM spine_specifications WHERE arrow_id IN ({placeholders})", arrow_ids)
            deleted_specs = cursor.rowcount
        else:
            deleted_specs = 0
        
        # Delete arrows
        cursor.execute("DELETE FROM arrows WHERE manufacturer = ?", (manufacturer_name,))
        deleted_arrows = cursor.rowcount
        
        db.get_connection().commit()
        
        return jsonify({
            'message': f'Successfully deleted manufacturer "{manufacturer_name}" and all associated data',
            'deleted_arrows': deleted_arrows,
            'deleted_spine_specifications': deleted_specs,
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
        cursor.execute("SELECT COUNT(*) FROM arrows WHERE LOWER(manufacturer) = LOWER(?)", (manufacturer_name,))
        if cursor.fetchone()[0] > 0:
            return jsonify({'error': 'A manufacturer with this name already exists'}), 409
        
        # Create a placeholder arrow for the manufacturer
        # This ensures the manufacturer appears in the list
        now = datetime.utcnow().isoformat()
        cursor.execute("""
            INSERT INTO arrows 
            (manufacturer, model_name, material, arrow_type, description, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            manufacturer_name,
            'Placeholder Model',
            'TBD',
            'TBD',
            f'Placeholder arrow for {manufacturer_name} manufacturer. Replace with actual arrow data.',
            now
        ))
        
        arrow_id = cursor.lastrowid
        
        # Add a basic spine specification for the placeholder
        cursor.execute("""
            INSERT INTO spine_specifications 
            (arrow_id, spine, outer_diameter, gpi_weight)
            VALUES (?, ?, ?, ?)
        """, (arrow_id, 500, 0.246, 10.0))
        
        db.get_connection().commit()
        
        return jsonify({
            'message': f'Successfully created manufacturer "{manufacturer_name}"',
            'manufacturer_name': manufacturer_name,
            'placeholder_arrow_id': arrow_id,
            'created_by': current_user['email']
        }), 201
        
    except Exception as e:
        db.get_connection().rollback()
        return jsonify({'error': str(e)}), 500

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
        
        # Upload to CDN
        cdn_type = os.getenv('CDN_TYPE', 'bunnycdn')
        try:
            uploader = CDNUploader(cdn_type)
        except Exception as e:
            print(f"CDN initialization failed, using local storage: {e}")
            uploader = CDNUploader('local')
            cdn_type = 'local'
        
        # Upload backup to CDN  
        result = uploader.upload_from_file(
            local_backup_path,
            manufacturer="backups",  # Use 'backups' as manufacturer to simplify path
            model_name=backup_name,  # Just the backup name without extra path
            image_type="backup"
        )
        
        if not result:
            return jsonify({'error': 'Failed to upload backup to CDN'}), 500
        
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
            backup_name, result['cdn_url'], result['cdn_type'], backup_size,
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

def get_bunny_cdn_backups():
    """Fetch backup files directly from Bunny CDN Storage API"""
    import requests
    
    # Get Bunny CDN configuration from environment
    storage_zone = os.getenv('BUNNY_STORAGE_ZONE', 'arrowtuner-images')
    access_key = os.getenv('BUNNY_ACCESS_KEY')
    region = os.getenv('BUNNY_REGION', 'de')
    
    if not access_key:
        print("❌ Bunny CDN access key not configured")
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
        print(f"🌐 Fetching backups from Bunny CDN: {api_url}")
        response = requests.get(api_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            files = response.json()
            cdn_backups = []
            
            for file_info in files:
                # Filter for backup files (.tar.gz and .gz)
                filename = file_info.get('ObjectName', '')
                if filename.endswith('.tar.gz') or filename.endswith('.gz'):
                    # Convert Bunny CDN file info to our backup format
                    import hashlib
                    clean_name = filename.replace('.tar.gz', '').replace('.gz', '')
                    cdn_backup_id = hashlib.md5(filename.encode()).hexdigest()[:8]
                    
                    backup_info = {
                        'id': f"cdn_{cdn_backup_id}",  # Add consistent ID field
                        'backup_name': clean_name,
                        'name': clean_name,
                        'file_size_mb': file_info.get('Length', 0) / (1024 * 1024),
                        'created_at': file_info.get('LastChanged', 'Unknown'),
                        'cdn_url': f"https://{os.getenv('BUNNY_HOSTNAME', f'{storage_zone}.b-cdn.net')}/arrows/backups/{filename}",
                        'cdn_type': 'bunnycdn',
                        'include_arrow_db': True,  # Assume all backups include both
                        'include_user_db': True,
                        'file': filename,
                        'is_cdn_direct': True  # Flag to indicate this came directly from CDN API
                    }
                    cdn_backups.append(backup_info)
            
            print(f"✅ Found {len(cdn_backups)} backup files on Bunny CDN")
            return cdn_backups
            
        else:
            print(f"❌ Bunny CDN API error: {response.status_code} - {response.text}")
            return []
            
    except requests.RequestException as e:
        print(f"❌ Network error fetching from Bunny CDN: {e}")
        return []
    except Exception as e:
        print(f"❌ Unexpected error fetching from Bunny CDN: {e}")
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
            ORDER BY bm.created_at DESC
        ''')
        
        cdn_backups = []
        for row in cursor.fetchall():
            backup_info = dict(row)
            # Ensure database backups have consistent ID format
            if 'id' not in backup_info or not backup_info['id']:
                backup_info['id'] = f"db_{backup_info.get('backup_name', 'unknown')}"
            # Add status based on whether local file still exists
            backup_info['local_exists'] = os.path.exists(backup_info['local_path']) if backup_info['local_path'] else False
            backup_info['is_cdn_direct'] = False  # Flag to indicate this came from database
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
        
        # Get CDN backups directly from Bunny CDN Storage API
        cdn_backups = []
        try:
            cdn_backups = get_bunny_cdn_backups()
        except Exception as cdn_error:
            print(f"⚠️  Could not fetch CDN backups: {cdn_error}")
            # Fallback to database metadata if CDN API fails
            cdn_backups = get_database_cdn_backups()
        
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

# Run the app
if __name__ == '__main__':
    port = int(os.environ.get('API_PORT', 5000))
    print(f"🚀 Starting ArrowTuner API on port {port}")
    print(f"🎯 Environment: {os.environ.get('NODE_ENV', 'development')}")
    print(f"📊 Arrow Database: {os.environ.get('ARROW_DATABASE_PATH', '/app/arrow_database.db')}")
    print(f"👤 User Database: {os.environ.get('USER_DATABASE_PATH', '/app/user_data/user_data.db')}")
    app.run(host='0.0.0.0', port=port, debug=False)

