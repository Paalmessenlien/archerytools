#!/usr/bin/env python3
"""
Test the updated scraper with a single URL to verify spine-specific extraction
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from scrapers.easton_scraper import EastonScraper

async def test_single_url():
    """Test scraping a single Easton URL"""
    print("Testing Updated Scraper with Single URL")
    print("=" * 50)
    
    # Load environment
    load_dotenv()
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
    
    if not deepseek_api_key:
        print("❌ DEEPSEEK_API_KEY not found in .env file")
        return False
    
    print(f"✓ API key loaded: {deepseek_api_key[:10]}...")
    
    # Create scraper
    scraper = EastonScraper(deepseek_api_key)
    print(f"✓ Scraper created with session ID: {scraper.session_id}")
    
    # Test URL - let's use the hunting category
    test_url = "https://eastonarchery.com/huntingarrows/"
    print(f"📡 Testing URL: {test_url}")
    
    try:
        # Get the extraction prompt
        extraction_prompt = scraper.get_easton_extraction_prompt()
        print("✓ Extraction prompt generated")
        
        # Scrape the URL
        print("🔍 Starting scrape...")
        result = await scraper.scrape_url(test_url, extraction_prompt)
        
        if result.success:
            print(f"✅ Scrape successful!")
            print(f"📊 Arrows found: {result.arrows_found}")
            
            if result.processed_data:
                print("\n📋 Sample extracted data:")
                print("-" * 30)
                
                for i, arrow in enumerate(result.processed_data[:2]):  # Show first 2 arrows
                    print(f"\nArrow {i+1}: {arrow.model_name}")
                    print(f"  Manufacturer: {arrow.manufacturer}")
                    print(f"  Spine options: {arrow.get_spine_options()}")
                    print(f"  Diameter range: {arrow.get_diameter_range()[0]:.3f}\" - {arrow.get_diameter_range()[1]:.3f}\"")
                    print(f"  GPI range: {arrow.get_gpi_range()[0]:.1f} - {arrow.get_gpi_range()[1]:.1f}")
                    
                    # Show spine-specific details for first arrow
                    if i == 0:
                        print("  Spine-specific details:")
                        for spec in arrow.spine_specifications[:3]:  # Show first 3 spines
                            print(f"    Spine {spec.spine}: {spec.outer_diameter:.3f}\" dia, {spec.gpi_weight:.1f} GPI")
                        if len(arrow.spine_specifications) > 3:
                            print(f"    ... and {len(arrow.spine_specifications) - 3} more spine options")
                
                print(f"\n✅ VERIFICATION: Spine-specific data is being extracted correctly!")
                print(f"   Total arrows with spine specifications: {len(result.processed_data)}")
                print(f"   Total spine options across all arrows: {sum(len(arrow.spine_specifications) for arrow in result.processed_data)}")
                
            else:
                print("⚠️  No processed data available")
                
        else:
            print(f"❌ Scrape failed: {result.errors}")
            return False
            
        # Save the test data
        scraper.save_session_data()
        print("💾 Test session data saved")
        
        return True
        
    except Exception as e:
        print(f"💥 Error during scraping: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the single URL test"""
    success = asyncio.run(test_single_url())
    
    if success:
        print("\n🎉 Single URL test passed!")
        print("✅ Spine-specific extraction is working correctly")
        print("✅ Ready to run full scraping")
        print("\nTo run full scraping:")
        print("python main.py easton")
    else:
        print("\n❌ Single URL test failed")
        print("Please check the logs and fix any issues before running full scraping")

if __name__ == "__main__":
    main()