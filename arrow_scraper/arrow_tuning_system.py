#!/usr/bin/env python3
"""
Complete Arrow Tuning System
Integrates database, spine calculations, matching engine, and tuning calculations
into a unified arrow selection and tuning platform
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import json
from datetime import datetime

# Import all system components
from arrow_database import ArrowDatabase
from spine_calculator import SpineCalculator, BowConfiguration, BowType
from arrow_matching_engine import ArrowMatchingEngine, MatchRequest, ArrowMatch
from tuning_calculator import TuningCalculator, ArrowComponents, TuningGoal, ArrowType, TuningResult

@dataclass
class ArcherProfile:
    """Archer configuration and preferences"""
    name: str
    bow_config: BowConfiguration
    shooting_style: str  # target, hunting, traditional, etc.
    experience_level: str  # beginner, intermediate, advanced
    preferred_manufacturers: List[str] = None
    budget_range: Tuple[float, float] = None  # (min, max) per dozen
    arrow_length: float = 29.0
    point_weight_preference: float = 100.0
    target_foc_range: Tuple[float, float] = None
    notes: str = ""

@dataclass
class TuningSession:
    """Complete tuning session results"""
    session_id: str
    archer_profile: ArcherProfile
    recommended_arrows: List[ArrowMatch]
    tuning_analysis: Dict[str, TuningResult]
    optimization_results: Dict[str, Any]
    session_timestamp: str
    recommendations: List[str]
    next_steps: List[str]

class ArrowTuningSystem:
    """Main arrow tuning system integrating all components"""
    
    def __init__(self, database_path: str = "arrow_database.db"):
        """Initialize the complete tuning system"""
        
        print("🚀 Initializing Arrow Tuning System")
        
        # Initialize all subsystems
        self.database = ArrowDatabase(database_path)
        self.spine_calculator = SpineCalculator()
        self.matching_engine = ArrowMatchingEngine(database_path)
        self.tuning_calculator = TuningCalculator()
        
        print("✅ All subsystems initialized")
    
    def create_tuning_session(self, archer_profile: ArcherProfile,
                            tuning_goals: List[TuningGoal] = None,
                            custom_requirements: Dict[str, Any] = None,
                            material_preference: str = None) -> TuningSession:
        """
        Create a complete tuning session for an archer
        
        Args:
            archer_profile: Archer configuration and preferences
            tuning_goals: List of tuning objectives (default: balanced performance)
            custom_requirements: Additional custom requirements
            
        Returns:
            Complete tuning session with recommendations
        """
        
        if tuning_goals is None:
            tuning_goals = [TuningGoal.BALANCED_PERFORMANCE]
        
        session_id = f"tuning_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        print(f"🎯 Starting Tuning Session: {session_id}")
        print(f"   Archer: {archer_profile.name}")
        print(f"   Bow: {archer_profile.bow_config.draw_weight}# {archer_profile.bow_config.bow_type.value}")
        print(f"   Goals: {[goal.value for goal in tuning_goals]}")
        print(f"   Material Preference: {material_preference}")
        
        # Step 1: Create match request from archer profile
        match_request = self._create_match_request(archer_profile, custom_requirements, material_preference)
        
        # Step 2: Find matching arrows
        print("\n🔍 Finding matching arrows...")
        arrow_matches = self.matching_engine.find_matching_arrows(match_request)
        
        if not arrow_matches:
            print("❌ No suitable arrows found")
            return self._create_empty_session(session_id, archer_profile)
        
        print(f"✅ Found {len(arrow_matches)} arrow matches")
        
        # Step 3: Detailed tuning analysis for top matches
        print("\n🔧 Performing detailed tuning analysis...")
        tuning_analyses = {}
        
        for i, arrow_match in enumerate(arrow_matches[:3], 1):  # Analyze top 3 matches
            print(f"   Analyzing match {i}: {arrow_match.manufacturer} {arrow_match.model_name}")
            
            # Create arrow components based on match
            components = ArrowComponents(
                shaft_weight=arrow_match.gpi_weight * archer_profile.arrow_length,
                point_weight=archer_profile.point_weight_preference,
                nock_weight=10.0,  # Standard nock weight
                fletching_weight=15.0,  # Standard fletching weight
                insert_weight=15.0  # Standard insert weight
            )
            
            # Perform comprehensive analysis
            analysis = self.tuning_calculator.comprehensive_tuning_analysis(
                components=components,
                arrow_length=archer_profile.arrow_length,
                bow_weight=archer_profile.bow_config.draw_weight,
                arrow_diameter=arrow_match.outer_diameter or 0.246,
                tuning_goal=tuning_goals[0],  # Primary goal
                arrow_type=self._determine_arrow_type(archer_profile.shooting_style)
            )
            
            tuning_analyses[f"{arrow_match.manufacturer}_{arrow_match.model_name}"] = analysis
        
        # Step 4: Optimization analysis
        print("\n⚙️ Performing optimization analysis...")
        optimization_results = {}
        
        if arrow_matches:
            best_match = arrow_matches[0]
            base_components = ArrowComponents(
                shaft_weight=best_match.gpi_weight * archer_profile.arrow_length,
                point_weight=archer_profile.point_weight_preference,
                nock_weight=10.0,
                fletching_weight=15.0,
                insert_weight=15.0
            )
            
            # Test different point weights
            point_weights = [75, 100, 125, 150, 175, 200]
            
            for goal in tuning_goals:
                optimization = self.tuning_calculator.optimize_for_goal(
                    base_components=base_components,
                    arrow_length=archer_profile.arrow_length,
                    bow_weight=archer_profile.bow_config.draw_weight,
                    tuning_goal=goal,
                    available_point_weights=point_weights
                )
                optimization_results[goal.value] = optimization
        
        # Step 5: Generate comprehensive recommendations
        recommendations = self._generate_session_recommendations(
            archer_profile, arrow_matches, tuning_analyses, optimization_results
        )
        
        # Step 6: Create next steps
        next_steps = self._generate_next_steps(archer_profile, arrow_matches)
        
        # Create session result
        session = TuningSession(
            session_id=session_id,
            archer_profile=archer_profile,
            recommended_arrows=arrow_matches,
            tuning_analysis=tuning_analyses,
            optimization_results=optimization_results,
            session_timestamp=datetime.now().isoformat(),
            recommendations=recommendations,
            next_steps=next_steps
        )
        
        print(f"✅ Tuning session complete: {session_id}")
        return session
    
    def generate_comprehensive_report(self, session: TuningSession) -> str:
        """Generate a comprehensive tuning report"""
        
        profile = session.archer_profile
        
        report = f"""
