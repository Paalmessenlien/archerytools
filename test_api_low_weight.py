#!/usr/bin/env python3
"""Test the API endpoint for low draw weight issue"""

import json
import sys
import os

# Add the arrow_scraper directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'arrow_scraper'))

from arrow_tuning_system import ArrowTuningSystem, ArcherProfile, BowConfiguration, BowType, TuningGoal

def test_api_low_weight():
    print("🎯 Testing API for 24 lbs recurve, 26\" arrow")
    print("=" * 50)
    
    # Create the exact configuration from the user's example
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
        arrow_length=26.0,  # 26" arrow as mentioned
        point_weight_preference=100.0
    )
    
    # Create tuning system and session
    ts = ArrowTuningSystem()
    session = ts.create_tuning_session(
        archer_profile,
        tuning_goals=[TuningGoal.MAXIMUM_ACCURACY]
    )
    
    # Check session attributes
    print(f"📊 Session attributes: {dir(session)}")
    
    if hasattr(session, 'spine_calculation'):
        print(f"📊 Calculated spine: {session.spine_calculation['calculated_spine']}")
        print(f"📊 Spine range: {session.spine_calculation['spine_range']}")
    elif hasattr(session, 'archer_profile'):
        print(f"📊 Archer profile found")
    
    print(f"\n🏹 Recommended arrows: {len(session.recommended_arrows)}")
    
    if session.recommended_arrows:
        for i, arrow in enumerate(session.recommended_arrows[:5]):
            print(f"   {i+1}. {arrow.manufacturer} {arrow.model_name}")
            print(f"      Spine: {arrow.matched_spine} (deviation: ±{arrow.spine_deviation:.0f})")
            print(f"      Score: {arrow.match_score:.1f}")
            print()
    else:
        print("   ❌ No arrows found!")
        
        # Debug: Let's see what spine ranges are being searched
        print(f"\n🔍 Debug information:")
        print(f"   Calculated spine: {session.spine_calculation['calculated_spine']}")
        print(f"   Search range: {session.spine_calculation['spine_range']}")
        
        # Check if we can find any arrows with a much wider search
        print(f"\n🔄 Testing with manual wider search...")
        
        from arrow_database import ArrowDatabase
        db = ArrowDatabase()
        
        # Try a much wider spine range
        wide_search = db.search_arrows(
            spine_min=1000,  # Much wider
            spine_max=2500,
            limit=20
        )
        
        print(f"   Wide search found {len(wide_search)} arrows")
        if wide_search:
            for arrow in wide_search[:5]:
                print(f"   - {arrow['manufacturer']} {arrow['model_name']} (spine: {arrow['min_spine']}-{arrow['max_spine']})")
                
                # Check if any of these arrows have spine specs near our target
                arrow_details = db.get_arrow_details(arrow['id'])
                if arrow_details:
                    target_spine = session.spine_calculation['calculated_spine']
                    spine_specs = arrow_details.get('spine_specifications', [])
                    for spec in spine_specs:
                        if spec.get('spine'):
                            deviation = abs(spec['spine'] - target_spine)
                            if deviation < 300:  # Within 300 spine units
                                print(f"     -> Has spine {spec['spine']} (deviation: ±{deviation:.0f})")

if __name__ == "__main__":
    test_api_low_weight()