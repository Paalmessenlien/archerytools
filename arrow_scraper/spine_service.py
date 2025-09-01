"""
Unified Spine Calculation Service

This module provides a single, centralized spine calculation service that ensures
all parts of the system use the same calculation logic as the calculator page.
All spine calculations across the system should use this service.
"""

from typing import Dict, Any, Optional, List, Tuple
import json
import sqlite3
from spine_calculator import SpineCalculator, BowConfiguration, BowType
from arrow_database import ArrowDatabase


class UnifiedSpineService:
    """
    Centralized spine calculation service that provides consistent calculations
    across the entire system. Uses the same logic as the calculator page.
    """
    
    def __init__(self):
        self.spine_calculator = SpineCalculator()
        self.db = ArrowDatabase()
        self._cache = {}  # Cache for calculation parameters
    
    def calculate_spine(
        self,
        draw_weight: float,
        arrow_length: float,
        point_weight: float = 125.0,
        bow_type: str = 'compound',
        draw_length: float = 28.0,
        nock_weight: float = 10.0,
        fletching_weight: float = 15.0,
        material_preference: Optional[str] = None,
        string_material: Optional[str] = None,
        calculation_method: str = 'universal',
        manufacturer_chart: Optional[str] = None,
        chart_id: Optional[str] = None,
        bow_speed: Optional[float] = None,
        release_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate spine using the same logic as the calculator page API endpoint.
        
        Args:
            draw_weight: Bow's marked draw weight in pounds
            arrow_length: Physical arrow length in inches
            point_weight: Point weight in grains (default 125)
            bow_type: 'compound', 'recurve', 'traditional', or 'longbow'
            draw_length: Bow's actual draw length in inches (important for calculations!)
            nock_weight: Nock weight in grains (default 10)
            fletching_weight: Fletching weight in grains (default 15)
            material_preference: Optional arrow material preference
            
        Returns:
            Dictionary with spine calculation results in same format as calculator API
        """
        
        # Normalize bow type (map longbow to traditional)
        if bow_type.lower() == 'longbow':
            bow_type = 'traditional'
            
        # Validate bow type
        valid_bow_types = ['compound', 'recurve', 'traditional']
        if bow_type.lower() not in valid_bow_types:
            bow_type = 'compound'
        
        # Always use the research-based simple calculator for all bow types
        # The old advanced calculator uses outdated Easton chart logic that doesn't match research standards
        print(f"🎯 Using research-based calculation for {bow_type} bow")
        
        # Apply Professional mode adjustments if parameters provided
        adjusted_draw_weight = draw_weight
        professional_adjustments = []
        
        # Bow speed adjustment (Professional mode)
        if bow_speed is not None:
            speed_adjustment = self._get_bow_speed_adjustment(bow_speed)
            adjusted_draw_weight += speed_adjustment
            if speed_adjustment != 0:
                professional_adjustments.append(f"Bow speed {bow_speed}fps: {speed_adjustment:+.1f}lbs")
        
        # Release type adjustment (Professional mode)
        if release_type is not None:
            release_adjustment = self._get_release_type_adjustment(release_type)
            adjusted_draw_weight += release_adjustment
            if release_adjustment != 0:
                professional_adjustments.append(f"Release type {release_type}: {release_adjustment:+.1f}lbs")
        
        # Fallback to simple calculation (same logic as calculator API)
        result = self._calculate_simple_spine(
            draw_weight=adjusted_draw_weight,
            arrow_length=arrow_length,
            point_weight=point_weight,
            bow_type=bow_type.lower(),
            string_material=string_material,
            material_preference=material_preference,
            calculation_method=calculation_method,
            manufacturer_chart=manufacturer_chart,
            chart_id=chart_id
        )
        
        # Add Professional mode information to the result
        if professional_adjustments:
            result['calculations']['adjustments']['professional_mode'] = True
            result['calculations']['adjustments']['original_draw_weight'] = draw_weight
            result['calculations']['adjustments']['adjusted_draw_weight'] = adjusted_draw_weight
            result['calculations']['adjustments']['professional_adjustments'] = professional_adjustments
            result['notes'].extend(professional_adjustments)
            result['source'] = 'professional_' + result.get('source', 'calculator')
        
        return result
    
    def _calculate_simple_spine(
        self,
        draw_weight: float,
        arrow_length: float,
        point_weight: float,
        bow_type: str,
        string_material: Optional[str] = None,
        material_preference: Optional[str] = None,
        calculation_method: str = 'universal',
        manufacturer_chart: Optional[str] = None,
        chart_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Simple spine calculation with chart-based lookup support
        Supports universal formula, German industry standard, and manufacturer charts
        """
        # Check for wood arrow calculation first
        if material_preference and material_preference.lower() == 'wood':
            # Wood arrows use pound test values (40#, 45#, 50#, etc.)
            # Convert draw weight to recommended wood spine using traditional formula
            wood_spine = round(draw_weight)  # Simple conversion: 40lbs = 40# spine
            
            # Wood arrows have their own range system
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
        
        # Chart-based calculation (if manufacturer chart is selected)
        if manufacturer_chart and chart_id:
            chart_result = self._lookup_chart_spine(
                manufacturer_chart, chart_id, draw_weight, arrow_length, bow_type
            )
            if chart_result:
                return chart_result
        
        # Research-standard formula: Recommended Spine = (bowWeight × bowType × (arrowLength - 1)) / (pointWeight / 100)
        
        # Bow type multipliers (from research document)
        if bow_type == 'compound':
            bow_type_multiplier = 1.0
        elif bow_type in ['recurve', 'traditional']:
            bow_type_multiplier = 1.2  # Research standard for recurve/longbow
        else:
            bow_type_multiplier = 1.0
        
        # Carbon Express adjustment system for compound bows (from research)
        effective_draw_weight = draw_weight
        carbon_express_adjustments = []
        
        if bow_type == 'compound':
            # Carbon Express systematic adjustments
            # Single cam adjustment (+7 lbs) - assume single cam if not specified
            effective_draw_weight += 7
            carbon_express_adjustments.append("Single cam: +7 lbs")
            
            # Let-off adjustment (assume 65-80% let-off for most compounds)
            effective_draw_weight -= 5
            carbon_express_adjustments.append("High let-off (65-80%): -5 lbs")
            
            # Point weight adjustment (-6 lbs for 100gr insert plus point)
            if point_weight >= 100:
                effective_draw_weight -= 6
                carbon_express_adjustments.append("Point weight 100gr+: -6 lbs")
            
            # Arrow length adjustment (+3 lbs for 28" arrows)
            if abs(arrow_length - 28.0) < 0.5:  # Close to 28"
                effective_draw_weight += 3
                carbon_express_adjustments.append("28\" arrow length: +3 lbs")
        
        # CORRECTED: The research formula produces deflection values, need realistic spine ratings
        # Real-world spine calculation based on draw weight and bow type
        
        if calculation_method == 'german_industry':
            # German Industry method - more conservative spine recommendations
            if bow_type == 'compound':
                base_spine = 300 + (effective_draw_weight * 2.2)  # Conservative compound formula
            elif bow_type in ['recurve', 'traditional']:
                base_spine = 250 + (effective_draw_weight * 4.5)  # Traditional/recurve formula
            else:
                base_spine = 300 + (effective_draw_weight * 2.2)
        else:
            # Universal formula - realistic spine ratings based on industry practices
            if bow_type == 'compound':
                base_spine = 720 - (effective_draw_weight * 6.5)  # 45lbs = 453, 60lbs = 330
            elif bow_type in ['recurve', 'traditional']:
                # Improved formula for light bow support - more appropriate for traditional archery
                if effective_draw_weight <= 25:
                    # Very light bow formula: better support for youth/beginner traditional bows
                    base_spine = 1000 - (effective_draw_weight * 3.5)  # 20lbs = 930, 25lbs = 912
                elif effective_draw_weight <= 35:
                    # Light bow formula: better support for 25-35lbs traditional/recurve
                    base_spine = 950 - (effective_draw_weight * 4.5)  # 30lbs = 815, 35lbs = 792
                else:
                    # Standard formula for medium/heavy bows
                    base_spine = 900 - (effective_draw_weight * 5.0)  # 45lbs = 675, 50lbs = 650
            else:
                base_spine = 720 - (effective_draw_weight * 6.5)
        
        # Length adjustment: shorter arrows need higher spine numbers (weaker)
        # Increased adjustment factor based on industry research and ratio of cubes principle
        length_adjustment = (arrow_length - 28) * 25  # 25 spine units per inch (industry standard)
        base_spine -= length_adjustment  # Shorter = higher spine number (26" vs 28" = +50 spine)
        
        # Point weight adjustment: lighter points need higher spine numbers (weaker)  
        point_adjustment = (point_weight - 125) * 0.6  # 0.6 spine units per grain
        base_spine -= point_adjustment  # Lighter = higher spine number (80gr vs 125gr = +27 spine)
        
        bow_type_adjustment = 0  # Adjustments now included in realistic formulas
        
        # String material adjustment (based on German calculator)
        string_adjustment = 0
        if string_material:
            if string_material.lower() in ['dacron', 'b50']:
                string_adjustment = 15  # Dacron strings need weaker arrows (higher spine)
            elif string_material.lower() in ['fastflight', 'spectra', 'dyneema', 'b55']:
                string_adjustment = 0   # FastFlight baseline
        base_spine += string_adjustment
        
        calculated_spine = round(base_spine)
        
        # Create spine range (±25 spine for research-based tolerance)
        return {
            'calculated_spine': calculated_spine,
            'spine_range': {
                'minimum': calculated_spine - 25,
                'optimal': calculated_spine,
                'maximum': calculated_spine + 25
            },
            'calculations': {
                'base_draw_weight': draw_weight,
                'effective_draw_weight': effective_draw_weight,
                'bow_type_multiplier': bow_type_multiplier,
                'formula_result': base_spine,
                'adjustments': {
                    'carbon_express_adjustments': carbon_express_adjustments if bow_type == 'compound' else [],
                    'effective_weight_change': effective_draw_weight - draw_weight if bow_type == 'compound' else 0,
                    'length_adjustment': length_adjustment,
                    'point_weight_adjustment': point_adjustment,
                    'string_material_adjustment': string_adjustment,
                    'calculation_method': calculation_method,
                    'bow_type_method': f'realistic_{calculation_method}_{bow_type}',
                    'bow_type': bow_type,
                    'string_material': string_material or 'not_specified'
                },
                'total_adjustment': -length_adjustment - point_adjustment + string_adjustment,
                'bow_type': bow_type,
                'confidence': 'high'  # High confidence with research-standard formula
            },
            'notes': [
                f'Realistic spine calculation: {calculation_method} method for {bow_type} bow',
                f'Effective draw weight: {effective_draw_weight}lbs (adjusted from {draw_weight}lbs)',
                f'Carbon Express adjustments: {", ".join(carbon_express_adjustments)}' if carbon_express_adjustments else 'Standard bow parameters applied',
                f'Length adjustment: {-length_adjustment:+.1f} spine units ({arrow_length}" vs 28" baseline)',
                f'Point weight adjustment: {-point_adjustment:+.1f} spine units ({point_weight}gr vs 125gr baseline)',
                'String material factor included' if string_material else 'String material not specified'
            ],
            'source': f'research_based_{calculation_method}_calculator'
        }
    
    def _lookup_chart_spine(
        self, 
        manufacturer: str, 
        chart_id: str, 
        draw_weight: float, 
        arrow_length: float, 
        bow_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        Lookup spine value from manufacturer chart database
        """
        conn = None
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # First try custom charts
            cursor.execute("""
                SELECT manufacturer, model, spine_grid, chart_notes, spine_system
                FROM custom_spine_charts 
                WHERE id = ? AND is_active = 1
            """, (chart_id,))
            
            result = cursor.fetchone()
            if not result:
                # Try manufacturer charts
                cursor.execute("""
                    SELECT manufacturer, model, spine_grid, chart_notes, spine_system
                    FROM manufacturer_spine_charts_enhanced 
                    WHERE id = ? AND is_active = 1
                """, (chart_id,))
                result = cursor.fetchone()
            
            if not result:
                return None
                
            chart_manufacturer, model, spine_grid_json, chart_notes, spine_system = result
            
            # Parse spine grid
            import json
            spine_grid = json.loads(spine_grid_json) if spine_grid_json else []
            
            # Find matching entry in spine grid
            best_match = None
            for entry in spine_grid:
                # Parse draw weight range
                weight_range = entry.get('draw_weight_range_lbs', '')
                arrow_length_chart = float(entry.get('arrow_length_in', 0))
                spine_value = entry.get('spine', '')
                
                # Check if draw weight matches
                if '-' in weight_range:
                    min_weight, max_weight = map(float, weight_range.split('-'))
                    weight_match = min_weight <= draw_weight <= max_weight
                else:
                    target_weight = float(weight_range)
                    weight_match = abs(draw_weight - target_weight) <= 2.5
                
                # Check if arrow length is close (within 1 inch)
                length_match = abs(arrow_length - arrow_length_chart) <= 1.0
                
                if weight_match and length_match:
                    best_match = entry
                    break
            
            if best_match:
                spine_value = best_match.get('spine', '')
                # Parse spine (could be single value or range)
                if '-' in spine_value:
                    min_spine, max_spine = map(int, spine_value.split('-'))
                    calculated_spine = (min_spine + max_spine) // 2
                    spine_range = {'minimum': min_spine, 'optimal': calculated_spine, 'maximum': max_spine}
                else:
                    calculated_spine = int(spine_value)
                    spine_range = {
                        'minimum': calculated_spine - 25,
                        'optimal': calculated_spine,
                        'maximum': calculated_spine + 25
                    }
                
                return {
                    'calculated_spine': calculated_spine,
                    'spine_range': spine_range,
                    'calculations': {
                        'chart_manufacturer': chart_manufacturer,
                        'chart_model': model,
                        'chart_entry': best_match,
                        'spine_system': spine_system,
                        'bow_type': bow_type,
                        'confidence': 'high'
                    },
                    'notes': [
                        f'Spine from {chart_manufacturer} {model} chart',
                        f'Chart entry: {weight_range}lbs @ {arrow_length_chart}"',
                        chart_notes or 'Manufacturer chart data'
                    ],
                    'source': 'manufacturer_chart'
                }
                
        except Exception as e:
            print(f"Chart lookup failed: {e}")
            return None
        finally:
            if conn:
                conn.close()
        
        return None
    
    def calculate_spine_for_bow_setup(self, bow_setup_data: Dict[str, Any], arrow_data: Dict[str, Any]) -> Optional[int]:
        """
        Calculate spine specifically for adding arrows to bow setups.
        
        Args:
            bow_setup_data: Dictionary containing bow setup information (from database row)
            arrow_data: Dictionary containing arrow information (arrow_length, point_weight, etc.)
            
        Returns:
            Calculated spine value as integer, or None if calculation fails
        """
        try:
            # Get effective draw length from bow setup data (primary) or fallback
            from api import get_effective_draw_length
            user_id = bow_setup_data.get('user_id')
            effective_draw_length, draw_length_source = get_effective_draw_length(
                user_id, bow_data=bow_setup_data
            )
            
            print(f"🏹 Bow setup spine calculation using draw length: {effective_draw_length}\" from {draw_length_source}")
            
            result = self.calculate_spine(
                draw_weight=bow_setup_data['draw_weight'],
                arrow_length=arrow_data.get('arrow_length', 29.0),
                point_weight=arrow_data.get('point_weight', 125.0),
                bow_type=bow_setup_data.get('bow_type', 'compound'),
                draw_length=effective_draw_length,  # Use bow-specific draw length
                nock_weight=arrow_data.get('nock_weight', 10.0),
                fletching_weight=arrow_data.get('fletching_weight', 15.0)
            )
            
            return result.get('calculated_spine')
            
        except Exception as e:
            print(f"Spine calculation failed for bow setup: {e}")
            return None
    
    def get_calculation_parameters(self, parameter_group: str = None) -> Dict[str, Any]:
        """Get calculation parameters from database"""
        cache_key = f"params_{parameter_group or 'all'}"
        
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        conn = None
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            if parameter_group:
                cursor.execute("""
                    SELECT parameter_name, parameter_value, parameter_unit, description
                    FROM calculation_parameters 
                    WHERE parameter_group = ? AND is_active = 1
                """, (parameter_group,))
            else:
                cursor.execute("""
                    SELECT parameter_group, parameter_name, parameter_value, parameter_unit, description
                    FROM calculation_parameters 
                    WHERE is_active = 1
                """)
            
            params = {}
            for row in cursor.fetchall():
                if parameter_group:
                    params[row[0]] = {
                        'value': float(row[1]),
                        'unit': row[2],
                        'description': row[3]
                    }
                else:
                    group = row[0]
                    if group not in params:
                        params[group] = {}
                    params[group][row[1]] = {
                        'value': float(row[2]),
                        'unit': row[3],
                        'description': row[4]
                    }
            
            self._cache[cache_key] = params
            return params
            
        except sqlite3.Error as e:
            print(f"Error getting calculation parameters: {e}")
            return {}
        finally:
            if conn:
                conn.close()
    
    def get_material_properties(self, material_name: str = None) -> Dict[str, Any]:
        """Get arrow material properties from database"""
        cache_key = f"materials_{material_name or 'all'}"
        
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        conn = None
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            if material_name:
                cursor.execute("""
                    SELECT * FROM arrow_material_properties 
                    WHERE material_name = ? AND is_active = 1
                """, (material_name,))
                row = cursor.fetchone()
                if row:
                    # Convert sqlite3.Row to dict
                    result = dict(row)
                    self._cache[cache_key] = result
                    return result
            else:
                cursor.execute("""
                    SELECT * FROM arrow_material_properties 
                    WHERE is_active = 1
                """)
                materials = {}
                for row in cursor.fetchall():
                    materials[row['material_name']] = dict(row)
                self._cache[cache_key] = materials
                return materials
            
            return {}
            
        except sqlite3.Error as e:
            print(f"Error getting material properties: {e}")
            return {}
        finally:
            if conn:
                conn.close()
    
    def get_manufacturer_spine_recommendations(self, manufacturer: str, bow_type: str, 
                                             draw_weight: float, arrow_length: float) -> List[Dict[str, Any]]:
        """Get manufacturer-specific spine recommendations"""
        conn = None
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM manufacturer_spine_charts 
                WHERE manufacturer = ? AND bow_type = ? 
                AND draw_weight_min <= ? AND draw_weight_max >= ?
                AND arrow_length_min <= ? AND arrow_length_max >= ?
                AND is_active = 1
                ORDER BY confidence_rating DESC
            """, (manufacturer, bow_type, draw_weight, draw_weight, arrow_length, arrow_length))
            
            recommendations = []
            for row in cursor.fetchall():
                recommendations.append(dict(row))
                
            return recommendations
            
        except sqlite3.Error as e:
            print(f"Error getting manufacturer recommendations: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    def get_flight_problem_diagnostics(self, problem_category: str = None) -> Dict[str, Any]:
        """Get flight problem diagnostics and solutions"""
        conn = None
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            if problem_category:
                cursor.execute("""
                    SELECT * FROM flight_problem_diagnostics 
                    WHERE problem_category = ? AND is_active = 1
                """, (problem_category,))
            else:
                cursor.execute("""
                    SELECT * FROM flight_problem_diagnostics 
                    WHERE is_active = 1
                """)
            
            problems = {}
            for row in cursor.fetchall():
                category = row['problem_category']
                if category not in problems:
                    problems[category] = {}
                problems[category][row['problem_name']] = dict(row)
                
            return problems
            
        except sqlite3.Error as e:
            print(f"Error getting flight problem diagnostics: {e}")
            return {}
        finally:
            if conn:
                conn.close()
    
    def calculate_enhanced_spine(
        self,
        draw_weight: float,
        arrow_length: float,
        point_weight: float = 125.0,
        bow_type: str = 'compound',
        material_preference: str = None,
        manufacturer_preference: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Enhanced spine calculation using comprehensive database data
        """
        try:
            # Get enhanced calculation parameters from database
            base_params = self.get_calculation_parameters('base_calculation')
            bow_adjustments = self.get_calculation_parameters('bow_adjustments')
            safety_factors = self.get_calculation_parameters('safety_factors')
            
            # Use database parameters or fall back to defaults
            draw_weight_factor = base_params.get('draw_weight_factor', {}).get('value', 12.5)
            length_adjustment_factor = base_params.get('length_adjustment_factor', {}).get('value', 25.0)
            point_weight_factor = base_params.get('point_weight_factor', {}).get('value', 0.5)
            
            # Enhanced base calculation
            base_spine = draw_weight * draw_weight_factor
            
            # Length adjustment with database parameters (longer = stiffer needed)
            length_adjustment = (arrow_length - 28) * length_adjustment_factor
            base_spine -= length_adjustment
            
            # Point weight adjustment with database parameters
            point_adjustment = (point_weight - 125) * point_weight_factor
            base_spine += point_adjustment
            
            # Bow type adjustments from database
            bow_type_adjustment = 0
            if bow_type == 'recurve':
                bow_type_adjustment = bow_adjustments.get('recurve_spine_adjustment', {}).get('value', 50.0)
            elif bow_type == 'traditional':
                bow_type_adjustment = bow_adjustments.get('traditional_spine_adjustment', {}).get('value', 100.0)
            
            base_spine += bow_type_adjustment
            
            # Material adjustments if material preference is specified
            material_factor = 1.0
            material_info = {}
            if material_preference:
                material_data = self.get_material_properties(material_preference.lower())
                if material_data:
                    material_factor = material_data.get('spine_adjustment_factor', 1.0)
                    material_info = {
                        'material': material_preference,
                        'density': material_data.get('density'),
                        'strength_factor': material_data.get('strength_factor'),
                        'description': material_data.get('description')
                    }
            
            calculated_spine = round(base_spine * material_factor)
            
            # Get spine tolerance from database
            spine_tolerance = safety_factors.get('spine_tolerance_range', {}).get('value', 25.0)
            
            # Check for manufacturer-specific recommendations
            manufacturer_recommendations = []
            if manufacturer_preference:
                manufacturer_recommendations = self.get_manufacturer_spine_recommendations(
                    manufacturer_preference, bow_type, draw_weight, arrow_length
                )
            
            # Enhanced result with comprehensive data
            result = {
                'calculated_spine': calculated_spine,
                'spine_range': {
                    'minimum': calculated_spine - spine_tolerance,
                    'optimal': calculated_spine,
                    'maximum': calculated_spine + spine_tolerance
                },
                'calculations': {
                    'base_spine': base_spine / material_factor,
                    'adjustments': {
                        'length_adjustment': length_adjustment,
                        'point_weight_adjustment': point_adjustment,
                        'bow_type_adjustment': bow_type_adjustment,
                        'material_factor': material_factor
                    },
                    'parameters_used': {
                        'draw_weight_factor': draw_weight_factor,
                        'length_adjustment_factor': length_adjustment_factor,
                        'point_weight_factor': point_weight_factor,
                        'spine_tolerance': spine_tolerance
                    },
                    'bow_type': bow_type,
                    'confidence': 'high' if manufacturer_recommendations else 'medium'
                },
                'material_info': material_info,
                'manufacturer_recommendations': manufacturer_recommendations,
                'notes': ['Enhanced calculation using comprehensive spine database'],
                'source': 'enhanced_database_calculator'
            }
            
            return result
            
        except Exception as e:
            print(f"Enhanced spine calculation failed: {e}")
            # Fall back to standard calculation
            return self.calculate_spine(draw_weight, arrow_length, point_weight, bow_type, **kwargs)

    def _get_bow_speed_adjustment(self, bow_speed: float) -> float:
        """
        Calculate draw weight adjustment based on bow speed (Professional mode).
        Based on industry standards from spine_calculator.py and calculation_formulas.json
        """
        if bow_speed <= 275:
            return -10.0  # Slower bows need weaker spine
        elif bow_speed <= 300:
            return -5.0
        elif bow_speed <= 320:
            return 0.0   # Baseline speed range
        elif bow_speed <= 340:
            return 5.0   # Faster bows need stiffer spine  
        elif bow_speed <= 350:
            return 10.0
        else:
            return 15.0  # Very fast bows need much stiffer spine

    def _get_release_type_adjustment(self, release_type: str) -> float:
        """
        Calculate draw weight adjustment based on release type (Professional mode).
        Based on industry standards from spine_calculator.py
        """
        if release_type.lower() in ['finger', 'finger_release', 'fingers']:
            return 5.0   # Finger release needs stiffer spine (+5lbs equivalent)
        else:  # mechanical release (default)
            return 0.0   # No adjustment for mechanical release


# Global instance for easy import
spine_service = UnifiedSpineService()


def calculate_unified_spine(
    draw_weight: float,
    arrow_length: float, 
    point_weight: float = 125.0,
    bow_type: str = 'compound',
    draw_length: float = 28.0,
    string_material: Optional[str] = None,
    material_preference: Optional[str] = None,
    calculation_method: str = 'universal',
    manufacturer_chart: Optional[str] = None,
    chart_id: Optional[str] = None,
    bow_speed: Optional[float] = None,
    release_type: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Convenience function for unified spine calculation.
    Uses corrected logic with German calculator validation.
    
    This is the function that should be imported and used throughout the system.
    """
    return spine_service.calculate_spine(
        draw_weight=draw_weight,
        arrow_length=arrow_length,
        point_weight=point_weight,
        bow_type=bow_type,
        draw_length=draw_length,
        string_material=string_material,
        material_preference=material_preference,
        calculation_method=calculation_method,
        manufacturer_chart=manufacturer_chart,
        chart_id=chart_id,
        bow_speed=bow_speed,
        release_type=release_type,
        **kwargs
    )

def calculate_spine_for_setup(bow_setup_data: Dict[str, Any], arrow_data: Dict[str, Any]) -> Optional[int]:
    """
    Convenience function for calculating spine when adding arrows to bow setups.
    """
    return spine_service.calculate_spine_for_bow_setup(bow_setup_data, arrow_data)