🎯 COMPREHENSIVE ARROW TUNING REPORT
{'=' * 80}

ARCHER PROFILE:
• Name: {profile.name}
• Experience Level: {profile.experience_level.title()}
• Shooting Style: {profile.shooting_style.title()}

BOW CONFIGURATION:
• Type: {profile.bow_config.bow_type.value.title()}
• Draw Weight: {profile.bow_config.draw_weight}#
• Draw Length: {profile.bow_config.draw_length}"
• Arrow Length: {profile.arrow_length}"
• Cam Type: {getattr(profile.bow_config, 'cam_type', 'N/A')}
• Arrow Rest: {getattr(profile.bow_config, 'arrow_rest_type', 'N/A')}

SESSION RESULTS:
• Session ID: {session.session_id}
• Generated: {session.session_timestamp}
• Arrows Analyzed: {len(session.recommended_arrows)}
• Tuning Goals: {list(session.optimization_results.keys())}

TOP ARROW RECOMMENDATIONS:
"""
        
        # Top 3 recommendations with detailed analysis
        for i, arrow in enumerate(session.recommended_arrows[:3], 1):
            # Get tuning analysis for this arrow
            analysis_key = f"{arrow.manufacturer}_{arrow.model_name}"
            analysis = session.tuning_analysis.get(analysis_key)
            
            confidence_emoji = {"high": "🟢", "medium": "🟡", "low": "🔴"}
            
            report += f"""
{i}. {arrow.manufacturer} {arrow.model_name}
   {confidence_emoji[arrow.confidence_level]} Overall Match Score: {arrow.match_score}/100
   
   SPINE SPECIFICATIONS:
   • Matched Spine: {arrow.matched_spine}
   • Spine Deviation: ±{arrow.spine_deviation:.0f}
   • Available Spines: {len(arrow.spine_specifications)} options
   • GPI Weight: {arrow.gpi_weight}
   • Outer Diameter: {arrow.outer_diameter:.3f}"
   
   PERFORMANCE ANALYSIS:
