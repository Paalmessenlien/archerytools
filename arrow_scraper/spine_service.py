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
        shooting_style: str = 'standard',
        calculation_method: str = 'universal',
        manufacturer_chart: Optional[str] = None,
        chart_id: Optional[str] = None,
        bow_speed: Optional[float] = None,
        release_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate spine using reverted simple formulas with shooting style support.
        
        Args:
            draw_weight: Bow's marked draw weight in pounds
            arrow_length: Physical arrow length in inches
            point_weight: Point weight in grains (default 125)
            bow_type: 'compound', 'recurve', 'traditional', or 'longbow'
            draw_length: Bow's actual draw length in inches (important for calculations!)
            nock_weight: Nock weight in grains (default 10)
            fletching_weight: Fletching weight in grains (default 15)
            material_preference: Optional arrow material preference
            string_material: String material type for adjustments
            shooting_style: Shooting style ('standard', 'barebow', 'olympic', 'traditional', 'hunting', 'target')
            
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
            
        # Handle wood arrows - they use pound-test spine values instead of deflection values
        if material_preference and material_preference.lower() == 'wood':
            return self._calculate_wood_arrow_spine(
                draw_weight=draw_weight,
                arrow_length=arrow_length,
                point_weight=point_weight,
                bow_type=bow_type,
                string_material=string_material,
                shooting_style=shooting_style
            )
        
        # Always use the research-based simple calculator for all bow types
        # The old advanced calculator uses outdated Easton chart logic that doesn't match research standards
        print(f"🎯 Using research-based calculation for {bow_type} bow")
        
        # Check if chart-based calculation is requested (Professional Mode)
        if manufacturer_chart or chart_id:
            print(f"🎯 Using chart-based calculation: manufacturer={manufacturer_chart}, chart_id={chart_id}")
            chart_result = self._lookup_chart_spine(
                manufacturer_chart or '', 
                chart_id or '', 
                draw_weight, 
                arrow_length, 
                bow_type
            )
            
            if chart_result:
                # Apply Professional mode adjustments to chart-based result
                if bow_speed is not None or release_type is not None:
                    adjusted_draw_weight = draw_weight
                    professional_adjustments = []
                    
                    if bow_speed is not None:
                        speed_adjustment = self._get_bow_speed_adjustment(bow_speed)
                        adjusted_draw_weight += speed_adjustment
                        if speed_adjustment != 0:
                            professional_adjustments.append(f"Bow speed {bow_speed}fps: {speed_adjustment:+.1f}lbs")
                    
                    if release_type is not None:
                        release_adjustment = self._get_release_type_adjustment(release_type)
                        adjusted_draw_weight += release_adjustment
                        if release_adjustment != 0:
                            professional_adjustments.append(f"Release type {release_type}: {release_adjustment:+.1f}lbs")
                    
                    # Re-lookup with adjusted draw weight if significant change
                    if abs(adjusted_draw_weight - draw_weight) > 1.0:
                        adjusted_chart_result = self._lookup_chart_spine(
                            manufacturer_chart or '', 
                            chart_id or '', 
                            adjusted_draw_weight, 
                            arrow_length, 
                            bow_type
                        )
                        if adjusted_chart_result:
                            chart_result = adjusted_chart_result
                    
                    # Add professional adjustments to result
                    if professional_adjustments:
                        chart_result['calculations']['professional_mode'] = True
                        chart_result['calculations']['original_draw_weight'] = draw_weight
                        chart_result['calculations']['adjusted_draw_weight'] = adjusted_draw_weight
                        chart_result['calculations']['professional_adjustments'] = professional_adjustments
                        chart_result['notes'].extend(professional_adjustments)
                        chart_result['source'] = 'professional_chart_' + chart_result.get('source', 'calculator')
                
                return chart_result
            else:
                print(f"⚠️ Chart lookup failed, falling back to formula calculation")
        
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
        
        # Fallback to simple calculation (reverted to original formulas)
        result = self._calculate_simple_spine(
            draw_weight=adjusted_draw_weight,
            arrow_length=arrow_length,
            point_weight=point_weight,
            bow_type=bow_type.lower(),
            string_material=string_material,
            material_preference=material_preference,
            shooting_style=shooting_style.lower()
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
        shooting_style: str = 'standard'
    ) -> Dict[str, Any]:
        """
        Simple spine calculation - reverted to original formulas with shooting style support
        This ensures exact consistency with the original calculator logic.
        """
        # Wood arrows should use proper database lookup, not formula override
        # The database contains comprehensive wood arrow species data that should be used instead
        
        # CORRECTED SPINE CALCULATION - Higher draw weight = Lower spine numbers (stiffer)
        # Base calculation: Start with high number and divide by draw weight
        base_spine = 18000 / draw_weight  # Example: 25lb = 720, 50lb = 360
        
        # Adjust for arrow length (longer arrows need STIFFER = LOWER spine numbers)
        # Every 1" change = ±4% spine change (reduced from 10% - was too aggressive)
        length_factor = (arrow_length - 28) * 0.04
        base_spine = base_spine * (1 - length_factor)
        
        # Adjust for point weight (heavier points = stiffer arrows needed = lower spine)
        # Every 25 grains = ±5% spine change
        point_factor = (point_weight - 125) / 25 * 0.05
        base_spine = base_spine * (1 - point_factor)
        
        # Bow type adjustments - Recurve/Traditional need weaker arrows (higher spine)
        bow_type_multiplier = 1.0
        if bow_type == 'recurve':
            bow_type_multiplier = 1.15  # 15% weaker (higher spine number)
        elif bow_type == 'traditional':
            bow_type_multiplier = 1.25  # 25% weaker (higher spine number)
        
        base_spine = base_spine * bow_type_multiplier
        
        # String material adjustment - Dacron/B50 need weaker arrows (higher spine)
        string_multiplier = 1.0
        if string_material:
            if string_material.lower() in ['dacron', 'b50']:
                string_multiplier = 1.05  # 5% weaker (higher spine)
            elif string_material.lower() in ['fastflight', 'spectra', 'dyneema', 'b55']:
                string_multiplier = 1.0   # FastFlight baseline
        
        base_spine = base_spine * string_multiplier
        
        # Shooting style adjustments - Use multiplication for consistency
        shooting_style_multiplier = 1.0
        shooting_style_notes = []
        
        if shooting_style == 'standard':
            shooting_style_multiplier = 1.0  # No adjustments
        elif shooting_style == 'barebow':
            shooting_style_multiplier = 0.95  # 5% stiffer (lower spine) for string walking
            shooting_style_notes.append('Barebow style (string walking): stiffer arrows for accuracy')
        elif shooting_style == 'olympic':
            shooting_style_multiplier = 1.03  # 3% weaker for competition stability
            shooting_style_notes.append('Olympic style (stabilized): slightly weaker for precision')
        elif shooting_style == 'traditional':
            shooting_style_multiplier = 1.08  # 8% weaker for instinctive shooting
            shooting_style_notes.append('Traditional instinctive: weaker arrows for forgiving flight')
        elif shooting_style == 'hunting':
            shooting_style_multiplier = 1.05  # 5% weaker for heavier arrows
            shooting_style_notes.append('Hunting style: weaker spine for heavy broadhead compatibility')
        elif shooting_style == 'target':
            shooting_style_multiplier = 1.0  # Same as standard
            shooting_style_notes.append('Target competition: standard spine calculation')
        
        base_spine = base_spine * shooting_style_multiplier
        
        calculated_spine = round(base_spine)
        
        # Create spine range (±25 spine for tolerance)
        return {
            'calculated_spine': calculated_spine,
            'spine_range': {
                'minimum': calculated_spine - 25,
                'optimal': calculated_spine,
                'maximum': calculated_spine + 25
            },
            'calculations': {
                'base_spine': 18000 / draw_weight,
                'adjustments': {
                    'length_factor': length_factor,
                    'point_factor': point_factor,
                    'bow_type_multiplier': bow_type_multiplier,
                    'string_multiplier': string_multiplier,
                    'shooting_style_multiplier': shooting_style_multiplier,
                    'bow_type': bow_type,
                    'string_material': string_material or 'not_specified',
                    'shooting_style': shooting_style
                },
                'total_multiplier': (1 + length_factor) * (1 - point_factor) * bow_type_multiplier * string_multiplier * shooting_style_multiplier,
                'bow_type': bow_type,
                'confidence': 'high'  # High confidence with corrected formula
            },
            'notes': [
                f'CORRECTED spine calculation for {bow_type} bow (formula fixed)',
                f'Base calculation: 18000 ÷ {draw_weight}lbs = {18000/draw_weight:.1f}',
                f'Length factor: {length_factor:+.2f} ({arrow_length}" vs 28" baseline)',
                f'Point weight factor: {point_factor:+.3f} ({point_weight}gr vs 125gr baseline)',
                f'Bow type multiplier: {bow_type_multiplier:.2f}x',
                f'String material multiplier: {string_multiplier:.2f}x' if string_multiplier != 1.0 else 'No string material specified',
                *shooting_style_notes
            ],
            'source': 'corrected_spine_calculator'
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
            
            # If chart_id is provided, use specific chart
            if chart_id:
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
            
            # If no specific chart or chart lookup failed, find best matching chart for manufacturer
            elif manufacturer:
                # First try to find manufacturer chart marked as system default
                cursor.execute("""
                    SELECT manufacturer, model, spine_grid, chart_notes, spine_system
                    FROM manufacturer_spine_charts_enhanced 
                    WHERE manufacturer = ? AND bow_type = ? AND is_active = 1 AND is_system_default = 1
                    ORDER BY calculation_priority ASC
                    LIMIT 1
                """, (manufacturer, bow_type))
                result = cursor.fetchone()
                
                # If no system default, get best match for manufacturer
                if not result:
                    cursor.execute("""
                        SELECT manufacturer, model, spine_grid, chart_notes, spine_system
                        FROM manufacturer_spine_charts_enhanced 
                        WHERE manufacturer = ? AND bow_type = ? AND is_active = 1
                        ORDER BY calculation_priority ASC, created_at DESC
                        LIMIT 1
                    """, (manufacturer, bow_type))
                    result = cursor.fetchone()
            
            else:
                # No manufacturer specified - check for global system default
                cursor.execute("""
                    SELECT manufacturer, model, spine_grid, chart_notes, spine_system
                    FROM manufacturer_spine_charts_enhanced 
                    WHERE bow_type = ? AND is_active = 1 AND is_system_default = 1
                    ORDER BY calculation_priority ASC
                    LIMIT 1
                """, (bow_type,))
                result = cursor.fetchone()
                
                # Also check custom charts for system default
                if not result:
                    cursor.execute("""
                        SELECT manufacturer, model, spine_grid, chart_notes, spine_system
                        FROM custom_spine_charts 
                        WHERE bow_type = ? AND is_active = 1 AND is_system_default = 1
                        ORDER BY calculation_priority ASC
                        LIMIT 1
                    """, (bow_type,))
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
    
    def get_system_settings(self, category: str = None) -> Dict[str, Any]:
        """Get spine system settings"""
        conn = None
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            if category:
                cursor.execute("""
                    SELECT setting_name, setting_value, setting_type, description
                    FROM spine_system_settings 
                    WHERE category = ?
                    ORDER BY setting_name
                """, (category,))
            else:
                cursor.execute("""
                    SELECT category, setting_name, setting_value, setting_type, description
                    FROM spine_system_settings 
                    ORDER BY category, setting_name
                """)
            
            settings = {}
            for row in cursor.fetchall():
                if category:
                    setting_name, setting_value, setting_type, description = row
                    settings[setting_name] = {
                        'value': self._parse_setting_value(setting_value, setting_type),
                        'type': setting_type,
                        'description': description
                    }
                else:
                    cat, setting_name, setting_value, setting_type, description = row
                    if cat not in settings:
                        settings[cat] = {}
                    settings[cat][setting_name] = {
                        'value': self._parse_setting_value(setting_value, setting_type),
                        'type': setting_type,
                        'description': description
                    }
            
            return settings
            
        except sqlite3.Error as e:
            print(f"Error getting system settings: {e}")
            return {}
        finally:
            if conn:
                conn.close()
    
    def update_system_setting(self, setting_name: str, setting_value: str, user_id: str = None) -> bool:
        """Update a system setting"""
        conn = None
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE spine_system_settings 
                SET setting_value = ?, updated_at = CURRENT_TIMESTAMP, last_modified_by = ?
                WHERE setting_name = ?
            """, (setting_value, user_id, setting_name))
            
            success = cursor.rowcount > 0
            conn.commit()
            return success
            
        except sqlite3.Error as e:
            print(f"Error updating system setting: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def set_system_default_chart(self, chart_id: int, chart_type: str = 'manufacturer') -> bool:
        """Set a chart as the system default"""
        conn = None
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Clear all existing system defaults
            if chart_type == 'manufacturer':
                cursor.execute("UPDATE manufacturer_spine_charts_enhanced SET is_system_default = 0")
                cursor.execute("UPDATE manufacturer_spine_charts_enhanced SET is_system_default = 1 WHERE id = ?", (chart_id,))
            else:
                cursor.execute("UPDATE custom_spine_charts SET is_system_default = 0")
                cursor.execute("UPDATE custom_spine_charts SET is_system_default = 1 WHERE id = ?", (chart_id,))
            
            success = cursor.rowcount > 0
            conn.commit()
            return success
            
        except sqlite3.Error as e:
            print(f"Error setting system default chart: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def duplicate_spine_chart(self, chart_id: int, new_name: str, chart_type: str = 'manufacturer', user_id: str = None) -> Optional[int]:
        """Duplicate an existing spine chart for testing"""
        conn = None
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Get original chart data
            if chart_type == 'manufacturer':
                cursor.execute("""
                    SELECT manufacturer, model, bow_type, grid_definition, spine_grid, 
                           provenance, spine_system, chart_notes
                    FROM manufacturer_spine_charts_enhanced 
                    WHERE id = ? AND is_active = 1
                """, (chart_id,))
            else:
                cursor.execute("""
                    SELECT manufacturer, model, bow_type, grid_definition, spine_grid, 
                           spine_system, chart_notes
                    FROM custom_spine_charts 
                    WHERE id = ? AND is_active = 1
                """, (chart_id,))
            
            result = cursor.fetchone()
            if not result:
                return None
            
            # Create duplicate in custom charts table
            if chart_type == 'manufacturer':
                manufacturer, model, bow_type, grid_definition, spine_grid, provenance, spine_system, chart_notes = result
                cursor.execute("""
                    INSERT INTO custom_spine_charts 
                    (chart_name, manufacturer, model, bow_type, grid_definition, spine_grid, 
                     spine_system, chart_notes, created_by, overrides_manufacturer_chart)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                """, (new_name, manufacturer, model, bow_type, grid_definition, spine_grid, 
                      spine_system, f"Duplicated from {manufacturer} {model}. {chart_notes or ''}", user_id))
            else:
                manufacturer, model, bow_type, grid_definition, spine_grid, spine_system, chart_notes = result
                cursor.execute("""
                    INSERT INTO custom_spine_charts 
                    (chart_name, manufacturer, model, bow_type, grid_definition, spine_grid, 
                     spine_system, chart_notes, created_by, overrides_manufacturer_chart)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                """, (new_name, manufacturer, model, bow_type, grid_definition, spine_grid, 
                      spine_system, f"Duplicated chart. {chart_notes or ''}", user_id))
            
            new_chart_id = cursor.lastrowid
            conn.commit()
            return new_chart_id
            
        except sqlite3.Error as e:
            print(f"Error duplicating spine chart: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    def _parse_setting_value(self, value: str, setting_type: str):
        """Parse setting value based on type"""
        if setting_type == 'boolean':
            return value.lower() in ('true', '1', 'yes')
        elif setting_type == 'number':
            try:
                return float(value)
            except ValueError:
                return 0
        elif setting_type == 'json':
            try:
                import json
                return json.loads(value)
            except (json.JSONDecodeError, ValueError):
                return {}
        else:
            return value
    
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
        Reduced adjustment values to prevent "too soft" spine recommendations for heavy bows.
        """
        if bow_speed <= 275:
            return -3.0  # Slower bows need slightly weaker spine (reduced from -10.0)
        elif bow_speed <= 300:
            return -1.5  # Reduced from -5.0
        elif bow_speed <= 320:
            return 0.0   # Baseline speed range
        elif bow_speed <= 340:
            return 2.0   # Faster bows need slightly stiffer spine (reduced from 5.0)
        elif bow_speed <= 350:
            return 4.0   # Reduced from 10.0
        else:
            return 6.0   # Very fast bows need stiffer spine (reduced from 15.0)

    def _get_release_type_adjustment(self, release_type: str) -> float:
        """
        Calculate draw weight adjustment based on release type (Professional mode).
        Based on industry standards from spine_calculator.py
        """
        if release_type.lower() in ['finger', 'finger_release', 'fingers']:
            return 5.0   # Finger release needs stiffer spine (+5lbs equivalent)
        else:  # mechanical release (default)
            return 0.0   # No adjustment for mechanical release

    def _calculate_wood_arrow_spine(
        self,
        draw_weight: float,
        arrow_length: float,
        point_weight: float,
        bow_type: str,
        string_material: Optional[str] = None,
        shooting_style: str = 'standard'
    ) -> Dict[str, Any]:
        """
        Calculate spine for wood arrows using proper traditional wood arrow spine chart.
        
        Uses the established traditional wood arrow spine chart that maps draw weight 
        and arrow length to specific spine values in pounds, with adjustments for
        point weight and other factors.
        """
        print(f"🌳 Using traditional wood arrow spine chart for {bow_type} bow")
        
        # Get base spine from traditional wood arrow chart
        base_spine = self._get_wood_spine_from_chart(draw_weight, arrow_length)
        
        # Point weight adjustments based on traditional wood arrow methodology
        # Chart is based on 100gr points, with specific adjustment values
        point_weight_adjustments = {
            30: 1, 70: 2, 100: 3, 125: 4
        }
        
        # Find closest point weight in the adjustment table
        closest_point_weight = min(point_weight_adjustments.keys(), 
                                 key=lambda x: abs(x - point_weight))
        point_adjustment_value = point_weight_adjustments[closest_point_weight]
        
        # Baseline is 100gr (value 3), calculate adjustment
        baseline_adjustment = 3
        point_adjustment_diff = point_adjustment_value - baseline_adjustment
        
        # Apply point weight adjustment (each point moves spine by ~5#)
        spine_adjustment = point_adjustment_diff * 5
        final_spine = base_spine + spine_adjustment
        
        # Ensure spine stays within reasonable range for wood arrows (25-90#)
        final_spine = max(25, min(90, final_spine))
        
        # Wood arrows are sold in 5# ranges, provide appropriate range
        range_center = round(final_spine / 5) * 5
        if range_center < final_spine:
            range_center += 5
        
        spine_range = {
            'minimum': range_center - 2.5,
            'optimal': final_spine,
            'maximum': range_center + 2.5
        }
        
        return {
            'calculated_spine': round(spine_range['optimal']),
            'spine_range': spine_range,
            'spine_units': 'pounds',  # This tells the matching engine it's pound-test values
            'calculations': {
                'base_spine': base_spine,
                'adjustments': {
                    'point_weight_adjustment': spine_adjustment,
                    'point_weight': point_weight,
                    'bow_type': bow_type,
                    'shooting_style': shooting_style
                },
                'final_spine': final_spine,
                'range_center': range_center,
                'confidence': 'high'
            },
            'notes': [
                f'Wood arrow spine from traditional chart',
                f'Draw weight: {draw_weight}# @ {arrow_length}" → Base spine: {base_spine}#',
                f'Point weight adjustment: {spine_adjustment:+.1f}# ({point_weight}gr vs 100gr baseline)',
                f'Final spine: {final_spine}# → Range: {spine_range["minimum"]}-{spine_range["maximum"]}#',
                f'Wood arrows sold in 5# ranges (e.g., {range_center-5}-{range_center}#)',
                'Based on traditional wood arrow spine chart'
            ],
            'source': 'traditional_wood_arrow_chart'
        }
    
    def _get_wood_spine_from_chart(self, draw_weight: float, arrow_length: float) -> float:
        """Get wood spine value from traditional wood arrow chart (in pounds)"""
        
        # Traditional Wood Arrow Spine Chart
        # Format: draw_weight: {arrow_length: spine_value_in_pounds}
        wood_spine_chart = {
            30: {26: 32.5, 27: 32.5, 28: 35, 29: 37.5, 30: 42.5, 31: 47.5, 32: 47.5},
            35: {26: 35, 27: 35, 28: 37.5, 29: 42.5, 30: 47.5, 31: 52.5, 32: 52.5},
            40: {26: 37.5, 27: 37.5, 28: 42.5, 29: 47.5, 30: 52.5, 31: 57.5, 32: 62.5},
            45: {26: 42.5, 27: 42.5, 28: 47.5, 29: 52.5, 30: 57.5, 31: 62.5, 32: 67.5},
            50: {26: 47.5, 27: 47.5, 28: 52.5, 29: 57.5, 30: 62.5, 31: 67.5, 32: 77.5},
            55: {26: 52.5, 27: 52.5, 28: 57.5, 29: 62.5, 30: 67.5, 31: 72.5, 32: 77.5},
            60: {26: 57.5, 27: 57.5, 28: 62.5, 29: 67.5, 30: 72.5, 31: 77.5, 32: 82.5},
            65: {26: 62.5, 27: 62.5, 28: 67.5, 29: 72.5, 30: 77.5, 31: 82.5, 32: 87.5}
        }
        
        # Find closest draw weight
        available_weights = list(wood_spine_chart.keys())
        closest_weight = min(available_weights, key=lambda x: abs(x - draw_weight))
        
        # Find closest arrow length  
        weight_data = wood_spine_chart[closest_weight]
        available_lengths = list(weight_data.keys())
        closest_length = min(available_lengths, key=lambda x: abs(x - arrow_length))
        
        base_spine = weight_data[closest_length]
        
        # Interpolate if draw weight is significantly different
        if abs(draw_weight - closest_weight) > 2.5:
            if draw_weight > closest_weight:
                next_weight = min([w for w in available_weights if w > closest_weight], default=closest_weight)
                if next_weight != closest_weight:
                    lower_spine = wood_spine_chart[closest_weight][closest_length]
                    upper_spine = wood_spine_chart[next_weight].get(closest_length, lower_spine)
                    ratio = (draw_weight - closest_weight) / (next_weight - closest_weight)
                    base_spine = lower_spine + (upper_spine - lower_spine) * ratio
            else:
                prev_weight = max([w for w in available_weights if w < closest_weight], default=closest_weight)
                if prev_weight != closest_weight:
                    upper_spine = wood_spine_chart[closest_weight][closest_length]
                    lower_spine = wood_spine_chart[prev_weight].get(closest_length, upper_spine)
                    ratio = (closest_weight - draw_weight) / (closest_weight - prev_weight)
                    base_spine = upper_spine + (lower_spine - upper_spine) * ratio
        
        return base_spine


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
    shooting_style: str = 'standard',
    calculation_method: str = 'universal',
    manufacturer_chart: Optional[str] = None,
    chart_id: Optional[str] = None,
    bow_speed: Optional[float] = None,
    release_type: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Convenience function for unified spine calculation.
    Uses reverted simple formulas with shooting style support.
    
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
        shooting_style=shooting_style,
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