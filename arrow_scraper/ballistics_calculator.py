#!/usr/bin/env python3
"""
Advanced Ballistics Calculator for Arrow Performance Analysis
Implements trajectory modeling, environmental adjustments, and performance metrics
"""

import math
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from enum import Enum

class ArrowType(Enum):
    """Arrow types for ballistics calculations"""
    TARGET = "target"
    HUNTING = "hunting"
    FIELD = "field"
    THREE_D = "3d"

@dataclass
class EnvironmentalConditions:
    """Environmental conditions affecting arrow flight"""
    temperature_f: float = 70.0  # Temperature in Fahrenheit
    humidity_percent: float = 50.0  # Relative humidity
    altitude_feet: float = 0.0  # Altitude above sea level
    wind_speed_mph: float = 0.0  # Wind speed
    wind_direction_degrees: float = 0.0  # Wind direction (0 = headwind, 90 = right crosswind)
    air_pressure_inHg: float = 29.92  # Barometric pressure

@dataclass
class ShootingConditions:
    """Shooting setup and conditions"""
    shot_angle_degrees: float = 0.0  # Elevation angle (-60 to +60 degrees)
    sight_height_inches: float = 7.0  # Height of sight above arrow
    zero_distance_yards: float = 20.0  # Distance sight is zeroed at
    max_range_yards: float = 100.0  # Maximum calculation range

