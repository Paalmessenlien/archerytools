#!/usr/bin/env python3
import sys
sys.path.append('/home/paal/arrowtuner2/arrow_scraper')

from arrow_matching_engine import ArrowMatchingEngine, MatchRequest
from models import BowConfiguration, BowType, ArcherProfile, TuningGoal

def debug_wood_arrow_matching():
    """Debug the exact matching process for wood arrows"""
    
    print("🔍 Debugging Wood Arrow Matching Process")
    print("=" * 50)
    
    # Create the exact request that should work
    bow_config = BowConfiguration(
        draw_weight=42,
        draw_length=28,
        bow_type=BowType.TRADITIONAL,
        cam_type='medium',
        arrow_rest_type='drop_away'
    )
    
    archer_profile = ArcherProfile(
        name='Test',
        bow_config=bow_config,
        shooting_style='target',
        experience_level='intermediate'
    )
    
    request = MatchRequest(
        archer_profile=archer_profile,
        arrow_length=30,
        point_weight=100,
        nock_weight=10,
        fletching_weight=15,
        tuning_goals=[TuningGoal.MAXIMUM_ACCURACY],
        material_preference='Wood',
        min_spine_options=3  # Default value
    )
    
    print(f"Request material preference: '{request.material_preference}'")
    print(f"Request min_spine_options: {request.min_spine_options}")
    print()
    
    # Test the matching engine
    engine = ArrowMatchingEngine()
    
    print("Step 1: Database search test")
    search_results = engine.db.search_arrows(
        spine_min=33,
        spine_max=53,
        material='Wood',
        limit=50
    )
    print(f"Database returned {len(search_results)} candidates")
    
    if search_results:
        print("\nStep 2: Processing candidates")
        arrow_matches = []
        
        for i, arrow_data in enumerate(search_results[:3]):
            arrow_id = arrow_data['id']
            print(f"\nCandidate {i+1}: {arrow_data['manufacturer']} {arrow_data['model_name']} (ID: {arrow_id})")
            
            # Test get_arrow_details
            arrow_details = engine.db.get_arrow_details(arrow_id)
            if arrow_details:
                spine_specs = arrow_details.get('spine_specifications', [])
                print(f"  Arrow details: {len(spine_specs)} spine specifications")
                
                # Test the min_spine_req logic
                material_pref = request.material_preference
                if material_pref and material_pref.lower() == 'wood':
                    min_spine_req = 2
                else:
                    min_spine_req = request.min_spine_options
                    
                print(f"  Material preference: '{material_pref}'")
                print(f"  Min spine requirement: {min_spine_req}")
                print(f"  Passes spine count filter: {len(spine_specs) >= min_spine_req}")
                
                if len(spine_specs) >= min_spine_req:
                    print(f"  ✅ Candidate {i+1} should be processed")
                else:
                    print(f"  ❌ Candidate {i+1} filtered out")
            else:
                print(f"  ❌ get_arrow_details returned None")
    
    print(f"\nStep 3: Full matching engine test")
    matches = engine.find_matching_arrows(request)
    print(f"Final result: {len(matches)} matches found")

if __name__ == "__main__":
    debug_wood_arrow_matching()