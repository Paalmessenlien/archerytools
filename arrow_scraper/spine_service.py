"""
Unified Spine Calculation Service

This module provides a single, centralized spine calculation service that ensures
all parts of the system use the same calculation logic as the calculator page.
All spine calculations across the system should use this service.
"""

from typing import Dict, Any, Optional
import json
from spine_calculator import SpineCalculator, BowConfiguration, BowType


class UnifiedSpineService:
    """
    Centralized spine calculation service that provides consistent calculations
    across the entire system. Uses the same logic as the calculator page.
    """
    
    def __init__(self):
        self.spine_calculator = SpineCalculator()
    
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