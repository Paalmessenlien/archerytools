#!/usr/bin/env python3
"""
Spine Calculator for Arrow Tuning Engine
Implements standard archery spine calculation formulas and arrow matching algorithms
"""

import math
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

class BowType(Enum):
    """Bow types for different spine calculations"""
    COMPOUND = "compound"
    RECURVE = "recurve"
    TRADITIONAL = "traditional"

class ArrowLength(Enum):
    """Arrow length measurement types"""
    BACK_OF_POINT = "back_of_point"  # Standard measurement
    NOCK_GROOVE_TO_END = "nock_groove_to_end"

@dataclass
class BowConfiguration:
    """Bow setup configuration for spine calculations"""
    draw_weight: float  # in pounds
    draw_length: float  # in inches
    bow_type: BowType
    cam_type: str = "medium"  # soft, medium, hard (for compounds)
    center_shot: float = 13.0/16.0  # inches from center
    arrow_rest_type: str = "drop_away"  # drop_away, blade, whisker_biscuit
    
class SpineCalculator:
    """Calculate required arrow spine based on bow configuration and shooting setup"""
    
    def __init__(self):
        # Standard spine reference values (AMO/ATA standards)
        self.reference_spine = {
            # Reference: 28" arrow, 70lb draw, compound bow
            "compound_baseline": {
                "draw_weight": 70,
                "draw_length": 28,
                "spine": 340
            }
        }
    
    def calculate_required_spine(self, bow_config: BowConfiguration, 
                               arrow_length: float,
                               point_weight: float = 100.0,
                               nock_weight: float = 10.0,
                               fletching_weight: float = 15.0,
                               material_preference: str = None) -> Dict[str, Any]:
        """
        Calculate required spine for given bow configuration
        
        Args:
            bow_config: Bow setup parameters
            arrow_length: Total arrow length in inches
            point_weight: Point weight in grains
            nock_weight: Nock weight in grains  
            fletching_weight: Total fletching weight in grains
            material_preference: Arrow material type (affects spine calculation method)
            
        Returns:
            Dict with calculated spine requirements and recommendations
        """
        
        if bow_config.bow_type == BowType.COMPOUND:
            return self._calculate_compound_spine(
                bow_config, arrow_length, point_weight, nock_weight, fletching_weight
            )
        elif bow_config.bow_type == BowType.RECURVE:
            return self._calculate_recurve_spine(
                bow_config, arrow_length, point_weight, nock_weight, fletching_weight
            )
        else:
            return self._calculate_traditional_spine(
                bow_config, arrow_length, point_weight, nock_weight, fletching_weight, material_preference
            )
    
    def _calculate_compound_spine(self, bow_config: BowConfiguration,
                                arrow_length: float, point_weight: float,
                                nock_weight: float, fletching_weight: float) -> Dict[str, Any]:
        """Calculate spine for compound bows using modified AMO formula"""
        
        # Base spine calculation using draw weight and arrow length
        base_spine = self._get_base_spine_from_chart(bow_config.draw_weight, arrow_length)
        
        # Adjustments for compound bows
        adjustments = {}
        total_adjustment = 0
        
        # Note: Draw length is NOT used in spine calculations per traditional spine charts
        # Only arrow length and draw weight matter for spine selection
        
        # Point weight adjustment (per 25 grains from 100gr)
        point_weight_diff = point_weight - 100.0
        point_adjustment = (point_weight_diff / 25.0) * 15  # ~15 spine per 25gr
        adjustments["point_weight"] = point_adjustment
        total_adjustment += point_adjustment
        
        # Cam timing adjustment
        cam_adjustments = {"soft": -10, "medium": 0, "hard": +10}
        cam_adjustment = cam_adjustments.get(bow_config.cam_type, 0)
        adjustments["cam_type"] = cam_adjustment
        total_adjustment += cam_adjustment
        
        # Arrow rest adjustment
        rest_adjustments = {
            "drop_away": 0,
            "blade": +10,
            "whisker_biscuit": +20,
            "full_containment": +15
        }
        rest_adjustment = rest_adjustments.get(bow_config.arrow_rest_type, 0)
        adjustments["arrow_rest"] = rest_adjustment
        total_adjustment += rest_adjustment
        
        # Center shot adjustment
        center_shot_diff = bow_config.center_shot - (13.0/16.0)
        center_shot_adjustment = center_shot_diff * 100  # Rough approximation
        adjustments["center_shot"] = center_shot_adjustment
        total_adjustment += center_shot_adjustment
        
        # Calculate final spine
        calculated_spine = base_spine - total_adjustment
        
        # Provide spine range (±25 spine tolerance)
        spine_range = {
            "minimum": calculated_spine - 25,
            "optimal": calculated_spine,
            "maximum": calculated_spine + 25
        }
        
        return {
            "bow_type": "compound",
            "calculated_spine": round(calculated_spine),
            "spine_range": {k: round(v) for k, v in spine_range.items()},
            "adjustments": adjustments,
            "total_adjustment": round(total_adjustment),
            "base_spine": base_spine,
            "confidence": "high",
            "notes": self._get_spine_notes(bow_config, calculated_spine)
        }
    
    def _calculate_recurve_spine(self, bow_config: BowConfiguration,
                               arrow_length: float, point_weight: float,
                               nock_weight: float, fletching_weight: float) -> Dict[str, Any]:
        """Calculate spine for recurve bows"""
        
        # Recurve calculation uses actual draw weight at draw length
        actual_draw_weight = bow_config.draw_weight
        
        # Base spine from recurve-specific chart
        base_spine = self._get_recurve_base_spine(actual_draw_weight, arrow_length)
        
        # Adjustments for recurve
        adjustments = {}
        total_adjustment = 0
        
        # Point weight adjustment (more sensitive than compound)
        point_weight_diff = point_weight - 100.0
        point_adjustment = (point_weight_diff / 25.0) * 20  # ~20 spine per 25gr
        adjustments["point_weight"] = point_adjustment
        total_adjustment += point_adjustment
        
        # String material adjustment
        # Note: This could be expanded to include string type parameter
        # For now, assume modern string materials
        
        calculated_spine = base_spine - total_adjustment
        
        spine_range = {
            "minimum": calculated_spine - 30,
            "optimal": calculated_spine,
            "maximum": calculated_spine + 30
        }
        
        return {
            "bow_type": "recurve",
            "calculated_spine": round(calculated_spine),
            "spine_range": {k: round(v) for k, v in spine_range.items()},
            "adjustments": adjustments,
            "total_adjustment": round(total_adjustment),
            "base_spine": base_spine,
            "confidence": "medium",
            "notes": self._get_spine_notes(bow_config, calculated_spine)
        }
    
    def _calculate_traditional_spine(self, bow_config: BowConfiguration,
                                   arrow_length: float, point_weight: float,
                                   nock_weight: float, fletching_weight: float,
                                   material_preference: str = None) -> Dict[str, Any]:
        """Calculate spine for traditional bows using wood arrow spine chart methodology"""
        
        # For wood arrows, use pound-based spine values directly from the chart
        if material_preference and material_preference.lower() == 'wood':
            # Get wood spine value directly from chart (in pounds)
            wood_spine_value = self._get_wood_spine_from_chart(bow_config.draw_weight, arrow_length)
            
            # Point weight adjustments based on traditional wood arrow chart
            adjustments = {}
            total_adjustment = 0
            
            # Wood arrow point weight adjustment (from chart notes)
            # 30 grains = 1, 70 grains = 2, 100 grains = 3, 125 grains = 4
            # Chart is based on 100 grain points (value 3)
            point_weight_adjustment_table = {
                30: 1, 70: 2, 100: 3, 125: 4
            }
            
            # Find closest point weight adjustment value
            closest_point_weight = min(point_weight_adjustment_table.keys(), 
                                     key=lambda x: abs(x - point_weight))
            point_adjustment_value = point_weight_adjustment_table[closest_point_weight]
            
            # Baseline is 100gr (value 3), so calculate adjustment
            baseline_adjustment = 3
            point_adjustment_diff = point_adjustment_value - baseline_adjustment
            
            # Each adjustment point represents about 2.5 pounds in wood spine
            point_adjustment = point_adjustment_diff * 2.5
            adjustments["point_weight"] = point_adjustment
            total_adjustment += point_adjustment
            
            # Apply adjustment to wood spine value (in pounds)
            calculated_spine = wood_spine_value + total_adjustment
            
            # Wood arrow spine range is typically ±5 pounds
            spine_range = {
                "minimum": calculated_spine - 5,
                "optimal": calculated_spine,
                "maximum": calculated_spine + 5
            }
            
            return {
                "bow_type": "traditional",
                "calculated_spine": round(calculated_spine),
                "spine_range": {k: round(v) for k, v in spine_range.items()},
                "adjustments": adjustments,
                "total_adjustment": round(total_adjustment),
                "base_spine": wood_spine_value,
                "confidence": "high",  # High confidence with proper wood chart
                "spine_units": "pounds",  # Indicate this is in pounds, not carbon spine numbers
                "notes": self._get_spine_notes(bow_config, calculated_spine) + [
                    "Based on traditional wood arrow spine chart",
                    "Spine values in pounds (wood arrow standard)",
                    "Point weight adjustment applied per chart guidelines",
                    "Consider testing with bare shaft tuning"
                ]
            }
        else:
            # For non-wood arrows on traditional bows, use carbon equivalent method
            # Get base spine from wood arrow chart
            base_spine = self._get_traditional_base_spine(bow_config.draw_weight, arrow_length)
            
            # Point weight adjustments based on traditional wood arrow chart
            adjustments = {}
            total_adjustment = 0
            
            # Wood arrow point weight adjustment (from chart notes)
            # 30 grains = 1, 70 grains = 2, 100 grains = 3, 125 grains = 4
            # Chart is based on 100 grain points (value 3)
            point_weight_adjustment_table = {
                30: 1, 70: 2, 100: 3, 125: 4
            }
            
            # Find closest point weight adjustment value
            closest_point_weight = min(point_weight_adjustment_table.keys(), 
                                     key=lambda x: abs(x - point_weight))
            point_adjustment_value = point_weight_adjustment_table[closest_point_weight]
            
            # Baseline is 100gr (value 3), so calculate adjustment
            baseline_adjustment = 3
            point_adjustment_diff = point_adjustment_value - baseline_adjustment
            
            # Each adjustment point represents about 5 spine units in carbon arrows
            point_adjustment = point_adjustment_diff * 5
            adjustments["point_weight"] = point_adjustment
            total_adjustment += point_adjustment
            
            # Apply adjustment to carbon equivalent spine
            calculated_spine = base_spine - total_adjustment
            
            # Carbon arrow spine range is typically ±30 spine units
            spine_range = {
                "minimum": calculated_spine - 30,
                "optimal": calculated_spine,
                "maximum": calculated_spine + 30
            }
            
            return {
                "bow_type": "traditional",
                "calculated_spine": round(calculated_spine),
                "spine_range": {k: round(v) for k, v in spine_range.items()},
                "adjustments": adjustments,
                "total_adjustment": round(total_adjustment),
                "base_spine": base_spine,
                "confidence": "medium",  # Medium confidence with carbon equivalent
                "notes": self._get_spine_notes(bow_config, calculated_spine) + [
                    "Based on traditional wood arrow spine chart (carbon equivalent)",
                    "Point weight adjustment applied per chart guidelines",
                    "Consider testing with bare shaft tuning"
                ]
            }
    
    def _get_base_spine_from_chart(self, draw_weight: float, arrow_length: float) -> float:
        """Get base spine from standard compound bow chart"""
        
        # Simplified spine chart - in production this would be a comprehensive lookup table
        # Based on common manufacturer spine charts - uses ARROW LENGTH, not draw length
        
        spine_chart = {
            # Draw weight: {arrow_length: spine}
            50: {26: 500, 27: 500, 28: 400, 29: 400, 30: 340, 31: 340},
            55: {26: 500, 27: 400, 28: 400, 29: 340, 30: 340, 31: 300},
            60: {26: 400, 27: 400, 28: 340, 29: 340, 30: 300, 31: 300},
            65: {26: 400, 27: 340, 28: 340, 29: 300, 30: 300, 31: 250},
            70: {26: 340, 27: 340, 28: 300, 29: 300, 30: 250, 31: 250},
            75: {26: 340, 27: 300, 28: 300, 29: 250, 30: 250, 31: 200}
        }
        
        # Find closest weight and arrow length
        closest_weight = min(spine_chart.keys(), key=lambda x: abs(x - draw_weight))
        weight_chart = spine_chart[closest_weight]
        closest_length = min(weight_chart.keys(), key=lambda x: abs(x - arrow_length))
        
        base_spine = weight_chart[closest_length]
        
        # Interpolate if needed
        if abs(closest_weight - draw_weight) > 2.5:
            # Linear interpolation between weight ranges
            if draw_weight > closest_weight:
                next_weight = min([w for w in spine_chart.keys() if w > closest_weight], default=closest_weight)
                if next_weight != closest_weight:
                    lower_spine = spine_chart[closest_weight][closest_length]
                    upper_spine = spine_chart[next_weight].get(closest_length, lower_spine)
                    ratio = (draw_weight - closest_weight) / (next_weight - closest_weight)
                    base_spine = lower_spine + (upper_spine - lower_spine) * ratio
            else:
                prev_weight = max([w for w in spine_chart.keys() if w < closest_weight], default=closest_weight)
                if prev_weight != closest_weight:
                    upper_spine = spine_chart[closest_weight][closest_length]
                    lower_spine = spine_chart[prev_weight].get(closest_length, upper_spine)
                    ratio = (closest_weight - draw_weight) / (closest_weight - prev_weight)
                    base_spine = upper_spine + (lower_spine - upper_spine) * ratio
        
        return base_spine
    
    def _get_recurve_base_spine(self, draw_weight: float, arrow_length: float) -> float:
        """Get base spine for recurve bows"""
        
        # Expanded recurve spine chart (generally weaker than compound for same draw weight)
        # Based on standard archery spine charts and real-world recurve recommendations
        recurve_chart = {
            20: {24: 2000, 25: 1900, 26: 1800, 27: 1700, 28: 1600, 29: 1500, 30: 1400, 31: 1300, 32: 1200},
            25: {24: 1800, 25: 1700, 26: 1600, 27: 1500, 28: 1400, 29: 1300, 30: 1200, 31: 1100, 32: 1000},
            30: {24: 1400, 25: 1300, 26: 1200, 27: 1100, 28: 1000, 29: 900, 30: 800, 31: 750, 32: 700},
            35: {24: 1000, 25: 900, 26: 800, 27: 750, 28: 700, 29: 650, 30: 600, 31: 550, 32: 500},
            40: {24: 800, 25: 750, 26: 700, 27: 650, 28: 600, 29: 550, 30: 500, 31: 450, 32: 400},
            45: {24: 700, 25: 650, 26: 600, 27: 550, 28: 500, 29: 450, 30: 400, 31: 370, 32: 340},
            50: {24: 600, 25: 550, 26: 500, 27: 450, 28: 400, 29: 370, 30: 340, 31: 320, 32: 300},
            55: {24: 500, 25: 450, 26: 400, 27: 370, 28: 340, 29: 320, 30: 300, 31: 280, 32: 260},
            60: {24: 450, 25: 400, 26: 370, 27: 340, 28: 320, 29: 300, 30: 280, 31: 260, 32: 240},
            65: {24: 400, 25: 370, 26: 340, 27: 320, 28: 300, 29: 280, 30: 260, 31: 240, 32: 220}
        }
        
        # Find closest weight and interpolate if necessary
        available_weights = list(recurve_chart.keys())
        closest_weight = min(available_weights, key=lambda x: abs(x - draw_weight))
        
        # Get spine for closest weight
        weight_chart = recurve_chart[closest_weight]
        closest_length = min(weight_chart.keys(), key=lambda x: abs(x - arrow_length))
        base_spine = weight_chart[closest_length]
        
        # Interpolate between weights if necessary for better accuracy
        if abs(draw_weight - closest_weight) > 2.5:
            if draw_weight > closest_weight:
                next_weight = min([w for w in available_weights if w > closest_weight], default=closest_weight)
                if next_weight != closest_weight:
                    lower_spine = recurve_chart[closest_weight][closest_length]
                    upper_spine = recurve_chart[next_weight].get(closest_length, lower_spine)
                    ratio = (draw_weight - closest_weight) / (next_weight - closest_weight)
                    base_spine = lower_spine + (upper_spine - lower_spine) * ratio
            else:
                prev_weight = max([w for w in available_weights if w < closest_weight], default=closest_weight)
                if prev_weight != closest_weight:
                    upper_spine = recurve_chart[closest_weight][closest_length]
                    lower_spine = recurve_chart[prev_weight].get(closest_length, upper_spine)
                    ratio = (closest_weight - draw_weight) / (closest_weight - prev_weight)
                    base_spine = upper_spine + (lower_spine - upper_spine) * ratio
        
        # Interpolate between lengths if necessary
        if abs(arrow_length - closest_length) > 0.5:
            available_lengths = list(weight_chart.keys())
            if arrow_length > closest_length:
                next_length = min([l for l in available_lengths if l > closest_length], default=closest_length)
                if next_length != closest_length:
                    lower_spine = weight_chart[closest_length]
                    upper_spine = weight_chart[next_length]
                    ratio = (arrow_length - closest_length) / (next_length - closest_length)
                    base_spine = lower_spine + (upper_spine - lower_spine) * ratio
            else:
                prev_length = max([l for l in available_lengths if l < closest_length], default=closest_length)
                if prev_length != closest_length:
                    upper_spine = weight_chart[closest_length]
                    lower_spine = weight_chart[prev_length]
                    ratio = (closest_length - arrow_length) / (closest_length - prev_length)
                    base_spine = upper_spine + (lower_spine - upper_spine) * ratio
        
        return base_spine
    
    def _get_traditional_base_spine(self, draw_weight: float, arrow_length: float) -> float:
        """Get base spine for traditional bows using actual wood arrow spine chart"""
        
        # Wood Arrow Spine Chart - based on actual traditional archery spine chart
        # Format: draw_weight: {arrow_length: spine_value}
        # Spine values represent the middle of the spine range (e.g., 30-35 becomes 32.5)
        wood_spine_chart = {
            # Chart data from traditional wood arrow spine chart
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
        
        # Interpolate if the actual values are significantly different
        if abs(draw_weight - closest_weight) > 2.5:
            # Linear interpolation between weight ranges
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
        
        # Convert wood spine rating to carbon equivalent for internal calculations
        # Wood spine 35# ≈ 600 carbon spine
        # Wood spine 50# ≈ 450 carbon spine  
        # Wood spine 65# ≈ 350 carbon spine
        # Linear conversion: carbon_spine = 950 - (wood_spine * 9)
        carbon_equivalent = max(300, 950 - (base_spine * 9))
        
        return carbon_equivalent
    
    def _get_wood_spine_from_chart(self, draw_weight: float, arrow_length: float) -> float:
        """Get wood spine value directly from traditional wood arrow chart (in pounds)"""
        
        # Wood Arrow Spine Chart - based on actual traditional wood arrow spine chart
        # Format: draw_weight: {arrow_length: spine_value_in_pounds}
        # Using the middle values from the chart ranges (e.g., 30-35 becomes 32.5)
        wood_spine_chart = {
            # Chart data from traditional wood arrow spine chart image
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
        
        # Interpolate if the actual values are significantly different
        if abs(draw_weight - closest_weight) > 2.5:
            # Linear interpolation between weight ranges
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
    
    def _get_spine_notes(self, bow_config: BowConfiguration, calculated_spine: float) -> List[str]:
        """Generate helpful notes for spine selection"""
        
        notes = []
        
        if calculated_spine < 250:
            notes.append("Very stiff arrow required - consider high draw weight setup")
        elif calculated_spine > 600:
            notes.append("Weak spine required - double-check calculations")
        
        if bow_config.bow_type == BowType.COMPOUND:
            notes.append("Fine-tune with paper tuning or bare shaft testing")
            
            if bow_config.arrow_rest_type == "whisker_biscuit":
                notes.append("Whisker biscuit may require slightly stiffer arrow")
        
        return notes
    
    def get_spine_tolerance_range(self, target_spine: float, bow_type: BowType) -> Tuple[float, float]:
        """Get acceptable spine range around target spine"""
        
        tolerances = {
            BowType.COMPOUND: 25,
            BowType.RECURVE: 30,
            BowType.TRADITIONAL: 40
        }
        
        tolerance = tolerances[bow_type]
        return (target_spine - tolerance, target_spine + tolerance)
    
    def calculate_foc(self, arrow_length: float, point_weight: float,
                     shaft_weight: float, nock_weight: float = 10.0,
                     fletching_weight: float = 15.0, insert_weight: float = 15.0) -> Dict[str, float]:
        """
        Calculate Front of Center (FOC) percentage
        
        Args:
            arrow_length: Total arrow length in inches
            point_weight: Point weight in grains
            shaft_weight: Shaft weight in grains
            nock_weight: Nock weight in grains
            fletching_weight: Fletching weight in grains  
            insert_weight: Insert weight in grains
            
        Returns:
            Dict with FOC calculations
        """
        
        # Total arrow weight
        total_weight = point_weight + shaft_weight + nock_weight + fletching_weight + insert_weight
        
        # Front half weight (point + half of shaft + insert)
        front_weight = point_weight + insert_weight + (shaft_weight / 2.0)
        
        # Back half weight (nock + fletching + half of shaft)
        back_weight = nock_weight + fletching_weight + (shaft_weight / 2.0)
        
        # Physical center (arrow length / 2)
        physical_center = arrow_length / 2.0
        
        # Balance point calculation
        # Simplified: assume shaft weight is evenly distributed
        balance_point = physical_center + ((front_weight - back_weight) / total_weight) * physical_center
        
        # FOC percentage
        foc_distance = balance_point - physical_center
        foc_percentage = (foc_distance / arrow_length) * 100
        
        return {
            "foc_percentage": round(foc_percentage, 2),
            "balance_point": round(balance_point, 3),
            "physical_center": round(physical_center, 3),
            "total_weight": round(total_weight, 1),
            "front_weight": round(front_weight, 1),
            "back_weight": round(back_weight, 1)
        }

# Example usage and testing
if __name__ == "__main__":
    print("🎯 Spine Calculator Test Suite")
    print("=" * 50)
    
    calculator = SpineCalculator()
    
    # Test compound bow setup
    compound_bow = BowConfiguration(
        draw_weight=70,
        draw_length=29,
        bow_type=BowType.COMPOUND,
        cam_type="medium",
        arrow_rest_type="drop_away"
    )
    
    print("\n🏹 Compound Bow Test (70# @ 29\"):")
    result = calculator.calculate_required_spine(
        compound_bow, 
        arrow_length=29.5, 
        point_weight=100
    )
    
    print(f"   Calculated spine: {result['calculated_spine']}")
    print(f"   Spine range: {result['spine_range']['minimum']}-{result['spine_range']['maximum']}")
    print(f"   Adjustments: {result['adjustments']}")
    
    # Test recurve bow
    recurve_bow = BowConfiguration(
        draw_weight=45,
        draw_length=28,
        bow_type=BowType.RECURVE
    )
    
    print("\n🏹 Recurve Bow Test (45# @ 28\"):")
    result = calculator.calculate_required_spine(
        recurve_bow,
        arrow_length=29,
        point_weight=125
    )
    
    print(f"   Calculated spine: {result['calculated_spine']}")
    print(f"   Spine range: {result['spine_range']['minimum']}-{result['spine_range']['maximum']}")
    
    # Test FOC calculation
    print("\n📏 FOC Calculation Test:")
    foc_result = calculator.calculate_foc(
        arrow_length=29.5,
        point_weight=100,
        shaft_weight=300,
        nock_weight=10,
        fletching_weight=15
    )
    
    print(f"   FOC: {foc_result['foc_percentage']}%")
    print(f"   Balance point: {foc_result['balance_point']}\"")
    print(f"   Total weight: {foc_result['total_weight']} grains")