#!/usr/bin/env python3
"""
Test the manufacturer learning system
"""

import sys
import os
sys.path.append('/home/paal/archerytools/arrow_scraper')

from equipment_learning_manager import EquipmentLearningManager

def test_manufacturer_learning():
    print("🧠 Testing Manufacturer Learning System")
    print("=" * 45)
    
    try:
        learning = EquipmentLearningManager()
        
        # Test adding a new manufacturer
        print("📝 Testing learn_equipment_entry with 'Zniper'...")
        result = learning.learn_equipment_entry(
            manufacturer_name="Zniper",
            model_name="Test Sight Pro",
            category_name="Sight",
            user_id=1  # Assuming user ID 1 exists
        )
        
        print(f"📊 Learning result:")
        print(f"   new_manufacturer: {result['new_manufacturer']}")
        print(f"   new_model: {result['new_model']}")
        print(f"   manufacturer_status: {result['manufacturer_status']}")
        print(f"   model_usage_count: {result['model_usage_count']}")
        
        # Check pending manufacturers
        print("\n📋 Checking pending manufacturers...")
        pending = learning.get_pending_manufacturers('pending', 50)
        print(f"Found {len(pending)} pending manufacturers:")
        
        for p in pending:
            print(f"   - ID: {p.get('id')}, Name: '{p.get('name')}', Status: {p.get('status')}")
            print(f"     Created: {p.get('created_at')}, Usage: {p.get('usage_count')}")
            print(f"     Categories: {p.get('category_context')}")
        
        # Test another manufacturer to see usage counting
        print(f"\n📝 Testing second equipment with same manufacturer...")
        result2 = learning.learn_equipment_entry(
            manufacturer_name="Zniper", 
            model_name="Another Model",
            category_name="Stabilizer", 
            user_id=1
        )
        
        print(f"📊 Second learning result:")
        print(f"   new_manufacturer: {result2['new_manufacturer']}")
        print(f"   manufacturer_status: {result2['manufacturer_status']}")
        
        # Check updated pending manufacturers
        print("\n📋 Checking updated pending manufacturers...")
        pending2 = learning.get_pending_manufacturers('pending', 50)
        for p in pending2:
            print(f"   - ID: {p.get('id')}, Name: '{p.get('name')}', Usage: {p.get('usage_count')}")
            print(f"     Categories: {p.get('category_context')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_manufacturer_learning()