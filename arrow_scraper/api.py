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
from tuning_rule_engine import TuningRuleEngine, PaperTuningRules, BareshaftTuningRules, WalkbackTuningRules, create_tuning_rule_engine, calculate_test_number, create_change_log_entry
from spine_calculator import SpineCalculator, BowConfiguration, BowType
from ballistics_calculator import BallisticsCalculator, EnvironmentalConditions, ShootingConditions, ArrowType as BallisticsArrowType
from tuning_calculator import TuningGoal, ArrowType
from unified_database import UnifiedDatabase
from arrow_database import ArrowDatabase  # Keep for compatibility during transition
from component_database import ComponentDatabase
from spine_service import UnifiedSpineService
from compatibility_engine import CompatibilityEngine
from change_log_service import ChangeLogService

# Import authentication functions
import jwt
from auth import token_required, get_user_from_google_token

def import_arrow_data_validator():
    """
    Import ArrowDataValidator with production-compatible path resolution
    """
    import sys
    
    # Try multiple paths for arrow_data_validator (development vs production)
    validator_paths = [
        os.path.dirname(os.path.dirname(__file__)),  # ../arrow_data_validator.py (development)
        '/app',  # /app/arrow_data_validator.py (production Docker)
        os.getcwd(),  # Current working directory
        os.path.dirname(__file__),  # Same directory as api.py
        '/app/arrow_scraper',  # /app/arrow_scraper/ (if copied there)
        os.path.join(os.getcwd(), 'arrow_scraper'),  # ./arrow_scraper/
    ]
    
    debug_info = []
    
    for path in validator_paths:
        if path not in sys.path:
            sys.path.append(path)
        
        # Check if the file actually exists at this path
        validator_file = os.path.join(path, 'arrow_data_validator.py')
        file_exists = os.path.exists(validator_file)
        debug_info.append(f"Path: {path}, File exists: {file_exists}")
        
        try:
            from arrow_data_validator import ArrowDataValidator
            return ArrowDataValidator
        except ImportError as e:
            debug_info.append(f"Import failed from {path}: {str(e)}")
            continue
    
    # If we get here, create detailed error message
    debug_msg = "\n".join(debug_info)
    cwd = os.getcwd()
    files_in_cwd = os.listdir(cwd) if os.path.exists(cwd) else []
    
    error_msg = f"ArrowDataValidator module not found. Debug info:\n{debug_msg}\nCWD: {cwd}\nFiles in CWD: {files_in_cwd[:10]}"
    raise ImportError(error_msg)

def get_current_user_optional():
    """
    Get current user from JWT token if present, return None if no valid token
    This allows endpoints to work with both authenticated and anonymous users
    """
    try:
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]
        
        if not token:
            return None
        
        data = jwt.decode(token, os.environ.get("SECRET_KEY", "arrow-tuning-secret-key-change-in-production"), algorithms=["HS256"])
        db = UnifiedDatabase()
        current_user = db.get_user_by_id(data["user_id"])
        return current_user
    except Exception as e:
        print(f"Optional auth failed (this is OK for public endpoints): {e}")
        return None

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
unified_database = None
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

def get_fallback_ata_speed(bow_type, bow_ibo_speed=None, bow_draw_weight=None):
    """Get appropriate fallback ATA speed based on bow type"""
    # If we have a valid IBO speed, use it - but validate it's realistic for the bow type
    if bow_ibo_speed and bow_ibo_speed > 0:
        # Validate IBO speed against bow type to catch unrealistic values
        bow_type_lower = bow_type.lower()
        if bow_type_lower in ['recurve', 'longbow', 'traditional', 'barebow']:
            # Traditional bows shouldn't exceed ~200 fps IBO, but also need realistic minimums
            # IBO speeds are typically tested at higher draw weights (40-50#)
            # For very light bows, the stored IBO might be inappropriate
            if bow_draw_weight:
                max_realistic_ibo = min(200, bow_draw_weight * 3.5)  # Roughly 3.5 fps per pound max
                if bow_ibo_speed > max_realistic_ibo:
                    print(f"⚠️  Warning: IBO speed {bow_ibo_speed} fps too high for {bow_type} at {bow_draw_weight}#, using fallback")
                else:
                    return bow_ibo_speed
            else:
                # No draw weight available, use basic validation
                if bow_ibo_speed > 200:
                    print(f"⚠️  Warning: IBO speed {bow_ibo_speed} fps too high for {bow_type}, using fallback")
                else:
                    return bow_ibo_speed
        else:
            # Compound bows - accept the provided IBO speed
            return bow_ibo_speed
    
    # Fallback ATA speeds based on realistic bow performance
    # Traditional bows significantly slower than compounds
    bow_type_ata_speeds = {
        'compound': 320,      # Modern compound bows (IBO standard)
        'recurve': 175,       # Olympic recurve bows typically 170-190 fps
        'longbow': 155,       # Traditional longbows 150-165 fps
        'traditional': 160,   # General traditional bows 155-170 fps
        'barebow': 175        # Barebow recurves typically 165-185 fps
    }
    
    return bow_type_ata_speeds.get(bow_type.lower(), 320)

def validate_bow_setup_data(bow_type, bow_draw_weight, bow_draw_length, bow_ibo_speed=None):
    """
    Validate bow setup data for realistic values and warn about potential issues
    
    Args:
        bow_type: Type of bow (compound, recurve, longbow, traditional, barebow)
        bow_draw_weight: Draw weight in pounds
        bow_draw_length: Draw length in inches  
        bow_ibo_speed: Optional IBO speed rating in fps
        
    Returns:
        dict with validation results and warnings
    """
    warnings = []
    errors = []
    bow_type_lower = str(bow_type).lower()
    
    try:
        # Validate draw weight ranges
        if bow_type_lower in ['compound']:
            if bow_draw_weight < 20 or bow_draw_weight > 100:
                if bow_draw_weight < 20:
                    errors.append(f"Compound bow draw weight {bow_draw_weight}# is too low (minimum 20#)")
                else:
                    warnings.append(f"Compound bow draw weight {bow_draw_weight}# is very high (typical range: 40-80#)")
        else:  # Traditional bows
            if bow_draw_weight < 15 or bow_draw_weight > 80:
                if bow_draw_weight < 15:
                    errors.append(f"Traditional bow draw weight {bow_draw_weight}# is too low (minimum 15#)")
                else:
                    warnings.append(f"Traditional bow draw weight {bow_draw_weight}# is very high (typical range: 20-60#)")
        
        # Validate draw length ranges
        if bow_draw_length < 24 or bow_draw_length > 34:
            if bow_draw_length < 24:
                warnings.append(f"Draw length {bow_draw_length}\" is very short (typical range: 26-32\")")
            else:
                warnings.append(f"Draw length {bow_draw_length}\" is very long (typical range: 26-32\")")
        
        # Validate IBO speed if provided
        if bow_ibo_speed and bow_ibo_speed > 0:
            if bow_type_lower in ['compound']:
                if bow_ibo_speed < 250 or bow_ibo_speed > 370:
                    if bow_ibo_speed < 250:
                        warnings.append(f"Compound bow IBO speed {bow_ibo_speed} fps is low (typical range: 300-360 fps)")
                    else:
                        warnings.append(f"Compound bow IBO speed {bow_ibo_speed} fps is extremely high (typical range: 300-360 fps)")
            else:  # Traditional bows
                # Calculate realistic maximum based on draw weight
                realistic_max_ibo = min(220, bow_draw_weight * 3.5)
                if bow_ibo_speed > realistic_max_ibo:
                    warnings.append(f"Traditional bow IBO speed {bow_ibo_speed} fps is too high for {bow_draw_weight}# (realistic max: ~{realistic_max_ibo:.0f} fps)")
                elif bow_ibo_speed < 150:
                    warnings.append(f"Traditional bow IBO speed {bow_ibo_speed} fps is very low (typical range: 155-200 fps)")
        
        # Check for unrealistic combinations
        if bow_type_lower in ['compound'] and bow_draw_weight < 40 and bow_ibo_speed and bow_ibo_speed > 320:
            warnings.append(f"High IBO speed ({bow_ibo_speed} fps) with low draw weight ({bow_draw_weight}#) is unusual for compound bows")
        
        return {
            'valid': len(errors) == 0,
            'warnings': warnings,
            'errors': errors,
            'bow_type': bow_type,
            'summary': f"Validated {bow_type} bow: {bow_draw_weight}# @ {bow_draw_length}\"" + (f", {bow_ibo_speed} fps IBO" if bow_ibo_speed else "")
        }
        
    except Exception as e:
        return {
            'valid': False,
            'warnings': [],
            'errors': [f"Validation error: {str(e)}"],
            'bow_type': bow_type,
            'summary': f"Validation failed for {bow_type} bow setup"
        }

def calculate_enhanced_arrow_speed_internal(bow_ibo_speed, bow_draw_weight, bow_draw_length, bow_type, arrow_weight_grains, string_material='dacron', setup_id=None, arrow_id=None):
    """Internal helper for enhanced arrow speed calculation with chronograph data and string materials"""
    
    # Input validation and logging
    try:
        # Validate inputs
        if not all([bow_draw_weight, bow_draw_length, bow_type, arrow_weight_grains]):
            print(f"❌ Missing required inputs for speed calculation: weight={bow_draw_weight}, length={bow_draw_length}, type={bow_type}, arrow_weight={arrow_weight_grains}")
            return {"speed": None, "source": "error", "error": "Missing required inputs"}
        
        # Validate numeric inputs
        try:
            bow_ibo_speed = float(bow_ibo_speed) if bow_ibo_speed else 0
            bow_draw_weight = float(bow_draw_weight)
            bow_draw_length = float(bow_draw_length)
            arrow_weight_grains = float(arrow_weight_grains)
        except (ValueError, TypeError) as e:
            print(f"❌ Invalid numeric inputs: {e}")
            return {"speed": None, "source": "error", "error": "Invalid numeric inputs"}
        
        # Validate ranges
        if not (10 <= bow_draw_weight <= 200):
            print(f"❌ Bow draw weight out of range: {bow_draw_weight}#")
            return {"speed": None, "source": "error", "error": f"Draw weight {bow_draw_weight}# out of range (10-200#)"}
        
        if not (20 <= bow_draw_length <= 35):
            print(f"❌ Bow draw length out of range: {bow_draw_length}\"")
            return {"speed": None, "source": "error", "error": f"Draw length {bow_draw_length}\" out of range (20-35\")"}
        
        if not (100 <= arrow_weight_grains <= 1500):
            print(f"❌ Arrow weight out of range: {arrow_weight_grains} grains")
            return {"speed": None, "source": "error", "error": f"Arrow weight {arrow_weight_grains} grains out of range (100-1500 grains)"}
        
        print(f"🔧 Enhanced speed calculation inputs: bow_type={bow_type}, draw_weight={bow_draw_weight}#, draw_length={bow_draw_length}\", ibo_speed={bow_ibo_speed}, arrow_weight={arrow_weight_grains}gr, string={string_material}")
        
        # Check for chronograph data first (most accurate)
        chronograph_result = None
        if setup_id and arrow_id:
            try:
                print(f"🔍 Checking chronograph data for setup_id={setup_id}, arrow_id={arrow_id}")
                user_db = get_database()
                if not user_db:
                    print(f"❌ Database not available for chronograph lookup")
                    return {"speed": None, "source": "error", "error": "Database not available"}
                cursor = user_db.get_connection().cursor()
                
                cursor.execute('''
                    SELECT measured_speed_fps, arrow_weight_grains, std_deviation, shot_count
                    FROM chronograph_data 
                    WHERE setup_id = ? AND arrow_id = ? AND verified = 1
                    ORDER BY measurement_date DESC
                    LIMIT 1
                ''', (setup_id, arrow_id))
                
                chronograph_data = cursor.fetchone()
                
                if chronograph_data:
                    measured_speed, measured_weight, std_dev, shot_count = chronograph_data
                    print(f"📊 Found chronograph data: {measured_speed} fps, {shot_count} shots, std_dev={std_dev}")
                    
                    # Use measured speed directly - chronograph data represents this exact arrow configuration
                    adjusted_speed = measured_speed
                    
                    confidence = min(100, (shot_count * 10) + (85 if std_dev and std_dev < 5 else 70))
                    
                    chronograph_result = {
                        'speed': adjusted_speed,
                        'confidence': confidence,
                        'source': 'chronograph',
                        'shot_count': shot_count,
                        'std_deviation': std_dev
                    }
                    print(f"✅ Using chronograph speed: {adjusted_speed} fps (confidence: {confidence}%)")
                else:
                    print(f"📊 No chronograph data found for setup_id={setup_id}, arrow_id={arrow_id}")
            except Exception as chrono_error:
                print(f"⚠️  Error retrieving chronograph data: {chrono_error}")
                # Don't return error here, continue with calculation
        
        # If chronograph data available, use it
        if chronograph_result:
            return {"speed": chronograph_result['speed'], "source": "chronograph", "confidence": chronograph_result['confidence']}
        
        # String material speed modifiers
        string_speed_modifiers = {
            'dacron': 0.92,           # Slowest, most forgiving (default)
            'fastflight': 1.00,       # Standard modern string  
            'dyneema': 1.02,          # Faster, low stretch
            'vectran': 1.03,          # High performance
            'sk75_dyneema': 1.04,     # Premium racing strings
            'custom_blend': 1.01      # Custom string materials
        }
        
        # Get string material modifier
        string_modifier = string_speed_modifiers.get(string_material.lower(), 0.92)  # Default to dacron
        
        # Bow type specific efficiency factors (adjusted for realistic speeds)
        bow_type_factors = {
            'compound': 0.95,         # Most efficient transfer
            'recurve': 0.90,          # Traditional recurve efficiency (improved)
            'longbow': 0.88,          # Traditional longbow efficiency (improved)
            'traditional': 0.85,      # Traditional bow efficiency (improved)
            'barebow': 0.88          # Barebow efficiency (improved)
        }
        
        bow_efficiency = bow_type_factors.get(bow_type.lower(), 0.95)
        
        # Use proper ATA speed with fallback based on bow type
        try:
            effective_ata_speed = get_fallback_ata_speed(bow_type, bow_ibo_speed, bow_draw_weight)
            print(f"📏 Effective ATA speed: {effective_ata_speed} fps (input: {bow_ibo_speed}, bow_type: {bow_type})")
        except Exception as ata_error:
            print(f"⚠️  Error getting ATA speed: {ata_error}, using default")
            effective_ata_speed = 320 if bow_type.lower() == 'compound' else 140
        
        # Enhanced IBO-based speed calculation with bow-type specific reference parameters
        try:
            if bow_type.lower() in ['compound']:
                # IBO standard for compounds: 350gr arrow, 30" draw, 70lb bow
                reference_weight = 350.0
                reference_draw_weight = 70.0
                reference_draw_length = 30.0
            else:
                # AMO standard for traditional bows: typically tested at lower weights and lengths
                reference_weight = 350.0  # Keep same arrow weight standard
                reference_draw_weight = 50.0  # More realistic for traditional bows
                reference_draw_length = 28.0  # More common traditional draw length
            
            # Validate calculations won't cause division by zero or overflow
            if arrow_weight_grains <= 0:
                print(f"❌ Invalid arrow weight for calculation: {arrow_weight_grains}")
                raise ValueError(f"Invalid arrow weight: {arrow_weight_grains}")
            
            # Adjust for draw weight difference (approximately 2.5 fps per pound - more realistic)
            weight_adjustment = (bow_draw_weight - reference_draw_weight) * 2.5
            
            # Adjust for draw length difference (approximately 10 fps per inch)  
            length_adjustment = (bow_draw_length - reference_draw_length) * 10
            
            # Adjust for arrow weight difference using kinetic energy conservation
            # Heavier arrows = slower speed, lighter arrows = faster speed
            weight_ratio = (reference_weight / arrow_weight_grains) ** 0.5
            
            print(f"🧮 Calculation factors: weight_adj={weight_adjustment:.1f}, length_adj={length_adjustment:.1f}, weight_ratio={weight_ratio:.3f}, string_mod={string_modifier:.3f}, bow_eff={bow_efficiency:.3f}")
            
            # Calculate base speed with adjustments using effective ATA speed
            adjusted_ibo = effective_ata_speed + weight_adjustment + length_adjustment
            estimated_speed = adjusted_ibo * weight_ratio * string_modifier * bow_efficiency
            
            print(f"🎯 Pre-bounds speed calculation: {estimated_speed:.1f} fps")
            
            # Apply reasonable bounds based on bow type
            if bow_type.lower() in ['compound']:
                min_speed, max_speed = 180, 450  # Compound bow bounds
            else:
                min_speed, max_speed = 150, 350  # Traditional bow bounds (realistic minimum)
            
            # Apply bounds and validate result
            bounded_speed = max(min_speed, min(max_speed, estimated_speed))
            
            if bounded_speed != estimated_speed:
                print(f"⚠️  Speed bounded from {estimated_speed:.1f} to {bounded_speed:.1f} fps (bounds: {min_speed}-{max_speed})")
            
            print(f"✅ Final enhanced speed: {bounded_speed:.1f} fps")
            return {"speed": bounded_speed, "source": "enhanced_estimated", "confidence": 85}
            
        except Exception as calc_error:
            print(f"❌ Enhanced calculation failed: {calc_error}")
            raise calc_error  # Re-raise to trigger fallback
        
    except Exception as e:
        print(f"❌ Enhanced speed calculation error: {e}")
        print(f"🔄 Falling back to basic calculation")
        
        # Enhanced fallback calculation with validation
        try:
            # Validate inputs for fallback
            bow_draw_weight = float(bow_draw_weight) if bow_draw_weight else 50.0
            arrow_weight_grains = float(arrow_weight_grains) if arrow_weight_grains else 400.0
            bow_type = str(bow_type).lower() if bow_type else 'compound'
            
            if bow_type == 'compound':
                basic_speed = (bow_draw_weight * 10) - (arrow_weight_grains - 350) * 0.1
                basic_speed = max(180, min(350, basic_speed))
            else:
                basic_speed = (bow_draw_weight * 8) - (arrow_weight_grains - 350) * 0.08
                basic_speed = max(150, min(300, basic_speed))
            
            print(f"🔄 Fallback speed: {basic_speed:.1f} fps")
            return {"speed": basic_speed, "source": "fallback_estimated", "confidence": 60, "error": str(e)}
            
        except Exception as fallback_error:
            print(f"❌ Fallback calculation also failed: {fallback_error}")
            # Last resort - return reasonable default based on bow type
            default_speed = 280 if bow_type == 'compound' else 175
            print(f"🆘 Using emergency default: {default_speed} fps")
            return {"speed": default_speed, "source": "default", "confidence": 30, "error": f"All calculations failed: {str(e)}"}

def calculate_arrow_performance(archer_profile, arrow_rec, estimated_speed=None):
    """Calculate comprehensive performance metrics for a specific arrow recommendation"""
    try:
        ballistics_calc = BallisticsCalculator()
        
        # Extract arrow properties
        raw_gpi = getattr(arrow_rec, 'gpi_weight', None)
        arrow_weight = raw_gpi if raw_gpi and raw_gpi > 0 else 8.5  # Default realistic GPI (grains per inch)
        arrow_length = archer_profile.arrow_length or 29.0
        point_weight = archer_profile.point_weight_preference or 125.0
        
        # Calculate total arrow weight (GPI * length + point weight + nock/fletching)
        total_arrow_weight = (arrow_weight * arrow_length) + point_weight + 25  # 25gr for nock+fletching
        
        # Estimate arrow speed based on bow configuration if not provided
        if not estimated_speed:
            draw_weight = archer_profile.bow_config.draw_weight
            # More realistic speed estimation based on industry standards
            if archer_profile.bow_config.bow_type.value == 'compound':
                # Base speed: ~4-5 fps per pound of draw weight for compound bows
                base_speed = draw_weight * 4.5 + 80  # Base formula
                # Speed loss for arrow weight: ~2 fps per 10gr over 350gr
                weight_penalty = max(0, (total_arrow_weight - 350) / 10) * 2
                estimated_speed = base_speed - weight_penalty
            else:
                # Recurve/traditional bows are slower
                base_speed = draw_weight * 3.5 + 60
                weight_penalty = max(0, (total_arrow_weight - 400) / 10) * 1.5  # Traditional bows less sensitive to weight
                estimated_speed = base_speed - weight_penalty
            estimated_speed = max(180, min(320, estimated_speed))  # More realistic bounds
        
        # Determine arrow type for ballistics
        arrow_type_str = getattr(arrow_rec, 'arrow_type', 'hunting') or 'hunting'
        try:
            arrow_type = BallisticsArrowType(arrow_type_str.lower())
        except:
            arrow_type = BallisticsArrowType.HUNTING
        
        # Get arrow diameter for ballistics
        arrow_diameter = getattr(arrow_rec, 'outer_diameter', 0.246) or 0.246  # Default .246"
        
        # Standard environmental conditions
        env = EnvironmentalConditions()
        shooting = ShootingConditions()
        
        # Calculate enhanced FOC
        spine_calc = SpineCalculator()
        shaft_weight = arrow_weight * arrow_length  # GPI * length = total shaft weight
        
        # Debug logging
        print(f"FOC Debug - arrow_weight (GPI): {arrow_weight}, arrow_length: {arrow_length}, shaft_weight: {shaft_weight}, point_weight: {point_weight}")
        
        foc_result = spine_calc.calculate_enhanced_foc(
            arrow_length=arrow_length,
            point_weight=point_weight,
            shaft_weight=shaft_weight,
            intended_use=archer_profile.shooting_style
        )
        
        # Calculate kinetic energy and penetration at key distances
        ke_initial = ballistics_calc.calculate_kinetic_energy(estimated_speed, total_arrow_weight, 0)
        ke_20yd = ballistics_calc.calculate_kinetic_energy(estimated_speed, total_arrow_weight, 20)
        ke_40yd = ballistics_calc.calculate_kinetic_energy(estimated_speed, total_arrow_weight, 40)
        
        penetration_analysis = ballistics_calc.calculate_penetration_potential(
            ke_40yd['kinetic_energy_ft_lbs'],
            ke_40yd['momentum_slug_fps'],
            arrow_type
        )
        
        # Calculate trajectory for flight characteristics
        trajectory = ballistics_calc.calculate_trajectory(
            arrow_speed_fps=estimated_speed,
            arrow_weight_grains=total_arrow_weight,
            arrow_diameter_inches=arrow_diameter,
            arrow_type=arrow_type,
            environmental=env,
            shooting=shooting
        )
        
        return {
            'performance_summary': {
                'estimated_speed_fps': round(estimated_speed, 1),
                'total_arrow_weight_grains': round(total_arrow_weight, 1),
                'kinetic_energy_initial': ke_initial['kinetic_energy_ft_lbs'],
                'kinetic_energy_40yd': ke_40yd['kinetic_energy_ft_lbs'],
                'momentum': ke_initial['momentum_slug_fps'],
                'momentum_40yd': ke_40yd['momentum_slug_fps'],
                'penetration_score': penetration_analysis['penetration_score'],
                'penetration_category': penetration_analysis['category'],
                'foc_percentage': foc_result.get('foc_percentage', 0),
                'foc_category': foc_result.get('foc_analysis', {}).get('category', 'unknown')
            },
            'detailed_foc': foc_result,
            'kinetic_energy_data': {
                '20_yards': ke_20yd,
                '40_yards': ke_40yd
            },
            'penetration_analysis': penetration_analysis,
            'flight_characteristics': {
                'max_range_yards': trajectory['performance_metrics'].get('max_effective_range_yards', 0),
                'trajectory_flatness_score': trajectory['performance_metrics'].get('trajectory_flatness_score', 0),
                'ballistic_coefficient': trajectory.get('ballistic_coefficient', 0)
            }
        }
        
    except Exception as e:
        print(f"Error calculating arrow performance: {e}")
        return {
            'performance_summary': {
                'estimated_speed_fps': estimated_speed or 250,
                'total_arrow_weight_grains': 400,
                'kinetic_energy_initial': 0,
                'kinetic_energy_40yd': 0,
                'momentum': 0,
                'momentum_40yd': 0,
                'penetration_score': 0,
                'penetration_category': 'unknown',
                'foc_percentage': 0,
                'foc_category': 'unknown'
            },
            'error': f'Performance calculation failed: {str(e)}'
        }

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

def get_unified_database():
    """Get unified database with lazy initialization for journal and user data"""
    global unified_database
    if unified_database is None:
        try:
            unified_database = UnifiedDatabase()
        except Exception as e:
            import traceback
            print(f"Error creating UnifiedDatabase: {e}")
            traceback.print_exc()
            unified_database = None
    return unified_database

def get_effective_draw_length(user_id, bow_config=None, bow_data=None, default=28.0):
    """
    Get effective draw length using unified system (Migration 045+):
    - PRIMARY: bow_setups.draw_length (mandatory per setup, single source of truth)
    - FALLBACK: system default (28.0") only for data integrity issues
    
    All bow setups must have draw_length after Migration 045.
    No more user-level or compound-specific draw length columns.
    
    Returns tuple: (draw_length, source_description)
    """
    try:
        db = get_database()
        if not db:
            return default, "System default (no database)"
        
        # Extract bow type and draw length data
        bow_type = None
        bow_draw_length = None
        bow_setup_id = None
        
        if bow_config:
            bow_type = bow_config.get('bow_type', '').lower()
            bow_draw_length = bow_config.get('draw_length')
            bow_setup_id = bow_config.get('id') or bow_config.get('bow_setup_id')
        elif bow_data:
            bow_type = bow_data.get('bow_type', '').lower()
            bow_draw_length = bow_data.get('draw_length')
            bow_setup_id = bow_data.get('id') or bow_data.get('bow_setup_id')
        
        # PRIMARY SOURCE: Use bow setup draw_length if available (this is correct for all calculations)
        if bow_draw_length and bow_draw_length != 0:
            bow_type_display = bow_type.title() if bow_type else "Bow"
            return float(bow_draw_length), f"{bow_type_display} setup draw length ({bow_draw_length}\")"
        
        # Note: Unified system - no more complex fallbacks needed
        # bow_setups.draw_length is now mandatory and single source of truth
        
        # If bow setup has no draw_length, this indicates a data integrity issue
        # All bow setups should have draw_length after Migration 045
        
        # FINAL FALLBACK: System default
        bow_type_display = bow_type.title() if bow_type else "System"
        return default, f"{bow_type_display} default ({default}\")"
        
    except Exception as e:
        print(f"Error getting effective draw length for user {user_id}: {e}")
        return default, f"Error fallback ({default}\")"

def get_user_draw_length(user_id, default=28.0):
    """Legacy function - get just the draw length value for backward compatibility"""
    draw_length, _ = get_effective_draw_length(user_id, default=default)
    return draw_length

def get_arrow_db():
    """
    DEPRECATED: This function is no longer used due to unified database architecture.
    Use get_database() instead for unified arrow/user database access.
    
    Legacy function for arrow database connection with fallback locations.
    """
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
        if not db:
            return jsonify({"error": "Database not available"}), 500
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

# Git Commits API
@app.route('/api/git/commits', methods=['GET'])
@token_required
def get_git_commits(current_user):
    """Get recent git commits for authenticated users"""
    try:
        import subprocess
        import os
        
        # Get the project root directory
        project_root = Path(__file__).parent.parent
        
        # Execute git log command
        result = subprocess.run([
            'git', 'log', '--oneline', '-20', 
            '--pretty=format:%h|%s|%an|%ad|%cr', 
            '--date=iso'
        ], 
        cwd=project_root,
        capture_output=True, 
        text=True, 
        timeout=10
        )
        
        if result.returncode != 0:
            return jsonify({'error': 'Failed to fetch git commits'}), 500
        
        commits = []
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split('|')
                if len(parts) >= 5:
                    commits.append({
                        'hash': parts[0].strip(),
                        'message': parts[1].strip(),
                        'author': parts[2].strip(),
                        'date': parts[3].strip(),
                        'relative_time': parts[4].strip()
                    })
        
        return jsonify({
            'commits': commits,
            'total_count': len(commits),
            'generated_at': datetime.now(timezone.utc).isoformat()
        })
        
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Git command timed out'}), 500
    except Exception as e:
        print(f"Git commits error: {e}")
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
        
        # Search arrows using unified database (with manufacturer active status filtering)
        db = get_unified_database()
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
            limit=per_page * 10,  # Get more for pagination
            include_inactive=False  # Filter out inactive manufacturers for public API
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

