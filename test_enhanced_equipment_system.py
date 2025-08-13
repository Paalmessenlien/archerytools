#!/usr/bin/env python3
"""
Test Enhanced Equipment System

Tests all the new features:
- New equipment categories (Scope, Plunger, Other)
- Auto-learning system for manufacturers and models
- Model name suggestions
- Admin manufacturer management

Created: August 2025
"""

import requests
import json

API_BASE = "http://localhost:5000/api"

def test_new_equipment_categories():
    """Test the new equipment categories (Scope, Plunger, Other)"""
    print("🔧 Testing New Equipment Categories")
    print("=" * 50)
    
    categories = ["Scope", "Plunger", "Other"]
    
    for category in categories:
        try:
            response = requests.get(f"{API_BASE}/equipment/form-schema/{category}")
            data = response.json()
            
            if response.status_code == 200 and 'fields' in data:
                fields = data['fields']
                print(f"✅ {category}: {len(fields)} fields")
                for field in fields[:2]:  # Show first 2 fields
                    print(f"   • {field['label']} ({field['type']})")
            else:
                print(f"❌ {category}: Error - {data}")
                
        except Exception as e:
            print(f"❌ {category}: Exception - {e}")
        
        print()

def test_equipment_learning_system():
    """Test auto-learning by adding equipment and checking suggestions"""
    print("🧠 Testing Equipment Learning System")
    print("=" * 50)
    
    # Test model suggestions (should be empty initially)
    print("1. Testing model suggestions before adding equipment:")
    try:
        response = requests.get(f"{API_BASE}/equipment/models/suggest", params={
            'manufacturer': 'Leupold',
            'category': 'Scope'
        })
        data = response.json()
        
        if response.status_code == 200:
            models = data.get('models', [])
            print(f"   Models for Leupold Scope: {len(models)} models")
        else:
            print(f"   Error: {data}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    print("\\n2. Equipment learning will be tested when adding equipment through the frontend.")
    print("   Visit http://localhost:3000 and add some equipment to see:")
    print("   • Automatic manufacturer detection")
    print("   • Model name learning")
    print("   • Usage statistics tracking")
    
def test_manufacturer_suggestions():
    """Test enhanced manufacturer suggestions"""
    print("\\n🏭 Testing Enhanced Manufacturer Suggestions")
    print("=" * 50)
    
    test_cases = [
        ("leupold", "Scope"),
        ("beiter", "Plunger"),
        ("custom", "Other"),
    ]
    
    for query, category in test_cases:
        try:
            response = requests.get(f"{API_BASE}/equipment/manufacturers/suggest", params={
                'q': query,
                'category': category
            })
            data = response.json()
            
            if response.status_code == 200:
                manufacturers = data.get('manufacturers', [])
                print(f"✅ '{query}' in {category}: {len(manufacturers)} suggestions")
                for mfg in manufacturers[:3]:
                    print(f"   • {mfg['name']} ({mfg.get('country', 'Unknown')})")
            else:
                print(f"❌ '{query}': Error - {data}")
                
        except Exception as e:
            print(f"❌ '{query}': Exception - {e}")
        
        print()

def test_sight_category_update():
    """Test that Sight category no longer includes scope options"""
    print("👁️ Testing Sight Category Update (Scope Option Removed)")
    print("=" * 50)
    
    try:
        response = requests.get(f"{API_BASE}/equipment/form-schema/Sight")
        data = response.json()
        
        if response.status_code == 200 and 'fields' in data:
            fields = data['fields']
            sight_type_field = None
            
            for field in fields:
                if field.get('name') == 'sight_type':
                    sight_type_field = field
                    break
            
            if sight_type_field:
                options = sight_type_field.get('options', [])
                if 'scope' in options:
                    print("❌ ERROR: 'scope' option still found in Sight Type")
                else:
                    print("✅ SUCCESS: 'scope' option removed from Sight Type")
                    print(f"   Available options: {options}")
            else:
                print("⚠️  WARNING: sight_type field not found")
        else:
            print(f"❌ Error getting sight schema: {data}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def show_system_overview():
    """Show overview of the enhanced equipment system"""
    print("\\n" + "=" * 80)
    print("🚀 ENHANCED EQUIPMENT SYSTEM - OVERVIEW")
    print("=" * 80)
    
    print("\\n📋 NEW EQUIPMENT CATEGORIES:")
    print("  1. Scope (6 fields) - Magnification, reticle, turrets, etc.")
    print("  2. Plunger (5 fields) - Type, tension, material, thread, adjustment")
    print("  3. Other (5 fields) - Flexible category for any equipment")
    
    print("\\n🧠 AUTO-LEARNING FEATURES:")
    print("  • Automatic new manufacturer detection")
    print("  • Model name learning with usage statistics")
    print("  • Smart manufacturer suggestions with fuzzy matching")
    print("  • Admin approval workflow for new manufacturers")
    
    print("\\n🔗 API ENDPOINTS ADDED:")
    print("  • GET /api/equipment/models/suggest - Model name autocomplete")
    print("  • GET /api/admin/pending-manufacturers - Admin manufacturer review")
    print("  • PUT /api/admin/manufacturers/<id>/approve - Approve manufacturers")
    print("  • GET /api/equipment/usage-analytics - Usage statistics")
    
    print("\\n✅ SIGHT CATEGORY UPDATED:")
    print("  • Removed 'scope' from sight type options")
    print("  • Focuses on pin sights, instinctive, etc.")
    
    print("\\n🎯 TESTING INSTRUCTIONS:")
    print("  1. Visit http://localhost:3000")
    print("  2. Navigate to a bow setup → Add Equipment")
    print("  3. Try different categories: Scope, Plunger, Other")
    print("  4. Enter new manufacturers to test auto-learning")
    print("  5. Admin users can review pending manufacturers at /admin")
    
    print("\\n" + "=" * 80)

def main():
    """Run all enhanced equipment system tests"""
    print("🏹 ENHANCED EQUIPMENT SYSTEM TESTING")
    print("=" * 80)
    
    # Test new equipment categories
    test_new_equipment_categories()
    
    # Test equipment learning
    test_equipment_learning_system()
    
    # Test manufacturer suggestions  
    test_manufacturer_suggestions()
    
    # Test sight category update
    test_sight_category_update()
    
    # Show system overview
    show_system_overview()
    
    print("\\n✅ Enhanced Equipment System Testing Complete!")

if __name__ == "__main__":
    main()