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

class PointType(Enum):
    """Point types for trajectory analysis"""
    FIELD_POINT = "field_point"
    FIXED_BROADHEAD = "fixed_broadhead"
    MECHANICAL_BROADHEAD = "mechanical_broadhead"
    BLUNT = "blunt"
    JUDO_POINT = "judo_point"

@dataclass
class EnvironmentalConditions:
    """Enhanced environmental conditions affecting arrow flight"""
    temperature_f: float = 70.0  # Temperature in Fahrenheit
    humidity_percent: float = 50.0  # Relative humidity
    altitude_feet: float = 0.0  # Altitude above sea level
    wind_speed_mph: float = 0.0  # Wind speed
    wind_direction_degrees: float = 0.0  # Wind direction (0 = headwind, 90 = right crosswind)
    air_pressure_inHg: float = 29.92  # Barometric pressure
    
    # Enhanced environmental factors
    air_density_factor: float = 1.0  # Air density multiplier (calculated from temp/pressure/humidity)
    mirage_intensity: float = 0.0  # Mirage effect intensity (0-1.0)
    lighting_conditions: str = "normal"  # normal, low_light, bright_sun
    ground_effect_distance: float = 0.0  # Distance where ground effect applies (yards)

@dataclass
class BroadheadSpecifications:
    """Specifications for broadhead trajectory modeling"""
    point_type: PointType = PointType.FIELD_POINT
    weight_grains: float = 100.0  # Point weight in grains
    cutting_diameter: float = 0.0  # Cutting diameter in inches (0 for field points)
    blade_count: int = 0  # Number of blades (0 for field points)
    ferrule_diameter: float = 0.246  # Ferrule diameter in inches
    blade_thickness: float = 0.020  # Blade thickness in inches
    profile_type: str = "streamlined"  # streamlined, wide_profile, chisel_tip
    
    # Mechanical broadhead parameters
    is_mechanical: bool = False
    deployment_speed_fps: float = 0.0  # Speed at which blades deploy
    deployed_diameter: float = 0.0  # Fully deployed cutting diameter
    
    # Flight characteristics
    wind_planning_factor: float = 1.0  # How much broadhead "plans" in wind (1.0 = same as field point)
    drag_coefficient_multiplier: float = 1.0  # Multiplier over base arrow drag

@dataclass
class ArrowParadoxParameters:
    """Parameters for modeling arrow paradox (dynamic spine behavior during launch)"""
    static_spine: float = 340.0  # Static spine rating
    dynamic_spine_factor: float = 1.0  # Dynamic spine adjustment factor
    shaft_material: str = "carbon"  # carbon, aluminum, wood
    shaft_length_inches: float = 29.0  # Arrow shaft length
    shaft_diameter_inches: float = 0.246  # Shaft outer diameter
    nocking_point_height: float = 0.0  # Nocking point height above arrow rest (inches)
    bow_centershot: float = 0.0  # Bow centershot adjustment (inches from center)
    arrow_rest_type: str = "drop_away"  # drop_away, blade, whisker_biscuit
    
    # Launch dynamics
    bow_acceleration_time_ms: float = 8.0  # Time bow accelerates arrow (milliseconds)
    peak_acceleration_g: float = 200.0  # Peak acceleration in G-forces
    paradox_frequency_hz: float = 15.0  # Arrow oscillation frequency during launch
    dampening_factor: float = 0.85  # How quickly oscillations dampen (0-1.0)

