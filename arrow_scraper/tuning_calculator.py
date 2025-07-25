#!/usr/bin/env python3
"""
Advanced Tuning Calculator
Comprehensive calculations for arrow tuning, FOC optimization, and weight balancing
"""

import math
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

class TuningGoal(Enum):
    """Different tuning objectives"""
    MAXIMUM_SPEED = "maximum_speed"
    OPTIMAL_PENETRATION = "optimal_penetration"
    BALANCED_PERFORMANCE = "balanced_performance"
    MAXIMUM_ACCURACY = "maximum_accuracy"
    HUNTING_EFFECTIVENESS = "hunting_effectiveness"

class ArrowType(Enum):
    """Arrow application types"""
    TARGET_INDOOR = "target_indoor"
    TARGET_OUTDOOR = "target_outdoor"
    FIELD_ARCHERY = "field_archery"
    HUNTING_SMALL_GAME = "hunting_small_game"
    HUNTING_BIG_GAME = "hunting_big_game"
    TRADITIONAL_ARCHERY = "traditional_archery"

@dataclass
class ArrowComponents:
    """Individual arrow component weights"""
    shaft_weight: float          # grains
    point_weight: float          # grains
    nock_weight: float           # grains
    fletching_weight: float      # grains
    insert_weight: float         # grains
    wrap_weight: float = 0.0     # grains (optional)
    outsert_weight: float = 0.0  # grains (optional)

@dataclass
class TuningResult:
    """Complete tuning analysis result"""
    total_weight: float
    foc_percentage: float
    balance_point: float
    kinetic_energy: float
    momentum: float
    speed_estimate: float
    penetration_score: float
    accuracy_score: float
    wind_drift_factor: float
    trajectory_rating: str
    recommendations: List[str]
    component_breakdown: Dict[str, float]

