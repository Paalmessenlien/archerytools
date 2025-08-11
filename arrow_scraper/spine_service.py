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
        nock_weight: float = 10.0,
        fletching_weight: float = 15.0,
        material_preference: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate spine using the same logic as the calculator page API endpoint.
        
        Args:
            draw_weight: Bow's marked draw weight in pounds
            arrow_length: Physical arrow length in inches
            point_weight: Point weight in grains (default 125)
            bow_type: 'compound', 'recurve', 'traditional', or 'longbow'
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
        
        try:
            # Create BowConfiguration for advanced calculation
            bow_config = BowConfiguration(
                draw_weight=draw_weight,
                draw_length=28,  # Standard reference draw length (not used in spine calc)
                bow_type=BowType(bow_type.lower()),
                cam_type='medium',
                arrow_rest_type='drop_away'
            )
            
            # Try advanced calculation first
            try:
                spine_result = self.spine_calculator.calculate_required_spine(
                    bow_config,
                    arrow_length=arrow_length,
                    point_weight=point_weight,
                    nock_weight=nock_weight,
                    fletching_weight=fletching_weight,
                    material_preference=material_preference
                )
                
                return {
                    'calculated_spine': spine_result['calculated_spine'],
                    'spine_range': spine_result['spine_range'],
                    'calculations': {
                        'base_spine': spine_result.get('base_spine'),
                        'adjustments': spine_result.get('adjustments', {}),
                        'total_adjustment': spine_result.get('total_adjustment'),
                        'bow_type': spine_result.get('bow_type'),
                        'confidence': spine_result.get('confidence', 'high')
                    },
                    'notes': spine_result.get('notes', []),
                    'source': 'advanced_calculator'
                }
                
            except Exception as e:
                print(f"Advanced spine calculation failed: {e}")
                # Fall through to simple calculation
                pass
                
        except Exception as e:
            print(f"BowConfiguration creation failed: {e}")
            # Fall through to simple calculation
            pass
        
        # Fallback to simple calculation (same logic as calculator API)
        return self._calculate_simple_spine(
            draw_weight=draw_weight,
            arrow_length=arrow_length,
            point_weight=point_weight,
            bow_type=bow_type.lower()
        )
    
    def _calculate_simple_spine(
        self,
        draw_weight: float,
        arrow_length: float,
        point_weight: float,
        bow_type: str
    ) -> Dict[str, Any]:
        """
        Simple spine calculation - identical to calculate_simple_spine in api.py
        This ensures exact consistency with the calculator fallback logic.
        """
        # Basic spine calculation based on draw weight and arrow length
        base_spine = draw_weight * 12.5
        
        # Adjust for arrow length (longer = weaker/higher spine number)
        length_adjustment = (arrow_length - 28) * 25
        base_spine += length_adjustment
        
        # Adjust for point weight (heavier = weaker/higher spine number) 
        point_adjustment = (point_weight - 125) * 0.5
        base_spine += point_adjustment
        
        # Bow type adjustments
        bow_type_adjustment = 0
        if bow_type == 'recurve':
            bow_type_adjustment = 50  # Recurve typically needs weaker arrows
            base_spine += bow_type_adjustment
        elif bow_type == 'traditional':
            bow_type_adjustment = 100  # Traditional bows need even weaker arrows
            base_spine += bow_type_adjustment
        
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
                'base_spine': base_spine - length_adjustment - point_adjustment - bow_type_adjustment,
                'adjustments': {
                    'length_adjustment': length_adjustment,
                    'point_weight_adjustment': point_adjustment,
                    'bow_type_adjustment': bow_type_adjustment,
                    'bow_type': bow_type
                },
                'total_adjustment': length_adjustment + point_adjustment + bow_type_adjustment,
                'bow_type': bow_type,
                'confidence': 'medium'
            },
            'notes': ['Calculated using simplified spine formula'],
            'source': 'simple_calculator'
        }
    
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
            result = self.calculate_spine(
                draw_weight=bow_setup_data['draw_weight'],
                arrow_length=arrow_data.get('arrow_length', 29.0),
                point_weight=arrow_data.get('point_weight', 125.0),
                bow_type=bow_setup_data.get('bow_type', 'compound'),
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
            
            # Length adjustment with database parameters
            length_adjustment = (arrow_length - 28) * length_adjustment_factor
            base_spine += length_adjustment
            
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


# Global instance for easy import
spine_service = UnifiedSpineService()


def calculate_unified_spine(
    draw_weight: float,
    arrow_length: float, 
    point_weight: float = 125.0,
    bow_type: str = 'compound',
    **kwargs
) -> Dict[str, Any]:
    """
    Convenience function for unified spine calculation.
    Uses the same logic as the calculator page.
    
    This is the function that should be imported and used throughout the system.
    """
    return spine_service.calculate_spine(
        draw_weight=draw_weight,
        arrow_length=arrow_length,
        point_weight=point_weight,
        bow_type=bow_type,
        **kwargs
    )

def calculate_spine_for_setup(bow_setup_data: Dict[str, Any], arrow_data: Dict[str, Any]) -> Optional[int]:
    """
    Convenience function for calculating spine when adding arrows to bow setups.
    """
    return spine_service.calculate_spine_for_bow_setup(bow_setup_data, arrow_data)