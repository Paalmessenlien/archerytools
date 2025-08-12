#!/usr/bin/env python3
"""
Spine Calculator Data Importer
Imports manufacturer spine charts, conversion tables, and calculation formulas from JSON files
"""

import json
import sqlite3
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

class SpineCalculatorDataImporter:
    def __init__(self, database_path: str = "arrow_database.db"):
        """Initialize the importer with database path"""
        self.database_path = database_path
        self.data_dir = Path(__file__).parent / "spinecalculatordata"
        
    def connect_db(self):
        """Create database connection"""
        return sqlite3.connect(self.database_path)
    
    def create_enhanced_spine_tables(self):
        """Create enhanced spine calculation tables"""
        with self.connect_db() as conn:
            cursor = conn.cursor()
            
            # Manufacturer spine charts table (enhanced version)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS manufacturer_spine_charts_enhanced (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    manufacturer TEXT NOT NULL,
                    model TEXT NOT NULL,
                    bow_type TEXT NOT NULL,
                    grid_definition TEXT, -- JSON: units, spine system, notes
                    spine_grid TEXT NOT NULL, -- JSON: array of spine data points
                    provenance TEXT, -- Source information
                    spine_system TEXT DEFAULT 'standard_deflection', -- carbon, wood_spine_range, aluminum, etc.
                    chart_notes TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(manufacturer, model, bow_type)
                )
            """)
            
            # Custom spine charts (admin-created overrides)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS custom_spine_charts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chart_name TEXT NOT NULL,
                    manufacturer TEXT,
                    model TEXT,
                    bow_type TEXT NOT NULL,
                    grid_definition TEXT, -- JSON: units, spine system, notes
                    spine_grid TEXT NOT NULL, -- JSON: array of spine data points
                    spine_system TEXT DEFAULT 'standard_deflection',
                    chart_notes TEXT,
                    created_by TEXT, -- admin user
                    overrides_manufacturer_chart BOOLEAN DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Spine conversion tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS spine_conversion_tables (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversion_type TEXT NOT NULL, -- carbon_to_aluminum, wood_to_carbon, etc.
                    from_spine TEXT NOT NULL,
                    to_spine TEXT NOT NULL,
                    accuracy_note TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Weight and length conversion factors
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS unit_conversions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversion_category TEXT NOT NULL, -- weight, length, diameter
                    from_unit TEXT NOT NULL,
                    to_unit TEXT NOT NULL,
                    conversion_factor REAL NOT NULL,
                    formula TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Calculation adjustment formulas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS spine_calculation_adjustments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    adjustment_type TEXT NOT NULL, -- arrow_length, point_weight, bow_speed, etc.
                    formula TEXT NOT NULL,
                    description TEXT,
                    base_conditions TEXT, -- JSON: standard conditions this applies to
                    adjustment_examples TEXT, -- JSON: example calculations
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            print("✓ Enhanced spine calculation tables created successfully")
    
    def import_spine_charts(self):
        """Import manufacturer spine charts from spine_charts.json"""
        spine_charts_file = self.data_dir / "spine_charts.json"
        
        if not spine_charts_file.exists():
            print(f"❌ Spine charts file not found: {spine_charts_file}")
            return
        
        with open(spine_charts_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        spine_charts = data.get('spine_charts', [])
        print(f"📊 Importing {len(spine_charts)} spine charts...")
        
        with self.connect_db() as conn:
            cursor = conn.cursor()
            
            imported_count = 0
            skipped_count = 0
            
            for chart in spine_charts:
                try:
                    manufacturer = chart.get('manufacturer', '')
                    model = chart.get('model', '')
                    bow_type = chart.get('bow_type', 'compound')
                    grid_definition = json.dumps(chart.get('grid_definition', {}))
                    spine_grid = json.dumps(chart.get('spine_grid', []))
                    provenance = chart.get('provenance', '')
                    spine_system = chart.get('grid_definition', {}).get('spine_system', 'standard_deflection')
                    chart_notes = chart.get('grid_definition', {}).get('note', '')
                    
                    # Check if chart already exists
                    cursor.execute("""
                        SELECT id FROM manufacturer_spine_charts_enhanced 
                        WHERE manufacturer = ? AND model = ? AND bow_type = ?
                    """, (manufacturer, model, bow_type))
                    
                    if cursor.fetchone():
                        # Update existing chart
                        cursor.execute("""
                            UPDATE manufacturer_spine_charts_enhanced 
                            SET grid_definition = ?, spine_grid = ?, provenance = ?, 
                                spine_system = ?, chart_notes = ?, updated_at = CURRENT_TIMESTAMP
                            WHERE manufacturer = ? AND model = ? AND bow_type = ?
                        """, (grid_definition, spine_grid, provenance, spine_system, 
                             chart_notes, manufacturer, model, bow_type))
                        skipped_count += 1
                    else:
                        # Insert new chart
                        cursor.execute("""
                            INSERT INTO manufacturer_spine_charts_enhanced 
                            (manufacturer, model, bow_type, grid_definition, spine_grid, 
                             provenance, spine_system, chart_notes)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (manufacturer, model, bow_type, grid_definition, spine_grid,
                             provenance, spine_system, chart_notes))
                        imported_count += 1
                    
                except Exception as e:
                    print(f"❌ Error importing chart for {manufacturer} {model}: {e}")
                    continue
            
            conn.commit()
            print(f"✓ Imported {imported_count} new spine charts, updated {skipped_count} existing charts")
    
    def import_conversion_tables(self):
        """Import conversion tables from conversion_tables.json"""
        conversion_file = self.data_dir / "conversion_tables.json"
        
        if not conversion_file.exists():
            print(f"❌ Conversion tables file not found: {conversion_file}")
            return
        
        with open(conversion_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        conversion_tables = data.get('conversion_tables', {})
        print(f"🔄 Importing conversion tables...")
        
        with self.connect_db() as conn:
            cursor = conn.cursor()
            
            # Clear existing conversion data
            cursor.execute("DELETE FROM spine_conversion_tables")
            cursor.execute("DELETE FROM unit_conversions")
            
            # Import spine equivalents
            spine_equivalents = conversion_tables.get('spine_equivalents', {})
            
            # Carbon to aluminum conversions
            carbon_to_aluminum = spine_equivalents.get('carbon_to_aluminum_approximate', {})
            for carbon_spine, aluminum_spine in carbon_to_aluminum.items():
                cursor.execute("""
                    INSERT INTO spine_conversion_tables 
                    (conversion_type, from_spine, to_spine, accuracy_note)
                    VALUES (?, ?, ?, ?)
                """, ('carbon_to_aluminum', carbon_spine, aluminum_spine, 
                     'Approximate conversion - verify with manufacturer'))
            
            # Wood to carbon conversions
            wood_to_carbon = spine_equivalents.get('wood_spine_to_carbon_approximate', {})
            for wood_spine, carbon_spine in wood_to_carbon.items():
                cursor.execute("""
                    INSERT INTO spine_conversion_tables 
                    (conversion_type, from_spine, to_spine, accuracy_note)
                    VALUES (?, ?, ?, ?)
                """, ('wood_to_carbon', wood_spine, carbon_spine, 
                     'Approximate conversion based on traditional spine measurements'))
            
            # Import unit conversions
            weight_conversions = conversion_tables.get('weight_conversions', {})
            for conversion_name, conversion_value in weight_conversions.items():
                if '=' in conversion_value:
                    parts = conversion_value.split('=')
                    if len(parts) == 2:
                        from_unit = parts[0].strip().split()[-1]
                        to_value_unit = parts[1].strip().split()
                        if len(to_value_unit) >= 2:
                            factor = float(to_value_unit[0])
                            to_unit = ' '.join(to_value_unit[1:])
                            
                            cursor.execute("""
                                INSERT INTO unit_conversions 
                                (conversion_category, from_unit, to_unit, conversion_factor, formula)
                                VALUES (?, ?, ?, ?, ?)
                            """, ('weight', from_unit, to_unit, factor, conversion_value))
            
            # Length conversions
            length_conversions = conversion_tables.get('length_conversions', {})
            for conversion_name, conversion_value in length_conversions.items():
                if '=' in conversion_value:
                    parts = conversion_value.split('=')
                    if len(parts) == 2:
                        from_unit = parts[0].strip().split()[-1]
                        to_value_unit = parts[1].strip().split()
                        if len(to_value_unit) >= 2:
                            factor = float(to_value_unit[0])
                            to_unit = ' '.join(to_value_unit[1:])
                            
                            cursor.execute("""
                                INSERT INTO unit_conversions 
                                (conversion_category, from_unit, to_unit, conversion_factor, formula)
                                VALUES (?, ?, ?, ?, ?)
                            """, ('length', from_unit, to_unit, factor, conversion_value))
            
            conn.commit()
            print(f"✓ Imported conversion tables successfully")
    
    def import_calculation_formulas(self):
        """Import calculation formulas from calculation_formulas.json"""
        formulas_file = self.data_dir / "calculation_formulas.json"
        
        if not formulas_file.exists():
            print(f"❌ Calculation formulas file not found: {formulas_file}")
            return
        
        with open(formulas_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        calculation_formulas = data.get('calculation_formulas', {})
        print(f"🧮 Importing calculation formulas...")
        
        with self.connect_db() as conn:
            cursor = conn.cursor()
            
            # Clear existing adjustment formulas
            cursor.execute("DELETE FROM spine_calculation_adjustments")
            
            # Import base conditions
            base_conditions = json.dumps(calculation_formulas.get('base_conditions', {}))
            
            # Import adjustment formulas
            adjustment_formulas = calculation_formulas.get('adjustment_formulas', {})
            
            for adjustment_type, formula_data in adjustment_formulas.items():
                try:
                    formula = formula_data.get('calculation', formula_data.get('formula', ''))
                    description = formula_data.get('description', '')
                    examples = json.dumps(formula_data.get('example', {})) if 'example' in formula_data else None
                    
                    # Handle compound bow adjustments specially
                    if adjustment_type == 'bow_speed_adjustment' and 'compound_bow_adjustments' in formula_data:
                        compound_adjustments = formula_data['compound_bow_adjustments']
                        examples = json.dumps({
                            'compound_bow_adjustments': compound_adjustments,
                            'example': formula_data.get('example', {})
                        })
                    
                    cursor.execute("""
                        INSERT INTO spine_calculation_adjustments 
                        (adjustment_type, formula, description, base_conditions, adjustment_examples)
                        VALUES (?, ?, ?, ?, ?)
                    """, (adjustment_type, formula, description, base_conditions, examples))
                    
                except Exception as e:
                    print(f"❌ Error importing formula for {adjustment_type}: {e}")
                    continue
            
            # Import total calculation formula
            total_formula = calculation_formulas.get('total_calculation_formula', {})
            if total_formula:
                cursor.execute("""
                    INSERT INTO spine_calculation_adjustments 
                    (adjustment_type, formula, description, base_conditions, adjustment_examples)
                    VALUES (?, ?, ?, ?, ?)
                """, ('total_calculation', 
                     total_formula.get('formula', ''),
                     total_formula.get('description', ''),
                     base_conditions,
                     json.dumps(total_formula.get('steps', []))))
            
            # Import calculation examples
            examples = calculation_formulas.get('calculation_examples', {})
            if examples:
                cursor.execute("""
                    INSERT INTO spine_calculation_adjustments 
                    (adjustment_type, formula, description, base_conditions, adjustment_examples)
                    VALUES (?, ?, ?, ?, ?)
                """, ('calculation_examples', '', 'Example calculations', base_conditions, json.dumps(examples)))
            
            conn.commit()
            print(f"✓ Imported calculation formulas successfully")
    
    def import_all_data(self):
        """Import all spine calculator data"""
        print("🎯 Starting spine calculator data import...")
        print(f"📁 Data directory: {self.data_dir}")
        print(f"🗃️ Database: {self.database_path}")
        
        try:
            # Create enhanced tables
            self.create_enhanced_spine_tables()
            
            # Import all data
            self.import_spine_charts()
            self.import_conversion_tables()
            self.import_calculation_formulas()
            
            print("\n✅ Spine calculator data import completed successfully!")
            
            # Show summary
            with self.connect_db() as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM manufacturer_spine_charts_enhanced")
                chart_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM spine_conversion_tables")
                conversion_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM spine_calculation_adjustments")
                formula_count = cursor.fetchone()[0]
                
                print(f"\n📊 Import Summary:")
                print(f"   • Spine Charts: {chart_count}")
                print(f"   • Conversion Tables: {conversion_count}")
                print(f"   • Calculation Formulas: {formula_count}")
                
        except Exception as e:
            print(f"❌ Error during import: {e}")
            raise

def main():
    """Main function to run the importer"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Import spine calculator data into database')
    parser.add_argument('--database', '-d', 
                       default='arrow_database.db',
                       help='Database file path (default: arrow_database.db)')
    parser.add_argument('--charts-only', action='store_true',
                       help='Import only spine charts')
    parser.add_argument('--conversions-only', action='store_true', 
                       help='Import only conversion tables')
    parser.add_argument('--formulas-only', action='store_true',
                       help='Import only calculation formulas')
    
    args = parser.parse_args()
    
    importer = SpineCalculatorDataImporter(args.database)
    
    if args.charts_only:
        importer.create_enhanced_spine_tables()
        importer.import_spine_charts()
    elif args.conversions_only:
        importer.create_enhanced_spine_tables()
        importer.import_conversion_tables()
    elif args.formulas_only:
        importer.create_enhanced_spine_tables()
        importer.import_calculation_formulas()
    else:
        importer.import_all_data()

if __name__ == "__main__":
    main()