#!/usr/bin/env python3
"""
Test script for bow setup API manufacturer learning
Tests that creating and updating bow setups properly learns manufacturers
"""

import json
import sys
import os

# Add arrow_scraper to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def simulate_bow_setup_creation():
    """Simulate bow setup creation with manufacturer learning"""
    print("🧪 Testing bow setup creation with manufacturer learning...")
    
    try:
        from equipment_learning_manager import EquipmentLearningManager
        from user_database import UserDatabase
        
        learning = EquipmentLearningManager()
        user_db = UserDatabase()
        
        # Test data for different bow types
        test_setups = [
            {
                'name': 'Test Compound Setup',
                'bow_type': 'compound',
                'draw_weight': 60,
                'compound_brand': 'Test Compound Manufacturer',
                'compound_model': 'Test Compound Model',
                'ibo_speed': 320,
                'description': 'Test compound bow setup'
            },
            {
                'name': 'Test Recurve Setup',
                'bow_type': 'recurve',
                'draw_weight': 45,
                'riser_brand': 'Test Riser Manufacturer',
                'riser_model': 'Test Riser Model',
                'riser_length': '25',
                'limb_brand': 'Test Limb Manufacturer',
                'limb_model': 'Test Limb Model',
                'limb_length': 'Long',
                'description': 'Test recurve bow setup'
            },
            {
                'name': 'Test Traditional Setup',
                'bow_type': 'traditional',
                'draw_weight': 50,
                'riser_brand': 'Traditional Riser Maker',
                'riser_model': 'Traditional Model',
                'limb_brand': 'Traditional Limb Maker',
                'limb_model': 'Traditional Limbs',
                'description': 'Test traditional bow setup'
            }
        ]
        
        user_id = 1  # Test user ID
        
        for i, setup_data in enumerate(test_setups):
            print(f"\n--- Testing Setup {i + 1}: {setup_data['name']} ---")
            
            # Simulate the creation logic from the API
            print(f"Creating {setup_data['bow_type']} bow setup...")
            
            # Test manufacturer learning for each setup type
            learning_results = []
            
            if setup_data.get('compound_brand') and setup_data.get('bow_type') == 'compound':
                result = learning.learn_equipment_entry(
                    setup_data['compound_brand'],
                    setup_data.get('compound_model', 'Unknown Model'),
                    'compound_bows',
                    user_id
                )
                learning_results.append({
                    'manufacturer': setup_data['compound_brand'],
                    'category': 'compound_bows',
                    'result': result
                })
                
            if setup_data.get('riser_brand') and setup_data.get('bow_type') in ['recurve', 'traditional']:
                category = 'recurve_risers' if setup_data['bow_type'] == 'recurve' else 'traditional_risers'
                result = learning.learn_equipment_entry(
                    setup_data['riser_brand'],
                    setup_data.get('riser_model', 'Unknown Model'),
                    category,
                    user_id
                )
                learning_results.append({
                    'manufacturer': setup_data['riser_brand'],
                    'category': category,
                    'result': result
                })
                
            if setup_data.get('limb_brand') and setup_data.get('bow_type') in ['recurve', 'traditional']:
                category = 'recurve_limbs' if setup_data['bow_type'] == 'recurve' else 'traditional_limbs'
                result = learning.learn_equipment_entry(
                    setup_data['limb_brand'],
                    setup_data.get('limb_model', 'Unknown Model'),
                    category,
                    user_id
                )
                learning_results.append({
                    'manufacturer': setup_data['limb_brand'],
                    'category': category,
                    'result': result
                })
            
            # Print learning results
            print(f"📊 Learning Results for {setup_data['name']}:")
            for lr in learning_results:
                result = lr['result']
                print(f"  - {lr['manufacturer']} ({lr['category']}):")
                print(f"    • New manufacturer: {result['new_manufacturer']}")
                print(f"    • New model: {result['new_model']}")
                print(f"    • Status: {result['manufacturer_status']}")
                print(f"    • Model usage: {result['model_usage_count']}")
        
        print("\n✅ Bow setup creation learning test completed")
        
    except Exception as e:
        print(f"❌ Bow setup creation learning test failed: {e}")

def test_manufacturer_update_learning():
    """Test manufacturer learning when updating bow setups"""
    print("\n🧪 Testing bow setup update with manufacturer learning...")
    
    try:
        from equipment_learning_manager import EquipmentLearningManager
        
        learning = EquipmentLearningManager()
        user_id = 1
        
        # Simulate updating a compound bow manufacturer
        print("Simulating compound bow manufacturer change...")
        
        old_data = {
            'compound_brand': 'Old Compound Brand',
            'compound_model': 'Old Model',
            'bow_type': 'compound'
        }
        
        new_data = {
            'compound_brand': 'New Compound Brand',
            'compound_model': 'New Compound Model',
            'bow_type': 'compound'
        }
        
        # Check if the manufacturer changed
        if old_data['compound_brand'] != new_data['compound_brand']:
            print(f"Manufacturer changed: {old_data['compound_brand']} → {new_data['compound_brand']}")
            
            # Learn from the new manufacturer
            result = learning.learn_equipment_entry(
                new_data['compound_brand'],
                new_data['compound_model'],
                'compound_bows',
                user_id
            )
            
            print(f"📚 Learning result:")
            print(f"  - New manufacturer: {result['new_manufacturer']}")
            print(f"  - New model: {result['new_model']}")
            print(f"  - Status: {result['manufacturer_status']}")
            print(f"  - Model usage: {result['model_usage_count']}")
        
        print("✅ Bow setup update learning test completed")
        
    except Exception as e:
        print(f"❌ Bow setup update learning test failed: {e}")

def test_pending_manufacturers():
    """Test viewing pending manufacturers from bow setup learning"""
    print("\n🧪 Testing pending manufacturers from bow setup learning...")
    
    try:
        from equipment_learning_manager import EquipmentLearningManager
        
        learning = EquipmentLearningManager()
        
        # Get pending manufacturers
        pending = learning.get_pending_manufacturers()
        
        print(f"📋 Found {len(pending)} pending manufacturers:")
        for p in pending:
            categories = json.loads(p['category_context'] or '[]')
            print(f"  - {p['name']}")
            print(f"    • Status: {p['status']}")
            print(f"    • Usage count: {p['usage_count']}")
            print(f"    • Categories: {', '.join(categories)}")
            print(f"    • Created: {p.get('created_at', 'Unknown')}")
        
        print("✅ Pending manufacturers test completed")
        
    except Exception as e:
        print(f"❌ Pending manufacturers test failed: {e}")

if __name__ == "__main__":
    print("🔧 Testing Bow Setup API Manufacturer Learning")
    print("=" * 60)
    
    simulate_bow_setup_creation()
    test_manufacturer_update_learning()
    test_pending_manufacturers()
    
    print("\n🎯 All bow setup learning tests completed!")