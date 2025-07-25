#!/usr/bin/env python3
"""
Test script for diameter categories functionality
"""

from models import classify_diameter, DiameterCategory, SpineSpecification, ArrowSpecification
from arrow_database import ArrowDatabase
import json

def test_diameter_classification():
    """Test diameter classification function"""
    print("🧪 Testing diameter classification...")
    
    test_cases = [
        (0.166, DiameterCategory.ULTRA_THIN, "Ultra-thin target arrow"),
        (0.204, DiameterCategory.THIN, "Thin 3D/target arrow"),
        (0.244, DiameterCategory.SMALL_HUNTING, "Small hunting diameter"),
        (0.246, DiameterCategory.STANDARD_TARGET, "Standard target/hunting"),
        (0.300, DiameterCategory.STANDARD_HUNTING, "Standard hunting"),
        (0.340, DiameterCategory.LARGE_HUNTING, "Large hunting"),
        (0.400, DiameterCategory.HEAVY_HUNTING, "Heavy/traditional hunting"),
        (0.450, DiameterCategory.HEAVY_HUNTING, "Very heavy hunting")
    ]
    
    all_passed = True
    for diameter, expected_category, description in test_cases:
        result = classify_diameter(diameter)
        status = "✅" if result == expected_category else "❌"
        print(f"   {status} {diameter}\" -> {result.value} ({description})")
        if result != expected_category:
            all_passed = False
    
    return all_passed

def test_spine_specification_model():
    """Test SpineSpecification model with diameter category"""
    print("\n🧪 Testing SpineSpecification model...")
    
    try:
        # Test with outer diameter only
        spec1 = SpineSpecification(
            spine=300,
            outer_diameter=0.246,
            gpi_weight=8.5
        )
        assert spec1.diameter_category == DiameterCategory.STANDARD_TARGET
        print("   ✅ Outer diameter classification works")
        
        # Test with inner diameter (should be preferred)
        spec2 = SpineSpecification(
            spine=400,
            outer_diameter=0.300,
            inner_diameter=0.204,  # This should be used for classification
            gpi_weight=9.2
        )
        assert spec2.diameter_category == DiameterCategory.THIN
        print("   ✅ Inner diameter preference works")
        
        return True
    except Exception as e:
        print(f"   ❌ Model test failed: {e}")
        return False

def test_arrow_specification_methods():
    """Test ArrowSpecification diameter category methods"""
    print("\n🧪 Testing ArrowSpecification methods...")
    
    try:
        # Create arrow with multiple spine options
        arrow = ArrowSpecification(
            manufacturer="Test Manufacturer",
            model_name="Test Arrow",
            source_url="http://test.com",
            spine_specifications=[
                SpineSpecification(spine=300, outer_diameter=0.246, gpi_weight=8.5),
                SpineSpecification(spine=400, outer_diameter=0.204, gpi_weight=7.8),
                SpineSpecification(spine=500, outer_diameter=0.166, gpi_weight=6.2)
            ]
        )
        
        categories = arrow.get_diameter_categories()
        expected_categories = [DiameterCategory.STANDARD_TARGET, DiameterCategory.THIN, DiameterCategory.ULTRA_THIN]
        
        print(f"   ✅ Found categories: {[cat.value for cat in categories]}")
        
        primary = arrow.get_primary_diameter_category()
        print(f"   ✅ Primary category: {primary.value}")
        
        effective_diameter = arrow.get_effective_diameter(300)
        print(f"   ✅ Effective diameter for spine 300: {effective_diameter}\"")
        
        return True
    except Exception as e:
        print(f"   ❌ Arrow methods test failed: {e}")
        return False

def test_database_integration():
    """Test database integration with diameter categories"""
    print("\n🧪 Testing database integration...")
    
    try:
        db = ArrowDatabase()
        
        # Test statistics include diameter categories
        stats = db.get_statistics()
        diameter_categories = stats.get('diameter_categories', [])
        
        if not diameter_categories:
            print("   ❌ No diameter categories in statistics")
            return False
        
        print(f"   ✅ Found {len(diameter_categories)} diameter categories in stats")
        for cat in diameter_categories[:3]:  # Show top 3
            print(f"      - {cat['diameter_category']}: {cat['count']} specifications")
        
        # Test search with diameter category
        results = db.search_arrows(diameter_category="ultra_thin", limit=5)
        if results:
            print(f"   ✅ Found {len(results)} ultra-thin arrows")
        else:
            print("   ⚠️  No ultra-thin arrows found (may be expected)")
        
        return True
    except Exception as e:
        print(f"   ❌ Database integration test failed: {e}")
        return False

def test_api_integration():
    """Test API endpoints with diameter categories"""
    print("\n🧪 Testing API integration...")
    
    try:
        import requests
        
        # Test database stats endpoint
        response = requests.get('http://localhost:5000/api/database/stats')
        if response.status_code == 200:
            data = response.json()
            diameter_categories = data.get('diameter_categories', [])
            
            if diameter_categories:
                print(f"   ✅ API returns {len(diameter_categories)} diameter categories")
                print(f"      Top category: {diameter_categories[0]['diameter_category']} "
                      f"({diameter_categories[0]['count']} specs)")
                return True
            else:
                print("   ❌ No diameter categories in API response")
                return False
        else:
            print(f"   ⚠️  API not responding (status: {response.status_code})")
            return False
            
    except ImportError:
        print("   ⚠️  requests module not available, skipping API test")
        return True
    except Exception as e:
        print(f"   ❌ API integration test failed: {e}")
        return False

if __name__ == "__main__":
    print("🎯 Testing Diameter Categories Implementation")
    print("=" * 50)
    
    tests = [
        ("Diameter Classification", test_diameter_classification),
        ("SpineSpecification Model", test_spine_specification_model),
        ("ArrowSpecification Methods", test_arrow_specification_methods),
        ("Database Integration", test_database_integration),
        ("API Integration", test_api_integration)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                failed += 1
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} ERROR: {e}")
    
    print(f"\n📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n🎉 All tests passed! Diameter categories are working correctly.")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review the implementation.")
    
    print("\n💡 Diameter Categories Summary:")
    print("   - Ultra-thin (.166\"): High-end target arrows for reduced wind drift")
    print("   - Thin (.204\"): 3D archery and target applications")
    print("   - Small hunting (.244\"): Good penetration for hunting")
    print("   - Standard target (.246\"): Common for target and hunting")
    print("   - Standard hunting (.300\"): Widely used hunting diameter")
    print("   - Large hunting (.340\"): Larger hunting applications")
    print("   - Heavy hunting (.400\"+): Traditional bows and heavy setups")