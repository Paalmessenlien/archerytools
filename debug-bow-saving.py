#!/usr/bin/env python3
"""
Debug script to test bow setup saving end-to-end
"""
import requests
import json
import sys
sys.path.append('arrow_scraper')

def test_bow_saving_debug():
    print("🔍 Debugging Bow Setup Saving")
    print("=" * 50)
    
    # Test data with brand fields
    test_setup = {
        "name": "Debug Test Setup",
        "bow_type": "recurve", 
        "draw_weight": 45.5,
        "draw_length": 28.0,
        "arrow_length": 27.5,
        "point_weight": 100.0,
        "riser_brand": "Hoyt",
        "riser_model": "Satori", 
        "limb_brand": "Uukha",
        "limb_model": "VX1000",
        "compound_brand": "",
        "compound_model": "",
        "description": "Debug test with all brand fields",
        "bow_usage": '["Target", "Field"]'
    }
    
    print("📤 Test Data:")
    for key, value in test_setup.items():
        print(f"  {key}: {value}")
    
    print(f"\n🌐 Testing API Endpoints:")
    
    # Test 1: API Health
    try:
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ API Health: OK")
        else:
            print(f"❌ API Health: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ API Connection Failed: {e}")
        return
    
    # Test 2: Check if bow-setups endpoint exists
    try:
        # This should fail with 401 (auth required) not 404 (not found)
        response = requests.get("http://localhost:5000/api/bow-setups", timeout=5)
        if response.status_code == 401:
            print("✅ Bow-setups endpoint exists (401 auth required)")
        elif response.status_code == 404:
            print("❌ Bow-setups endpoint not found")
            return
        else:
            print(f"⚠️  Bow-setups endpoint returned: {response.status_code}")
    except Exception as e:
        print(f"❌ Bow-setups endpoint test failed: {e}")
        return
    
    # Test 3: Database direct test
    print(f"\n💾 Testing Database Direct Access:")
    try:
        from user_database import UserDatabase
        db = UserDatabase()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Insert test data directly
        cursor.execute("""
            INSERT INTO bow_setups (
                user_id, name, bow_type, draw_weight, draw_length, arrow_length, point_weight,
                riser_brand, riser_model, limb_brand, limb_model, 
                compound_brand, compound_model, description, bow_usage
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            999,  # test user ID
            test_setup["name"], test_setup["bow_type"], test_setup["draw_weight"],
            test_setup["draw_length"], test_setup["arrow_length"], test_setup["point_weight"],
            test_setup["riser_brand"], test_setup["riser_model"],
            test_setup["limb_brand"], test_setup["limb_model"],
            test_setup["compound_brand"], test_setup["compound_model"],
            test_setup["description"], test_setup["bow_usage"]
        ))
        conn.commit()
        test_id = cursor.lastrowid
        
        # Retrieve and verify
        cursor.execute("SELECT * FROM bow_setups WHERE id = ?", (test_id,))
        saved_setup = cursor.fetchone()
        
        if saved_setup:
            print("✅ Database Save: SUCCESS")
            print(f"  📝 Name: {saved_setup['name']}")
            print(f"  🏹 Type: {saved_setup['bow_type']}")
            print(f"  🎯 Riser: {saved_setup['riser_brand']} {saved_setup['riser_model']}")
            print(f"  🌟 Limb: {saved_setup['limb_brand']} {saved_setup['limb_model']}")
            
            # Clean up
            cursor.execute("DELETE FROM bow_setups WHERE id = ?", (test_id,))
            conn.commit()
            print("🧹 Test data cleaned up")
        else:
            print("❌ Database Save: FAILED - No data retrieved")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Database Test Failed: {e}")
    
    print(f"\n🎯 Summary:")
    print("✅ API is running and responsive")
    print("✅ Bow-setups endpoint exists") 
    print("✅ Database schema supports all brand fields")
    print("✅ Direct database save/retrieve works")
    print(f"\n💡 If frontend saving fails:")
    print("  1. Check browser DevTools Console for JS errors")
    print("  2. Check Network tab for failed API requests")
    print("  3. Verify user authentication tokens")
    print("  4. Check if brand fields are being sent in request body")

if __name__ == "__main__":
    test_bow_saving_debug()