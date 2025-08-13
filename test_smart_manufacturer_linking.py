#!/usr/bin/env python3
"""
Test Smart Manufacturer Linking System

Tests the smart manufacturer detection and linking functionality
in the equipment addition API.
"""

import requests
import json

API_BASE = "http://localhost:5000/api"

def test_manufacturer_suggestions():
    """Test the smart manufacturer suggestions endpoint"""
    print("🔍 Testing Smart Manufacturer Suggestions")
    print("=" * 50)
    
    test_cases = [
        ("easton", "Sight"),
        ("goldtip", "String"),  
        ("bstinger", "Stabilizer"),
        ("blackgold", "Sight"),
        ("qad", "Arrow Rest"),
    ]
    
    for query, category in test_cases:
        url = f"{API_BASE}/equipment/manufacturers/suggest"
        params = {"q": query, "category": category}
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if response.status_code == 200:
                manufacturers = data.get('manufacturers', [])
                print(f"✅ Query: '{query}' (Category: {category})")
                print(f"   Suggestions: {[m['name'] for m in manufacturers[:3]]}")
            else:
                print(f"❌ Query: '{query}' - Error: {data}")
                
        except Exception as e:
            print(f"❌ Query: '{query}' - Exception: {e}")
        
        print()

def test_manufacturer_linking_in_logs():
    """Check API logs for manufacturer linking messages"""
    print("📝 Recent Manufacturer Linking Activity")
    print("=" * 50)
    
    try:
        # Read the last 20 lines of API logs
        with open("/home/paal/archerytools/logs/api.log", "r") as f:
            lines = f.readlines()
            recent_lines = lines[-30:]  # Get last 30 lines
            
        # Look for linking messages
        linking_messages = []
        for line in recent_lines:
            if "Smart manufacturer linking:" in line or "No manufacturer match found" in line:
                linking_messages.append(line.strip())
        
        if linking_messages:
            print("Recent linking activity:")
            for msg in linking_messages:
                print(f"  {msg}")
        else:
            print("No recent manufacturer linking activity found in logs.")
            
    except Exception as e:
        print(f"❌ Could not read logs: {e}")

def main():
    """Run all tests"""
    print("🏹 Smart Manufacturer Linking System Test")
    print("=" * 60)
    print()
    
    # Test suggestions
    test_manufacturer_suggestions()
    
    # Check logs for linking activity
    test_manufacturer_linking_in_logs()
    
    print("\n✅ Testing completed!")
    print("\nTo test manufacturer linking in equipment addition:")
    print("1. Go to http://localhost:3000")
    print("2. Navigate to a bow setup")
    print("3. Add custom equipment with variations like:")
    print("   - 'easton' → Should link to 'Easton Archery'")
    print("   - 'goldtip' → Should link to 'Gold Tip'")
    print("   - 'bstinger' → Should link to 'B-Stinger'")
    print("4. Check logs for linking messages")

if __name__ == "__main__":
    main()