class TuningCalculator:
    """Advanced tuning calculations and optimization"""
    
    def __init__(self):
        # Reference values for calculations
        self.reference_values = {
            "standard_foc_range": (8.0, 15.0),
            "optimal_foc_hunting": (10.0, 12.0),
            "optimal_foc_target": (8.0, 10.0),
            "max_efficient_weight_ratio": 0.08,  # 8% of draw weight for max efficiency
            "min_weight_hunting": 350,  # Minimum total arrow weight for hunting
            "optimal_ke_small_game": 25,  # ft-lbs
            "optimal_ke_big_game": 45,   # ft-lbs
        }
    
    def comprehensive_tuning_analysis(self, components: ArrowComponents, 
                                    arrow_length: float, bow_weight: float,
                                    arrow_diameter: float = 0.246,
                                    tuning_goal: TuningGoal = TuningGoal.BALANCED_PERFORMANCE,
                                    arrow_type: ArrowType = ArrowType.HUNTING_BIG_GAME) -> TuningResult:
        """
        Perform comprehensive tuning analysis
        
        Args:
            components: Arrow component weights
            arrow_length: Total arrow length in inches
            bow_weight: Bow draw weight in pounds
            arrow_diameter: Arrow diameter in inches
            tuning_goal: Primary tuning objective
            arrow_type: Intended arrow application
            
        Returns:
            Complete tuning analysis
        """
        
        print(f"🎯 Comprehensive Tuning Analysis")
        print(f"   Goal: {tuning_goal.value}")
        print(f"   Arrow Type: {arrow_type.value}")
        print(f"   Bow Weight: {bow_weight}#")
        
        # Calculate basic metrics
        total_weight = self._calculate_total_weight(components)
        foc_data = self._calculate_advanced_foc(components, arrow_length)
        
        # Estimate arrow speed
        speed_fps = self._estimate_arrow_speed(total_weight, bow_weight)
        
        # Calculate ballistic properties
        ke_ft_lbs = self._calculate_kinetic_energy(total_weight, speed_fps)
        momentum = self._calculate_momentum(total_weight, speed_fps)
        
        # Performance scores
        penetration_score = self._calculate_penetration_score(
            total_weight, speed_fps, foc_data['foc_percentage'], arrow_diameter
        )
        accuracy_score = self._calculate_accuracy_score(
            total_weight, foc_data['foc_percentage'], arrow_length, tuning_goal
        )
        
        # Environmental factors
        wind_drift = self._calculate_wind_drift_factor(total_weight, arrow_diameter, speed_fps)
        trajectory_rating = self._rate_trajectory(speed_fps, total_weight)
        
        # Generate recommendations
        recommendations = self._generate_tuning_recommendations(
            components, foc_data, total_weight, speed_fps, tuning_goal, arrow_type
        )
        
        # Component breakdown
        component_breakdown = {
            "shaft_percentage": (components.shaft_weight / total_weight) * 100,
            "point_percentage": (components.point_weight / total_weight) * 100,
            "nock_percentage": (components.nock_weight / total_weight) * 100,
            "fletching_percentage": (components.fletching_weight / total_weight) * 100,
            "insert_percentage": (components.insert_weight / total_weight) * 100,
        }
        
        result = TuningResult(
            total_weight=total_weight,
            foc_percentage=foc_data['foc_percentage'],
            balance_point=foc_data['balance_point'],
            kinetic_energy=ke_ft_lbs,
            momentum=momentum,
            speed_estimate=speed_fps,
            penetration_score=penetration_score,
            accuracy_score=accuracy_score,
            wind_drift_factor=wind_drift,
            trajectory_rating=trajectory_rating,
            recommendations=recommendations,
            component_breakdown=component_breakdown
        )
        
        print(f"   Total Weight: {total_weight:.0f} grains")
        print(f"   FOC: {foc_data['foc_percentage']:.1f}%")
        print(f"   Estimated Speed: {speed_fps:.0f} fps")
        print(f"   Kinetic Energy: {ke_ft_lbs:.0f} ft-lbs")
        
        return result
    
    def optimize_for_goal(self, base_components: ArrowComponents, arrow_length: float,
                         bow_weight: float, tuning_goal: TuningGoal,
                         available_point_weights: List[float]) -> Dict[str, Any]:
        """
        Optimize arrow setup for specific tuning goal
        
        Args:
            base_components: Starting component configuration
            arrow_length: Arrow length in inches
            bow_weight: Bow draw weight in pounds
            tuning_goal: Target optimization goal
            available_point_weights: List of available point weights to test
            
        Returns:
            Optimization results with best configuration
        """
        
        print(f"🔧 Optimizing for {tuning_goal.value}")
        
        best_config = None
        best_score = -1
        optimization_results = []
        
        for point_weight in available_point_weights:
            # Create test configuration
            test_components = ArrowComponents(
                shaft_weight=base_components.shaft_weight,
                point_weight=point_weight,
                nock_weight=base_components.nock_weight,
                fletching_weight=base_components.fletching_weight,
                insert_weight=base_components.insert_weight,
                wrap_weight=base_components.wrap_weight,
                outsert_weight=base_components.outsert_weight
            )
            
            # Analyze configuration
            analysis = self.comprehensive_tuning_analysis(
                test_components, arrow_length, bow_weight, tuning_goal=tuning_goal
            )
            
            # Score based on tuning goal
            config_score = self._score_configuration(analysis, tuning_goal)
            
            optimization_results.append({
                "point_weight": point_weight,
                "total_weight": analysis.total_weight,
                "foc": analysis.foc_percentage,
                "speed": analysis.speed_estimate,
                "kinetic_energy": analysis.kinetic_energy,
                "score": config_score,
                "analysis": analysis
            })
            
            if config_score > best_score:
                best_score = config_score
                best_config = {
                    "components": test_components,
                    "analysis": analysis,
                    "score": config_score
                }
        
        # Sort results by score
        optimization_results.sort(key=lambda x: x['score'], reverse=True)
        
        return {
            "best_configuration": best_config,
            "all_results": optimization_results,
            "optimization_goal": tuning_goal,
            "recommendations": self._get_optimization_recommendations(optimization_results, tuning_goal)
        }
    
    def calculate_ideal_foc_range(self, arrow_type: ArrowType, bow_type: str = "compound") -> Tuple[float, float]:
        """Calculate ideal FOC range for specific arrow application"""
        
        foc_ranges = {
            ArrowType.TARGET_INDOOR: (7.0, 9.0),
            ArrowType.TARGET_OUTDOOR: (8.0, 10.0),
            ArrowType.FIELD_ARCHERY: (9.0, 11.0),
            ArrowType.HUNTING_SMALL_GAME: (10.0, 12.0),
            ArrowType.HUNTING_BIG_GAME: (11.0, 15.0),
            ArrowType.TRADITIONAL_ARCHERY: (12.0, 18.0)
        }
        
        base_range = foc_ranges.get(arrow_type, (10.0, 12.0))
        
        # Adjust for bow type
        if bow_type.lower() == "traditional":
            return (base_range[0] + 2, base_range[1] + 3)
        elif bow_type.lower() == "recurve":
            return (base_range[0] + 1, base_range[1] + 2)
        
        return base_range
    
    def calculate_broadhead_tuning_adjustments(self, field_point_weight: float,
                                             broadhead_weight: float,
                                             current_foc: float) -> Dict[str, Any]:
        """Calculate adjustments needed when switching from field points to broadheads"""
        
        weight_difference = broadhead_weight - field_point_weight
        
        # Estimate FOC change (approximate)
        foc_change = (weight_difference / 100) * 1.5  # Rough approximation
        new_foc = current_foc + foc_change
        
        # Determine if adjustments are needed
        adjustments_needed = abs(weight_difference) > 5  # 5+ grain difference
        
        recommendations = []
        
        if weight_difference > 0:
            recommendations.append(f"Broadheads are {weight_difference:.0f} grains heavier")
            recommendations.append(f"FOC will increase to approximately {new_foc:.1f}%")
            if weight_difference > 15:
                recommendations.append("Consider reducing shaft weight or using lighter broadheads")
        elif weight_difference < 0:
            recommendations.append(f"Broadheads are {abs(weight_difference):.0f} grains lighter")
            recommendations.append(f"FOC will decrease to approximately {new_foc:.1f}%")
            if abs(weight_difference) > 15:
                recommendations.append("Consider increasing shaft weight or using heavier broadheads")
        else:
            recommendations.append("Field point and broadhead weights match - excellent!")
        
        return {
            "weight_difference": weight_difference,
            "new_foc_estimate": new_foc,
            "foc_change": foc_change,
            "adjustments_needed": adjustments_needed,
            "recommendations": recommendations
        }
    
    def _calculate_total_weight(self, components: ArrowComponents) -> float:
        """Calculate total arrow weight"""
        return (components.shaft_weight + components.point_weight + 
                components.nock_weight + components.fletching_weight + 
                components.insert_weight + components.wrap_weight + components.outsert_weight)
    
    def _calculate_advanced_foc(self, components: ArrowComponents, arrow_length: float) -> Dict[str, float]:
        """Calculate advanced FOC with detailed component analysis"""
        
        total_weight = self._calculate_total_weight(components)
        
        # Component positions (from nock end)
        nock_position = 0.0
        fletching_position = 1.0  # Approximately 1" from nock
        shaft_center = arrow_length / 2.0
        insert_position = arrow_length - 0.5  # Approximately 0.5" from point
        point_position = arrow_length
        
        # Calculate center of gravity using weighted positions
        total_moment = (
            components.nock_weight * nock_position +
            components.fletching_weight * fletching_position +
            components.shaft_weight * shaft_center +
            components.insert_weight * insert_position +
            components.point_weight * point_position +
            components.wrap_weight * (arrow_length * 0.75) +  # Assume 3/4 down shaft
            components.outsert_weight * point_position
        )
        
        balance_point = total_moment / total_weight
        physical_center = arrow_length / 2.0
        
        # FOC calculation
        foc_distance = balance_point - physical_center
        foc_percentage = (foc_distance / arrow_length) * 100
        
        return {
            "foc_percentage": foc_percentage,
            "balance_point": balance_point,
            "physical_center": physical_center,
            "total_weight": total_weight
        }
    
    def _estimate_arrow_speed(self, arrow_weight_grains: float, bow_weight_lbs: float) -> float:
        """Estimate arrow speed using simplified ballistics formula"""
        
        # Simplified speed estimation (actual speed depends on many bow factors)
        # This is a rough approximation based on common compound bow performance
        
        # Base speed for a 350-grain arrow at given draw weight
        base_speed = bow_weight_lbs * 3.5 + 180  # Rough approximation
        
        # Weight adjustment (lighter arrows go faster)
        weight_factor = (350 / arrow_weight_grains) ** 0.5
        estimated_speed = base_speed * weight_factor
        
        # Practical limits
        return min(max(estimated_speed, 150), 400)  # Between 150-400 fps
    
    def _calculate_kinetic_energy(self, weight_grains: float, speed_fps: float) -> float:
        """Calculate kinetic energy in foot-pounds"""
        weight_lbs = weight_grains / 7000  # Convert grains to pounds
        ke = 0.5 * weight_lbs * (speed_fps ** 2) / 32.174  # ft-lbs
        return ke
    
    def _calculate_momentum(self, weight_grains: float, speed_fps: float) -> float:
        """Calculate momentum (better penetration predictor than KE)"""
        weight_lbs = weight_grains / 7000
        momentum = weight_lbs * speed_fps
        return momentum
    
    def _calculate_penetration_score(self, weight: float, speed: float, foc: float, diameter: float) -> float:
        """Calculate penetration effectiveness score (0-100)"""
        
        # Momentum is key for penetration
        momentum = self._calculate_momentum(weight, speed)
        
        # FOC contribution (higher FOC = better penetration)
        foc_factor = min(foc / 12.0, 1.5)  # Optimal around 12%, diminishing returns after
        
        # Diameter factor (smaller = better penetration)
        diameter_factor = 0.25 / diameter if diameter > 0 else 1.0
        
        # Weight factor (heavier arrows penetrate better)
        weight_factor = min(weight / 400, 1.2)
        
        base_score = momentum * 10  # Base score from momentum
        penetration_score = base_score * foc_factor * diameter_factor * weight_factor
        
        return min(penetration_score, 100)
    
    def _calculate_accuracy_score(self, weight: float, foc: float, arrow_length: float, goal: TuningGoal) -> float:
        """Calculate accuracy potential score (0-100)"""
        
        # Base score from arrow stability factors
        base_score = 50
        
        # FOC contribution to accuracy
        if 8 <= foc <= 12:
            foc_bonus = 20
        elif 6 <= foc <= 15:
            foc_bonus = 15
        else:
            foc_bonus = max(0, 15 - abs(foc - 10))
        
        # Weight consistency factor
        if 350 <= weight <= 500:
            weight_bonus = 15
        else:
            weight_bonus = max(0, 15 - abs(weight - 425) / 50)
        
        # Arrow length factor (longer arrows can be more forgiving)
        if 28 <= arrow_length <= 31:
            length_bonus = 10
        else:
            length_bonus = max(0, 10 - abs(arrow_length - 29.5))
        
        # Tuning goal adjustment
        if goal == TuningGoal.MAXIMUM_ACCURACY:
            goal_bonus = 5
        else:
            goal_bonus = 0
        
        accuracy_score = base_score + foc_bonus + weight_bonus + length_bonus + goal_bonus
        return min(accuracy_score, 100)
    
    def _calculate_wind_drift_factor(self, weight: float, diameter: float, speed: float) -> float:
        """Calculate wind drift susceptibility factor"""
        
        # Heavier arrows drift less
        weight_factor = 400 / weight if weight > 0 else 1.0
        
        # Smaller diameter arrows drift less
        diameter_factor = diameter / 0.244  # Relative to standard diameter
        
        # Faster arrows drift less
        speed_factor = 300 / speed if speed > 0 else 1.0
        
        wind_drift_factor = weight_factor * diameter_factor * speed_factor
        return round(wind_drift_factor, 2)
    
    def _rate_trajectory(self, speed: float, weight: float) -> str:
        """Rate arrow trajectory characteristics"""
        
        if speed > 320:
            if weight < 350:
                return "Very flat, but may lack downrange energy"
            else:
                return "Flat trajectory with good energy retention"
        elif speed > 280:
            return "Good trajectory with balanced performance"
        elif speed > 250:
            return "Moderate arc, good for close-medium range"
        else:
            return "High arc, requires careful range estimation"
    
    def _score_configuration(self, analysis: TuningResult, goal: TuningGoal) -> float:
        """Score configuration based on tuning goal"""
        
        if goal == TuningGoal.MAXIMUM_SPEED:
            return analysis.speed_estimate
        elif goal == TuningGoal.OPTIMAL_PENETRATION:
            return analysis.penetration_score
        elif goal == TuningGoal.MAXIMUM_ACCURACY:
            return analysis.accuracy_score
        elif goal == TuningGoal.HUNTING_EFFECTIVENESS:
            # Balanced score for hunting
            return (analysis.penetration_score * 0.4 + 
                   analysis.kinetic_energy * 0.3 +
                   analysis.accuracy_score * 0.3)
        else:  # BALANCED_PERFORMANCE
            # Equal weighting of all factors
            return (analysis.speed_estimate / 4 +
                   analysis.penetration_score * 0.3 +
                   analysis.accuracy_score * 0.3 +
                   analysis.kinetic_energy * 0.4)
    
    def _generate_tuning_recommendations(self, components: ArrowComponents, foc_data: Dict[str, float],
                                       total_weight: float, speed: float, goal: TuningGoal,
                                       arrow_type: ArrowType) -> List[str]:
        """Generate specific tuning recommendations"""
        
        recommendations = []
        foc = foc_data['foc_percentage']
        
        # FOC recommendations
        ideal_foc_range = self.calculate_ideal_foc_range(arrow_type)
        if foc < ideal_foc_range[0]:
            recommendations.append(f"FOC is low ({foc:.1f}%) - consider heavier points or lighter nock/fletching")
        elif foc > ideal_foc_range[1]:
            recommendations.append(f"FOC is high ({foc:.1f}%) - consider lighter points or heavier nock/fletching")
        else:
            recommendations.append(f"FOC is optimal ({foc:.1f}%) for {arrow_type.value}")
        
        # Weight recommendations
        if arrow_type in [ArrowType.HUNTING_BIG_GAME, ArrowType.HUNTING_SMALL_GAME]:
            if total_weight < 350:
                recommendations.append("Arrow may be too light for hunting - consider heavier components")
            elif total_weight > 550:
                recommendations.append("Arrow may be very heavy - check if speed is acceptable")
        
        # Speed-specific recommendations
        if speed < 250 and goal == TuningGoal.MAXIMUM_SPEED:
            recommendations.append("Consider lighter arrow components to increase speed")
        elif speed > 350:
            recommendations.append("Very fast setup - ensure arrow spine is adequate")
        
        # Component-specific recommendations
        if components.point_weight < 75:
            recommendations.append("Point weight is very light - may affect FOC and penetration")
        elif components.point_weight > 150:
            recommendations.append("Point weight is heavy - verify spine selection")
        
        return recommendations
    
    def _get_optimization_recommendations(self, results: List[Dict[str, Any]], goal: TuningGoal) -> List[str]:
        """Generate optimization-specific recommendations"""
        
        recommendations = []
        best = results[0]
        worst = results[-1]
        
        score_improvement = best['score'] - worst['score']
        
        recommendations.append(f"Best configuration scores {best['score']:.1f} vs worst at {worst['score']:.1f}")
        recommendations.append(f"Point weight optimization shows {score_improvement:.1f}% improvement potential")
        
        if goal == TuningGoal.MAXIMUM_SPEED:
            fastest = max(results, key=lambda x: x['speed'])
            recommendations.append(f"Fastest setup: {fastest['point_weight']:.0f}gr point = {fastest['speed']:.0f} fps")
        
        elif goal == TuningGoal.OPTIMAL_PENETRATION:
            best_penetration = max(results, key=lambda x: x['analysis'].penetration_score)
            recommendations.append(f"Best penetration: {best_penetration['point_weight']:.0f}gr point")
        
        return recommendations

