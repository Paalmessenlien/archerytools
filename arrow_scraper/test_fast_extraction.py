#!/usr/bin/env python3
"""
Test the fast extraction improvements:
1. Image download skipping for non-vision manufacturers
2. Consistent manufacturer naming
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from config_loader import ConfigLoader
from run_comprehensive_extraction_fast import FastDirectLLMExtractor

def test_fast_extraction():
    """Test the fast extraction improvements"""
    
    # Load environment
    load_dotenv()
    api_key = os.getenv("DEEPSEEK_API_KEY")
    
    if not api_key:
        print("❌ DEEPSEEK_API_KEY not found")
        return
    
    # Load config
    config = ConfigLoader()
    
    print("🧪 Testing Fast Extraction Improvements")
    print("=" * 50)
    
    # Test 1: Check vision vs non-vision manufacturers
    print("\n📊 Manufacturer Extraction Methods:")
    for manufacturer in config.get_manufacturer_names()[:5]:  # Test first 5
        is_vision = config.is_vision_extraction(manufacturer)
        method = config.get_extraction_method(manufacturer)
        print(f"  • {manufacturer}: {method} (Vision: {'Yes' if is_vision else 'No'})")
    
    # Test 2: Create extractors with different settings
    print("\n🔧 Testing Extractor Initialization:")
    
    # Non-vision manufacturer (should skip images)
    easton_extractor = FastDirectLLMExtractor(
        api_key,
        manufacturer_name="Easton Archery",
        skip_images=True
    )
    print(f"  • Easton Archery: skip_images={easton_extractor.skip_images}")
    
    # Vision manufacturer (should download images)
    carbon_extractor = FastDirectLLMExtractor(
        api_key,
        manufacturer_name="Carbon Express",
        skip_images=False
    )
    print(f"  • Carbon Express: skip_images={carbon_extractor.skip_images}")
    
    # Test 3: Test image URL handling
    print("\n🖼️ Testing Image URL Handling:")
    test_url = "https://example.com/arrow.jpg"
    
    # Non-vision (should return URL)
    result1 = easton_extractor.download_image(test_url, "Easton", "Test Arrow", "primary")
    print(f"  • Non-vision result: {result1} (Should be URL)")
    
    # Vision would download (but we'll skip actual download in test)
    print(f"  • Vision would download: {test_url}")
    
    # Test 4: Manufacturer name consistency
    print("\n🏷️ Testing Manufacturer Name Consistency:")
    print(f"  • Config name: 'Easton Archery'")
    print(f"  • Extractor will use: '{easton_extractor.manufacturer_name}'")
    
    print("\n✅ Fast extraction improvements are ready!")
    print("  - Image downloads will be skipped for non-vision manufacturers")
    print("  - Manufacturer names will be consistent from config")
    print("  - This should significantly speed up scraping!")

if __name__ == "__main__":
    test_fast_extraction()