"""
            
            if analysis:
                report += f"""   • Total Arrow Weight: ~{analysis.total_weight:.0f} grains
   • FOC: {analysis.foc_percentage:.1f}%
   • Estimated Speed: {analysis.speed_estimate:.0f} fps
   • Kinetic Energy: {analysis.kinetic_energy:.0f} ft-lbs
   • Momentum: {analysis.momentum:.2f}
   • Penetration Score: {analysis.penetration_score:.0f}/100
   • Accuracy Score: {analysis.accuracy_score:.0f}/100
   • Wind Drift Factor: {analysis.wind_drift_factor}
   • Trajectory: {analysis.trajectory_rating}
"""
            
            report += f"""
   ✅ MATCH REASONS:
"""
            for reason in arrow.match_reasons:
                report += f"      • {reason}\n"
            
            if arrow.potential_issues:
                report += f"""   ⚠️  CONSIDERATIONS:
"""
                for issue in arrow.potential_issues:
                    report += f"      • {issue}\n"
        
        # Optimization results
        if session.optimization_results:
            report += f"""

OPTIMIZATION ANALYSIS:
"""
            for goal, optimization in session.optimization_results.items():
                best_config = optimization['best_configuration']
                report += f"""
{goal.replace('_', ' ').title()}:
• Optimal Point Weight: {best_config['components'].point_weight:.0f} grains
• Performance Score: {best_config['score']:.1f}
• Total Arrow Weight: {best_config['analysis'].total_weight:.0f} grains
• FOC: {best_config['analysis'].foc_percentage:.1f}%
• Estimated Speed: {best_config['analysis'].speed_estimate:.0f} fps
"""
        
        # Session recommendations
        report += f"""

EXPERT RECOMMENDATIONS:
"""
        for rec in session.recommendations:
            report += f"• {rec}\n"
        
        # Next steps
        report += f"""

NEXT STEPS:
"""
        for step in session.next_steps:
            report += f"• {step}\n"
        
        report += f"""

IMPORTANT NOTES:
• All calculations are estimates based on standard formulas
• Actual performance may vary based on bow setup and conditions
• Paper tuning and field testing are recommended for final verification
• Consider professional archery shop consultation for setup
• Broadhead testing required for hunting applications

