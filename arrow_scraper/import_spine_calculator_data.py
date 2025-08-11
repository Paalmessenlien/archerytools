#!/usr/bin/env python3
"""
Import Spine Calculator Data from JSON

This script imports the comprehensive spine calculator data from 
archery_spine_catalog_complete.json into the database tables created 
by the migration script.
"""

import sqlite3
import json
from pathlib import Path
from arrow_database import ArrowDatabase

def load_spine_calculator_json():
    """Load the spine calculator JSON data"""
    # Try sample file first, then fall back to main file
    sample_path = Path(__file__).parent / "spine_data_sample.json"
    main_path = Path(__file__).parent / "spinecalculatordata" / "archery_spine_catalog_complete.json"
    
    for json_path in [sample_path, main_path]:
        if json_path.exists():
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"✅ Loaded spine calculator JSON data from: {json_path}")
                return data
            except Exception as e:
                print(f"⚠️ Error loading {json_path}: {e}")
                continue
    
    print("❌ No valid JSON file found")
    return None

def import_spine_calculation_formulas(data, conn):
    """Import spine calculation formulas and base data"""
    cursor = conn.cursor()
    
    print("🔧 Importing spine calculation formulas...")
    
    # Import calculation formulas
    if 'calculation_formulas' in data:
        for category, formulas in data['calculation_formulas'].items():
            if isinstance(formulas, dict):
                for formula_name, formula_data in formulas.items():
                    if isinstance(formula_data, dict):
                        for param_name, param_value in formula_data.items():
                            cursor.execute("""
                                INSERT OR REPLACE INTO spine_calculation_data
                                (category, subcategory, parameter_name, parameter_value, data_type, description)
                                VALUES (?, ?, ?, ?, ?, ?)
                            """, (category, formula_name, param_name, str(param_value), 
                                 type(param_value).__name__, f"Formula parameter for {formula_name}"))
                    else:
                        cursor.execute("""
                            INSERT OR REPLACE INTO spine_calculation_data
                            (category, parameter_name, parameter_value, data_type, description)
                            VALUES (?, ?, ?, ?, ?)
                        """, (category, formula_name, str(formula_data), 
                             type(formula_data).__name__, f"Formula value for {category}"))
    
    # Import spine adjustment formulas
    if 'spine_adjustments' in data:
        for adj_type, adjustment_data in data['spine_adjustments'].items():
            if isinstance(adjustment_data, dict):
                for param_name, param_value in adjustment_data.items():
                    cursor.execute("""
                        INSERT OR REPLACE INTO spine_calculation_data
                        (category, subcategory, parameter_name, parameter_value, data_type, description)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, ("spine_adjustments", adj_type, param_name, str(param_value),
                         type(param_value).__name__, f"Spine adjustment parameter for {adj_type}"))
    
    conn.commit()
    print("✅ Successfully imported spine calculation formulas")

def import_material_properties(data, conn):
    """Import enhanced material properties"""
    cursor = conn.cursor()
    
    print("🔧 Importing material properties...")
    
    if 'materials' in data:
        for material_name, material_data in data['materials'].items():
            if isinstance(material_data, dict):
                cursor.execute("""
                    INSERT OR REPLACE INTO arrow_material_properties
                    (material_name, density, elasticity_modulus, strength_factor, spine_adjustment_factor,
                     temperature_coefficient, humidity_resistance_rating, description, typical_use)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    material_name,
                    material_data.get('density', 1.0),
                    material_data.get('elasticity_modulus', 100.0),
                    material_data.get('strength_factor', 1.0),
                    material_data.get('spine_adjustment_factor', 1.0),
                    material_data.get('temperature_coefficient', 0.0001),
                    material_data.get('humidity_resistance_rating', 5),
                    material_data.get('description', f'Properties for {material_name} arrows'),
                    material_data.get('typical_use', 'General use')
                ))
    
    conn.commit()
    print("✅ Successfully imported material properties")

def import_manufacturer_spine_charts(data, conn):
    """Import manufacturer-specific spine charts"""
    cursor = conn.cursor()
    
    print("🔧 Importing manufacturer spine charts...")
    
    if 'manufacturer_charts' in data:
        for manufacturer, bow_types in data['manufacturer_charts'].items():
            if isinstance(bow_types, dict):
                for bow_type, spine_data in bow_types.items():
                    if isinstance(spine_data, list):
                        for chart_entry in spine_data:
                            if isinstance(chart_entry, dict):
                                cursor.execute("""
                                    INSERT OR REPLACE INTO manufacturer_spine_charts
                                    (manufacturer, bow_type, draw_weight_min, draw_weight_max,
                                     arrow_length_min, arrow_length_max, recommended_spine,
                                     point_weight_range, confidence_rating, notes)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    manufacturer,
                                    bow_type,
                                    chart_entry.get('draw_weight_min', 20),
                                    chart_entry.get('draw_weight_max', 70),
                                    chart_entry.get('arrow_length_min', 26),
                                    chart_entry.get('arrow_length_max', 32),
                                    chart_entry.get('recommended_spine', 500),
                                    chart_entry.get('point_weight_range', '100-150gr'),
                                    chart_entry.get('confidence_rating', 85),
                                    chart_entry.get('notes', '')
                                ))
    
    conn.commit()
    print("✅ Successfully imported manufacturer spine charts")

def import_flight_problem_diagnostics(data, conn):
    """Import flight problem diagnostics and solutions"""
    cursor = conn.cursor()
    
    print("🔧 Importing flight problem diagnostics...")
    
    if 'flight_problems' in data:
        for problem_category, problems in data['flight_problems'].items():
            if isinstance(problems, dict):
                for problem_name, problem_data in problems.items():
                    if isinstance(problem_data, dict):
                        cursor.execute("""
                            INSERT OR REPLACE INTO flight_problem_diagnostics
                            (problem_category, problem_name, symptoms, root_causes, solutions,
                             prevention_tips, difficulty_level, equipment_needed, safety_warnings)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            problem_category,
                            problem_name,
                            problem_data.get('symptoms', ''),
                            problem_data.get('root_causes', ''),
                            problem_data.get('solutions', ''),
                            problem_data.get('prevention_tips', ''),
                            problem_data.get('difficulty_level', 'intermediate'),
                            problem_data.get('equipment_needed', ''),
                            problem_data.get('safety_warnings', '')
                        ))
    
    conn.commit()
    print("✅ Successfully imported flight problem diagnostics")