# Manufacturer Autocomplete and Status API
@app.route('/api/manufacturers/suggestions', methods=['GET'])
def get_manufacturer_suggestions():
    """Get manufacturer suggestions for autocomplete with learning integration"""
    try:
        query = request.args.get('query', '').strip()
        category = request.args.get('category', '')
        limit = int(request.args.get('limit', 8))
        
        if len(query) < 2:
            return jsonify({'suggestions': []})
        
        suggestions = []
        
        # Search in approved manufacturers first
        db = get_database()
        if not db:
            return jsonify({"error": "Database not available"}), 500
        if db:
            conn = db.get_connection()
            cursor = conn.cursor()
            
            # Search manufacturers with category support
            cursor.execute('''
                SELECT DISTINCT m.name, mec.category_name
                FROM manufacturers m
                LEFT JOIN manufacturer_equipment_categories mec ON m.id = mec.manufacturer_id
                WHERE m.is_active = 1 
                AND LOWER(m.name) LIKE LOWER(?)
                AND (mec.category_name = ? OR mec.category_name IS NULL)
                ORDER BY 
                    CASE WHEN LOWER(m.name) = LOWER(?) THEN 0 ELSE 1 END,
                    LENGTH(m.name),
                    m.name
                LIMIT ?
            ''', (f'%{query}%', category, query, limit))
            
            # Group results by manufacturer name
            manufacturer_data = {}
            for row in cursor.fetchall():
                name = row['name']
                cat = row['category_name']
                
                if name not in manufacturer_data:
                    manufacturer_data[name] = {
                        'name': name,
                        'status': 'approved',
                        'categories': [],
                        'usage_count': 0
                    }
                
                if cat and cat not in manufacturer_data[name]['categories']:
                    manufacturer_data[name]['categories'].append(cat)
            
            # Convert to list and add to suggestions
            for manufacturer in manufacturer_data.values():
                suggestions.append(manufacturer)
            
            conn.close()
        
        # Search in pending manufacturers and equipment models (user learning data)
        try:
            # Using unified database - ArrowDatabase
            db = get_database()
            if not db:
                return jsonify({"error": "Database not available"}), 500
            user_conn = db.get_connection()
            user_cursor = user_conn.cursor()
            
            # Add pending manufacturers
            user_cursor.execute('''
                SELECT name, usage_count, category_context
                FROM pending_manufacturers
                WHERE status = 'pending'
                AND LOWER(name) LIKE LOWER(?)
                ORDER BY usage_count DESC
                LIMIT ?
            ''', (f'%{query}%', limit))
            
            for row in user_cursor.fetchall():
                categories = json.loads(row['category_context'] or '[]')
                if not category or category in categories:
                    suggestions.append({
                        'name': row['name'],
                        'status': 'pending',
                        'categories': categories,
                        'usage_count': row['usage_count']
                    })
            
            # Add learned models for usage statistics
            user_cursor.execute('''
                SELECT manufacturer_name, SUM(usage_count) as total_usage
                FROM equipment_models
                WHERE LOWER(manufacturer_name) LIKE LOWER(?)
                AND (category_name = ? OR ? = '')
                GROUP BY manufacturer_name
                ORDER BY total_usage DESC
                LIMIT ?
            ''', (f'%{query}%', category, category, limit))
            
            # Update usage counts for existing suggestions
            for row in user_cursor.fetchall():
                for suggestion in suggestions:
                    if suggestion['name'].lower() == row['manufacturer_name'].lower():
                        suggestion['usage_count'] += row['total_usage']
                        break
            
            user_conn.close()
            
        except Exception as e:
            print(f"Warning: Could not access user learning data: {e}")
        
        # Remove duplicates and sort by relevance
        unique_suggestions = {}
        for suggestion in suggestions:
            name_lower = suggestion['name'].lower()
            if name_lower not in unique_suggestions:
                unique_suggestions[name_lower] = suggestion
            else:
                # Merge data if duplicate
                existing = unique_suggestions[name_lower]
                existing['usage_count'] += suggestion['usage_count']
                if suggestion['status'] == 'approved' and existing['status'] == 'pending':
                    existing['status'] = 'approved'
                for cat in suggestion['categories']:
                    if cat not in existing['categories']:
                        existing['categories'].append(cat)
        
        # Sort suggestions by relevance
        final_suggestions = list(unique_suggestions.values())
        final_suggestions.sort(key=lambda x: (
            0 if x['name'].lower() == query.lower() else 1,  # Exact matches first
            -x['usage_count'],  # Higher usage count
            len(x['name']),  # Shorter names
            x['name'].lower()  # Alphabetical
        ))
        
        return jsonify({
            'suggestions': final_suggestions[:limit],
            'query': query,
            'category': category
        })
        
    except Exception as e:
        print(f"Error getting manufacturer suggestions: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/manufacturers/status', methods=['GET'])
def get_manufacturer_status():
    """Get manufacturer approval status"""
    try:
        name = request.args.get('name', '').strip()
        category = request.args.get('category', '')
        
        if not name:
            return jsonify({'status': None})
        
        # Check in approved manufacturers first
        db = get_database()
        if not db:
            return jsonify({"error": "Database not available"}), 500
        if db:
            conn = db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT m.id, m.name, mec.category_name
                FROM manufacturers m
                LEFT JOIN manufacturer_equipment_categories mec ON m.id = mec.manufacturer_id
                WHERE m.is_active = 1 
                AND LOWER(m.name) = LOWER(?)
                AND (mec.category_name = ? OR ? = '' OR mec.category_name IS NULL)
            ''', (name, category, category))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return jsonify({
                    'status': 'approved',
                    'manufacturer_id': result['id'],
                    'category_supported': bool(result['category_name'])
                })
        
        # Check in pending manufacturers
        try:
            # Using unified database - ArrowDatabase
            db = get_database()
            if not db:
                return jsonify({"error": "Database not available"}), 500
            user_conn = db.get_connection()
            user_cursor = user_conn.cursor()
            
            user_cursor.execute('''
                SELECT id, status, category_context, usage_count
                FROM pending_manufacturers
                WHERE LOWER(name) = LOWER(?)
                ORDER BY created_at DESC
                LIMIT 1
            ''', (name,))
            
            pending = user_cursor.fetchone()
            user_conn.close()
            
            if pending:
                categories = json.loads(pending['category_context'] or '[]')
                return jsonify({
                    'status': pending['status'],
                    'pending_id': pending['id'],
                    'categories': categories,
                    'usage_count': pending['usage_count'],
                    'category_supported': category in categories if category else True
                })
            
        except Exception as e:
            print(f"Warning: Could not check pending manufacturers: {e}")
        
        # Not found - will be new
        return jsonify({'status': 'new'})
        
    except Exception as e:
        print(f"Error checking manufacturer status: {e}")
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

def calculate_simple_spine(draw_weight, arrow_length, point_weight, bow_type, string_material=None, material_preference=None, calculation_method='universal'):
    """Simple spine calculation fallback - corrected based on German industry standards"""
    # Check for wood arrow calculation first
    if material_preference and material_preference.lower() == 'wood':
        # Wood arrows use pound test values (40#, 45#, 50#, etc.)
        wood_spine = round(draw_weight)  # Simple conversion: 40lbs = 40# spine
        
        return {
            'calculated_spine': f"{wood_spine}#",
            'spine_range': {
                'minimum': f"{max(wood_spine - 5, 25)}#",
                'optimal': f"{wood_spine}#", 
                'maximum': f"{wood_spine + 5}#"
            },
            'calculations': {
                'base_spine': wood_spine,
                'adjustments': {
                    'bow_weight_conversion': wood_spine,
                    'system_type': 'wood_pound_test',
                    'bow_type': bow_type,
                    'material': 'wood'
                },
                'total_adjustment': 0,
                'bow_type': bow_type,
                'confidence': 'high'
            },
            'notes': [
                'Wood arrow spine calculation using pound test system',
                f'Recommended spine: {wood_spine}# (pound test)',
                'Range represents typical wood arrow spine tolerances'
            ],
            'source': 'wood_arrow_calculator'
        }
    
    # Calculation method selection
    if calculation_method == 'german_industry':
        # German Industry Standard formulas
        if bow_type == 'compound':
            base_spine = draw_weight * 12.5
            bow_type_adjustment = 0
        elif bow_type == 'recurve':
            base_spine = 1100 - (draw_weight * 10)
            bow_type_adjustment = 0
        elif bow_type == 'traditional':
            base_spine = 1100 - (draw_weight * 10)
            bow_type_adjustment = 0
        else:
            base_spine = draw_weight * 12.5
            bow_type_adjustment = 0
    else:
        # Universal formula (original system - default)
        base_spine = draw_weight * 12.5
        
        # Bow type adjustments (original system)
        if bow_type == 'compound':
            bow_type_adjustment = 0
        elif bow_type == 'recurve':
            bow_type_adjustment = 50  # Original recurve adjustment
        elif bow_type == 'traditional':
            bow_type_adjustment = 100  # Original traditional adjustment
        else:
            bow_type_adjustment = 0
        
        base_spine += bow_type_adjustment
    
    # Adjust for arrow length (longer = stiffer needed/lower spine number)
    length_adjustment = (arrow_length - 28) * 25
    base_spine -= length_adjustment
    
    # Adjust for point weight (heavier = weaker/higher spine number)
    point_adjustment = (point_weight - 125) * 0.5
    base_spine += point_adjustment
    
    # String material adjustment (based on German calculator)
    string_adjustment = 0
    if string_material:
        if string_material.lower() in ['dacron', 'b50']:
            string_adjustment = 15  # Dacron strings need weaker arrows (higher spine)
        elif string_material.lower() in ['fastflight', 'spectra', 'dyneema', 'b55']:
            string_adjustment = 0   # FastFlight baseline
    base_spine += string_adjustment
    
    calculated_spine = round(base_spine)
    
    # Create spine range (±25 spine)
    return {
        'calculated_spine': calculated_spine,
        'spine_range': {
            'minimum': calculated_spine - 25,
            'optimal': calculated_spine,
            'maximum': calculated_spine + 25
        },
        'calculations': {
            'base_spine': base_spine - bow_type_adjustment - length_adjustment - point_adjustment - string_adjustment,
            'adjustments': {
                'length_adjustment': length_adjustment,
                'point_weight_adjustment': point_adjustment,
                'string_material_adjustment': string_adjustment,
                'bow_type_adjustment': bow_type_adjustment,
                'bow_type_method': f'{bow_type}_universal_formula',
                'bow_type': bow_type,
                'string_material': string_material or 'not_specified'
            },
            'total_adjustment': bow_type_adjustment + length_adjustment + point_adjustment + string_adjustment,
            'bow_type': bow_type,
            'confidence': 'high'  # Improved confidence with corrected formula
        },
        'notes': [
            f'Calculated using {calculation_method} spine formula',
            f'Base formula: {calculation_method}_{bow_type}_formula',
            'String material factor included' if string_material else 'String material not specified'
        ],
        'source': f'{calculation_method}_calculator'
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
        
        # Get effective draw length using proper hierarchy
        current_user = get_current_user_optional()
        user_id = current_user['id'] if current_user else None
        effective_draw_length, draw_length_source = get_effective_draw_length(
            user_id, bow_config=data
        )
        
        print(f"🎯 Spine calculation using draw length: {effective_draw_length}\" from {draw_length_source}")
        
        # Use the unified spine calculation service
        from spine_service import calculate_unified_spine
        
        spine_result = calculate_unified_spine(
            draw_weight=float(data.get('draw_weight', 45)),
            arrow_length=float(data.get('arrow_length', 29.0)),
            point_weight=float(data.get('point_weight', 125.0)),
            bow_type=data.get('bow_type', 'compound'),
            draw_length=effective_draw_length,  # Use corrected draw length
            nock_weight=float(data.get('nock_weight', 10.0)),
            fletching_weight=float(data.get('fletching_weight', 15.0)),
            string_material=data.get('string_material'),  # Add string material parameter
            material_preference=data.get('arrow_material'),
            shooting_style=data.get('shooting_style', 'standard'),  # Add shooting style parameter
            calculation_method=data.get('calculation_method', 'universal'),
            manufacturer_chart=data.get('manufacturer_chart'),
            chart_id=data.get('chart_id'),
            # Professional mode parameters
            bow_speed=float(data['bow_speed']) if data.get('bow_speed') else None,
            release_type=data.get('release_type')
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
            
            # Get effective draw length using proper hierarchy (bow setup > user fallback)
            current_user = get_current_user_optional()
            user_id = current_user['id'] if current_user else None
            effective_draw_length, draw_length_source = get_effective_draw_length(
                user_id, bow_config=data
            )
            
            print(f"🎯 Using draw length: {effective_draw_length}\" from {draw_length_source}")
            
            bow_config = BowConfiguration(
                draw_weight=float(data['draw_weight']),
                draw_length=effective_draw_length,  # Use corrected draw length
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
                preferred_manufacturers=data.get('preferred_manufacturers', []),
                wood_species=data.get('wood_species', None)
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
            
            # Extract search and filter parameters from request
            search_filters = {
                'search_query': data.get('search_query', '').strip(),
                'manufacturer_filter': data.get('manufacturer_filter', '').strip(),
                'match_quality_min': data.get('match_quality_min'),
                'diameter_range': data.get('diameter_range'),
                'weight_range': data.get('weight_range'),
                'material_filter': data.get('material_filter', '').strip(),
                'sort_by': data.get('sort_by', 'compatibility')
            }
            
            # Clean up empty string filters
            search_filters = {k: v for k, v in search_filters.items() if v != ''}
            
            print(f"🔍 API search filters: {search_filters}")
            
            session = ts.create_tuning_session(
                archer_profile, 
                tuning_goals=[primary_goal],
                material_preference=material_pref,
                search_filters=search_filters
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
                
                # Calculate performance metrics for this arrow
                try:
                    performance_data = calculate_arrow_performance(archer_profile, rec)
                except Exception as perf_error:
                    print(f"Performance calculation failed for arrow {getattr(rec, 'arrow_id', 'unknown')}: {perf_error}")
                    performance_data = {
                        'performance_summary': {
                            'estimated_speed_fps': 250,
                            'total_arrow_weight_grains': 400,
                            'kinetic_energy_40yd': 0,
                            'momentum_40yd': 0,
                            'penetration_score': 0,
                            'penetration_category': 'unknown',
                            'foc_percentage': 0,
                            'foc_category': 'unknown'
                        },
                        'error': f'Performance calculation failed: {str(perf_error)}'
                    }

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
                    'potential_issues': getattr(rec, 'potential_issues', []),
                    # Add comprehensive performance data
                    'performance': performance_data
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

@app.route('/api/tuning-guides/sessions', methods=['POST'])
@token_required
def create_enhanced_tuning_session(current_user):
    """Create a new enhanced tuning session with database storage"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        guide_type = data.get('guide_type')
        arrow_id = data.get('arrow_id')
        arrow_length = data.get('arrow_length')
        point_weight = data.get('point_weight')
        bow_setup_id = data.get('bow_setup_id')
        
        if not all([guide_type, arrow_id, arrow_length, point_weight, bow_setup_id]):
            return jsonify({'error': 'Missing required fields: guide_type, arrow_id, arrow_length, point_weight, bow_setup_id'}), 400
        
        # Get database connection
        db = get_database()
        if not db:
            return jsonify({"error": "Database not available"}), 500
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Create session in database
        cursor.execute('''
            INSERT INTO guide_sessions (
                user_id, bow_setup_id, guide_name, guide_type, status, 
                current_step, total_steps, arrow_id, arrow_length, 
                point_weight, started_at, notes
            ) VALUES (?, ?, ?, ?, 'active', 1, 10, ?, ?, ?, CURRENT_TIMESTAMP, ?)
        ''', (
            current_user['id'], bow_setup_id, f"{guide_type.replace('_', ' ').title()} Session", 
            guide_type, arrow_id, arrow_length, point_weight, 
            data.get('notes', '')
        ))
        
        session_id = cursor.lastrowid
        conn.commit()
        
        # Return session data
        session_data = {
            'session_id': session_id,
            'guide_type': guide_type,
            'arrow_id': arrow_id,
            'arrow_length': arrow_length,
            'point_weight': point_weight,
            'bow_setup_id': bow_setup_id,
            'status': 'active',
            'created_at': datetime.now().isoformat()
        }
        
        return jsonify(session_data), 201
        
    except Exception as e:
        print(f"Error creating enhanced tuning session: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/api/tuning-guides/sessions/<int:session_id>/complete', methods=['POST'])
@token_required
def complete_tuning_session(current_user, session_id):
    """Complete a tuning session and optionally save results to journal"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Get database connection
        db = get_database()
        if not db:
            return jsonify({"error": "Database not available"}), 500
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Get session details
        cursor.execute('''
            SELECT gs.*, a.manufacturer, a.model_name, bs.name as bow_name
            FROM guide_sessions gs
            LEFT JOIN arrows a ON gs.arrow_id = a.id
            LEFT JOIN bow_setups bs ON gs.bow_setup_id = bs.id
            WHERE gs.id = ? AND gs.user_id = ?
        ''', (session_id, current_user['id']))
        
        session = cursor.fetchone()
        if not session:
            return jsonify({'error': 'Session not found or access denied'}), 404
        
        # Update session status
        cursor.execute('''
            UPDATE guide_sessions 
            SET status = 'completed', completed_at = CURRENT_TIMESTAMP,
                completion_notes = ?
            WHERE id = ?
        ''', (data.get('completion_notes', ''), session_id))
        
        # Create journal entry if requested (skip if handled externally)
        journal_entry_id = None
        if data.get('save_to_journal', True) and not data.get('skip_journal_creation', False):
            # Prepare journal entry data
            arrow_name = f"{session[12]} {session[13]}" if session[12] and session[13] else f"Arrow {session[7]}"
            bow_name = session[14] if session[14] else f"Bow Setup {session[2]}"
            
            title = f"{session[3].replace('_', ' ').title()} Session - {arrow_name}"
            content = f"""# {title}

## Session Details
- **Arrow**: {arrow_name}
- **Bow Setup**: {bow_name}  
- **Arrow Length**: {session[8]}"
- **Point Weight**: {session[9]} grains
- **Session Duration**: {session[6]} to {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Test Results
{data.get('test_summary', 'Test results recorded during session.')}

## Conclusions
{data.get('conclusion', 'Session completed successfully.')}

## Notes
{data.get('completion_notes', session[11] if session[11] else 'No additional notes.')}
"""
            
            # Insert journal entry
            cursor.execute('''
                INSERT INTO journal_entries (
                    user_id, entry_type, title, content, 
                    bow_setup_id, arrow_id, is_favorite, created_at
                ) VALUES (?, 'tuning_session', ?, ?, ?, ?, 0, CURRENT_TIMESTAMP)
            ''', (current_user['id'], title, content, session[2], session[7]))
            
            journal_entry_id = cursor.lastrowid
        
        conn.commit()
        
        response_data = {
            'success': True,
            'session_id': session_id,
            'status': 'completed',
            'journal_entry_id': journal_entry_id,
            'message': 'Session completed successfully'
        }
        
        if journal_entry_id:
            response_data['journal_saved'] = True
            response_data['message'] += ' and saved to journal'
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"Error completing tuning session: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/api/tuning-guides/sessions/<int:session_id>', methods=['GET'])
@token_required  
def get_tuning_guide_session(current_user, session_id):
    """Get tuning session details"""
    try:
        # Get database connection
        db = get_database()
        if not db:
            return jsonify({"error": "Database not available"}), 500
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Get session with related data
        cursor.execute('''
            SELECT gs.*, a.manufacturer, a.model_name, a.material,
                   bs.name as bow_name, bs.bow_type
            FROM guide_sessions gs
            LEFT JOIN arrows a ON gs.arrow_id = a.id  
            LEFT JOIN bow_setups bs ON gs.bow_setup_id = bs.id
            WHERE gs.id = ? AND gs.user_id = ?
        ''', (session_id, current_user['id']))
        
        session = cursor.fetchone()
        if not session:
            return jsonify({'error': 'Session not found or access denied'}), 404
        
        # Convert to dict
        session_data = {
            'session_id': session[0],
            'user_id': session[1],
            'bow_setup_id': session[2],
            'guide_name': session[3],
            'guide_type': session[4],
            'status': session[5],
            'started_at': session[6],
            'arrow_id': session[7],
            'arrow_length': session[8],
            'point_weight': session[9],
            'notes': session[11],
            'completed_at': session[12] if len(session) > 12 else None,
            'completion_notes': session[13] if len(session) > 13 else None,
            'arrow': {
                'manufacturer': session[14] if len(session) > 14 else None,
                'model_name': session[15] if len(session) > 15 else None,
                'material': session[16] if len(session) > 16 else None
            },
            'bow_setup': {
                'name': session[17] if len(session) > 17 else None,
                'bow_type': session[18] if len(session) > 18 else None
            }
        }
        
        return jsonify(session_data), 200
        
    except Exception as e:
        print(f"Error getting tuning session: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/api/tuning-guides/<int:session_id>', methods=['GET'])
@token_required  
def get_session_data(current_user, session_id):
    """Get tuning session data for the frontend page - simplified endpoint"""
    try:
        # Get database connection
        db = get_database()
        if not db:
            return jsonify({"error": "Database not available"}), 500
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Get session with complete related data for enhanced journal entries
        cursor.execute('''
            SELECT gs.*, 
                   a.manufacturer, a.model_name, a.material,
                   ss.spine, ss.outer_diameter, ss.gpi_weight, ss.inner_diameter, 
                   ss.diameter_category, ss.wall_thickness, ss.nock_size,
                   ss.straightness_tolerance, ss.weight_tolerance,
                   bs.name, bs.bow_type, bs.draw_weight, bs.draw_length,
                   bs.bow_make, bs.bow_model, bs.brace_height, bs.riser_brand, bs.riser_model,
                   bs.limb_brand, bs.limb_model, bs.compound_brand, bs.compound_model,
                   bs.ibo_speed, bs.measured_speed_fps, bs.description
            FROM guide_sessions gs
            LEFT JOIN arrows a ON gs.arrow_id = a.id  
            LEFT JOIN spine_specifications ss ON a.id = ss.arrow_id
            LEFT JOIN bow_setups bs ON gs.bow_setup_id = bs.id
            WHERE gs.id = ? AND gs.user_id = ?
        ''', (session_id, current_user['id']))
        
        session = cursor.fetchone()
        if not session:
            return jsonify({'error': 'Session not found or access denied'}), 404
        
        # Convert to dict with frontend-friendly structure with complete data
        # Column mapping based on the SQL query:
        # gs.* (guide_sessions columns 0-19), then arrow data (20-22), spine specs (23-31), bow setup (32+)
        session_data = {
            'session_id': session[0],  # gs.id
            'guide_type': session[4],   # gs.guide_type
            'status': session[5],       # gs.status 
            'started_at': session[8],   # gs.started_at
            'arrow_id': session[15],    # gs.arrow_id
            'arrow_length': session[16], # gs.arrow_length 
            'point_weight': session[17], # gs.point_weight
            'bow_setup_id': session[2], # gs.bow_setup_id
            'notes': session[10] if session[10] else '', # gs.notes
            'arrow': {
                'id': session[15],  # gs.arrow_id
                'manufacturer': session[20] if len(session) > 20 and session[20] else 'Unknown',  # a.manufacturer
                'model_name': session[21] if len(session) > 21 and session[21] else 'Unknown',    # a.model_name
                'material': session[22] if len(session) > 22 and session[22] else 'Unknown',      # a.material
                'spine': session[23] if len(session) > 23 and session[23] else None,              # ss.spine
                'outer_diameter': session[24] if len(session) > 24 and session[24] else None,     # ss.outer_diameter
                'gpi_weight': session[25] if len(session) > 25 and session[25] else None,         # ss.gpi_weight
                'inner_diameter': session[26] if len(session) > 26 and session[26] else None,     # ss.inner_diameter
                'diameter_category': session[27] if len(session) > 27 and session[27] else None,  # ss.diameter_category
                'wall_thickness': session[28] if len(session) > 28 and session[28] else None,     # ss.wall_thickness
                'nock_size': session[29] if len(session) > 29 and session[29] else None,          # ss.nock_size
                'straightness_tolerance': session[30] if len(session) > 30 and session[30] else None, # ss.straightness_tolerance
                'weight_tolerance': session[31] if len(session) > 31 and session[31] else None    # ss.weight_tolerance
            },
            'bow_setup': {
                'id': session[2],  # gs.bow_setup_id
                'name': session[32] if len(session) > 32 and session[32] else 'Unknown Setup',           # bs.name
                'bow_type': session[33] if len(session) > 33 and session[33] else 'compound',            # bs.bow_type
                'draw_weight': session[34] if len(session) > 34 and session[34] else 0,                  # bs.draw_weight
                'draw_length': session[35] if len(session) > 35 and session[35] else 0,                  # bs.draw_length
                'bow_make': session[36] if len(session) > 36 and session[36] else None,                  # bs.bow_make
                'bow_model': session[37] if len(session) > 37 and session[37] else None,                 # bs.bow_model
                'brace_height': session[38] if len(session) > 38 and session[38] else None,              # bs.brace_height
                'riser_brand': session[39] if len(session) > 39 and session[39] else None,               # bs.riser_brand
                'riser_model': session[40] if len(session) > 40 and session[40] else None,               # bs.riser_model
                'limb_brand': session[41] if len(session) > 41 and session[41] else None,                # bs.limb_brand
                'limb_model': session[42] if len(session) > 42 and session[42] else None,                # bs.limb_model
                'compound_brand': session[43] if len(session) > 43 and session[43] else None,            # bs.compound_brand
                'compound_model': session[44] if len(session) > 44 and session[44] else None,            # bs.compound_model
                'ibo_speed': session[45] if len(session) > 45 and session[45] else None,                 # bs.ibo_speed
                'measured_speed_fps': session[46] if len(session) > 46 and session[46] else None,        # bs.measured_speed_fps
                'description': session[47] if len(session) > 47 and session[47] else None               # bs.description
            }
        }
        
        return jsonify(session_data), 200
        
    except Exception as e:
        print(f"Error getting session data: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/api/tuning-guides/sessions/<int:session_id>/test', methods=['POST'])
@token_required
def record_tuning_test(current_user, session_id):
    """Record a test result for a tuning session"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Get database connection
        db = get_database()
        if not db:
            return jsonify({"error": "Database not available"}), 500
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Verify session exists and belongs to user
        cursor.execute('''
            SELECT id, status FROM guide_sessions 
            WHERE id = ? AND user_id = ?
        ''', (session_id, current_user['id']))
        
        session = cursor.fetchone()
        if not session:
            return jsonify({'error': 'Session not found or access denied'}), 404
        
        if session[1] != 'active':
            return jsonify({'error': 'Session is not active'}), 400
        
        # Record test data properly formatted for different tuning types
        if data.get('test_type') == 'paper_tuning':
            test_summary = f"Test {data.get('test_number', 'N/A')}: "
            test_summary += f"Tear at {data.get('tear_position', 'unknown')} "
            test_summary += f"({data.get('tear_direction', 'unknown')} direction), "
            test_summary += f"magnitude: {data.get('tear_magnitude', 'unknown')}"
            
            if data.get('environmental_conditions'):
                env = data.get('environmental_conditions')
                if env.get('wind') or env.get('lighting'):
                    test_summary += f", conditions: wind={env.get('wind', 'unknown')} lighting={env.get('lighting', 'unknown')}"
            
            if data.get('notes'):
                test_summary += f", notes: {data.get('notes')}"
        elif data.get('test_type') == 'bareshaft_tuning':
            test_data = data.get('test_data', {})
            test_summary = f"Test {data.get('test_number', 'N/A')}: "
            test_summary += f"Distance: {test_data.get('shooting_distance_m', 'unknown')}m, "
            test_summary += f"Offset: {test_data.get('offset_distance_cm', 'unknown')}cm {test_data.get('bareshaft_offset', 'unknown')}, "
            test_summary += f"Consistency: {test_data.get('group_consistency', 'unknown')}"
            
            if data.get('notes'):
                test_summary += f", notes: {data.get('notes')}"
        else:
            test_summary = f"Test {data.get('test_number', 'N/A')}: {data.get('result', 'No result')}"
        
        # Generate intelligent recommendations using TuningRuleEngine
        recommendations = []
        tuning_analysis = {}
        
        if data.get('test_type') == 'paper_tuning' and data.get('tear_direction'):
            direction = data.get('tear_direction')
            if direction == 'clean':
                recommendations.append("Perfect! This arrow is well-tuned.")
            elif direction in ['high', 'low']:
                recommendations.append("Vertical tear detected. Check nocking point height or arrow spine.")
            elif direction in ['left', 'right']:
                recommendations.append("Horizontal tear detected. Adjust rest position or arrow spine.")
            else:
                recommendations.append("Multi-directional tear. May need combined adjustments.")
        elif data.get('test_type') == 'bareshaft_tuning':
            # Use TuningRuleEngine for bareshaft analysis
            try:
                # Get bow setup information for this session
                cursor.execute('''
                    SELECT bs.bow_type, bs.handedness 
                    FROM guide_sessions gs
                    JOIN bow_setups bs ON gs.bow_setup_id = bs.id
                    WHERE gs.id = ?
                ''', (session_id,))
                bow_info = cursor.fetchone()
                
                if bow_info:
                    bow_type = bow_info[0] if bow_info[0] else 'compound'
                    handedness = bow_info[1] if bow_info[1] else 'RH'
                    
                    # Create rule engine and analyze test
                    rule_engine = create_tuning_rule_engine(bow_type, handedness)
                    test_data_for_analysis = data.get('test_data', {})
                    tuning_analysis = rule_engine.analyze_test_result('bareshaft_tuning', test_data_for_analysis)
                    
                    # Extract recommendations from analysis
                    if tuning_analysis.get('recommendations'):
                        for rec in tuning_analysis['recommendations']:
                            rec_text = f"{rec.get('component', 'Setup')}: {rec.get('action', 'adjust')} {rec.get('magnitude', '')}"
                            if rec.get('reason'):
                                rec_text += f" - {rec.get('reason')}"
                            recommendations.append(rec_text)
                    
                    if not recommendations:
                        recommendations.append("Analysis complete. Check detailed results for specific adjustments.")
                else:
                    recommendations.append("Could not retrieve bow setup information for detailed analysis.")
            except Exception as e:
                print(f"Error in bareshaft tuning analysis: {e}")
                recommendations.append("Basic analysis: Review offset distance and direction for tuning adjustments.")
        
        # Store test data in session_data and summary in notes
        try:
            # Get current session_data to append new test
            cursor.execute('SELECT session_data FROM guide_sessions WHERE id = ?', (session_id,))
            current_session_data = cursor.fetchone()[0]
            
            # Parse existing session data
            session_data = {}
            if current_session_data:
                try:
                    session_data = json.loads(current_session_data)
                except json.JSONDecodeError:
                    session_data = {}
            
            # Initialize tests array if it doesn't exist
            if 'tests' not in session_data:
                session_data['tests'] = []
            
            # Add new test data
            test_record = {
                'test_number': data.get('test_number'),
                'test_type': data.get('test_type'),
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'test_data': data.get('test_data', {}),
                'notes': data.get('notes', ''),
                'summary': test_summary
            }
            
            # Include tuning analysis if available
            if tuning_analysis:
                test_record['analysis'] = tuning_analysis
            
            session_data['tests'].append(test_record)
            
            # Update both session_data and notes
            cursor.execute('''
                UPDATE guide_sessions 
                SET notes = COALESCE(notes, '') || ? || char(10),
                    current_step = current_step + 1,
                    session_data = ?
                WHERE id = ?
            ''', (test_summary, json.dumps(session_data), session_id))
            
        except Exception as e:
            print(f"Error storing session data: {e}")
            # Fall back to just updating notes
            cursor.execute('''
                UPDATE guide_sessions 
                SET notes = COALESCE(notes, '') || ? || char(10),
                    current_step = current_step + 1
                WHERE id = ?
            ''', (test_summary, session_id))
        
        conn.commit()
        
        response_data = {
            'success': True,
            'message': 'Test recorded successfully',
            'test_number': data.get('test_number'),
            'id': session_id,  # Return session ID as test ID for frontend
            'recommendations': recommendations
        }
        
        # Include detailed tuning analysis for bareshaft tests
        if tuning_analysis:
            response_data['analysis'] = {
                'confidence_score': tuning_analysis.get('confidence_score', 0),
                'detailed_recommendations': tuning_analysis.get('recommendations', []),
                'analysis_summary': tuning_analysis.get('analysis_summary', ''),
                'tuning_status': tuning_analysis.get('tuning_status', 'unknown')
            }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"Error recording tuning test: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

# User Authentication API

@app.route('/api/auth/google', methods=['POST'])
def google_auth():
    data = request.get_json()
    code = data.get('code')

    if not code:
        return jsonify({'error': 'No authorization code provided'}), 400

    user, needs_profile_completion = get_user_from_google_token(code)

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
    
    # Map database column names to frontend expected names
    if 'user_draw_length' in user_dict:
        user_dict['draw_length'] = user_dict['user_draw_length']
        # Keep user_draw_length for backward compatibility but prioritize draw_length for frontend
    
    return jsonify(user_dict)

@app.route('/api/user/profile', methods=['PUT'])
@token_required
def update_user_profile(current_user):
    """Update current authenticated user's profile details including archer-specific fields"""
    # Using unified database - ArrowDatabase
    db = get_database()
    if not db:
        return jsonify({"error": "Database not available"}), 500
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
    
    # Validate and convert shooting styles (can be array or single value)
    valid_styles = ['target', 'hunting', 'traditional', '3d']
    if shooting_style is not None:
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
            # Convert any other type to string representation
            shooting_style = json.dumps([str(shooting_style)])
    
    if draw_length and (draw_length < 20 or draw_length > 36):
        return jsonify({'error': 'Draw length must be between 20 and 36 inches'}), 400
    
    # Convert preferred_manufacturers list to JSON string if provided
    if preferred_manufacturers is not None:
        if isinstance(preferred_manufacturers, list):
            preferred_manufacturers = json.dumps(preferred_manufacturers)
        elif not isinstance(preferred_manufacturers, str):
            # Convert any other type to string
            preferred_manufacturers = str(preferred_manufacturers)
    
    # Convert shooting_style list to JSON string if provided
    if shooting_style is not None:
        if isinstance(shooting_style, list):
            shooting_style = json.dumps(shooting_style)
        elif not isinstance(shooting_style, str):
            # Convert any other type to string
            shooting_style = str(shooting_style)
    
    try:
        from arrow_database import ArrowDatabase
        db = ArrowDatabase()
        
        # Build update dict with only provided fields
        update_data = {}
        if name is not None:
            update_data['name'] = name
        if draw_length is not None:
            update_data['user_draw_length'] = draw_length  # Map draw_length to user_draw_length column
        if skill_level is not None:
            update_data['skill_level'] = skill_level
        if shooting_style is not None:
            update_data['shooting_style'] = shooting_style
        if preferred_manufacturers is not None:
            update_data['preferred_manufacturers'] = preferred_manufacturers
        if notes is not None:
            update_data['notes'] = notes
        
        # Debug logging to identify the issue
        print(f"Debug - Update data types:")
        for key, value in update_data.items():
            print(f"  {key}: {type(value)} = {value}")
        
        # Ensure all values are serializable for SQLite
        for key, value in update_data.items():
            if isinstance(value, list):
                print(f"WARNING: Found list value for {key}: {value}")
                update_data[key] = json.dumps(value)
            elif value is not None and not isinstance(value, (str, int, float, bool)):
                print(f"WARNING: Converting {key} from {type(value)} to string: {value}")
                update_data[key] = str(value)
            
        # Update user profile
        success = db.update_user(current_user['id'], **update_data)
        
        if success:
            # Get updated user data
            updated_user = db.get_user_by_id(current_user['id'])
        
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
    # Using unified database - ArrowDatabase
    db = get_database()
    if not db:
        return jsonify({"error": "Database not available"}), 500
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bow_setups WHERE user_id = ?", (current_user['id'],))
    setups = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in setups])

@app.route('/api/bow-setups/<int:setup_id>', methods=['GET'])
@token_required
def get_bow_setup(current_user, setup_id):
    """Get a specific bow setup with its details"""
    # Using unified database - ArrowDatabase
    db = get_database()
    if not db:
        return jsonify({"error": "Database not available"}), 500
    conn = db.get_connection()
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
    """Create a new bow setup with manufacturer learning"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    try:
        # Use the ArrowDatabase for creating bow setups
        from arrow_database import ArrowDatabase
        db = ArrowDatabase()
        new_setup_id = db.create_bow_setup(current_user['id'], **data)
        
        if not new_setup_id:
            return jsonify({'error': 'Failed to create bow setup'}), 500
        
        # Learn from manufacturer entries in the bow setup
        learning_results = []
        try:
            from equipment_learning_manager import EquipmentLearningManager
            learning = EquipmentLearningManager()
            
            # Learn from compound bow manufacturer
            if data.get('compound_brand') and data.get('bow_type') == 'compound':
                result = learning.learn_equipment_entry(
                    data['compound_brand'],
                    data.get('compound_model', 'Unknown Model'),
                    'compound_bows',
                    current_user['id']
                )
                learning_results.append({
                    'manufacturer': data['compound_brand'],
                    'category': 'compound_bows',
                    'result': result
                })
                
            # Learn from riser manufacturer
            if data.get('riser_brand') and data.get('bow_type') in ['recurve', 'traditional']:
                category = 'recurve_risers' if data['bow_type'] == 'recurve' else 'traditional_risers'
                result = learning.learn_equipment_entry(
                    data['riser_brand'],
                    data.get('riser_model', 'Unknown Model'),
                    category,
                    current_user['id']
                )
                learning_results.append({
                    'manufacturer': data['riser_brand'],
                    'category': category,
                    'result': result
                })
                
            # Learn from limb manufacturer
            if data.get('limb_brand') and data.get('bow_type') in ['recurve', 'traditional']:
                category = 'recurve_limbs' if data['bow_type'] == 'recurve' else 'traditional_limbs'
                result = learning.learn_equipment_entry(
                    data['limb_brand'],
                    data.get('limb_model', 'Unknown Model'),
                    category,
                    current_user['id']
                )
                learning_results.append({
                    'manufacturer': data['limb_brand'],
                    'category': category,
                    'result': result
                })
            
            # Log learning results
            for lr in learning_results:
                if lr['result']['new_manufacturer']:
                    print(f"📚 New manufacturer learned: '{lr['manufacturer']}' in {lr['category']} (pending approval)")
                if lr['result']['new_model']:
                    print(f"📚 New model learned: '{lr['manufacturer']}' model for {lr['category']}")
                    
        except Exception as e:
            print(f"Warning: Manufacturer learning failed during bow setup creation: {e}")
        
        # Get the created setup data
        new_setup = db.get_bow_setup(new_setup_id)
        
        if not new_setup:
            return jsonify({'error': 'Failed to retrieve created bow setup'}), 500
        
        # Add learning results to response for debugging
        response_data = dict(new_setup)
        if learning_results:
            response_data['manufacturer_learning'] = learning_results
        
        return jsonify(response_data), 201
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
        # Using unified database - ArrowDatabase
        from change_log_service import ChangeLogService
        
        db = get_database()
        if not db:
            return jsonify({"error": "Database not available"}), 500
        change_service = ChangeLogService()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Get current setup data for change tracking
        cursor.execute("SELECT * FROM bow_setups WHERE id = ? AND user_id = ?", (setup_id, current_user['id']))
        current_setup = cursor.fetchone()
        
        if not current_setup:
            conn.close()
            return jsonify({'error': 'Setup not found or you do not have permission to edit it'}), 404
        
        # Extract user_note from data for change logging
        user_note = data.pop('user_note', None)
        
        # Update the setup using the unified database
        from arrow_database import ArrowDatabase
        db = ArrowDatabase()
        
        # First verify the setup belongs to the current user
        setup = db.get_bow_setup(setup_id)
        if not setup or setup.get('user_id') != current_user['id']:
            conn.close()
            return jsonify({'error': 'Setup not found or you do not have permission to edit it'}), 404
            
        # Update the setup
        success = db.update_bow_setup(setup_id, **data)
        updated_setup = db.get_bow_setup(setup_id) if success else None
        
        if not updated_setup:
            conn.close()
            return jsonify({'error': 'Failed to update setup'}), 500
        
        # Log the setup changes
        changes_logged = []
        trackable_fields = {
            'name': 'Setup name',
            'bow_type': 'Bow type', 
            'draw_weight': 'Draw weight',
            'draw_length': 'Draw length',  # Added unified draw length tracking
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
        
        # Learn from manufacturer changes in the bow setup
        learning_results = []
        try:
            from equipment_learning_manager import EquipmentLearningManager
            learning = EquipmentLearningManager()
            
            # Check if manufacturers were changed and learn from new ones
            manufacturer_fields = [
                ('compound_brand', 'compound_model', 'compound_bows'),
                ('riser_brand', 'riser_model', 'recurve_risers'),  # Will be adjusted based on bow_type
                ('limb_brand', 'limb_model', 'recurve_limbs')     # Will be adjusted based on bow_type
            ]
            
            bow_type = data.get('bow_type', current_setup['bow_type'])
            
            for brand_field, model_field, default_category in manufacturer_fields:
                if brand_field in data and data[brand_field]:
                    # Only learn if the manufacturer actually changed
                    old_brand = current_setup[brand_field] or ''
                    new_brand = data[brand_field] or ''
                    
                    if old_brand != new_brand and new_brand:
                        # Determine correct category based on bow type
                        if brand_field == 'compound_brand' and bow_type == 'compound':
                            category = 'compound_bows'
                        elif brand_field == 'riser_brand' and bow_type in ['recurve', 'traditional']:
                            category = 'recurve_risers' if bow_type == 'recurve' else 'traditional_risers'
                        elif brand_field == 'limb_brand' and bow_type in ['recurve', 'traditional']:
                            category = 'recurve_limbs' if bow_type == 'recurve' else 'traditional_limbs'
                        else:
                            continue  # Skip if bow type doesn't match manufacturer type
                        
                        model_name = data.get(model_field, current_setup.get(model_field, 'Unknown Model'))
                        
                        result = learning.learn_equipment_entry(
                            new_brand,
                            model_name,
                            category,
                            current_user['id']
                        )
                        
                        learning_results.append({
                            'manufacturer': new_brand,
                            'category': category,
                            'field': brand_field,
                            'result': result
                        })
            
            # Log learning results
            for lr in learning_results:
                if lr['result']['new_manufacturer']:
                    print(f"📚 New manufacturer learned from setup update: '{lr['manufacturer']}' in {lr['category']} (pending approval)")
                if lr['result']['new_model']:
                    print(f"📚 New model learned from setup update: '{lr['manufacturer']}' model for {lr['category']}")
                    
        except Exception as e:
            print(f"Warning: Manufacturer learning failed during bow setup update: {e}")
        
        conn.close()
        
        # Add learning results to response for debugging
        response_data = dict(updated_setup)
        if learning_results:
            response_data['manufacturer_learning'] = learning_results
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Error updating bow setup: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/bow-setups/<int:setup_id>', methods=['DELETE'])
@token_required
def delete_bow_setup(current_user, setup_id):
    """Delete a bow setup"""
    # Using unified database - ArrowDatabase
    db = get_database()
    if not db:
        return jsonify({"error": "Database not available"}), 500
    conn = db.get_connection()
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
        # Using unified database - ArrowDatabase
        db = get_database()
        if not db:
            return jsonify({"error": "Database not available"}), 500
        conn = db.get_connection()
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
                    nock_weight = ?, insert_weight = ?, wrap_weight = ?, fletching_weight = ?, bushing_weight = ?
                WHERE id = ?
            ''', (
                calculated_spine,
                compatibility_score,
                data.get('notes'),
                data.get('nock_weight', 10),
                data.get('insert_weight', 0),
                data.get('wrap_weight', 0),
                data.get('fletching_weight', 15),
                data.get('bushing_weight', 0),
                existing_record[0]
            ))
            arrow_association_id = existing_record[0]
        else:
            # Insert new record with component weights
            cursor.execute('''
                INSERT INTO setup_arrows 
                (setup_id, arrow_id, arrow_length, point_weight, calculated_spine, compatibility_score, notes,
                 nock_weight, insert_weight, wrap_weight, fletching_weight, bushing_weight)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                data.get('wrap_weight', 0),
                data.get('fletching_weight', 15),
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
        
        # Get the created association with arrow details from unified database
        cursor.execute('''
            SELECT sa.*, a.manufacturer, a.model_name, a.material
            FROM setup_arrows sa
            LEFT JOIN arrows a ON sa.arrow_id = a.id
            WHERE sa.id = ?
        ''', (arrow_association_id,))
        result = cursor.fetchone()
        conn.close()
        
        # Extract arrow data from unified query
        arrow_data = None
        if result and result['manufacturer']:
            arrow_data = {
                'manufacturer': result['manufacturer'],
                'model_name': result['model_name'], 
                'material': result['material']
            }
        
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
        
        # Calculate performance metrics for the added arrow
        try:
            # Create a mock arrow recommendation object for performance calculation
            class MockArrowRec:
                def __init__(self, arrow_data, data):
                    self.gpi_weight = data.get('gpi_weight', 400) or 400  # Default if not provided
                    self.outer_diameter = data.get('outer_diameter', 0.246) or 0.246
                    self.arrow_type = arrow_data[2] if arrow_data and len(arrow_data) > 2 else 'hunting'  # material
                    self.arrow_id = data['arrow_id']
            
            # Create a mock archer profile from bow setup data  
            class MockArcherProfile:
                def __init__(self, bow_setup, arrow_data):
                    self.arrow_length = arrow_data['arrow_length']
                    self.point_weight_preference = arrow_data['point_weight']
                    self.shooting_style = 'hunting'  # Default
                    
                    # Create mock bow config
                    class MockBowConfig:
                        def __init__(self, setup_data):
                            self.draw_weight = setup_data.get('draw_weight', 50) or 50
                            self.bow_type = type('BowType', (), {'value': setup_data.get('bow_type', 'compound') or 'compound'})()
                    
                    self.bow_config = MockBowConfig(dict(bow_setup))
            
            mock_arrow = MockArrowRec(arrow_data, data)
            mock_profile = MockArcherProfile(bow_setup, data)
            
            # Enhanced arrow speed estimation for new arrow addition
            enhanced_speed = None
            try:
                # Prepare speed calculation data
                arrow_weight_grains = (mock_arrow.gpi_weight * mock_profile.arrow_length) + mock_profile.point_weight_preference + 25
                string_material = 'dacron'  # Default for new arrows (no string equipment likely configured yet)
                
                # Get effective draw length based on bow type
                effective_draw_length, draw_length_source = get_effective_draw_length(
                    current_user['id'], bow_data=dict(bow_setup)
                )
                
                # Call enhanced speed calculation (no chronograph data for new arrows)
                enhanced_speed_result = calculate_enhanced_arrow_speed_internal(
                    bow_ibo_speed=dict(bow_setup).get('ibo_speed', 0),  # Let the function handle fallbacks
                    bow_draw_weight=dict(bow_setup).get('draw_weight', 50),
                    bow_draw_length=effective_draw_length,  # Use bow-type specific draw length
                    bow_type=dict(bow_setup).get('bow_type', 'compound'),
                    arrow_weight_grains=arrow_weight_grains,
                    string_material=string_material,
                    setup_id=None,  # No setup_id for new arrow
                    arrow_id=None   # No chronograph data for new arrow
                )
                enhanced_speed = enhanced_speed_result.get('speed') if isinstance(enhanced_speed_result, dict) else enhanced_speed_result
                speed_source = enhanced_speed_result.get('source', 'estimated') if isinstance(enhanced_speed_result, dict) else 'estimated'
                print(f"Enhanced speed for new arrow addition: {enhanced_speed} FPS (source: {speed_source})")
                
            except Exception as speed_error:
                print(f"Enhanced speed calculation failed for new arrow: {speed_error}")
                enhanced_speed = None
            
            performance_data = calculate_arrow_performance(mock_profile, mock_arrow, estimated_speed=enhanced_speed)
            # Add draw length source information
            if 'draw_length_source' in locals():
                performance_data['draw_length_source'] = draw_length_source
                performance_data['effective_draw_length'] = effective_draw_length
            response_data['performance'] = performance_data
            
        except Exception as perf_error:
            print(f"Performance calculation failed for added arrow: {perf_error}")
            response_data['performance'] = {
                'performance_summary': {
                    'estimated_speed_fps': 250,
                    'total_arrow_weight_grains': 400,
                    'kinetic_energy_40yd': 0,
                    'momentum_40yd': 0,
                    'penetration_score': 0,
                    'penetration_category': 'unknown',
                    'foc_percentage': 0,
                    'foc_category': 'unknown'
                },
                'error': f'Performance calculation failed: {str(perf_error)}'
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
        # Get unified database connection
        db = get_database()
        if not db:
            return jsonify({"error": "Database not available"}), 500
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Verify the bow setup belongs to the current user
        cursor.execute("SELECT * FROM bow_setups WHERE id = ? AND user_id = ?", (setup_id, current_user['id']))
        bow_setup = cursor.fetchone()
        
        if not bow_setup:
            return jsonify({'error': 'Bow setup not found or access denied'}), 404
        
        # Get all arrows for this setup with arrow details in single query (unified database)
        cursor.execute('''
            SELECT sa.*, a.manufacturer, a.model_name, a.material, a.description,
                   a.image_url, a.arrow_type
            FROM setup_arrows sa
            LEFT JOIN arrows a ON sa.arrow_id = a.id
            WHERE sa.setup_id = ?
            ORDER BY sa.created_at DESC
        ''', (setup_id,))
        
        rows = cursor.fetchall()
        print(f"🔍 [get_setup_arrows] Found {len(rows)} arrows for setup_id {setup_id}")
        
        # Get arrow details with spine specifications (unified database)
        arrow_details = {}
        for i, row in enumerate(rows):
            if hasattr(row, 'keys'):
                created_at = row['created_at'] if 'created_at' in row.keys() else 'unknown'
                print(f"  - Arrow {i+1}: ID={row['id']}, arrow_id={row['arrow_id']}, created_at={created_at}")
            
            arrow_id = row['arrow_id']
            print(f"Looking for spine specs for arrow_id: {arrow_id}")  # Debug log
            
            # Get spine specifications for this arrow (same unified database)
            cursor.execute('''
                SELECT spine, outer_diameter, inner_diameter, gpi_weight, length_options
                FROM spine_specifications WHERE arrow_id = ?
                ORDER BY spine ASC
            ''', (arrow_id,))
            spine_specs = cursor.fetchall()
            
            # Build arrow details from unified database
            if row['manufacturer']:  # Arrow data exists
                arrow_details[arrow_id] = {
                    'basic_info': {
                        'manufacturer': row['manufacturer'],
                        'model_name': row['model_name'],
                        'material': row['material'],
                        'description': row['description'],
                        'image_url': row['image_url'],
                        'arrow_type': row['arrow_type']
                    },
                    'spine_specifications': [dict(spec) for spec in spine_specs] if spine_specs else []
                }
                print(f"Found arrow data in unified DB: {row['manufacturer']} {row['model_name']}")
            else:
                print(f"Warning: Arrow ID {arrow_id} not found in unified database")
        
        conn.close()
        
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
                for field in ['nock_weight', 'insert_weight', 'wrap_weight', 'fletching_weight']:
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
            
            # Extract performance data from notes field if present
            try:
                # Load performance data from dedicated performance_data column
                # Handle SQLite3 Row objects (use bracket notation instead of .get())
                performance_data_raw = row['performance_data'] if 'performance_data' in row and row['performance_data'] else None
                if performance_data_raw:
                    import json
                    performance_data = json.loads(performance_data_raw)
                    
                    # Check if we have the correct performance_summary structure
                    if 'performance_summary' in performance_data:
                        # Already in correct format from calculate_arrow_performance
                        arrow_info['performance'] = performance_data
                    elif 'foc_percentage' in performance_data:
                        # Legacy enhanced FOC format - convert to performance_summary format
                        performance_summary = {
                            'foc_percentage': performance_data.get('foc_percentage', 0),
                            'estimated_speed_fps': performance_data.get('estimated_speed_fps', 260),
                            'kinetic_energy_40yd': performance_data.get('kinetic_energy_40yd', 45.0),
                            'total_arrow_weight_grains': performance_data.get('total_arrow_weight_grains', 400),
                            'penetration_category': performance_data.get('penetration_category', 'acceptable'),
                            'penetration_score': performance_data.get('penetration_score', 75)
                        }
                        arrow_info['performance'] = {
                            'performance_summary': performance_summary,
                            'detailed_data': performance_data  # Keep original data
                        }
                    else:
                        # Unknown format - use as-is
                        arrow_info['performance'] = performance_data
                # Fallback: check for legacy performance data in notes field
                elif row['notes'] and 'Performance:' in row['notes']:
                    import json
                    # Extract JSON from notes field (legacy format)
                    notes = row['notes']
                    if 'Performance: {' in notes:
                        json_start = notes.find('Performance: {') + len('Performance: ')
                        json_str = notes[json_start:]
                        # Handle cases where there might be additional text after JSON
                        if ' | Performance:' in json_str:
                            json_str = json_str[:json_str.find(' | Performance:')]
                        performance_data = json.loads(json_str)
                        arrow_info['performance'] = performance_data
            except Exception as perf_error:
                print(f"Error parsing performance data for arrow {row['arrow_id']}: {perf_error}")
                # Continue without performance data rather than failing
            
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
        # Using unified database - ArrowDatabase
        db = get_database()
        if not db:
            return jsonify({"error": "Database not available"}), 500
        conn = db.get_connection()
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

@app.route('/api/bow-setups/<int:setup_id>/arrows/calculate-performance', methods=['POST'])
@token_required
def calculate_setup_arrows_performance(current_user, setup_id):
    """Calculate performance metrics for all arrows in a bow setup"""
    conn = None
    try:
        # Get user database connection
        # Using unified database - ArrowDatabase
        db = get_database()
        if not db:
            return jsonify({"error": "Database not available"}), 500
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Verify the bow setup belongs to the current user
        cursor.execute("SELECT * FROM bow_setups WHERE id = ? AND user_id = ?", (setup_id, current_user['id']))
        bow_setup = cursor.fetchone()
        
        if not bow_setup:
            return jsonify({'error': 'Bow setup not found or access denied'}), 404
        
        # Get all arrows in the setup with arrow details (unified database)
        cursor.execute('''
            SELECT sa.*, a.id as arrow_id, a.manufacturer, a.model_name, a.material, a.arrow_type
            FROM setup_arrows sa
            LEFT JOIN arrows a ON sa.arrow_id = a.id
            WHERE sa.setup_id = ?
        ''', (setup_id,))
        setup_arrows = cursor.fetchall()
        
        if not setup_arrows:
            return jsonify({'message': 'No arrows found in setup', 'updated_arrows': []})
        
        print(f"Successfully connected to unified database with {len(setup_arrows)} arrows")
        
        updated_arrows = []
        
        for setup_arrow in setup_arrows:
            try:
                arrow_id = setup_arrow['arrow_id']
                print(f"Processing arrow_id {arrow_id}: {setup_arrow['manufacturer']} {setup_arrow['model_name']}")
                
                if not setup_arrow['manufacturer']:
                    print(f"Skipping arrow_id {arrow_id} - not found in unified database")
                    continue
                
                # Get spine specifications from unified database
                print(f"Querying spine specs for arrow_id: {arrow_id}")
                cursor.execute('''
                    SELECT spine, outer_diameter, inner_diameter, gpi_weight
                    FROM spine_specifications WHERE arrow_id = ?
                    ORDER BY spine ASC LIMIT 1
                ''', (arrow_id,))
                spine_data = cursor.fetchone()
                
                # Create arrow data from unified query results
                arrow_data = {
                    'id': arrow_id,
                    'manufacturer': setup_arrow['manufacturer'],
                    'model_name': setup_arrow['model_name'], 
                    'material': setup_arrow['material'],
                    'arrow_type': setup_arrow['arrow_type']
                }
                
                if spine_data:
                    print(f"Found spine data: {dict(spine_data)}")
                else:
                    print(f"No spine data found for arrow_id: {setup_arrow['arrow_id']}")
                    # Try to see if ANY spine data exists for this arrow
                    arrow_cursor.execute('SELECT COUNT(*) as count FROM spine_specifications WHERE arrow_id = ?', (setup_arrow['arrow_id'],))
                    count_result = arrow_cursor.fetchone()
                    print(f"  Total spine specs for this arrow: {count_result['count'] if count_result else 'unknown'}")
                
                # Create mock objects for performance calculation
                class MockArrowRec:
                    def __init__(self, arrow_data, spine_data, setup_arrow):
                        # Handle None/0 GPI weight with debugging
                        raw_gpi = spine_data['gpi_weight'] if spine_data else None
                        self.gpi_weight = raw_gpi if raw_gpi and raw_gpi > 0 else 8.5  # Default realistic GPI
                        self.outer_diameter = spine_data['outer_diameter'] if spine_data else 0.246
                        self.arrow_type = arrow_data['arrow_type'] if arrow_data['arrow_type'] else 'hunting'
                        self.arrow_id = setup_arrow['arrow_id']
                        
                        # Debug logging
                        print(f"MockArrow Debug - raw_gpi: {raw_gpi}, final_gpi: {self.gpi_weight}, arrow_id: {self.arrow_id}")
                        if spine_data:
                            print(f"  Spine data available: spine={spine_data.get('spine')}, outer_diameter={spine_data.get('outer_diameter')}, gpi_weight={spine_data.get('gpi_weight')}")
                        else:
                            print(f"  No spine data found for arrow_id: {self.arrow_id}")
                
                class MockArcherProfile:
                    def __init__(self, bow_setup, setup_arrow):
                        self.arrow_length = setup_arrow['arrow_length']
                        self.point_weight_preference = setup_arrow['point_weight']
                        self.shooting_style = 'hunting'  # Default
                        
                        class MockBowConfig:
                            def __init__(self, setup_data):
                                self.draw_weight = setup_data['draw_weight'] or 50
                                self.bow_type = type('BowType', (), {'value': setup_data['bow_type'] or 'compound'})()
                        
                        self.bow_config = MockBowConfig(dict(bow_setup))
                
                mock_arrow = MockArrowRec(dict(arrow_data), dict(spine_data) if spine_data else None, dict(setup_arrow))
                mock_profile = MockArcherProfile(bow_setup, dict(setup_arrow))
                
                # Enhanced arrow speed estimation for bulk calculation
                enhanced_speed = None
                try:
                    # Prepare speed calculation data
                    arrow_weight_grains = (mock_arrow.gpi_weight * mock_profile.arrow_length) + mock_profile.point_weight_preference + 25
                    string_material = 'dacron'  # Default for bulk calculation
                    
                    # Try to get string equipment data for this setup
                    try:
                        cursor.execute('''
                            SELECT specifications 
                            FROM bow_equipment 
                            WHERE setup_id = ? AND category = 'String'
                            LIMIT 1
                        ''', (setup_arrow['setup_id'],))
                        string_equipment = cursor.fetchone()
                        
                        if string_equipment and string_equipment['specifications']:
                            import json
                            spec_data = json.loads(string_equipment['specifications'])
                            if spec_data.get('material'):
                                string_material = spec_data['material'].lower()
                    except Exception:
                        pass  # Use default string material
                    
                    # Get effective draw length based on bow type
                    effective_draw_length, draw_length_source = get_effective_draw_length(
                        current_user['id'], bow_data=dict(bow_setup)
                    )
                    
                    # Call enhanced speed calculation
                    enhanced_speed_result = calculate_enhanced_arrow_speed_internal(
                        bow_ibo_speed=dict(bow_setup).get('ibo_speed', 0),  # Let the function handle fallbacks
                        bow_draw_weight=dict(bow_setup).get('draw_weight', 50),
                        bow_draw_length=effective_draw_length,  # Use bow-type specific draw length
                        bow_type=dict(bow_setup).get('bow_type', 'compound'),
                        arrow_weight_grains=arrow_weight_grains,
                        string_material=string_material,
                        setup_id=setup_arrow['setup_id'],
                        arrow_id=setup_arrow['arrow_id']
                    )
                    enhanced_speed = enhanced_speed_result.get('speed') if isinstance(enhanced_speed_result, dict) else enhanced_speed_result
                    speed_source = enhanced_speed_result.get('source', 'estimated') if isinstance(enhanced_speed_result, dict) else 'estimated'
                    print(f"Bulk enhanced speed for arrow {setup_arrow['arrow_id']}: {enhanced_speed} FPS (source: {speed_source})")
                    
                except Exception as speed_error:
                    print(f"Bulk enhanced speed calculation failed for arrow {setup_arrow['arrow_id']}: {speed_error}")
                    enhanced_speed = None
                
                # Calculate performance with enhanced speed
                performance_data = calculate_arrow_performance(mock_profile, mock_arrow, estimated_speed=enhanced_speed)
                
                # Add draw length source information
                if 'draw_length_source' in locals():
                    performance_data['draw_length_source'] = draw_length_source
                    performance_data['effective_draw_length'] = effective_draw_length
                
                # Store performance data as JSON in dedicated performance_data column
                import json
                performance_json = json.dumps(performance_data)
                
                # Update the setup_arrows record with performance data in dedicated column
                cursor.execute('''
                    UPDATE setup_arrows 
                    SET performance_data = ?
                    WHERE id = ?
                ''', (performance_json, setup_arrow['id']))
                
                updated_arrows.append({
                    'arrow_setup_id': setup_arrow['id'],
                    'arrow_id': setup_arrow['arrow_id'],
                    'performance': performance_data
                })
                
            except Exception as arrow_error:
                print(f"Error calculating performance for arrow {setup_arrow['arrow_id']}: {arrow_error}")
                continue
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': f'Performance calculated for {len(updated_arrows)} arrows',
            'updated_arrows': updated_arrows,
            'setup_id': setup_id
        })
        
    except Exception as e:
        if conn:
            conn.close()
        print(f"Error calculating setup arrows performance: {e}")
        return jsonify({'error': 'Failed to calculate performance'}), 500

@app.route('/api/setup-arrows/<int:setup_arrow_id>/calculate-performance', methods=['POST'])
def calculate_individual_arrow_performance(setup_arrow_id):
    """Calculate performance metrics for a single arrow in a bow setup"""
    conn = None
    try:
        # Get current user (optional authentication)
        current_user = get_current_user_optional()
        
        # Parse request data for bow configuration
        data = request.get_json() or {}
        bow_config = data.get('bow_config', {})
        
        # Debug: Log what the frontend is sending
        print(f"🔍 Frontend bow_config received: {bow_config}")
        print(f"🔍 Current user: {current_user['email'] if current_user else 'Anonymous'}")
        
        # Get unified database connection
        db = get_database()
        if not db:
            return jsonify({'error': 'Database not available'}), 500
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Get the arrow setup with arrow details and verify ownership (unified database)
        cursor.execute('''
            SELECT sa.*, bs.user_id, bs.draw_weight, bs.bow_type, bs.ibo_speed,
                   a.id as arrow_id, a.manufacturer, a.model_name, a.material, a.arrow_type
            FROM setup_arrows sa
            JOIN bow_setups bs ON sa.setup_id = bs.id
            LEFT JOIN arrows a ON sa.arrow_id = a.id
            WHERE sa.id = ?
        ''', (setup_arrow_id,))
        setup_arrow = cursor.fetchone()
        
        if not setup_arrow:
            return jsonify({'error': 'Arrow setup not found'}), 404
            
        # Only check ownership if user is authenticated
        if current_user and setup_arrow['user_id'] != current_user['id']:
            return jsonify({'error': 'Access denied'}), 403
        # Allow anonymous access for public arrow setups or when not authenticated
        elif not current_user:
            print(f"🔍 Anonymous access to arrow setup {setup_arrow_id}")
        
        if not setup_arrow['manufacturer']:
            return jsonify({'error': 'Arrow not found in unified database'}), 404
        
        try:
            # Create arrow data from unified query results
            arrow_data = {
                'id': setup_arrow['arrow_id'],
                'manufacturer': setup_arrow['manufacturer'],
                'model_name': setup_arrow['model_name'],
                'material': setup_arrow['material'],
                'arrow_type': setup_arrow['arrow_type']
            }
            
            # Get spine specifications from unified database
            cursor.execute('''
                SELECT spine, outer_diameter, inner_diameter, gpi_weight
                FROM spine_specifications WHERE arrow_id = ?
                ORDER BY spine ASC LIMIT 1
            ''', (setup_arrow['arrow_id'],))
            spine_data = cursor.fetchone()
            
            # Create mock objects for performance calculation
            class MockArrowRec:
                def __init__(self, arrow_data, spine_data, setup_arrow):
                    raw_gpi = spine_data['gpi_weight'] if spine_data else None
                    self.gpi_weight = raw_gpi if raw_gpi and raw_gpi > 0 else 8.5
                    self.outer_diameter = spine_data['outer_diameter'] if spine_data else 0.246
                    self.arrow_type = arrow_data['arrow_type'] if arrow_data['arrow_type'] else 'hunting'
                    self.arrow_id = setup_arrow['arrow_id']
            
            class MockArcherProfile:
                def __init__(self, setup_data, bow_config_override=None):
                    self.arrow_length = setup_data['arrow_length']
                    self.point_weight_preference = setup_data['point_weight']
                    self.shooting_style = 'hunting'
                    
                    class MockBowConfig:
                        def __init__(self, bow_data, config_override=None):
                            # Use bow_config from request if provided, otherwise fall back to database
                            if config_override:
                                self.draw_weight = config_override.get('draw_weight', bow_data.get('draw_weight', 50))
                                self.bow_type = type('BowType', (), {'value': config_override.get('bow_type', bow_data.get('bow_type', 'compound'))})()
                                # Use bow-type specific draw length logic
                                if 'draw_length' in config_override:
                                    self.draw_length = config_override['draw_length']
                                    self.draw_length_source = f"Request override ({config_override['draw_length']}\")"
                                else:
                                    bow_config_dict = {**bow_data, **config_override}
                                    self.draw_length, self.draw_length_source = get_effective_draw_length(
                                        bow_data.get('user_id'), bow_config=bow_config_dict
                                    )
                            else:
                                self.draw_weight = bow_data.get('draw_weight', 50)
                                self.bow_type = type('BowType', (), {'value': bow_data.get('bow_type', 'compound')})()
                                self.draw_length, self.draw_length_source = get_effective_draw_length(
                                    bow_data.get('user_id'), bow_data=bow_data
                                )
                    
                    self.bow_config = MockBowConfig(setup_data, bow_config_override)
            
            mock_arrow = MockArrowRec(dict(arrow_data), dict(spine_data) if spine_data else None, dict(setup_arrow))
            mock_profile = MockArcherProfile(dict(setup_arrow), bow_config)
            
            # Enhanced arrow speed estimation using chronograph data and string materials
            enhanced_speed = None
            try:
                # Prepare data for enhanced speed calculation
                # Convert Row objects to dict for .get() method compatibility
                bow_config_dict = dict(bow_config) if bow_config else {}
                setup_arrow_dict = dict(setup_arrow)
                
                calculated_arrow_weight = (mock_arrow.gpi_weight * mock_profile.arrow_length) + mock_profile.point_weight_preference + 25
                
                # Get user's draw length for proper calculation
                user_draw_length = 29  # Default fallback
                try:
                    if current_user:
                        cursor.execute('SELECT user_draw_length FROM users WHERE id = ?', (current_user['id'],))
                        user_result = cursor.fetchone()
                        if user_result and user_result['user_draw_length']:
                            user_draw_length = user_result['user_draw_length']
                except:
                    pass  # Use default
                
                speed_request_data = {
                    'bow_ibo_speed': bow_config_dict.get('ibo_speed', setup_arrow_dict.get('ibo_speed', 0)),  # Let the function handle fallbacks
                    'bow_draw_weight': bow_config_dict.get('draw_weight', setup_arrow_dict.get('draw_weight', 50)),
                    'bow_draw_length': bow_config_dict.get('draw_length', user_draw_length),
                    'bow_type': bow_config_dict.get('bow_type', setup_arrow_dict.get('bow_type', 'compound')),
                    'arrow_weight_grains': calculated_arrow_weight,
                    'string_material': 'dacron',  # Default to slowest for safety
                    'setup_id': setup_arrow['setup_id'],
                    'arrow_id': setup_arrow['arrow_id']
                }
                
                print(f"🔍 Speed Request Data Debug:")
                print(f"   bow_ibo_speed: {speed_request_data['bow_ibo_speed']}")
                print(f"   bow_draw_weight: {speed_request_data['bow_draw_weight']}")
                print(f"   bow_draw_length: {speed_request_data['bow_draw_length']}")
                print(f"   bow_type: {speed_request_data['bow_type']}")
                print(f"   arrow_weight_grains: {speed_request_data['arrow_weight_grains']} (gpi: {mock_arrow.gpi_weight}, length: {mock_profile.arrow_length}, point: {mock_profile.point_weight_preference})")
                print(f"   string_material: {speed_request_data['string_material']}")
                print(f"   setup_id: {speed_request_data['setup_id']}")
                print(f"   arrow_id: {speed_request_data['arrow_id']}")
                
                # Validate bow setup data for realistic values
                try:
                    validation_result = validate_bow_setup_data(
                        bow_type=speed_request_data['bow_type'],
                        bow_draw_weight=speed_request_data['bow_draw_weight'], 
                        bow_draw_length=speed_request_data['bow_draw_length'],
                        bow_ibo_speed=speed_request_data['bow_ibo_speed']
                    )
                    
                    print(f"🔍 Bow Setup Validation: {validation_result['summary']}")
                    
                    for warning in validation_result['warnings']:
                        print(f"⚠️  Bow Setup Warning: {warning}")
                    
                    for error in validation_result['errors']:
                        print(f"❌ Bow Setup Error: {error}")
                    
                    if not validation_result['valid']:
                        print(f"⚠️  Proceeding with calculations despite validation errors")
                        
                except Exception as validation_error:
                    print(f"⚠️  Bow setup validation failed: {validation_error}")
                
                # Get string equipment data for speed calculation
                try:
                    cursor.execute('''
                        SELECT specifications 
                        FROM bow_equipment 
                        WHERE setup_id = ? AND category = 'String'
                        LIMIT 1
                    ''', (setup_arrow['setup_id'],))
                    string_equipment = cursor.fetchone()
                    
                    if string_equipment and string_equipment['specifications']:
                        import json
                        spec_data = json.loads(string_equipment['specifications'])
                        if spec_data.get('material'):
                            speed_request_data['string_material'] = spec_data['material'].lower()
                except Exception as string_error:
                    print(f"Warning: Could not retrieve string equipment data: {string_error}")
                
                # Call enhanced speed calculation function directly
                enhanced_speed_result = calculate_enhanced_arrow_speed_internal(
                    bow_ibo_speed=speed_request_data['bow_ibo_speed'],
                    bow_draw_weight=speed_request_data['bow_draw_weight'],
                    bow_draw_length=speed_request_data['bow_draw_length'],
                    bow_type=speed_request_data['bow_type'],
                    arrow_weight_grains=speed_request_data['arrow_weight_grains'],
                    string_material=speed_request_data['string_material'],
                    setup_id=speed_request_data['setup_id'],
                    arrow_id=speed_request_data['arrow_id']
                )
                enhanced_speed = enhanced_speed_result.get('speed') if isinstance(enhanced_speed_result, dict) else enhanced_speed_result
                speed_source = enhanced_speed_result.get('source', 'estimated') if isinstance(enhanced_speed_result, dict) else 'estimated'
                print(f"🎯 Enhanced speed calculated: {enhanced_speed} FPS (source: {speed_source}) for setup_id={speed_request_data['setup_id']}, arrow_id={speed_request_data['arrow_id']}")
                
                # Ensure we have a valid speed (should be > 0 and < 500 fps)
                if enhanced_speed and isinstance(enhanced_speed, (int, float)) and 50 < enhanced_speed < 500:
                    print(f"✅ Using enhanced speed: {enhanced_speed} FPS")
                else:
                    print(f"⚠️  Enhanced speed invalid ({enhanced_speed}), falling back to basic calculation")
                    enhanced_speed = None
                
            except Exception as speed_error:
                print(f"❌ Enhanced speed calculation failed, falling back to basic calculation: {speed_error}")
                import traceback
                traceback.print_exc()
                enhanced_speed = None
            
            # Calculate performance with enhanced speed
            performance_data = calculate_arrow_performance(mock_profile, mock_arrow, estimated_speed=enhanced_speed)
            
            # Add speed source information to performance data
            if performance_data and 'performance_summary' in performance_data:
                if enhanced_speed and isinstance(enhanced_speed, (int, float)) and 'speed_source' in locals():
                    performance_data['performance_summary']['speed_source'] = speed_source
                    if speed_source == 'chronograph':
                        performance_data['performance_summary']['speed_source_info'] = f'Weight-adjusted from measured chronograph data'
                        print(f"📊 Performance data updated with chronograph speed source")
                    elif speed_source == 'enhanced_estimated':
                        performance_data['performance_summary']['speed_source_info'] = f'Enhanced calculation with string material and bow efficiency'
                        print(f"📊 Performance data updated with enhanced estimated speed source")
                    else:
                        performance_data['performance_summary']['speed_source_info'] = f'Basic calculation from bow specifications'
                        print(f"📊 Performance data updated with estimated speed source")
                else:
                    performance_data['performance_summary']['speed_source'] = 'estimated'
                    performance_data['performance_summary']['speed_source_info'] = f'Fallback calculation (no enhanced speed data)'
            
            # Store performance data as JSON in dedicated performance_data column
            import json
            performance_json = json.dumps(performance_data)
            
            # Update the setup_arrows record with performance data
            cursor.execute('''
                UPDATE setup_arrows 
                SET performance_data = ?
                WHERE id = ?
            ''', (performance_json, setup_arrow_id))
            
            conn.commit()
            
            return jsonify({
                'message': 'Performance calculated successfully',
                'arrow_setup_id': setup_arrow_id,
                'performance': performance_data
            })
            
        finally:
            pass  # No separate arrow connection to close in unified database
            
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error calculating individual arrow performance: {e}")
        return jsonify({'error': 'Failed to calculate performance'}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/bow-setups/<int:setup_id>/arrows/<int:arrow_id>', methods=['PUT'])
@token_required  
def update_bow_setup_arrow(current_user, setup_id, arrow_id):
    """Update an arrow configuration in a bow setup by setup_id and arrow_id"""
    conn = None
    try:
        data = request.get_json()
        
        # Get user database connection
        # Using unified database - ArrowDatabase
        db = get_database()
        if not db:
            return jsonify({"error": "Database not available"}), 500
        conn = db.get_connection()
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
        'wrap_weight': data.get('wrap_weight', arrow_setup_dict.get('wrap_weight', 0)),
        'compatibility_score': data.get('compatibility_score', arrow_setup_dict.get('compatibility_score'))
    }
    
    # Update the arrow setup with component weights
    cursor.execute('''
        UPDATE setup_arrows 
        SET arrow_length = ?, point_weight = ?, calculated_spine = ?, notes = ?,
            nock_weight = ?, insert_weight = ?, wrap_weight = ?, compatibility_score = ?
        WHERE id = ?
    ''', (
        new_data['arrow_length'],
        new_data['point_weight'],
        new_data['calculated_spine'],
        new_data['notes'],
        new_data['nock_weight'],
        new_data['insert_weight'],
        new_data['wrap_weight'],
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
        # Using unified database - ArrowDatabase
        db = get_database()
        if not db:
            return jsonify({"error": "Database not available"}), 500
        conn = db.get_connection()
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

@app.route('/api/setup-arrows/<int:setup_arrow_id>/details', methods=['GET'])
def get_setup_arrow_details(setup_arrow_id):
    """Get comprehensive details for a specific arrow setup including arrow data, setup configuration, and performance"""
    conn = None
    try:
        # Get current user (optional authentication)
        current_user = get_current_user_optional()
        
        # Get user database connection
        # Using unified database - ArrowDatabase
        db = get_database()
        if not db:
            return jsonify({"error": "Database not available"}), 500
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Get the arrow setup with bow setup context
        # Only check ownership if user is authenticated
        if current_user:
            cursor.execute('''
                SELECT sa.*, 
                       bs.id as bow_setup_id, bs.name as bow_setup_name, bs.bow_type, 
                       bs.draw_weight, bs.ibo_speed, bs.draw_length
                FROM setup_arrows sa
                JOIN bow_setups bs ON sa.setup_id = bs.id
                WHERE sa.id = ? AND bs.user_id = ?
            ''', (setup_arrow_id, current_user['id']))
        else:
            # Anonymous access - don't filter by user_id
            cursor.execute('''
                SELECT sa.*, 
                       bs.id as bow_setup_id, bs.name as bow_setup_name, bs.bow_type, 
                       bs.draw_weight, bs.ibo_speed, bs.draw_length
                FROM setup_arrows sa
                JOIN bow_setups bs ON sa.setup_id = bs.id
                WHERE sa.id = ?
            ''', (setup_arrow_id,))
        
        setup_arrow = cursor.fetchone()
        
        if not setup_arrow:
            return jsonify({'error': 'Arrow setup not found'}), 404
        
        # Convert to dict for easier access
        setup_dict = dict(setup_arrow)
        
        # Get arrow details and spine specifications from unified database
        arrow_data = None
        spine_specifications = []
        
        print(f"[setup_arrow_details] Arrow ID: {setup_dict['arrow_id']}")  # Debug
        
        if setup_dict['arrow_id']:
            try:
                # Get comprehensive arrow information from unified database
                cursor.execute('''
                    SELECT id, manufacturer, model_name, material, description, 
                           arrow_type, carbon_content, image_url, source_url
                    FROM arrows WHERE id = ?
                ''', (setup_dict['arrow_id'],))
                arrow_result = cursor.fetchone()
                
                if arrow_result:
                    arrow_data = dict(arrow_result)
                    print(f"[setup_arrow_details] Arrow data found: {arrow_data.get('manufacturer')} {arrow_data.get('model_name')}")  # Debug
                    
                    # Get spine specifications from unified database
                    cursor.execute('''
                        SELECT id, spine, outer_diameter, inner_diameter, gpi_weight, 
                               length_options, wall_thickness, insert_weight_range, 
                               nock_size, notes, straightness_tolerance, weight_tolerance
                        FROM spine_specifications 
                        WHERE arrow_id = ?
                        ORDER BY spine ASC
                    ''', (setup_dict['arrow_id'],))
                    spine_specs = cursor.fetchall()
                    spine_specifications = [dict(spec) for spec in spine_specs] if spine_specs else []
                else:
                    print(f"[setup_arrow_details] Arrow ID {setup_dict['arrow_id']} NOT FOUND in unified database")  # Debug
                    
            except Exception as e:
                print(f"Error fetching arrow details from unified database: {e}")
        
        # Get performance data if available
        performance_data = None
        if 'performance_data' in setup_dict and setup_dict['performance_data']:
            try:
                import json
                performance_data = json.loads(setup_dict['performance_data'])
            except:
                performance_data = None
        
        # Add spine specifications to arrow data if arrow data exists
        if arrow_data and spine_specifications:
            arrow_data['spine_specifications'] = spine_specifications
        
        # Build comprehensive response
        response_data = {
            'setup_arrow': {
                'id': setup_dict['id'],
                'arrow_id': setup_dict['arrow_id'],
                'setup_id': setup_dict['setup_id'],
                'arrow_length': setup_dict['arrow_length'],
                'point_weight': setup_dict['point_weight'],
                'calculated_spine': setup_dict['calculated_spine'],
                'compatibility_score': setup_dict['compatibility_score'],
                'notes': setup_dict['notes'],
                'created_at': setup_dict['created_at'],
                # Component weights
                'nock_weight': setup_dict.get('nock_weight', 10),
                'insert_weight': setup_dict.get('insert_weight', 0),
                'wrap_weight': setup_dict.get('wrap_weight', 0),
                'fletching_weight': setup_dict.get('fletching_weight', 15),
                # Performance data
                'performance': performance_data
            },
            'arrow': arrow_data,
            'spine_specifications': spine_specifications,  # Keep for backward compatibility
            'bow_setup': {
                'id': setup_dict['bow_setup_id'],
                'name': setup_dict['bow_setup_name'],
                'bow_type': setup_dict['bow_type'],
                'draw_weight': setup_dict['draw_weight'],
                'draw_length': setup_dict['draw_length'],
                'ibo_speed': setup_dict['ibo_speed']
            }
        }
        
        conn.close()
        return jsonify(response_data)
        
    except Exception as e:
        if conn:
            conn.close()
        print(f"Error in get_setup_arrow_details: {e}")
        import traceback
        traceback.print_exc()
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
                arrow_type=arrow_filters.get('arrow_type'),  # Use arrow_type from filters
                model_search=arrow_filters.get('search'),
                limit=25
            )
            wood_arrows_2 = db.search_arrows(
                manufacturer="Traditional Wood Arrows", 
                arrow_type=arrow_filters.get('arrow_type'),  # Use arrow_type from filters
                model_search=arrow_filters.get('search'),
                limit=25
            )
            compatible_arrows = wood_arrows_1 + wood_arrows_2
        else:
            # Regular search for other materials
            compatible_arrows = db.search_arrows(
                manufacturer=arrow_filters.get('manufacturer'),
                arrow_type=arrow_filters.get('arrow_type'),  # Use arrow_type from filters, not bow_config
                model_search=arrow_filters.get('search'),
                limit=1000  # Much higher limit to include all arrows
            )
        
        # Minimal filtering - only apply material filter if explicitly requested
        filtered_arrows = []
        for arrow in compatible_arrows:
            # Basic compatibility check
            is_compatible = True
            
            # Only filter by material if explicitly requested in bow_config
            if bow_config.get('arrow_material'):
                arrow_material = arrow.get('material') or ''
                arrow_material = arrow_material.lower()
                selected_material = bow_config['arrow_material'].lower()
                
                # Only exclude if there's a clear material mismatch
                if selected_material == 'wood' and 'wood' not in arrow_material:
                    is_compatible = False
                elif selected_material == 'aluminum' and 'aluminum' not in arrow_material:
                    is_compatible = False
                # For carbon, accept any non-wood, non-aluminum arrow (more permissive)
                elif selected_material == 'carbon' and ('wood' in arrow_material):
                    is_compatible = False
            
            if is_compatible:
                filtered_arrows.append(arrow)
        
        # Sort by arrow type to give variety, then by manufacturer
        filtered_arrows.sort(key=lambda x: (x.get('arrow_type', 'zz'), x.get('manufacturer', ''), x.get('model_name', '')))
        
        return jsonify({
            'compatible_arrows': filtered_arrows[:200],  # Show many more results to ensure variety
            'total_compatible': len(filtered_arrows),
            'bow_config': bow_config
        })
        
    except Exception as e:
        import traceback
        return jsonify({'error': f'Compatible arrows error: {str(e)}'}), 500

# Real-time compatibility score calculation
@app.route('/api/calculate-compatibility-score', methods=['POST'])
def calculate_compatibility_score():
    """Calculate real-time compatibility score for arrow configuration changes"""
    try:
        data = request.get_json()
        
        # Extract required parameters
        arrow_id = data.get('arrow_id')
        bow_config = data.get('bow_config', {})
        arrow_config = data.get('arrow_config', {})
        
        if not arrow_id:
            return jsonify({'error': 'arrow_id is required'}), 400
        
        # Get arrow details from database
        db = get_database()
        arrow_details = db.get_arrow_details(arrow_id)
        
        if not arrow_details:
            return jsonify({'error': 'Arrow not found'}), 404
        
        # Create a simplified match request for compatibility calculation
        from arrow_matching_engine import MatchRequest
        
        # Extract bow configuration parameters
        draw_weight = bow_config.get('draw_weight', 60)
        draw_length = bow_config.get('draw_length', 28)
        bow_type = bow_config.get('bow_type', 'compound')
        
        # Extract arrow configuration parameters
        arrow_length = arrow_config.get('arrow_length', 32)
        point_weight = arrow_config.get('point_weight', 100)
        calculated_spine = arrow_config.get('calculated_spine')
        
        # Calculate optimal spine for this configuration
        from spine_calculator import SpineCalculator
        spine_calc = SpineCalculator()
        
        # Create bow configuration for spine calculation
        from spine_calculator import BowConfiguration
        bow_config_for_calc = BowConfiguration(
            bow_type=bow_type,
            draw_weight=draw_weight,
            draw_length=draw_length
        )
        
        # Use arrow length from configuration instead of default
        spine_result = spine_calc.calculate_required_spine(
            bow_config=bow_config_for_calc,
            arrow_length=arrow_length,
            point_weight=point_weight
        )
        optimal_spine = spine_result['calculated_spine']
        
        # Calculate spine range
        tolerance = 50  # +/- spine tolerance
        spine_range = {
            'minimum': optimal_spine - tolerance,
            'maximum': optimal_spine + tolerance
        }
        
        # Use user-selected spine if provided, otherwise find the best spine match
        best_spine_match = None
        min_deviation = float('inf')
        
        if calculated_spine:
            # User has selected a specific spine - use that for calculation
            selected_spine_value = float(calculated_spine)
            min_deviation = abs(selected_spine_value - optimal_spine)
            
            # Find the matching spine specification for the selected spine
            for spine_spec in arrow_details['spine_specifications']:
                if float(spine_spec['spine']) == selected_spine_value:
                    best_spine_match = spine_spec
                    break
            
            # If selected spine not found in specifications, create a mock one
            if not best_spine_match:
                best_spine_match = {
                    'spine': selected_spine_value,
                    'gpi_weight': 8.0,  # Default GPI
                    'outer_diameter': 0.246  # Default diameter
                }
        else:
            # No spine selected - find the best available spine match
            for spine_spec in arrow_details['spine_specifications']:
                spine_value = float(spine_spec['spine'])
                deviation = abs(spine_value - optimal_spine)
                
                if deviation < min_deviation:
                    min_deviation = deviation
                    best_spine_match = spine_spec
        
        if not best_spine_match:
            return jsonify({'error': 'No spine specifications found for arrow'}), 400
        
        # Create a basic match request for scoring
        match_request = MatchRequest(
            bow_config=bow_config_for_calc,
            arrow_length=arrow_length,
            point_weight=point_weight,
            preferred_manufacturers=[],
            material_preference=None,
            target_diameter_range=None
        )
        
        # Calculate compatibility score using arrow matching engine logic
        from arrow_matching_engine import ArrowMatchingEngine
        matching_engine = ArrowMatchingEngine(db)
        
        # Calculate match score
        compatibility_score = matching_engine._calculate_match_score(
            arrow_details, best_spine_match, optimal_spine, spine_range, match_request
        )
        
        # Round to whole number for display
        compatibility_score = round(compatibility_score)
        
        # Determine compatibility rating
        if compatibility_score >= 90:
            rating = 'excellent'
        elif compatibility_score >= 75:
            rating = 'good'
        elif compatibility_score >= 60:
            rating = 'fair'
        else:
            rating = 'poor'
        
        # Calculate additional metrics for context
        spine_accuracy = max(0, 100 - (min_deviation / 50) * 100)  # 50 spine deviation = 0% accuracy
        
        return jsonify({
            'compatibility_score': compatibility_score,
            'compatibility_rating': rating,
            'optimal_spine': round(optimal_spine, 1),
            'selected_spine': float(calculated_spine) if calculated_spine else best_spine_match['spine'],
            'spine_accuracy': round(spine_accuracy, 1),
            'spine_deviation': round(min_deviation, 1),
            'recommendations': {
                'spine_match': 'excellent' if min_deviation < 25 else 'good' if min_deviation < 50 else 'fair' if min_deviation < 100 else 'poor',
                'length_match': 'optimal' if 28 <= arrow_length <= 32 else 'acceptable' if 26 <= arrow_length <= 34 else 'suboptimal'
            }
        })
        
    except Exception as e:
        import traceback
        print(f"Compatibility calculation error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': f'Compatibility calculation failed: {str(e)}'}), 500

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
        # Using unified database - ArrowDatabase
        # Check admin status from current_user data
        if not current_user.get('is_admin', False):
            return jsonify({'error': 'Admin access required'}), 403
        
        return f(current_user, *args, **kwargs)
    
    return decorated_function

@app.route('/api/admin/statistics', methods=['GET'])
@token_required
@admin_required
def get_admin_statistics(current_user):
    """Get comprehensive usage statistics for admin dashboard"""
    try:
        db = get_unified_database()
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        # Basic counts
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE status = 'approved'")
        approved_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE last_login > date('now', '-30 days')")
        active_users_30d = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM bow_setups")
        total_bow_setups = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM bow_equipment")
        total_equipment = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM arrows")
        total_arrows = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT name) FROM manufacturers WHERE is_active = 1")
        active_manufacturers = cursor.fetchone()[0]
        
        # Journal entries if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='journal_entries'")
        journal_table_exists = cursor.fetchone()
        journal_entries = 0
        if journal_table_exists:
            cursor.execute("SELECT COUNT(*) FROM journal_entries")
            journal_entries = cursor.fetchone()[0]
        
        # Arrows by manufacturer
        cursor.execute("""
            SELECT m.name, COUNT(a.id) as arrow_count 
            FROM manufacturers m 
            LEFT JOIN arrows a ON m.name = a.manufacturer 
            WHERE m.is_active = 1
            GROUP BY m.name 
            ORDER BY arrow_count DESC
        """)
        arrows_by_manufacturer = [{"manufacturer": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        # Recent activity (last 7 days)
        cursor.execute("SELECT COUNT(*) FROM users WHERE created_at > date('now', '-7 days')")
        new_users_7d = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM bow_setups WHERE created_at > date('now', '-7 days')")
        new_setups_7d = cursor.fetchone()[0]
        
        # Equipment categories
        cursor.execute("""
            SELECT category, COUNT(*) as count 
            FROM bow_equipment 
            GROUP BY category 
            ORDER BY count DESC
        """)
        equipment_by_category = [{"category": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'overview': {
                'total_users': total_users,
                'approved_users': approved_users,
                'active_users_30d': active_users_30d,
                'total_bow_setups': total_bow_setups,
                'total_equipment': total_equipment,
                'total_arrows': total_arrows,
                'active_manufacturers': active_manufacturers,
                'journal_entries': journal_entries
            },
            'recent_activity': {
                'new_users_7d': new_users_7d,
                'new_setups_7d': new_setups_7d
            },
            'breakdowns': {
                'arrows_by_manufacturer': arrows_by_manufacturer,
                'equipment_by_category': equipment_by_category
            },
            'generated_at': datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        print(f"Statistics error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/users', methods=['GET'])
@token_required
@admin_required
def get_all_users_admin(current_user):
    """Get all users (admin only)"""
    try:
        # Using unified database - ArrowDatabase
        from arrow_database import ArrowDatabase
        db = ArrowDatabase()
        
        users = db.get_all_users()
        
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
        # Using unified database - ArrowDatabase
        db = get_database()
        if not db:
            return jsonify({"error": "Database not available"}), 500
        
        data = request.get_json()
        is_admin = data.get('is_admin', False)
        from arrow_database import ArrowDatabase
        db = ArrowDatabase()
        
        success = db.set_admin_status(user_id, is_admin)
        
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

@app.route('/api/admin/users/<int:user_id>/status', methods=['PUT'])
@token_required
@admin_required
def update_user_status(current_user, user_id):
    """Update user status (suspend/activate) - admin only"""
    try:
        from arrow_database import ArrowDatabase
        db = ArrowDatabase()
        
        data = request.get_json()
        status = data.get('status', 'active')
        
        # Validate status values
        if status not in ['active', 'suspended']:
            return jsonify({'error': 'Invalid status. Must be "active" or "suspended"'}), 400
        
        # Update user status
        success = db.update_user_status(user_id, status)
        
        if success:
            return jsonify({
                'message': f'User {user_id} status updated to {status}',
                'user_id': user_id,
                'status': status
            })
        else:
            return jsonify({'error': 'Failed to update user status'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_user(current_user, user_id):
    """Delete a non-admin user - admin only"""
    try:
        from arrow_database import ArrowDatabase
        db = ArrowDatabase()
        
        # Check if the user exists and get their details
        user_to_delete = db.get_user_by_id(user_id)
        if not user_to_delete:
            return jsonify({'error': 'User not found'}), 404
            
        # Prevent deletion of admin users
        if user_to_delete.get('is_admin', False):
            return jsonify({'error': 'Cannot delete admin users'}), 403
        
        # Prevent deletion of current user
        if user_id == current_user.get('id'):
            return jsonify({'error': 'Cannot delete yourself'}), 403
        
        # Delete the user and all related data
        success = db.delete_user(user_id)
        
        if success:
            return jsonify({
                'message': f'User {user_to_delete.get("name", user_to_delete.get("email", user_id))} deleted successfully',
                'user_id': user_id
            })
        else:
            return jsonify({'error': 'Failed to delete user'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/check', methods=['GET'])
@token_required
def check_admin_status(current_user):
    """Check if current user has admin access"""
    try:
        # Using unified database for user operations
        from arrow_database import ArrowDatabase
        db = ArrowDatabase()
        
        # Check admin status directly from user data
        is_admin = current_user.get('is_admin', False)
        
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
        if not db:
            return jsonify({"error": "Database not available"}), 500
        
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
        if not db:
            return jsonify({"error": "Database not available"}), 500
        
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
        if not db:
            return jsonify({"error": "Database not available"}), 500
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
        if not db:
            return jsonify({"error": "Database not available"}), 500
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
        if not db:
            return jsonify({"error": "Database not available"}), 500
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
        if not db:
            return jsonify({"error": "Database not available"}), 500
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
        if not db:
            return jsonify({"error": "Database not available"}), 500
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
        if not db:
            return jsonify({"error": "Database not available"}), 500
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
        if not db:
            return jsonify({"error": "Database not available"}), 500
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
        if not db:
            return jsonify({"error": "Database not available"}), 500
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
        if not db:
            return jsonify({"error": "Database not available"}), 500
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
        if not db:
            return jsonify({"error": "Database not available"}), 500
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
        if not db:
            return jsonify({"error": "Database not available"}), 500
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
        if not db:
            return jsonify({"error": "Database not available"}), 500
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
                # Using consolidated database - ArrowDatabase
                db = get_database()
                if not db:
                    return jsonify({"error": "Database not available"}), 500
                user_conn = db.get_connection()
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
            if not db:
                return jsonify({"error": "Database not available"}), 500
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
        # Using unified database - ArrowDatabase
        db = get_database()
        if not db:
            return jsonify({"error": "Database not available"}), 500
        conn = db.get_connection()
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
                        if not db:
                            return jsonify({"error": "Database not available"}), 500
                        if not arrow_db:
                            return jsonify({"error": "Database not available"}), 500
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
        
        # Using unified database - ArrowDatabase
        db = get_database()
        if not db:
            return jsonify({"error": "Database not available"}), 500
        conn = db.get_connection()
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
            # Check for exact manufacturer match in unified database
            cursor.execute('SELECT id FROM manufacturers WHERE LOWER(name) = LOWER(?)', 
                         (data['manufacturer_name'],))
            exact_match = cursor.fetchone()
            
            if exact_match:
                # Exact match found - use existing manufacturer
                manufacturer_id = exact_match['id']
                print(f"✅ Exact manufacturer match found for: '{data['manufacturer_name']}'")
            else:
                # No exact match - this will become a pending manufacturer
                # Preserve the user's exact input without any smart matching alterations
                print(f"📝 New manufacturer: '{data['manufacturer_name']}' - will be saved as pending")
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
        
        # Log the equipment addition
        try:
            from change_log_service import ChangeLogService
            change_service = ChangeLogService()
            
            equipment_name = f"{data['manufacturer_name']} {data['model_name']}"
            change_description = f"Equipment added: {equipment_name} ({data['category_name']})"
            
            change_service.log_equipment_change(
                bow_setup_id=setup_id,
                equipment_id=bow_equipment_id,
                user_id=current_user['id'],
                change_type='add',
                field_name=None,
                old_value=None,
                new_value=None,
                change_description=change_description,
                change_reason=data.get('notes', 'Equipment added to setup')
            )
            print(f"✅ Logged equipment addition: {equipment_name}")
        except Exception as log_error:
            print(f"⚠️  Failed to log equipment addition: {log_error}")
        
        # Auto-learn from this equipment entry
        try:
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
            except ImportError:
                print("Info: Equipment learning manager not available, skipping auto-learning")
                
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
        import traceback
        error_details = {
            'error': str(e),
            'type': type(e).__name__,
            'traceback': traceback.format_exc()
        }
        print(f"Error adding custom bow equipment: {e}")
        print(f"Error type: {type(e).__name__}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': f'Failed to add equipment: {str(e)}'}), 500

@app.route('/api/bow-setups/<int:setup_id>/equipment/<int:equipment_id>', methods=['PUT'])
@token_required
def update_bow_equipment(current_user, setup_id, equipment_id):
    """Update custom equipment configuration in a bow setup with change logging"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Using unified database - ArrowDatabase
        from change_log_service import ChangeLogService
        
        db = get_database()
        if not db:
            return jsonify({"error": "Database not available"}), 500
        change_service = ChangeLogService()
        conn = db.get_connection()
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
    conn = None
    try:
        # Using unified database - ArrowDatabase
        from change_log_service import ChangeLogService
        
        db = get_database()
        if not db:
            return jsonify({"error": "Database not available"}), 500
        change_service = ChangeLogService()
        conn = db.get_connection()
        
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
            
        cursor = conn.cursor()
        
        # Get equipment details for logging before deletion
        print(f"DEBUG: Looking for equipment_id={equipment_id} in setup_id={setup_id} for user_id={current_user['id']}")
        
        cursor.execute('''
            SELECT be.*, bs.user_id 
            FROM bow_equipment be
            JOIN bow_setups bs ON be.bow_setup_id = bs.id
            WHERE be.bow_setup_id = ? AND be.id = ? 
            AND bs.user_id = ? AND be.is_active = 1
        ''', (setup_id, equipment_id, current_user['id']))
        
        equipment_row = cursor.fetchone()
        print(f"DEBUG: Equipment query result: {equipment_row}")
        
        if not equipment_row:
            print(f"DEBUG: Equipment not found - checking alternatives...")
            
            # Check if equipment exists but belongs to different user
            cursor.execute('''
                SELECT be.*, bs.user_id 
                FROM bow_equipment be
                JOIN bow_setups bs ON be.bow_setup_id = bs.id
                WHERE be.bow_setup_id = ? AND be.id = ?
            ''', (setup_id, equipment_id))
            
            alt_row = cursor.fetchone()
            if alt_row:
                print(f"DEBUG: Equipment exists but user_id mismatch or inactive. Actual user_id: {alt_row[-1]}")
            else:
                print(f"DEBUG: Equipment {equipment_id} does not exist at all")
            
            conn.close()
            return jsonify({'error': 'Equipment not found or access denied'}), 404
        
        # Convert row to dict for easier access
        try:
            if hasattr(equipment_row, 'keys'):
                equipment = dict(equipment_row)
            else:
                # Fallback manual conversion
                equipment = {
                    'id': equipment_row[0] if len(equipment_row) > 0 else None,
                    'manufacturer_name': equipment_row[1] if len(equipment_row) > 1 else None,
                    'model_name': equipment_row[2] if len(equipment_row) > 2 else None,
                    'category_name': equipment_row[3] if len(equipment_row) > 3 else None,
                }
        except Exception as conv_error:
            print(f"Error converting equipment row to dict: {conv_error}")
            conn.close()
            return jsonify({'error': 'Failed to process equipment data'}), 500
        
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
        equipment_name = f"{equipment.get('manufacturer_name') or 'Unknown'} {equipment.get('model_name') or 'Equipment'}"
        category = equipment.get('category_name') or 'Equipment'
        
        # Try to log the change, but don't fail the removal if logging fails
        try:
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
        except Exception as log_error:
            print(f"Warning: Failed to log equipment removal: {log_error}")
            # Continue with removal even if logging fails
        
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
        import traceback
        traceback.print_exc()
        
        # Ensure connection is closed on error
        if conn:
            try:
                conn.close()
            except:
                pass
                
        return jsonify({'error': 'Failed to remove equipment'}), 500

@app.route('/api/bow-setups/<int:setup_id>/equipment/<int:equipment_id>/restore', methods=['POST'])
@token_required
def restore_bow_equipment(current_user, setup_id, equipment_id):
    """Restore previously deleted equipment to a bow setup"""
    try:
        # Using unified database - ArrowDatabase
        from change_log_service import ChangeLogService
        
        db = get_database()
        if not db:
            return jsonify({"error": "Database not available"}), 500
        change_service = ChangeLogService()
        conn = db.get_connection()
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
        # Using unified database - ArrowDatabase
        
        db = get_database()
        if not db:
            return jsonify({"error": "Database not available"}), 500
        conn = db.get_connection()
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

# ===== STANDALONE EQUIPMENT ENDPOINT =====

@app.route('/api/equipment/<int:equipment_id>', methods=['GET'])
@token_required
def get_equipment_by_id(current_user, equipment_id):
    """Get equipment details by ID (standalone endpoint for equipment detail pages)"""
    try:
        # Using unified database - ArrowDatabase
        db = get_database()
        if not db:
            return jsonify({"error": "Database not available"}), 500
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Get equipment with bow setup context, ensuring user owns the setup
        cursor.execute('''
            SELECT be.*, bs.user_id, bs.name as setup_name, bs.bow_type
            FROM bow_equipment be
            JOIN bow_setups bs ON be.bow_setup_id = bs.id
            WHERE be.id = ? AND bs.user_id = ? AND be.is_active = 1
        ''', (equipment_id, current_user['id']))
        
        equipment_data = cursor.fetchone()
        if not equipment_data:
            conn.close()
            return jsonify({'error': 'Equipment not found or access denied'}), 404
        
        # Convert to dict for JSON serialization
        equipment = dict(equipment_data)
        
        # Parse custom specifications if they exist
        if equipment.get('custom_specifications'):
            try:
                import json
                equipment['specifications'] = json.loads(equipment['custom_specifications'])
            except:
                equipment['specifications'] = {}
        else:
            equipment['specifications'] = {}
        
        # Add setup context
        equipment['setup_context'] = {
            'id': equipment['bow_setup_id'],
            'name': equipment['setup_name'],
            'bow_type': equipment['bow_type']
        }
        
        # Format installation date if it exists
        if equipment.get('installation_date'):
            equipment['installation_date'] = equipment['installation_date']
        
        conn.close()
        
        return jsonify({
            'success': True,
            'equipment': equipment
        })
        
    except Exception as e:
        print(f"Error getting equipment by ID: {e}")
        if 'conn' in locals():
            try:
                conn.close()
            except:
                pass
        return jsonify({'error': 'Failed to get equipment details'}), 500

@app.route('/api/equipment/<int:equipment_id>', methods=['PATCH'])
@token_required
def update_equipment_by_id(current_user, equipment_id):
    """Update equipment details by ID (standalone endpoint for equipment detail pages)"""
    try:
        # Using unified database - ArrowDatabase
        db = get_database()
        if not db:
            return jsonify({"error": "Database not available"}), 500
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Get equipment with bow setup context, ensuring user owns the setup
        cursor.execute('''
            SELECT be.*, bs.user_id, bs.name as setup_name, bs.bow_type
            FROM bow_equipment be
            JOIN bow_setups bs ON be.bow_setup_id = bs.id
            WHERE be.id = ? AND bs.user_id = ?
        ''', (equipment_id, current_user['id']))
        
        equipment_data = cursor.fetchone()
        if not equipment_data:
            conn.close()
            return jsonify({'error': 'Equipment not found or access denied'}), 404
        
        # Get the update data from request
        data = request.get_json()
        if not data:
            conn.close()
            return jsonify({'error': 'No data provided'}), 400
        
        # Prepare update fields
        update_fields = []
        params = []
        
        # Handle is_active field
        if 'is_active' in data:
            update_fields.append('is_active = ?')
            params.append(1 if data['is_active'] else 0)
        
        # Handle other updatable fields
        updatable_fields = ['manufacturer_name', 'model_name', 'category_name', 'notes', 'image_url']
        for field in updatable_fields:
            if field in data:
                update_fields.append(f'{field} = ?')
                params.append(data[field])
        
        # Handle custom specifications
        if 'specifications' in data:
            update_fields.append('custom_specifications = ?')
            params.append(json.dumps(data['specifications']))
        
        if not update_fields:
            conn.close()
            return jsonify({'error': 'No valid fields to update'}), 400
        
        # Add equipment_id to params for WHERE clause
        params.append(equipment_id)
        
        # Update the equipment
        update_query = f'''
            UPDATE bow_equipment 
            SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        '''
        
        cursor.execute(update_query, params)
        conn.commit()
        
        # Get the updated equipment data
        cursor.execute('''
            SELECT be.*, bs.user_id, bs.name as setup_name, bs.bow_type
            FROM bow_equipment be
            JOIN bow_setups bs ON be.bow_setup_id = bs.id
            WHERE be.id = ? AND bs.user_id = ?
        ''', (equipment_id, current_user['id']))
        
        updated_equipment = dict(cursor.fetchone())
        
        # Parse custom specifications if they exist
        if updated_equipment.get('custom_specifications'):
            try:
                updated_equipment['specifications'] = json.loads(updated_equipment['custom_specifications'])
            except:
                updated_equipment['specifications'] = {}
        else:
            updated_equipment['specifications'] = {}
        
        conn.close()
        
        return jsonify({
            'success': True,
            'is_active': updated_equipment['is_active'] == 1,
            'equipment': updated_equipment
        })
        
    except Exception as e:
        print(f"Error updating equipment by ID: {e}")
        if 'conn' in locals():
            try:
                conn.close()
            except:
                pass
        return jsonify({'error': 'Failed to update equipment'}), 500

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
        # Using unified database - ArrowDatabase
        db = get_database()
        if not db:
            return jsonify({"error": "Database not available"}), 500
        conn = db.get_connection()
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
        # Using unified database - ArrowDatabase
        db = get_database()
        if not db:
            return jsonify({"error": "Database not available"}), 500
        conn = db.get_connection()
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
        # Using unified database - ArrowDatabase
        db = get_database()
        if not db:
            return jsonify({"error": "Database not available"}), 500
        conn = db.get_connection()
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
        # Using unified database - ArrowDatabase
        db = get_database()
        if not db:
            return jsonify({"error": "Database not available"}), 500
        conn = db.get_connection()
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
        # Using unified database - ArrowDatabase
        db = get_database()
        if not db:
            return jsonify({"error": "Database not available"}), 500
        conn = db.get_connection()
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
        # Using unified database - ArrowDatabase
        db = get_database()
        if not db:
            return jsonify({"error": "Database not available"}), 500
        conn = db.get_connection()
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

@app.route('/api/calculate-trajectory', methods=['POST'])
@token_required
def calculate_trajectory(current_user):
    """Calculate arrow trajectory for visualization"""
    from ballistics_calculator import BallisticsCalculator, EnvironmentalConditions, ShootingConditions, ArrowType
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        arrow_data = data.get('arrow_data', {})
        bow_config = data.get('bow_config', {})
        env_conditions = data.get('environmental_conditions', {})
        shooting_conditions = data.get('shooting_conditions', {})

        # Extract arrow parameters with flexible field name matching
        # Try multiple possible field names for arrow speed
        arrow_speed = (
            arrow_data.get('estimated_speed_fps') or 
            arrow_data.get('arrow_speed_fps') or 
            arrow_data.get('speed_fps') or 
            (arrow_data.get('performance', {}).get('performance_summary', {}).get('estimated_speed_fps')) or
            280  # Default fallback
        )
        
        # Try multiple possible field names for arrow weight  
        arrow_weight = (
            arrow_data.get('total_weight') or
            arrow_data.get('total_arrow_weight_grains') or
            arrow_data.get('weight_grains') or
            (arrow_data.get('performance', {}).get('performance_summary', {}).get('total_arrow_weight_grains')) or
            400  # Default fallback
        )
        
        # Try multiple possible field names for arrow diameter
        arrow_diameter = (
            arrow_data.get('outer_diameter') or
            arrow_data.get('diameter_inches') or
            arrow_data.get('diameter') or
            0.246  # Default fallback
        )
        
        # Debug: Log the extracted parameters with comprehensive data structure
        print(f"🎯 Trajectory Calculation Debug:")
        print(f"   Arrow Speed: {arrow_speed} fps")
        print(f"   Arrow Weight: {arrow_weight} grains") 
        print(f"   Arrow Diameter: {arrow_diameter} inches")
        print(f"   Raw arrow_data keys: {list(arrow_data.keys())}")
        print(f"   Raw arrow_data: {arrow_data}")
        if arrow_data.get('performance'):
            print(f"   Performance data keys: {list(arrow_data.get('performance', {}).keys())}")
            print(f"   Full performance data: {arrow_data.get('performance')}")
            if arrow_data.get('performance', {}).get('performance_summary'):
                print(f"   Performance summary keys: {list(arrow_data.get('performance', {}).get('performance_summary', {}).keys())}")
                print(f"   Full performance summary: {arrow_data.get('performance', {}).get('performance_summary')}")
        
        # Determine arrow type based on arrow data
        arrow_type_str = arrow_data.get('arrow_type', 'hunting').lower()
        if 'target' in arrow_type_str:
            arrow_type = ArrowType.TARGET
        elif 'field' in arrow_type_str:
            arrow_type = ArrowType.FIELD
        elif '3d' in arrow_type_str:
            arrow_type = ArrowType.THREE_D
        else:
            arrow_type = ArrowType.HUNTING

        # Create environmental conditions
        environmental = EnvironmentalConditions(
            temperature_f=env_conditions.get('temperature_f', 70.0),
            humidity_percent=env_conditions.get('humidity_percent', 50.0),
            altitude_feet=env_conditions.get('altitude_feet', 0.0),
            wind_speed_mph=env_conditions.get('wind_speed_mph', 0.0),
            wind_direction_degrees=env_conditions.get('wind_direction_degrees', 0.0),
            air_pressure_inHg=env_conditions.get('air_pressure_inHg', 29.92)
        )

        # Create shooting conditions
        shooting = ShootingConditions(
            shot_angle_degrees=shooting_conditions.get('shot_angle_degrees', 0.0),
            sight_height_inches=shooting_conditions.get('sight_height_inches', 7.0),
            zero_distance_yards=shooting_conditions.get('zero_distance_yards', 20.0),
            max_range_yards=shooting_conditions.get('max_range_yards', 100.0)
        )

        # Calculate trajectory
        calculator = BallisticsCalculator()
        result = calculator.calculate_trajectory(
            arrow_speed_fps=arrow_speed,
            arrow_weight_grains=arrow_weight,
            arrow_diameter_inches=arrow_diameter,
            arrow_type=arrow_type,
            environmental=environmental,
            shooting=shooting
        )

        return jsonify({
            'success': True,
            'trajectory_data': result,
            'calculation_parameters': {
                'arrow_speed_fps': arrow_speed,
                'arrow_weight_grains': arrow_weight,
                'arrow_diameter_inches': arrow_diameter,
                'arrow_type': arrow_type.value,
                'environmental_conditions': {
                    'temperature_f': environmental.temperature_f,
                    'wind_speed_mph': environmental.wind_speed_mph,
                    'altitude_feet': environmental.altitude_feet
                }
            }
        })

    except Exception as e:
        import traceback
        error_details = {
            'error_message': str(e),
            'error_type': type(e).__name__,
            'traceback': traceback.format_exc()
        }
        print(f"🚨 TRAJECTORY CALCULATION ERROR:")
        print(f"   Error Type: {type(e).__name__}")
        print(f"   Error Message: {str(e)}")
        print(f"   Full Traceback: {traceback.format_exc()}")
        print(f"   Arrow Data: {arrow_data}")
        print(f"   Bow Config: {bow_config}")
        
        return jsonify({
            'success': False,
            'error': str(e),
            'error_details': error_details,
            'fallback_data': {
                'trajectory_points': generate_fallback_trajectory(
                    arrow_data.get('estimated_speed_fps', 280),
                    shooting_conditions.get('max_range_yards', 100)
                )
            }
        }), 500

def generate_fallback_trajectory(arrow_speed_fps, max_range_yards):
    """Generate basic trajectory for fallback when ballistics calculation fails"""
    trajectory_points = []
    
    for distance in range(0, int(max_range_yards) + 1, 5):
        if distance == 0:
            height = 7.0  # Sight height
        else:
            # Basic ballistic trajectory calculation
            time_of_flight = (distance * 3) / arrow_speed_fps  # Convert yards to feet, calculate time
            drop_feet = 16.1 * time_of_flight * time_of_flight  # Gravity drop in feet
            height = 7.0 - (drop_feet * 12)  # Convert to inches, adjust for sight height
        
        trajectory_points.append({
            'time': round(time_of_flight if distance > 0 else 0, 3),
            'distance_yards': distance,
            'height_inches': round(height, 2),
            'velocity_fps': round(arrow_speed_fps * (0.95 ** (distance / 10)), 1),  # Simple velocity decay
            'drop_inches': round(7.0 - height, 2) if height < 7.0 else 0,
            'wind_drift_inches': 0
        })
    
    return trajectory_points

@app.route('/api/guide-sessions/<int:session_id>', methods=['GET'])
@token_required
def get_guide_session_details(current_user, session_id):
    """Get detailed information about a guide session"""
    conn = None
    try:
        # Get user database connection
        # Using unified database - ArrowDatabase
        db = get_database()
        if not db:
            return jsonify({"error": "Database not available"}), 500
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Get session info
        cursor.execute('''
            SELECT gs.*, bs.name as bow_name, bs.bow_type, bs.draw_weight
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

# ======================================
# ENHANCED INTERACTIVE TUNING SYSTEM
# ======================================

@app.route('/api/tuning-guides/start', methods=['POST'])
@token_required
def start_enhanced_tuning_session(current_user):
    """Start enhanced tuning session with bow/arrow selection"""
    conn = None
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        bow_setup_id = data.get('bow_setup_id')
        arrow_id = data.get('arrow_id')
        arrow_length = data.get('arrow_length')
        point_weight = data.get('point_weight')
        guide_type = data.get('guide_type', 'paper_tuning')
        
        # Validate required fields
        if not all([bow_setup_id, arrow_id, arrow_length, point_weight]):
            return jsonify({'error': 'bow_setup_id, arrow_id, arrow_length, and point_weight are required'}), 400
            
        if guide_type not in ['paper_tuning', 'bareshaft_tuning', 'walkback_tuning']:
            return jsonify({'error': 'Invalid guide_type. Must be paper_tuning, bareshaft_tuning, or walkback_tuning'}), 400
        
        # Get database connection
        db = get_database()
        if not db:
            return jsonify({"error": "Database not available"}), 500
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Verify bow setup belongs to user
        cursor.execute('SELECT name, bow_type FROM bow_setups WHERE id = ? AND user_id = ?', 
                     (bow_setup_id, current_user['id']))
        bow_setup = cursor.fetchone()
        if not bow_setup:
            return jsonify({'error': 'Bow setup not found or access denied'}), 404
        
        # Get arrow information
        cursor.execute('SELECT manufacturer, model_name FROM arrows WHERE id = ?', (arrow_id,))
        arrow = cursor.fetchone()
        if not arrow:
            return jsonify({'error': 'Arrow not found'}), 404
        
        # Create enhanced guide session with arrow tracking
        guide_name_map = {
            'paper_tuning': 'Enhanced Paper Tuning',
            'bareshaft_tuning': 'Enhanced Bareshaft Tuning', 
            'walkback_tuning': 'Enhanced Walkback Tuning'
        }
        
        cursor.execute('''
            INSERT INTO guide_sessions (
                user_id, bow_setup_id, guide_name, guide_type, 
                arrow_id, arrow_length, point_weight, total_steps, test_results_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            current_user['id'], bow_setup_id, guide_name_map[guide_type], 
            guide_type, arrow_id, arrow_length, point_weight, 5, 0
        ))
        
        session_id = cursor.lastrowid
        conn.commit()
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'guide_type': guide_type,
            'bow_setup': {'name': bow_setup[0], 'bow_type': bow_setup[1]},
            'arrow': {'manufacturer': arrow[0], 'model_name': arrow[1]},
            'arrow_length': arrow_length,
            'point_weight': point_weight,
            'message': f'Enhanced {guide_name_map[guide_type]} session started'
        })
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/tuning-guides/<session_id>/record-test', methods=['POST'])
@token_required
def record_enhanced_tuning_test(current_user, session_id):
    """Record test result with intelligent recommendations"""
    conn = None
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        test_data = data.get('test_data', {})
        environmental_conditions = data.get('environmental_conditions', {})
        shooting_distance = data.get('shooting_distance')
        notes = data.get('notes', '')
        
        if not test_data:
            return jsonify({'error': 'test_data is required'}), 400
        
        # Get database connection
        db = get_database()
        if not db:
            return jsonify({"error": "Database not available"}), 500
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Get session information
        cursor.execute('''
            SELECT gs.*, bs.bow_type 
            FROM guide_sessions gs
            LEFT JOIN bow_setups bs ON gs.bow_setup_id = bs.id
            WHERE gs.id = ? AND gs.user_id = ?
        ''', (session_id, current_user['id']))
        
        session = cursor.fetchone()
        if not session:
            return jsonify({'error': 'Guide session not found or access denied'}), 404
        
        # Extract session details using correct indices based on schema
        # guide_sessions has 19 columns (0-18), bow_type from JOIN is at index 19
        bow_type = session[19] if len(session) > 19 else 'compound'  # bow_type from JOIN
        guide_type = session[4]   # guide_type column
        arrow_id = session[15]    # arrow_id column (corrected)
        bow_setup_id = session[2] # bow_setup_id column
        arrow_length = session[16] # arrow_length column (corrected)
        point_weight = session[17] # point_weight column (corrected)
        
        # Create rule engine for recommendations
        rule_engine = create_tuning_rule_engine(bow_type, 'RH')  # Default to RH for now
        
        # Generate recommendations using rule engine
        try:
            analysis_result = rule_engine.analyze_test_result(guide_type, test_data)
        except Exception as e:
            return jsonify({'error': f'Analysis failed: {str(e)}'}), 400
        
        # Calculate test number for this arrow
        test_number = calculate_test_number(
            current_user['id'], arrow_id, bow_setup_id, 
            arrow_length, point_weight, guide_type, conn
        )
        
        # Store test result permanently
        cursor.execute('''
            INSERT INTO tuning_test_results (
                guide_session_id, user_id, bow_setup_id, arrow_id, 
                arrow_length, point_weight, test_type, test_data, 
                recommendations, environmental_conditions, shooting_distance,
                confidence_score, test_number, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id, current_user['id'], bow_setup_id, arrow_id,
            arrow_length, point_weight, guide_type, json.dumps(test_data),
            json.dumps(analysis_result['recommendations']), 
            json.dumps(environmental_conditions), shooting_distance,
            analysis_result['confidence_score'], test_number, notes
        ))
        
        test_result_id = cursor.lastrowid
        
        # Update session test count
        cursor.execute('''
            UPDATE guide_sessions 
            SET test_results_count = test_results_count + 1,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (session_id,))
        
        # Create enhanced change log entry for tuning test
        change_log_service = ChangeLogService()
        change_log_service.log_tuning_test(
            test_result_id=test_result_id,
            user_id=current_user['id'],
            test_type=guide_type,
            arrow_id=arrow_id,
            bow_setup_id=bow_setup_id,
            test_number=test_number,
            confidence_score=analysis_result['confidence_score'],
            recommendations_count=len(analysis_result['recommendations']),
            conn=conn  # Reuse existing connection to prevent database lock
        )
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'test_result_id': test_result_id,
            'test_number': test_number,
            'recommendations': analysis_result['recommendations'],
            'confidence_score': analysis_result['confidence_score'],
            'analysis': analysis_result['analysis'],
            'message': f'Test #{test_number} recorded successfully'
        })
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/arrows/<int:arrow_id>/tuning-history', methods=['GET'])
@token_required 
def get_arrow_tuning_history(current_user, arrow_id):
    """Get complete tuning history for a specific arrow"""
    conn = None
    try:
        # Get database connection
        db = get_database()
        if not db:
            return jsonify({"error": "Database not available"}), 500
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Get query parameters
        bow_setup_id = request.args.get('bow_setup_id', type=int)
        test_type = request.args.get('test_type')
        limit = request.args.get('limit', 50, type=int)
        
        # Build query for test results
        query = '''
            SELECT ttr.*, bs.name as bow_name, bs.bow_type, a.manufacturer, a.model_name,
                   COUNT(*) OVER (PARTITION BY ttr.arrow_id, ttr.test_type) as total_tests_of_type
            FROM tuning_test_results ttr
            LEFT JOIN bow_setups bs ON ttr.bow_setup_id = bs.id
            LEFT JOIN arrows a ON ttr.arrow_id = a.id
            WHERE ttr.user_id = ? AND ttr.arrow_id = ?
        '''
        
        params = [current_user['id'], arrow_id]
        
        if bow_setup_id:
            query += ' AND ttr.bow_setup_id = ?'
            params.append(bow_setup_id)
        
        if test_type:
            query += ' AND ttr.test_type = ?'
            params.append(test_type)
        
        query += ' ORDER BY ttr.created_at DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        test_results = []
        
        for row in cursor.fetchall():
            result = dict(row)
            # Parse JSON fields
            result['test_data'] = json.loads(result['test_data']) if result['test_data'] else {}
            result['recommendations'] = json.loads(result['recommendations']) if result['recommendations'] else []
            result['environmental_conditions'] = json.loads(result['environmental_conditions']) if result['environmental_conditions'] else {}
            test_results.append(result)
        
        # Get aggregate history data
        cursor.execute('''
            SELECT * FROM arrow_tuning_history 
            WHERE user_id = ? AND arrow_id = ?
        ''' + (' AND bow_setup_id = ?' if bow_setup_id else ''), 
        params[:2] + ([bow_setup_id] if bow_setup_id else []))
        
        history_summary = cursor.fetchone()
        if history_summary:
            history_summary = dict(history_summary)
            history_summary['current_recommendations'] = json.loads(history_summary['current_recommendations']) if history_summary['current_recommendations'] else []
            history_summary['success_indicators'] = json.loads(history_summary['success_indicators']) if history_summary['success_indicators'] else {}
        
        return jsonify({
            'test_results': test_results,
            'history_summary': history_summary,
            'total_results': len(test_results),
            'filters': {
                'bow_setup_id': bow_setup_id,
                'test_type': test_type,
                'limit': limit
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/arrows/<int:arrow_id>/tuning-summary', methods=['GET'])
@token_required
def get_arrow_tuning_summary(current_user, arrow_id):
    """Get tuning progress summary for an arrow"""
    conn = None
    try:
        # Get database connection
        db = get_database()
        if not db:
            return jsonify({"error": "Database not available"}), 500
        conn = db.get_connection()
        cursor = conn.cursor()
        
        bow_setup_id = request.args.get('bow_setup_id', type=int)
        
        # Get arrow information
        cursor.execute('SELECT manufacturer, model_name FROM arrows WHERE id = ?', (arrow_id,))
        arrow = cursor.fetchone()
        if not arrow:
            return jsonify({'error': 'Arrow not found'}), 404
        
        # Get summary statistics
        base_query = '''
            SELECT 
                COUNT(*) as total_tests,
                COUNT(DISTINCT test_type) as test_types_performed,
                MAX(created_at) as last_test_date,
                MIN(created_at) as first_test_date,
                AVG(confidence_score) as avg_confidence,
                test_type,
                COUNT(*) as count_by_type
            FROM tuning_test_results 
            WHERE user_id = ? AND arrow_id = ?
        '''
        
        params = [current_user['id'], arrow_id]
        if bow_setup_id:
            base_query += ' AND bow_setup_id = ?'
            params.append(bow_setup_id)
        
        # Get overall stats
        cursor.execute(base_query + ' GROUP BY test_type', params)
        test_type_stats = [dict(row) for row in cursor.fetchall()]
        
        # Get recent improvements
        cursor.execute('''
            SELECT test_type, confidence_score, created_at, test_number
            FROM tuning_test_results 
            WHERE user_id = ? AND arrow_id = ?
        ''' + (' AND bow_setup_id = ?' if bow_setup_id else '') + '''
            ORDER BY created_at DESC 
            LIMIT 10
        ''', params)
        
        recent_tests = [dict(row) for row in cursor.fetchall()]
        
        # Calculate improvement trend (if enough data)
        improvement_trend = 'stable'
        if len(recent_tests) >= 3:
            scores = [test['confidence_score'] for test in reversed(recent_tests)]
            if len(scores) >= 3:
                recent_avg = sum(scores[-3:]) / 3
                earlier_avg = sum(scores[:3]) / 3
                if recent_avg > earlier_avg + 5:
                    improvement_trend = 'improving'
                elif recent_avg < earlier_avg - 5:
                    improvement_trend = 'declining'
        
        return jsonify({
            'arrow': {'id': arrow_id, 'manufacturer': arrow[0], 'model_name': arrow[1]},
            'test_type_statistics': test_type_stats,
            'recent_tests': recent_tests,
            'improvement_trend': improvement_trend,
            'summary': {
                'total_tests': sum(stat['count_by_type'] for stat in test_type_stats),
                'test_types_performed': len(test_type_stats),
                'average_confidence': sum(stat['avg_confidence'] * stat['count_by_type'] for stat in test_type_stats) / sum(stat['count_by_type'] for stat in test_type_stats) if test_type_stats else 0,
                'days_active': (datetime.now() - datetime.fromisoformat(recent_tests[-1]['created_at'])).days if recent_tests else 0
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

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
        # Using unified database - ArrowDatabase
        db = get_database()
        if not db:
            return jsonify({"error": "Database not available"}), 500
        conn = db.get_connection()
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
        # Using unified database - ArrowDatabase
        db = get_database()
        if not db:
            return jsonify({"error": "Database not available"}), 500
        conn = db.get_connection()
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

@app.route('/api/tuning-change-log', methods=['GET'])
@token_required
def get_tuning_change_log(current_user):
    """Get comprehensive tuning test history from change log system"""
    try:
        # Get query parameters
        arrow_id = request.args.get('arrow_id')
        bow_setup_id = request.args.get('bow_setup_id')
        test_type = request.args.get('test_type')
        limit = int(request.args.get('limit', 50))
        days_back = request.args.get('days_back')
        
        if days_back:
            days_back = int(days_back)
        
        # Use the enhanced change log service
        change_log_service = ChangeLogService()
        test_history = change_log_service.get_tuning_history(
            arrow_id=arrow_id,
            bow_setup_id=bow_setup_id,
            user_id=current_user['id'],
            test_type=test_type,
            limit=limit,
            days_back=days_back
        )
        
        return jsonify({
            'test_history': test_history,
            'count': len(test_history)
        })
        
    except Exception as e:
        print(f"❌ Error getting tuning change log: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/equipment-adjustments', methods=['GET'])
@token_required
def get_equipment_adjustments(current_user):
    """Get equipment adjustment history from change log system"""
    try:
        # Get query parameters
        bow_setup_id = request.args.get('bow_setup_id')
        component = request.args.get('component')
        limit = int(request.args.get('limit', 50))
        
        # Use the enhanced change log service
        change_log_service = ChangeLogService()
        adjustment_history = change_log_service.get_adjustment_history(
            bow_setup_id=bow_setup_id,
            user_id=current_user['id'],
            component=component,
            limit=limit
        )
        
        return jsonify({
            'adjustments': adjustment_history,
            'count': len(adjustment_history)
        })
        
    except Exception as e:
        print(f"❌ Error getting equipment adjustments: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/tuning-adjustment', methods=['POST'])
@token_required
def record_tuning_adjustment_enhanced(current_user):
    """Record a tuning adjustment using the enhanced change log system"""
    try:
        data = request.get_json()
        
        required_fields = ['bow_setup_id', 'component', 'adjustment_type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Verify bow setup belongs to user
        db = get_database()
        if not db:
            return jsonify({"error": "Database not available"}), 500
        
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM bow_setups WHERE id = ? AND user_id = ?', 
                      (data['bow_setup_id'], current_user['id']))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Bow setup not found or access denied'}), 404
        
        conn.close()
        
        # Use the enhanced change log service
        change_log_service = ChangeLogService()
        adjustment_id = change_log_service.log_tuning_adjustment(
            user_id=current_user['id'],
            bow_setup_id=data['bow_setup_id'],
            component=data['component'],
            adjustment_type=data['adjustment_type'],
            old_value=data.get('old_value'),
            new_value=data.get('new_value'),
            reason=data.get('reason'),
            test_result_id=data.get('test_result_id')
        )
        
        return jsonify({
            'message': 'Tuning adjustment recorded successfully',
            'adjustment_id': adjustment_id
        })
        
    except Exception as e:
        print(f"❌ Error recording tuning adjustment: {e}")
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
        
        # Validate file size (50MB max)
        max_size = 50 * 1024 * 1024  # 50MB
        file.seek(0, 2)  # Seek to end
        size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if size > max_size:
            return jsonify({'error': 'File too large. Maximum size: 50MB'}), 400
        
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
                # Using consolidated database
                from arrow_database import ArrowDatabase
                db = ArrowDatabase()
                success = db.update_user(
                    current_user['id'], 
                    profile_picture_url=result['cdn_url']
                )
                if success:
                    updated_user = db.get_user_by_id(current_user['id'])
                
                if not updated_user:
                    print(f"Warning: Failed to update user profile picture URL in database")
            
            # Enhanced response for modular system compatibility
            response_data = {
                'success': True,
                'data': {
                    'cdn_url': result['cdn_url'],
                    'image_id': f"{upload_path}_{current_user['id']}_{uuid.uuid4().hex[:8]}",
                    'original_url': result.get('original_url', result['cdn_url']),
                    'cdn_type': result['cdn_type'],
                    'upload_path': upload_path,
                    'file_size': result.get('bytes', size),
                    'uploaded_at': datetime.utcnow().isoformat(),
                    'metadata': {
                        'original_filename': file.filename,
                        'file_extension': file_extension,
                        'context': request.form.get('context', upload_path),
                        'entity_id': request.form.get('entityId')
                    }
                },
                'message': f'Image uploaded successfully to {cdn_type.upper()} CDN'
            }
            
            # Log successful upload
            print(f"✅ Image upload successful: {result['cdn_url']} (size: {size} bytes, type: {cdn_type})")
            
            return jsonify(response_data)
                
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
    """Create unified database backup and upload to CDN"""
    try:
        from backup_manager import BackupManager
        from cdn_uploader import CDNUploader
        import tempfile
        import uuid
        from datetime import datetime
        
        data = request.get_json() or {}
        backup_name = data.get('backup_name')
        
        # With unified database, we always backup the single database
        include_arrow_db = True
        include_user_db = False  # Not applicable with unified architecture
        
        # Create backup manager
        backup_manager = BackupManager()
        
        # Generate backup name if not provided
        if not backup_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"admin_backup_unified_{timestamp}"
        
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
            backup_type = 'full'  # Always full backup with unified database
            
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
        
        # Make CDN upload optional - backup can succeed without CDN
        if not result or not result.get('success'):
            print("⚠️  CDN upload failed, but backup file created successfully locally")
            result = {
                'success': True,
                'url': None,
                'cdn_url': None,
                'cdn_type': 'local',
                'filename': backup_name,
                'local_only': True
            }
        
        # Get backup file size
        backup_size = os.path.getsize(local_backup_path) / (1024 * 1024)  # MB
        
        # Store backup metadata in user database
        # Using unified database - ArrowDatabase
        db = get_database()
        if not db:
            return jsonify({"error": "Database not available"}), 500
        conn = db.get_connection()
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
                'unified_database': True
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
    # Using unified database - ArrowDatabase
    db = get_database()
    if not db:
        return jsonify({"error": "Database not available"}), 500
    conn = db.get_connection()
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
    """Restore unified database from CDN backup"""
    try:
        from backup_manager import BackupManager
        import tempfile
        import requests
        
        data = request.get_json() or {}
        force = data.get('force', False)
        
        # With unified database, always restore the single database
        restore_arrow_db = True
        restore_user_db = False  # Not applicable with unified architecture
        
        # Get backup metadata from database
        # Using unified database - ArrowDatabase
        db = get_database()
        if not db:
            return jsonify({"error": "Database not available"}), 500
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM backup_metadata WHERE id = ?', (backup_id,))
        backup_record = cursor.fetchone()
        conn.close()
        
        if not backup_record:
            return jsonify({'error': 'Backup not found'}), 404
        
        backup_record = dict(backup_record)
        
        # With unified database, all backups contain the unified database
        # No need to check separate database flags
        
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
        # Using unified database - ArrowDatabase
        db = get_database()
        if not db:
            return jsonify({"error": "Database not available"}), 500
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO backup_restore_log 
            (backup_id, restored_by, restore_arrow_db, restore_user_db)
            VALUES (?, ?, ?, ?)
        ''', (backup_id, current_user['id'], True, False))  # Always unified database restore
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Successfully restored from backup "{backup_record["backup_name"]}"',
            'backup_name': backup_record['backup_name'],
            'restored': {
                'unified_database': True
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
        # Using unified database - ArrowDatabase
        db = get_database()
        if not db:
            return jsonify({"error": "Database not available"}), 500
        conn = db.get_connection()
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
                'message': 'Unified backup restored successfully',
                'restored_databases': {
                    'unified_db': True
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
        # Using unified database - ArrowDatabase
        db = get_database()
        if not db:
            return jsonify({"error": "Database not available"}), 500
        conn = db.get_connection()
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
    """Upload and restore from unified backup file"""
    try:
        from backup_manager import BackupManager
        # Using unified database - ArrowDatabase
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
        
        # With unified database, always restore the single database
        restore_arrow_db = True
        restore_user_db = False  # Not applicable with unified architecture
        force_restore = request.form.get('force_restore', 'false').lower() == 'true'
        
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
        print(f"🔄 Restoring from uploaded unified backup...")
        print(f"   Unified DB: Yes")
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
            # Using unified database - ArrowDatabase
            db = get_database()
            if not db:
                return jsonify({"error": "Database not available"}), 500
            conn = db.get_connection()
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
                    'restore_unified_db': True,
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
                'unified_database': True
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
        # Using unified database - ArrowDatabase
        
        # Get database information
        arrow_db = ArrowDatabase()
        arrow_db_path = str(arrow_db.db_path)
        
        # Since we're using unified database, user data is in the same database
        user_db_path = arrow_db_path
        
        # Get unified database statistics (all data in one database now)
        conn = arrow_db.get_connection()
        cursor = conn.cursor()
        
        # Count arrows and manufacturers (only from active manufacturers for public stats)
        cursor.execute("""
            SELECT COUNT(*) FROM arrows a
            JOIN manufacturers m ON a.manufacturer = m.name
            WHERE m.is_active = TRUE
        """)
        arrow_count = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(DISTINCT a.manufacturer) FROM arrows a
            JOIN manufacturers m ON a.manufacturer = m.name
            WHERE m.is_active = TRUE
        """)
        manufacturer_count = cursor.fetchone()[0]
        
        # Count spine specifications
        cursor.execute("SELECT COUNT(*) FROM spine_specifications")
        spine_spec_count = cursor.fetchone()[0]
        
        # Count user data (now in unified database)
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM bow_setups")
        bow_setup_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM setup_arrows")
        setup_arrow_count = cursor.fetchone()[0]
        
        # Get unified database file size
        import os
        arrow_db_size = os.path.getsize(arrow_db_path) if os.path.exists(arrow_db_path) else 0
        user_db_size = arrow_db_size  # Same database now
        
        conn.close()
        
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

@app.route('/api/calculator/system-default', methods=['GET'])
def get_system_default_chart():
    """Get system default spine chart for calculator, with optional material preference"""
    try:
        bow_type = request.args.get('bow_type', 'compound')
        material_preference = request.args.get('material', None)  # Optional material filter
        
        db = get_database()
        if not db:
            return jsonify({'error': 'Database not available'}), 500
        
        conn = db.get_connection()
        cursor = conn.cursor()
        print(f"🔍 Debug: Database path: {db.db_path if hasattr(db, 'db_path') else 'Unknown'}")
        print(f"🔍 Debug: Request for bow_type='{bow_type}', material='{material_preference}'")
        
        # Enhanced query that considers material preference
        if material_preference:
            # Try to find material-specific system default first
            material_conditions = {
                'carbon': "AND (manufacturer LIKE '%Carbon%' OR model LIKE '%Carbon%' OR manufacturer = 'Generic')",
                'wood': "AND (manufacturer LIKE '%Wood%' OR manufacturer IN ('Port Orford Cedar', 'Douglas Fir', 'Pine', 'Birch'))",
                'aluminum': "AND (manufacturer LIKE '%Aluminum%' OR model LIKE '%Aluminum%' OR model LIKE '%XX7%')",
                'carbon-aluminum': "AND (model LIKE '%FMJ%' OR model LIKE '%A/C%')"
            }
            
            material_condition = material_conditions.get(material_preference.lower(), "")
            
            query = f"""
                SELECT id, manufacturer, model, bow_type, spine_system, chart_notes
                FROM manufacturer_spine_charts_enhanced 
                WHERE bow_type = ? AND is_active = 1 AND is_system_default = 1 {material_condition}
                ORDER BY calculation_priority ASC
                LIMIT 1
            """
        else:
            # Original query for system default only
            query = """
                SELECT id, manufacturer, model, bow_type, spine_system, chart_notes
                FROM manufacturer_spine_charts_enhanced 
                WHERE bow_type = ? AND is_active = 1 AND is_system_default = 1
                ORDER BY calculation_priority ASC
                LIMIT 1
            """
        
        print(f"🔍 Debug: Executing query for bow_type '{bow_type}': {query}")
        cursor.execute(query, (bow_type,))
        result = cursor.fetchone()
        print(f"🔍 Debug: Query result: {result}")
        
        # If no manufacturer chart, check custom charts
        if not result:
            cursor.execute("""
                SELECT id, manufacturer, model, bow_type, spine_system, chart_notes
                FROM custom_spine_charts 
                WHERE bow_type = ? AND is_active = 1 AND is_system_default = 1
                ORDER BY calculation_priority ASC
                LIMIT 1
            """, (bow_type,))
            result = cursor.fetchone()
        
        conn.close()
        
        if result:
            return jsonify({
                'default_chart': {
                    'id': result[0],
                    'manufacturer': result[1],
                    'model': result[2],
                    'bow_type': result[3],
                    'spine_system': result[4],
                    'chart_notes': result[5]
                },
                'bow_type': bow_type,
                'material_preference': material_preference
            })
        else:
            return jsonify({
                'default_chart': None,
                'bow_type': bow_type,
                'material_preference': material_preference,
                'message': f'No system default chart configured for {bow_type} bows' + (f' with {material_preference} material' if material_preference else '')
            })
            
    except Exception as e:
        print(f"Error getting system default chart: {e}")
        return jsonify({'error': 'Failed to get system default chart'}), 500

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
                   grid_definition, spine_grid, is_system_default, calculation_priority
            FROM manufacturer_spine_charts_enhanced
            ORDER BY is_system_default DESC, calculation_priority ASC, manufacturer, model, bow_type
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
                'spine_grid': json.loads(row[11]) if row[11] else [],
                'is_system_default': bool(row[12]) if len(row) > 12 else False,
                'calculation_priority': row[13] if len(row) > 13 else 100
            })
        
        # Get custom charts
        cursor.execute("""
            SELECT 'custom' as chart_type, id, manufacturer, model, bow_type, 
                   spine_system, chart_notes, created_by, is_active, created_at,
                   grid_definition, spine_grid, is_system_default, calculation_priority
            FROM custom_spine_charts
            ORDER BY is_system_default DESC, calculation_priority ASC, chart_name
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
                'spine_grid': json.loads(row[11]) if row[11] else [],
                'is_system_default': bool(row[12]) if len(row) > 12 else False,
                'calculation_priority': row[13] if len(row) > 13 else 100
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

@app.route('/api/admin/spine-charts/system-settings', methods=['GET'])
@token_required
@admin_required
def get_spine_system_settings(current_user):
    """Get spine calculation system settings"""
    try:
        spine_service = get_spine_service()
        if not spine_service:
            return jsonify({'error': 'Spine service not available'}), 500
        
        settings = spine_service.get_system_settings()
        return jsonify({'settings': settings})
    except Exception as e:
        print(f"Error getting spine system settings: {e}")
        return jsonify({'error': 'Failed to get system settings'}), 500

@app.route('/api/admin/spine-charts/system-settings/<setting_name>', methods=['PUT'])
@token_required
@admin_required
def update_spine_system_setting(current_user, setting_name):
    """Update a spine calculation system setting"""
    try:
        data = request.get_json()
        setting_value = data.get('value')
        
        if setting_value is None:
            return jsonify({'error': 'Setting value is required'}), 400
        
        spine_service = get_spine_service()
        if not spine_service:
            return jsonify({'error': 'Spine service not available'}), 500
        
        success = spine_service.update_system_setting(setting_name, str(setting_value), current_user['id'])
        
        if success:
            return jsonify({'message': 'System setting updated successfully'})
        else:
            return jsonify({'error': 'Setting not found or update failed'}), 404
            
    except Exception as e:
        print(f"Error updating spine system setting: {e}")
        return jsonify({'error': 'Failed to update system setting'}), 500

@app.route('/api/admin/spine-charts/<chart_type>/<int:chart_id>/set-default', methods=['POST'])
@token_required
@admin_required
def set_system_default_chart(current_user, chart_type, chart_id):
    """Set a spine chart as the system default"""
    try:
        if chart_type not in ['manufacturer', 'custom']:
            return jsonify({'error': 'Invalid chart type. Must be manufacturer or custom'}), 400
        
        spine_service = get_spine_service()
        if not spine_service:
            return jsonify({'error': 'Spine service not available'}), 500
        
        success = spine_service.set_system_default_chart(chart_id, chart_type)
        
        if success:
            return jsonify({'message': f'Chart {chart_id} set as system default'})
        else:
            return jsonify({'error': 'Chart not found or update failed'}), 404
            
    except Exception as e:
        print(f"Error setting system default chart: {e}")
        return jsonify({'error': 'Failed to set system default chart'}), 500

@app.route('/api/admin/spine-charts/<chart_type>/<int:chart_id>/duplicate', methods=['POST'])
@token_required
@admin_required
def duplicate_spine_chart(current_user, chart_type, chart_id):
    """Duplicate a spine chart for testing and modification"""
    try:
        data = request.get_json()
        new_name = data.get('name')
        
        if not new_name:
            return jsonify({'error': 'New chart name is required'}), 400
        
        if chart_type not in ['manufacturer', 'custom']:
            return jsonify({'error': 'Invalid chart type. Must be manufacturer or custom'}), 400
        
        spine_service = get_spine_service()
        if not spine_service:
            return jsonify({'error': 'Spine service not available'}), 500
        
        new_chart_id = spine_service.duplicate_spine_chart(
            chart_id, new_name, chart_type, current_user['id']
        )
        
        if new_chart_id:
            return jsonify({
                'message': 'Chart duplicated successfully',
                'new_chart_id': new_chart_id,
                'new_chart_name': new_name
            }), 201
        else:
            return jsonify({'error': 'Chart not found or duplication failed'}), 404
            
    except Exception as e:
        print(f"Error duplicating spine chart: {e}")
        return jsonify({'error': 'Failed to duplicate chart'}), 500

# Database Migration Management API Endpoints

@app.route('/api/admin/migrations/status', methods=['GET'])
@token_required
@admin_required
def get_migration_status(current_user):
    """Get comprehensive migration status for both arrow and user databases"""
    try:
        from database_migration_manager import DatabaseMigrationManager
        import json
        
        # Migration target mapping based on unified database architecture
        # Note: With unified architecture, all migrations target the same database
        migration_targets = {
            # Legacy mapping for reference (all are now in unified database)
            '001': 'user',    # Initial user database schema
            '002': 'user',    # User authentication tables
            '003': 'user',    # Bow setups and setup_arrows
            '004': 'user',    # Enhanced user profiles
            '005': 'user',    # Tuning sessions
            '006': 'user',    # Guide sessions
            '007': 'user',    # Equipment management
            '008': 'user',    # Equipment field standards
            '009': 'user',    # Equipment categories
            '010': 'user',    # User database enhancements
            '011': 'user',    # Database logging
            '012': 'user',    # Admin system
            '013': 'user',    # Equipment change logging
            '014': 'user',    # Enhanced equipment management
            '015': 'user',    # Manufacturer equipment categories
            '016': 'user',    # Bow equipment enhancements
            '017': 'user',    # Setup arrows duplicate constraint removal
            '018': 'user',    # Equipment ID nullable
            '019': 'user',    # Chronograph data
            '020': 'user',    # Enhanced string equipment fields
            '021': 'user',    # Performance calculation fixes
            '022': 'user',    # Performance data column
            '023': 'user',    # User database consolidation
            '024': 'user',    # Schema columns additions
            '025': 'user',    # Equipment ID nullable fixes
            '026': 'user',    # Draw length and peep sight category
            '027': 'user',    # IBO speed unified database
            '028': 'user',    # Remaining schema columns
            '029': 'user',    # Schema issues fixes
            '030': 'user',    # Draw length architecture
            '031': 'user',    # User profile columns
            '032': 'user',    # Change description column
            '033': 'arrow',   # Production schema fixes (unified database)
            '034': 'user',    # Change log service SQL
            '035': 'arrow',   # Enhanced tuning system (unified database)
            '036': 'arrow',   # Equipment ID nullable (unified database)
            '037': 'arrow',   # Chronograph integration fixes (unified database)
            
            # Arrow database migrations (arrow specs, spine data, components)
            'spine_calc': 'arrow',  # Spine calculation system
        }
        
        # Get database paths with unified architecture support
        arrow_db = get_database()
        if not arrow_db:
            return jsonify({"error": "Database not available"}), 500
        # With unified architecture, user data is in the same database
        user_db = arrow_db
        
        if not arrow_db:
            return jsonify({'error': 'Arrow database not available'}), 500
        
        # Always convert Path objects to strings
        arrow_db_path = str(arrow_db.db_path) if hasattr(arrow_db, 'db_path') else 'arrow_database.db'
        
        # Check if we have unified architecture (user_db might point to same file as arrow_db)
        user_db_path = None
        user_manager = None
        user_status = {}
        
        if user_db:
            user_db_path = str(user_db.db_path) if hasattr(user_db, 'db_path') else 'user_data.db'
            
            # Check if user database is separate from arrow database
            if user_db_path != arrow_db_path and os.path.exists(user_db_path):
                # Separate user database exists
                migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')
                user_manager = DatabaseMigrationManager(user_db_path, migrations_dir)
                try:
                    user_status = user_manager.get_migration_status() or {}
                except Exception as e:
                    print(f"Warning: Could not get user database migration status: {e}")
                    user_status = {}
            else:
                # Unified architecture - user tables are in arrow database
                user_db_path = arrow_db_path
        
        # Initialize arrow database migration manager
        migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')
        arrow_manager = DatabaseMigrationManager(arrow_db_path, migrations_dir)
        
        # Get status from arrow database (includes user tables in unified architecture)
        try:
            arrow_status = arrow_manager.get_migration_status() or {}
        except Exception as e:
            print(f"Error getting arrow database migration status: {e}")
            arrow_status = {}
        
        # Create combined status with database targeting
        combined_status = {}
        
        # Get all migration files from filesystem to know what migrations exist
        migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')
        all_migrations = set()
        
        # Scan migration files to get complete list
        if os.path.exists(migrations_dir):
            for filename in os.listdir(migrations_dir):
                if filename.endswith('.py') and not filename.startswith('__'):
                    # Extract version number from filename (e.g., "001_description.py" -> "001")
                    parts = filename.split('_', 1)
                    if len(parts) >= 1:
                        version = parts[0]
                        if version.isdigit() or version in migration_targets:
                            all_migrations.add(version)
        
        # Add any migrations found in database that might not have files
        if arrow_status:
            all_migrations.update(arrow_status.keys())
        if user_status:
            all_migrations.update(user_status.keys())
        
        # For each migration, determine if it's been applied
        for migration_version in sorted(all_migrations):
            # Determine target database
            target_db = migration_targets.get(migration_version, 'user')
            
            # Check if migration is recorded in the migrations table
            migration_recorded = False
            migration_info = {}
            
            if target_db == 'arrow':
                migration_info = arrow_status.get(migration_version, {})
                migration_recorded = migration_version in arrow_status
            else:
                migration_info = user_status.get(migration_version, {})
                migration_recorded = migration_version in user_status
            
            # For migrations not in the migrations table, we need to check if the schema changes exist
            # This handles legacy migrations applied before the migration tracking system
            if not migration_recorded:
                # Check if this migration's changes are already applied by examining database schema
                is_schema_applied = check_migration_schema_applied(arrow_db_path, migration_version)
                
                migration_info = {
                    'description': get_migration_description(migration_version),
                    'applied': is_schema_applied,
                    'applied_at': 'Legacy (before migration tracking)' if is_schema_applied else None
                }
            
            # Set database status indicators
            if target_db == 'arrow':
                status_in_arrow = migration_info.get('applied', False)
                status_in_user = None
            else:
                status_in_user = migration_info.get('applied', False) 
                status_in_arrow = None
            
            combined_status[migration_version] = {
                'description': migration_info.get('description', f'Migration {migration_version}'),
                'target_database': target_db,
                'applied': migration_info.get('applied', False),
                'applied_at': migration_info.get('applied_at'),
                'status_in_arrow_db': status_in_arrow,
                'status_in_user_db': status_in_user,
                'arrow_db_path': arrow_db_path if target_db == 'arrow' else None,
                'user_db_path': user_db_path if target_db == 'user' else None,
                'recorded_in_db': migration_recorded
            }
        
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
        clean_status = convert_paths_to_strings(combined_status)
        
        # Add summary information
        total_migrations = len(clean_status)
        applied_migrations = len([m for m in clean_status.values() if m['applied']])
        pending_migrations = total_migrations - applied_migrations
        arrow_db_migrations = len([m for m in clean_status.values() if m['target_database'] == 'arrow'])
        user_db_migrations = len([m for m in clean_status.values() if m['target_database'] == 'user'])
        
        result = {
            'migrations': clean_status,
            'summary': {
                'total_migrations': total_migrations,
                'applied_migrations': applied_migrations,
                'pending_migrations': pending_migrations,
                'arrow_db_migrations': arrow_db_migrations,
                'user_db_migrations': user_db_migrations,
                'arrow_db_path': arrow_db_path,
                'user_db_path': user_db_path
            }
        }
        
        return jsonify(result), 200
    except Exception as e:
        print(f"Error getting migration status: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Failed to get migration status'}), 500

def check_migration_schema_applied(db_path, migration_version):
    """Check if a migration's schema changes have been applied to the database"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check for key schema changes based on migration version
        schema_checks = {
            '001': "SELECT name FROM sqlite_master WHERE type='table' AND name='spine_calculations'",
            '002': "SELECT name FROM sqlite_master WHERE type='table' AND name='users'",
            '003': "SELECT name FROM sqlite_master WHERE type='table' AND name='bow_setups'",
            '004': "SELECT name FROM sqlite_master WHERE type='table' AND name='bow_equipment'",
            '005': "SELECT name FROM sqlite_master WHERE type='table' AND name='unified_manufacturers'",
            '019': "SELECT name FROM sqlite_master WHERE type='table' AND name='chronograph_data'",
            '023': "SELECT name FROM sqlite_master WHERE type='table' AND name='migrations'",
        }
        
        # For most migrations, if key tables exist, assume applied
        if migration_version in schema_checks:
            cursor.execute(schema_checks[migration_version])
            result = cursor.fetchone()
            conn.close()
            return result is not None
        
        # For migrations without specific checks, assume applied if core tables exist
        # This handles the majority of schema modifications
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        users_table = cursor.fetchone()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bow_setups'")
        setups_table = cursor.fetchone()
        
        conn.close()
        
        # If core tables exist, assume most migrations are applied
        return users_table is not None and setups_table is not None
        
    except Exception as e:
        print(f"Error checking schema for migration {migration_version}: {e}")
        return False

def get_migration_description(migration_version):
    """Get descriptive name for a migration version"""
    descriptions = {
        '001': 'Initial spine calculation tables',
        '002': 'User authentication tables', 
        '003': 'Bow setups and setup arrows',
        '004': 'Bow equipment schema',
        '005': 'Unified manufacturers',
        '006': 'Bow limb manufacturers',
        '007': 'User bow equipment table',
        '008': 'Custom equipment schema',
        '009': 'User custom equipment schema',
        '010': 'Complete equipment categories',
        '011': 'Enhanced manufacturer workflow',
        '012': 'Fix pending manufacturers schema',
        '013': 'Equipment change logging',
        '014': 'Arrow change logging',
        '015': 'Remove setup arrows unique constraint',
        '016': 'Equipment soft delete enhancement',
        '017': 'Remove setup arrows duplicate constraint',
        '018': 'Make equipment ID nullable',
        '019': 'Add chronograph data table',
        '020': 'Enhanced string equipment fields',
        '021': 'Fix performance calculation import',
        '022': 'Add performance data column',
        '023': 'Consolidate user database',
        '024': 'Add missing schema columns',
        '025': 'Fix equipment ID nullable unified',
        '026': 'Add draw length to bow setups',
        '027': 'Add IBO speed unified database',
        '028': 'Add remaining schema columns',
        '029': 'Fix remaining schema issues',
        '030': 'Fix draw length architecture',
        '031': 'Add user profile columns',
        '032': 'Add change description column',
        '033': 'Production schema fixes',
        '034': 'Fix change log service SQL',
        '035': 'Enhanced tuning system',
        '036': 'Make equipment ID nullable',
        '037': 'Chronograph integration fixes'
    }
    
    return descriptions.get(migration_version, f'Migration {migration_version}')

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

@app.route('/api/admin/validate-arrows', methods=['GET'])
@token_required
@admin_required
def validate_arrows_data(current_user):
    """Validate arrow data quality for calculator compatibility"""
    try:
        # Import the validation script with production-compatible paths
        try:
            ArrowDataValidator = import_arrow_data_validator()
        except ImportError as e:
            return jsonify({'error': f'Failed to import validation module: {str(e)}'}), 500
        
        # Get database path from current database instance
        db = get_database()
        if not db:
            return jsonify({'error': 'Database not available'}), 500
        
        db_path = db.db_path if hasattr(db, 'db_path') else 'arrow_database.db'
        
        # Run validation
        validator = ArrowDataValidator(db_path)
        report = validator.validate_all_data()
        
        # Calculate health score
        total_arrows = report.total_arrows
        critical_count = report.critical_issues
        warning_count = report.warning_issues
        
        # Health score: 100 - (critical_issues * 10 + warning_issues * 2) / total_arrows * 100
        health_score = max(0, 100 - ((critical_count * 10 + warning_count * 2) / max(total_arrows, 1) * 100))
        
        # Convert dataclass to dict for JSON response
        validation_results = {
            'total_arrows': report.total_arrows,
            'total_issues': report.total_issues,
            'critical_issues': report.critical_issues,
            'warning_issues': report.warning_issues,
            'info_issues': report.info_issues,
            'health_score': round(health_score, 1),  # Add health_score for frontend
            'issues_by_category': report.issues_by_category,
            'summary_stats': report.summary_stats,
            'fix_recommendations': report.fix_recommendations,
            'calculator_impact': report.calculator_impact,
            'validation_timestamp': datetime.now().isoformat(),
            'issues': [
                {
                    'category': issue.category,
                    'severity': issue.severity,
                    'arrow_id': issue.arrow_id,
                    'manufacturer': issue.manufacturer,
                    'model_name': issue.model_name,
                    'field': issue.field,
                    'issue': issue.issue,
                    'current_value': issue.current_value,
                    'suggested_fix': issue.suggested_fix,
                    'sql_fix': issue.sql_fix
                }
                for issue in report.validation_issues
            ][:100]  # Limit to first 100 issues for performance
        }
        
        return jsonify(validation_results), 200
        
    except Exception as e:
        print(f"Error validating arrow data: {e}")
        return jsonify({'error': f'Failed to validate arrow data: {str(e)}'}), 500

@app.route('/api/admin/validate-arrows/sql-fix', methods=['GET'])
@token_required
@admin_required  
def get_arrow_validation_sql_fix(current_user):
    """Generate SQL fix script for arrow data validation issues"""
    try:
        # Import the validation script with production-compatible paths
        try:
            ArrowDataValidator = import_arrow_data_validator()
        except ImportError as e:
            return jsonify({'error': f'Failed to import validation module: {str(e)}'}), 500
        
        # Get database path
        db = get_database()
        if not db:
            return jsonify({'error': 'Database not available'}), 500
        
        db_path = db.db_path if hasattr(db, 'db_path') else 'arrow_database.db'
        
        # Generate SQL fix script
        validator = ArrowDataValidator(db_path)
        validator.validate_all_data()  # Run validation first
        sql_script = validator.get_sql_fix_script()
        
        return jsonify({
            'sql_script': sql_script,
            'generated_at': datetime.now().isoformat(),
            'total_fixes': len(validator.validation_issues)
        }), 200
        
    except Exception as e:
        print(f"Error generating SQL fix script: {e}")
        return jsonify({'error': f'Failed to generate SQL fix script: {str(e)}'}), 500

@app.route('/api/admin/validate-arrows/execute-fixes', methods=['POST'])
@token_required
@admin_required
def execute_arrow_validation_fixes(current_user):
    """Execute arrow data validation fixes with automatic backup"""
    try:
        # Import required modules with production-compatible paths
        try:
            ArrowDataValidator = import_arrow_data_validator()
        except ImportError as e:
            return jsonify({'error': f'Failed to import validation module: {str(e)}'}), 500
        
        # Import backup manager
        import sys
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        from backup_manager import BackupManager
        
        # Get database instance
        db = get_database()
        if not db:
            return jsonify({'error': 'Database not available'}), 500
        
        db_path = db.db_path if hasattr(db, 'db_path') else 'arrow_database.db'
        
        # Create automatic backup before applying fixes
        backup_manager = BackupManager()
        backup_name = f"validation_fixes_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        print(f"🛡️ Creating automatic backup before validation fixes: {backup_name}")
        backup_path = backup_manager.create_backup(backup_name)
        
        if not backup_path:
            return jsonify({
                'error': 'Failed to create backup before applying fixes'
            }), 500
        
        # Run validation to get current issues
        validator = ArrowDataValidator(db_path)
        report = validator.validate_all_data()
        
        if report.total_issues == 0:
            return jsonify({
                'success': True,
                'message': 'No validation issues to fix',
                'issues_fixed': 0,
                'backup_created': backup_result['backup_id']
            }), 200
        
        # Execute SQL fixes
        fixes_applied = 0
        errors = []
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Apply each SQL fix
            for issue in validator.validation_issues:
                if issue.sql_fix and not issue.sql_fix.strip().startswith('--'):
                    try:
                        cursor.execute(issue.sql_fix)
                        fixes_applied += 1
                        print(f"✅ Applied fix for {issue.manufacturer} {issue.model_name}: {issue.field}")
                    except Exception as fix_error:
                        error_msg = f"Failed to apply fix for {issue.manufacturer} {issue.model_name}: {str(fix_error)}"
                        errors.append(error_msg)
                        print(f"❌ {error_msg}")
            
            conn.commit()
        
        # Run validation again to verify fixes
        post_fix_validator = ArrowDataValidator(db_path)
        post_fix_report = post_fix_validator.validate_all_data()
        
        return jsonify({
            'success': True,
            'backup_created': backup_path,
            'backup_name': backup_name,
            'fixes_applied': fixes_applied,
            'errors': errors,
            'before_issues': report.total_issues,
            'after_issues': post_fix_report.total_issues,
            'improvement': report.total_issues - post_fix_report.total_issues,
            'execution_timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        print(f"Error executing validation fixes: {e}")
        return jsonify({'error': f'Failed to execute validation fixes: {str(e)}'}), 500

@app.route('/api/admin/execute-sql', methods=['POST'])
@token_required
@admin_required
def execute_individual_sql(current_user):
    """Execute individual SQL statement for arrow data fixes"""
    try:
        data = request.get_json()
        sql = data.get('sql', '').strip()
        description = data.get('description', 'Manual SQL execution')
        
        if not sql:
            return jsonify({'success': False, 'error': 'No SQL statement provided'}), 400
        
        # Basic security check - only allow UPDATE and DELETE statements for arrow data
        sql_upper = sql.upper().strip()
        if not (sql_upper.startswith('UPDATE ARROWS') or 
                sql_upper.startswith('UPDATE SPINE_SPECIFICATIONS') or
                sql_upper.startswith('DELETE FROM SPINE_SPECIFICATIONS')):
            return jsonify({'success': False, 'error': 'Only UPDATE and DELETE statements for arrow data are allowed'}), 400
        
        # Get database instance
        db = get_database()
        if not db:
            return jsonify({'success': False, 'error': 'Database not available'}), 500
        
        # Execute the SQL
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            rows_affected = cursor.rowcount
            conn.commit()
        
        print(f"✅ Executed individual SQL fix: {description}")
        print(f"   SQL: {sql}")
        print(f"   Rows affected: {rows_affected}")
        
        return jsonify({
            'success': True,
            'rows_affected': rows_affected,
            'description': description,
            'sql_executed': sql
        })
        
    except Exception as e:
        print(f"Error executing individual SQL: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/validate-arrows/merge-duplicates', methods=['POST'])
@token_required
@admin_required
def merge_duplicate_arrows(current_user):
    """Merge all duplicate arrows with automatic backup"""
    try:
        # Import required modules with production-compatible paths
        try:
            ArrowDataValidator = import_arrow_data_validator()
        except ImportError as e:
            return jsonify({'error': f'Failed to import validation module: {str(e)}'}), 500
        
        # Import backup manager
        import sys
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        from backup_manager import BackupManager
        
        # Get database instance
        db = get_database()
        if not db:
            return jsonify({'error': 'Database not available'}), 500
        
        db_path = db.db_path if hasattr(db, 'db_path') else 'arrow_database.db'
        
        # Create automatic backup before merging
        backup_manager = BackupManager()
        backup_name = f"duplicate_merge_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        print(f"🛡️ Creating backup before duplicate merge: {backup_name}")
        backup_path = backup_manager.create_backup(backup_name)
        
        if not backup_path:
            return jsonify({
                'error': 'Failed to create backup before merge operation'
            }), 500
        
        # Execute merge operation
        validator = ArrowDataValidator(db_path)
        merge_result = validator.merge_all_duplicates()
        
        return jsonify({
            'success': True,
            'backup_created': backup_path,
            'backup_name': backup_name,
            'merged_count': merge_result['merged_count'],
            'merge_operations': merge_result['merge_operations'],
            'errors': merge_result['errors'],
            'total_groups_processed': merge_result['total_groups_processed'],
            'execution_timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        print(f"Error merging duplicate arrows: {e}")
        return jsonify({'error': f'Failed to merge duplicates: {str(e)}'}), 500

# Enhanced Arrow Validation System API Endpoints

@app.route('/api/admin/validation/status', methods=['GET'])
@token_required
@admin_required
def get_validation_status(current_user):
    """Get overall validation health and latest results"""
    try:
        # Import the enhanced validation script with production-compatible paths
        try:
            ArrowDataValidator = import_arrow_data_validator()
        except ImportError as e:
            return jsonify({'error': f'Failed to import validation module: {str(e)}'}), 500
        
        db = get_database()
        if not db:
            return jsonify({'error': 'Database not available'}), 500
        
        db_path = db.db_path if hasattr(db, 'db_path') else 'arrow_database.db'
        
        # Quick validation run focusing on critical issues
        validator = ArrowDataValidator(db_path)
        report = validator.validate_all_data()
        
        # Categorize issues by severity
        critical_issues = [issue for issue in validator.validation_issues if issue.severity == 'critical']
        warning_issues = [issue for issue in validator.validation_issues if issue.severity == 'warning']
        
        # Calculate validation health score
        total_arrows = report.total_arrows
        critical_count = len(critical_issues)
        warning_count = len(warning_issues)
        
        # Health score: 100 - (critical_issues * 10 + warning_issues * 2) / total_arrows * 100
        health_score = max(0, 100 - ((critical_count * 10 + warning_count * 2) / max(total_arrows, 1) * 100))
        
        return jsonify({
            'validation_health_score': round(health_score, 1),
            'status': 'excellent' if health_score >= 90 else 'good' if health_score >= 70 else 'fair' if health_score >= 50 else 'poor',
            'total_arrows': total_arrows,
            'total_issues': len(validator.validation_issues),
            'critical_issues': critical_count,
            'warning_issues': warning_count,
            'issues_by_category': report.issues_by_category,
            'search_visibility_issues': len([i for i in critical_issues if i.category == 'Search Visibility']),
            'database_integrity_issues': len([i for i in critical_issues if i.category == 'Database Integrity']),
            'last_validation': datetime.now().isoformat(),
            'quick_fix_available': sum(1 for issue in validator.validation_issues if issue.sql_fix)
        }), 200
        
    except Exception as e:
        print(f"Error getting validation status: {e}")
        return jsonify({'error': f'Failed to get validation status: {str(e)}'}), 500

@app.route('/api/admin/validation/run', methods=['POST'])
@token_required
@admin_required
def trigger_validation_run(current_user):
    """Trigger a comprehensive validation run"""
    try:
        # Import the enhanced validation script with production-compatible paths
        try:
            ArrowDataValidator = import_arrow_data_validator()
        except ImportError as e:
            return jsonify({'error': f'Failed to import validation module: {str(e)}'}), 500
        
        db = get_database()
        if not db:
            return jsonify({'error': 'Database not available'}), 500
        
        db_path = db.db_path if hasattr(db, 'db_path') else 'arrow_database.db'
        
        # Run comprehensive validation
        validator = ArrowDataValidator(db_path)
        report = validator.validate_all_data()
        
        # Return detailed results
        return jsonify({
            'success': True,
            'validation_timestamp': datetime.now().isoformat(),
            'total_arrows': report.total_arrows,
            'total_issues': report.total_issues,
            'critical_issues': report.critical_issues,
            'warning_issues': report.warning_issues,
            'info_issues': report.info_issues,
            'issues_by_category': report.issues_by_category,
            'summary_stats': report.summary_stats,
            'fix_recommendations': report.fix_recommendations,
            'calculator_impact': report.calculator_impact,
            'detailed_issues': [
                {
                    'id': idx,
                    'category': issue.category,
                    'severity': issue.severity,
                    'arrow_id': issue.arrow_id,
                    'manufacturer': issue.manufacturer,
                    'model_name': issue.model_name,
                    'field': issue.field,
                    'issue': issue.issue,
                    'current_value': str(issue.current_value),
                    'suggested_fix': issue.suggested_fix,
                    'sql_fix': issue.sql_fix,
                    'auto_fixable': bool(issue.sql_fix)
                }
                for idx, issue in enumerate(validator.validation_issues)
            ]
        }), 200
        
    except Exception as e:
        print(f"Error running validation: {e}")
        return jsonify({'error': f'Failed to run validation: {str(e)}'}), 500

@app.route('/api/admin/validation/issues', methods=['GET'])
@token_required
@admin_required
def get_validation_issues(current_user):
    """Get current validation issues with filtering options"""
    try:
        # Import the enhanced validation script with production-compatible paths
        try:
            ArrowDataValidator = import_arrow_data_validator()
        except ImportError as e:
            return jsonify({'error': f'Failed to import validation module: {str(e)}'}), 500
        
        db = get_database()
        if not db:
            return jsonify({'error': 'Database not available'}), 500
        
        db_path = db.db_path if hasattr(db, 'db_path') else 'arrow_database.db'
        
        # Get query parameters for filtering
        severity_filter = request.args.get('severity')  # critical, warning, info
        category_filter = request.args.get('category')  # Search Visibility, Database Integrity, etc.
        limit = int(request.args.get('limit', 100))
        
        # Run validation
        validator = ArrowDataValidator(db_path)
        report = validator.validate_all_data()
        
        # Filter issues
        filtered_issues = validator.validation_issues
        if severity_filter:
            filtered_issues = [i for i in filtered_issues if i.severity == severity_filter]
        if category_filter:
            filtered_issues = [i for i in filtered_issues if i.category == category_filter]
        
        # Limit results
        filtered_issues = filtered_issues[:limit]
        
        return jsonify({
            'total_issues': len(validator.validation_issues),
            'filtered_count': len(filtered_issues),
            'applied_filters': {
                'severity': severity_filter,
                'category': category_filter,
                'limit': limit
            },
            'issues': [
                {
                    'id': idx,
                    'category': issue.category,
                    'severity': issue.severity,
                    'arrow_id': issue.arrow_id,
                    'manufacturer': issue.manufacturer,
                    'model_name': issue.model_name,
                    'field': issue.field,
                    'issue': issue.issue,
                    'current_value': str(issue.current_value),
                    'suggested_fix': issue.suggested_fix,
                    'sql_fix': issue.sql_fix,
                    'auto_fixable': bool(issue.sql_fix)
                }
                for idx, issue in enumerate(filtered_issues)
            ]
        }), 200
        
    except Exception as e:
        print(f"Error getting validation issues: {e}")
        return jsonify({'error': f'Failed to get validation issues: {str(e)}'}), 500

@app.route('/api/admin/validation/fix/<int:issue_id>', methods=['POST'])
@token_required
@admin_required
def apply_validation_fix(current_user, issue_id):
    """Apply automated fix for a specific validation issue"""
    try:
        # Import the enhanced validation script with production-compatible paths
        try:
            ArrowDataValidator = import_arrow_data_validator()
        except ImportError as e:
            return jsonify({'error': f'Failed to import validation module: {str(e)}'}), 500
        
        db = get_database()
        if not db:
            return jsonify({'error': 'Database not available'}), 500
        
        db_path = db.db_path if hasattr(db, 'db_path') else 'arrow_database.db'
        
        # Run validation to get current issues
        validator = ArrowDataValidator(db_path)
        report = validator.validate_all_data()
        
        # Find the specific issue
        if issue_id >= len(validator.validation_issues):
            return jsonify({'error': 'Issue ID not found'}), 404
        
        issue = validator.validation_issues[issue_id]
        
        if not issue.sql_fix:
            return jsonify({'error': 'Issue is not auto-fixable'}), 400
        
        # Apply the SQL fix
        with validator.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(issue.sql_fix)
            affected_rows = cursor.rowcount
            conn.commit()
        
        return jsonify({
            'success': True,
            'issue_id': issue_id,
            'arrow_id': issue.arrow_id,
            'fix_applied': issue.sql_fix,
            'affected_rows': affected_rows,
            'fix_timestamp': datetime.now().isoformat(),
            'issue_details': {
                'category': issue.category,
                'severity': issue.severity,
                'manufacturer': issue.manufacturer,
                'model_name': issue.model_name,
                'issue': issue.issue
            }
        }), 200
        
    except Exception as e:
        print(f"Error applying validation fix: {e}")
        return jsonify({'error': f'Failed to apply fix: {str(e)}'}), 500

@app.route('/api/admin/validation/mark-not-duplicate', methods=['POST'])
@token_required
@admin_required
def mark_not_duplicate(current_user):
    """Mark an issue as not a duplicate to exclude from future detection"""
    try:
        data = request.get_json()
        arrow_id = data.get('arrow_id')
        field = data.get('field', 'unknown')
        issue_hash = data.get('issue_hash')
        reason = data.get('reason', 'User marked as not duplicate')
        
        if not arrow_id:
            return jsonify({'success': False, 'error': 'Arrow ID required'}), 400
        
        db = get_database()
        if not db:
            return jsonify({'success': False, 'error': 'Database not available'}), 500
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS duplicate_exclusions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    arrow_id INTEGER NOT NULL,
                    field TEXT NOT NULL,
                    issue_hash TEXT,
                    reason TEXT,
                    excluded_by TEXT NOT NULL,
                    excluded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(arrow_id, field)
                )
            ''')
            
            # Insert exclusion record
            cursor.execute('''
                INSERT OR REPLACE INTO duplicate_exclusions 
                (arrow_id, field, issue_hash, reason, excluded_by)
                VALUES (?, ?, ?, ?, ?)
            ''', (arrow_id, field, issue_hash, reason, current_user['email']))
            
            # Mark the validation issue as resolved
            if issue_hash:
                cursor.execute('''
                    UPDATE validation_issues 
                    SET is_resolved = TRUE, 
                        resolved_at = datetime('now'),
                        resolved_by = ?
                    WHERE issue_hash = ?
                ''', (current_user['email'], issue_hash))
            
            conn.commit()
            
        return jsonify({
            'success': True,
            'message': f'Arrow ID {arrow_id} marked as not a duplicate'
        }), 200
        
    except Exception as e:
        print(f"Error marking not duplicate: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/bulk-fix-visibility', methods=['POST'])
@token_required
@admin_required
def bulk_fix_arrow_visibility(current_user):
    """
    Bulk fix for all arrows with search visibility issues
    Fixes missing description and arrow_type fields that prevent arrows from appearing in search
    """
    try:
        db = get_database()
        if not db:
            return jsonify({'success': False, 'error': 'Database not available'}), 500
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Count arrows needing fixes
            cursor.execute("""
                SELECT COUNT(*) 
                FROM arrows 
                WHERE description IS NULL 
                   OR description = '' 
                   OR arrow_type IS NULL 
                   OR arrow_type = ''
            """)
            
            issues_count = cursor.fetchone()[0]
            
            if issues_count == 0:
                return jsonify({
                    'success': True, 
                    'message': 'No invisible arrows found - all arrows have proper search visibility',
                    'fixed_count': 0
                })
            
            # Bulk fix for missing descriptions
            cursor.execute("""
                UPDATE arrows 
                SET description = COALESCE(
                    NULLIF(description, ''), 
                    manufacturer || ' ' || model_name || ' - High quality arrow'
                )
                WHERE description IS NULL OR description = ''
            """)
            
            description_fixes = cursor.rowcount
            
            # Bulk fix for missing arrow_type  
            cursor.execute("""
                UPDATE arrows 
                SET arrow_type = CASE
                    WHEN model_name LIKE '%target%' OR model_name LIKE '%Target%' THEN 'target'
                    WHEN model_name LIKE '%hunt%' OR model_name LIKE '%Hunt%' THEN 'hunting'
                    WHEN model_name LIKE '%3D%' OR model_name LIKE '%field%' THEN 'field'
                    WHEN model_name LIKE '%trad%' OR model_name LIKE '%traditional%' THEN 'traditional'
                    ELSE 'target'
                END
                WHERE arrow_type IS NULL OR arrow_type = ''
            """)
            
            type_fixes = cursor.rowcount
            
            conn.commit()
            
            total_fixes = description_fixes + type_fixes
            
            return jsonify({
                'success': True,
                'message': f'Successfully fixed search visibility for {total_fixes} field updates',
                'fixed_count': total_fixes,
                'description_fixes': description_fixes,
                'type_fixes': type_fixes
            })
        
    except Exception as e:
        logger.error(f"Error in bulk fix arrow visibility: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

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
    
    # Arrow length adjustment (5 lbs per inch difference from 28") - longer = stiffer needed
    length_adjustment = (arrow_length - 28) * 5
    effective_weight -= length_adjustment
    
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

# ===== ACTIVE BOW SETUP API ENDPOINTS =====

@app.route('/api/user/active-bow-setup', methods=['GET'])
@token_required
def get_active_bow_setup(current_user):
    """Get user's currently active bow setup"""
    try:
        user_db = get_database()
        if not user_db:
            return jsonify({"error": "Database not available"}), 500
        
        conn = user_db.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get user's active bow setup ID
        cursor.execute(
            'SELECT active_bow_setup_id FROM users WHERE id = ?',
            (current_user['id'],)
        )
        result = cursor.fetchone()
        
        if not result or not result['active_bow_setup_id']:
            # No active setup set, get the most recently updated setup
            cursor.execute('''
                SELECT id, name, bow_type, draw_weight, updated_at
                FROM bow_setups 
                WHERE user_id = ?
                ORDER BY updated_at DESC
                LIMIT 1
            ''', (current_user['id'],))
            
            most_recent = cursor.fetchone()
            if most_recent:
                # Auto-set this as active
                cursor.execute(
                    'UPDATE users SET active_bow_setup_id = ? WHERE id = ?',
                    (most_recent['id'], current_user['id'])
                )
                conn.commit()
                
                conn.close()
                return jsonify({
                    'active_bow_setup': dict(most_recent),
                    'auto_selected': True
                })
            else:
                conn.close()
                return jsonify({
                    'active_bow_setup': None,
                    'message': 'No bow setups found'
                })
        
        # Get the active setup details
        active_setup_id = result['active_bow_setup_id']
        cursor.execute('''
            SELECT id, name, bow_type, draw_weight, updated_at
            FROM bow_setups 
            WHERE id = ? AND user_id = ?
        ''', (active_setup_id, current_user['id']))
        
        active_setup = cursor.fetchone()
        conn.close()
        
        if not active_setup:
            # Active setup doesn't exist anymore, clear it
            conn = user_db.get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE users SET active_bow_setup_id = NULL WHERE id = ?',
                (current_user['id'],)
            )
            conn.commit()
            conn.close()
            
            return jsonify({
                'active_bow_setup': None,
                'message': 'Previously active setup no longer exists'
            })
        
        return jsonify({
            'active_bow_setup': dict(active_setup),
            'auto_selected': False
        })
        
    except Exception as e:
        print(f"Error getting active bow setup: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/active-bow-setup', methods=['PUT'])
@token_required
def set_active_bow_setup(current_user):
    """Set user's active bow setup"""
    try:
        data = request.get_json()
        setup_id = data.get('bow_setup_id')
        
        if not setup_id:
            return jsonify({'error': 'bow_setup_id is required'}), 400
        
        user_db = get_database()
        if not user_db:
            return jsonify({"error": "Database not available"}), 500
        
        conn = user_db.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Verify the setup exists and belongs to the user
        cursor.execute('''
            SELECT id, name, bow_type FROM bow_setups 
            WHERE id = ? AND user_id = ?
        ''', (setup_id, current_user['id']))
        
        setup = cursor.fetchone()
        if not setup:
            conn.close()
            return jsonify({'error': 'Bow setup not found'}), 404
        
        # Update user's active bow setup
        cursor.execute('''
            UPDATE users SET active_bow_setup_id = ? WHERE id = ?
        ''', (setup_id, current_user['id']))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': 'Active bow setup updated successfully',
            'active_bow_setup': dict(setup)
        })
        
    except Exception as e:
        print(f"Error setting active bow setup: {e}")
        return jsonify({'error': str(e)}), 500

# ===== GLOBAL CHANGE LOG API ENDPOINTS =====

@app.route('/api/change-log/global', methods=['GET'])
@token_required
def get_global_change_log(current_user):
    """Get global change history across all user's bow setups"""
    try:
        from change_log_service import ChangeLogService
        change_service = ChangeLogService()
        
        # Get query parameters
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        change_source = request.args.get('change_source', '')  # setup, equipment, arrow
        days_back = request.args.get('days_back')
        
        # Get all user's bow setups
        user_db = get_database()
        if not user_db:
            return jsonify({"error": "Database not available"}), 500
        conn = user_db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, name FROM bow_setups WHERE user_id = ?', (current_user['id'],))
        bow_setups = {row['id']: row['name'] for row in cursor.fetchall()}
        conn.close()
        
        if not bow_setups:
            return jsonify({'changes': [], 'statistics': {
                'total_activities': 0,
                'setup_count': 0,
                'recent_activities': 0,
                'active_setups': 0
            }})
        
        # Get unified changes across all setups
        all_changes = []
        setup_ids = list(bow_setups.keys())
        
        for setup_id in setup_ids:
            changes = change_service.get_unified_change_history(
                bow_setup_id=setup_id,
                user_id=current_user['id'],
                limit=1000,  # Get all changes, we'll paginate manually
                days_back=int(days_back) if days_back else None
            )
            
            # Add setup name to each change
            for change in changes:
                change['bow_setup_name'] = bow_setups[setup_id]
                change['bow_setup_id'] = setup_id
            
            all_changes.extend(changes)
        
        # Filter by change source if specified
        if change_source:
            all_changes = [c for c in all_changes if c.get('change_source') == change_source]
        
        # Sort by timestamp (most recent first)
        all_changes.sort(key=lambda x: x['created_at'], reverse=True)
        
        # Manual pagination
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_changes = all_changes[start_idx:end_idx]
        
        # Calculate statistics
        from datetime import datetime, timedelta
        recent_cutoff = datetime.now() - timedelta(days=30)
        recent_changes = [c for c in all_changes if isinstance(c['created_at'], datetime) and c['created_at'] >= recent_cutoff]
        
        statistics = {
            'total_activities': len(all_changes),
            'setup_count': len(bow_setups),
            'recent_activities': len(recent_changes),
            'active_setups': len([s for s in setup_ids if any(c['bow_setup_id'] == s for c in recent_changes)])
        }
        
        return jsonify({
            'changes': paginated_changes,
            'statistics': statistics,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': len(all_changes),
                'has_more': end_idx < len(all_changes)
            }
        })
        
    except Exception as e:
        print(f"Error getting global change log: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/change-log/global-statistics', methods=['GET'])
@token_required
def get_global_statistics(current_user):
    """Get global statistics across all user activities"""
    try:
        from change_log_service import ChangeLogService
        change_service = ChangeLogService()
        
        # Get all user's bow setups
        user_db = get_database()
        if not user_db:
            return jsonify({"error": "Database not available"}), 500
        conn = user_db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM bow_setups WHERE user_id = ?', (current_user['id'],))
        setup_ids = [row['id'] for row in cursor.fetchall()]
        conn.close()
        
        if not setup_ids:
            return jsonify({
                'total_activities': 0,
                'setup_count': 0,
                'recent_activities': 0,
                'active_setups': 0,
                'activity_breakdown': {
                    'setup_changes': 0,
                    'equipment_changes': 0,
                    'arrow_changes': 0
                }
            })
        
        # Aggregate statistics across all setups
        total_stats = {
            'total_activities': 0,
            'recent_activities': 0,
            'equipment_changes': 0,
            'arrow_changes': 0,
            'setup_changes': 0
        }
        
        active_setups = set()
        
        for setup_id in setup_ids:
            stats = change_service.get_change_statistics(setup_id, current_user['id'])
            
            total_stats['total_activities'] += stats.get('total_changes', 0)
            total_stats['recent_activities'] += stats.get('changes_last_30_days', 0)
            
            # Count changes by type
            equipment_changes = stats.get('equipment_changes_by_type', {})
            arrow_changes = stats.get('arrow_changes_by_type', {})
            
            total_stats['equipment_changes'] += sum(equipment_changes.values())
            total_stats['arrow_changes'] += sum(arrow_changes.values())
            
            # Setup changes (total - equipment - arrow)
            setup_change_count = stats.get('total_changes', 0) - sum(equipment_changes.values()) - sum(arrow_changes.values())
            total_stats['setup_changes'] += setup_change_count
            
            # Check if setup had recent activity
            if stats.get('changes_last_30_days', 0) > 0:
                active_setups.add(setup_id)
        
        return jsonify({
            'total_activities': total_stats['total_activities'],
            'setup_count': len(setup_ids),
            'recent_activities': total_stats['recent_activities'],
            'active_setups': len(active_setups),
            'activity_breakdown': {
                'setup_changes': total_stats['setup_changes'],
                'equipment_changes': total_stats['equipment_changes'],
                'arrow_changes': total_stats['arrow_changes']
            }
        })
        
    except Exception as e:
        print(f"Error getting global statistics: {e}")
        return jsonify({'error': str(e)}), 500

# Enhanced Performance Analysis API Endpoints
# ==========================================

@app.route('/api/calculator/enhanced-foc', methods=['POST'])
def calculate_enhanced_foc():
    """Calculate enhanced FOC with optimization recommendations and performance analysis"""
    try:
        data = request.get_json()
        
        # Extract arrow specifications
        arrow_length = data.get('arrow_length', 29.0)
        point_weight = data.get('point_weight', 125.0)
        shaft_weight = data.get('shaft_weight', 300.0)
        nock_weight = data.get('nock_weight', 10.0)
        fletching_weight = data.get('fletching_weight', 15.0)
        insert_weight = data.get('insert_weight', 15.0)
        intended_use = data.get('intended_use', 'hunting')
        
        # Initialize spine calculator
        calculator = SpineCalculator()
        
        # Calculate enhanced FOC
        result = calculator.calculate_enhanced_foc(
            arrow_length=arrow_length,
            point_weight=point_weight,
            shaft_weight=shaft_weight,
            nock_weight=nock_weight,
            fletching_weight=fletching_weight,
            insert_weight=insert_weight,
            intended_use=intended_use
        )
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error calculating enhanced FOC: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Failed to calculate enhanced FOC analysis'}), 500

@app.route('/api/calculator/ballistics', methods=['POST'])
def calculate_ballistics():
    """Calculate comprehensive ballistics analysis including trajectory and performance metrics"""
    try:
        data = request.get_json()
        
        # Extract arrow and bow specifications
        arrow_speed_fps = data.get('arrow_speed_fps', 280.0)
        arrow_weight_grains = data.get('arrow_weight_grains', 420.0)
        arrow_diameter_inches = data.get('arrow_diameter_inches', 0.246)
        arrow_type = data.get('arrow_type', 'hunting')
        
        # Environmental conditions
        env_data = data.get('environmental', {})
        environmental = EnvironmentalConditions(
            temperature_f=env_data.get('temperature_f', 70.0),
            humidity_percent=env_data.get('humidity_percent', 50.0),
            altitude_feet=env_data.get('altitude_feet', 0.0),
            wind_speed_mph=env_data.get('wind_speed_mph', 0.0),
            wind_direction_degrees=env_data.get('wind_direction_degrees', 0.0),
            air_pressure_inHg=env_data.get('air_pressure_inHg', 29.92)
        )
        
        # Shooting conditions
        shoot_data = data.get('shooting', {})
        shooting = ShootingConditions(
            shot_angle_degrees=shoot_data.get('shot_angle_degrees', 0.0),
            sight_height_inches=shoot_data.get('sight_height_inches', 7.0),
            zero_distance_yards=shoot_data.get('zero_distance_yards', 20.0),
            max_range_yards=shoot_data.get('max_range_yards', 100.0)
        )
        
        # Map arrow type string to enum
        arrow_type_map = {
            'hunting': BallisticsArrowType.HUNTING,
            'target': BallisticsArrowType.TARGET,
            'field': BallisticsArrowType.FIELD,
            '3d': BallisticsArrowType.THREE_D
        }
        arrow_type_enum = arrow_type_map.get(arrow_type, BallisticsArrowType.HUNTING)
        
        # Initialize ballistics calculator
        calculator = BallisticsCalculator()
        
        # Calculate trajectory
        result = calculator.calculate_trajectory(
            arrow_speed_fps=arrow_speed_fps,
            arrow_weight_grains=arrow_weight_grains,
            arrow_diameter_inches=arrow_diameter_inches,
            arrow_type=arrow_type_enum,
            environmental=environmental,
            shooting=shooting
        )
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error calculating ballistics: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Failed to calculate ballistics analysis'}), 500

@app.route('/api/calculator/kinetic-energy', methods=['POST'])
def calculate_kinetic_energy():
    """Calculate kinetic energy and momentum at specified distances"""
    try:
        data = request.get_json()
        
        arrow_speed_fps = data.get('arrow_speed_fps', 280.0)
        arrow_weight_grains = data.get('arrow_weight_grains', 420.0)
        distances = data.get('distances', [20, 30, 40, 50, 60, 80, 100])
        
        # Initialize ballistics calculator
        calculator = BallisticsCalculator()
        
        results = {}
        for distance in distances:
            ke_data = calculator.calculate_kinetic_energy(
                arrow_speed_fps=arrow_speed_fps,
                arrow_weight_grains=arrow_weight_grains,
                distance_yards=distance
            )
            results[f"{distance}yd"] = ke_data
        
        return jsonify({
            'kinetic_energy_by_distance': results,
            'arrow_speed_fps': arrow_speed_fps,
            'arrow_weight_grains': arrow_weight_grains
        })
        
    except Exception as e:
        print(f"Error calculating kinetic energy: {e}")
        return jsonify({'error': 'Failed to calculate kinetic energy'}), 500

@app.route('/api/calculator/penetration-analysis', methods=['POST'])
def calculate_penetration_analysis():
    """Calculate penetration potential based on kinetic energy and momentum"""
    try:
        data = request.get_json()
        
        kinetic_energy_ft_lbs = data.get('kinetic_energy_ft_lbs')
        momentum_slug_fps = data.get('momentum_slug_fps')
        arrow_type = data.get('arrow_type', 'hunting')
        
        # If KE and momentum not provided, calculate from speed and weight
        if kinetic_energy_ft_lbs is None or momentum_slug_fps is None:
            arrow_speed_fps = data.get('arrow_speed_fps', 280.0)
            arrow_weight_grains = data.get('arrow_weight_grains', 420.0)
            distance_yards = data.get('distance_yards', 0.0)
            
            calculator = BallisticsCalculator()
            ke_data = calculator.calculate_kinetic_energy(
                arrow_speed_fps=arrow_speed_fps,
                arrow_weight_grains=arrow_weight_grains,
                distance_yards=distance_yards
            )
            kinetic_energy_ft_lbs = ke_data['kinetic_energy_ft_lbs']
            momentum_slug_fps = ke_data['momentum_slug_fps']
        
        # Map arrow type string to enum
        arrow_type_map = {
            'hunting': BallisticsArrowType.HUNTING,
            'target': BallisticsArrowType.TARGET,
            'field': BallisticsArrowType.FIELD,
            '3d': BallisticsArrowType.THREE_D
        }
        arrow_type_enum = arrow_type_map.get(arrow_type, BallisticsArrowType.HUNTING)
        
        # Calculate penetration potential
        calculator = BallisticsCalculator()
        result = calculator.calculate_penetration_potential(
            kinetic_energy_ft_lbs=kinetic_energy_ft_lbs,
            momentum_slug_fps=momentum_slug_fps,
            arrow_type=arrow_type_enum
        )
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error calculating penetration analysis: {e}")
        return jsonify({'error': 'Failed to calculate penetration analysis'}), 500

@app.route('/api/calculator/arrow-speed-estimate', methods=['POST'])
def estimate_arrow_speed():
    """Enhanced arrow speed estimation with chronograph data and string material factors"""
    try:
        data = request.get_json()
        
        # Bow specifications
        bow_ibo_speed = data.get('bow_ibo_speed', 310.0)
        bow_draw_weight = data.get('bow_draw_weight', 70.0)
        bow_draw_length = data.get('bow_draw_length', 29.0)
        bow_type = data.get('bow_type', 'compound')
        
        # Arrow specifications
        arrow_weight_grains = data.get('arrow_weight_grains', 420.0)
        
        # Enhanced parameters
        string_material = data.get('string_material', 'dacron')
        setup_id = data.get('setup_id')
        arrow_id = data.get('arrow_id')
        
        # Check for chronograph data first (most accurate)
        chronograph_result = None
        if setup_id and arrow_id:
            try:
                user_db = get_database()
                if not user_db:
                    return jsonify({"error": "Database not available"}), 500
                cursor = user_db.get_connection().cursor()
                
                cursor.execute('''
                    SELECT measured_speed_fps, arrow_weight_grains, std_deviation, shot_count
                    FROM chronograph_data 
                    WHERE setup_id = ? AND arrow_id = ? AND verified = 1
                    ORDER BY measurement_date DESC
                    LIMIT 1
                ''', (setup_id, arrow_id))
                
                chronograph_data = cursor.fetchone()
                
                if chronograph_data:
                    measured_speed, measured_weight, std_dev, shot_count = chronograph_data
                    
                    # Adjust for different arrow weight using kinetic energy conservation
                    if measured_weight != arrow_weight_grains:
                        speed_ratio = (measured_weight / arrow_weight_grains) ** 0.5
                        adjusted_speed = measured_speed * speed_ratio
                    else:
                        adjusted_speed = measured_speed
                    
                    confidence = min(100, (shot_count * 10) + (85 if std_dev and std_dev < 5 else 70))
                    
                    chronograph_result = {
                        'speed': adjusted_speed,
                        'confidence': confidence,
                        'original_data': {
                            'measured_speed_fps': measured_speed,
                            'measured_weight_grains': measured_weight,
                            'shot_count': shot_count,
                            'std_deviation': std_dev
                        }
                    }
                    
            except Exception as e:
                print(f"Error checking chronograph data: {e}")
                # Continue with estimation if chronograph lookup fails
        
        # If chronograph data available, use it
        if chronograph_result:
            return jsonify({
                'estimated_speed_fps': round(chronograph_result['speed'], 1),
                'calculation_method': 'chronograph_data',
                'confidence_percent': chronograph_result['confidence'],
                'chronograph_data': chronograph_result['original_data'],
                'string_material': string_material
            }), 200
        
        # String material speed modifiers
        string_speed_modifiers = {
            'dacron': 0.92,           # Slowest, most forgiving (default)
            'fastflight': 1.00,       # Standard modern string
            'dyneema': 1.02,          # Faster, low stretch
            'vectran': 1.03,          # High performance
            'sk75_dyneema': 1.04,     # Premium racing strings
            'custom_blend': 1.01      # Custom string materials
        }
        
        # Get string modifier (default to slowest for safety)
        string_modifier = string_speed_modifiers.get(string_material.lower(), 0.92)
        
        # Use existing spine calculator for base calculation
        calculator = SpineCalculator()
        
        # Map bow type string to enum
        bow_type_map = {
            'compound': BowType.COMPOUND,
            'recurve': BowType.RECURVE,
            'longbow': BowType.TRADITIONAL,  # Map longbow to traditional
            'traditional': BowType.TRADITIONAL,
            'barebow': BowType.RECURVE  # Map barebow to recurve
        }
        bow_type_enum = bow_type_map.get(bow_type.lower(), BowType.COMPOUND)
        
        # Create bow configuration
        bow_config = BowConfiguration(
            draw_weight=bow_draw_weight,
            draw_length=bow_draw_length,
            bow_type=bow_type_enum,
            ibo_speed=bow_ibo_speed
        )
        
        # Estimate arrow speed using existing calculator
        base_estimated_speed = calculator._estimate_arrow_speed(bow_config, arrow_weight_grains)
        
        # Apply string material modifier
        final_speed = base_estimated_speed * string_modifier
        
        # Ensure reasonable bounds
        final_speed = max(100, min(450, final_speed))
        
        # Calculate velocity factors for reporting
        standard_arrow_weight = 5 * bow_draw_weight  # Standard: 5 grains per pound
        weight_ratio = arrow_weight_grains / standard_arrow_weight
        length_factor = bow_draw_length / 30.0  # Standard: 30" draw
        
        return jsonify({
            'estimated_speed_fps': round(final_speed, 1),
            'calculation_method': f'{bow_type}_estimation_with_string_material',
            'confidence_percent': 75,  # Moderate confidence for estimation
            'bow_ibo_speed': bow_ibo_speed,
            'arrow_weight_grains': arrow_weight_grains,
            'string_material': string_material,
            'factors': {
                'base_speed_estimate': round(base_estimated_speed, 1),
                'string_modifier': string_modifier,
                'string_speed_effect': f"{((string_modifier - 1) * 100):+.1f}%",
                'bow_type': bow_type,
                'standard_arrow_weight': standard_arrow_weight,
                'weight_ratio': round(weight_ratio, 2),
                'length_factor': round(length_factor, 3)
            },
            'speed_factors': {
                'weight_effect': f"{'Heavier' if weight_ratio > 1 else 'Lighter'} than standard",
                'length_effect': f"{'Longer' if bow_draw_length > 30 else 'Shorter'} than standard draw",
                'string_effect': f"String material: {string_material} ({((string_modifier - 1) * 100):+.1f}% speed)"
            }
        })
        
    except Exception as e:
        import traceback
        print(f"Error estimating arrow speed: {e}")
        print(f"Full traceback:\n{traceback.format_exc()}")
        return jsonify({'error': f'Failed to estimate arrow speed: {str(e)}'}), 500

@app.route('/api/calculator/comprehensive-performance', methods=['POST'])
def calculate_comprehensive_performance():
    """Calculate comprehensive arrow performance analysis combining FOC, ballistics, and penetration"""
    try:
        data = request.get_json()
        
        # Extract all specifications
        bow_config_data = data.get('bow_config', {})
        arrow_specs = data.get('arrow_specs', {})
        environmental_data = data.get('environmental', {})
        shooting_data = data.get('shooting', {})
        
        # Initialize calculators
        spine_calculator = SpineCalculator()
        ballistics_calculator = BallisticsCalculator()
        
        # Extract arrow specifications
        arrow_length = arrow_specs.get('arrow_length', 29.0)
        point_weight = arrow_specs.get('point_weight', 125.0)
        shaft_weight = arrow_specs.get('shaft_weight', 300.0)
        total_arrow_weight = arrow_specs.get('total_weight', 
            point_weight + shaft_weight + arrow_specs.get('nock_weight', 10.0) + 
            arrow_specs.get('fletching_weight', 15.0) + arrow_specs.get('insert_weight', 15.0))
        arrow_diameter = arrow_specs.get('diameter', 0.246)
        intended_use = arrow_specs.get('intended_use', 'hunting')
        
        # Estimate arrow speed if not provided
        arrow_speed = arrow_specs.get('speed_fps')
        if not arrow_speed:
            bow_config = BowConfiguration(
                draw_weight=bow_config_data.get('draw_weight', 70.0),
                draw_length=bow_config_data.get('draw_length', 29.0),
                bow_type=BowType.COMPOUND,
                ibo_speed=bow_config_data.get('ibo_speed', 310.0)
            )
            arrow_speed = spine_calculator._estimate_arrow_speed(bow_config, total_arrow_weight)
        
        # Calculate enhanced FOC
        foc_result = spine_calculator.calculate_enhanced_foc(
            arrow_length=arrow_length,
            point_weight=point_weight,
            shaft_weight=shaft_weight,
            nock_weight=arrow_specs.get('nock_weight', 10.0),
            fletching_weight=arrow_specs.get('fletching_weight', 15.0),
            insert_weight=arrow_specs.get('insert_weight', 15.0),
            intended_use=intended_use
        )
        
        # Calculate kinetic energy at multiple distances
        ke_distances = [20, 30, 40, 50, 60, 80]
        kinetic_energy_data = {}
        for distance in ke_distances:
            ke_data = ballistics_calculator.calculate_kinetic_energy(
                arrow_speed_fps=arrow_speed,
                arrow_weight_grains=total_arrow_weight,
                distance_yards=distance
            )
            kinetic_energy_data[f"{distance}yd"] = ke_data
        
        # Calculate penetration analysis
        arrow_type_map = {
            'hunting': BallisticsArrowType.HUNTING,
            'target': BallisticsArrowType.TARGET,
            'field': BallisticsArrowType.FIELD,
            '3d': BallisticsArrowType.THREE_D
        }
        arrow_type_enum = arrow_type_map.get(intended_use, BallisticsArrowType.HUNTING)
        
        penetration_result = ballistics_calculator.calculate_penetration_potential(
            kinetic_energy_ft_lbs=kinetic_energy_data['20yd']['kinetic_energy_ft_lbs'],
            momentum_slug_fps=kinetic_energy_data['20yd']['momentum_slug_fps'],
            arrow_type=arrow_type_enum
        )
        
        # Calculate overall performance score
        overall_score = (
            foc_result['performance_metrics']['overall_performance'] * 0.3 +
            penetration_result['penetration_score'] * 0.4 +
            (arrow_speed / 350 * 100) * 0.3  # Speed factor
        )
        
        return jsonify({
            'foc_analysis': foc_result,
            'kinetic_energy_analysis': kinetic_energy_data,
            'penetration_analysis': penetration_result,
            'performance_summary': {
                'overall_score': round(overall_score, 1),
                'arrow_speed_fps': round(arrow_speed, 1),
                'total_arrow_weight': total_arrow_weight,
                'primary_recommendation': get_primary_recommendation(overall_score, intended_use),
                'key_strengths': get_key_strengths(foc_result, penetration_result, arrow_speed),
                'improvement_areas': get_improvement_areas(foc_result, penetration_result, arrow_speed, intended_use)
            }
        })
        
    except Exception as e:
        print(f"Error calculating comprehensive performance: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Failed to calculate comprehensive performance analysis'}), 500

# ============================================================================
# CHRONOGRAPH DATA API ENDPOINTS
# ============================================================================

@app.route('/api/chronograph-data', methods=['POST'])
@token_required
def create_chronograph_data(current_user):
    """Create new chronograph data entry"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['setup_id', 'setup_arrow_id', 'measured_speed_fps', 'arrow_weight_grains']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Field {field} is required'}), 400
        
        # Get user database
        user_db = get_database()
        if not user_db:
            return jsonify({"error": "Database not available"}), 500
        cursor = user_db.get_connection().cursor()
        
        # Get arrow_length and point_weight from setup_arrows table
        cursor.execute('''
            SELECT arrow_length, point_weight, arrow_id 
            FROM setup_arrows 
            WHERE id = ?
        ''', (data['setup_arrow_id'],))
        setup_arrow = cursor.fetchone()
        
        if not setup_arrow:
            return jsonify({'error': 'Setup arrow not found'}), 404
        
        arrow_length, point_weight, arrow_id = setup_arrow
        
        # Insert chronograph data with both old and new column formats for compatibility
        cursor.execute('''
            INSERT INTO chronograph_data 
            (setup_id, arrow_id, arrow_length, point_weight, measured_speed,
             setup_arrow_id, measured_speed_fps, arrow_weight_grains,
             temperature_f, humidity_percent, chronograph_model, shot_count, std_deviation,
             min_speed_fps, max_speed_fps, notes, verified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['setup_id'], arrow_id, arrow_length, point_weight, data['measured_speed_fps'],
            data['setup_arrow_id'], data['measured_speed_fps'], data['arrow_weight_grains'],
            data.get('temperature_f', 70), data.get('humidity_percent', 50),
            data.get('chronograph_model', ''), data.get('shot_count', 1),
            data.get('std_deviation'), data.get('min_speed_fps'), data.get('max_speed_fps'),
            data.get('notes', ''), 1  # Set verified = 1 by default
        ))
        
        chronograph_id = cursor.lastrowid
        user_db.get_connection().commit()
        
        # Return the created data
        cursor.execute('SELECT * FROM chronograph_data WHERE id = ?', (chronograph_id,))
        created_data = cursor.fetchone()
        
        return jsonify({
            'id': created_data[0],
            'setup_id': created_data[1],
            'arrow_id': created_data[2],
            'setup_arrow_id': created_data[3],
            'measured_speed_fps': created_data[4],
            'arrow_weight_grains': created_data[5],
            'temperature_f': created_data[6],
            'humidity_percent': created_data[7],
            'measurement_date': created_data[8],
            'chronograph_model': created_data[9],
            'shot_count': created_data[10],
            'std_deviation': created_data[11],
            'min_speed_fps': created_data[12],
            'max_speed_fps': created_data[13],
            'verified': created_data[14],
            'notes': created_data[15]
        }), 201
        
    except Exception as e:
        print(f"Error creating chronograph data: {e}")
        return jsonify({'error': 'Failed to create chronograph data'}), 500

@app.route('/api/chronograph-data/setup/<int:setup_id>', methods=['GET'])
@token_required
def get_chronograph_data_for_setup(current_user, setup_id):
    """Get all chronograph data for a specific bow setup"""
    try:
        user_db = get_database()
        if not user_db:
            return jsonify({"error": "Database not available"}), 500
        cursor = user_db.get_connection().cursor()
        
        # Get chronograph data with arrow information
        cursor.execute('''
            SELECT cd.id, cd.setup_id, cd.arrow_id, cd.setup_arrow_id, 
                   cd.measured_speed_fps, cd.arrow_weight_grains, cd.temperature_f, 
                   cd.humidity_percent, cd.measurement_date, cd.chronograph_model, 
                   cd.shot_count, cd.std_deviation, cd.min_speed_fps, cd.max_speed_fps, 
                   cd.verified, cd.notes, cd.created_at, cd.updated_at,
                   sa.arrow_length, sa.point_weight, sa.calculated_spine,
                   COALESCE(a.manufacturer, 'Unknown') as manufacturer, 
                   COALESCE(a.model_name, 'Arrow') as model_name
            FROM chronograph_data cd
            LEFT JOIN setup_arrows sa ON cd.setup_arrow_id = sa.id
            LEFT JOIN arrows a ON cd.arrow_id = a.id
            WHERE cd.setup_id = ?
            ORDER BY cd.measurement_date DESC
        ''', (setup_id,))
        
        rows = cursor.fetchall()
        chronograph_data = []
        
        for row in rows:
            # Use dict access for better safety and readability
            row_dict = dict(row)
            arrow_name = f"{row_dict.get('manufacturer', 'Unknown')} {row_dict.get('model_name', 'Arrow')}"
            
            chronograph_data.append({
                'id': row_dict.get('id'),
                'setup_id': row_dict.get('setup_id'),
                'arrow_id': row_dict.get('arrow_id'),
                'setup_arrow_id': row_dict.get('setup_arrow_id'),
                'measured_speed_fps': row_dict.get('measured_speed_fps'),
                'arrow_weight_grains': row_dict.get('arrow_weight_grains'),
                'temperature_f': row_dict.get('temperature_f'),
                'humidity_percent': row_dict.get('humidity_percent'),
                'measurement_date': row_dict.get('measurement_date'),
                'chronograph_model': row_dict.get('chronograph_model'),
                'shot_count': row_dict.get('shot_count'),
                'std_deviation': row_dict.get('std_deviation'),
                'min_speed_fps': row_dict.get('min_speed_fps'),
                'max_speed_fps': row_dict.get('max_speed_fps'),
                'verified': row_dict.get('verified'),
                'notes': row_dict.get('notes'),
                'arrow_name': arrow_name,
                'arrow_length': row_dict.get('arrow_length'),
                'point_weight': row_dict.get('point_weight'),
                'calculated_spine': row_dict.get('calculated_spine')
            })
        
        return jsonify(chronograph_data), 200
        
    except Exception as e:
        print(f"Error getting chronograph data: {e}")
        return jsonify({'error': 'Failed to get chronograph data'}), 500

@app.route('/api/chronograph-data/<int:data_id>', methods=['PUT'])
@token_required
def update_chronograph_data(current_user, data_id):
    """Update chronograph data entry"""
    try:
        data = request.get_json()
        
        user_db = get_database()
        if not user_db:
            return jsonify({"error": "Database not available"}), 500
        cursor = user_db.get_connection().cursor()
        
        # Update chronograph data
        cursor.execute('''
            UPDATE chronograph_data SET
                measured_speed_fps = ?, arrow_weight_grains = ?, temperature_f = ?,
                humidity_percent = ?, chronograph_model = ?, shot_count = ?,
                std_deviation = ?, min_speed_fps = ?, max_speed_fps = ?, notes = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            data.get('measured_speed_fps'), data.get('arrow_weight_grains'),
            data.get('temperature_f'), data.get('humidity_percent'),
            data.get('chronograph_model', ''), data.get('shot_count', 1),
            data.get('std_deviation'), data.get('min_speed_fps'), data.get('max_speed_fps'),
            data.get('notes', ''), data_id
        ))
        
        user_db.get_connection().commit()
        
        if cursor.rowcount == 0:
            return jsonify({'error': 'Chronograph data not found'}), 404
        
        return jsonify({'message': 'Chronograph data updated successfully'}), 200
        
    except Exception as e:
        print(f"Error updating chronograph data: {e}")
        return jsonify({'error': 'Failed to update chronograph data'}), 500

@app.route('/api/chronograph-data/<int:data_id>', methods=['DELETE'])
@token_required
def delete_chronograph_data(current_user, data_id):
    """Delete chronograph data entry"""
    try:
        user_db = get_database()
        if not user_db:
            return jsonify({"error": "Database not available"}), 500
        cursor = user_db.get_connection().cursor()
        
        cursor.execute('DELETE FROM chronograph_data WHERE id = ?', (data_id,))
        user_db.get_connection().commit()
        
        if cursor.rowcount == 0:
            return jsonify({'error': 'Chronograph data not found'}), 404
        
        return jsonify({'message': 'Chronograph data deleted successfully'}), 200
        
    except Exception as e:
        print(f"Error deleting chronograph data: {e}")
        return jsonify({'error': 'Failed to delete chronograph data'}), 500

@app.route('/api/chronograph-data/arrow/<int:arrow_id>/estimate-speed', methods=['POST'])
@token_required
def estimate_speed_from_chronograph(current_user, arrow_id):
    """Estimate arrow speed for different weights using chronograph data"""
    try:
        data = request.get_json()
        target_weight = data.get('target_weight')
        
        if not target_weight:
            return jsonify({'error': 'target_weight is required'}), 400
        
        user_db = get_database()
        if not user_db:
            return jsonify({"error": "Database not available"}), 500
        cursor = user_db.get_connection().cursor()
        
        # Find chronograph data for this arrow or similar setup
        cursor.execute('''
            SELECT measured_speed_fps, arrow_weight_grains, std_deviation, shot_count
            FROM chronograph_data 
            WHERE arrow_id = ? AND verified = 1
            ORDER BY measurement_date DESC
            LIMIT 5
        ''', (arrow_id,))
        
        chronograph_records = cursor.fetchall()
        
        if not chronograph_records:
            return jsonify({'error': 'No chronograph data found for this arrow'}), 404
        
        # Use the most recent measurement for calculation
        measured_speed, measured_weight, std_dev, shot_count = chronograph_records[0]
        
        # Calculate speed for target weight using kinetic energy conservation
        # KE = 0.5 * m * v², so v₂ = v₁ * √(m₁/m₂)
        speed_ratio = (measured_weight / target_weight) ** 0.5
        estimated_speed = measured_speed * speed_ratio
        
        # Calculate confidence based on data quality
        confidence = min(100, (shot_count * 10) + (85 if std_dev and std_dev < 5 else 60))
        
        return jsonify({
            'estimated_speed_fps': round(estimated_speed, 1),
            'confidence_percent': confidence,
            'based_on': {
                'measured_speed_fps': measured_speed,
                'measured_weight_grains': measured_weight,
                'target_weight_grains': target_weight,
                'shot_count': shot_count,
                'std_deviation': std_dev
            },
            'calculation_method': 'kinetic_energy_conservation'
        }), 200
        
    except Exception as e:
        print(f"Error estimating speed from chronograph: {e}")
        return jsonify({'error': 'Failed to estimate speed'}), 500

def get_primary_recommendation(overall_score: float, intended_use: str) -> str:
    """Get primary recommendation based on overall performance score"""
    if overall_score >= 85:
        return f"Excellent setup for {intended_use} - ready for field use"
    elif overall_score >= 70:
        return f"Good setup for {intended_use} - minor optimizations possible"
    elif overall_score >= 55:
        return f"Adequate setup for {intended_use} - consider improvements"
    else:
        return f"Setup needs optimization for {intended_use} applications"

def get_key_strengths(foc_result: dict, penetration_result: dict, arrow_speed: float) -> List[str]:
    """Identify key strengths of the arrow setup"""
    strengths = []
    
    if foc_result.get('foc_status') == 'optimal':
        strengths.append("Optimal FOC balance")
    
    if penetration_result.get('penetration_score', 0) >= 80:
        strengths.append("Excellent penetration power")
    
    if arrow_speed >= 300:
        strengths.append("High velocity for flat trajectory")
    
    if foc_result.get('performance_metrics', {}).get('overall_performance', 0) >= 80:
        strengths.append("Well-balanced performance characteristics")
    
    return strengths or ["Functional arrow setup"]

def get_improvement_areas(foc_result: dict, penetration_result: dict, 
                         arrow_speed: float, intended_use: str) -> List[str]:
    """Identify areas for improvement"""
    improvements = []
    
    foc_status = foc_result.get('foc_status')
    if foc_status in ['too_low', 'too_high']:
        improvements.append(f"FOC optimization needed ({foc_status.replace('_', ' ')})")
    
    penetration_score = penetration_result.get('penetration_score', 0)
    if penetration_score < 60 and intended_use == 'hunting':
        improvements.append("Increase arrow weight for better penetration")
    
    if arrow_speed < 250:
        improvements.append("Consider lighter arrow or higher draw weight for better speed")
    
    overall_performance = foc_result.get('performance_metrics', {}).get('overall_performance', 0)
    if overall_performance < 70:
        improvements.append("Overall setup tuning needed for intended use")
    
    return improvements or ["Setup is well-optimized"]

# ==========================================
# Journal System API Endpoints
# ==========================================

@app.route('/api/journal/entries', methods=['GET'])
@token_required
def get_journal_entries(current_user):
    """Get journal entries for current user with filtering options"""
    try:
        db = get_unified_database()
        if not db:
            return jsonify({'error': 'Database connection failed'}), 500
        
        # Get query parameters for filtering
        bow_setup_id = request.args.get('bow_setup_id', type=int)
        linked_equipment = request.args.get('linked_equipment', type=int)
        linked_arrow = request.args.get('linked_arrow', type=int)
        entry_type = request.args.get('entry_type')
        search_query = request.args.get('search')
        tags = request.args.get('tags')  # Comma-separated tags
        has_session_data = request.args.get('has_session_data', type=bool)
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Build the WHERE clause
        where_conditions = ['je.user_id = ?']
        params = [current_user['id']]
        
        if bow_setup_id:
            where_conditions.append('je.bow_setup_id = ?')
            params.append(bow_setup_id)
        
        if linked_equipment:
            where_conditions.append('''
                je.id IN (
                    SELECT jer.journal_entry_id 
                    FROM journal_equipment_references jer 
                    WHERE jer.bow_equipment_id = ?
                )
            ''')
            params.append(linked_equipment)
        
        if linked_arrow:
            where_conditions.append('''
                je.id IN (
                    SELECT jer.journal_entry_id 
                    FROM journal_equipment_references jer 
                    WHERE jer.arrow_id = ?
                )
            ''')
            params.append(linked_arrow)
        
        
        if entry_type:
            where_conditions.append('je.entry_type = ?')
            params.append(entry_type)
        
        if has_session_data:
            where_conditions.append('je.session_metadata IS NOT NULL')
            where_conditions.append('je.session_metadata != ""')
        
        # Full-text search if query provided
        if search_query:
            where_conditions.append('je.id IN (SELECT rowid FROM journal_fts WHERE journal_fts MATCH ?)')
            params.append(search_query)
        
        # Tag filtering - check if any provided tag is in the JSON array
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
            tag_conditions = []
            for tag in tag_list:
                tag_conditions.append('je.tags LIKE ?')
                params.append(f'%"{tag}"%')
            if tag_conditions:
                where_conditions.append(f'({" OR ".join(tag_conditions)})')
        
        where_clause = ' AND '.join(where_conditions)
        offset = (page - 1) * limit
        
        # Get entries with setup information
        query = f'''
            SELECT 
                je.*,
                bs.name as setup_name,
                bs.bow_type,
                (SELECT COUNT(*) FROM journal_attachments ja WHERE ja.journal_entry_id = je.id) as attachment_count,
                (SELECT ja.cdn_url FROM journal_attachments ja WHERE ja.journal_entry_id = je.id AND ja.is_primary = 1 LIMIT 1) as primary_image_url
            FROM journal_entries je
            LEFT JOIN bow_setups bs ON je.bow_setup_id = bs.id
            WHERE {where_clause}
            ORDER BY je.created_at DESC
            LIMIT ? OFFSET ?
        '''
        
        cursor.execute(query, params + [limit, offset])
        entries = []
        
        for row in cursor.fetchall():
            entry = dict(row)
            # Parse tags JSON
            if entry['tags']:
                try:
                    entry['tags'] = json.loads(entry['tags'])
                except:
                    entry['tags'] = []
            else:
                entry['tags'] = []
            
            # Parse session metadata JSON
            if entry.get('session_metadata'):
                try:
                    if isinstance(entry['session_metadata'], str):
                        entry['session_metadata'] = json.loads(entry['session_metadata'])
                except:
                    entry['session_metadata'] = None
            
            # Get images for this entry
            cursor.execute('''
                SELECT cdn_url, description, original_filename, created_at
                FROM journal_attachments 
                WHERE journal_entry_id = ? AND file_type = 'image'
                ORDER BY is_primary DESC, created_at ASC
            ''', (entry['id'],))
            
            images = []
            for img_row in cursor.fetchall():
                images.append({
                    'url': img_row['cdn_url'],
                    'alt': img_row['description'] or img_row['original_filename'],
                    'uploadedAt': img_row['created_at']
                })
            entry['images'] = images
            
            entries.append(entry)
        
        # Get total count for pagination
        count_query = f'SELECT COUNT(*) as total FROM journal_entries je WHERE {where_clause}'
        cursor.execute(count_query, params)  # Use original params (limit/offset were added separately)
        total_count = cursor.fetchone()['total']
        
        conn.close()
        
        return jsonify({
            'entries': entries,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total_count,
                'pages': (total_count + limit - 1) // limit
            }
        })
        
    except Exception as e:
        print(f"Error fetching journal entries: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to fetch journal entries'}), 500

@app.route('/api/journal/entries', methods=['POST'])
@token_required
def create_journal_entry(current_user):
    """Create a new journal entry"""
    try:
        data = request.get_json()
        
        # Validation
        if not data.get('title') or not data.get('content'):
            return jsonify({'error': 'Title and content are required'}), 400
        
        db = get_unified_database()
        if not db:
            return jsonify({'error': 'Database connection failed'}), 500
        
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Validate bow setup belongs to user if provided
        if data.get('bow_setup_id'):
            cursor.execute('SELECT id FROM bow_setups WHERE id = ? AND user_id = ?', 
                         (data['bow_setup_id'], current_user['id']))
            if not cursor.fetchone():
                return jsonify({'error': 'Invalid bow setup'}), 400
        
        # Create journal entry
        tags_json = json.dumps(data.get('tags', [])) if data.get('tags') else None
        
        # Handle session metadata - accept both session_data (from frontend) and session_metadata
        session_metadata = None
        if data.get('session_data'):
            session_metadata = json.dumps(data['session_data']) if isinstance(data['session_data'], dict) else data['session_data']
        elif data.get('session_metadata'):
            session_metadata = json.dumps(data['session_metadata']) if isinstance(data['session_metadata'], dict) else data['session_metadata']
        
        # Extract arrow_id from linked_arrow if provided
        arrow_id = None
        if data.get('linked_arrow'):
            if isinstance(data['linked_arrow'], int):
                arrow_id = data['linked_arrow']
            elif isinstance(data['linked_arrow'], list) and len(data['linked_arrow']) > 0:
                arrow_id = data['linked_arrow'][0]  # Use first arrow if multiple

        cursor.execute('''
            INSERT INTO journal_entries 
            (user_id, bow_setup_id, title, content, entry_type, tags, is_private, 
             session_metadata, session_type, session_quality_score, arrow_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            current_user['id'],
            data.get('bow_setup_id'),
            data['title'],
            data['content'],
            data.get('entry_type', 'general'),
            tags_json,
            data.get('is_private', False),
            session_metadata,
            data.get('session_type', 'general'),
            data.get('session_quality_score'),
            arrow_id
        ))
        
        entry_id = cursor.lastrowid
        
        # Handle image attachments if provided
        if data.get('images'):
            for i, image in enumerate(data['images']):
                cursor.execute('''
                    INSERT INTO journal_attachments 
                    (journal_entry_id, filename, original_filename, file_type, 
                     file_path, file_size, mime_type, cdn_url, description, is_primary)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    entry_id,
                    f"journal_image_{entry_id}_{i}",
                    image.get('alt', f'Journal image {i+1}'),
                    'image',
                    image['url'],  # Use CDN URL as file_path for now
                    image.get('file_size', 0),  # Default to 0 if not provided
                    image.get('mime_type', 'image/jpeg'),  # Default mime type
                    image['url'],
                    image.get('alt', ''),
                    i == 0  # First image is primary
                ))
        
        # Handle equipment links if provided
        if data.get('linked_equipment'):
            if isinstance(data['linked_equipment'], int):
                # Simple equipment ID linking
                cursor.execute('''
                    INSERT INTO journal_equipment_references 
                    (journal_entry_id, bow_equipment_id, reference_type)
                    VALUES (?, ?, ?)
                ''', (entry_id, data['linked_equipment'], 'mentioned'))
            else:
                # Array of equipment IDs
                for equipment_id in data['linked_equipment']:
                    cursor.execute('''
                        INSERT INTO journal_equipment_references 
                        (journal_entry_id, bow_equipment_id, reference_type)
                        VALUES (?, ?, ?)
                    ''', (entry_id, equipment_id, 'mentioned'))
        
        # Handle arrow links if provided
        if data.get('linked_arrow'):
            if isinstance(data['linked_arrow'], int):
                # Simple arrow ID linking
                cursor.execute('''
                    INSERT INTO journal_equipment_references 
                    (journal_entry_id, arrow_id, reference_type)
                    VALUES (?, ?, ?)
                ''', (entry_id, data['linked_arrow'], 'mentioned'))
            else:
                # Array of arrow IDs
                for arrow_id in data['linked_arrow']:
                    cursor.execute('''
                        INSERT INTO journal_equipment_references 
                        (journal_entry_id, arrow_id, reference_type)
                        VALUES (?, ?, ?)
                    ''', (entry_id, arrow_id, 'mentioned'))
        
        # Handle change log links if provided
        if data.get('change_log_links'):
            for link in data['change_log_links']:
                cursor.execute('''
                    INSERT INTO journal_change_links 
                    (journal_entry_id, change_log_type, change_log_id, link_type)
                    VALUES (?, ?, ?, ?)
                ''', (
                    entry_id,
                    link['change_log_type'],
                    link['change_log_id'],
                    link.get('link_type', 'documents')
                ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': 'Journal entry created successfully',
            'entry_id': entry_id
        }), 201
        
    except Exception as e:
        print(f"Error creating journal entry: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to create journal entry'}), 500

@app.route('/api/journal/entries/<int:entry_id>', methods=['GET'])
@token_required
def get_journal_entry(current_user, entry_id):
    """Get a specific journal entry with all related data"""
    try:
        db = get_unified_database()
        if not db:
            return jsonify({'error': 'Database connection failed'}), 500
        
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Get entry with setup info
        cursor.execute('''
            SELECT 
                je.*,
                bs.name as setup_name,
                bs.bow_type
            FROM journal_entries je
            LEFT JOIN bow_setups bs ON je.bow_setup_id = bs.id
            WHERE je.id = ? AND je.user_id = ?
        ''', (entry_id, current_user['id']))
        
        entry_row = cursor.fetchone()
        if not entry_row:
            return jsonify({'error': 'Journal entry not found'}), 404
        
        entry = dict(entry_row)
        
        # Parse tags
        if entry['tags']:
            try:
                entry['tags'] = json.loads(entry['tags'])
            except:
                entry['tags'] = []
        else:
            entry['tags'] = []
        
        # Get attachments
        cursor.execute('''
            SELECT * FROM journal_attachments 
            WHERE journal_entry_id = ? 
            ORDER BY is_primary DESC, created_at ASC
        ''', (entry_id,))
        attachments = [dict(row) for row in cursor.fetchall()]
        entry['attachments'] = attachments
        
        # Convert image attachments to the format expected by frontend
        entry['images'] = []
        for attachment in attachments:
            if attachment['file_type'] == 'image' and attachment['cdn_url']:
                entry['images'].append({
                    'url': attachment['cdn_url'],
                    'alt': attachment['description'] or attachment['original_filename'],
                    'uploadedAt': attachment['created_at']
                })
        
        # Get equipment links (new schema from migration 043)
        cursor.execute('''
            SELECT * FROM equipment_journal_links 
            WHERE journal_entry_id = ?
            ORDER BY created_at ASC
        ''', (entry_id,))
        entry['equipment_links'] = [dict(row) for row in cursor.fetchall()]
        
        # Legacy equipment references (fallback for old entries)
        cursor.execute('''
            SELECT 
                jer.*,
                be.manufacturer_name, be.model_name, be.category_name,
                a.manufacturer as arrow_manufacturer, a.model_name as arrow_model
            FROM journal_equipment_references jer
            LEFT JOIN bow_equipment be ON jer.bow_equipment_id = be.id
            LEFT JOIN arrows a ON jer.arrow_id = a.id
            WHERE jer.journal_entry_id = ?
        ''', (entry_id,))
        legacy_refs = [dict(row) for row in cursor.fetchall()]
        entry['equipment_references'] = legacy_refs
        
        # Get change log links
        cursor.execute('''
            SELECT * FROM journal_change_links 
            WHERE journal_entry_id = ?
            ORDER BY created_at ASC
        ''', (entry_id,))
        entry['change_log_links'] = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({'entry': entry})
        
    except Exception as e:
        print(f"Error fetching journal entry: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to fetch journal entry'}), 500

@app.route('/api/journal/entries/<int:entry_id>', methods=['PUT'])
@token_required
def update_journal_entry(current_user, entry_id):
    """Update an existing journal entry"""
    try:
        data = request.get_json()
        
        db = get_unified_database()
        if not db:
            return jsonify({'error': 'Database connection failed'}), 500
        
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Verify ownership
        cursor.execute('SELECT id FROM journal_entries WHERE id = ? AND user_id = ?', 
                      (entry_id, current_user['id']))
        if not cursor.fetchone():
            return jsonify({'error': 'Journal entry not found'}), 404
        
        # Update journal entry
        update_fields = []
        params = []
        
        if 'title' in data:
            update_fields.append('title = ?')
            params.append(data['title'])
        
        if 'content' in data:
            update_fields.append('content = ?')
            params.append(data['content'])
        
        if 'entry_type' in data:
            update_fields.append('entry_type = ?')
            params.append(data['entry_type'])
        
        if 'tags' in data:
            update_fields.append('tags = ?')
            params.append(json.dumps(data['tags']) if data['tags'] else None)
        
        if 'is_private' in data:
            update_fields.append('is_private = ?')
            params.append(data['is_private'])
        
        # Handle image updates if provided
        if 'images' in data:
            # Remove existing image attachments
            cursor.execute('DELETE FROM journal_attachments WHERE journal_entry_id = ? AND file_type = ?', 
                         (entry_id, 'image'))
            
            # Add new image attachments
            for i, image in enumerate(data['images']):
                cursor.execute('''
                    INSERT INTO journal_attachments 
                    (journal_entry_id, filename, original_filename, file_type, 
                     file_path, file_size, mime_type, cdn_url, description, is_primary)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    entry_id,
                    f"journal_image_{entry_id}_{i}",
                    image.get('alt', f'Journal image {i+1}'),
                    'image',
                    image['url'],  # Use CDN URL as file_path for now
                    image.get('file_size', 0),  # Default to 0 if not provided
                    image.get('mime_type', 'image/jpeg'),  # Default mime type
                    image['url'],
                    image.get('alt', ''),
                    i == 0  # First image is primary
                ))
        
        if update_fields:
            update_fields.append('updated_at = CURRENT_TIMESTAMP')
            params.append(entry_id)
            
            cursor.execute(f'''
                UPDATE journal_entries 
                SET {', '.join(update_fields)}
                WHERE id = ?
            ''', params)
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Journal entry updated successfully'})
        
    except Exception as e:
        print(f"Error updating journal entry: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to update journal entry'}), 500

@app.route('/api/journal/entries/<int:entry_id>', methods=['DELETE'])
@token_required
def delete_journal_entry(current_user, entry_id):
    """Delete a journal entry and all related data"""
    try:
        db = get_unified_database()
        if not db:
            return jsonify({'error': 'Database connection failed'}), 500
        
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Verify ownership
        cursor.execute('SELECT id FROM journal_entries WHERE id = ? AND user_id = ?', 
                      (entry_id, current_user['id']))
        if not cursor.fetchone():
            return jsonify({'error': 'Journal entry not found'}), 404
        
        # Delete entry (cascading will handle related tables)
        cursor.execute('DELETE FROM journal_entries WHERE id = ?', (entry_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Journal entry deleted successfully'})
        
    except Exception as e:
        print(f"Error deleting journal entry: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to delete journal entry'}), 500

@app.route('/api/journal/search', methods=['GET'])
@token_required
def search_journal_entries(current_user):
    """Full-text search journal entries"""
    try:
        search_query = request.args.get('q')
        if not search_query:
            return jsonify({'error': 'Search query is required'}), 400
        
        bow_setup_id = request.args.get('bow_setup_id', type=int)
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        
        db = get_unified_database()
        if not db:
            return jsonify({'error': 'Database connection failed'}), 500
        
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Build search parameters
        where_conditions = ['je.user_id = ?', 'je.id IN (SELECT rowid FROM journal_fts WHERE journal_fts MATCH ?)']
        params = [current_user['id'], search_query]
        
        if bow_setup_id:
            where_conditions.append('je.bow_setup_id = ?')
            params.append(bow_setup_id)
        
        where_clause = ' AND '.join(where_conditions)
        offset = (page - 1) * limit
        
        # Search entries with ranking
        cursor.execute(f'''
            SELECT 
                je.*,
                bs.name as setup_name,
                bs.bow_type,
                rank
            FROM journal_entries je
            LEFT JOIN bow_setups bs ON je.bow_setup_id = bs.id
            JOIN (
                SELECT rowid, rank 
                FROM journal_fts 
                WHERE journal_fts MATCH ?
                ORDER BY rank
            ) fts ON je.id = fts.rowid
            WHERE {where_clause}
            ORDER BY fts.rank, je.created_at DESC
            LIMIT ? OFFSET ?
        ''', [search_query] + params + [limit, offset])
        
        entries = []
        for row in cursor.fetchall():
            entry = dict(row)
            if entry['tags']:
                try:
                    entry['tags'] = json.loads(entry['tags'])
                except:
                    entry['tags'] = []
            else:
                entry['tags'] = []
            entries.append(entry)
        
        conn.close()
        
        return jsonify({
            'entries': entries,
            'search_query': search_query,
            'pagination': {
                'page': page,
                'limit': limit
            }
        })
        
    except Exception as e:
        print(f"Error searching journal entries: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to search journal entries'}), 500

@app.route('/api/journal/tags', methods=['GET'])
@token_required
def get_journal_tags(current_user):
    """Get all unique tags used by the current user"""
    try:
        db = get_unified_database()
        if not db:
            return jsonify({'error': 'Database connection failed'}), 500
        
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT tags FROM journal_entries 
            WHERE user_id = ? AND tags IS NOT NULL AND tags != ''
        ''', (current_user['id'],))
        
        all_tags = set()
        for row in cursor.fetchall():
            try:
                tags = json.loads(row[0])
                if isinstance(tags, list):
                    all_tags.update(tags)
            except:
                continue
        
        conn.close()
        
        return jsonify({'tags': sorted(list(all_tags))})
        
    except Exception as e:
        print(f"Error fetching journal tags: {e}")
        return jsonify({'error': 'Failed to fetch tags'}), 500

@app.route('/api/journal/entry-types', methods=['GET'])
def get_journal_entry_types():
    """Get available journal entry types"""
    entry_types = [
        {'value': 'general', 'label': 'General Entry', 'description': 'General observations and notes'},
        {'value': 'setup_change', 'label': 'Setup Change', 'description': 'Changes to bow setup configuration'},
        {'value': 'equipment_change', 'label': 'Equipment Change', 'description': 'Equipment additions, removals, or modifications'},
        {'value': 'arrow_change', 'label': 'Arrow Change', 'description': 'Arrow changes and tuning'},
        {'value': 'tuning_session', 'label': 'Tuning Session', 'description': 'Detailed tuning session notes'},
        {'value': 'shooting_notes', 'label': 'Shooting Notes', 'description': 'Performance observations and shooting notes'},
        {'value': 'maintenance', 'label': 'Maintenance', 'description': 'Equipment maintenance activities'},
        {'value': 'upgrade', 'label': 'Upgrade', 'description': 'Equipment upgrades and improvements'}
    ]
    
    return jsonify({'entry_types': entry_types})

@app.route('/api/journal/templates', methods=['GET'])
@token_required
def get_journal_templates(current_user):
    """Get available journal templates"""
    try:
        db = get_unified_db()
        cursor = db.cursor()
        
        # Get templates available to the current user (system templates + their own templates)
        cursor.execute('''
            SELECT id, name, description, category, template_data, is_system_template, 
                   is_public, usage_count, last_used_at, created_at, updated_at
            FROM journal_templates 
            WHERE is_system_template = TRUE 
               OR created_by = ?
               OR is_public = TRUE
            ORDER BY is_system_template DESC, usage_count DESC, created_at DESC
        ''', (current_user['id'],))
        
        templates = []
        for row in cursor.fetchall():
            template = {
                'id': row['id'],
                'name': row['name'],
                'description': row['description'],
                'category': row['category'],
                'template_data': row['template_data'],
                'is_system_template': bool(row['is_system_template']),
                'is_public': bool(row['is_public']),
                'usage_count': row['usage_count'] or 0,
                'last_used_at': row['last_used_at'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            }
            templates.append(template)
        
        return jsonify({
            'success': True,
            'data': {
                'templates': templates
            }
        })
        
    except Exception as e:
        print(f"Error getting journal templates: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to load journal templates'
        }), 500

@app.route('/api/journal/filter-presets', methods=['GET'])
@token_required
def get_filter_presets(current_user):
    """Get user's filter presets"""
    try:
        db = get_unified_db()
        cursor = db.cursor()
        
        cursor.execute('''
            SELECT id, name, filter_configuration, icon, is_default, created_at, updated_at
            FROM journal_filter_presets 
            WHERE user_id = ?
            ORDER BY is_default DESC, name ASC
        ''', (current_user['id'],))
        
        presets = []
        for row in cursor.fetchall():
            preset = {
                'id': row['id'],
                'name': row['name'],
                'filter_configuration': row['filter_configuration'],
                'icon': row['icon'] or 'fas fa-filter',
                'is_default': bool(row['is_default']),
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            }
            presets.append(preset)
        
        return jsonify({
            'success': True,
            'data': presets
        })
        
    except Exception as e:
        print(f"Error getting filter presets: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to load filter presets'
        }), 500

@app.route('/api/journal/filter-presets', methods=['POST'])
@token_required
def create_filter_preset(current_user):
    """Create a new filter preset"""
    try:
        data = request.get_json()
        
        if not data.get('name') or not data.get('filter_configuration'):
            return jsonify({'error': 'Name and filter configuration are required'}), 400
        
        db = get_unified_db()
        cursor = db.cursor()
        
        cursor.execute('''
            INSERT INTO journal_filter_presets 
            (user_id, name, filter_configuration, icon, is_default)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            current_user['id'],
            data['name'],
            data['filter_configuration'],
            data.get('icon', 'fas fa-filter'),
            data.get('is_default', False)
        ))
        
        preset_id = cursor.lastrowid
        db.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'id': preset_id,
                'message': 'Filter preset created successfully'
            }
        }), 201
        
    except Exception as e:
        print(f"Error creating filter preset: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to create filter preset'
        }), 500

@app.route('/api/change-log', methods=['GET'])
@token_required
def get_change_log_entries(current_user):
    """Get change log entries for the current user"""
    try:
        db = get_unified_db()
        cursor = db.cursor()
        
        # Get query parameters
        bow_setup_id = request.args.get('bow_setup_id')
        change_type = request.args.get('change_type')
        limit = min(int(request.args.get('limit', 50)), 100)
        offset = int(request.args.get('offset', 0))
        
        # Build query
        query = '''
            SELECT cle.*, bs.name as bow_setup_name
            FROM change_log_entries cle
            LEFT JOIN bow_setups bs ON cle.bow_setup_id = bs.id
            WHERE cle.user_id = ?
        '''
        params = [current_user['id']]
        
        if bow_setup_id:
            query += ' AND cle.bow_setup_id = ?'
            params.append(bow_setup_id)
            
        if change_type:
            query += ' AND cle.change_type = ?'
            params.append(change_type)
        
        query += ' ORDER BY cle.created_at DESC LIMIT ? OFFSET ?'
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        entries = []
        
        for row in cursor.fetchall():
            entry = {
                'id': row['id'],
                'user_id': row['user_id'],
                'bow_setup_id': row['bow_setup_id'],
                'bow_setup_name': row['bow_setup_name'],
                'change_type': row['change_type'],
                'change_category': row['change_category'],
                'item_type': row['item_type'],
                'item_name': row['item_name'],
                'old_value': json.loads(row['old_value']) if row['old_value'] else None,
                'new_value': json.loads(row['new_value']) if row['new_value'] else None,
                'reason': row['reason'],
                'notes': row['notes'],
                'created_at': row['created_at']
            }
            entries.append(entry)
        
        return jsonify({
            'success': True,
            'data': entries,
            'pagination': {
                'limit': limit,
                'offset': offset,
                'has_more': len(entries) == limit
            }
        })
        
    except Exception as e:
        print(f"Error getting change log entries: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to load change log entries'
        }), 500

@app.route('/api/change-log', methods=['POST'])
@token_required
def create_change_log_entry(current_user):
    """Create a new change log entry"""
    try:
        data = request.get_json()
        
        # Validation
        required_fields = ['change_type', 'change_category', 'item_type', 'item_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        db = get_unified_db()
        cursor = db.cursor()
        
        # Validate bow setup belongs to user if provided
        if data.get('bow_setup_id'):
            cursor.execute('SELECT id FROM bow_setups WHERE id = ? AND user_id = ?', 
                         (data['bow_setup_id'], current_user['id']))
            if not cursor.fetchone():
                return jsonify({'error': 'Invalid bow setup'}), 400
        
        # Create change log entry
        cursor.execute('''
            INSERT INTO change_log_entries 
            (user_id, bow_setup_id, change_type, change_category, item_type, 
             item_name, old_value, new_value, reason, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            current_user['id'],
            data.get('bow_setup_id'),
            data['change_type'],
            data['change_category'],
            data['item_type'],
            data['item_name'],
            json.dumps(data.get('old_value')) if data.get('old_value') else None,
            json.dumps(data.get('new_value')) if data.get('new_value') else None,
            data.get('reason'),
            data.get('notes')
        ))
        
        change_log_id = cursor.lastrowid
        db.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'id': change_log_id,
                'message': 'Change log entry created successfully'
            }
        }), 201
        
    except Exception as e:
        print(f"Error creating change log entry: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to create change log entry'
        }), 500

