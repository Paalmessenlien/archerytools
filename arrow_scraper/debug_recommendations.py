#!/usr/bin/env python3
"""
Debug the recommendations endpoint
"""

import json
import sys
import traceback
from arrow_tuning_system import ArrowTuningSystem, ArcherProfile
from spine_calculator import BowConfiguration, BowType
from tuning_calculator import TuningGoal, ArrowType

def test_recommendations():
    """Test the recommendations functionality"""
    
    print("🔧 Testing recommendations functionality...")
    
    try:
        # Create test data similar to API request
        test_data = {
            'draw_weight': 45.0,
            'draw_length': 28.0,
            'bow_type': 'traditional',
            'shooting_style': 'target',
            'archer_name': 'Test Archer',
            'experience_level': 'intermediate',
            'primary_goal': 'maximum_accuracy',
            'arrow_type': 'target_outdoor'
        }
        
        print(f"📊 Test parameters: {test_data}")
        
        # Create bow configuration
        print("\n🏹 Creating bow configuration...")
        bow_config = BowConfiguration(
            draw_weight=float(test_data['draw_weight']),
            draw_length=float(test_data['draw_length']),
            bow_type=BowType(test_data['bow_type']),
            cam_type=test_data.get('cam_type', 'medium'),
            arrow_rest_type=test_data.get('arrow_rest_type', 'drop_away')
        )
        print(f"✅ Bow config created: {bow_config}")
        
        # Create archer profile
        print("\n👤 Creating archer profile...")
        archer_profile = ArcherProfile(
            name=test_data.get('archer_name', 'Anonymous'),
            bow_config=bow_config,
            shooting_style=test_data.get('shooting_style', 'target'),
            experience_level=test_data.get('experience_level', 'intermediate')
        )
        print(f"✅ Archer profile created: {archer_profile.name}")
        
        # Create tuning goals
        print("\n🎯 Setting up tuning goals...")
        primary_goal = TuningGoal(test_data.get('primary_goal', 'maximum_accuracy'))
        print(f"✅ Primary goal: {primary_goal}")
        
        # Initialize tuning system
        print("\n🚀 Initializing tuning system...")
        ts = ArrowTuningSystem()
        print("✅ Tuning system initialized")
        
        # Create tuning session
        print("\n🎯 Creating tuning session...")
        session = ts.create_tuning_session(
            archer_profile, 
            tuning_goals=[primary_goal]
        )
        print(f"✅ Session created: {session.session_id}")
        
        # Check recommendations
        print(f"\n📊 Session results:")
        print(f"   Session ID: {session.session_id}")
        print(f"   Recommended arrows count: {len(session.recommended_arrows)}")
        
        if session.recommended_arrows:
            print(f"\n🎯 First 3 recommendations:")
            for i, rec in enumerate(session.recommended_arrows[:3]):
                print(f"   {i+1}. {rec.manufacturer} {rec.model_name} - Score: {rec.match_score}")
        else:
            print("❌ No arrow recommendations found")
            
        return True
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        print(f"Stack trace:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_recommendations()
    sys.exit(0 if success else 1)