@dataclass
class ShootingConditions:
    """Enhanced shooting setup and conditions"""
    shot_angle_degrees: float = 0.0  # Elevation angle (-60 to +60 degrees)
    sight_height_inches: float = 7.0  # Height of sight above arrow
    zero_distance_yards: float = 20.0  # Distance sight is zeroed at
    max_range_yards: float = 100.0  # Maximum calculation range
    
    # Enhanced shooting parameters
    bow_cant_degrees: float = 0.0  # Bow cant angle
    anchor_consistency: float = 1.0  # Anchor point consistency factor (0.8-1.0)
    release_consistency: float = 1.0  # Release consistency factor (0.8-1.0)
    follow_through_quality: float = 1.0  # Follow-through quality (0.8-1.0)

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
    
    def calculate_enhanced_trajectory(self, arrow_speed_fps: float, arrow_weight_grains: float,
                           arrow_diameter_inches: float, arrow_type: ArrowType,
                           environmental: EnvironmentalConditions,
                           shooting: ShootingConditions,
                           paradox_params: ArrowParadoxParameters) -> Dict[str, Any]:
        """
        Enhanced trajectory calculation with arrow paradox modeling and environmental factors
        
        Includes:
        - Arrow paradox effects during launch phase
        - Enhanced environmental modeling (air density, temperature effects)
        - Dynamic spine behavior and oscillation dampening
        - Improved drag coefficients based on arrow configuration
        - Ground effect and altitude adjustments
        """
        
        # Calculate enhanced air density from environmental conditions
        air_density = self._calculate_enhanced_air_density(environmental)
        
        # Get enhanced drag coefficient based on arrow configuration and paradox
        drag_coefficient = self._get_enhanced_drag_coefficient(arrow_type, paradox_params)
        
        # Apply arrow paradox effects to initial launch conditions
        launch_conditions = self._apply_arrow_paradox_effects(
            arrow_speed_fps, arrow_weight_grains, paradox_params, shooting
        )
        
        # Enhanced trajectory calculation with paradox and environmental effects
        trajectory_result = self._calculate_enhanced_trajectory_physics(
            launch_conditions, arrow_weight_grains, arrow_diameter_inches,
            drag_coefficient, air_density, environmental, shooting, paradox_params
        )
        
        return trajectory_result
    
    def compare_field_point_vs_broadhead(self, arrow_speed_fps: float, arrow_weight_grains: float,
                                        arrow_diameter_inches: float, arrow_type: ArrowType,
                                        environmental: EnvironmentalConditions,
                                        shooting: ShootingConditions,
                                        broadhead_specs: BroadheadSpecifications) -> Dict[str, Any]:
        """
        Compare trajectory differences between field points and broadheads
        
        This is crucial for hunters who practice with field points but hunt with broadheads.
        Provides practical sighting adjustments and impact point predictions.
        """
        
        # Calculate field point trajectory (baseline)
        field_point_specs = BroadheadSpecifications(
            point_type=PointType.FIELD_POINT,
            weight_grains=broadhead_specs.weight_grains,  # Same weight for fair comparison
            cutting_diameter=0.0,
            blade_count=0,
            drag_coefficient_multiplier=1.0
        )
        
        field_point_trajectory = self._calculate_broadhead_trajectory(
            arrow_speed_fps, arrow_weight_grains, arrow_diameter_inches, arrow_type,
            environmental, shooting, field_point_specs
        )
        
        # Calculate broadhead trajectory
        broadhead_trajectory = self._calculate_broadhead_trajectory(
            arrow_speed_fps, arrow_weight_grains, arrow_diameter_inches, arrow_type,
            environmental, shooting, broadhead_specs
        )
        
        # Compare trajectories and generate practical sighting recommendations
        comparison_analysis = self._analyze_trajectory_differences(
            field_point_trajectory, broadhead_trajectory, broadhead_specs, shooting
        )
        
        return {
            "field_point_trajectory": field_point_trajectory,
            "broadhead_trajectory": broadhead_trajectory,
            "comparison_analysis": comparison_analysis,
            "sighting_recommendations": self._generate_sighting_recommendations(comparison_analysis),
            "practical_notes": self._get_practical_broadhead_notes(broadhead_specs, comparison_analysis)
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
        
        # Calculate proper launch angle for archery setup
        # For bows with elevated sights, we need an upward launch angle to zero at the specified distance
        launch_angle_rad = self._calculate_launch_angle(
            arrow_speed_fps, shooting.sight_height_inches, shooting.zero_distance_yards
        )
        
        # Calculate environmental adjustments
        air_density = self._calculate_air_density(environmental)
        drag_coefficient = self.drag_coefficients[arrow_type]
        
        # Initial velocity components with calculated launch angle
        v0_x = arrow_speed_fps * math.cos(launch_angle_rad)
        v0_y = arrow_speed_fps * math.sin(launch_angle_rad)
        
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
            
            # Store trajectory points at regular distance intervals
            current_distance_yards = x * 3  # feet to yards
            
            # Store a point approximately every yard (when distance crosses integer boundaries)
            if len(trajectory_points) == 0 or current_distance_yards >= len(trajectory_points):
                trajectory_points.append({
                    "time": round(t, 3),
                    "distance_yards": round(current_distance_yards, 1),
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
    
    def _calculate_launch_angle(self, arrow_speed_fps: float, sight_height_inches: float, 
                               zero_distance_yards: float) -> float:
        """
        Calculate proper launch angle for archery setup with elevated sight
        
        For bows with elevated sights, the arrow must be launched at an upward angle
        to intersect the line of sight at the zero distance (typically 20 yards).
        This accounts for the fundamental physics of archery trajectory.
        
        Args:
            arrow_speed_fps: Initial arrow velocity
            sight_height_inches: Height of sight above arrow center line
            zero_distance_yards: Distance at which sight is zeroed
            
        Returns:
            Launch angle in radians (positive = upward)
        """
        # Convert units
        sight_height_feet = sight_height_inches / 12.0
        zero_distance_feet = zero_distance_yards * 3.0
        
        # Time to reach zero distance (ignoring drag for initial calculation)
        time_to_zero = zero_distance_feet / arrow_speed_fps
        
        # Vertical drop due to gravity at zero distance
        gravity_drop_feet = 0.5 * self.gravity * time_to_zero * time_to_zero
        
        # Required vertical displacement to compensate for sight height and gravity
        # The arrow must rise to sight level (sight_height_feet) and overcome gravity drop
        required_vertical_displacement = sight_height_feet + gravity_drop_feet
        
        # Calculate required initial vertical velocity
        required_vy = required_vertical_displacement / time_to_zero
        
        # Calculate launch angle from velocity components
        launch_angle_rad = math.atan(required_vy / arrow_speed_fps)
        
        # Clamp to reasonable archery angles (typically 0.5° to 3°)
        max_angle_rad = math.radians(3.0)  # 3 degrees maximum
        min_angle_rad = math.radians(0.5)  # 0.5 degrees minimum
        
        launch_angle_rad = max(min_angle_rad, min(max_angle_rad, launch_angle_rad))
        
        return launch_angle_rad
    
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


    def _calculate_enhanced_air_density(self, environmental: EnvironmentalConditions) -> float:
        """
        Calculate enhanced air density based on comprehensive environmental factors
        
        Accounts for:
        - Temperature effects on air density
        - Barometric pressure variations
        - Humidity effects (surprisingly, humid air is less dense)
        - Altitude adjustments
        """
        
        # Standard air density at sea level: 0.0765 lb/ft³ at 59°F, 29.92 inHg, 0% humidity
        base_density = self.air_density_sea_level
        
        # Temperature correction (air density inversely proportional to absolute temperature)
        temp_kelvin = (environmental.temperature_f + 459.67) * 5/9  # Fahrenheit to Kelvin
        standard_temp_kelvin = (59 + 459.67) * 5/9  # 59°F in Kelvin
        temp_factor = standard_temp_kelvin / temp_kelvin
        
        # Pressure correction (air density directly proportional to pressure)
        pressure_factor = environmental.air_pressure_inHg / 29.92
        
        # Humidity correction (water vapor is lighter than dry air)
        # Approximate: each 10% humidity reduces density by ~0.3%
        humidity_factor = 1.0 - (environmental.humidity_percent * 0.003)
        
        # Altitude correction (exponential decrease with altitude)
        # Standard atmosphere: density decreases by ~12% per 1000ft up to 36,000ft
        altitude_factor = math.exp(-environmental.altitude_feet / 28000)  # More accurate exponential model
        
        # Combined air density
        enhanced_density = base_density * temp_factor * pressure_factor * humidity_factor * altitude_factor
        
        # Store for reference
        environmental.air_density_factor = enhanced_density / base_density
        
        return enhanced_density
    
    def _get_enhanced_drag_coefficient(self, arrow_type: ArrowType, paradox_params: ArrowParadoxParameters) -> float:
        """
        Calculate enhanced drag coefficient based on arrow configuration and paradox effects
        
        Factors in:
        - Base arrow type drag characteristics
        - Shaft material and surface properties
        - Arrow oscillation effects during flight
        - Rest type interference effects
        """
        
        # Base drag coefficient from arrow type
        base_drag = self.drag_coefficients.get(arrow_type, 0.40)
        
        # Material surface drag adjustments
        material_factors = {
            "carbon": 1.0,      # Smooth surface (baseline)
            "aluminum": 1.05,   # Slightly rougher surface
            "wood": 1.15        # Natural wood grain increases drag
        }
        material_factor = material_factors.get(paradox_params.shaft_material, 1.0)
        
        # Arrow rest type affects initial drag (turbulence at launch)
        rest_factors = {
            "drop_away": 1.0,       # Clean release (baseline)
            "blade": 1.08,          # Some contact drag
            "whisker_biscuit": 1.12 # Continuous contact
        }
        rest_factor = rest_factors.get(paradox_params.arrow_rest_type, 1.0)
        
        # Paradox oscillation effects on drag (oscillating arrow has higher effective drag)
        # Higher frequency oscillations create more turbulence
        oscillation_drag_increase = 1.0 + (paradox_params.paradox_frequency_hz - 10) * 0.005
        oscillation_factor = min(oscillation_drag_increase, 1.2)  # Cap at 20% increase
        
        # Combined drag coefficient
        enhanced_drag = base_drag * material_factor * rest_factor * oscillation_factor
        
        return enhanced_drag
    
    def _apply_arrow_paradox_effects(self, arrow_speed_fps: float, arrow_weight_grains: float,
                                   paradox_params: ArrowParadoxParameters,
                                   shooting: ShootingConditions) -> Dict[str, Any]:
        """
        Apply arrow paradox effects to initial launch conditions
        
        Models:
        - Initial launch angle deviations due to spine mismatch
        - Velocity variations due to energy lost in flex oscillations
        - Angular velocity components from arrow oscillation
        - Rest clearance effects
        """
        
        # Calculate spine mismatch effects
        # Perfect spine match = 1.0, overspined = >1.0, underspined = <1.0
        spine_match_factor = paradox_params.dynamic_spine_factor
        
        # Launch angle deviation due to spine mismatch (radians)
        # Overspined arrows tend to kick left (RH shooter), underspined kick right
        spine_angle_deviation = (spine_match_factor - 1.0) * 0.02  # ~1° per 10% spine mismatch
        
        # Rest clearance effects
        rest_clearance_factors = {
            "drop_away": 0.0,       # Perfect clearance
            "blade": 0.005,         # Minor contact
            "whisker_biscuit": 0.015 # Continuous contact
        }
        rest_angle_deviation = rest_clearance_factors.get(paradox_params.arrow_rest_type, 0.0)
        
        # Combined launch angle deviation
        total_angle_deviation = spine_angle_deviation + rest_angle_deviation
        
        # Velocity loss due to flex energy
        # Poorly matched spine wastes energy in oscillation
        spine_mismatch_loss = abs(spine_match_factor - 1.0) * 0.05  # Up to 5% loss
        paradox_velocity_factor = 1.0 - spine_mismatch_loss
        
        # Arrow oscillation parameters for initial conditions
        initial_oscillation_amplitude = abs(spine_match_factor - 1.0) * 2.0  # inches
        
        return {
            "effective_velocity": arrow_speed_fps * paradox_velocity_factor,
            "launch_angle_deviation": total_angle_deviation,
            "initial_oscillation_amplitude": initial_oscillation_amplitude,
            "oscillation_frequency": paradox_params.paradox_frequency_hz,
            "dampening_factor": paradox_params.dampening_factor,
            "spine_match_factor": spine_match_factor
        }
    
    def _calculate_enhanced_trajectory_physics(self, launch_conditions: Dict[str, Any],
                                             arrow_weight_grains: float, arrow_diameter_inches: float,
                                             drag_coefficient: float, air_density: float,
                                             environmental: EnvironmentalConditions,
                                             shooting: ShootingConditions,
                                             paradox_params: ArrowParadoxParameters) -> Dict[str, Any]:
        """
        Enhanced trajectory physics calculation with arrow paradox modeling
        
        Includes:
        - Dynamic oscillation dampening over time
        - Environmental effects throughout flight
        - Ground effect modeling for low altitude shots
        - Enhanced wind drift calculations
        """
        
        # Initial conditions with paradox effects
        vx = launch_conditions["effective_velocity"] * math.cos(math.radians(shooting.shot_angle_degrees + math.degrees(launch_conditions["launch_angle_deviation"])))
        vy = launch_conditions["effective_velocity"] * math.sin(math.radians(shooting.shot_angle_degrees + math.degrees(launch_conditions["launch_angle_deviation"])))
        
        x, y = 0.0, shooting.sight_height_inches / 12.0  # Start at sight height
        t = 0.0
        time_step = 0.001  # 1ms precision
        
        # Arrow oscillation tracking
        oscillation_amplitude = launch_conditions["initial_oscillation_amplitude"]
        oscillation_phase = 0.0
        
        trajectory_points = []
        arrow_weight_lbs = arrow_weight_grains / 7000.0
        
        while y > -10.0 and t < 30.0:  # Continue until arrow hits ground or 30 second timeout
            # Current arrow velocity magnitude
            velocity_magnitude = math.sqrt(vx**2 + vy**2)
            
            # Dynamic oscillation dampening (exponential decay)
            current_oscillation = oscillation_amplitude * math.exp(-launch_conditions["dampening_factor"] * t * launch_conditions["oscillation_frequency"])
            oscillation_phase += launch_conditions["oscillation_frequency"] * 2 * math.pi * time_step
            
            # Enhanced drag calculation with oscillation effects
            oscillation_drag_multiplier = 1.0 + (current_oscillation / 10.0) * 0.1  # Oscillation increases effective drag
            effective_drag_coefficient = drag_coefficient * oscillation_drag_multiplier
            
            # Ground effect (arrow flies more efficiently close to ground)
            ground_effect_factor = 1.0
            if y * 12 < 36:  # Below 3 feet
                ground_effect_factor = 0.95  # 5% drag reduction near ground
            
            # Enhanced drag force calculation
            drag_force = 0.5 * air_density * effective_drag_coefficient * ground_effect_factor * \
                        (math.pi * (arrow_diameter_inches/12/2)**2) * velocity_magnitude**2
            
            # Drag acceleration (opposing velocity direction)
            if velocity_magnitude > 0:
                drag_accel_x = -(drag_force / arrow_weight_lbs) * (vx / velocity_magnitude)
                drag_accel_y = -(drag_force / arrow_weight_lbs) * (vy / velocity_magnitude)
            else:
                drag_accel_x = drag_accel_y = 0
            
            # Enhanced wind effects with oscillation
            wind_effect = self._calculate_enhanced_wind_effect(environmental, vx, vy, current_oscillation)
            
            # Total acceleration including environmental effects
            ax = drag_accel_x + wind_effect["ax"]
            ay = -self.gravity + drag_accel_y + wind_effect["ay"]
            
            # Store trajectory point
            current_distance_yards = x * 3  # feet to yards
            if len(trajectory_points) == 0 or current_distance_yards >= len(trajectory_points):
                trajectory_points.append({
                    "time": round(t, 3),
                    "distance_yards": round(current_distance_yards, 1),
                    "height_inches": round(y * 12, 2),
                    "velocity_fps": round(velocity_magnitude, 1),
                    "drop_inches": round((shooting.sight_height_inches / 12.0 - y) * 12, 2),
                    "wind_drift_inches": round(wind_effect.get("drift_total", 0) * 12, 2),
                    "oscillation_amplitude": round(current_oscillation, 3),
                    "kinetic_energy": round((arrow_weight_grains * velocity_magnitude**2) / 450240, 1)
                })
            
            # Update position and velocity
            vx += ax * time_step
            vy += ay * time_step
            x += vx * time_step
            y += vy * time_step
            t += time_step
            
            # Stop if maximum range exceeded
            if x * 3 > shooting.max_range_yards:
                break
        
        # Calculate enhanced performance metrics
        performance_metrics = self._calculate_enhanced_performance_metrics(
            trajectory_points, launch_conditions, paradox_params
        )
        
        return {
            "trajectory_points": trajectory_points,
            "performance_metrics": performance_metrics,
            "launch_conditions": launch_conditions,
            "environmental_summary": self._get_environmental_summary(environmental),
            "paradox_analysis": self._get_paradox_analysis(launch_conditions, paradox_params)
        }
    
    def _calculate_enhanced_wind_effect(self, environmental: EnvironmentalConditions, 
                                      vx: float, vy: float, oscillation_amplitude: float) -> Dict[str, Any]:
        """Enhanced wind effect calculation including arrow oscillation influence"""
        
        wind_speed_fps = environmental.wind_speed_mph * 1.467  # mph to fps
        wind_angle_rad = math.radians(environmental.wind_direction_degrees)
        
        # Base wind components
        wind_x = wind_speed_fps * math.cos(wind_angle_rad)
        wind_y = wind_speed_fps * math.sin(wind_angle_rad)
        
        # Relative wind velocity
        relative_wind_x = wind_x - vx
        relative_wind_y = wind_y - vy
        
        # Oscillation increases wind sensitivity (larger effective area)
        oscillation_factor = 1.0 + (oscillation_amplitude / 10.0) * 0.2
        
        # Wind force components
        wind_force_x = 0.5 * relative_wind_x * abs(relative_wind_x) * oscillation_factor * 0.001
        wind_force_y = 0.5 * relative_wind_y * abs(relative_wind_y) * oscillation_factor * 0.001
        
        return {
            "ax": wind_force_x,
            "ay": wind_force_y,
            "drift_total": wind_force_x * 0.1  # Cumulative drift effect
        }
    
    def _calculate_enhanced_performance_metrics(self, trajectory_points: List[Dict],
                                              launch_conditions: Dict[str, Any],
                                              paradox_params: ArrowParadoxParameters) -> Dict[str, Any]:
        """Calculate enhanced performance metrics including paradox effects"""
        
        if not trajectory_points:
            return {}
        
        # Find key trajectory points
        max_height = max(point["height_inches"] for point in trajectory_points)
        max_range = trajectory_points[-1]["distance_yards"] if trajectory_points else 0
        
        # Find 40-yard performance (common reference distance)
        point_40yd = next((p for p in trajectory_points if abs(p["distance_yards"] - 40) <= 1), None)
        
        # Oscillation analysis
        initial_oscillation = launch_conditions.get("initial_oscillation_amplitude", 0)
        final_oscillation = trajectory_points[-1].get("oscillation_amplitude", 0) if trajectory_points else 0
        oscillation_dampening = 1.0 - (final_oscillation / max(initial_oscillation, 0.1))
        
        return {
            "max_height_inches": round(max_height, 1),
            "max_range_yards": round(max_range, 1),
            "velocity_40yd": point_40yd["velocity_fps"] if point_40yd else 0,
            "energy_40yd": point_40yd["kinetic_energy"] if point_40yd else 0,
            "drop_40yd": point_40yd["drop_inches"] if point_40yd else 0,
            "oscillation_analysis": {
                "initial_amplitude": round(initial_oscillation, 2),
                "final_amplitude": round(final_oscillation, 2),
                "dampening_effectiveness": round(oscillation_dampening * 100, 1),
                "spine_match_rating": self._get_spine_match_rating(launch_conditions["spine_match_factor"])
            }
        }
    
    def _get_environmental_summary(self, environmental: EnvironmentalConditions) -> Dict[str, Any]:
        """Generate environmental conditions summary"""
        return {
            "air_density_factor": round(environmental.air_density_factor, 3),
            "conditions": f"{environmental.temperature_f}°F, {environmental.humidity_percent}% humidity",
            "altitude": f"{environmental.altitude_feet} ft",
            "wind": f"{environmental.wind_speed_mph} mph at {environmental.wind_direction_degrees}°"
        }
    
    def _get_paradox_analysis(self, launch_conditions: Dict[str, Any], 
                            paradox_params: ArrowParadoxParameters) -> Dict[str, Any]:
        """Generate arrow paradox analysis summary"""
        spine_match = launch_conditions["spine_match_factor"]
        
        return {
            "spine_match_factor": round(spine_match, 2),
            "spine_rating": self._get_spine_match_rating(spine_match),
            "velocity_loss_percent": round((1.0 - launch_conditions["effective_velocity"] / 300) * 100, 1),
            "oscillation_frequency": paradox_params.paradox_frequency_hz,
            "recommendation": self._get_spine_recommendation(spine_match)
        }
    
    def _get_spine_match_rating(self, spine_factor: float) -> str:
        """Get spine match rating for user understanding"""
        if 0.95 <= spine_factor <= 1.05:
            return "Excellent Match"
        elif 0.90 <= spine_factor <= 1.10:
            return "Good Match"
        elif 0.85 <= spine_factor <= 1.15:
            return "Acceptable"
        elif spine_factor < 0.85:
            return "Too Weak (Underspined)"
        else:
            return "Too Stiff (Overspined)"
    
    def _get_spine_recommendation(self, spine_factor: float) -> str:
        """Get spine tuning recommendation"""
        if spine_factor < 0.90:
            return "Consider stiffer spine or reduce point weight"
        elif spine_factor > 1.10:
            return "Consider weaker spine or increase point weight"
        else:
            return "Spine match is good for current setup"
    
    def _calculate_broadhead_trajectory(self, arrow_speed_fps: float, arrow_weight_grains: float,
                                      arrow_diameter_inches: float, arrow_type: ArrowType,
                                      environmental: EnvironmentalConditions,
                                      shooting: ShootingConditions,
                                      broadhead_specs: BroadheadSpecifications) -> Dict[str, Any]:
        """Calculate trajectory for specific broadhead configuration"""
        
        # Calculate enhanced drag coefficient for broadhead
        broadhead_drag_coefficient = self._calculate_broadhead_drag_coefficient(
            arrow_type, broadhead_specs
        )
        
        # Calculate air density (same for both trajectories)
        air_density = self._calculate_enhanced_air_density(environmental)
        
        # Calculate broadhead-specific trajectory
        return self._calculate_broadhead_physics(
            arrow_speed_fps, arrow_weight_grains, arrow_diameter_inches,
            broadhead_drag_coefficient, air_density, environmental, shooting, broadhead_specs
        )
    
    def _calculate_broadhead_drag_coefficient(self, arrow_type: ArrowType, 
                                            broadhead_specs: BroadheadSpecifications) -> float:
        """Calculate drag coefficient specific to broadhead configuration"""
        
        # Base drag coefficient from arrow type
        base_drag = self.drag_coefficients.get(arrow_type, 0.40)
        
        # Point type specific adjustments
        point_drag_factors = {
            PointType.FIELD_POINT: 1.0,            # Baseline (streamlined)
            PointType.FIXED_BROADHEAD: 1.25,       # 25% increase due to blades
            PointType.MECHANICAL_BROADHEAD: 1.15,  # 15% increase (closed position)
            PointType.BLUNT: 1.40,                 # 40% increase (flat face)
            PointType.JUDO_POINT: 1.35             # 35% increase (wire springs)
        }
        
        point_factor = point_drag_factors.get(broadhead_specs.point_type, 1.0)
        
        # Cutting diameter effects (larger diameter = more drag)
        if broadhead_specs.cutting_diameter > 0:
            diameter_factor = 1.0 + (broadhead_specs.cutting_diameter - 1.0) * 0.15
        else:
            diameter_factor = 1.0
        
        # Blade count effects (more blades = more drag)
        blade_factor = 1.0 + (broadhead_specs.blade_count * 0.05)  # 5% per blade
        
        # Profile type effects
        profile_factors = {
            "streamlined": 1.0,    # Low-profile, aerodynamic
            "wide_profile": 1.15,  # Wide cutting surface
            "chisel_tip": 1.10     # Flat tip design
        }
        profile_factor = profile_factors.get(broadhead_specs.profile_type, 1.0)
        
        # Combined drag coefficient
        total_drag = base_drag * point_factor * diameter_factor * blade_factor * profile_factor
        
        # Apply any additional multiplier from broadhead specs
        return total_drag * broadhead_specs.drag_coefficient_multiplier
    
    def _calculate_broadhead_physics(self, arrow_speed_fps: float, arrow_weight_grains: float,
                                   arrow_diameter_inches: float, drag_coefficient: float,
                                   air_density: float, environmental: EnvironmentalConditions,
                                   shooting: ShootingConditions,
                                   broadhead_specs: BroadheadSpecifications) -> Dict[str, Any]:
        """Calculate physics for broadhead-equipped arrow"""
        
        # Initial conditions
        vx = arrow_speed_fps * math.cos(math.radians(shooting.shot_angle_degrees))
        vy = arrow_speed_fps * math.sin(math.radians(shooting.shot_angle_degrees))
        
        x, y = 0.0, shooting.sight_height_inches / 12.0
        t = 0.0
        time_step = 0.001
        
        trajectory_points = []
        arrow_weight_lbs = arrow_weight_grains / 7000.0
        
        while y > -10.0 and t < 30.0:
            velocity_magnitude = math.sqrt(vx**2 + vy**2)
            
            # Mechanical broadhead deployment effects
            current_drag_coefficient = drag_coefficient
            if (broadhead_specs.is_mechanical and 
                broadhead_specs.deployment_speed_fps > 0 and 
                velocity_magnitude < broadhead_specs.deployment_speed_fps):
                # Blades have deployed - increase drag significantly
                deployment_drag_increase = (broadhead_specs.deployed_diameter / 
                                          broadhead_specs.cutting_diameter) ** 2
                current_drag_coefficient = drag_coefficient * deployment_drag_increase
            
            # Drag force calculation
            drag_force = 0.5 * air_density * current_drag_coefficient * \
                        (math.pi * (arrow_diameter_inches/12/2)**2) * velocity_magnitude**2
            
            # Drag acceleration
            if velocity_magnitude > 0:
                drag_accel_x = -(drag_force / arrow_weight_lbs) * (vx / velocity_magnitude)
                drag_accel_y = -(drag_force / arrow_weight_lbs) * (vy / velocity_magnitude)
            else:
                drag_accel_x = drag_accel_y = 0
            
            # Enhanced wind effects for broadheads (wind planning)
            wind_effect = self._calculate_broadhead_wind_effect(
                environmental, vx, vy, broadhead_specs
            )
            
            # Total acceleration
            ax = drag_accel_x + wind_effect["ax"]
            ay = -self.gravity + drag_accel_y + wind_effect["ay"]
            
            # Store trajectory point
            current_distance_yards = x * 3
            if len(trajectory_points) == 0 or current_distance_yards >= len(trajectory_points):
                trajectory_points.append({
                    "time": round(t, 3),
                    "distance_yards": round(current_distance_yards, 1),
                    "height_inches": round(y * 12, 2),
                    "velocity_fps": round(velocity_magnitude, 1),
                    "drop_inches": round((shooting.sight_height_inches / 12.0 - y) * 12, 2),
                    "wind_drift_inches": round(wind_effect.get("drift_total", 0) * 12, 2),
                    "kinetic_energy": round((arrow_weight_grains * velocity_magnitude**2) / 450240, 1)
                })
            
            # Update position and velocity
            vx += ax * time_step
            vy += ay * time_step
            x += vx * time_step
            y += vy * time_step
            t += time_step
            
            if x * 3 > shooting.max_range_yards:
                break
        
        return {
            "trajectory_points": trajectory_points,
            "point_type": broadhead_specs.point_type.value,
            "drag_coefficient": drag_coefficient
        }
    
    def _calculate_broadhead_wind_effect(self, environmental: EnvironmentalConditions,
                                       vx: float, vy: float, 
                                       broadhead_specs: BroadheadSpecifications) -> Dict[str, Any]:
        """Calculate wind effects specific to broadhead configuration"""
        
        wind_speed_fps = environmental.wind_speed_mph * 1.467
        wind_angle_rad = math.radians(environmental.wind_direction_degrees)
        
        # Base wind components
        wind_x = wind_speed_fps * math.cos(wind_angle_rad)
        wind_y = wind_speed_fps * math.sin(wind_angle_rad)
        
        # Relative wind velocity
        relative_wind_x = wind_x - vx
        relative_wind_y = wind_y - vy
        
        # Broadhead wind planning factor (broadheads "plan" more in crosswinds)
        planning_factor = broadhead_specs.wind_planning_factor
        if broadhead_specs.point_type != PointType.FIELD_POINT:
            # Broadheads typically plan 20-40% more than field points
            if broadhead_specs.cutting_diameter > 1.0:  # Large broadheads
                planning_factor = 1.3
            else:
                planning_factor = 1.2
        
        # Wind force calculation with broadhead planning
        wind_force_x = 0.5 * relative_wind_x * abs(relative_wind_x) * planning_factor * 0.001
        wind_force_y = 0.5 * relative_wind_y * abs(relative_wind_y) * planning_factor * 0.001
        
        return {
            "ax": wind_force_x,
            "ay": wind_force_y,
            "drift_total": wind_force_x * 0.1 * planning_factor
        }
    
    def _analyze_trajectory_differences(self, field_point_traj: Dict[str, Any],
                                      broadhead_traj: Dict[str, Any],
                                      broadhead_specs: BroadheadSpecifications,
                                      shooting: ShootingConditions) -> Dict[str, Any]:
        """Analyze practical differences between field point and broadhead trajectories"""
        
        fp_points = field_point_traj["trajectory_points"]
        bh_points = broadhead_traj["trajectory_points"]
        
        if not fp_points or not bh_points:
            return {}
        
        # Compare at common distances
        comparison_distances = [20, 30, 40, 50, 60]
        distance_comparisons = {}
        
        for distance in comparison_distances:
            fp_point = next((p for p in fp_points if abs(p["distance_yards"] - distance) <= 1), None)
            bh_point = next((p for p in bh_points if abs(p["distance_yards"] - distance) <= 1), None)
            
            if fp_point and bh_point:
                drop_difference = bh_point["drop_inches"] - fp_point["drop_inches"]
                wind_difference = bh_point["wind_drift_inches"] - fp_point["wind_drift_inches"]
                speed_difference = fp_point["velocity_fps"] - bh_point["velocity_fps"]
                energy_difference = fp_point["kinetic_energy"] - bh_point["kinetic_energy"]
                
                distance_comparisons[f"{distance}yd"] = {
                    "drop_difference_inches": round(drop_difference, 1),
                    "wind_drift_difference_inches": round(wind_difference, 1),
                    "speed_loss_fps": round(speed_difference, 1),
                    "energy_loss_ft_lbs": round(energy_difference, 1)
                }
        
        return {
            "distance_comparisons": distance_comparisons,
            "broadhead_type": broadhead_specs.point_type.value,
            "cutting_diameter": broadhead_specs.cutting_diameter
        }
    
    def _generate_sighting_recommendations(self, comparison_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate practical sighting recommendations for broadhead vs field point"""
        
        distance_comps = comparison_analysis.get("distance_comparisons", {})
        if not distance_comps:
            return {}
        
        # Focus on 20-yard and 40-yard differences (common hunting ranges)
        twenty_yd = distance_comps.get("20yd", {})
        forty_yd = distance_comps.get("40yd", {})
        
        recommendations = {
            "sight_adjustment_needed": False,
            "vertical_adjustment": "none",
            "horizontal_adjustment": "none",
            "practical_notes": []
        }
        
        # Vertical adjustment (drop difference)
        if forty_yd.get("drop_difference_inches", 0) > 2:
            recommendations["sight_adjustment_needed"] = True
            recommendations["vertical_adjustment"] = f"Move sight down {abs(forty_yd['drop_difference_inches']):.1f} inches at 40 yards"
            recommendations["practical_notes"].append("Broadhead drops more than field point - sight needs lowering")
        elif forty_yd.get("drop_difference_inches", 0) < -2:
            recommendations["sight_adjustment_needed"] = True  
            recommendations["vertical_adjustment"] = f"Move sight up {abs(forty_yd['drop_difference_inches']):.1f} inches at 40 yards"
            recommendations["practical_notes"].append("Broadhead flies higher than field point - sight needs raising")
        
        # Horizontal adjustment (wind planning)
        if forty_yd.get("wind_drift_difference_inches", 0) > 1:
            recommendations["horizontal_adjustment"] = "Broadhead plans more in wind - aim into wind slightly"
            recommendations["practical_notes"].append("Expect more wind drift with broadheads")
        
        # Energy considerations
        if forty_yd.get("energy_loss_ft_lbs", 0) > 10:
            recommendations["practical_notes"].append("Significant energy loss - verify broadhead sharpness")
        
        return recommendations
    
    def _get_practical_broadhead_notes(self, broadhead_specs: BroadheadSpecifications,
                                     comparison_analysis: Dict[str, Any]) -> List[str]:
        """Generate practical notes for broadhead selection and tuning"""
        
        notes = []
        
        # Point type specific notes
        if broadhead_specs.point_type == PointType.FIXED_BROADHEAD:
            notes.append("Fixed broadheads: Ensure perfect arrow spine tuning for best accuracy")
            if broadhead_specs.cutting_diameter > 1.25:
                notes.append("Large cutting diameter increases wind sensitivity")
        elif broadhead_specs.point_type == PointType.MECHANICAL_BROADHEAD:
            notes.append("Mechanical broadheads: Verify deployment speed matches arrow velocity")
            notes.append("Consider practice heads for consistent trajectory matching")
        
        # Weight considerations
        if broadhead_specs.weight_grains != 100:
            if broadhead_specs.weight_grains > 125:
                notes.append("Heavy broadheads: Excellent penetration but steeper trajectory")
            elif broadhead_specs.weight_grains < 85:
                notes.append("Light broadheads: Flatter trajectory but reduced momentum")
        
        # Practical tuning advice
        notes.append("Always verify broadhead flight with practice shots before hunting")
        notes.append("Consider dedicated broadhead arrows for consistent performance")
        
        return notes

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