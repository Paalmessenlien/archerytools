#!/usr/bin/env python3
"""
Demo script showing the fixed extraction handling spine-specific data
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from scrapers.base_scraper import BaseScraper
from models import ArrowSpecification, SpineSpecification

def demo_extraction_fix():
    """Demo the extraction fix for spine-specific data"""
    print("Arrow Scraper Fix Demo")
    print("=" * 50)
    print("Demonstrating the fix for spine-specific arrow specifications\n")
    
    # Create scraper instance  
    scraper = BaseScraper("Easton", "demo-api-key")
    
    print("PROBLEM: Old extraction would save only first GPI/diameter value")
    print("SOLUTION: New extraction creates separate specifications per spine\n")
    
    # Show the updated extraction prompt
    print("Updated Extraction Prompt:")
    print("-" * 30)
    prompt = scraper.get_extraction_prompt()
    key_lines = [line.strip() for line in prompt.split('\n') 
                 if 'CRITICAL' in line or 'spine_specifications' in line or 'different values' in line]
    for line in key_lines:
        if line:
            print(f"• {line}")
    
    print("\nUpdated JSON Schema:")
    print("-" * 20)
    schema = scraper._get_extraction_schema()
    spine_spec_props = schema['properties']['arrows']['items']['properties']['spine_specifications']['items']['properties']
    print("spine_specifications array contains objects with:")
    for prop, details in spine_spec_props.items():
        required = prop in schema['properties']['arrows']['items']['properties']['spine_specifications']['items']['required']
        req_text = " (required)" if required else " (optional)"
        print(f"  • {prop}: {details['type']}{req_text}")
    
    print("\nSample Data Processing:")
    print("-" * 25)
    
    # Sample data that would come from corrected DeepSeek extraction
    sample_data = {
        "arrows": [
            {
                "model_name": "Carbon Legacy",
                "spine_specifications": [
                    {"spine": 340, "outer_diameter": 0.289, "gpi_weight": 7.1},
                    {"spine": 400, "outer_diameter": 0.291, "gpi_weight": 7.5},
                    {"spine": 500, "outer_diameter": 0.296, "gpi_weight": 8.3}
                ],
                "material": "Carbon Fiber",
                "arrow_type": "hunting"
            }
        ]
    }
    
    # Process the data
    arrows = scraper._process_extracted_data(sample_data, "https://example.com")
    arrow = arrows[0]
    
    print(f"Model: {arrow.model_name}")
    print(f"Available spines: {arrow.get_spine_options()}")
    print("Spine-specific specifications:")
    
    for spec in arrow.spine_specifications:
        print(f"  Spine {spec.spine}: {spec.outer_diameter:.3f}\" diameter, {spec.gpi_weight:.1f} GPI")
    
    print(f"\nDiameter range: {arrow.get_diameter_range()[0]:.3f}\" - {arrow.get_diameter_range()[1]:.3f}\"")
    print(f"GPI range: {arrow.get_gpi_range()[0]:.1f} - {arrow.get_gpi_range()[1]:.1f}")
    
    print("\n✅ FIXED: Each spine now has its own specifications!")
    print("✅ FIXED: No more data loss when arrows have varying specs per spine!")
    print("✅ FIXED: Proper validation and data integrity!")

def show_before_after():
    """Show before and after data structures"""
    print("\nBefore vs After Data Structure:")
    print("=" * 40)
    
    print("BEFORE (Lost Data):")
    print("-" * 20)
    old_structure = {
        "model_name": "Carbon Legacy",
        "spine_options": [340, 400, 500, 600, 700],
        "diameter": 0.289,  # Only first value saved!
        "gpi_weight": 7.1,  # Only first value saved!
    }
    print(json.dumps(old_structure, indent=2))
    print("❌ Lost: Different diameters for spines 400-700")
    print("❌ Lost: Different GPI weights for spines 400-700")
    
    print("\nAFTER (Complete Data):")
    print("-" * 20)
    new_structure = {
        "model_name": "Carbon Legacy",
        "spine_specifications": [
            {"spine": 340, "outer_diameter": 0.289, "gpi_weight": 7.1},
            {"spine": 400, "outer_diameter": 0.291, "gpi_weight": 7.5},
            {"spine": 500, "outer_diameter": 0.296, "gpi_weight": 8.3},
            {"spine": 600, "outer_diameter": 0.300, "gpi_weight": 8.8},
            {"spine": 700, "outer_diameter": 0.305, "gpi_weight": 9.2}
        ]
    }
    print(json.dumps(new_structure, indent=2))
    print("✅ Preserved: All spine-specific diameters")
    print("✅ Preserved: All spine-specific GPI weights")
    print("✅ Added: Support for spine-specific length options")
    print("✅ Added: Data validation and integrity checks")

def main():
    """Run the demo"""
    demo_extraction_fix()
    show_before_after()
    
    print("\nNext Steps:")
    print("=" * 15)
    print("1. Test with real scraping: python main.py easton")
    print("2. Verify extracted data in data/processed/")
    print("3. Check that each arrow has proper spine_specifications")
    print("4. Validate that different spine values have different specs")
    
    print("\nThe scraper is now ready to extract complete arrow data!")

if __name__ == "__main__":
    main()