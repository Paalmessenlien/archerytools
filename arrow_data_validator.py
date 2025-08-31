#!/usr/bin/env python3
"""
Arrow Data Validation Script
Comprehensive validation tool to identify data quality issues preventing arrows from displaying in calculator
"""

import sqlite3
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
from arrow_scraper.unified_database import UnifiedDatabase
from datetime import datetime

@dataclass
class ValidationIssue:
    """Single validation issue"""
    category: str
    severity: str  # critical, warning, info
    arrow_id: int
    manufacturer: str
    model_name: str
    field: str
    issue: str
    current_value: Any
    suggested_fix: str
    sql_fix: Optional[str] = None

@dataclass
class ValidationReport:
    """Complete validation report"""
    total_arrows: int
    total_issues: int
    critical_issues: int
    warning_issues: int
    info_issues: int
    issues_by_category: Dict[str, int]
    validation_issues: List[ValidationIssue]
    summary_stats: Dict[str, Any]
    fix_recommendations: List[str]
    calculator_impact: Dict[str, Any]

class ArrowDataValidator:
    """Comprehensive arrow data validation engine"""
    
    def __init__(self, database_path: str = None):
        """Initialize validator with database connection"""
        self.db = UnifiedDatabase(database_path)
        self.validation_issues = []
        
        # Standard material categories for frontend compatibility
        self.standard_materials = {
            'Carbon', 'Carbon / Aluminum', 'Aluminum', 'Wood', 'Fiberglass'
        }
        
        # Common material mapping for normalization
        self.material_mapping = {
            # German variants
            'kohlefaser': 'Carbon',
            'kohlenstoff': 'Carbon', 
            'carbonfaser': 'Carbon',
            'aluminium': 'Aluminum',
            'holz': 'Wood',
            'fiberglas': 'Fiberglass',
            
            # English variants
            'carbon fiber': 'Carbon',
            'carbon fibre': 'Carbon',
            'graphite': 'Carbon',
            'alloy': 'Aluminum',
            'wood shaft': 'Wood',
            'wooden': 'Wood',
            'timber': 'Wood',
            'glass': 'Fiberglass',
            
            # Mixed variants
            'carbon-aluminum': 'Carbon / Aluminum',
            'carbon/aluminum': 'Carbon / Aluminum',
            'carbon + aluminum': 'Carbon / Aluminum',
            'carbon core aluminum jacket': 'Carbon / Aluminum',
        }
    
    def validate_all_data(self) -> ValidationReport:
        """Run comprehensive validation on all arrow data"""
        print("🔍 Starting comprehensive arrow data validation...")
        
        # Clear previous issues
        self.validation_issues = []
        
        # Get all arrows for validation
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM arrows')
            total_arrows = cursor.fetchone()[0]
            
            print(f"📊 Analyzing {total_arrows} arrows in database...")
        
        # Run all validation categories
        self._validate_critical_fields()
        self._validate_material_standardization()
        self._validate_spine_data_quality()
        self._validate_manufacturer_integration()
        self._validate_duplicate_detection()
        self._validate_data_field_formatting()
        self._validate_calculator_compatibility()
        
        # Generate comprehensive report
        report = self._generate_validation_report(total_arrows)
        
        print(f"✅ Validation complete: {report.total_issues} issues found")
        return report
    
    def _validate_critical_fields(self):
        """Validate critical required fields"""
        print("🔍 Validating critical fields...")
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check for missing manufacturer
            cursor.execute('''
                SELECT id, manufacturer, model_name 
                FROM arrows 
                WHERE manufacturer IS NULL OR manufacturer = '' OR trim(manufacturer) = ''
            ''')
            for row in cursor.fetchall():
                self.validation_issues.append(ValidationIssue(
                    category="Critical Fields",
                    severity="critical",
                    arrow_id=row['id'],
                    manufacturer=row['manufacturer'] or 'NULL',
                    model_name=row['model_name'] or 'NULL',
                    field="manufacturer",
                    issue="Missing or empty manufacturer",
                    current_value=row['manufacturer'],
                    suggested_fix="Add manufacturer name or mark as 'Unknown'",
                    sql_fix=f"UPDATE arrows SET manufacturer = 'Unknown' WHERE id = {row['id']};"
                ))
            
            # Check for missing model_name
            cursor.execute('''
                SELECT id, manufacturer, model_name 
                FROM arrows 
                WHERE model_name IS NULL OR model_name = '' OR trim(model_name) = ''
            ''')
            for row in cursor.fetchall():
                self.validation_issues.append(ValidationIssue(
                    category="Critical Fields",
                    severity="critical",
                    arrow_id=row['id'],
                    manufacturer=row['manufacturer'] or 'Unknown',
                    model_name=row['model_name'] or 'NULL',
                    field="model_name",
                    issue="Missing or empty model name",
                    current_value=row['model_name'],
                    suggested_fix="Add model name or mark as 'Unnamed Model'",
                    sql_fix=f"UPDATE arrows SET model_name = 'Unnamed Model' WHERE id = {row['id']};"
                ))
            
            # Check arrows without spine specifications
            cursor.execute('''
                SELECT a.id, a.manufacturer, a.model_name
                FROM arrows a
                LEFT JOIN spine_specifications ss ON a.id = ss.arrow_id
                WHERE ss.arrow_id IS NULL
            ''')
            for row in cursor.fetchall():
                self.validation_issues.append(ValidationIssue(
                    category="Critical Fields",
                    severity="critical",
                    arrow_id=row['id'],
                    manufacturer=row['manufacturer'] or 'Unknown',
                    model_name=row['model_name'] or 'Unknown',
                    field="spine_specifications",
                    issue="No spine specifications available",
                    current_value="NULL",
                    suggested_fix="Add spine specifications or remove arrow",
                    sql_fix=f"DELETE FROM arrows WHERE id = {row['id']}; -- Remove arrow without spine data"
                ))
    
    def _validate_material_standardization(self):
        """Validate and suggest material standardization"""
        print("🔍 Validating material standardization...")
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get all unique materials
            cursor.execute('SELECT DISTINCT material, COUNT(*) as count FROM arrows GROUP BY material ORDER BY count DESC')
            materials = cursor.fetchall()
            
            for material_row in materials:
                material = material_row['material']
                count = material_row['count']
                
                if not material or material.strip() == '':
                    # Missing material
                    cursor.execute('SELECT id, manufacturer, model_name FROM arrows WHERE material IS NULL OR material = "" OR trim(material) = ""')
                    for row in cursor.fetchall():
                        self.validation_issues.append(ValidationIssue(
                            category="Material Standardization",
                            severity="warning",
                            arrow_id=row['id'],
                            manufacturer=row['manufacturer'] or 'Unknown',
                            model_name=row['model_name'] or 'Unknown',
                            field="material",
                            issue="Missing material specification",
                            current_value=material,
                            suggested_fix="Set to 'Carbon' (most common default)",
                            sql_fix=f"UPDATE arrows SET material = 'Carbon' WHERE id = {row['id']};"
                        ))
                elif material not in self.standard_materials:
                    # Non-standard material that needs mapping
                    suggested_material = self._suggest_material_mapping(material)
                    if suggested_material != material:
                        cursor.execute('SELECT id, manufacturer, model_name FROM arrows WHERE material = ?', (material,))
                        for row in cursor.fetchall():
                            self.validation_issues.append(ValidationIssue(
                                category="Material Standardization",
                                severity="warning",
                                arrow_id=row['id'],
                                manufacturer=row['manufacturer'] or 'Unknown',
                                model_name=row['model_name'] or 'Unknown',
                                field="material",
                                issue=f"Non-standard material: '{material}'",
                                current_value=material,
                                suggested_fix=f"Map to standard material: '{suggested_material}'",
                                sql_fix=f"UPDATE arrows SET material = '{suggested_material}' WHERE material = '{material}';"
                            ))
    
    def _validate_spine_data_quality(self):
        """Validate spine data quality and ranges"""
        print("🔍 Validating spine data quality...")
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check for invalid spine values
            cursor.execute('''
                SELECT ss.id, ss.arrow_id, a.manufacturer, a.model_name, ss.spine, a.material
                FROM spine_specifications ss
                JOIN arrows a ON ss.arrow_id = a.id
                WHERE ss.spine IS NULL OR ss.spine = '' OR ss.spine = 0
            ''')
            for row in cursor.fetchall():
                self.validation_issues.append(ValidationIssue(
                    category="Spine Data Quality",
                    severity="critical",
                    arrow_id=row['arrow_id'],
                    manufacturer=row['manufacturer'] or 'Unknown',
                    model_name=row['model_name'] or 'Unknown',
                    field="spine",
                    issue="Invalid or missing spine value",
                    current_value=row['spine'],
                    suggested_fix="Remove invalid spine specification",
                    sql_fix=f"DELETE FROM spine_specifications WHERE id = {row['id']};"
                ))
            
            # Check for unrealistic spine ranges
            cursor.execute('''
                SELECT ss.id, ss.arrow_id, a.manufacturer, a.model_name, ss.spine, a.material
                FROM spine_specifications ss
                JOIN arrows a ON ss.arrow_id = a.id
                WHERE 
                    (a.material = 'Wood' AND (ss.spine < 25 OR ss.spine > 100)) OR
                    (a.material = 'Carbon' AND (ss.spine < 150 OR ss.spine > 2000)) OR
                    (a.material = 'Aluminum' AND (ss.spine < 150 OR ss.spine > 3000))
            ''')
            for row in cursor.fetchall():
                material = row['material'] or 'Unknown'
                if material == 'Wood':
                    spine_range = "25-100 lbs"
                elif material == 'Carbon':
                    spine_range = "150-2000"
                elif material == 'Aluminum':
                    spine_range = "150-3000"
                else:
                    spine_range = "150-2000 (default)"
                self.validation_issues.append(ValidationIssue(
                    category="Spine Data Quality",
                    severity="warning",
                    arrow_id=row['arrow_id'],
                    manufacturer=row['manufacturer'] or 'Unknown',
                    model_name=row['model_name'] or 'Unknown',
                    field="spine",
                    issue=f"Spine value {row['spine']} outside realistic range for {material} arrows ({spine_range})",
                    current_value=row['spine'],
                    suggested_fix=f"Verify spine value is correct for {material} material",
                    sql_fix=f"-- Manual review required for spine_specifications.id = {row['id']}"
                ))
    
    def _validate_manufacturer_integration(self):
        """Validate manufacturer integration and active status"""
        print("🔍 Validating manufacturer integration...")
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check arrows referencing non-existent manufacturers
            cursor.execute('''
                SELECT a.id, a.manufacturer, a.model_name
                FROM arrows a
                LEFT JOIN manufacturers m ON a.manufacturer = m.name
                WHERE m.name IS NULL
            ''')
            for row in cursor.fetchall():
                self.validation_issues.append(ValidationIssue(
                    category="Manufacturer Integration",
                    severity="critical",
                    arrow_id=row['id'],
                    manufacturer=row['manufacturer'] or 'Unknown',
                    model_name=row['model_name'] or 'Unknown',
                    field="manufacturer",
                    issue="References non-existent manufacturer",
                    current_value=row['manufacturer'],
                    suggested_fix="Create manufacturer entry or update manufacturer name",
                    sql_fix=f"INSERT INTO manufacturers (name, is_active) VALUES ('{row['manufacturer']}', 1);"
                ))
            
            # Check arrows from inactive manufacturers (for info)
            cursor.execute('''
                SELECT a.id, a.manufacturer, a.model_name, m.is_active
                FROM arrows a
                JOIN manufacturers m ON a.manufacturer = m.name
                WHERE m.is_active = 0
            ''')
            for row in cursor.fetchall():
                self.validation_issues.append(ValidationIssue(
                    category="Manufacturer Integration",
                    severity="info",
                    arrow_id=row['id'],
                    manufacturer=row['manufacturer'] or 'Unknown',
                    model_name=row['model_name'] or 'Unknown',
                    field="manufacturer_active_status",
                    issue="Arrow from inactive manufacturer (hidden from calculator)",
                    current_value="inactive",
                    suggested_fix="Reactivate manufacturer or migrate arrows",
                    sql_fix=f"UPDATE manufacturers SET is_active = 1 WHERE name = '{row['manufacturer']}';"
                ))
    
    def _validate_duplicate_detection(self):
        """Detect duplicate arrow entries and spine specifications"""
        print("🔍 Detecting duplicate arrows and spine specifications...")
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Detect duplicate arrows (same manufacturer + model_name)
            cursor.execute('''
                SELECT manufacturer, model_name, COUNT(*) as count, GROUP_CONCAT(id) as arrow_ids
                FROM arrows 
                WHERE manufacturer IS NOT NULL AND model_name IS NOT NULL
                GROUP BY LOWER(TRIM(manufacturer)), LOWER(TRIM(model_name))
                HAVING COUNT(*) > 1
                ORDER BY count DESC
            ''')
            
            for row in cursor.fetchall():
                arrow_ids = row['arrow_ids'].split(',')
                # Report all but the first arrow as duplicates
                for arrow_id in arrow_ids[1:]:
                    self.validation_issues.append(ValidationIssue(
                        category="Duplicate Detection",
                        severity="warning",
                        arrow_id=int(arrow_id),
                        manufacturer=row['manufacturer'],
                        model_name=row['model_name'],
                        field="duplicate_arrow",
                        issue=f"Duplicate arrow entry ({row['count']} total found)",
                        current_value=f"Arrow ID {arrow_id}",
                        suggested_fix="Remove duplicate or merge specifications",
                        sql_fix=f"-- DELETE FROM arrows WHERE id = {arrow_id}; -- Review before deletion"
                    ))
            
            # 2. Detect duplicate spine specifications for same arrow
            cursor.execute('''
                SELECT ss.arrow_id, a.manufacturer, a.model_name, ss.spine, COUNT(*) as count, 
                       GROUP_CONCAT(ss.id) as spine_ids
                FROM spine_specifications ss
                JOIN arrows a ON ss.arrow_id = a.id
                GROUP BY ss.arrow_id, ss.spine
                HAVING COUNT(*) > 1
                ORDER BY count DESC
            ''')
            
            for row in cursor.fetchall():
                spine_ids = row['spine_ids'].split(',')
                # Report all but the first spine spec as duplicates
                for spine_id in spine_ids[1:]:
                    self.validation_issues.append(ValidationIssue(
                        category="Duplicate Detection",
                        severity="warning",
                        arrow_id=row['arrow_id'],
                        manufacturer=row['manufacturer'],
                        model_name=row['model_name'],
                        field="duplicate_spine_spec",
                        issue=f"Duplicate spine specification (spine {row['spine']}, {row['count']} total)",
                        current_value=f"Spine spec ID {spine_id}",
                        suggested_fix="Remove duplicate spine specification",
                        sql_fix=f"DELETE FROM spine_specifications WHERE id = {spine_id};"
                    ))
            
            # 3. Detect near-duplicate arrows (similar names, fuzzy matching)
            cursor.execute('''
                SELECT a1.id as id1, a1.manufacturer as man1, a1.model_name as model1,
                       a2.id as id2, a2.manufacturer as man2, a2.model_name as model2
                FROM arrows a1
                JOIN arrows a2 ON a1.id < a2.id
                WHERE LOWER(TRIM(a1.manufacturer)) = LOWER(TRIM(a2.manufacturer))
                  AND (
                    -- Very similar model names (minor differences)
                    LOWER(REPLACE(REPLACE(a1.model_name, ' ', ''), '-', '')) = 
                    LOWER(REPLACE(REPLACE(a2.model_name, ' ', ''), '-', ''))
                    OR
                    -- One model name contains the other
                    (LENGTH(a1.model_name) > 3 AND LENGTH(a2.model_name) > 3 AND
                     (LOWER(a1.model_name) LIKE '%' || LOWER(a2.model_name) || '%' OR
                      LOWER(a2.model_name) LIKE '%' || LOWER(a1.model_name) || '%'))
                  )
                LIMIT 50
            ''')
            
            for row in cursor.fetchall():
                self.validation_issues.append(ValidationIssue(
                    category="Duplicate Detection",
                    severity="info",
                    arrow_id=row['id2'],
                    manufacturer=row['man2'],
                    model_name=row['model2'],
                    field="near_duplicate",
                    issue=f"Potential duplicate of Arrow ID {row['id1']} ({row['model1']})",
                    current_value=f"Similar to: {row['model1']}",
                    suggested_fix="Review and merge if truly duplicate",
                    sql_fix=f"-- Potential duplicate: Compare Arrow {row['id1']} vs {row['id2']}"
                ))
            
            # 4. Detect arrows with identical specifications but different IDs
            cursor.execute('''
                SELECT ss1.arrow_id as arrow1, ss2.arrow_id as arrow2,
                       a1.manufacturer, a1.model_name as model1, a2.model_name as model2,
                       ss1.spine, ss1.outer_diameter, ss1.gpi_weight
                FROM spine_specifications ss1
                JOIN spine_specifications ss2 ON ss1.id < ss2.id
                JOIN arrows a1 ON ss1.arrow_id = a1.id
                JOIN arrows a2 ON ss2.arrow_id = a2.id
                WHERE LOWER(TRIM(a1.manufacturer)) = LOWER(TRIM(a2.manufacturer))
                  AND ss1.spine = ss2.spine
                  AND ABS(COALESCE(ss1.outer_diameter, 0) - COALESCE(ss2.outer_diameter, 0)) < 0.001
                  AND ABS(COALESCE(ss1.gpi_weight, 0) - COALESCE(ss2.gpi_weight, 0)) < 0.1
                  AND ss1.arrow_id != ss2.arrow_id
                LIMIT 25
            ''')
            
            for row in cursor.fetchall():
                self.validation_issues.append(ValidationIssue(
                    category="Duplicate Detection", 
                    severity="info",
                    arrow_id=row['arrow2'],
                    manufacturer=row['manufacturer'],
                    model_name=row['model2'],
                    field="identical_specifications",
                    issue=f"Identical specs to {row['model1']} (spine {row['spine']}, diameter {row['outer_diameter']}, weight {row['gpi_weight']})",
                    current_value="Identical specifications",
                    suggested_fix="Review if truly different arrows or consolidate",
                    sql_fix=f"-- Review: Arrow {row['arrow1']} vs {row['arrow2']} have identical specs"
                ))
    
    def _validate_data_field_formatting(self):
        """Validate data field formatting that could break calculator logic"""
        print("🔍 Validating data field formatting...")
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Validate length_options formatting in spine_specifications
            cursor.execute('''
                SELECT ss.id, ss.arrow_id, a.manufacturer, a.model_name, ss.length_options
                FROM spine_specifications ss
                JOIN arrows a ON ss.arrow_id = a.id
                WHERE ss.length_options IS NOT NULL AND ss.length_options != ''
            ''')
            
            for row in cursor.fetchall():
                length_options = row['length_options']
                arrow_id = row['arrow_id']
                manufacturer = row['manufacturer'] or 'Unknown'
                model_name = row['model_name'] or 'Unknown'
                
                # Check for malformed length values
                issues_found = []
                
                try:
                    # Try to parse as JSON first
                    if length_options.startswith('[') or length_options.startswith('{'):
                        parsed = json.loads(length_options)
                        if isinstance(parsed, list):
                            for i, length in enumerate(parsed):
                                if isinstance(length, str):
                                    # Check for European decimal notation like "33,5" or "29,13"
                                    if self._has_european_decimal_comma(length):
                                        issues_found.append(f"European decimal comma notation at index {i}: '{length}' (should use period: '{length.replace(',', '.')}')")
                                    # Check for problematic patterns like "31, 5" within a single string element  
                                    elif ',' in length and not self._is_valid_single_length_with_comma(length):
                                        issues_found.append(f"Malformed length value at index {i}: '{length}' (contains problematic comma)")
                                    elif not self._is_valid_length_format(length):
                                        issues_found.append(f"Invalid length format at index {i}: '{length}'")
                                elif isinstance(length, (int, float)):
                                    # Numeric values should be reasonable (6-36 inches typically)
                                    if length < 6 or length > 36:
                                        issues_found.append(f"Unrealistic length value: {length}")
                    else:
                        # Handle non-JSON formats - check for "31, 5" type patterns
                        if self._has_problematic_comma_pattern(length_options):
                            issues_found.append(f"Problematic comma pattern detected: '{length_options}'")
                        elif ',' in length_options and not self._is_valid_comma_separated_lengths(length_options):
                            issues_found.append(f"Malformed comma-separated values: '{length_options}'")
                        elif not self._is_valid_length_format(length_options):
                            issues_found.append(f"Invalid length format: '{length_options}'")
                            
                except (json.JSONDecodeError, ValueError) as e:
                    issues_found.append(f"JSON parsing error: {str(e)}")
                
                # Report all issues found for this arrow
                for issue_desc in issues_found:
                    self.validation_issues.append(ValidationIssue(
                        category="Data Field Formatting",
                        severity="critical",  # These break calculator logic
                        arrow_id=arrow_id,
                        manufacturer=manufacturer,
                        model_name=model_name,
                        field="length_options",
                        issue=issue_desc,
                        current_value=length_options,
                        suggested_fix="Fix formatting to valid JSON array or clean string format",
                        sql_fix=self._generate_length_options_sql_fix(row['id'], length_options, issue_desc)
                    ))
            
            # Validate diameter formatting in spine_specifications table
            cursor.execute('''
                SELECT ss.id, ss.arrow_id, a.manufacturer, a.model_name, ss.outer_diameter
                FROM spine_specifications ss
                JOIN arrows a ON ss.arrow_id = a.id
                WHERE ss.outer_diameter IS NOT NULL
            ''')
            
            for row in cursor.fetchall():
                diameter = row['outer_diameter']
                if not self._is_valid_diameter_numeric(diameter):
                    self.validation_issues.append(ValidationIssue(
                        category="Data Field Formatting",
                        severity="warning",
                        arrow_id=row['arrow_id'],
                        manufacturer=row['manufacturer'] or 'Unknown',
                        model_name=row['model_name'] or 'Unknown',
                        field="outer_diameter",
                        issue=f"Invalid outer diameter value: '{diameter}'",
                        current_value=diameter,
                        suggested_fix="Should be numeric value: 0.15-0.7 inches or 4.0-18.0 mm",
                        sql_fix=f"-- UPDATE spine_specifications SET outer_diameter = corrected_value WHERE id = {row['id']};"
                    ))
            
            # Validate weight formatting in spine_specifications table
            cursor.execute('''
                SELECT ss.id, ss.arrow_id, a.manufacturer, a.model_name, ss.gpi_weight
                FROM spine_specifications ss
                JOIN arrows a ON ss.arrow_id = a.id
                WHERE ss.gpi_weight IS NOT NULL
            ''')
            
            for row in cursor.fetchall():
                weight = row['gpi_weight']
                if not self._is_valid_weight_numeric(weight):
                    self.validation_issues.append(ValidationIssue(
                        category="Data Field Formatting",
                        severity="warning",
                        arrow_id=row['arrow_id'],
                        manufacturer=row['manufacturer'] or 'Unknown',
                        model_name=row['model_name'] or 'Unknown',
                        field="gpi_weight",
                        issue=f"Invalid gpi weight value: '{weight}'",
                        current_value=weight,
                        suggested_fix="Should be numeric value between 1.0-50.0 gpi",
                        sql_fix=f"-- UPDATE spine_specifications SET gpi_weight = corrected_value WHERE id = {row['id']};"
                    ))
    
    def _is_valid_length_format(self, length_str: str) -> bool:
        """Check if length string is in valid format"""
        if not length_str:
            return False
            
        # Clean the string
        clean = length_str.strip().replace('"', '').replace("'", "")
        
        # Check for problematic patterns
        if ',' in clean and len(clean.split(',')) > 1:
            # Could be "31, 5" which is invalid
            parts = [p.strip() for p in clean.split(',')]
            for part in parts:
                try:
                    float(part)
                except ValueError:
                    return False
            return True
        
        # Single value check
        try:
            value = float(clean)
            return 6 <= value <= 36  # Reasonable arrow length range
        except ValueError:
            return False
    
    def _is_valid_comma_separated_lengths(self, lengths_str: str) -> bool:
        """Validate comma-separated length values"""
        try:
            parts = [p.strip().replace('"', '').replace("'", "") for p in lengths_str.split(',')]
            for part in parts:
                if part:  # Skip empty parts
                    value = float(part)
                    if not (6 <= value <= 36):
                        return False
            return True
        except (ValueError, TypeError):
            return False
    
    def _is_valid_single_length_with_comma(self, length_str: str) -> bool:
        """Check if a single length string with comma is valid (e.g., '31.5' not '31, 5')"""
        if not length_str or ',' not in length_str:
            return True
            
        # Clean and check if it's a valid decimal number
        clean = length_str.strip().replace('"', '').replace("'", "")
        
        # If there's a comma, it should be a decimal separator, not a list separator
        if clean.count(',') == 1:
            # Could be European decimal format like "31,5" 
            decimal_clean = clean.replace(',', '.')
            try:
                value = float(decimal_clean)
                return 6 <= value <= 36
            except ValueError:
                return False
        
        return False  # Multiple commas or other issues
    
    def _generate_length_options_sql_fix(self, spec_id: int, current_value: str, issue_desc: str) -> str:
        """Generate specific SQL fix for length_options formatting issues"""
        
        # Handle European decimal comma notation
        if "European decimal comma notation" in issue_desc:
            try:
                # Parse JSON and fix comma notation
                parsed = json.loads(current_value)
                if isinstance(parsed, list) and len(parsed) > 0:
                    fixed_list = []
                    for item in parsed:
                        if isinstance(item, str) and ',' in item:
                            # Replace comma with period for decimal notation
                            fixed_item = item.replace(',', '.')
                            fixed_list.append(fixed_item)
                        else:
                            fixed_list.append(item)
                    
                    fixed_json = json.dumps(fixed_list)
                    return f"UPDATE spine_specifications SET length_options = '{fixed_json}' WHERE id = {spec_id};"
            except:
                pass
        
        # Default fallback for other formatting issues
        return f"UPDATE spine_specifications SET length_options = NULL WHERE id = {spec_id}; -- Fix manually: {issue_desc[:50]}..."
    
    def _has_european_decimal_comma(self, text: str) -> bool:
        """Detect European decimal comma notation like '33,5' that should be '33.5'"""
        if not text or ',' not in text:
            return False
            
        # Clean the text first
        clean_text = text.strip().replace('"', '').replace("'", '').replace('\\', '')
        
        # Look for patterns like "number,number" (European decimal)
        # Examples: "33,5" "29,13" "28,75"
        pattern = r'^\d+,\d+$'  # Matches entire string being a decimal with comma
        return bool(re.search(pattern, clean_text))
    
    def _has_problematic_comma_pattern(self, text: str) -> bool:
        """Detect problematic comma patterns like '31, 5' that should be '31.5'"""
        if not text or ',' not in text:
            return False
            
        # Look for patterns like "number, number" with space after comma
        pattern = r'\d+\s*,\s+\d+'  # Matches "31, 5" or "31,5" or "31 , 5"
        return bool(re.search(pattern, text))
    
    def _is_valid_diameter_format(self, diameter_str: str) -> bool:
        """Check if diameter is in valid format"""
        if not diameter_str:
            return False
            
        # Clean the string
        clean = diameter_str.strip().replace('mm', '').replace('in', '').replace('"', '')
        
        try:
            value = float(clean)
            return 4.0 <= value <= 15.0  # Reasonable diameter range in mm
        except ValueError:
            return False
    
    def _is_valid_diameter_numeric(self, diameter_value) -> bool:
        """Check if numeric diameter value is in valid range"""
        if diameter_value is None:
            return True  # NULL is acceptable
        
        try:
            value = float(diameter_value)
            # Handle multiple diameter formats:
            # 1. Decimal inches: 0.15-0.7 (e.g., 0.245")
            # 2. Hundredths of inch: 150-700 (e.g., 245 = 0.245")
            # 3. Millimeters: 4.0-18.0 (e.g., 6.2mm)
            return (0.15 <= value <= 0.7) or (150 <= value <= 700) or (4.0 <= value <= 18.0)
        except (ValueError, TypeError):
            return False
    
    def _is_valid_weight_format(self, weight_str: str) -> bool:
        """Check if weight is in valid format"""
        if not weight_str:
            return False
            
        # Clean the string
        clean = weight_str.strip().lower().replace('gpi', '').replace('grains', '').replace('g', '')
        
        try:
            value = float(clean)
            return 1.0 <= value <= 50.0  # Reasonable weight range
        except ValueError:
            return False
    
    def _is_valid_weight_numeric(self, weight_value) -> bool:
        """Check if numeric weight value is in valid range"""
        if weight_value is None:
            return True  # NULL is acceptable
        
        try:
            value = float(weight_value)
            return 1.0 <= value <= 50.0  # Reasonable weight range in gpi
        except (ValueError, TypeError):
            return False
    
    def _validate_calculator_compatibility(self):
        """Test compatibility with calculator filtering logic"""
        print("🔍 Validating calculator compatibility...")
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Test material filtering compatibility
            cursor.execute('SELECT DISTINCT material FROM arrows WHERE material IS NOT NULL')
            db_materials = [row['material'] for row in cursor.fetchall()]
            
            # Check if materials can be properly mapped for frontend
            frontend_materials = {'carbon', 'aluminum', 'carbon-aluminum', 'wood', 'fiberglass'}
            
            for db_material in db_materials:
                if db_material and db_material.lower() not in [m.lower() for m in self.standard_materials]:
                    # Find arrows with problematic materials
                    cursor.execute('SELECT id, manufacturer, model_name FROM arrows WHERE material = ?', (db_material,))
                    for row in cursor.fetchall():
                        suggested = self._suggest_material_mapping(db_material)
                        self.validation_issues.append(ValidationIssue(
                            category="Calculator Compatibility",
                            severity="warning",
                            arrow_id=row['id'],
                            manufacturer=row['manufacturer'] or 'Unknown',
                            model_name=row['model_name'] or 'Unknown',
                            field="material",
                            issue=f"Material '{db_material}' not in standard frontend categories",
                            current_value=db_material,
                            suggested_fix=f"Map to standard material: '{suggested}'",
                            sql_fix=f"UPDATE arrows SET material = '{suggested}' WHERE material = '{db_material}';"
                        ))
            
            # Check JSON field formatting in spine_specifications
            cursor.execute('''
                SELECT ss.id, ss.arrow_id, a.manufacturer, a.model_name, ss.length_options
                FROM spine_specifications ss
                JOIN arrows a ON ss.arrow_id = a.id
                WHERE ss.length_options IS NOT NULL AND ss.length_options != ''
            ''')
            for row in cursor.fetchall():
                try:
                    if row['length_options']:
                        json.loads(row['length_options'])
                except (json.JSONDecodeError, TypeError):
                    self.validation_issues.append(ValidationIssue(
                        category="Calculator Compatibility",
                        severity="warning",
                        arrow_id=row['arrow_id'],
                        manufacturer=row['manufacturer'] or 'Unknown',
                        model_name=row['model_name'] or 'Unknown',
                        field="length_options",
                        issue="Invalid JSON format in length_options",
                        current_value=row['length_options'],
                        suggested_fix="Fix JSON formatting or set to NULL",
                        sql_fix=f"UPDATE spine_specifications SET length_options = NULL WHERE id = {row['id']};"
                    ))
    
    def _suggest_material_mapping(self, material: str) -> str:
        """Suggest standard material mapping"""
        if not material:
            return 'Carbon'
        
        material_lower = material.lower().strip()
        
        # Check direct mapping first
        for variant, standard in self.material_mapping.items():
            if variant in material_lower:
                return standard
        
        # Pattern-based mapping
        if any(keyword in material_lower for keyword in ['carbon', 'graphite', 'fibre', 'fiber']):
            if any(keyword in material_lower for keyword in ['aluminum', 'alloy', 'metal']):
                return 'Carbon / Aluminum'
            return 'Carbon'
        elif any(keyword in material_lower for keyword in ['aluminum', 'alloy']):
            return 'Aluminum'
        elif any(keyword in material_lower for keyword in ['wood', 'cedar', 'pine', 'bamboo', 'ash']):
            return 'Wood'
        elif any(keyword in material_lower for keyword in ['glass', 'fiberglass']):
            return 'Fiberglass'
        
        # Default fallback
        return 'Carbon'
    
    def _generate_validation_report(self, total_arrows: int) -> ValidationReport:
        """Generate comprehensive validation report"""
        
        # Count issues by severity
        critical_count = sum(1 for issue in self.validation_issues if issue.severity == 'critical')
        warning_count = sum(1 for issue in self.validation_issues if issue.severity == 'warning')
        info_count = sum(1 for issue in self.validation_issues if issue.severity == 'info')
        
        # Count issues by category
        categories = {}
        for issue in self.validation_issues:
            categories[issue.category] = categories.get(issue.category, 0) + 1
        
        # Generate summary statistics
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Material distribution
            cursor.execute('SELECT material, COUNT(*) as count FROM arrows GROUP BY material ORDER BY count DESC')
            material_stats = dict(cursor.fetchall())
            
            # Manufacturer active status
            cursor.execute('''
                SELECT m.is_active, COUNT(a.id) as arrow_count
                FROM manufacturers m
                LEFT JOIN arrows a ON m.name = a.manufacturer
                GROUP BY m.is_active
            ''')
            manufacturer_stats = dict(cursor.fetchall())
            
            # Spine specifications coverage
            cursor.execute('''
                SELECT 
                    COUNT(DISTINCT a.id) as arrows_with_specs,
                    (SELECT COUNT(*) FROM arrows) as total_arrows
                FROM arrows a
                JOIN spine_specifications ss ON a.id = ss.arrow_id
            ''')
            spine_coverage = cursor.fetchone()
            
            summary_stats = {
                'material_distribution': material_stats,
                'manufacturer_status': manufacturer_stats,
                'spine_coverage': {
                    'arrows_with_specs': spine_coverage['arrows_with_specs'],
                    'total_arrows': spine_coverage['total_arrows'],
                    'coverage_percentage': (spine_coverage['arrows_with_specs'] / spine_coverage['total_arrows']) * 100 if spine_coverage['total_arrows'] > 0 else 0
                }
            }
        
        # Generate fix recommendations
        fix_recommendations = self._generate_fix_recommendations()
        
        # Analyze calculator impact
        calculator_impact = self._analyze_calculator_impact()
        
        return ValidationReport(
            total_arrows=total_arrows,
            total_issues=len(self.validation_issues),
            critical_issues=critical_count,
            warning_issues=warning_count,
            info_issues=info_count,
            issues_by_category=categories,
            validation_issues=self.validation_issues,
            summary_stats=summary_stats,
            fix_recommendations=fix_recommendations,
            calculator_impact=calculator_impact
        )
    
    def _generate_fix_recommendations(self) -> List[str]:
        """Generate actionable fix recommendations"""
        recommendations = []
        
        # Count issues by category for prioritization
        critical_fields = sum(1 for issue in self.validation_issues if issue.category == "Critical Fields" and issue.severity == "critical")
        material_issues = sum(1 for issue in self.validation_issues if issue.category == "Material Standardization")
        manufacturer_issues = sum(1 for issue in self.validation_issues if issue.category == "Manufacturer Integration")
        
        if critical_fields > 0:
            recommendations.append(f"🚨 URGENT: Fix {critical_fields} critical field issues preventing arrow display")
        
        if material_issues > 0:
            recommendations.append(f"🔧 Standardize {material_issues} material classifications for better filtering")
        
        if manufacturer_issues > 0:
            recommendations.append(f"👥 Resolve {manufacturer_issues} manufacturer integration issues")
        
        # Add SQL batch fix recommendations
        if self.validation_issues:
            recommendations.append("💡 Use provided SQL fixes to batch resolve issues")
            recommendations.append("🧪 Test calculator functionality after applying fixes")
            recommendations.append("📊 Re-run validation to verify improvements")
        
        return recommendations
    
    def _analyze_calculator_impact(self) -> Dict[str, Any]:
        """Analyze impact on calculator functionality"""
        
        # Count arrows that would be hidden due to issues
        hidden_arrows = 0
        display_issues = {}
        
        for issue in self.validation_issues:
            if issue.severity == "critical":
                hidden_arrows += 1
                category = issue.category
                display_issues[category] = display_issues.get(category, 0) + 1
        
        return {
            'potentially_hidden_arrows': hidden_arrows,
            'issues_affecting_display': display_issues,
            'estimated_calculator_accuracy': max(0, 100 - (hidden_arrows * 2))  # Rough estimate
        }
    
    def get_sql_fix_script(self) -> str:
        """Generate comprehensive SQL script to fix all issues"""
        
        sql_lines = [
            "-- Arrow Data Validation Fix Script",
            f"-- Generated on {datetime.now().isoformat()}",
            f"-- Fixes {len(self.validation_issues)} identified issues",
            "",
            "BEGIN TRANSACTION;",
            ""
        ]
        
        # Group fixes by category
        categories = {}
        for issue in self.validation_issues:
            if issue.sql_fix:
                if issue.category not in categories:
                    categories[issue.category] = []
                categories[issue.category].append(issue)
        
        for category, issues in categories.items():
            sql_lines.append(f"-- {category} Fixes ({len(issues)} issues)")
            for issue in issues:
                if issue.sql_fix:
                    sql_lines.append(issue.sql_fix)
            sql_lines.append("")
        
        sql_lines.extend([
            "COMMIT;",
            "",
            "-- Run 'SELECT changes()' to see how many rows were affected",
            "-- Recommended: Re-run validation after applying fixes"
        ])
        
        return "\n".join(sql_lines)
    
    def get_validation_summary(self) -> str:
        """Get human-readable validation summary"""
        if not self.validation_issues:
            return "✅ No validation issues found - database is in excellent condition!"
        
        report = self.validate_all_data()
        
        summary = f"""
🔍 ARROW DATA VALIDATION REPORT
{'='*50}

📊 OVERVIEW:
• Total Arrows Analyzed: {report.total_arrows:,}
• Total Issues Found: {report.total_issues:,}
• Critical Issues: {report.critical_issues:,} (blocks calculator display)
• Warning Issues: {report.warning_issues:,} (impacts functionality)
• Info Issues: {report.info_issues:,} (minor improvements)

📋 ISSUES BY CATEGORY:
"""
        
        for category, count in report.issues_by_category.items():
            summary += f"• {category}: {count:,} issues\n"
        
        summary += f"""
🎯 CALCULATOR IMPACT:
• Potentially Hidden Arrows: {report.calculator_impact['potentially_hidden_arrows']:,}
• Estimated Calculator Accuracy: {report.calculator_impact['estimated_calculator_accuracy']:.1f}%

🔧 MATERIAL DISTRIBUTION:
"""
        
        for material, count in report.summary_stats['material_distribution'].items():
            summary += f"• {material or 'NULL'}: {count:,} arrows\n"
        
        summary += f"""
📈 SPINE COVERAGE:
• Arrows with Spine Data: {report.summary_stats['spine_coverage']['arrows_with_specs']:,}
• Coverage Percentage: {report.summary_stats['spine_coverage']['coverage_percentage']:.1f}%

💡 TOP RECOMMENDATIONS:
"""
        
        for rec in report.fix_recommendations[:5]:
            summary += f"• {rec}\n"
        
        return summary

# CLI interface for running validation
if __name__ == "__main__":
    import sys
    
    # Allow specifying database path
    db_path = sys.argv[1] if len(sys.argv) > 1 else None
    
    print("🏹 Arrow Data Validation Engine")
    print("=" * 50)
    
    try:
        validator = ArrowDataValidator(db_path)
        report = validator.validate_all_data()
        
        # Print summary
        print(validator.get_validation_summary())
        
        # Offer to generate SQL fix script
        if report.total_issues > 0:
            print(f"\n💾 SQL Fix Script Available")
            print(f"Run with --generate-sql to create fix script")
            
            if len(sys.argv) > 1 and '--generate-sql' in sys.argv:
                sql_script = validator.get_sql_fix_script()
                fix_file = f"arrow_validation_fixes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
                
                with open(fix_file, 'w') as f:
                    f.write(sql_script)
                
                print(f"✅ SQL fix script saved to: {fix_file}")
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        sys.exit(1)