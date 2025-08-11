#!/usr/bin/env python3
"""
Spine Calculation Data Migration Script

This script creates the database schema for storing comprehensive spine calculation data
from archery_spine_catalog_complete.json, including formulas, material properties,
manufacturer spine charts, and tuning guidelines.
"""

import sqlite3
import json
from pathlib import Path
from arrow_database import ArrowDatabase

def create_spine_calculation_tables():
    """Create tables for spine calculation data"""
    db = ArrowDatabase()
    conn = None
    
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        print("🔧 Creating spine calculation data tables...")
        
        # Table 1: Spine calculation formulas and base data
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS spine_calculation_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                subcategory TEXT,
                parameter_name TEXT NOT NULL,
                parameter_value TEXT NOT NULL,
                data_type TEXT NOT NULL DEFAULT 'string',
                description TEXT,
                unit TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(category, subcategory, parameter_name)
            )
        """)
        
        # Table 2: Material properties for different arrow materials
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS arrow_material_properties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                material_name TEXT UNIQUE NOT NULL,
                density REAL,
                elasticity_modulus REAL,
                strength_factor REAL,
                spine_adjustment_factor REAL,
                temperature_coefficient REAL,
                humidity_resistance_rating INTEGER,
                description TEXT,
                typical_use TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table 3: Manufacturer-specific spine charts and recommendations
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS manufacturer_spine_charts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                manufacturer TEXT NOT NULL,
                bow_type TEXT NOT NULL,
                draw_weight_min REAL NOT NULL,
                draw_weight_max REAL NOT NULL,
                arrow_length_min REAL NOT NULL,
                arrow_length_max REAL NOT NULL,
                recommended_spine INTEGER NOT NULL,
                point_weight_range TEXT,
                confidence_rating INTEGER DEFAULT 85,
                notes TEXT,
                source_url TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table 4: Flight problem diagnostics and solutions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS flight_problem_diagnostics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                problem_category TEXT NOT NULL,
                problem_name TEXT NOT NULL,
                symptoms TEXT NOT NULL,
                root_causes TEXT NOT NULL,
                solutions TEXT NOT NULL,
                prevention_tips TEXT,
                difficulty_level TEXT DEFAULT 'intermediate',
                equipment_needed TEXT,
                safety_warnings TEXT,
                related_problems TEXT,
                success_indicators TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(problem_category, problem_name)
            )
        """)
        
        # Table 5: Tuning methodologies and step-by-step guides
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tuning_methodologies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                method_name TEXT UNIQUE NOT NULL,
                method_category TEXT NOT NULL,
                bow_types_applicable TEXT NOT NULL,
                skill_level_required TEXT DEFAULT 'intermediate',
                time_estimate_minutes INTEGER,
                equipment_needed TEXT,
                step_by_step_guide TEXT NOT NULL,
                expected_outcomes TEXT,
                troubleshooting_tips TEXT,
                safety_considerations TEXT,
                success_metrics TEXT,
                related_methods TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table 6: Calculation parameters that can be tuned by admins
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS calculation_parameters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parameter_group TEXT NOT NULL,
                parameter_name TEXT NOT NULL,
                parameter_value REAL NOT NULL,
                parameter_unit TEXT,
                description TEXT NOT NULL,
                min_value REAL,
                max_value REAL,
                default_value REAL,
                adjustment_increment REAL DEFAULT 0.1,
                requires_admin BOOLEAN DEFAULT 1,
                affects_calculation TEXT,
                last_modified_by INTEGER,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(parameter_group, parameter_name),
                FOREIGN KEY (last_modified_by) REFERENCES users (id) ON DELETE SET NULL
            )
        """)
        
        # Table 7: Component specifications and effects on spine
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS component_spine_effects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                component_type TEXT NOT NULL,
                component_name TEXT NOT NULL,
                weight_grams REAL,
                spine_effect_factor REAL DEFAULT 0.0,
                foc_contribution REAL DEFAULT 0.0,
                balance_point_shift REAL DEFAULT 0.0,
                aerodynamic_impact TEXT,
                compatibility_notes TEXT,
                manufacturer TEXT,
                typical_use TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        print("✅ Successfully created spine calculation data tables")
        
        # Create indexes for performance
        print("🔧 Creating performance indexes...")
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_spine_calc_category ON spine_calculation_data (category, subcategory)",
            "CREATE INDEX IF NOT EXISTS idx_material_properties_name ON arrow_material_properties (material_name)",
            "CREATE INDEX IF NOT EXISTS idx_manufacturer_bow_type ON manufacturer_spine_charts (manufacturer, bow_type)",
            "CREATE INDEX IF NOT EXISTS idx_draw_weight_range ON manufacturer_spine_charts (draw_weight_min, draw_weight_max)",
            "CREATE INDEX IF NOT EXISTS idx_spine_recommendation ON manufacturer_spine_charts (recommended_spine)",
            "CREATE INDEX IF NOT EXISTS idx_flight_problems_category ON flight_problem_diagnostics (problem_category)",
            "CREATE INDEX IF NOT EXISTS idx_tuning_methods_category ON tuning_methodologies (method_category, bow_types_applicable)",
            "CREATE INDEX IF NOT EXISTS idx_calc_params_group ON calculation_parameters (parameter_group, is_active)",
            "CREATE INDEX IF NOT EXISTS idx_component_type ON component_spine_effects (component_type)",
            "CREATE INDEX IF NOT EXISTS idx_weight_spine_effect ON component_spine_effects (weight_grams, spine_effect_factor)",
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
            
        conn.commit()
        print("✅ Successfully created performance indexes")
        
    except sqlite3.Error as e:
        print(f"❌ Error creating spine calculation tables: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def populate_default_calculation_parameters():
    """Populate default calculation parameters"""
    db = ArrowDatabase()
    conn = None
    
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        print("🔧 Populating default calculation parameters...")
        
        default_params = [
            # Base calculation factors
            ("base_calculation", "draw_weight_factor", 12.5, "multiplier", "Base multiplier for draw weight in spine calculation", 10.0, 15.0, 12.5, 0.1),
            ("base_calculation", "length_adjustment_factor", 25.0, "spine/inch", "Spine adjustment per inch of arrow length deviation from 28\"", 15.0, 35.0, 25.0, 1.0),
            ("base_calculation", "point_weight_factor", 0.5, "spine/grain", "Spine adjustment per grain of point weight deviation from 125gr", 0.3, 0.8, 0.5, 0.05),
            
            # Bow type adjustments
            ("bow_adjustments", "recurve_spine_adjustment", 50.0, "spine", "Additional spine needed for recurve bows", 25.0, 75.0, 50.0, 5.0),
            ("bow_adjustments", "traditional_spine_adjustment", 100.0, "spine", "Additional spine needed for traditional bows", 75.0, 125.0, 100.0, 5.0),
            ("bow_adjustments", "compound_efficiency_factor", 1.0, "multiplier", "Efficiency factor for compound bows", 0.85, 1.15, 1.0, 0.05),
            
            # Safety factors
            ("safety_factors", "spine_tolerance_range", 25.0, "spine", "Acceptable spine deviation range (+/-)", 15.0, 40.0, 25.0, 5.0),
            ("safety_factors", "minimum_spine_safety_margin", 10.0, "spine", "Minimum safety margin for spine calculations", 5.0, 20.0, 10.0, 1.0),
            ("safety_factors", "maximum_point_weight_ratio", 0.15, "ratio", "Maximum point weight as ratio of arrow weight", 0.1, 0.25, 0.15, 0.01),
            
            # Material adjustments
            ("material_factors", "carbon_spine_consistency", 0.95, "multiplier", "Consistency factor for carbon arrows", 0.9, 1.0, 0.95, 0.01),
            ("material_factors", "aluminum_spine_consistency", 0.9, "multiplier", "Consistency factor for aluminum arrows", 0.85, 0.95, 0.9, 0.01),
            ("material_factors", "wood_spine_variability", 1.2, "multiplier", "Variability factor for wood arrows", 1.1, 1.4, 1.2, 0.05),
        ]
        
        for group, name, value, unit, desc, min_val, max_val, default, increment in default_params:
            cursor.execute("""
                INSERT OR IGNORE INTO calculation_parameters 
                (parameter_group, parameter_name, parameter_value, parameter_unit, description, 
                 min_value, max_value, default_value, adjustment_increment)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (group, name, value, unit, desc, min_val, max_val, default, increment))
        
        conn.commit()
        print("✅ Successfully populated default calculation parameters")
        
    except sqlite3.Error as e:
        print(f"❌ Error populating calculation parameters: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def populate_default_material_properties():
    """Populate default arrow material properties"""
    db = ArrowDatabase()
    conn = None
    
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        print("🔧 Populating default material properties...")
        
        materials = [
            ("Carbon", 1.6, 230.0, 1.0, 1.0, 0.0001, 9, "High-performance carbon fiber arrows with excellent consistency", "Target and hunting"),
            ("Aluminum", 2.7, 69.0, 0.85, 0.95, 0.0002, 7, "Durable aluminum arrows with good straightness", "Target and recreational"),
            ("Carbon/Aluminum", 2.0, 150.0, 0.95, 0.98, 0.0001, 8, "Hybrid construction combining carbon and aluminum", "Hunting and target"),
            ("Wood", 0.6, 12.0, 0.7, 1.3, 0.001, 4, "Traditional wooden arrows with natural variability", "Traditional archery"),
            ("Fiberglass", 1.8, 38.0, 0.8, 1.1, 0.0003, 6, "Economic fiberglass arrows for beginners", "Recreational"),
        ]
        
        for name, density, elasticity, strength, spine_adj, temp_coeff, humidity, desc, use in materials:
            cursor.execute("""
                INSERT OR IGNORE INTO arrow_material_properties 
                (material_name, density, elasticity_modulus, strength_factor, spine_adjustment_factor,
                 temperature_coefficient, humidity_resistance_rating, description, typical_use)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, density, elasticity, strength, spine_adj, temp_coeff, humidity, desc, use))
        
        conn.commit()
        print("✅ Successfully populated default material properties")
        
    except sqlite3.Error as e:
        print(f"❌ Error populating material properties: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def main():
    """Main migration function"""
    print("🚀 Starting spine calculation data migration...")
    
    try:
        # Create tables
        create_spine_calculation_tables()
        
        # Populate default data
        populate_default_calculation_parameters()
        populate_default_material_properties()
        
        print("✅ Spine calculation data migration completed successfully!")
        print("📊 Created 7 new tables for comprehensive spine calculation data:")
        print("   - spine_calculation_data (formulas and base data)")
        print("   - arrow_material_properties (material specifications)")
        print("   - manufacturer_spine_charts (brand-specific recommendations)")
        print("   - flight_problem_diagnostics (troubleshooting guide)")
        print("   - tuning_methodologies (step-by-step tuning guides)")
        print("   - calculation_parameters (admin-configurable values)")
        print("   - component_spine_effects (component impact on spine)")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()