Generated by Arrow Tuning System v2.0
Report ID: {session.session_id}
"""
        
        return report
    
    def save_session(self, session: TuningSession, filename: Optional[str] = None) -> str:
        """Save tuning session to file"""
        
        if filename is None:
            filename = f"tuning_session_{session.session_id}.json"
        
        # Convert session to serializable format
        session_data = {
            "session_id": session.session_id,
            "timestamp": session.session_timestamp,
            "archer_profile": {
                "name": session.archer_profile.name,
                "bow_config": {
                    "draw_weight": session.archer_profile.bow_config.draw_weight,
                    "draw_length": session.archer_profile.bow_config.draw_length,
                    "bow_type": session.archer_profile.bow_config.bow_type.value,
                    "cam_type": getattr(session.archer_profile.bow_config, 'cam_type', 'medium'),
                    "arrow_rest_type": getattr(session.archer_profile.bow_config, 'arrow_rest_type', 'drop_away')
                },
                "shooting_style": session.archer_profile.shooting_style,
                "experience_level": session.archer_profile.experience_level,
                "arrow_length": session.archer_profile.arrow_length,
                "point_weight_preference": session.archer_profile.point_weight_preference
            },
            "recommended_arrows": [
                {
                    "manufacturer": arrow.manufacturer,
                    "model_name": arrow.model_name,
                    "match_score": arrow.match_score,
                    "matched_spine": arrow.matched_spine,
                    "gpi_weight": arrow.gpi_weight,
                    "outer_diameter": arrow.outer_diameter,
                    "confidence_level": arrow.confidence_level
                }
                for arrow in session.recommended_arrows
            ],
            "recommendations": session.recommendations,
            "next_steps": session.next_steps
        }
        
        with open(filename, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        print(f"✅ Session saved to {filename}")
        return filename
    
    def _create_match_request(self, archer_profile: ArcherProfile, 
                            custom_requirements: Optional[Dict[str, Any]],
                            material_preference: Optional[str] = None) -> MatchRequest:
        """Create match request from archer profile"""
        
        # Determine arrow type preference
        arrow_type = None
        if "hunting" in archer_profile.shooting_style.lower():
            arrow_type = "hunting"
        elif "target" in archer_profile.shooting_style.lower():
            arrow_type = "target"
        
        request = MatchRequest(
            bow_config=archer_profile.bow_config,
            arrow_length=archer_profile.arrow_length,
            point_weight=archer_profile.point_weight_preference,
            preferred_manufacturers=archer_profile.preferred_manufacturers,
            target_foc_range=archer_profile.target_foc_range,
            arrow_type_preference=arrow_type,
            material_preference=material_preference,
            max_results=10
        )
        
        # Apply custom requirements
        if custom_requirements:
            if 'diameter_range' in custom_requirements:
                request.target_diameter_range = custom_requirements['diameter_range']
            if 'weight_range' in custom_requirements:
                request.target_weight_range = custom_requirements['weight_range']
        
        return request
    
    def _determine_arrow_type(self, shooting_style: str) -> ArrowType:
        """Determine ArrowType enum from shooting style string"""
        
        style_lower = shooting_style.lower()
        
        if "hunting" in style_lower:
            if "big game" in style_lower:
                return ArrowType.HUNTING_BIG_GAME
            else:
                return ArrowType.HUNTING_SMALL_GAME
        elif "target" in style_lower:
            if "indoor" in style_lower:
                return ArrowType.TARGET_INDOOR
            else:
                return ArrowType.TARGET_OUTDOOR
        elif "field" in style_lower:
            return ArrowType.FIELD_ARCHERY
        elif "traditional" in style_lower:
            return ArrowType.TRADITIONAL_ARCHERY
        else:
            return ArrowType.TARGET_OUTDOOR  # Default
    
    def _create_empty_session(self, session_id: str, archer_profile: ArcherProfile) -> TuningSession:
        """Create empty session when no arrows found"""
        
        return TuningSession(
            session_id=session_id,
            archer_profile=archer_profile,
            recommended_arrows=[],
            tuning_analysis={},
            optimization_results={},
            session_timestamp=datetime.now().isoformat(),
            recommendations=[
                "No arrows found matching your criteria",
                "Consider expanding manufacturer preferences",
                "Check if draw weight and length are correctly specified",
                "Consider consulting with a professional archery shop"
            ],
            next_steps=[
                "Review bow configuration settings",
                "Expand search criteria",
                "Consider custom arrow building"
            ]
        )
    
    def _generate_session_recommendations(self, archer_profile: ArcherProfile,
                                        arrow_matches: List[ArrowMatch],
                                        tuning_analyses: Dict[str, TuningResult],
                                        optimization_results: Dict[str, Any]) -> List[str]:
        """Generate comprehensive session recommendations"""
        
        recommendations = []
        
        if not arrow_matches:
            return ["No suitable arrows found - consider expanding search criteria"]
        
        # Top match recommendation
        best_match = arrow_matches[0]
        recommendations.append(
            f"Primary recommendation: {best_match.manufacturer} {best_match.model_name} "
            f"with {best_match.matched_spine} spine (match score: {best_match.match_score})"
        )
        
        # Experience-based recommendations
        if archer_profile.experience_level == "beginner":
            recommendations.append("As a beginner, focus on consistent form before fine-tuning equipment")
            recommendations.append("Consider starting with the most forgiving arrow setup")
        elif archer_profile.experience_level == "advanced":
            recommendations.append("Consider testing multiple spine options for optimal tuning")
            recommendations.append("Paper tuning and bare shaft testing recommended")
        
        # Shooting style recommendations
        if "hunting" in archer_profile.shooting_style.lower():
            recommendations.append("Ensure broadhead compatibility testing before hunting season")
            recommendations.append("Consider fixed-blade broadheads for consistency")
        elif "target" in archer_profile.shooting_style.lower():
            recommendations.append("Focus on consistency and accuracy over speed")
            recommendations.append("Consider spine selection based on shooting distance")
        
        # Optimization insights
        if optimization_results:
            for goal, optimization in optimization_results.items():
                best_point_weight = optimization['best_configuration']['components'].point_weight
                recommendations.append(
                    f"For {goal.replace('_', ' ')}: optimal point weight is {best_point_weight:.0f} grains"
                )
        
        # General tuning recommendations
        recommendations.append("Start with manufacturer's recommended spine, then fine-tune")
        recommendations.append("Keep detailed records of your testing and results")
        
        return recommendations
    
    def _generate_next_steps(self, archer_profile: ArcherProfile, 
                           arrow_matches: List[ArrowMatch]) -> List[str]:
        """Generate next steps for the archer"""
        
        next_steps = []
        
        if arrow_matches:
            # Purchase recommendations
            next_steps.append(f"Purchase test arrows in {arrow_matches[0].matched_spine} spine")
            next_steps.append("Start with 6 arrows for initial testing")
            
            # Testing steps
            next_steps.append("Perform paper tuning at 6 feet")
            next_steps.append("Conduct group testing at your primary shooting distance")
            
            if "hunting" in archer_profile.shooting_style.lower():
                next_steps.append("Test with your intended broadheads")
                next_steps.append("Verify point of impact consistency")
            
            # Fine-tuning
            next_steps.append("Adjust rest position if needed based on paper tuning")
            next_steps.append("Consider micro-spine adjustments if groups are inconsistent")
            
        else:
            next_steps.append("Expand search criteria or consult archery professional")
            next_steps.append("Consider custom arrow building service")
        
        # General steps
        next_steps.append("Document all testing results for future reference")
        next_steps.append("Schedule follow-up tuning session after testing")
        
        return next_steps

# Example usage and testing
if __name__ == "__main__":
    print("🏹 Complete Arrow Tuning System Demo")
    print("=" * 80)
    
    # Initialize system
    system = ArrowTuningSystem()
    
    # Create archer profile
    test_bow = BowConfiguration(
        draw_weight=65,
        draw_length=28.5,
        bow_type=BowType.COMPOUND,
        cam_type="medium",
        arrow_rest_type="drop_away"
    )
    
    archer = ArcherProfile(
        name="Test Archer",
        bow_config=test_bow,
        shooting_style="hunting big game",
        experience_level="intermediate",
        preferred_manufacturers=["Gold Tip", "Easton", "Carbon Express"],
        arrow_length=29.0,
        point_weight_preference=100.0,
        target_foc_range=(10.0, 12.0)
    )
    
    print(f"\n👤 Archer Profile:")
    print(f"   Name: {archer.name}")
    print(f"   Bow: {archer.bow_config.draw_weight}# @ {archer.bow_config.draw_length}\"")
    print(f"   Style: {archer.shooting_style}")
    print(f"   Experience: {archer.experience_level}")
    
    # Create tuning session
    session = system.create_tuning_session(
        archer_profile=archer,
        tuning_goals=[TuningGoal.HUNTING_EFFECTIVENESS, TuningGoal.BALANCED_PERFORMANCE]
    )
    
    # Generate and display report
    report = system.generate_comprehensive_report(session)
    print(report[:2000] + "..." if len(report) > 2000 else report)
    
    # Save session
    filename = system.save_session(session)
    print(f"\n💾 Session saved to: {filename}")