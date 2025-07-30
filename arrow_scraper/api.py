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

from datetime import datetime, timedelta, timedelta, timedelta, timedelta, timedelta, timedelta, timedelta, timedelta, timedelta, timedelta, timezone
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

# Enable CORS for the Nuxt frontend with explicit method support
CORS(app, origins=[
    "http://localhost:3000",  # Nuxt dev server
    "http://localhost:3001",  # Nuxt dev server alternate port
    "https://archerytool.online", # Production domain
    "https://www.archerytool.online", # Production domain with www
], methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'], allow_headers=['Content-Type', 'Authorization'])

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
    """Get arrow database connection with fallback locations"""
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
        db = get_database()
        if not db:
            return jsonify({'error': 'Database not available'}), 500
            
        arrow_details = db.get_arrow_details(arrow_id)
        
        if not arrow_details:
            return jsonify({'error': 'Arrow not found'}), 404
        
        # Enhance with proper image URL
        arrow_details['primary_image_url'] = get_image_url(
            arrow_id=arrow_details['id'],
            image_url=arrow_details.get('image_url'),
            saved_images=arrow_details.get('saved_images'),
            local_image_path=arrow_details.get('local_image_path')
        )
        
        return jsonify(arrow_details)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

# Tuning Calculation API
@app.route('/api/tuning/calculate-spine', methods=['POST'])
def calculate_spine():
    """Calculate recommended spine for given bow configuration"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Create bow configuration
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
        
        # Calculate spine using tuning system
        ts = get_tuning_system()
        if not ts:
            return jsonify({'error': 'Tuning system not available'}), 500
            
        # Use the spine calculator directly
        spine_result = ts.spine_calculator.calculate_required_spine(
            bow_config,
            arrow_length=data.get('arrow_length', 29.0),
            point_weight=data.get('point_weight', 100.0),
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
            'calculations': {
                'base_spine': spine_result['base_spine'],
                'adjustments': spine_result['adjustments'],
                'total_adjustment': spine_result['total_adjustment'],
                'bow_type': spine_result['bow_type'],
                'confidence': spine_result['confidence']
            },
            'notes': spine_result.get('notes', [])
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
                point_weight_preference=float(data.get('point_weight', 100.0))
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
        
        recommendations = session.recommended_arrows[:20]  # Limit to top 20
        
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
    
    if shooting_style and shooting_style not in ['target', 'hunting', 'traditional', '3d']:
        return jsonify({'error': 'Invalid shooting style. Must be target, hunting, traditional, or 3d'}), 400
    
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

from user_database import UserDatabase

# Bow Setups API
@app.route('/api/bow-setups', methods=['GET'])
@token_required
def get_bow_setups(current_user):
    """Get all bow setups for the current user"""
    user_db = UserDatabase()
    conn = user_db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bow_setups WHERE user_id = ?", (current_user['id'],))
    setups = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in setups])

@app.route('/api/bow-setups', methods=['POST'])
@token_required
def create_bow_setup(current_user):
    """Create a new bow setup"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    user_db = UserDatabase()
    conn = user_db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO bow_setups (user_id, name, bow_type, draw_weight, draw_length, arrow_length, point_weight, nock_weight, fletching_weight, insert_weight, description, bow_usage, riser_model, limb_model, compound_model) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                current_user['id'],
                data['name'],
                data['bow_type'],
                data['draw_weight'],
                data['draw_length'],
                data.get('arrow_length'),
                data.get('point_weight'),
                data.get('nock_weight'),
                data.get('fletching_weight'),
                data.get('insert_weight'),
                data.get('description'),
                data.get('bow_usage'),
                data.get('riser_model'),
                data.get('limb_model'),
                data.get('compound_model'),
            ),
        )
        conn.commit()
        new_setup_id = cursor.lastrowid
        cursor.execute("SELECT * FROM bow_setups WHERE id = ?", (new_setup_id,))
        new_setup = cursor.fetchone()
        conn.close()
        return jsonify(dict(new_setup)), 201
    except Exception as e:
        conn.close()
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
        
        # The setup_arrows table is now created in user_database.py initialization
        
        # Check if this exact combination already exists
        cursor.execute('''
            SELECT id FROM setup_arrows 
            WHERE setup_id = ? AND arrow_id = ? AND arrow_length = ? AND point_weight = ?
        ''', (setup_id, data['arrow_id'], data['arrow_length'], data['point_weight']))
        
        existing_record = cursor.fetchone()
        
        if existing_record:
            # Update existing record
            cursor.execute('''
                UPDATE setup_arrows 
                SET calculated_spine = ?, compatibility_score = ?, notes = ?
                WHERE id = ?
            ''', (
                data.get('calculated_spine'),
                data.get('compatibility_score'),
                data.get('notes'),
                existing_record[0]
            ))
            arrow_association_id = existing_record[0]
        else:
            # Insert new record
            cursor.execute('''
                INSERT INTO setup_arrows 
                (setup_id, arrow_id, arrow_length, point_weight, calculated_spine, compatibility_score, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                setup_id,
                data['arrow_id'],
                data['arrow_length'],
                data['point_weight'],
                data.get('calculated_spine'),
                data.get('compatibility_score'),
                data.get('notes')
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
            arrow_cursor = arrow_conn.cursor()
            for row in rows:
                arrow_cursor.execute('''
                    SELECT manufacturer, model_name, material, description
                    FROM arrows WHERE id = ?
                ''', (row['arrow_id'],))
                arrow_data = arrow_cursor.fetchone()
                if arrow_data:
                    arrow_details[row['arrow_id']] = arrow_data
            arrow_conn.close()
        
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
                arrow_data = arrow_details[row['arrow_id']]
                arrow_info['arrow'] = {
                    'manufacturer': arrow_data['manufacturer'], 
                    'model_name': arrow_data['model_name'],
                    'material': arrow_data['material'],
                    'description': arrow_data['description']
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
if __name__ == '__main__':
    # Development server
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    try:
        app.run(
            host='0.0.0.0',
            port=port,
            debug=debug
        )
    except OSError as e:
        if "Address already in use" in str(e):
            import sys
            sys.exit(1)
        else:
            raise e

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

