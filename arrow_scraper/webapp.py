#!/usr/bin/env python3
"""
Flask Web Application for Arrow Tuning System
Provides web interface for arrow selection, spine calculation, and tuning recommendations
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import os

# Import our arrow tuning system components
from arrow_tuning_system import ArrowTuningSystem, ArcherProfile, TuningSession
from spine_calculator import BowConfiguration, BowType
from tuning_calculator import TuningGoal, ArrowType
from arrow_database import ArrowDatabase

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'arrow-tuning-secret-key-change-in-production')

# Initialize the tuning system
tuning_system = ArrowTuningSystem()
database = ArrowDatabase()

@app.route('/')
def index():
    """Homepage with overview of the system"""
    
    # Get database statistics for homepage
    stats = database.get_statistics()
    
    return render_template('index.html', 
                         title="Arrow Tuning System",
                         stats=stats)

@app.route('/arrows')
def arrow_listing():
    """Arrow listing page with search and filters"""
    
    # Get query parameters
    manufacturer = request.args.get('manufacturer', '')
    arrow_type = request.args.get('arrow_type', '')
    spine_min = request.args.get('spine_min', type=int)
    spine_max = request.args.get('spine_max', type=int)
    gpi_min = request.args.get('gpi_min', type=float)
    gpi_max = request.args.get('gpi_max', type=float)
    diameter_min = request.args.get('diameter_min', type=float)
    diameter_max = request.args.get('diameter_max', type=float)
    search_query = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Search arrows using database
    arrows = database.search_arrows(
        manufacturer=manufacturer if manufacturer else None,
        arrow_type=arrow_type if arrow_type else None,
        spine_min=spine_min,
        spine_max=spine_max,
        gpi_min=gpi_min,
        gpi_max=gpi_max,
        diameter_min=diameter_min,
        diameter_max=diameter_max,
        model_search=search_query if search_query else None,
        limit=per_page * 5  # Get more for pagination simulation
    )
    
    # Simple pagination simulation
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_arrows = arrows[start_idx:end_idx]
    
    # Get available manufacturers for filter dropdown
    stats = database.get_statistics()
    manufacturers = [mfr['manufacturer'] for mfr in stats['manufacturers']]
    
    # Calculate pagination info
    total_arrows = len(arrows)
    total_pages = (total_arrows + per_page - 1) // per_page
    
    pagination = {
        'page': page,
        'per_page': per_page,
        'total': total_arrows,
        'total_pages': total_pages,
        'has_prev': page > 1,
        'has_next': page < total_pages,
        'prev_num': page - 1 if page > 1 else None,
        'next_num': page + 1 if page < total_pages else None
    }
    
    return render_template('arrows/listing.html',
                         title="Arrow Database",
                         arrows=paginated_arrows,
                         manufacturers=manufacturers,
                         pagination=pagination,
                         current_filters={
                             'manufacturer': manufacturer,
                             'arrow_type': arrow_type,
                             'spine_min': spine_min,
                             'spine_max': spine_max,
                             'gpi_min': gpi_min,
                             'gpi_max': gpi_max,
                             'diameter_min': diameter_min,
                             'diameter_max': diameter_max,
                             'search': search_query
                         })

@app.route('/arrow/<int:arrow_id>')
def arrow_detail(arrow_id):
    """Detailed view of a specific arrow"""
    
    arrow_details = database.get_arrow_details(arrow_id)
    
    if not arrow_details:
        flash('Arrow not found', 'error')
        return redirect(url_for('arrow_listing'))
    
    return render_template('arrows/detail.html',
                         title=f"{arrow_details['manufacturer']} {arrow_details['model_name']}",
                         arrow=arrow_details)

@app.route('/tuning')
def tuning_wizard():
    """Start the arrow tuning wizard"""
    return render_template('tuning/wizard.html',
                         title="Arrow Tuning Wizard")

@app.route('/tuning/calculate', methods=['POST'])
def calculate_tuning():
    """Process tuning calculation request"""
    
    try:
        # Get form data
        data = request.get_json() if request.is_json else request.form.to_dict()
        
        # Create bow configuration
        bow_config = BowConfiguration(
            draw_weight=float(data['draw_weight']),
            draw_length=float(data['draw_length']),
            bow_type=BowType(data['bow_type']),
            cam_type=data.get('cam_type', 'medium'),
            arrow_rest_type=data.get('arrow_rest_type', 'drop_away')
        )
        
        # Create archer profile
        archer_profile = ArcherProfile(
            name=data.get('archer_name', 'Anonymous Archer'),
            bow_config=bow_config,
            shooting_style=data.get('shooting_style', 'hunting'),
            experience_level=data.get('experience_level', 'intermediate'),
            preferred_manufacturers=data.get('preferred_manufacturers', '').split(',') if data.get('preferred_manufacturers') else None,
            arrow_length=float(data['arrow_length']),
            point_weight_preference=float(data.get('point_weight', 100.0)),
            target_foc_range=(float(data['foc_min']), float(data['foc_max'])) if data.get('foc_min') and data.get('foc_max') else None
        )
        
        # Determine tuning goals
        tuning_goals = []
        if data.get('goal_speed'):
            tuning_goals.append(TuningGoal.MAXIMUM_SPEED)
        if data.get('goal_accuracy'):
            tuning_goals.append(TuningGoal.MAXIMUM_ACCURACY)
        if data.get('goal_penetration'):
            tuning_goals.append(TuningGoal.OPTIMAL_PENETRATION)
        if data.get('goal_hunting'):
            tuning_goals.append(TuningGoal.HUNTING_EFFECTIVENESS)
        if not tuning_goals:
            tuning_goals = [TuningGoal.BALANCED_PERFORMANCE]
        
        # Create tuning session
        session_data = tuning_system.create_tuning_session(
            archer_profile=archer_profile,
            tuning_goals=tuning_goals
        )
        
        # Store session in Flask session
        session['tuning_session_id'] = session_data.session_id
        session['tuning_session'] = {
            'session_id': session_data.session_id,
            'timestamp': session_data.session_timestamp,
            'archer_name': archer_profile.name,
            'bow_setup': f"{bow_config.draw_weight}# @ {bow_config.draw_length}\"",
            'results_count': len(session_data.recommended_arrows)
        }
        
        # Generate report
        report = tuning_system.generate_comprehensive_report(session_data)
        
        if request.is_json:
            return jsonify({
                'success': True,
                'session_id': session_data.session_id,
                'results_count': len(session_data.recommended_arrows),
                'redirect_url': url_for('tuning_results', session_id=session_data.session_id)
            })
        else:
            return redirect(url_for('tuning_results', session_id=session_data.session_id))
            
    except Exception as e:
        error_msg = f"Tuning calculation error: {str(e)}"
        
        if request.is_json:
            return jsonify({
                'success': False,
                'error': error_msg
            }), 400
        else:
            flash(error_msg, 'error')
            return redirect(url_for('tuning_wizard'))

@app.route('/tuning/results/<session_id>')
def tuning_results(session_id):
    """Display tuning results"""
    
    # Try to load session file
    session_file = f"tuning_session_{session_id}.json"
    
    if not os.path.exists(session_file):
        flash('Tuning session not found', 'error')
        return redirect(url_for('tuning_wizard'))
    
    try:
        with open(session_file, 'r') as f:
            session_data = json.load(f)
        
        return render_template('tuning/results.html',
                             title="Tuning Results",
                             session_data=session_data)
                             
    except Exception as e:
        flash(f'Error loading tuning session: {e}', 'error')
        return redirect(url_for('tuning_wizard'))

@app.route('/comparison')
def arrow_comparison():
    """Arrow comparison tool"""
    
    # Get arrow IDs from query parameters
    arrow_ids = request.args.getlist('arrows', type=int)
    
    if not arrow_ids:
        flash('No arrows selected for comparison', 'warning')
        return redirect(url_for('arrow_listing'))
    
    # Get detailed information for selected arrows
    arrows = []
    for arrow_id in arrow_ids[:5]:  # Limit to 5 arrows
        arrow_details = database.get_arrow_details(arrow_id)
        if arrow_details:
            arrows.append(arrow_details)
    
    if not arrows:
        flash('Selected arrows not found', 'error')
        return redirect(url_for('arrow_listing'))
    
    return render_template('arrows/comparison.html',
                         title="Arrow Comparison",
                         arrows=arrows)

@app.route('/api/search')
def api_search():
    """API endpoint for arrow search (for AJAX requests)"""
    
    query = request.args.get('q', '')
    manufacturer = request.args.get('manufacturer', '')
    limit = request.args.get('limit', 10, type=int)
    
    arrows = database.search_arrows(
        manufacturer=manufacturer if manufacturer else None,
        model_search=query if query else None,
        limit=limit
    )
    
    # Format for API response
    results = []
    for arrow in arrows:
        results.append({
            'id': arrow['id'],
            'manufacturer': arrow['manufacturer'],
            'model_name': arrow['model_name'],
            'spine_count': arrow['spine_count'],
            'min_spine': arrow['min_spine'],
            'max_spine': arrow['max_spine'],
            'min_gpi': arrow['min_gpi'],
            'max_gpi': arrow['max_gpi']
        })
    
    return jsonify({
        'results': results,
        'count': len(results)
    })

@app.route('/api/stats')
def api_stats():
    """API endpoint for database statistics"""
    
    stats = database.get_statistics()
    return jsonify(stats)

@app.route('/about')
def about():
    """About page with system information"""
    
    stats = database.get_statistics()
    
    system_info = {
        'version': '2.0.0',
        'database_arrows': stats['total_arrows'],
        'database_specs': stats['total_specifications'],
        'manufacturers': len(stats['manufacturers']),
        'features': [
            'Professional spine calculations',
            'Multi-manufacturer database',
            'Advanced tuning analysis',
            'FOC optimization',
            'Broadhead tuning support',
            'Comprehensive reporting'
        ]
    }
    
    return render_template('about.html',
                         title="About Arrow Tuning System",
                         system_info=system_info,
                         stats=stats)

# Error handlers
@app.route('/favicon.ico')
def favicon():
    return '', 404

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html', title="Page Not Found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html', title="Internal Error"), 500

# Template filters and functions
@app.template_filter('currency')
def currency_filter(value):
    """Format number as currency"""
    if value is None:
        return 'N/A'
    return f"${value:.2f}"

@app.template_filter('percentage')
def percentage_filter(value, decimals=1):
    """Format number as percentage"""
    if value is None:
        return 'N/A'
    return f"{value:.{decimals}f}%"

@app.template_filter('weight')
def weight_filter(value):
    """Format weight in grains"""
    if value is None:
        return 'N/A'
    return f"{value:.1f} gr"

@app.template_filter('diameter')
def diameter_filter(value):
    """Format diameter in inches"""
    if value is None:
        return 'N/A'
    return f"{value:.3f}\""

@app.template_global()
def get_spine_color(spine_value):
    """Get color class for spine value"""
    if spine_value <= 300:
        return 'text-red-600'
    elif spine_value <= 400:
        return 'text-orange-600'
    elif spine_value <= 500:
        return 'text-yellow-600'
    elif spine_value <= 600:
        return 'text-green-600'
    else:
        return 'text-blue-600'

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('templates/arrows', exist_ok=True)
    os.makedirs('templates/tuning', exist_ok=True)
    os.makedirs('templates/errors', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('static/img', exist_ok=True)
    
    # Run in debug mode for development (single-threaded to avoid SQLite threading issues)
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=False)