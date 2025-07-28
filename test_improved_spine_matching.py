#!/usr/bin/env python3
"""Test improved spine matching with user's exact scenario"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'arrow_scraper'))

from arrow_tuning_system import ArrowTuningSystem, ArcherProfile, BowConfiguration, BowType, TuningGoal

def test_improved_spine_matching():
    print("🎯 Testing Improved Spine Matching")
    print("=" * 50)
    
    # Test the exact scenario: 24 lbs recurve with 26" arrow
    bow_config = BowConfiguration(
        draw_weight=24,
        draw_length=28,
        bow_type=BowType.RECURVE
    )
    
    archer_profile = ArcherProfile(
        name="Test User",
        bow_config=bow_config,
        shooting_style="target",
        experience_level="intermediate",
        arrow_length=26.0,
        point_weight_preference=100.0
    )
    
    print(f"🏹 Test Configuration:")
    print(f"   Bow: {bow_config.draw_weight}# {bow_config.bow_type.value}")
    print(f"   Arrow length: {archer_profile.arrow_length}\"")
    print(f"   Point weight: {archer_profile.point_weight_preference}gr")
    
    # Create tuning system and session
    ts = ArrowTuningSystem()
    session = ts.create_tuning_session(
        archer_profile,
        tuning_goals=[TuningGoal.MAXIMUM_ACCURACY]
    )
    
    print(f"\n📊 Results:")
    print(f"   Recommended arrows: {len(session.recommended_arrows)}")
    
    if session.recommended_arrows:
        print(f"\n🎯 Top Matches:")
        for i, arrow in enumerate(session.recommended_arrows[:10]):
            print(f"   {i+1}. {arrow.manufacturer} {arrow.model_name}")
            print(f"      Spine: {arrow.matched_spine} (deviation: ±{arrow.spine_deviation:.0f})")
            print(f"      Score: {arrow.match_score:.1f}")
            print(f"      GPI: {arrow.gpi_weight}gr, Diameter: {arrow.outer_diameter:.3f}\"")
            print()
        
        # Test with the specific spine mentioned by user (1620)
        print(f"\n🔍 Analyzing spine deviation from calculated optimal:")
        print(f"   User mentioned spine 1620 but got no results")
        print(f"   Our calculated optimal: {session.recommended_arrows[0].matched_spine}")
        
        # Check what spine 1620 would be 
        target_spine_1620 = 1620
        closest_to_1620 = min(session.recommended_arrows, 
                             key=lambda x: abs(x.matched_spine - target_spine_1620))
        print(f"   Closest to 1620: {closest_to_1620.manufacturer} {closest_to_1620.model_name}")
        print(f"   Spine {closest_to_1620.matched_spine} (deviation from 1620: ±{abs(closest_to_1620.matched_spine - target_spine_1620):.0f})")
        
    else:
        print("   ❌ Still no arrows found!")
        print("   This suggests a deeper issue in the database or search logic")

if __name__ == "__main__":
    test_improved_spine_matching()