@app.route('/api/journal/entries/from-change-log', methods=['POST'])
@token_required
def create_journal_entry_from_change_log(current_user):
    """Create a journal entry from a change log event with automatic linking"""
    try:
        data = request.get_json()
        
        # Validation
        if not data.get('change_log_type') or not data.get('change_log_id'):
            return jsonify({'error': 'Change log type and ID are required'}), 400
        
        db = get_unified_database()
        if not db:
            return jsonify({'error': 'Database connection failed'}), 500
        
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Fetch the change log entry to generate title and content
        change_log_type = data['change_log_type']
        change_log_id = data['change_log_id']
        
        # Get change log details based on type
        change_details = None
        bow_setup_id = None
        
        if change_log_type == 'equipment':
            cursor.execute('''
                SELECT 
                    ecl.*,
                    be.manufacturer_name, be.model_name, be.category_name,
                    bs.id as bow_setup_id, bs.name as setup_name
                FROM equipment_change_log ecl
                LEFT JOIN bow_equipment be ON ecl.bow_equipment_id = be.id
                LEFT JOIN bow_setups bs ON be.bow_setup_id = bs.id
                WHERE ecl.id = ? AND ecl.user_id = ?
            ''', (change_log_id, current_user['id']))
            
        elif change_log_type == 'setup':
            cursor.execute('''
                SELECT 
                    scl.*,
                    bs.id as bow_setup_id, bs.name as setup_name
                FROM setup_change_log scl
                LEFT JOIN bow_setups bs ON scl.bow_setup_id = bs.id
                WHERE scl.id = ? AND scl.user_id = ?
            ''', (change_log_id, current_user['id']))
            
        elif change_log_type == 'arrow':
            cursor.execute('''
                SELECT 
                    acl.*,
                    sa.setup_id as bow_setup_id,
                    bs.name as setup_name,
                    a.manufacturer, a.model_name
                FROM arrow_change_log acl
                LEFT JOIN setup_arrows sa ON acl.setup_arrow_id = sa.id
                LEFT JOIN bow_setups bs ON sa.setup_id = bs.id
                LEFT JOIN arrows a ON sa.arrow_id = a.id
                WHERE acl.id = ? AND acl.user_id = ?
            ''', (change_log_id, current_user['id']))
        
        change_details = cursor.fetchone()
        if not change_details:
            return jsonify({'error': 'Change log entry not found'}), 404
        
        bow_setup_id = change_details['bow_setup_id']
        
        # Generate automatic title and content based on change log type
        if change_log_type == 'equipment':
            equipment_name = f"{change_details['manufacturer_name']} {change_details['model_name']}"
            title = f"Equipment Change: {equipment_name}"
            content = f"""Equipment Change Documentation

**Equipment:** {equipment_name} ({change_details['category_name']})
**Change Type:** {change_details['change_type'].title()}
**Date:** {change_details['created_at']}

**Change Details:**
{change_details['change_description'] or 'No description provided'}

**Reason:** {change_details['change_reason'] or 'No reason specified'}

**Field Changes:**
"""
            if change_details['field_name']:
                content += f"- **{change_details['field_name']}:** {change_details['old_value']} → {change_details['new_value']}\n"
            
            entry_type = 'equipment_change'
            tags = ['equipment', change_details['change_type'], change_details['category_name'].lower()]
            
        elif change_log_type == 'setup':
            title = f"Setup Change: {change_details['setup_name']}"
            content = f"""Setup Change Documentation

**Setup:** {change_details['setup_name']}
**Change Type:** {change_details['change_type'].title()}
**Date:** {change_details['created_at']}

**Change Details:**
{change_details['change_description'] or 'No description provided'}

**Field Changes:**
"""
            if change_details['field_name']:
                content += f"- **{change_details['field_name']}:** {change_details['old_value']} → {change_details['new_value']}\n"
            
            entry_type = 'setup_change'
            tags = ['setup', change_details['change_type']]
            
        elif change_log_type == 'arrow':
            arrow_name = f"{change_details['manufacturer']} {change_details['model_name']}"
            title = f"Arrow Change: {arrow_name}"
            content = f"""Arrow Change Documentation

**Arrow:** {arrow_name}
**Setup:** {change_details['setup_name']}
**Change Type:** {change_details['change_type'].title()}
**Date:** {change_details['created_at']}

**Change Details:**
{change_details['change_description'] or 'No description provided'}

**Reason:** {change_details['change_reason'] or 'No reason specified'}

**Field Changes:**
"""
            if change_details['field_name']:
                content += f"- **{change_details['field_name']}:** {change_details['old_value']} → {change_details['new_value']}\n"
            
            entry_type = 'arrow_change'
            tags = ['arrow', change_details['change_type']]
        
        # Add user-provided content if any
        if data.get('additional_notes'):
            content += f"\n\n**Additional Notes:**\n{data['additional_notes']}"
        
        # Add user-provided tags
        if data.get('additional_tags'):
            tags.extend(data['additional_tags'])
        
        # Create the journal entry
        cursor.execute('''
            INSERT INTO journal_entries 
            (user_id, bow_setup_id, title, content, entry_type, tags)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            current_user['id'],
            bow_setup_id,
            title,
            content,
            entry_type,
            json.dumps(tags)
        ))
        
        journal_entry_id = cursor.lastrowid
        
        # Create the change log link
        cursor.execute('''
            INSERT INTO journal_change_links 
            (journal_entry_id, change_log_type, change_log_id, link_type)
            VALUES (?, ?, ?, 'documents')
        ''', (journal_entry_id, change_log_type, change_log_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': 'Journal entry created from change log successfully',
            'journal_entry_id': journal_entry_id
        }), 201
        
    except Exception as e:
        print(f"Error creating journal entry from change log: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to create journal entry from change log'}), 500

# Run the app
def clear_performance_cache():
    """Clear all cached performance data on server startup for fresh calculations"""
    try:
        db = get_database()
        if db:
            conn = db.get_connection()
            cursor = conn.cursor()
            
            # Clear performance_data cache for all setup_arrows
            cursor.execute('UPDATE setup_arrows SET performance_data = NULL WHERE performance_data IS NOT NULL')
            rows_cleared = cursor.rowcount
            conn.commit()
            conn.close()
            
            if rows_cleared > 0:
                print(f"🧹 Cleared cached performance data for {rows_cleared} arrow setups")
            else:
                print("🧹 No cached performance data found to clear")
        else:
            print("⚠️ Could not clear performance cache - database not available")
    except Exception as e:
        print(f"⚠️ Error clearing performance cache: {e}")

if __name__ == '__main__':
    port = int(os.environ.get('API_PORT', 5000))
    print(f"🚀 Starting ArrowTuner API on port {port}")
    print(f"🎯 Environment: {os.environ.get('NODE_ENV', 'development')}")
    print(f"📊 Arrow Database: {os.environ.get('ARROW_DATABASE_PATH', '/app/arrow_database.db')}")
    print(f"👤 User Database: {os.environ.get('USER_DATABASE_PATH', '/app/user_data/user_data.db')}")
    
    # Clear performance cache on startup for fresh calculations
    clear_performance_cache()
    
    app.run(host='0.0.0.0', port=port, debug=False)