# Example usage and testing
if __name__ == "__main__":
    print("🎯 Advanced Tuning Calculator Test")
    print("=" * 60)
    
    calculator = TuningCalculator()
    
    # Test arrow configuration
    components = ArrowComponents(
        shaft_weight=300,    # grains
        point_weight=100,    # grains
        nock_weight=10,      # grains
        fletching_weight=15, # grains
        insert_weight=15     # grains
    )
    
    print("\n📋 Test Configuration:")
    print(f"   Shaft: {components.shaft_weight}gr")
    print(f"   Point: {components.point_weight}gr")
    print(f"   Total: {calculator._calculate_total_weight(components):.0f}gr")
    
    # Comprehensive analysis
    result = calculator.comprehensive_tuning_analysis(
        components=components,
        arrow_length=29.0,
        bow_weight=65,
        tuning_goal=TuningGoal.HUNTING_EFFECTIVENESS,
        arrow_type=ArrowType.HUNTING_BIG_GAME
    )
    
    print(f"\n🎯 Analysis Results:")
    print(f"   Penetration Score: {result.penetration_score:.1f}/100")
    print(f"   Accuracy Score: {result.accuracy_score:.1f}/100")
    print(f"   Momentum: {result.momentum:.2f}")
    print(f"   Wind Drift Factor: {result.wind_drift_factor}")
    print(f"   Trajectory: {result.trajectory_rating}")
    
    print(f"\n💡 Recommendations:")
    for rec in result.recommendations:
        print(f"   • {rec}")
    
    # Test optimization
    print(f"\n🔧 Point Weight Optimization Test:")
    optimization = calculator.optimize_for_goal(
        base_components=components,
        arrow_length=29.0,
        bow_weight=65,
        tuning_goal=TuningGoal.HUNTING_EFFECTIVENESS,
        available_point_weights=[75, 100, 125, 150, 175]
    )
    
    print(f"   Best point weight: {optimization['best_configuration']['components'].point_weight:.0f}gr")
    print(f"   Score: {optimization['best_configuration']['score']:.1f}")
    
    # Test broadhead adjustments
    print(f"\n🏹 Broadhead Tuning Test:")
    bh_adjustments = calculator.calculate_broadhead_tuning_adjustments(
        field_point_weight=100,
        broadhead_weight=125,
        current_foc=10.5
    )
    
    print(f"   Weight difference: {bh_adjustments['weight_difference']:.0f}gr")
    print(f"   New FOC estimate: {bh_adjustments['new_foc_estimate']:.1f}%")
    for rec in bh_adjustments['recommendations'][:2]:
        print(f"   • {rec}")