class BallisticsCalculator:
    """Advanced ballistics calculator for arrow flight analysis"""
    
    def __init__(self):
        # Physical constants
        self.gravity = 32.174  # ft/s² at sea level
        self.air_density_sea_level = 0.0765  # lb/ft³ at standard conditions
        
        # Drag coefficients by arrow type (approximate values)
        self.drag_coefficients = {
            ArrowType.TARGET: 0.35,  # Low-profile vanes, small diameter
            ArrowType.HUNTING: 0.45,  # Larger diameter, mechanical broadheads
            ArrowType.FIELD: 0.40,   # Field points, moderate vanes
            ArrowType.THREE_D: 0.38  # Optimized for accuracy
        }
    
    def calculate_trajectory(self, arrow_speed_fps: float, arrow_weight_grains: float,
                           arrow_diameter_inches: float, arrow_type: ArrowType,
                           environmental: EnvironmentalConditions,
                           shooting: ShootingConditions) -> Dict[str, Any]:
        """
        Calculate complete arrow trajectory with environmental factors
        
        Args:
            arrow_speed_fps: Initial arrow velocity
            arrow_weight_grains: Total arrow weight
            arrow_diameter_inches: Arrow diameter for drag calculation
            arrow_type: Type of arrow affecting drag
            environmental: Environmental conditions
            shooting: Shooting setup parameters
            
        Returns:
            Dict with trajectory data and performance metrics
        """
        
        # Convert units
        arrow_weight_lbs = arrow_weight_grains / 7000.0
        shot_angle_rad = math.radians(shooting.shot_angle_degrees)
        
        # Calculate environmental adjustments
        air_density = self._calculate_air_density(environmental)
        drag_coefficient = self.drag_coefficients[arrow_type]
        
        # Initial velocity components
        v0_x = arrow_speed_fps * math.cos(shot_angle_rad)
        v0_y = arrow_speed_fps * math.sin(shot_angle_rad)
        
        # Calculate trajectory points
        trajectory_points = []
        time_step = 0.01  # seconds
        max_time = 10.0   # seconds
        
        x, y = 0.0, shooting.sight_height_inches / 12.0  # Convert to feet
        vx, vy = v0_x, v0_y
        t = 0.0
        
        while t <= max_time and y >= 0:
            # Current velocity magnitude
            velocity_magnitude = math.sqrt(vx**2 + vy**2)
            
            # Drag force calculation
            drag_force = 0.5 * air_density * drag_coefficient * \
                        (math.pi * (arrow_diameter_inches/12/2)**2) * velocity_magnitude**2
            
            # Acceleration due to drag (opposing velocity direction)
            if velocity_magnitude > 0:
                drag_accel_x = -(drag_force / arrow_weight_lbs) * (vx / velocity_magnitude)
                drag_accel_y = -(drag_force / arrow_weight_lbs) * (vy / velocity_magnitude)
            else:
                drag_accel_x = drag_accel_y = 0
            
            # Wind effects
            wind_effect = self._calculate_wind_effect(environmental, vx, vy, arrow_diameter_inches)
            
            # Total acceleration
            ax = drag_accel_x + wind_effect["ax"]
            ay = -self.gravity + drag_accel_y + wind_effect["ay"]
            
            # Store trajectory point (convert back to yards and inches)
            if t % (time_step * 10) < time_step:  # Store every 10th point
                trajectory_points.append({
                    "time": round(t, 3),
                    "distance_yards": round(x * 3, 1),  # feet to yards
                    "height_inches": round(y * 12, 2),  # feet to inches
                    "velocity_fps": round(velocity_magnitude, 1),
                    "drop_inches": round((shooting.sight_height_inches / 12.0 - y) * 12, 2),
                    "wind_drift_inches": round(wind_effect.get("drift", 0) * 12, 2)
                })
            
            # Update velocity and position using Euler integration
            vx += ax * time_step
            vy += ay * time_step
            x += vx * time_step
            y += vy * time_step
            t += time_step
            
            # Stop if maximum range exceeded
            if x * 3 > shooting.max_range_yards:  # Convert feet to yards
                break
        
        # Calculate performance metrics
        performance_metrics = self._calculate_performance_metrics(
            trajectory_points, arrow_speed_fps, arrow_weight_grains, arrow_type
        )
        
        # Calculate elevation adjustments
        elevation_adjustments = self._calculate_elevation_adjustments(
            shooting.shot_angle_degrees, trajectory_points
        )
        
        return {
            "trajectory_points": trajectory_points,
            "performance_metrics": performance_metrics,
            "elevation_adjustments": elevation_adjustments,
            "environmental_impact": self._analyze_environmental_impact(environmental),
            "ballistic_coefficient": self._calculate_ballistic_coefficient(
                arrow_weight_grains, arrow_diameter_inches, drag_coefficient
            ),
            "flight_summary": self._generate_flight_summary(trajectory_points, environmental)
        }
    
    def calculate_kinetic_energy(self, arrow_speed_fps: float, arrow_weight_grains: float,
                               distance_yards: float = 0) -> Dict[str, float]:
        """Calculate kinetic energy at given distance"""
        
        # Simple velocity retention model (approximation)
        # More accurate calculation would use full trajectory
        velocity_retention = max(0.6, 1.0 - (distance_yards * 0.003))
        velocity_at_distance = arrow_speed_fps * velocity_retention
        
        # Kinetic energy formula: KE = (mv²)/2
        # Using archery standard: KE = (weight in grains × velocity²) / 450240
        kinetic_energy = (arrow_weight_grains * velocity_at_distance**2) / 450240
        
        # Momentum calculation: p = mv
        momentum = (arrow_weight_grains / 7000) * velocity_at_distance
        
        return {
            "kinetic_energy_ft_lbs": round(kinetic_energy, 2),
            "momentum_slug_fps": round(momentum, 3),
            "velocity_fps": round(velocity_at_distance, 1),
            "velocity_retention_percent": round(velocity_retention * 100, 1)
        }
    
    def calculate_penetration_potential(self, kinetic_energy_ft_lbs: float, 
                                      momentum_slug_fps: float, arrow_type: ArrowType) -> Dict[str, Any]:
        """Calculate penetration potential based on KE and momentum"""
        
        # Penetration factors by arrow type
        penetration_factors = {
            ArrowType.TARGET: {"ke_weight": 0.3, "momentum_weight": 0.7},
            ArrowType.HUNTING: {"ke_weight": 0.4, "momentum_weight": 0.6},
            ArrowType.FIELD: {"ke_weight": 0.35, "momentum_weight": 0.65},
            ArrowType.THREE_D: {"ke_weight": 0.3, "momentum_weight": 0.7}
        }
        
        factors = penetration_factors[arrow_type]
        
        # Normalize values for scoring (based on typical hunting arrow performance)
        ke_score = min(100, (kinetic_energy_ft_lbs / 0.8) * 100)  # 80 ft-lbs = 100%
        momentum_score = min(100, (momentum_slug_fps / 0.6) * 100)  # 0.6 slug-fps = 100%
        
        # Calculate composite penetration score
        penetration_score = (ke_score * factors["ke_weight"] + 
                           momentum_score * factors["momentum_weight"])
        
        # Determine penetration category
        if penetration_score >= 80:
            category = "excellent"
            description = "Superior penetration for large game"
        elif penetration_score >= 60:
            category = "good"
            description = "Adequate for most hunting applications"
        elif penetration_score >= 40:
            category = "fair"
            description = "Suitable for smaller game"
        else:
            category = "poor"
            description = "Insufficient for hunting, good for target"
        
        return {
            "penetration_score": round(penetration_score, 1),
            "category": category,
            "description": description,
            "kinetic_energy_score": round(ke_score, 1),
            "momentum_score": round(momentum_score, 1),
            "recommendations": self._get_penetration_recommendations(penetration_score, arrow_type)
        }
    
    def _calculate_air_density(self, env: EnvironmentalConditions) -> float:
        """Calculate air density based on environmental conditions"""
        
        # Temperature effect (density decreases with temperature)
        temp_ratio = 459.67 + 70 / (459.67 + env.temperature_f)
        
        # Altitude effect (density decreases with altitude)
        altitude_ratio = math.exp(-env.altitude_feet / 26900)
        
        # Humidity effect (very small, often ignored)
        humidity_ratio = 1.0 - (env.humidity_percent / 100) * 0.02
        
        # Barometric pressure effect
        pressure_ratio = env.air_pressure_inHg / 29.92
        
        adjusted_density = (self.air_density_sea_level * temp_ratio * 
                          altitude_ratio * humidity_ratio * pressure_ratio)
        
        return adjusted_density
    
    def _calculate_wind_effect(self, env: EnvironmentalConditions, vx: float, vy: float,
                             arrow_diameter_inches: float) -> Dict[str, float]:
        """Calculate wind effect on arrow flight"""
        
        if env.wind_speed_mph == 0:
            return {"ax": 0, "ay": 0, "drift": 0}
        
        # Convert wind speed to fps
        wind_speed_fps = env.wind_speed_mph * 1.467
        
        # Wind components
        wind_rad = math.radians(env.wind_direction_degrees)
        wind_x = wind_speed_fps * math.cos(wind_rad)  # Along flight path
        wind_y = wind_speed_fps * math.sin(wind_rad)  # Crosswind
        
        # Relative wind velocity
        rel_wind_x = wind_x - vx
        rel_wind_y = wind_y - vy
        rel_wind_speed = math.sqrt(rel_wind_x**2 + rel_wind_y**2)
        
        # Wind force (simplified model)
        arrow_area = math.pi * (arrow_diameter_inches/12/2)**2
        wind_force = 0.5 * self.air_density_sea_level * 0.1 * arrow_area * rel_wind_speed**2
        
        # Convert to acceleration (assuming 400 grain arrow)
        arrow_mass_slugs = 400 / 7000 / 32.174
        wind_accel = wind_force / arrow_mass_slugs
        
        # Direction of wind effect
        if rel_wind_speed > 0:
            wind_ax = wind_accel * (rel_wind_x / rel_wind_speed)
            wind_ay = wind_accel * (rel_wind_y / rel_wind_speed)
        else:
            wind_ax = wind_ay = 0
        
        return {
            "ax": wind_ax,
            "ay": wind_ay,
            "drift": wind_y * 0.1  # Simplified drift calculation
        }
    
    def _calculate_performance_metrics(self, trajectory_points: List[Dict], 
                                     initial_speed: float, arrow_weight: float,
                                     arrow_type: ArrowType) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics"""
        
        if not trajectory_points:
            return {}
        
        # Find key distances
        distances = [20, 30, 40, 50, 60, 80, 100]
        performance_at_distance = {}
        
        for distance in distances:
            # Find closest trajectory point to this distance
            closest_point = min(trajectory_points, 
                              key=lambda p: abs(p["distance_yards"] - distance))
            
            if abs(closest_point["distance_yards"] - distance) <= 5:  # Within 5 yards
                ke_data = self.calculate_kinetic_energy(
                    closest_point["velocity_fps"], arrow_weight, distance
                )
                
                performance_at_distance[f"{distance}yd"] = {
                    "velocity_fps": closest_point["velocity_fps"],
                    "drop_inches": closest_point["drop_inches"],
                    "kinetic_energy": ke_data["kinetic_energy_ft_lbs"],
                    "momentum": ke_data["momentum_slug_fps"]
                }
        
        # Calculate trajectory characteristics
        max_height = max(p["height_inches"] for p in trajectory_points)
        max_range = max(p["distance_yards"] for p in trajectory_points)
        
        # Flight time calculations
        if trajectory_points:
            flight_time_40yd = next((p["time"] for p in trajectory_points 
                                   if abs(p["distance_yards"] - 40) <= 2), None)
            flight_time_60yd = next((p["time"] for p in trajectory_points 
                                   if abs(p["distance_yards"] - 60) <= 2), None)
        
        return {
            "performance_at_distance": performance_at_distance,
            "max_effective_range_yards": max_range,
            "max_trajectory_height_inches": round(max_height, 2),
            "flight_time_40yd": round(flight_time_40yd, 3) if flight_time_40yd else None,
            "flight_time_60yd": round(flight_time_60yd, 3) if flight_time_60yd else None,
            "trajectory_flatness_score": self._calculate_flatness_score(trajectory_points),
            "consistency_score": self._calculate_consistency_score(arrow_type, arrow_weight)
        }
    
    def _calculate_elevation_adjustments(self, shot_angle: float, 
                                       trajectory_points: List[Dict]) -> Dict[str, Any]:
        """Calculate elevation adjustments for angled shots"""
        
        adjustments = {}
        
        # Common shooting angles
        angles = [-30, -20, -10, 0, 10, 20, 30, 45]
        
        for angle in angles:
            if angle == shot_angle:
                continue
                
            # Simplified adjustment calculation
            # True horizontal distance = cos(angle) × line-of-sight distance
            cos_angle = math.cos(math.radians(angle))
            
            # For each distance, calculate adjustment
            distance_adjustments = {}
            for distance in [20, 30, 40, 50, 60]:
                # Find drop at this distance for level shot
                level_point = next((p for p in trajectory_points 
                                  if abs(p["distance_yards"] - distance) <= 2), None)
                
                if level_point:
                    # Horizontal equivalent distance
                    horizontal_distance = distance * cos_angle
                    
                    # Gravity effect adjustment
                    gravity_adjustment = distance * (1 - cos_angle) * 2  # Simplified
                    
                    distance_adjustments[f"{distance}yd"] = {
                        "horizontal_equivalent": round(horizontal_distance, 1),
                        "aim_adjustment_inches": round(gravity_adjustment, 2),
                        "holdover_recommendation": "aim low" if angle > 0 else "aim high"
                    }
            
            adjustments[f"{angle:+d}_degrees"] = distance_adjustments
        
        return {
            "angle_adjustments": adjustments,
            "general_rule": "Aim low for uphill shots, aim high for downhill shots",
            "notes": [
                "Adjustments are approximations - verify with practice",
                "Effect is more pronounced at longer distances",
                "Consider rangefinder with angle compensation"
            ]
        }
    
    def _analyze_environmental_impact(self, env: EnvironmentalConditions) -> Dict[str, Any]:
        """Analyze impact of environmental conditions on arrow flight"""
        
        impact_analysis = {
            "temperature_effect": "minimal",
            "altitude_effect": "minimal", 
            "humidity_effect": "minimal",
            "wind_effect": "minimal"
        }
        
        effects_description = []
        
        # Temperature effects
        if env.temperature_f < 40:
            impact_analysis["temperature_effect"] = "moderate"
            effects_description.append("Cold air increases air density, slightly reducing velocity")
        elif env.temperature_f > 90:
            impact_analysis["temperature_effect"] = "moderate"
            effects_description.append("Hot air decreases air density, slightly increasing velocity")
        
        # Altitude effects
        if env.altitude_feet > 3000:
            impact_analysis["altitude_effect"] = "moderate" if env.altitude_feet < 8000 else "significant"
            effects_description.append(f"High altitude ({env.altitude_feet}ft) reduces air density, increasing velocity and flattening trajectory")
        
        # Wind effects
        if env.wind_speed_mph > 5:
            impact_analysis["wind_effect"] = "moderate" if env.wind_speed_mph < 15 else "significant"
            effects_description.append(f"Wind ({env.wind_speed_mph}mph) will cause drift and affect trajectory")
        
        return {
            "impact_levels": impact_analysis,
            "effects_description": effects_description,
            "overall_impact": max(impact_analysis.values(), key=lambda x: ["minimal", "moderate", "significant"].index(x)),
            "recommendations": self._get_environmental_recommendations(env)
        }
    
    def _calculate_ballistic_coefficient(self, arrow_weight_grains: float,
                                       arrow_diameter_inches: float, 
                                       drag_coefficient: float) -> float:
        """Calculate ballistic coefficient for the arrow"""
        
        # Ballistic coefficient = mass / (drag coefficient × cross-sectional area)
        mass_lbs = arrow_weight_grains / 7000
        cross_sectional_area = math.pi * (arrow_diameter_inches / 2)**2
        
        bc = mass_lbs / (drag_coefficient * cross_sectional_area)
        
        return round(bc, 4)
    
    def _calculate_flatness_score(self, trajectory_points: List[Dict]) -> float:
        """Calculate trajectory flatness score (0-100)"""
        
        if len(trajectory_points) < 2:
            return 0
        
        # Calculate maximum drop over 60 yards
        points_60yd = [p for p in trajectory_points if p["distance_yards"] <= 60]
        if not points_60yd:
            return 0
        
        max_drop = max(abs(p["drop_inches"]) for p in points_60yd)
        
        # Score based on drop (less drop = higher score)
        # 0 inches = 100, 20 inches = 50, 40+ inches = 0
        score = max(0, 100 - (max_drop * 2.5))
        
        return round(score, 1)
    
    def _calculate_consistency_score(self, arrow_type: ArrowType, arrow_weight: float) -> float:
        """Calculate consistency score based on arrow characteristics"""
        
        # Base scores by arrow type
        base_scores = {
            ArrowType.TARGET: 85,
            ArrowType.HUNTING: 75,
            ArrowType.FIELD: 80,
            ArrowType.THREE_D: 82
        }
        
        base_score = base_scores[arrow_type]
        
        # Weight consistency factor
        if 350 <= arrow_weight <= 500:
            weight_factor = 1.0  # Optimal weight range
        elif 300 <= arrow_weight < 350 or 500 < arrow_weight <= 600:
            weight_factor = 0.95  # Good weight range
        else:
            weight_factor = 0.85  # Suboptimal weight range
        
        return round(base_score * weight_factor, 1)
    
    def _generate_flight_summary(self, trajectory_points: List[Dict],
                               env: EnvironmentalConditions) -> Dict[str, str]:
        """Generate human-readable flight summary"""
        
        if not trajectory_points:
            return {"summary": "No trajectory data available"}
        
        max_range = max(p["distance_yards"] for p in trajectory_points)
        max_height = max(p["height_inches"] for p in trajectory_points)
        
        # Find 40-yard performance
        point_40yd = next((p for p in trajectory_points 
                          if abs(p["distance_yards"] - 40) <= 2), None)
        
        summary_parts = [
            f"Maximum effective range: {max_range:.0f} yards",
            f"Peak trajectory height: {max_height:.1f} inches"
        ]
        
        if point_40yd:
            summary_parts.append(f"At 40 yards: {point_40yd['drop_inches']:.1f}\" drop, {point_40yd['velocity_fps']:.0f} fps")
        
        if env.wind_speed_mph > 0:
            summary_parts.append(f"Wind drift with {env.wind_speed_mph}mph wind")
        
        return {
            "summary": ". ".join(summary_parts),
            "key_points": summary_parts
        }
    
    def _get_penetration_recommendations(self, score: float, arrow_type: ArrowType) -> List[str]:
        """Get recommendations for improving penetration"""
        
        recommendations = []
        
        if score < 40:
            recommendations.extend([
                "Increase arrow weight for better penetration",
                "Consider heavier points (150-200+ grains)",
                "Add weight tubes or FOC weights"
            ])
        elif score < 60:
            recommendations.extend([
                "Good penetration for small to medium game",
                "Consider slightly heavier setup for large game"
            ])
        elif score < 80:
            recommendations.extend([
                "Excellent penetration for most hunting",
                "Well-balanced setup for hunting applications"
            ])
        else:
            recommendations.extend([
                "Superior penetration power",
                "Excellent for large game hunting",
                "Consider if speed/trajectory is adequate"
            ])
        
        return recommendations
    
    def _get_environmental_recommendations(self, env: EnvironmentalConditions) -> List[str]:
        """Get recommendations based on environmental conditions"""
        
        recommendations = []
        
        if env.wind_speed_mph > 10:
            recommendations.append("Strong wind conditions - consider wind flags and practice wind reading")
        
        if env.altitude_feet > 5000:
            recommendations.append("High altitude - expect flatter trajectory and potentially faster speeds")
        
        if env.temperature_f < 40 or env.temperature_f > 90:
            recommendations.append("Extreme temperature - verify zero and expect minor velocity changes")
        
        if not recommendations:
            recommendations.append("Favorable conditions for accurate shooting")
        
        return recommendations


# Example usage and testing
if __name__ == "__main__":
    print("🎯 Ballistics Calculator Test Suite")
    print("=" * 50)
    
    calculator = BallisticsCalculator()
    
    # Test environmental conditions
    env = EnvironmentalConditions(
        temperature_f=75,
        wind_speed_mph=10,
        wind_direction_degrees=90,  # Right crosswind
        altitude_feet=2000
    )
    
    # Test shooting conditions
    shooting = ShootingConditions(
        shot_angle_degrees=0,
        sight_height_inches=7,
        zero_distance_yards=20
    )
    
    print("\n🏹 Trajectory Calculation Test:")
    result = calculator.calculate_trajectory(
        arrow_speed_fps=280,
        arrow_weight_grains=420,
        arrow_diameter_inches=0.246,
        arrow_type=ArrowType.HUNTING,
        environmental=env,
        shooting=shooting
    )
    
    print(f"   Max range: {result['performance_metrics']['max_effective_range_yards']} yards")
    print(f"   Ballistic coefficient: {result['ballistic_coefficient']}")
    print(f"   Flight summary: {result['flight_summary']['summary']}")
    
    # Test kinetic energy calculation
    print("\n⚡ Kinetic Energy Test:")
    ke_result = calculator.calculate_kinetic_energy(280, 420, 40)
    print(f"   KE at 40 yards: {ke_result['kinetic_energy_ft_lbs']} ft-lbs")
    print(f"   Momentum: {ke_result['momentum_slug_fps']} slug-fps")
    
    # Test penetration potential
    print("\n🎯 Penetration Analysis:")
    pen_result = calculator.calculate_penetration_potential(
        ke_result['kinetic_energy_ft_lbs'], 
        ke_result['momentum_slug_fps'], 
        ArrowType.HUNTING
    )
    print(f"   Penetration score: {pen_result['penetration_score']}")
    print(f"   Category: {pen_result['category']}")