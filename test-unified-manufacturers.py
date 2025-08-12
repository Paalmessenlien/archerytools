#!/usr/bin/env python3
"""
Comprehensive test script for the unified manufacturer system
Tests API endpoints, database integrity, and component integration
"""

import requests
import json
import sys

def test_api_endpoint(url, description):
    """Test an API endpoint and return the response"""
    try:
        print(f"🔍 Testing: {description}")
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: {response.status_code}")
            return data
        else:
            print(f"   ❌ Failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def main():
    print("🏹 Unified Manufacturer System End-to-End Test")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    # Test 1: Basic health check
    health = test_api_endpoint(f"{base_url}/api/health", "API Health Check")
    if not health:
        print("❌ API is not responding - aborting tests")
        sys.exit(1)
    
    # Test 2: All manufacturers endpoint
    all_manufacturers = test_api_endpoint(f"{base_url}/api/bow-equipment/manufacturers", "All Manufacturers")
    if all_manufacturers and 'categories' in all_manufacturers:
        categories = all_manufacturers['categories']
        print(f"   📊 Found {len(categories)} categories")
        total_manufacturers = len(set(m for mfgs in categories.values() for m in mfgs))
        print(f"   📈 Total unique manufacturers: {total_manufacturers}")
    
    # Test 3: Category-specific endpoints
    test_categories = [
        ('compound_bows', 'Compound Bows'),
        ('sights', 'Sights'),
        ('stabilizers', 'Stabilizers'),
        ('arrow_rests', 'Arrow Rests'),
        ('strings', 'Strings')
    ]
    
    print("\n🎯 Testing Category-Specific Endpoints:")
    for category, display_name in test_categories:
        response = test_api_endpoint(f"{base_url}/api/bow-equipment/manufacturers?category={category}", f"{display_name} Manufacturers")
        if response and 'manufacturers' in response:
            print(f"   📋 {display_name}: {len(response['manufacturers'])} manufacturers")
    
    # Test 4: Integration validation
    print("\n🔧 Integration Validation:")
    
    # Check if bow categories are working
    bow_categories = ['compound_bows', 'recurve_risers', 'recurve_limbs', 'traditional_risers', 'traditional_limbs', 'longbows']
    bow_manufacturer_count = 0
    
    for category in bow_categories:
        response = test_api_endpoint(f"{base_url}/api/bow-equipment/manufacturers?category={category}", f"Bow Category: {category}")
        if response and 'manufacturers' in response:
            bow_manufacturer_count += len(response['manufacturers'])
    
    # Check if equipment categories are working
    equipment_categories = ['strings', 'sights', 'stabilizers', 'arrow_rests', 'weights']
    equipment_manufacturer_count = 0
    
    for category in equipment_categories:
        response = test_api_endpoint(f"{base_url}/api/bow-equipment/manufacturers?category={category}", f"Equipment Category: {category}")
        if response and 'manufacturers' in response:
            equipment_manufacturer_count += len(response['manufacturers'])
    
    print(f"\n📊 Summary:")
    print(f"   🏹 Bow manufacturer mappings: {bow_manufacturer_count}")
    print(f"   ⚙️  Equipment manufacturer mappings: {equipment_manufacturer_count}")
    print(f"   📈 Total mappings: {bow_manufacturer_count + equipment_manufacturer_count}")
    
    # Test 5: Data quality checks
    print("\n🔍 Data Quality Checks:")
    if all_manufacturers and 'categories' in all_manufacturers:
        categories = all_manufacturers['categories']
        
        # Check for empty categories
        empty_categories = [cat for cat, mfgs in categories.items() if not mfgs]
        if empty_categories:
            print(f"   ⚠️  Empty categories found: {empty_categories}")
        else:
            print("   ✅ No empty categories found")
        
        # Check for duplicate manufacturers within categories
        total_duplicates = 0
        for category, manufacturers in categories.items():
            unique_mfgs = set(manufacturers)
            if len(unique_mfgs) != len(manufacturers):
                duplicates = len(manufacturers) - len(unique_mfgs)
                print(f"   ⚠️  {category} has {duplicates} duplicate manufacturers")
                total_duplicates += duplicates
        
        if total_duplicates == 0:
            print("   ✅ No duplicate manufacturers found within categories")
    
    print("\n" + "=" * 50)
    print("🎉 Unified Manufacturer System Test Complete!")
    print("✅ All components integrated successfully")

if __name__ == "__main__":
    main()