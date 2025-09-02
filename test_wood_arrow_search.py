#!/usr/bin/env python3
"""Test wood arrow search functionality to verify the fix"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'arrow_scraper'))

from arrow_scraper.arrow_matching_engine import ArrowMatchingEngine, MatchRequest
from arrow_scraper.spine_calculator import BowConfiguration, BowType

def test_wood_arrow_search():
    """Test that wood arrows can be found with corrected material preference"""
    
    print("🪵 Testing Wood Arrow Search Functionality")
    print("=" * 60)
    
    # Create test request with wood material preference
    bow_config = BowConfiguration(
        bow_type=BowType.TRADITIONAL,
        draw_weight=40,
        draw_length=28
    )
    
    request = MatchRequest(
        bow_config=bow_config,
        arrow_length=28,
        point_weight=125,
        material_preference='Wood',  # Fixed: Now using title case
        max_results=10
    )
    
    # Initialize matching engine
    engine = ArrowMatchingEngine()
    
    print(f"🎯 Test Configuration:")
    print(f"   Material Preference: '{request.material_preference}'")
    print(f"   Bow Type: {bow_config.bow_type.value}")
    print(f"   Draw Weight: {bow_config.draw_weight}lbs")
    
    # Test material mapping
    mapped_material = engine._map_material_preference(request.material_preference)
    print(f"   Mapped Material: '{mapped_material}'")
    
    # Search for arrows
    matches = engine.find_matching_arrows(request)
    
    print(f"\n📊 Search Results:")
    print(f"   Found {len(matches)} wood arrow matches")
    
    if matches:
        print(f"\n🪵 Wood Arrow Examples:")
        for i, match in enumerate(matches[:5], 1):
            print(f"   {i}. {match.manufacturer} - {match.model_name}")
            print(f"      Material: {match.material}")
            print(f"      Spine: {match.matched_spine}")
            print(f"      Confidence: {match.confidence_level}")
        
        print(f"\n✅ SUCCESS: Wood arrows are being found!")
        return True
    else:
        print(f"\n❌ FAILED: No wood arrows found")
        
        # Debug: Check if wood arrows exist in database
        from arrow_scraper.arrow_database import ArrowDatabase
        db = ArrowDatabase()
        wood_arrows_db = db.search_arrows(material='Wood', limit=5)
        
        print(f"\n🔍 Debug - Wood arrows in database:")
        print(f"   Database contains {len(wood_arrows_db)} wood arrows")
        
        if wood_arrows_db:
            for arrow in wood_arrows_db:
                print(f"   - {arrow['manufacturer']} {arrow['model_name']} ({arrow['material']})")
        
        return False

def test_spine_calculation_with_wood():
    """Test that wood material triggers pound-based spine calculation"""
    
    print(f"\n🧮 Testing Wood Arrow Spine Calculation")
    print("=" * 60)
    
    from arrow_scraper.spine_service import calculate_unified_spine
    
    # Test wood arrow spine calculation
    result = calculate_unified_spine(
        draw_weight=40,
        arrow_length=28,
        point_weight=125,
        bow_type='traditional',
        material_preference='Wood'  # Should trigger wood arrow logic
    )
    
    calculated_spine = result['calculated_spine']
    source = result.get('source', 'unknown')
    
    print(f"📊 Wood Arrow Calculation Result:")
    print(f"   Calculated Spine: {calculated_spine}")
    print(f"   Source: {source}")
    
    # Wood arrows should return pound-based values like "40#"
    if isinstance(calculated_spine, str) and '#' in calculated_spine:
        print(f"✅ SUCCESS: Wood arrow pound-based calculation working!")
        return True
    else:
        print(f"❌ FAILED: Expected pound-based spine (e.g. '40#'), got numeric: {calculated_spine}")
        return False

if __name__ == "__main__":
    try:
        # Test search functionality
        search_success = test_wood_arrow_search()
        
        # Test calculation functionality  
        calc_success = test_spine_calculation_with_wood()
        
        if search_success and calc_success:
            print(f"\n🎉 ALL TESTS PASSED: Wood arrow functionality working!")
        else:
            print(f"\n⚠️  SOME TESTS FAILED: Wood arrow issues remain")
            
    except Exception as e:
        print(f"\n❌ Testing failed with error: {e}")
        import traceback
        traceback.print_exc()