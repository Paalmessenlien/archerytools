#!/usr/bin/env python3
"""
Test script to verify arrow scraper setup
"""

import sys
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        # Test crawl4ai import
        sys.path.append(str(Path(__file__).parent.parent))
        from crawl4ai import AsyncWebCrawler
        print("✓ crawl4ai import successful")
    except ImportError as e:
        print(f"✗ crawl4ai import failed: {e}")
        return False
    
    try:
        # Test our modules
        from models import ArrowSpecification, ScrapingResult
        print("✓ models import successful")
    except ImportError as e:
        print(f"✗ models import failed: {e}")
        return False
    
    try:
        from config.settings import MANUFACTURERS, ARROW_SCHEMA
        print("✓ config import successful")
    except ImportError as e:
        print(f"✗ config import failed: {e}")
        return False
    
    try:
        from scrapers.base_scraper import BaseScraper
        print("✓ base_scraper import successful")
    except ImportError as e:
        print(f"✗ base_scraper import failed: {e}")
        return False
    
    return True

def test_data_model():
    """Test arrow data model validation"""
    print("\nTesting data models...")
    
    try:
        from models import ArrowSpecification, SpineSpecification
        
        # Test valid arrow specification with spine specifications
        spine_specs = [
            SpineSpecification(spine=300, outer_diameter=0.244, gpi_weight=8.2),
            SpineSpecification(spine=340, outer_diameter=0.246, gpi_weight=8.5),
            SpineSpecification(spine=400, outer_diameter=0.248, gpi_weight=8.8)
        ]
        
        arrow = ArrowSpecification(
            manufacturer="Test Manufacturer",
            model_name="Test Arrow",
            spine_specifications=spine_specs,
            source_url="https://example.com"
        )
        print("✓ ArrowSpecification creation successful")
        
        # Test validation
        try:
            invalid_arrow = ArrowSpecification(
                manufacturer="Test",
                model_name="Test",
                spine_specifications=[],  # Invalid: empty list
                source_url="https://example.com"
            )
            print("✗ Validation failed - should have caught empty spine_specifications")
            return False
        except ValueError:
            print("✓ Validation working - caught invalid data")
        
        return True
        
    except Exception as e:
        print(f"✗ Data model test failed: {e}")
        return False

def test_configuration():
    """Test configuration settings"""
    print("\nTesting configuration...")
    
    try:
        from config.settings import MANUFACTURERS, DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR
        
        print(f"✓ Found {len(MANUFACTURERS)} manufacturers configured")
        print(f"✓ Data directories: {DATA_DIR}")
        
        # Check if directories exist
        if DATA_DIR.exists():
            print("✓ Data directory exists")
        else:
            print("! Data directory will be created when needed")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Arrow Scraper Setup Test")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_data_model,
        test_configuration
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! Setup is ready.")
        print("\nNext steps:")
        print("1. Create a .env file with your DEEPSEEK_API_KEY")
        print("2. Run: python main.py easton")
    else:
        print("❌ Some tests failed. Please check the setup.")

if __name__ == "__main__":
    main()