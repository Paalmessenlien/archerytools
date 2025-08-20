#!/usr/bin/env python3
"""
Enhanced Interactive Tuning System - Rule Engine
Provides intelligent tuning recommendations based on test results and bow type
"""

import json
import math
from typing import Dict, List, Any, Tuple, Optional
from abc import ABC, abstractmethod
from datetime import datetime
import numpy as np
from scipy import stats

class TuningRuleEngine:
    """Base class for all tuning rule processing"""
    
    def __init__(self, bow_type: str, handedness: str = 'RH'):
        """
        Initialize tuning rule engine
        
        Args:
            bow_type: "compound", "recurve", "barebow" 
            handedness: "RH" (right-handed) or "LH" (left-handed)
        """
        self.bow_type = bow_type.lower()
        self.handedness = handedness.upper()
        
    def analyze_test_result(self, test_type: str, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze test data and generate recommendations
        
        Args:
            test_type: "paper_tuning", "bareshaft_tuning", "walkback_tuning"
            test_data: Test-specific measurement data
            
        Returns:
            Dict containing recommendations, confidence score, and analysis
        """
        if test_type == 'paper_tuning':
            paper_engine = PaperTuningRules(self.bow_type, self.handedness)
            return paper_engine._analyze_paper_tuning(test_data)
        elif test_type == 'bareshaft_tuning':
            bareshaft_engine = BareshaftTuningRules(self.bow_type, self.handedness)
            return bareshaft_engine._analyze_bareshaft_tuning(test_data)
        elif test_type == 'walkback_tuning':
            walkback_engine = WalkbackTuningRules(self.bow_type, self.handedness)
            return walkback_engine._analyze_walkback_tuning(test_data)
        else:
            raise ValueError(f"Unknown test type: {test_type}")
            
    def _flip_direction_for_lh(self, direction: str) -> str:
        """Flip left/right directions for left-handed archers"""
        # Ensure direction is a string to prevent float.lower() error
        if not isinstance(direction, str):
            direction = str(direction)
            
        if self.handedness == 'LH':
            if 'left' in direction.lower():
                return direction.replace('left', 'right').replace('LEFT', 'RIGHT')
            elif 'right' in direction.lower():
                return direction.replace('right', 'left').replace('RIGHT', 'LEFT')
        return direction
    
    def _calculate_confidence_score(self, recommendations: List[Dict]) -> float:
        """Calculate confidence score based on recommendation clarity and consistency"""
        if not recommendations:
            return 0.0
            
        # Base confidence on number of clear recommendations
        base_confidence = min(90.0, len(recommendations) * 30.0)
        
        # Reduce confidence if conflicting recommendations
        priorities = [r.get('priority', 5) for r in recommendations]
        if len(set(priorities)) > 2:
            base_confidence *= 0.8
            
        return max(50.0, min(95.0, base_confidence))

class PaperTuningRules(TuningRuleEngine):
    """Paper tuning rule implementation based on documentation"""
    
    def _analyze_paper_tuning(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze paper tuning test results
        
        Expected test_data format:
        {
            "tear_direction": "left|right|high|low|nock-left|nock-high|clean",
            "tear_magnitude": "slight|moderate|severe",
            "consistency": "consistent|inconsistent",
            "shooting_distance": 3.0  # meters
        }
        """
        # Ensure all values are strings before calling .lower()
        tear_direction = str(test_data.get('tear_direction', '')).lower()
        tear_magnitude = str(test_data.get('tear_magnitude', 'moderate')).lower()
        consistency = str(test_data.get('consistency', 'consistent')).lower()
        
        # Flip direction for left-handed archers
        tear_direction = self._flip_direction_for_lh(tear_direction)
        
        recommendations = []
        
        # Prioritize vertical issues first (per documentation)
        if 'high' in tear_direction or 'low' in tear_direction:
            recommendations.extend(self._get_vertical_recommendations(tear_direction, tear_magnitude))
            
        # Then handle horizontal issues
        if 'left' in tear_direction or 'right' in tear_direction:
            recommendations.extend(self._get_horizontal_recommendations(tear_direction, tear_magnitude))
            
        # Handle diagonal tears
        if 'nock-left' in tear_direction or 'nock-right' in tear_direction:
            recommendations.extend(self._get_diagonal_recommendations(tear_direction, tear_magnitude))
            
        # Clean hole - good result
        if 'clean' in tear_direction or not tear_direction:
            recommendations.append({
                'component': 'none',
                'action': 'maintain',
                'magnitude': 'current settings',
                'reason': 'Clean hole - excellent tuning',
                'priority': 1
            })
        
        # Adjust confidence based on consistency
        confidence_modifier = 1.0 if consistency == 'consistent' else 0.7
        confidence_score = self._calculate_confidence_score(recommendations) * confidence_modifier
        
        # Add special notes for inconsistent tears
        if consistency == 'inconsistent':
            recommendations.append({
                'component': 'clearance_check',
                'action': 'check_clearance',
                'magnitude': 'powder test recommended',
                'reason': 'Inconsistent tears may indicate clearance issues',
                'priority': 1
            })
        
        return {
            'recommendations': recommendations,
            'confidence_score': confidence_score,
            'analysis': {
                'tear_direction': tear_direction,
                'tear_magnitude': tear_magnitude,
                'consistency': consistency,
                'primary_issue': self._identify_primary_issue(tear_direction),
                'next_step': 'Make single adjustment and retest'
            }
        }
    
    def _get_vertical_recommendations(self, tear_direction: str, magnitude: str) -> List[Dict]:
        """Get recommendations for vertical tear issues"""
        recommendations = []
        adjustment_amount = self._get_adjustment_amount(magnitude, 'vertical')
        
        if 'high' in tear_direction:
            if self.bow_type == 'compound':
                recommendations.append({
                    'component': 'nocking_point',
                    'action': 'lower',
                    'magnitude': adjustment_amount,
                    'reason': 'High tear - lower nocking point',
                    'priority': 1
                })
                recommendations.append({
                    'component': 'launcher_blade',
                    'action': 'stiffen',
                    'magnitude': 'slight adjustment',
                    'reason': 'Alternative: stiffen launcher blade',
                    'priority': 2
                })
            else:  # recurve/barebow
                recommendations.append({
                    'component': 'nocking_point',
                    'action': 'lower',
                    'magnitude': adjustment_amount,
                    'reason': 'High tear - lower nocking point',
                    'priority': 1
                })
                
        elif 'low' in tear_direction:
            if self.bow_type == 'compound':
                recommendations.append({
                    'component': 'nocking_point',
                    'action': 'raise',
                    'magnitude': adjustment_amount,
                    'reason': 'Low tear - raise nocking point',
                    'priority': 1
                })
                recommendations.append({
                    'component': 'launcher_blade',
                    'action': 'soften',
                    'magnitude': 'slight adjustment',
                    'reason': 'Alternative: soften launcher blade',
                    'priority': 2
                })
            else:  # recurve/barebow
                recommendations.append({
                    'component': 'nocking_point',
                    'action': 'raise',
                    'magnitude': adjustment_amount,
                    'reason': 'Low tear - raise nocking point',
                    'priority': 1
                })
        
        return recommendations
    
    def _get_horizontal_recommendations(self, tear_direction: str, magnitude: str) -> List[Dict]:
        """Get recommendations for horizontal tear issues"""
        recommendations = []
        adjustment_amount = self._get_adjustment_amount(magnitude, 'horizontal')
        
        if 'left' in tear_direction:
            if self.bow_type == 'compound':
                recommendations.append({
                    'component': 'rest',
                    'action': 'move_in',
                    'magnitude': adjustment_amount,
                    'reason': 'Left tear indicates arrow too stiff - move rest IN',
                    'priority': 2  # After vertical issues
                })
            else:  # recurve/barebow
                recommendations.append({
                    'component': 'plunger',
                    'action': 'reduce_tension',
                    'magnitude': '-1/4 turn',
                    'reason': 'Left tear indicates arrow too stiff - reduce plunger tension',
                    'priority': 2
                })
                
        elif 'right' in tear_direction:
            if self.bow_type == 'compound':
                recommendations.append({
                    'component': 'rest',
                    'action': 'move_out',
                    'magnitude': adjustment_amount,
                    'reason': 'Right tear indicates arrow too weak - move rest OUT',
                    'priority': 2
                })
            else:  # recurve/barebow
                recommendations.append({
                    'component': 'plunger',
                    'action': 'increase_tension',
                    'magnitude': '+1/4 turn',
                    'reason': 'Right tear indicates arrow too weak - increase plunger tension',
                    'priority': 2
                })
        
        return recommendations
    
    def _get_diagonal_recommendations(self, tear_direction: str, magnitude: str) -> List[Dict]:
        """Get recommendations for diagonal tear patterns"""
        recommendations = []
        
        # Handle diagonal tears by addressing both components
        if 'nock-left' in tear_direction:
            # Combination of high and left
            recommendations.extend(self._get_vertical_recommendations('high', magnitude))
            recommendations.extend(self._get_horizontal_recommendations('left', magnitude))
        elif 'nock-right' in tear_direction:
            # Combination of high and right
            recommendations.extend(self._get_vertical_recommendations('high', magnitude))
            recommendations.extend(self._get_horizontal_recommendations('right', magnitude))
            
        return recommendations
    
    def _get_adjustment_amount(self, magnitude: str, direction: str) -> str:
        """Get appropriate adjustment amount based on tear magnitude"""
        if direction == 'vertical':
            if magnitude == 'slight':
                return '0.5 mm'
            elif magnitude == 'moderate':
                return '0.5-1.0 mm'
            else:  # severe
                return '1.0-1.5 mm'
        else:  # horizontal
            if magnitude == 'slight':
                return '0.3 mm'
            elif magnitude == 'moderate':
                return '0.3-0.6 mm'
            else:  # severe
                return '0.6-0.9 mm'
    
    def _identify_primary_issue(self, tear_direction: str) -> str:
        """Identify the primary tuning issue from tear direction"""
        if 'high' in tear_direction or 'low' in tear_direction:
            return 'vertical_alignment'
        elif 'left' in tear_direction or 'right' in tear_direction:
            return 'spine_tuning'
        elif 'clean' in tear_direction:
            return 'well_tuned'
        else:
            return 'mixed_issues'

class BareshaftTuningRules(TuningRuleEngine):
    """Bareshaft tuning rule implementation"""
    
    def _analyze_bareshaft_tuning(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze bareshaft tuning test results
        
        Expected test_data format:
        {
            "bareshaft_offset": "left|right|high|low",
            "offset_distance_cm": 6.5,  # Distance in cm from fletched group
            "shooting_distance_m": 20,  # Test distance in meters
            "group_consistency": "tight|loose"
        }
        """
        # Ensure string values are strings before calling .lower()
        offset_direction = str(test_data.get('bareshaft_offset', '')).lower()
        offset_cm = test_data.get('offset_distance_cm', 0)
        distance_m = test_data.get('shooting_distance_m', 20)
        consistency = str(test_data.get('group_consistency', 'tight')).lower()
        
        # Flip direction for left-handed archers
        offset_direction = self._flip_direction_for_lh(offset_direction)
        
        recommendations = []
        
        # Check if within tolerance (5-7 cm at 20m per documentation)
        tolerance_cm = 7.0  # Upper limit of acceptable range
        scaled_tolerance = tolerance_cm * (distance_m / 20.0)  # Scale for different distances
        
        if offset_cm <= scaled_tolerance:
            recommendations.append({
                'component': 'none',
                'action': 'maintain',
                'magnitude': 'current settings',
                'reason': f'Bareshaft within acceptable tolerance ({offset_cm:.1f}cm ≤ {scaled_tolerance:.1f}cm)',
                'priority': 1
            })
        else:
            # Generate adjustment recommendations
            if 'left' in offset_direction or 'right' in offset_direction:
                recommendations.extend(self._get_horizontal_bareshaft_recommendations(offset_direction, offset_cm, distance_m))
                
            if 'high' in offset_direction or 'low' in offset_direction:
                recommendations.extend(self._get_vertical_bareshaft_recommendations(offset_direction, offset_cm))
        
        # Calculate confidence based on consistency and offset magnitude
        confidence_modifier = 1.0 if consistency == 'tight' else 0.8
        offset_factor = max(0.7, 1.0 - (offset_cm - scaled_tolerance) / 10.0)  # Reduce confidence for large offsets
        confidence_score = self._calculate_confidence_score(recommendations) * confidence_modifier * offset_factor
        
        return {
            'recommendations': recommendations,
            'confidence_score': confidence_score,
            'analysis': {
                'offset_direction': offset_direction,
                'offset_cm': offset_cm,
                'tolerance_cm': scaled_tolerance,
                'within_tolerance': offset_cm <= scaled_tolerance,
                'spine_indication': self._interpret_spine_indication(offset_direction),
                'next_step': 'Make adjustment and retest'
            }
        }
    
    def _get_horizontal_bareshaft_recommendations(self, direction: str, offset_cm: float, distance_m: float) -> List[Dict]:
        """Get recommendations for horizontal bareshaft offset"""
        recommendations = []
        adjustment_magnitude = self._calculate_bareshaft_adjustment(offset_cm, distance_m)
        
        if 'left' in direction:
            if self.bow_type == 'compound':
                recommendations.append({
                    'component': 'rest',
                    'action': 'move_in',
                    'magnitude': adjustment_magnitude,
                    'reason': f'Bareshafts {offset_cm:.1f}cm left - arrow too stiff',
                    'priority': 1
                })
                recommendations.append({
                    'component': 'point_weight',
                    'action': 'reduce',
                    'magnitude': '5-10 grains',
                    'reason': 'Alternative: reduce point weight to weaken spine',
                    'priority': 2
                })
            else:  # recurve/barebow
                recommendations.append({
                    'component': 'plunger',
                    'action': 'reduce_tension',
                    'magnitude': '-1/4 turn',
                    'reason': f'Bareshafts {offset_cm:.1f}cm left - arrow too stiff',
                    'priority': 1
                })
                recommendations.append({
                    'component': 'rest',
                    'action': 'move_in',
                    'magnitude': '0.5 mm',
                    'reason': 'Alternative: move rest IN slightly',
                    'priority': 2
                })
                
        elif 'right' in direction:
            if self.bow_type == 'compound':
                recommendations.append({
                    'component': 'rest',
                    'action': 'move_out',
                    'magnitude': adjustment_magnitude,
                    'reason': f'Bareshafts {offset_cm:.1f}cm right - arrow too weak',
                    'priority': 1
                })
                recommendations.append({
                    'component': 'point_weight',
                    'action': 'increase',
                    'magnitude': '5-10 grains',
                    'reason': 'Alternative: increase point weight to stiffen spine',
                    'priority': 2
                })
            else:  # recurve/barebow
                recommendations.append({
                    'component': 'plunger',
                    'action': 'increase_tension',
                    'magnitude': '+1/4 turn',
                    'reason': f'Bareshafts {offset_cm:.1f}cm right - arrow too weak',
                    'priority': 1
                })
                recommendations.append({
                    'component': 'rest',
                    'action': 'move_out',
                    'magnitude': '0.5 mm',
                    'reason': 'Alternative: move rest OUT slightly',
                    'priority': 2
                })
        
        return recommendations
    
    def _get_vertical_bareshaft_recommendations(self, direction: str, offset_cm: float) -> List[Dict]:
        """Get recommendations for vertical bareshaft offset"""
        recommendations = []
        
        if 'high' in direction:
            recommendations.append({
                'component': 'nocking_point',
                'action': 'raise',
                'magnitude': '0.5-1.0 mm',
                'reason': f'Bareshafts group high - nocking point too low',
                'priority': 1
            })
        elif 'low' in direction:
            recommendations.append({
                'component': 'nocking_point',
                'action': 'lower',
                'magnitude': '0.5-1.0 mm',
                'reason': f'Bareshafts group low - nocking point too high',
                'priority': 1
            })
        
        return recommendations
    
    def _calculate_bareshaft_adjustment(self, offset_cm: float, distance_m: float) -> str:
        """Calculate appropriate rest adjustment based on bareshaft offset"""
        # Scale adjustment based on offset magnitude
        base_adjustment = 0.3  # mm
        offset_factor = max(1.0, offset_cm / 5.0)  # Increase adjustment for larger offsets
        distance_factor = distance_m / 20.0  # Scale for distance
        
        adjustment = base_adjustment * offset_factor * distance_factor
        
        if adjustment < 0.5:
            return '0.3-0.6 mm'
        elif adjustment < 0.8:
            return '0.6-0.8 mm'
        else:
            return '0.8-1.0 mm'
    
    def _interpret_spine_indication(self, direction: str) -> str:
        """Interpret what the bareshaft offset indicates about spine"""
        if 'left' in direction:
            return 'arrow_too_stiff'
        elif 'right' in direction:
            return 'arrow_too_weak'
        else:
            return 'spine_appropriate'

class WalkbackTuningRules(TuningRuleEngine):
    """Walkback line tuning rule implementation"""
    
    def _analyze_walkback_tuning(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze walkback tuning test results
        
        Expected test_data format:
        {
            "distances_m": [5, 10, 15, 20, 30],
            "x_offsets_cm": [1.2, 2.1, 3.5, 4.8, 7.2],  # horizontal offsets from center line
            "group_sizes_cm": [2.1, 2.3, 2.8, 3.2, 4.1],  # optional group size data
            "reference_distance": 20  # distance where offsets are measured from
        }
        """
        distances = np.array(test_data.get('distances_m', []))
        offsets = np.array(test_data.get('x_offsets_cm', []))
        
        if len(distances) != len(offsets) or len(distances) < 3:
            raise ValueError("Need at least 3 distance/offset pairs for walkback analysis")
        
        # Flip offsets for left-handed archers
        if self.handedness == 'LH':
            offsets = -offsets
        
        # Perform linear regression to calculate slope and linearity
        slope, intercept, r_value, p_value, std_err = stats.linregress(distances, offsets)
        r_squared = r_value ** 2
        
        # Get tolerances based on bow type (from documentation)
        slope_tolerance, intercept_tolerance = self._get_walkback_tolerances()
        
        recommendations = []
        
        # Analyze slope (drift over distance)
        if abs(slope) <= slope_tolerance:
            recommendations.append({
                'component': 'alignment',
                'action': 'maintain',
                'magnitude': 'current settings',
                'reason': f'Slope {slope:.3f} cm/m within tolerance (≤{slope_tolerance:.2f})',
                'priority': 1
            })
        else:
            recommendations.extend(self._get_slope_recommendations(slope, slope_tolerance))
        
        # Analyze intercept (offset at zero distance)  
        if abs(intercept) > intercept_tolerance:
            recommendations.extend(self._get_intercept_recommendations(intercept, intercept_tolerance))
        
        # Analyze linearity
        if r_squared < 0.8:
            recommendations.append({
                'component': 'form_clearance',
                'action': 'check_issues',
                'magnitude': 'investigate',
                'reason': f'Low linearity (R²={r_squared:.2f}) suggests form or clearance issues',
                'priority': 1
            })
        
        # Calculate confidence based on linearity and measurement quality
        linearity_factor = min(1.0, r_squared + 0.2)  # Boost slightly for R² calculation
        confidence_score = self._calculate_confidence_score(recommendations) * linearity_factor
        
        return {
            'recommendations': recommendations,
            'confidence_score': confidence_score,
            'analysis': {
                'slope_cm_per_m': slope,
                'intercept_cm': intercept,
                'r_squared': r_squared,
                'slope_tolerance': slope_tolerance,
                'within_slope_tolerance': abs(slope) <= slope_tolerance,
                'drift_direction': 'right' if slope > 0 else 'left' if slope < 0 else 'none',
                'next_step': self._determine_next_walkback_step(slope, intercept, r_squared)
            }
        }
    
    def _get_walkback_tolerances(self) -> Tuple[float, float]:
        """Get slope and intercept tolerances based on bow type"""
        # From documentation: slope tolerances in cm/m
        slope_tolerances = {
            'compound': 0.10,
            'recurve': 0.15,
            'barebow': 0.20
        }
        
        # Intercept tolerances in cm
        intercept_tolerances = {
            'compound': 0.7,
            'recurve': 1.0,
            'barebow': 1.5
        }
        
        return slope_tolerances.get(self.bow_type, 0.15), intercept_tolerances.get(self.bow_type, 1.0)
    
    def _get_slope_recommendations(self, slope: float, tolerance: float) -> List[Dict]:
        """Get recommendations for slope correction"""
        recommendations = []
        adjustment_magnitude = self._calculate_slope_adjustment(slope, tolerance)
        
        if slope > tolerance:  # Drifting right
            if self.bow_type == 'compound':
                recommendations.append({
                    'component': 'rest',
                    'action': 'move_left',
                    'magnitude': adjustment_magnitude,
                    'reason': f'Drift {slope:.3f} cm/m right - move rest LEFT',
                    'priority': 1
                })
            else:  # recurve/barebow
                recommendations.append({
                    'component': 'plunger',
                    'action': 'reduce_tension',
                    'magnitude': '-1/8 to -1/4 turn',
                    'reason': f'Drift {slope:.3f} cm/m right - reduce plunger tension',
                    'priority': 1
                })
                recommendations.append({
                    'component': 'rest',
                    'action': 'move_in',
                    'magnitude': '0.5 mm',
                    'reason': 'Alternative: move rest IN',
                    'priority': 2
                })
                
        elif slope < -tolerance:  # Drifting left
            if self.bow_type == 'compound':
                recommendations.append({
                    'component': 'rest',
                    'action': 'move_right',
                    'magnitude': adjustment_magnitude,
                    'reason': f'Drift {abs(slope):.3f} cm/m left - move rest RIGHT',
                    'priority': 1
                })
            else:  # recurve/barebow
                recommendations.append({
                    'component': 'plunger',
                    'action': 'increase_tension',
                    'magnitude': '+1/8 to +1/4 turn',
                    'reason': f'Drift {abs(slope):.3f} cm/m left - increase plunger tension',
                    'priority': 1
                })
                recommendations.append({
                    'component': 'rest',
                    'action': 'move_out',
                    'magnitude': '0.5 mm',
                    'reason': 'Alternative: move rest OUT',
                    'priority': 2
                })
        
        return recommendations
    
    def _get_intercept_recommendations(self, intercept: float, tolerance: float) -> List[Dict]:
        """Get recommendations for intercept correction"""
        recommendations = []
        
        if abs(intercept) > tolerance:
            recommendations.append({
                'component': 'sight',
                'action': 'adjust_windage',
                'magnitude': f'{abs(intercept):.1f}cm adjustment',
                'reason': f'Residual offset {intercept:.1f}cm - adjust sight windage',
                'priority': 2
            })
        
        return recommendations
    
    def _calculate_slope_adjustment(self, slope: float, tolerance: float) -> str:
        """Calculate appropriate rest adjustment for slope correction"""
        excess_slope = abs(slope) - tolerance
        
        if excess_slope < 0.05:
            return '0.2-0.4 mm'
        elif excess_slope < 0.10:
            return '0.4-0.6 mm'
        else:
            return '0.6-0.8 mm'
    
    def _determine_next_walkback_step(self, slope: float, intercept: float, r_squared: float) -> str:
        """Determine the next recommended step in walkback tuning"""
        if r_squared < 0.8:
            return 'Investigate form consistency and clearance issues'
        elif abs(slope) > self._get_walkback_tolerances()[0]:
            return 'Make rest/plunger adjustment and retest'
        elif abs(intercept) > self._get_walkback_tolerances()[1]:
            return 'Adjust sight windage to center groups'
        else:
            return 'Walkback tuning complete - excellent results'

# Factory function for creating rule engines
def create_tuning_rule_engine(bow_type: str, handedness: str = 'RH') -> TuningRuleEngine:
    """
    Factory function to create appropriate rule engine
    
    Args:
        bow_type: "compound", "recurve", "barebow"
        handedness: "RH" or "LH"
        
    Returns:
        TuningRuleEngine instance
    """
    return TuningRuleEngine(bow_type, handedness)

# Helper functions for test result processing
def calculate_test_number(user_id: int, arrow_id: int, bow_setup_id: int, 
                         arrow_length: float, point_weight: float, 
                         test_type: str, conn) -> int:
    """Calculate the next test number for a specific arrow/bow combination"""
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT COALESCE(MAX(test_number), 0) + 1
        FROM tuning_test_results 
        WHERE user_id = ? AND arrow_id = ? AND bow_setup_id = ? 
        AND arrow_length = ? AND point_weight = ? AND test_type = ?
    ''', (user_id, arrow_id, bow_setup_id, arrow_length, point_weight, test_type))
    
    result = cursor.fetchone()
    return result[0] if result else 1

def create_change_log_entry(user_id: int, arrow_id: int, bow_setup_id: int, 
                           test_result_id: int, change_type: str, 
                           description: str, before_state: Dict = None, 
                           after_state: Dict = None, conn=None) -> bool:
    """Create a change log entry for tuning system integration"""
    if not conn:
        return False
        
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO tuning_change_log (
                user_id, arrow_id, bow_setup_id, test_result_id,
                change_type, description, before_state, after_state
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, arrow_id, bow_setup_id, test_result_id,
            change_type, description, 
            json.dumps(before_state) if before_state else None,
            json.dumps(after_state) if after_state else None
        ))
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"Error creating change log entry: {e}")
        return False