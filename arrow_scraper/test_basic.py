#!/usr/bin/env python3
"""
Basic test script for arrow scraper core functionality
"""

def test_models():
    """Test arrow data models"""
    print("Testing data models...")
    
    try:
        from models import ArrowSpecification, ManufacturerData, ScrapingResult
        
        # Test valid arrow specification
        arrow = ArrowSpecification(
            manufacturer="Test Manufacturer",
            model_name="Test Arrow X1",
            spine_options=[300, 340, 400, 500],
            diameter=0.246,
            gpi_weight=8.5,
            source_url="https://example.com/test-arrow",
            arrow_type="hunting"
        )
        print("✓ ArrowSpecification created successfully")
        print(f"  Model: {arrow.model_name}")
        print(f"  Spines: {arrow.spine_options}")
        print(f"  Diameter: {arrow.diameter}\"")
        print(f"  GPI: {arrow.gpi_weight}")
        
        # Test manufacturer data
        manufacturer_data = ManufacturerData(
            manufacturer="Test Manufacturer",
            arrows=[arrow]
        )
        print("✓ ManufacturerData created successfully")
        print(f"  Total arrows: {manufacturer_data.total_arrows}")
        
        return True
        
    except Exception as e:
        print(f"✗ Model test failed: {e}")
        return False

def test_configuration():
    """Test configuration"""
    print("\nTesting configuration...")
    
    try:
        from config.settings import MANUFACTURERS, ARROW_SCHEMA, DATA_DIR
        
        print(f"✓ Found {len(MANUFACTURERS)} manufacturers:")
        for key, config in MANUFACTURERS.items():
            print(f"  - {key}: {config['name']}")
        
        print(f"✓ Arrow schema has {len(ARROW_SCHEMA['required_fields'])} required fields")
        print(f"✓ Data directory: {DATA_DIR}")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def test_json_export():
    """Test JSON export functionality"""
    print("\nTesting JSON export...")
    
    try:
        import json
        from models import ArrowSpecification, ManufacturerData
        from pathlib import Path
        
        # Create test data
        arrows = [
            ArrowSpecification(
                manufacturer="Test Co",
                model_name="Arrow A",
                spine_options=[300, 400],
                diameter=0.246,
                gpi_weight=8.0,
                source_url="https://example.com/arrow-a",
                arrow_type="target"
            ),
            ArrowSpecification(
                manufacturer="Test Co", 
                model_name="Arrow B",
                spine_options=[400, 500],
                diameter=0.204,
                gpi_weight=6.5,
                source_url="https://example.com/arrow-b",
                arrow_type="hunting"
            )
        ]
        
        manufacturer_data = ManufacturerData(
            manufacturer="Test Co",
            arrows=arrows
        )
        
        # Test JSON serialization
        json_data = manufacturer_data.model_dump()
        json_str = json.dumps(json_data, indent=2, default=str)
        
        print("✓ JSON serialization successful")
        print(f"  Export preview (first 200 chars):")
        print(f"  {json_str[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"✗ JSON export test failed: {e}")
        return False

def main():
    """Run basic tests"""
    print("Arrow Scraper Basic Functionality Test")
    print("=" * 45)
    
    tests = [
        test_models,
        test_configuration, 
        test_json_export
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print(f"\nResults: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 Core functionality working!")
        print("\nPhase 1.1 (Environment Setup) Status:")
        print("✓ Project structure created")
        print("✓ Data models implemented")
        print("✓ Configuration system working")
        print("✓ JSON export/import ready")
        print("- Crawl4AI integration pending (full requirements.txt)")
        print("- DeepSeek API integration pending (.env setup)")
    else:
        print("❌ Some core tests failed")

if __name__ == "__main__":
    main()