def import_tuning_methodologies(data, conn):
    """Import tuning methodologies and guides"""
    cursor = conn.cursor()
    
    print("🔧 Importing tuning methodologies...")
    
    if 'tuning_methods' in data:
        for method_category, methods in data['tuning_methods'].items():
            if isinstance(methods, dict):
                for method_name, method_data in methods.items():
                    if isinstance(method_data, dict):
                        cursor.execute("""
                            INSERT OR REPLACE INTO tuning_methodologies
                            (method_name, method_category, bow_types_applicable, skill_level_required,
                             time_estimate_minutes, equipment_needed, step_by_step_guide,
                             expected_outcomes, troubleshooting_tips, safety_considerations)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            method_name,
                            method_category,
                            method_data.get('bow_types_applicable', 'compound,recurve'),
                            method_data.get('skill_level_required', 'intermediate'),
                            method_data.get('time_estimate_minutes', 30),
                            method_data.get('equipment_needed', ''),
                            method_data.get('step_by_step_guide', ''),
                            method_data.get('expected_outcomes', ''),
                            method_data.get('troubleshooting_tips', ''),
                            method_data.get('safety_considerations', '')
                        ))
    
    conn.commit()
    print("✅ Successfully imported tuning methodologies")

def import_component_spine_effects(data, conn):
    """Import component effects on spine calculations"""
    cursor = conn.cursor()
    
    print("🔧 Importing component spine effects...")
    
    if 'components' in data:
        for component_type, components in data['components'].items():
            if isinstance(components, dict):
                for component_name, component_data in components.items():
                    if isinstance(component_data, dict):
                        cursor.execute("""
                            INSERT OR REPLACE INTO component_spine_effects
                            (component_type, component_name, weight_grams, spine_effect_factor,
                             foc_contribution, balance_point_shift, aerodynamic_impact,
                             compatibility_notes, manufacturer, typical_use)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            component_type,
                            component_name,
                            component_data.get('weight_grams', 0.0),
                            component_data.get('spine_effect_factor', 0.0),
                            component_data.get('foc_contribution', 0.0),
                            component_data.get('balance_point_shift', 0.0),
                            component_data.get('aerodynamic_impact', ''),
                            component_data.get('compatibility_notes', ''),
                            component_data.get('manufacturer', ''),
                            component_data.get('typical_use', '')
                        ))
    
    conn.commit()
    print("✅ Successfully imported component spine effects")

def import_general_spine_data(data, conn):
    """Import any remaining general spine calculation data"""
    cursor = conn.cursor()
    
    print("🔧 Importing general spine calculation data...")
    
    # Import any top-level data that doesn't fit in specific categories
    excluded_keys = {'calculation_formulas', 'spine_adjustments', 'materials', 
                    'manufacturer_charts', 'flight_problems', 'tuning_methods', 'components'}
    
    for key, value in data.items():
        if key not in excluded_keys:
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    cursor.execute("""
                        INSERT OR REPLACE INTO spine_calculation_data
                        (category, subcategory, parameter_name, parameter_value, data_type, description)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (key, 'general', sub_key, str(sub_value), 
                         type(sub_value).__name__, f"General data for {key}"))
            else:
                cursor.execute("""
                    INSERT OR REPLACE INTO spine_calculation_data
                    (category, parameter_name, parameter_value, data_type, description)
                    VALUES (?, ?, ?, ?, ?)
                """, (key, 'value', str(value), type(value).__name__, f"General value for {key}"))
    
    conn.commit()
    print("✅ Successfully imported general spine calculation data")

def get_import_statistics(conn):
    """Get statistics about imported data"""
    cursor = conn.cursor()
    
    tables = [
        'spine_calculation_data',
        'arrow_material_properties', 
        'manufacturer_spine_charts',
        'flight_problem_diagnostics',
        'tuning_methodologies',
        'component_spine_effects'
    ]
    
    print("\n📊 Import Statistics:")
    total_records = 0
    
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        total_records += count
        print(f"   - {table}: {count} records")
    
    print(f"\n✅ Total records imported: {total_records}")

def main():
    """Main import function"""
    print("🚀 Starting spine calculator data import...")
    
    # Load JSON data
    data = load_spine_calculator_json()
    if not data:
        return False
    
    # Connect to database
    db = ArrowDatabase()
    conn = None
    
    try:
        conn = db.get_connection()
        
        # Import all data categories
        import_spine_calculation_formulas(data, conn)
        import_material_properties(data, conn)
        import_manufacturer_spine_charts(data, conn)
        import_flight_problem_diagnostics(data, conn)
        import_tuning_methodologies(data, conn)
        import_component_spine_effects(data, conn)
        import_general_spine_data(data, conn)
        
        # Show statistics
        get_import_statistics(conn)
        
        print("\n✅ Spine calculator data import completed successfully!")
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()
    
    return True

if __name__ == "__main__":
    main()