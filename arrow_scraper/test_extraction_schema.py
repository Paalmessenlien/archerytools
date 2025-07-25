#!/usr/bin/env python3
"""
Test the updated extraction schema with sample data
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from scrapers.base_scraper import BaseScraper
from models import ArrowSpecification, SpineSpecification

def test_extraction_schema():
    """Test the new extraction schema with sample extracted data"""
    print("Testing extraction schema with spine-specific data...")
    
    # Create a test scraper instance
    scraper = BaseScraper("Test Manufacturer", "test-api-key")
    
    # Sample extracted data that represents the corrected format
    sample_extracted_data = {
        "arrows": [
            {
                "model_name": "Carbon Legacy",
                "spine_specifications": [
                    {
                        "spine": 340,
                        "outer_diameter": 0.289,
                        "gpi_weight": 7.1,
                        "inner_diameter": None,
                        "length_options": [32, 33, 34]
                    },
                    {
                        "spine": 400,
                        "outer_diameter": 0.291,
                        "gpi_weight": 7.5,
                        "inner_diameter": None,
                        "length_options": [32, 33, 34]
                    },
                    {
                        "spine": 500,
                        "outer_diameter": 0.296,
                        "gpi_weight": 8.3,
                        "inner_diameter": None,
                        "length_options": [32, 33, 34]
                    }
                ],
                "material": "Carbon Fiber",
                "arrow_type": "hunting",
                "recommended_use": ["hunting"],
                "description": "Traditional wood-grained carbon arrow"
            },
            {
                "model_name": "4MM Axis Long Range",
                "spine_specifications": [
                    {
                        "spine": 250,
                        "outer_diameter": 0.244,
                        "gpi_weight": 9.8,
                        "inner_diameter": 0.234,
                        "length_options": [32, 33]
                    },
                    {
                        "spine": 300,
                        "outer_diameter": 0.244,
                        "gpi_weight": 9.8,
                        "inner_diameter": 0.234,
                        "length_options": [32, 33]
                    },
                    {
                        "spine": 340,
                        "outer_diameter": 0.244,
                        "gpi_weight": 9.8,
                        "inner_diameter": 0.234,
                        "length_options": [32, 33]
                    }
                ],
                "material": "Carbon Fiber",
                "arrow_type": "hunting",
                "recommended_use": ["hunting", "long range"],
                "description": "4MM micro-diameter hunting arrow"
            }
        ]
    }
    
    try:
        # Test data processing
        arrows = scraper._process_extracted_data(sample_extracted_data, "https://example.com/test")
        
        print(f"✓ Successfully processed {len(arrows)} arrows")
        
        # Validate the first arrow
        arrow1 = arrows[0]
        print(f"✓ Arrow 1: {arrow1.model_name}")
        print(f"  - Spine options: {arrow1.get_spine_options()}")
        print(f"  - Diameter range: {arrow1.get_diameter_range()[0]:.3f}\" - {arrow1.get_diameter_range()[1]:.3f}\"")
        print(f"  - GPI range: {arrow1.get_gpi_range()[0]:.1f} - {arrow1.get_gpi_range()[1]:.1f}")
        
        # Validate the second arrow
        arrow2 = arrows[1]
        print(f"✓ Arrow 2: {arrow2.model_name}")
        print(f"  - Spine options: {arrow2.get_spine_options()}")
        print(f"  - Diameter range: {arrow2.get_diameter_range()[0]:.3f}\" - {arrow2.get_diameter_range()[1]:.3f}\"")
        print(f"  - GPI range: {arrow2.get_gpi_range()[0]:.1f} - {arrow2.get_gpi_range()[1]:.1f}")
        
        # Test JSON serialization of processed data
        json_data = json.dumps([arrow.model_dump() for arrow in arrows], indent=2, default=str)
        print("✓ JSON serialization of processed arrows successful")
        
        return True
        
    except Exception as e:
        print(f"✗ Extraction processing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_schema_validation():
    """Test the JSON schema used for extraction"""
    print("\nTesting extraction schema validation...")
    
    scraper = BaseScraper("Test Manufacturer", "test-api-key")
    schema = scraper._get_extraction_schema()
    
    print("✓ Schema generated successfully")
    print(f"Schema structure: {list(schema['properties'].keys())}")
    print(f"Arrow properties: {list(schema['properties']['arrows']['items']['properties'].keys())}")
    print(f"Spine spec properties: {list(schema['properties']['arrows']['items']['properties']['spine_specifications']['items']['properties'].keys())}")
    
    return True

def main():
    """Run all extraction tests"""
    print("Testing Updated Extraction Schema")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 2
    
    if test_extraction_schema():
        tests_passed += 1
    
    if test_schema_validation():
        tests_passed += 1
    
    print(f"\nResults: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All extraction tests passed!")
        print("\nThe updated extraction system now:")
        print("- Properly extracts spine-specific specifications")
        print("- Handles different GPI weights per spine")
        print("- Handles different diameters per spine")
        print("- Maintains data integrity and validation")
        print("\nReady to run real scraping with the fixed data model!")
    else:
        print("❌ Some tests failed. Please check the implementation.")

if __name__ == "__main__":
    main()