#!/usr/bin/env python3
"""
API-Only Flask Backend for Arrow Tuning System
Provides RESTful API endpoints for the Nuxt 3 frontend
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import uuid

# Import our arrow tuning system components
from arrow_tuning_system import ArrowTuningSystem, ArcherProfile, TuningSession
from spine_calculator import BowConfiguration, BowType
from tuning_calculator import TuningGoal, ArrowType
from arrow_database import ArrowDatabase

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'arrow-tuning-secret-key-change-in-production')

# Enable CORS for the Nuxt frontend
CORS(app, origins=[
    "http://localhost:3000",  # Nuxt dev server
    "https://archerytool.online", # Production domain
    "https://www.archerytool.online", # Production domain with www
])

# Global variables for lazy initialization
tuning_system = None
database = None

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
                print("❌ Cannot initialize tuning system: no database available")
                return None
            
            # Use the same path the database is using
            db_path = db.db_path if hasattr(db, 'db_path') else 'arrow_database.db'
            print(f"🧮 Initializing tuning system with database: {db_path}")
            tuning_system = ArrowTuningSystem(database_path=db_path)
        except Exception as e:
            print(f"Error initializing tuning system: {e}")
            import traceback
            traceback.print_exc()
            tuning_system = None
    return tuning_system

def get_database():
    """Get database with lazy initialization"""
    global database
    if database is None:
        try:
            # Try multiple database locations in order of preference
            db_paths = [
                os.getenv('DATABASE_PATH', '/app/data/arrow_database.db'),  # Environment variable or default
                '/app/data/arrow_database.db',     # Docker data volume
                '/app/arrow_database.db',          # Docker app directory
                'arrow_database.db',               # Current directory (fallback)
                '../arrow_database.db'             # Parent directory (development)
            ]
            
            database_path = None
            for db_path in db_paths:
                if os.path.exists(db_path):
                    # Quick check if database has data
                    try:
                        import sqlite3
                        conn = sqlite3.connect(db_path)
                        cursor = conn.cursor()
                        cursor.execute("SELECT COUNT(*) FROM arrows")
                        count = cursor.fetchone()[0]
                        conn.close()
                        
                        if count > 0:
                            database_path = db_path
                            print(f"🗄️  Using database: {db_path} ({count} arrows)")
                            break
                        else:
                            print(f"⚠️  Database exists but empty: {db_path}")
                    except Exception as e:
                        print(f"⚠️  Database check failed for {db_path}: {e}")
                        continue
            
            if not database_path:
                print("❌ No valid database found. Available paths checked:")
                for db_path in db_paths:
                    exists = "✓" if os.path.exists(db_path) else "✗"
                    print(f"  {exists} {db_path}")
                database = None
                return None
            
            database = ArrowDatabase(database_path)
            
        except Exception as e:
            print(f"Error initializing database: {e}")
            import traceback
            traceback.print_exc()
            database = None
    return database

# Error handler
@app.errorhandler(Exception)
def handle_error(error):
    """Global error handler"""
    import traceback
    print(f"API Error: {error}")
    print(traceback.format_exc())
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
        'endpoints': {
            'health': '/api/health',
            'arrows': '/api/arrows',
            'manufacturers': '/api/manufacturers',
            'tuning': '/api/tuning/*'
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
                        'max_outer_diameter': max_outer_diameter
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
        print(f"❌ Compatible arrows error: {e}")
        print(f"Stack trace: {traceback.format_exc()}")
        return jsonify({'error': f'Compatible arrows error: {str(e)}'}), 500

# Configuration and setup
if __name__ == '__main__':
    # Development server
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"🚀 Starting ArrowTuner API Server on port {port}")
    print(f"Debug mode: {debug}")
    
    try:
        app.run(
            host='0.0.0.0',
            port=port,
            debug=debug
        )
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {port} is already in use!")
            print(f"Please check for other running instances or use a different port.")
            import sys
            sys.exit(1)
        else:
            raise e

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