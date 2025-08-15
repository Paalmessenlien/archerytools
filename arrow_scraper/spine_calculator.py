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
    ibo_speed: float = 310.0  # IBO speed rating in FPS (default to Easton baseline)
    release_type: str = "mechanical"  # mechanical, finger (for spine adjustments)
    manufacturer_preference: str = "easton"  # easton, victory, goldtip, generic
    
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
        
        # Use wood calculation logic if wood material is selected, regardless of bow type
        if material_preference and material_preference.lower() == 'wood':
            return self._calculate_wood_spine(
                bow_config, arrow_length, point_weight, nock_weight, fletching_weight
            )
        
        # Otherwise use bow-type specific calculations for non-wood materials
        if bow_config.bow_type == BowType.COMPOUND:
            return self._calculate_compound_spine(
                bow_config, arrow_length, point_weight, nock_weight, fletching_weight
            )
        elif bow_config.bow_type == BowType.RECURVE:
            return self._calculate_recurve_spine(
                bow_config, arrow_length, point_weight, nock_weight, fletching_weight
            )
        else:  # Traditional bow type
            return self._calculate_traditional_spine(
                bow_config, arrow_length, point_weight, nock_weight, fletching_weight, material_preference
            )
    
    def _calculate_wood_spine(self, bow_config: BowConfiguration,
                             arrow_length: float, point_weight: float,
                             nock_weight: float, fletching_weight: float) -> Dict[str, Any]:
        """Calculate spine for wood arrows using traditional wood arrow spine chart methodology"""
        
        # Get wood spine value directly from chart (in pounds) using bow's marked draw weight
        # NOTE: draw_length is NOT used in spine calculations - only for archer information
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
            "bow_type": bow_config.bow_type.value,
            "calculated_spine": round(calculated_spine),
            "spine_range": {k: round(v) for k, v in spine_range.items()},
            "adjustments": adjustments,
            "total_adjustment": round(total_adjustment),
            "base_spine": wood_spine_value,
            "confidence": "high",  # High confidence with proper wood chart
            "spine_units": "pounds",  # Indicate this is in pounds, not carbon spine numbers
            "material": "wood",
            "notes": self._get_spine_notes(bow_config, calculated_spine) + [
                "Based on traditional wood arrow spine chart",
                "Spine values in pounds (wood arrow standard)",
                "Point weight adjustment applied per chart guidelines",
                "Consider testing with bare shaft tuning"
            ]
        }
    
    def _calculate_compound_spine(self, bow_config: BowConfiguration,
                                arrow_length: float, point_weight: float,
                                nock_weight: float, fletching_weight: float) -> Dict[str, Any]:
        """Calculate spine for compound bows using modified AMO formula"""
        
        # Base spine calculation using bow's marked draw weight and arrow length
        # NOTE: draw_length is NOT used in spine calculations - only for archer information
        base_spine = self._get_base_spine_from_chart(bow_config.draw_weight, arrow_length)
        
        # Adjustments for compound bows per Easton standards
        adjustments = {}
        total_adjustment = 0
        
        # Note: Draw length is NOT used in spine calculations per traditional spine charts
        # Only arrow length and draw weight matter for spine selection
        
        # IBO Speed adjustment per Easton chart (effective bow weight modification)
        effective_bow_weight = bow_config.draw_weight + self._get_speed_adjustment(bow_config.ibo_speed)
        speed_adjustment = self._get_speed_adjustment(bow_config.ibo_speed)
        adjustments["bow_speed"] = speed_adjustment
        
        # Recalculate base spine with speed-adjusted weight
        base_spine = self._get_base_spine_from_chart(effective_bow_weight, arrow_length)
        
        # Point weight adjustment: ±3 lbs bow weight per 25 grains over/under 100gr
        point_weight_diff = point_weight - 100.0
        point_weight_adjustment = (point_weight_diff / 25.0) * 3
        bow_weight_adjustment = point_weight_adjustment
        adjustments["point_weight"] = bow_weight_adjustment
        
        # Release type adjustment per Easton standards
        release_adjustment = self._get_release_type_adjustment(bow_config.release_type)
        adjustments["release_type"] = release_adjustment
        
        # Apply all adjustments and recalculate spine
        final_effective_weight = effective_bow_weight + bow_weight_adjustment + release_adjustment
        final_spine = self._get_base_spine_from_chart(final_effective_weight, arrow_length)
        
        # Calculate total adjustment from baseline
        total_adjustment = speed_adjustment + bow_weight_adjustment + release_adjustment
        
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
        
        # Use final calculated spine with all adjustments
        calculated_spine = final_spine
        
        # Provide spine range (±25 spine tolerance)
        spine_range = {
            "minimum": calculated_spine - 25,
            "optimal": calculated_spine,
            "maximum": calculated_spine + 25
        }
        
        # Calculate dynamic spine for real-world conditions
        dynamic_spine_result = self._calculate_dynamic_spine(
            bow_config, arrow_length, point_weight, nock_weight, fletching_weight, calculated_spine
        )
        
        return {
            "bow_type": "compound",
            "calculated_spine": round(calculated_spine),
            "dynamic_spine": dynamic_spine_result,
            "spine_range": {k: round(v) for k, v in spine_range.items()},
            "adjustments": adjustments,
            "total_adjustment": round(total_adjustment),
            "base_spine": base_spine,
            "effective_bow_weight": round(final_effective_weight, 1),
            "ibo_speed": bow_config.ibo_speed,
            "confidence": "high",
            "spine_units": "carbon",
            "notes": self._get_spine_notes(bow_config, calculated_spine) + [
                f"IBO speed: {bow_config.ibo_speed} FPS (adjustment: {speed_adjustment:+.1f} lbs)",
                f"Effective bow weight: {final_effective_weight:.1f} lbs",
                "Based on Easton compound bow speed adjustments",
                "Dynamic spine calculated for real-world conditions"
            ]
        }
    
    def _calculate_recurve_spine(self, bow_config: BowConfiguration,
                               arrow_length: float, point_weight: float,
                               nock_weight: float, fletching_weight: float) -> Dict[str, Any]:
        """Calculate spine for recurve bows using official Easton recurve chart methodology"""
        
        # Use official Easton recurve chart data (finger release, carbon limbs)
        # Based on Easton Target Arrow Selection Chart for Recurve Bow
        base_spine = self._get_recurve_spine_from_easton_chart(bow_config.draw_weight, arrow_length)
        
        # Apply Easton's recurve-specific adjustments
        adjustments = {}
        total_adjustment = 0
        
        # Point weight adjustment per Easton chart: ±3 lbs bow weight per 25 grains over/under 100gr
        point_weight_diff = point_weight - 100
        bow_weight_adjustment = (point_weight_diff / 25) * 3
        adjustments["point_weight"] = bow_weight_adjustment
        total_adjustment += bow_weight_adjustment
        
        # Recurve bow limb type adjustment (Easton standard)
        # Carbon competition limb = no adjustment (default)
        # Wood/glass beginner limb = -5 lbs bow weight
        limb_adjustment = 0  # Assume carbon competition limbs by default
        adjustments["limb_type"] = limb_adjustment
        total_adjustment += limb_adjustment
        
        # Apply total bow weight adjustment to spine selection
        effective_bow_weight = bow_config.draw_weight + total_adjustment
        final_spine = self._get_recurve_spine_from_easton_chart(effective_bow_weight, arrow_length)
        
        # Provide spine range based on Easton recommendations
        # For recurve, recommend weaker side when multiple options available
        spine_range = {
            "minimum": final_spine - 50,  # Wider tolerance for finger release
            "optimal": final_spine,
            "maximum": final_spine + 25
        }
        
        return {
            "bow_type": "recurve",
            "calculated_spine": round(final_spine),
            "spine_range": {k: round(v) for k, v in spine_range.items()},
            "adjustments": adjustments,
            "total_adjustment": round(total_adjustment),
            "base_spine": base_spine,
            "effective_bow_weight": round(effective_bow_weight, 1),
            "confidence": "high",  # High confidence with Easton chart
            "spine_units": "carbon",
            "notes": self._get_spine_notes(bow_config, final_spine) + [
                "Based on Easton recurve chart (finger release, carbon limbs)",
                "Weaker spine recommended for better forgiveness",
                "Point weight adjustment applied per Easton guidelines",
                "Bare shaft tuning recommended for final verification"
            ]
        }
    
    def _calculate_traditional_spine(self, bow_config: BowConfiguration,
                                   arrow_length: float, point_weight: float,
                                   nock_weight: float, fletching_weight: float,
                                   material_preference: str = None) -> Dict[str, Any]:
        """Calculate spine for traditional bows using carbon equivalent method"""
        
        # For non-wood arrows on traditional bows, use carbon equivalent method
        # Get base spine from traditional bow chart using bow's marked draw weight
        # NOTE: draw_length is NOT used in spine calculations - only for archer information
        base_spine = self._get_traditional_base_spine(bow_config.draw_weight, arrow_length)
        
        # Point weight adjustments
        adjustments = {}
        total_adjustment = 0
        
        # Point weight adjustment for traditional bows (similar to recurve but more sensitive)
        point_weight_diff = point_weight - 100.0
        point_adjustment = (point_weight_diff / 25.0) * 25  # ~25 spine per 25gr for traditional
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
            "material": material_preference or "carbon",
            "notes": self._get_spine_notes(bow_config, calculated_spine) + [
                "Based on traditional bow requirements with carbon equivalent calculation",
                "Consider testing with bare shaft tuning for traditional setups"
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
    
    def _get_recurve_spine_from_easton_chart(self, draw_weight: float, arrow_length: float) -> float:
        """Get spine from official Easton recurve chart (finger release, carbon limbs)"""
        
        # Official Easton Recurve Chart Data (Carbon Limbs, Finger Release)
        # Based on Easton Target Arrow Selection Chart
        # Format: draw_weight: {arrow_length: spine_value}
        easton_recurve_chart = {
            # Under 17 lbs
            16: {21: 2000, 22: 2000, 23: 2000, 24: 1800, 25: 1750, 26: 1450, 27: 1250, 28: 1080, 29: 900, 30: 800, 31: 720, 32: 675, 33: 640, 34: 575},
            # 17-23 lbs  
            20: {21: 2000, 22: 2000, 23: 1800, 24: 1700, 25: 1400, 26: 1200, 27: 1050, 28: 880, 29: 750, 30: 700, 31: 625, 32: 600, 33: 570, 34: 500},
            # 24-28 lbs
            26: {21: 2000, 22: 1800, 23: 1700, 24: 1400, 25: 1200, 26: 1050, 27: 880, 28: 750, 29: 700, 30: 625, 31: 600, 32: 570, 33: 500, 34: 450},
            # 29-34 lbs
            31: {21: 1800, 22: 1700, 23: 1450, 24: 1200, 25: 1050, 26: 880, 27: 750, 28: 700, 29: 625, 30: 600, 31: 570, 32: 500, 33: 450, 34: 400},
            # 35-39 lbs
            37: {21: 1750, 22: 1400, 23: 1250, 24: 1050, 25: 880, 26: 750, 27: 625, 28: 575, 29: 500, 30: 450, 31: 400, 32: 370, 33: 340, 34: 300},
            # 40-44 lbs
            42: {21: 1450, 22: 1200, 23: 1050, 24: 880, 25: 750, 26: 625, 27: 575, 28: 500, 29: 450, 30: 400, 31: 370, 32: 340, 33: 300, 34: 250},
            # 45-49 lbs
            47: {21: 1250, 22: 1050, 23: 880, 24: 750, 25: 625, 26: 575, 27: 500, 28: 450, 29: 400, 30: 370, 31: 340, 32: 300, 33: 250, 34: 200},
            # 50-54 lbs
            52: {21: 1080, 22: 880, 23: 750, 24: 625, 25: 575, 26: 500, 27: 450, 28: 400, 29: 370, 30: 340, 31: 300, 32: 250, 33: 200, 34: 150},
            # 55-59 lbs
            57: {21: 900, 22: 750, 23: 625, 24: 575, 25: 500, 26: 450, 27: 400, 28: 370, 29: 340, 30: 300, 31: 250, 32: 200, 33: 150, 34: 150},
            # 60-64 lbs
            62: {21: 800, 22: 700, 23: 575, 24: 500, 25: 450, 26: 400, 27: 370, 28: 340, 29: 300, 30: 250, 31: 200, 32: 150, 33: 150, 34: 150},
            # 65-69 lbs
            67: {21: 720, 22: 625, 23: 500, 24: 450, 25: 400, 26: 370, 27: 340, 28: 300, 29: 250, 30: 200, 31: 150, 32: 150, 33: 150, 34: 150},
            # 70-76 lbs
            73: {21: 675, 22: 600, 23: 450, 24: 400, 25: 370, 26: 340, 27: 300, 28: 250, 29: 200, 30: 150, 31: 150, 32: 150, 33: 150, 34: 150}
        }
        
        # Find closest draw weight
        available_weights = list(easton_recurve_chart.keys())
        closest_weight = min(available_weights, key=lambda x: abs(x - draw_weight))
        
        # Find closest arrow length
        weight_data = easton_recurve_chart[closest_weight]
        available_lengths = list(weight_data.keys())
        closest_length = min(available_lengths, key=lambda x: abs(x - arrow_length))
        
        # Get base spine value
        base_spine = weight_data[closest_length]
        
        # Interpolate between draw weights if we're not exactly on a chart value
        if abs(draw_weight - closest_weight) > 1:
            if draw_weight > closest_weight:
                next_weight = min([w for w in available_weights if w > closest_weight], default=closest_weight)
                if next_weight != closest_weight:
                    lower_spine = easton_recurve_chart[closest_weight][closest_length]
                    upper_spine = easton_recurve_chart[next_weight].get(closest_length, lower_spine)
                    ratio = (draw_weight - closest_weight) / (next_weight - closest_weight)
                    base_spine = lower_spine + (upper_spine - lower_spine) * ratio
            else:
                prev_weight = max([w for w in available_weights if w < closest_weight], default=closest_weight)
                if prev_weight != closest_weight:
                    upper_spine = easton_recurve_chart[closest_weight][closest_length]
                    lower_spine = easton_recurve_chart[prev_weight].get(closest_length, upper_spine)
                    ratio = (closest_weight - draw_weight) / (closest_weight - prev_weight)
                    base_spine = upper_spine + (lower_spine - upper_spine) * ratio
        
        return base_spine
    
    def _get_speed_adjustment(self, ibo_speed: float) -> float:
        """Get bow weight adjustment based on IBO speed rating per Easton standards"""
        
        # Easton compound bow speed adjustments (bow weight modifications)
        # Based on bow speed rating with 301-320 FPS as baseline
        if ibo_speed <= 275:
            return -10.0
        elif ibo_speed <= 300:
            return -5.0
        elif ibo_speed <= 320:
            return 0.0  # Baseline range
        elif ibo_speed <= 340:
            return +5.0
        elif ibo_speed <= 350:
            return +10.0
        else:  # 351+ FPS
            return +15.0
    
    def _get_release_type_adjustment(self, release_type: str) -> float:
        """Get bow weight adjustment based on release type per Easton standards"""
        
        # Easton release type adjustments
        if release_type.lower() == "finger":
            return +5.0  # Add 5 lbs bow weight for finger release
        else:  # mechanical release (default)
            return 0.0   # No adjustment for mechanical release
    
    def _calculate_dynamic_spine(self, bow_config: BowConfiguration, arrow_length: float,
                               point_weight: float, nock_weight: float, fletching_weight: float,
                               static_spine: float) -> Dict[str, Any]:
        """Calculate dynamic spine based on real-world arrow flex during shot"""
        
        # Calculate total arrow weight
        shaft_weight = static_spine * 0.5  # Approximate GPI conversion
        total_arrow_weight = shaft_weight * arrow_length + point_weight + nock_weight + fletching_weight
        
        # Calculate kinetic energy
        arrow_speed_estimate = self._estimate_arrow_speed(bow_config, total_arrow_weight)
        kinetic_energy = (total_arrow_weight * arrow_speed_estimate * arrow_speed_estimate) / 450240
        
        # Calculate FOC (Front of Center)
        foc = self._calculate_foc(arrow_length, point_weight, shaft_weight * arrow_length, 
                                nock_weight, fletching_weight)
        
        # Dynamic spine adjustment factors
        # Heavy points increase effective spine stiffness
        foc_adjustment = (foc - 10) * 2  # 10% FOC is baseline
        
        # Speed affects dynamic flex
        speed_flex_factor = (arrow_speed_estimate - 250) * 0.1  # 250 fps baseline
        
        # Calculate dynamic spine
        dynamic_spine = static_spine + foc_adjustment - speed_flex_factor
        
        return {
            "dynamic_spine": round(dynamic_spine),
            "static_spine": round(static_spine),
            "foc_percentage": round(foc, 1),
            "estimated_speed": round(arrow_speed_estimate),
            "kinetic_energy": round(kinetic_energy, 1),
            "total_arrow_weight": round(total_arrow_weight),
            "foc_adjustment": round(foc_adjustment),
            "speed_adjustment": round(speed_flex_factor),
            "notes": [
                f"FOC: {foc:.1f}% (optimal: 10-15%)",
                f"Estimated speed: {arrow_speed_estimate} fps",
                "Dynamic spine accounts for real-world arrow flex"
            ]
        }
    
    def _estimate_arrow_speed(self, bow_config: BowConfiguration, arrow_weight: float) -> float:
        """Estimate arrow speed based on bow IBO and arrow weight"""
        
        # Basic IBO to actual speed conversion
        # Assumes 5 gr per pound of draw weight, 30" draw
        standard_arrow_weight = 5 * bow_config.draw_weight
        
        # Speed reduction per grain over standard
        weight_factor = (arrow_weight - standard_arrow_weight) / standard_arrow_weight
        speed_reduction = weight_factor * 10  # Rough approximation
        
        # Adjust for actual draw length vs standard 30"
        length_factor = bow_config.draw_length / 30.0
        
        estimated_speed = bow_config.ibo_speed * length_factor - speed_reduction
        
        return max(150, estimated_speed)  # Minimum realistic speed
    
    def _calculate_foc(self, arrow_length: float, point_weight: float, shaft_weight: float,
                      nock_weight: float, fletching_weight: float) -> float:
        """Calculate Front of Center percentage"""
        
        # Calculate balance point
        total_weight = point_weight + shaft_weight + nock_weight + fletching_weight
        
        # Approximate shaft center (middle of shaft)
        shaft_center = arrow_length / 2
        
        # Weighted center calculation
        # Point at front (0"), shaft center at middle, nock/fletching at back
        weighted_center = (
            (point_weight * 0) + 
            (shaft_weight * shaft_center) + 
            ((nock_weight + fletching_weight) * arrow_length)
        ) / total_weight
        
        # FOC = (Balance point - shaft center) / shaft length * 100
        foc = ((shaft_center - weighted_center) / arrow_length) * 100
        
        return foc
    
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
    
    def calculate_enhanced_foc(self, arrow_length: float, point_weight: float,
                              shaft_weight: float, nock_weight: float = 10.0,
                              fletching_weight: float = 15.0, insert_weight: float = 15.0,
                              intended_use: str = "hunting") -> Dict[str, Any]:
        """
        Enhanced FOC calculation with optimization recommendations and performance analysis
        
        Args:
            arrow_length: Total arrow length in inches
            point_weight: Point weight in grains
            shaft_weight: Shaft weight in grains  
            nock_weight: Nock weight in grains
            fletching_weight: Fletching weight in grains
            insert_weight: Insert weight in grains
            intended_use: Intended use case ("hunting", "target", "3d")
            
        Returns:
            Dict with enhanced FOC analysis and optimization recommendations
        """
        
        # Calculate base FOC
        base_foc = self.calculate_foc(arrow_length, point_weight, shaft_weight, 
                                    nock_weight, fletching_weight, insert_weight)
        
        # Define optimal FOC ranges by use case
        optimal_ranges = {
            "hunting": {"min": 10.0, "max": 16.0, "optimal": 13.0},
            "target": {"min": 7.0, "max": 10.0, "optimal": 8.5},
            "3d": {"min": 8.0, "max": 12.0, "optimal": 10.0}
        }
        
        target_range = optimal_ranges.get(intended_use, optimal_ranges["hunting"])
        current_foc = base_foc["foc_percentage"]
        
        # FOC performance analysis
        foc_analysis = self._analyze_foc_performance(current_foc, intended_use)
        
        # Calculate optimization recommendations
        optimization = self._calculate_foc_optimization(
            arrow_length, point_weight, shaft_weight, nock_weight, 
            fletching_weight, insert_weight, target_range["optimal"]
        )
        
        # Enhanced performance metrics
        performance_metrics = self._calculate_foc_performance_metrics(
            current_foc, base_foc["total_weight"], intended_use
        )
        
        return {
            **base_foc,
            "intended_use": intended_use,
            "optimal_range": target_range,
            "foc_status": self._get_foc_status(current_foc, target_range),
            "foc_analysis": foc_analysis,
            "optimization": optimization,
            "performance_metrics": performance_metrics,
            "recommendations": self._get_foc_recommendations(current_foc, target_range, intended_use)
        }
    
    def _analyze_foc_performance(self, foc_percentage: float, intended_use: str) -> Dict[str, Any]:
        """Analyze FOC impact on arrow performance characteristics"""
        
        analysis = {
            "stability": 0,
            "accuracy": 0,
            "penetration": 0,
            "wind_resistance": 0,
            "forgiveness": 0
        }
        
        # FOC impact on performance characteristics
        if foc_percentage < 5:
            # Very low FOC - unstable
            analysis.update({
                "stability": 3,
                "accuracy": 4,
                "penetration": 3,
                "wind_resistance": 2,
                "forgiveness": 2
            })
        elif foc_percentage < 8:
            # Low FOC - good for target
            analysis.update({
                "stability": 6,
                "accuracy": 8,
                "penetration": 5,
                "wind_resistance": 4,
                "forgiveness": 5
            })
        elif foc_percentage < 12:
            # Moderate FOC - balanced
            analysis.update({
                "stability": 8,
                "accuracy": 7,
                "penetration": 7,
                "wind_resistance": 6,
                "forgiveness": 7
            })
        elif foc_percentage < 16:
            # High FOC - good for hunting
            analysis.update({
                "stability": 9,
                "accuracy": 6,
                "penetration": 9,
                "wind_resistance": 8,
                "forgiveness": 8
            })
        else:
            # Very high FOC - may be overstabilized
            analysis.update({
                "stability": 7,
                "accuracy": 5,
                "penetration": 9,
                "wind_resistance": 9,
                "forgiveness": 6
            })
        
        # Calculate overall performance score
        if intended_use == "hunting":
            weights = {"stability": 0.25, "accuracy": 0.15, "penetration": 0.35, "wind_resistance": 0.15, "forgiveness": 0.10}
        elif intended_use == "target":
            weights = {"stability": 0.15, "accuracy": 0.45, "penetration": 0.05, "wind_resistance": 0.10, "forgiveness": 0.25}
        else:  # 3D
            weights = {"stability": 0.20, "accuracy": 0.35, "penetration": 0.10, "wind_resistance": 0.15, "forgiveness": 0.20}
        
        overall_score = sum(analysis[key] * weights[key] for key in weights) * 10
        
        return {
            **analysis,
            "overall_score": round(overall_score, 1),
            "performance_notes": self._get_foc_performance_notes(foc_percentage, intended_use)
        }
    
    def _calculate_foc_optimization(self, arrow_length: float, point_weight: float,
                                  shaft_weight: float, nock_weight: float,
                                  fletching_weight: float, insert_weight: float,
                                  target_foc: float) -> Dict[str, Any]:
        """Calculate optimal point weight to achieve target FOC"""
        
        # Calculate what point weight would achieve target FOC
        total_weight_without_point = shaft_weight + nock_weight + fletching_weight + insert_weight
        
        # FOC formula: (balance_point - physical_center) / arrow_length * 100
        # Solve for optimal point weight
        physical_center = arrow_length / 2.0
        target_foc_decimal = target_foc / 100.0
        
        # Simplified calculation for optimal point weight
        # This is an approximation that works well for most arrows
        optimal_point_weight = point_weight
        
        # Iterative approach to find optimal point weight
        for test_weight in range(50, 400, 5):
            test_foc = self.calculate_foc(arrow_length, test_weight, shaft_weight,
                                        nock_weight, fletching_weight, insert_weight)
            if abs(test_foc["foc_percentage"] - target_foc) < 0.1:
                optimal_point_weight = test_weight
                break
        
        point_weight_change = optimal_point_weight - point_weight
        
        # Calculate alternative adjustments
        alternatives = []
        
        # Insert weight adjustment
        if abs(point_weight_change) > 25:
            # Try adjusting insert weight instead
            for insert_adjust in [-10, -5, 5, 10, 15, 20]:
                new_insert = max(0, insert_weight + insert_adjust)
                test_foc = self.calculate_foc(arrow_length, point_weight, shaft_weight,
                                            nock_weight, fletching_weight, new_insert)
                if abs(test_foc["foc_percentage"] - target_foc) < 1.0:
                    alternatives.append({
                        "type": "insert_weight",
                        "description": f"Adjust insert weight to {new_insert}gr ({insert_adjust:+}gr)",
                        "resulting_foc": test_foc["foc_percentage"]
                    })
        
        # Fletching weight adjustment
        for fletch_adjust in [-5, -3, 3, 5, 8]:
            new_fletching = max(5, fletching_weight + fletch_adjust)
            test_foc = self.calculate_foc(arrow_length, point_weight, shaft_weight,
                                        nock_weight, new_fletching, insert_weight)
            if abs(test_foc["foc_percentage"] - target_foc) < 1.0:
                alternatives.append({
                    "type": "fletching_weight",
                    "description": f"Adjust fletching weight to {new_fletching}gr ({fletch_adjust:+}gr)",
                    "resulting_foc": test_foc["foc_percentage"]
                })
        
        return {
            "current_point_weight": point_weight,
            "optimal_point_weight": optimal_point_weight,
            "point_weight_change": point_weight_change,
            "target_foc": target_foc,
            "alternatives": alternatives[:3],  # Top 3 alternatives
            "feasible": abs(point_weight_change) <= 100,  # Practical weight change limit
            "notes": self._get_optimization_notes(point_weight_change)
        }
    
    def _calculate_foc_performance_metrics(self, foc_percentage: float, 
                                         total_weight: float, intended_use: str) -> Dict[str, Any]:
        """Calculate performance metrics based on FOC and arrow characteristics"""
        
        # FOC impact on flight characteristics
        stability_factor = min(1.2, max(0.6, 0.7 + (foc_percentage / 50)))
        penetration_factor = min(1.3, max(0.7, 0.8 + (foc_percentage / 40)))
        accuracy_factor = min(1.1, max(0.8, 1.1 - abs(foc_percentage - 9) / 20))
        
        # Base performance metrics (normalized to 100)
        base_metrics = {
            "hunting": {"accuracy": 75, "penetration": 85, "wind_resistance": 70},
            "target": {"accuracy": 90, "penetration": 60, "wind_resistance": 65},
            "3d": {"accuracy": 85, "penetration": 70, "wind_resistance": 75}
        }
        
        base = base_metrics.get(intended_use, base_metrics["hunting"])
        
        # Apply FOC factors
        performance = {
            "flight_stability": round(stability_factor * 80, 1),
            "accuracy_potential": round(accuracy_factor * base["accuracy"], 1),
            "penetration_power": round(penetration_factor * base["penetration"], 1),
            "wind_resistance": round(stability_factor * base["wind_resistance"], 1),
            "forgiveness": round((stability_factor + accuracy_factor) / 2 * 75, 1)
        }
        
        # Overall performance score
        if intended_use == "hunting":
            weights = {"flight_stability": 0.2, "accuracy_potential": 0.2, "penetration_power": 0.3, 
                      "wind_resistance": 0.2, "forgiveness": 0.1}
        elif intended_use == "target":
            weights = {"flight_stability": 0.15, "accuracy_potential": 0.4, "penetration_power": 0.05,
                      "wind_resistance": 0.15, "forgiveness": 0.25}
        else:  # 3D
            weights = {"flight_stability": 0.2, "accuracy_potential": 0.3, "penetration_power": 0.1,
                      "wind_resistance": 0.2, "forgiveness": 0.2}
        
        overall_score = sum(performance[key] * weights[key] for key in weights)
        
        return {
            **performance,
            "overall_performance": round(overall_score, 1),
            "weight_category": self._get_weight_category(total_weight),
            "foc_category": self._get_foc_category(foc_percentage)
        }
    
    def _get_foc_status(self, foc_percentage: float, target_range: Dict[str, float]) -> str:
        """Get FOC status relative to optimal range"""
        
        if foc_percentage < target_range["min"]:
            return "too_low"
        elif foc_percentage > target_range["max"]:
            return "too_high"
        elif abs(foc_percentage - target_range["optimal"]) <= 1:
            return "optimal"
        else:
            return "acceptable"
    
    def _get_foc_performance_notes(self, foc_percentage: float, intended_use: str) -> List[str]:
        """Generate performance notes based on FOC value"""
        
        notes = []
        
        if foc_percentage < 5:
            notes.extend([
                "Very low FOC may cause unstable flight",
                "Arrow may plane or drift in crosswinds",
                "Consider heavier points or inserts"
            ])
        elif foc_percentage < 8:
            notes.extend([
                "Good FOC for target accuracy",
                "Excellent flat trajectory",
                "May lack penetration for hunting"
            ])
        elif foc_percentage < 12:
            notes.extend([
                "Balanced FOC for most applications",
                "Good stability and accuracy",
                "Versatile for multiple shooting styles"
            ])
        elif foc_percentage < 16:
            notes.extend([
                "High FOC excellent for hunting",
                "Superior penetration and wind resistance",
                "May sacrifice some accuracy at long range"
            ])
        else:
            notes.extend([
                "Very high FOC may cause parabolic flight",
                "Excellent penetration but reduced accuracy",
                "Consider lighter points for better balance"
            ])
        
        # Add use-specific notes
        if intended_use == "hunting" and 10 <= foc_percentage <= 15:
            notes.append("Ideal FOC range for hunting applications")
        elif intended_use == "target" and 7 <= foc_percentage <= 9:
            notes.append("Optimal FOC for target accuracy")
        elif intended_use == "3d" and 8 <= foc_percentage <= 11:
            notes.append("Good FOC balance for 3D competition")
        
        return notes
    
    def _get_foc_recommendations(self, foc_percentage: float, target_range: Dict[str, float], 
                               intended_use: str) -> List[str]:
        """Generate actionable FOC recommendations"""
        
        recommendations = []
        optimal = target_range["optimal"]
        difference = foc_percentage - optimal
        
        if abs(difference) <= 1:
            recommendations.append("✅ Your FOC is optimal for " + intended_use)
            return recommendations
        
        if difference < -3:
            recommendations.extend([
                f"🎯 Increase FOC by {abs(difference):.1f}% to reach optimal range",
                "• Add 20-50gr to point weight",
                "• Switch to heavier inserts (brass vs aluminum)",
                "• Consider adding weight tubes or FOC weights"
            ])
        elif difference < 0:
            recommendations.extend([
                f"📈 Slightly increase FOC by {abs(difference):.1f}% for optimal performance",
                "• Add 10-25gr to point weight",
                "• Try slightly heavier inserts"
            ])
        elif difference > 3:
            recommendations.extend([
                f"📉 Reduce FOC by {difference:.1f}% for better balance",
                "• Reduce point weight by 25-50gr",
                "• Switch to lighter inserts",
                "• Add weight to rear (heavier nocks/fletching)"
            ])
        else:
            recommendations.extend([
                f"🔧 Fine-tune FOC by {difference:.1f}% for optimal performance",
                "• Adjust point weight by 10-20gr",
                "• Minor insert weight adjustments"
            ])
        
        return recommendations
    
    def _get_optimization_notes(self, point_weight_change: float) -> List[str]:
        """Generate notes about optimization feasibility"""
        
        notes = []
        
        if abs(point_weight_change) <= 10:
            notes.append("Minor point weight adjustment needed")
        elif abs(point_weight_change) <= 25:
            notes.append("Moderate point weight change recommended")
        elif abs(point_weight_change) <= 50:
            notes.append("Significant point weight adjustment required")
        else:
            notes.extend([
                "Large point weight change needed",
                "Consider alternative adjustments (inserts, fletching)",
                "May require different arrow shaft selection"
            ])
        
        if point_weight_change > 100:
            notes.append("⚠️ Weight change may affect spine requirements")
        
        return notes
    
    def _get_weight_category(self, total_weight: float) -> str:
        """Categorize arrow by total weight"""
        
        if total_weight < 350:
            return "light"
        elif total_weight < 450:
            return "medium"
        elif total_weight < 550:
            return "heavy"
        else:
            return "very_heavy"
    
    def _get_foc_category(self, foc_percentage: float) -> str:
        """Categorize FOC level"""
        
        if foc_percentage < 6:
            return "very_low"
        elif foc_percentage < 9:
            return "low"
        elif foc_percentage < 12:
            return "moderate"
        elif foc_percentage < 16:
            return "high"
        else:
            return "very_high"

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